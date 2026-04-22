"""Stage 1: discover primary sources about the expert.

We run one Parallel Search API call per intent bucket (essays, talks,
interviews, podcasts, frameworks/principles, books) in parallel, merge and
de-duplicate the results by URL, then ask the LLM to rank them by canonicity
and trim to ``max_sources``.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from .config import Settings
from .llm import LLMClient
from .parallel_client import ParallelClient
from .schemas import RankedSources, Source, SourceKind

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Bucket:
    """A discovery bucket definition."""

    name: str
    objective_template: str
    search_queries_template: tuple[str, ...]
    kind: SourceKind


BUCKETS: tuple[Bucket, ...] = (
    Bucket(
        name="essays",
        objective_template=(
            "Find essays, long-form blog posts, and written articles authored by "
            "{expert}{qualifier}. Prefer primary sources on their own site, Substack, or "
            "well-known publications. Avoid summaries written by other people. "
            "Exclude content by other people who happen to share this name."
        ),
        search_queries_template=(
            '{expert} essay',
            '{expert} blog post',
            '"{expert}" article site:substack.com OR site:medium.com',
        ),
        kind="essay",
    ),
    Bucket(
        name="talks",
        objective_template=(
            "Find lectures, talks, keynotes, and conference presentations given by "
            "{expert}{qualifier}. YouTube talks are preferred because they include "
            "transcripts. Exclude talks by other people who happen to share this name."
        ),
        search_queries_template=(
            '{expert} talk site:youtube.com',
            '{expert} keynote',
            '{expert} lecture',
        ),
        kind="talk",
    ),
    Bucket(
        name="interviews",
        objective_template=(
            "Find long-form interviews with {expert}{qualifier} - written Q&A "
            "transcripts or video interviews. Prefer in-depth interviews over short "
            "news quotes. Exclude interviews of other people who happen to share "
            "this name."
        ),
        search_queries_template=(
            '{expert} interview',
            '{expert} transcript interview',
            '{expert} conversation with',
        ),
        kind="interview",
    ),
    Bucket(
        name="podcasts",
        objective_template=(
            "Find podcast episodes where {expert}{qualifier} was the guest or "
            "co-host. Include transcripts or show notes where available. Exclude "
            "episodes featuring other people who happen to share this name."
        ),
        search_queries_template=(
            '{expert} podcast',
            '{expert} podcast transcript',
            '{expert} "podcast episode"',
        ),
        kind="podcast",
    ),
    Bucket(
        name="frameworks",
        objective_template=(
            "Find content that describes the frameworks, principles, mental models, "
            "or methodology of {expert}{qualifier}. Look for explainer pieces, book "
            "summaries, and their own framework write-ups. Exclude frameworks by "
            "other people who happen to share this name."
        ),
        search_queries_template=(
            '{expert} principles',
            '{expert} framework',
            '{expert} mental models',
        ),
        kind="other",
    ),
    Bucket(
        name="books",
        objective_template=(
            "Find books authored by {expert}{qualifier} along with chapter summaries, "
            "excerpts, and detailed reviews that cover the book's core ideas. Exclude "
            "books by other people who happen to share this name."
        ),
        search_queries_template=(
            '{expert} book',
            '{expert} book summary chapter',
            '{expert} author',
        ),
        kind="book",
    ),
)


async def discover_sources(
    *,
    settings: Settings,
    parallel: ParallelClient,
    llm: LLMClient,
) -> list[Source]:
    """Run the full discovery stage."""

    # The ranking step is LLM-driven, so scope it by model. Raw per-bucket
    # search results (from Parallel Search) remain model-agnostic and reusable.
    cache_path = (
        settings.workspace_dir
        / "discovery"
        / f"ranked_sources.{settings.model_cache_id}.json"
    )
    if cache_path.exists() and not settings.refresh:
        logger.info("Using cached ranked sources from %s", cache_path)
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return [Source.model_validate(s) for s in data]

    raw_sources = await _run_all_buckets(
        expert=settings.expert_name,
        expert_description=settings.expert_description,
        parallel=parallel,
        workspace=settings.workspace_dir / "discovery",
        refresh=settings.refresh,
    )
    logger.info("Discovered %d raw sources across %d buckets", len(raw_sources), len(BUCKETS))

    merged = _merge_and_dedupe(raw_sources)
    logger.info("%d unique sources after dedup", len(merged))

    ranked = await _rank_and_trim(
        expert=settings.expert_name,
        expert_description=settings.expert_description,
        sources=merged,
        target=settings.max_sources,
        llm=llm,
    )
    logger.info("Kept top %d sources after ranking", len(ranked))

    cache_path.write_text(
        json.dumps([s.model_dump() for s in ranked], indent=2),
        encoding="utf-8",
    )
    return ranked


async def _run_all_buckets(
    *,
    expert: str,
    expert_description: str | None,
    parallel: ParallelClient,
    workspace: Path,
    refresh: bool,
) -> list[Source]:
    tasks = [
        _run_bucket(
            expert=expert,
            expert_description=expert_description,
            bucket=b,
            parallel=parallel,
            workspace=workspace,
            refresh=refresh,
        )
        for b in BUCKETS
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    merged: list[Source] = []
    for bucket, result in zip(BUCKETS, results, strict=True):
        if isinstance(result, BaseException):
            logger.warning("Bucket %s failed: %s", bucket.name, result)
            continue
        merged.extend(result)
    return merged


async def _run_bucket(
    *,
    expert: str,
    expert_description: str | None,
    bucket: Bucket,
    parallel: ParallelClient,
    workspace: Path,
    refresh: bool,
) -> list[Source]:
    cache = workspace / f"{bucket.name}.json"
    if cache.exists() and not refresh:
        data = json.loads(cache.read_text(encoding="utf-8"))
        return [Source.model_validate(s) for s in data]

    # The qualifier anchors Parallel's objective to the right person when the
    # name itself is ambiguous. Search queries stay as bare keywords so we
    # don't over-constrain keyword matching.
    qualifier = f" ({expert_description})" if expert_description else ""
    objective = bucket.objective_template.format(expert=expert, qualifier=qualifier)
    queries = [
        q.format(expert=expert, qualifier=qualifier)
        for q in bucket.search_queries_template
    ]

    result = await parallel.search(
        objective=objective,
        search_queries=queries,
    )

    sources: list[Source] = []
    for idx, r in enumerate(result.results or []):
        if not r.url:
            continue
        sources.append(
            Source(
                id=f"{bucket.name}_{idx:03d}",
                url=str(r.url),
                title=r.title,
                publish_date=str(r.publish_date) if r.publish_date else None,
                kind=bucket.kind,
                medium=_guess_medium(str(r.url)),
                bucket=bucket.name,
                excerpts=list(r.excerpts or []),
            )
        )

    cache.write_text(
        json.dumps([s.model_dump() for s in sources], indent=2),
        encoding="utf-8",
    )
    logger.info("Bucket %s: %d sources", bucket.name, len(sources))
    return sources


def _guess_medium(url: str) -> str:
    lowered = url.lower()
    if "youtube.com/watch" in lowered or "youtu.be/" in lowered:
        return "youtube"
    if any(s in lowered for s in (".mp3", ".m4a", "podcasts.apple.com", "spotify.com/episode")):
        return "audio"
    return "web"


def _merge_and_dedupe(sources: list[Source]) -> list[Source]:
    """Merge by canonical URL, keeping the richest record and re-id'ing."""
    by_url: dict[str, Source] = {}
    for s in sources:
        key = _normalize_url(s.url)
        existing = by_url.get(key)
        if existing is None:
            by_url[key] = s
            continue
        # Merge: keep longest title, union excerpts, prefer non-other kind.
        merged_excerpts = list({*existing.excerpts, *s.excerpts})
        kind = existing.kind if existing.kind != "other" else s.kind
        by_url[key] = existing.model_copy(
            update={
                "title": existing.title or s.title,
                "publish_date": existing.publish_date or s.publish_date,
                "kind": kind,
                "bucket": existing.bucket,  # keep first bucket for traceability
                "excerpts": merged_excerpts,
            }
        )

    renumbered: list[Source] = []
    for i, src in enumerate(by_url.values()):
        renumbered.append(src.model_copy(update={"id": f"src_{i:03d}"}))
    return renumbered


