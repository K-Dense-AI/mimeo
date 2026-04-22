"""Stage 3: per-source structured extraction (the map step).

For each fetched source we call the configured model with the ``extract.md``
prompt and parse the result into an :class:`Extraction`. Results are cached
per source id so re-runs are cheap.

Long sources (books, paper PDFs, conference transcripts) are chunked on
paragraph boundaries with a small overlap, distilled in parallel, and then
merged. This preserves principles / quotes that live in the back half of a
long piece rather than silently dropping them via truncation.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from .config import Settings
from .llm import LLMClient, load_prompt, render_prompt
from .schemas import (
    AntiPattern,
    Extraction,
    FetchedContent,
    Framework,
    MentalModel,
    Principle,
    Quote,
    Source,
)

logger = logging.getLogger(__name__)

# Chunking thresholds. Sources under ``_CHUNK_THRESHOLD`` go through the
# single-call path. Larger sources are split into ``_CHUNK_TARGET_CHARS``-
# sized pieces with ``_CHUNK_OVERLAP`` of overlap so concepts that straddle a
# boundary aren't lost. ``_MAX_TOTAL_CHARS`` caps runaway book-length inputs
# at ~6x our comfortable prompt size.
_CHUNK_THRESHOLD = 50_000
_CHUNK_TARGET_CHARS = 40_000
_CHUNK_OVERLAP = 2_000
_MAX_TOTAL_CHARS = 240_000

# Back-compat alias: some tests reference the old truncation constant. It
# still controls the single-call path, now as the "send whole content in one
# request" ceiling rather than a hard truncation.
_MAX_CONTENT_CHARS = _CHUNK_THRESHOLD


async def distill_all(
    *,
    sources: list[Source],
    fetched: list[FetchedContent],
    settings: Settings,
    llm: LLMClient,
) -> list[Extraction]:
    by_id = {s.id: s for s in sources}
    distilled_dir = settings.workspace_dir / "distilled"
    sem = asyncio.Semaphore(settings.concurrency)
    template = load_prompt("extract")
    model_tag = settings.model_cache_id

    async def _task(fc: FetchedContent) -> Extraction | None:
        source = by_id.get(fc.source_id)
        if source is None:
            return None
        cache = distilled_dir / f"{source.id}.{model_tag}.json"
        if cache.exists() and not settings.refresh:
            try:
                return Extraction.model_validate_json(cache.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                logger.warning("Corrupt cache for %s; re-distilling", source.id)

        extraction = await _distill_one(
            source=source,
            fetched=fc,
            llm=llm,
            expert=settings.expert_name,
            expert_context=settings.expert_context,
            template=template,
            sem=sem,
        )
        if extraction is not None:
            cache.write_text(extraction.model_dump_json(indent=2), encoding="utf-8")
        return extraction

    results = await asyncio.gather(*(_task(fc) for fc in fetched))
    return [r for r in results if r is not None]


async def _distill_one(
    *,
    source: Source,
    fetched: FetchedContent,
    llm: LLMClient,
    expert: str,
    expert_context: str,
    template: str,
    sem: asyncio.Semaphore,
) -> Extraction | None:
    content = (fetched.text or "").strip()
    if not content:
        return None

    # Cap runaway inputs. We prefer a fixed ceiling over chunking without
    # bound so cost stays predictable; most real-world sources fit under it.
    if len(content) > _MAX_TOTAL_CHARS:
        content = content[:_MAX_TOTAL_CHARS] + "\n\n[...truncated for length...]"

    if len(content) <= _CHUNK_THRESHOLD:
        async with sem:
            return await _distill_chunk(
                source=source,
                fetched=fetched,
                content=content,
                chunk_index=None,
                chunk_count=None,
                llm=llm,
                expert=expert,
                expert_context=expert_context,
                template=template,
            )

    chunks = _chunk_text(content, target=_CHUNK_TARGET_CHARS, overlap=_CHUNK_OVERLAP)
    logger.info(
        "Source %s is %d chars; distilling as %d chunks",
        source.id,
        len(content),
        len(chunks),
    )

    async def _run(idx: int, chunk: str) -> Extraction | None:
        async with sem:
            return await _distill_chunk(
                source=source,
                fetched=fetched,
                content=chunk,
                chunk_index=idx,
                chunk_count=len(chunks),
                llm=llm,
                expert=expert,
                expert_context=expert_context,
                template=template,
            )

    results = await asyncio.gather(*(_run(i, c) for i, c in enumerate(chunks)))
    extractions = [e for e in results if e is not None]
    if not extractions:
        return None
    return _merge_extractions(extractions, source_id=source.id)


async def _distill_chunk(
    *,
    source: Source,
    fetched: FetchedContent,
    content: str,
    chunk_index: int | None,
    chunk_count: int | None,
    llm: LLMClient,
    expert: str,
    expert_context: str,
    template: str,
) -> Extraction | None:
    """Run the extract prompt against a single (possibly whole) chunk."""
    body = content
    if chunk_index is not None and chunk_count is not None and chunk_count > 1:
        body = (
            f"[This is chunk {chunk_index + 1} of {chunk_count} from a long "
            "source. Extract only what this chunk actually shows; don't "
            "invent context from chunks you haven't seen.]\n\n"
            f"{body}"
        )

    prompt = render_prompt(
        template,
        expert=expert,
        expert_context=expert_context,
        source_id=source.id,
        title=fetched.title or source.title or "(untitled)",
        url=source.url,
        kind=source.kind,
        content=body,
    )

    system = (
        "You are a careful research analyst. You read primary sources and "
        "extract structured data about an expert's thought process. You never "
        "fabricate; missing information is better than invented information."
    )

    try:
        extraction = await llm.structured(
            system=system,
            user=prompt,
            schema=Extraction,
            temperature=0.2,
        )
    except Exception as exc:  # noqa: BLE001
        label = (
            f"{source.id} chunk {chunk_index + 1}/{chunk_count}"
            if chunk_index is not None and chunk_count is not None
            else source.id
        )
        logger.warning("Distillation failed for %s: %s", label, exc)
        return None

    return _pin_source_id(extraction, source.id)


def _chunk_text(text: str, *, target: int, overlap: int) -> list[str]:
    """Split ``text`` into overlapping chunks of roughly ``target`` chars.

    We prefer to cut on paragraph boundaries (``\\n\\n``) and, failing that,
    on sentence boundaries (``. `` or ``\\n``). Each chunk after the first
    is prefixed with the last ``overlap`` characters of the previous chunk
    so concepts that straddle a cut point aren't silently dropped.
    """
    if len(text) <= target:
        return [text]

    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + target, n)
        if end < n:
            cut = _find_soft_break(text, start=start, end=end)
            if cut > start + target // 2:
                end = cut
        chunks.append(text[start:end])
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def _find_soft_break(text: str, *, start: int, end: int) -> int:
    """Find the best split point at or before ``end``, preferring paragraphs.

    Returns ``end`` unchanged when no soft break exists in the window, which
    is fine: we'll just do a hard cut at the char boundary.
    """
    for sep in ("\n\n", "\n", ". ", " "):
        idx = text.rfind(sep, start, end)
        if idx != -1 and idx > start:
            return idx + len(sep)
    return end


def _merge_extractions(extractions: list[Extraction], *, source_id: str) -> Extraction:
    """Combine per-chunk extractions into a single Extraction for the source.

    We union structured items across chunks, deduplicating by a canonical
    key so a principle quoted in both chunk 1 and chunk 2 only shows up
    once. Summary text is joined; themes are unioned.
    """
    summaries: list[str] = []
    themes_seen: set[str] = set()
    themes: list[str] = []
    heuristics_seen: set[str] = set()
    heuristics: list[str] = []

    principles: list[Principle] = []
    frameworks: list[Framework] = []
    mental_models: list[MentalModel] = []
    quotes: list[Quote] = []
    anti_patterns: list[AntiPattern] = []

    p_keys: set[str] = set()
    f_keys: set[str] = set()
    m_keys: set[str] = set()
    q_keys: set[str] = set()
    a_keys: set[str] = set()

    for ext in extractions:
        if ext.summary.strip():
            summaries.append(ext.summary.strip())
        for t in ext.themes:
            key = _norm(t)
            if key and key not in themes_seen:
                themes_seen.add(key)
                themes.append(t)
        for h in ext.heuristics:
            key = _norm(h)
            if key and key not in heuristics_seen:
                heuristics_seen.add(key)
                heuristics.append(h)
        for p in ext.principles:
            key = _norm(p.statement)
            if key and key not in p_keys:
                p_keys.add(key)
                principles.append(p)
        for fw in ext.frameworks:
            key = _norm(fw.name)
            if key and key not in f_keys:
                f_keys.add(key)
                frameworks.append(fw)
        for mm in ext.mental_models:
            key = _norm(mm.name)
            if key and key not in m_keys:
                m_keys.add(key)
                mental_models.append(mm)
        for q in ext.signature_quotes:
            key = _norm(q.text)
            if key and key not in q_keys:
                q_keys.add(key)
                quotes.append(q)
        for ap in ext.anti_patterns:
            key = _norm(ap.description)
            if key and key not in a_keys:
                a_keys.add(key)
                anti_patterns.append(ap)

    merged_summary = " ".join(summaries).strip() or extractions[0].summary
    merged = Extraction(
        source_id=source_id,
        summary=merged_summary,
        themes=themes,
        principles=principles,
        frameworks=frameworks,
        mental_models=mental_models,
        heuristics=heuristics,
        signature_quotes=quotes,
        anti_patterns=anti_patterns,
    )
    return _pin_source_id(merged, source_id)


def _norm(text: str) -> str:
    """Loose key for dedup: lowercase alphanumerics only."""
    return "".join(ch for ch in text.lower() if ch.isalnum())


def _pin_source_id(extraction: Extraction, source_id: str) -> Extraction:
    """Re-stamp ``source_id`` on the extraction and every nested item."""

    def _pin(items):
        return [x.model_copy(update={"source_id": source_id}) for x in items]

    return extraction.model_copy(
        update={
            "source_id": source_id,
            "principles": _pin(extraction.principles),
            "frameworks": _pin(extraction.frameworks),
            "mental_models": _pin(extraction.mental_models),
            "signature_quotes": _pin(extraction.signature_quotes),
            "anti_patterns": _pin(extraction.anti_patterns),
        }
    )
