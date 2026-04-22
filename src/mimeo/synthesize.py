"""Stage 4: cluster + author the final skill.

Two LLM calls happen here:

1. **Cluster** — merge per-source :class:`Extraction` objects into a single
   deduplicated :class:`ClusteredCorpus`.
2. **Synthesize** — turn that corpus into a :class:`SkillOutput` (SKILL body
   + reference markdown files) using the skill-creator-compliant template.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .config import Settings
from .llm import LLMClient, load_prompt, render_prompt
from .schemas import AgentsOutput, ClusteredCorpus, Extraction, SkillOutput

logger = logging.getLogger(__name__)


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

    template = load_prompt("cluster")
    extractions_json = json.dumps(
        [e.model_dump(exclude_none=True) for e in extractions],
        indent=2,
    )
    prompt = render_prompt(
        template,
        expert=settings.expert_name,
        expert_context=settings.expert_context,
        extractions_json=_maybe_truncate(extractions_json, 120_000),
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
    # Ensure expert name sticks.
    corpus = corpus.model_copy(update={"expert_name": settings.expert_name})
    cache_path.write_text(corpus.model_dump_json(indent=2), encoding="utf-8")
    return corpus


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
