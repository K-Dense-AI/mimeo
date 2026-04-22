"""Stage 4: cluster + author the final skill.

Two LLM calls happen here:

1. **Cluster** — merge per-source :class:`Extraction` objects into a single
   deduplicated :class:`ClusteredCorpus`. When the extractions don't fit in
   one prompt, we batch, cluster each batch, and merge the partial corpora
   in-memory so nothing gets silently dropped to a truncation.
2. **Synthesize** — turn that corpus into a :class:`SkillOutput` (SKILL body
   + reference markdown files) using the skill-creator-compliant template.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .config import Settings
from .llm import LLMClient, load_prompt, render_prompt
from .schemas import (
    AgentsOutput,
    ClusteredCorpus,
    ClusteredItem,
    Extraction,
    SkillOutput,
)

logger = logging.getLogger(__name__)

# Cluster-stage prompt budget. When the JSON-serialized extractions exceed
# this, we batch rather than truncate. Chosen to leave generous headroom for
# the schema hint + system prompt on most current models.
_CLUSTER_BATCH_CHARS = 60_000
# Bound on batch count. If we'd need more than this we fall back to
# proportional subsampling instead of dragging the run out.
_MAX_CLUSTER_BATCHES = 8


async def cluster_corpus(
    *,
    extractions: list[Extraction],
    settings: Settings,
    llm: LLMClient,
) -> ClusteredCorpus:
    cache_path = settings.workspace_dir / f"clustered_corpus.{settings.model_cache_id}.json"
    if cache_path.exists() and not settings.refresh:
        try:
            return ClusteredCorpus.model_validate_json(cache_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            logger.warning("Corrupt cluster cache; re-clustering")

    if not extractions:
        empty = ClusteredCorpus(expert_name=settings.expert_name)
        cache_path.write_text(empty.model_dump_json(indent=2), encoding="utf-8")
        return empty

    batches = _split_extractions_for_cluster(extractions)
    if len(batches) == 1:
        corpus = await _cluster_batch(
            extractions=batches[0], settings=settings, llm=llm
        )
    else:
        logger.info(
            "Clustering %d extractions in %d batches (corpus too large for one call)",
            len(extractions),
            len(batches),
        )
        partials: list[ClusteredCorpus] = []
        for idx, batch in enumerate(batches):
            logger.info("Cluster batch %d/%d (%d extractions)", idx + 1, len(batches), len(batch))
            partials.append(
                await _cluster_batch(extractions=batch, settings=settings, llm=llm)
            )
        corpus = _merge_corpora(partials, expert_name=settings.expert_name)

    corpus = corpus.model_copy(update={"expert_name": settings.expert_name})
    cache_path.write_text(corpus.model_dump_json(indent=2), encoding="utf-8")
    return corpus


async def _cluster_batch(
    *,
    extractions: list[Extraction],
    settings: Settings,
    llm: LLMClient,
) -> ClusteredCorpus:
    template = load_prompt("cluster")
    extractions_json = json.dumps(
        [e.model_dump(exclude_none=True) for e in extractions],
        indent=2,
    )
    prompt = render_prompt(
        template,
        expert=settings.expert_name,
        expert_context=settings.expert_context,
        extractions_json=_maybe_truncate(extractions_json, _CLUSTER_BATCH_CHARS),
    )
    system = (
        "You are a meticulous research synthesist. You merge many noisy "
        "extractions into a single clean knowledge base, preserving "
        "attribution and avoiding fabrication."
    )
    corpus = await llm.structured(
        system=system,
        user=prompt,
        schema=ClusteredCorpus,
        temperature=0.2,
    )
    return corpus.model_copy(update={"expert_name": settings.expert_name})


def _split_extractions_for_cluster(
    extractions: list[Extraction],
) -> list[list[Extraction]]:
    """Partition extractions so each batch's JSON fits under the budget.

    Extractions are treated as atomic — we never split one across batches —
    so a single pathologically large extraction that exceeds the budget
    still goes into its own batch and gets downstream-truncated. That's
    fine: the model still sees the start of the content.
    """
    sizes = [len(e.model_dump_json()) for e in extractions]
    # 100 chars of envelope per item (commas, brackets, indent).
    overhead = 100
    batches: list[list[Extraction]] = []
    current: list[Extraction] = []
    current_size = 0
    for ext, size in zip(extractions, sizes, strict=True):
        projected = current_size + size + overhead
        if current and projected > _CLUSTER_BATCH_CHARS:
            batches.append(current)
            current = [ext]
            current_size = size + overhead
        else:
            current.append(ext)
            current_size = projected
    if current:
        batches.append(current)

    if len(batches) > _MAX_CLUSTER_BATCHES:
        logger.warning(
            "Would split into %d batches; collapsing to %d by dropping the "
            "tail. Consider reducing --max-sources.",
            len(batches),
            _MAX_CLUSTER_BATCHES,
        )
        batches = batches[:_MAX_CLUSTER_BATCHES]
    return batches


def _merge_corpora(
    partials: list[ClusteredCorpus], *, expert_name: str
) -> ClusteredCorpus:
    """Combine several partial :class:`ClusteredCorpus` into one.

    Items across batches are deduplicated by a normalized label. When two
    items collide we union their ``source_ids``, keep the longer ``summary``
    and ``details``, and prefer the first non-null ``representative_quote``.
    """
    themes_seen: set[str] = set()
    themes: list[str] = []

    principles: dict[str, ClusteredItem] = {}
    frameworks: dict[str, ClusteredItem] = {}
    mental_models: dict[str, ClusteredItem] = {}
    heuristics: dict[str, ClusteredItem] = {}
    quotes: dict[str, ClusteredItem] = {}
    anti_patterns: dict[str, ClusteredItem] = {}

    buckets = (
        ("principles", principles),
        ("frameworks", frameworks),
        ("mental_models", mental_models),
        ("heuristics", heuristics),
        ("signature_quotes", quotes),
        ("anti_patterns", anti_patterns),
    )

    for corpus in partials:
        for t in corpus.themes:
            key = _norm(t)
            if key and key not in themes_seen:
                themes_seen.add(key)
                themes.append(t)
        for attr, target in buckets:
            for item in getattr(corpus, attr):
                key = _norm(item.label) or _norm(item.summary)
                if not key:
                    continue
                existing = target.get(key)
                if existing is None:
                    target[key] = item.model_copy(
                        update={"source_ids": list(item.source_ids)}
                    )
                    continue
                target[key] = _merge_item(existing, item)

    def _ordered(mapping: dict[str, ClusteredItem]) -> list[ClusteredItem]:
        # Frequency-first ordering mirrors what the cluster prompt asks the
        # model to produce within a single batch.
        return sorted(
            mapping.values(),
            key=lambda it: (-it.frequency, it.label.lower()),
        )

    return ClusteredCorpus(
        expert_name=expert_name,
        themes=themes,
        principles=_ordered(principles),
        frameworks=_ordered(frameworks),
        mental_models=_ordered(mental_models),
        heuristics=_ordered(heuristics),
        signature_quotes=_ordered(quotes),
        anti_patterns=_ordered(anti_patterns),
    )


def _merge_item(a: ClusteredItem, b: ClusteredItem) -> ClusteredItem:
    merged_ids = list({*a.source_ids, *b.source_ids})
    return ClusteredItem(
        label=a.label if len(a.label) >= len(b.label) else b.label,
        summary=a.summary if len(a.summary) >= len(b.summary) else b.summary,
        details=_pick_longer(a.details, b.details),
        representative_quote=a.representative_quote or b.representative_quote,
        source_ids=merged_ids,
    )


def _pick_longer(a: str | None, b: str | None) -> str | None:
    if not a:
        return b
    if not b:
        return a
    return a if len(a) >= len(b) else b


def _norm(text: str) -> str:
    return "".join(ch for ch in text.lower() if ch.isalnum())


async def author_skill(
    *,
    corpus: ClusteredCorpus,
    settings: Settings,
    llm: LLMClient,
) -> SkillOutput:
    cache_path = settings.workspace_dir / f"skill_output.{settings.model_cache_id}.json"
    if cache_path.exists() and not settings.refresh:
        try:
            return SkillOutput.model_validate_json(cache_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            logger.warning("Corrupt skill-output cache; re-authoring")

    template = load_prompt("synthesize_skill")
    corpus_json = corpus.model_dump_json(indent=2, exclude_none=True)
    prompt = render_prompt(
        template,
        expert=settings.expert_name,
        expert_context=settings.expert_context,
        corpus_json=_maybe_truncate(corpus_json, 80_000),
    )

    system = (
        "You write Agent Skills that make an AI assistant reason in the style "
        "of a specific expert. You follow the skill-creator conventions "
        "(YAML frontmatter description triggers the skill, body stays under "
        "~400 lines, depth goes in references/). You never impersonate the "
        "expert - you channel their thinking. Every quote is verbatim."
    )
    output = await llm.structured(
        system=system,
        user=prompt,
        schema=SkillOutput,
        temperature=0.4,
        max_tokens=16_000,
    )
    cache_path.write_text(output.model_dump_json(indent=2), encoding="utf-8")
    return output


async def author_agents(
    *,
    corpus: ClusteredCorpus,
    settings: Settings,
    llm: LLMClient,
) -> AgentsOutput:
    """Author a standalone AGENTS.md (no references, no frontmatter)."""
    cache_path = settings.workspace_dir / f"agents_output.{settings.model_cache_id}.json"
    if cache_path.exists() and not settings.refresh:
        try:
            return AgentsOutput.model_validate_json(cache_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            logger.warning("Corrupt agents-output cache; re-authoring")

    template = load_prompt("synthesize_agents")
    corpus_json = corpus.model_dump_json(indent=2, exclude_none=True)
    prompt = render_prompt(
        template,
        expert=settings.expert_name,
        expert_context=settings.expert_context,
        corpus_json=_maybe_truncate(corpus_json, 80_000),
    )

    system = (
        "You write AGENTS.md files that install an expert's reasoning as an "
        "AI coding agent's default behavior. AGENTS.md is always-on context "
        "(no frontmatter, no trigger description, no references/ split) so "
        "everything essential must live inside the single file. You never "
        "impersonate the expert - you adopt their defaults. Every quote is "
        "verbatim and attributed to its source id."
    )
    output = await llm.structured(
        system=system,
        user=prompt,
        schema=AgentsOutput,
        temperature=0.4,
        max_tokens=16_000,
    )
    cache_path.write_text(output.model_dump_json(indent=2), encoding="utf-8")
    return output


def _maybe_truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... [truncated for length] ..."