def _normalize_url(url: str) -> str:
    """Canonicalize a URL *for dedup purposes only* - never for fetching.

    We lowercase, drop the trailing slash, and truncate at the first tracking
    marker. The truncation is intentionally lossy: if a URL has legitimate
    query params *after* a tracking marker they'll be lost, but that only
    affects the dedup key, not any URL we actually hit.
    """
    u = url.strip().lower()
    if u.endswith("/"):
        u = u[:-1]
    for marker in ("?utm_", "&utm_", "?ref=", "&ref=", "#"):
        idx = u.find(marker)
        if idx != -1:
            u = u[:idx]
    return u


async def _rank_and_trim(
    *,
    expert: str,
    expert_description: str | None,
    sources: list[Source],
    target: int,
    llm: LLMClient,
) -> list[Source]:
    if len(sources) <= target:
        logger.info("Skipping rank: already at/below target (%d <= %d)", len(sources), target)
        return sources

    # We feed the LLM a compact table - just the fields it needs to judge.
    rows = [
        {
            "id": s.id,
            "url": s.url,
            "title": s.title,
            "kind": s.kind,
            "bucket": s.bucket,
            "publish_date": s.publish_date,
            "excerpt_chars": sum(len(e) for e in s.excerpts),
        }
        for s in sources
    ]

    system = (
        "You curate research corpora. Given a list of candidate sources about an "
        "expert, you select the most canonical, long-form, primary-source items. "
        "Prefer: essays/talks/interviews by the expert themselves, long pieces, "
        "reputable publishers, and a balanced mix across buckets so no single "
        "format dominates. Reject sources that are clearly about someone else "
        "who happens to share the expert's name."
    )
    expert_line = (
        f"Expert: {expert} ({expert_description})"
        if expert_description
        else f"Expert: {expert}"
    )
    user = (
        f"{expert_line}\n"
        f"Pick the top {target} sources from the list below, in priority order.\n"
        "If a candidate source URL or title suggests a namesake (different "
        "profession, wrong field, unrelated person), drop it rather than rank it.\n"
        "Assign each chosen source a canonicity_score between 0 and 1.\n"
        "Return ALL fields from the input plus canonicity_score unchanged except the id.\n\n"
        f"Candidate sources (JSON):\n{json.dumps(rows, indent=2)}"
    )

    result = await llm.structured(
        system=system,
        user=user,
        schema=RankedSources,
        temperature=0.2,
    )

    # LLM returned a ranked list of Sources (by id). Merge back scores + trim.
    by_id = {s.id: s for s in sources}
    ordered: list[Source] = []
    seen: set[str] = set()
    for ranked in result.sources:
        original = by_id.get(ranked.id)
        if original is None or ranked.id in seen:
            continue
        seen.add(ranked.id)
        ordered.append(
            original.model_copy(
                update={"canonicity_score": ranked.canonicity_score}
            )
        )
        if len(ordered) >= target:
            break

    # If the LLM under-returned, top up with remaining in original order.
    if len(ordered) < target:
        for s in sources:
            if s.id not in seen:
                ordered.append(s)
            if len(ordered) >= target:
                break
    return ordered
