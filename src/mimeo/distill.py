"""Stage 3: per-source structured extraction (the map step).

For each fetched source we call Opus with the ``extract.md`` prompt and parse
the result into an :class:`Extraction`. Results are cached per source id so
re-runs are cheap.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from .config import Settings
from .llm import LLMClient, load_prompt, render_prompt
from .schemas import Extraction, FetchedContent, Source

logger = logging.getLogger(__name__)

_MAX_CONTENT_CHARS = 50_000  # keep prompt size predictable; Opus 4.7 handles this comfortably


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

        async with sem:
            extraction = await _distill_one(
                source=source,
                fetched=fc,
                llm=llm,
                expert=settings.expert_name,
                expert_context=settings.expert_context,
                template=template,
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
) -> Extraction | None:
    content = (fetched.text or "").strip()
    if not content:
        return None
    if len(content) > _MAX_CONTENT_CHARS:
        content = content[:_MAX_CONTENT_CHARS] + "\n\n[...truncated for length...]"

    prompt = render_prompt(
        template,
        expert=expert,
        expert_context=expert_context,
        source_id=source.id,
        title=fetched.title or source.title or "(untitled)",
        url=source.url,
        kind=source.kind,
        content=content,
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
        logger.warning("Distillation failed for %s: %s", source.id, exc)
        return None

    # Enforce source_id consistency (model may occasionally drift).
    return _pin_source_id(extraction, source.id)


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
