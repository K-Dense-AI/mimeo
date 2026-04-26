"""Fetch plain-text content from a web URL.

Priority order:

1. Join Parallel Search excerpts (already in the Source) - cheapest.
2. If the joined length is below ``_MIN_CHARS``, call the Parallel Extract API
   for an LLM-optimized body.
3. Fall back to ``trafilatura`` scraping if Extract fails.
"""

from __future__ import annotations

import asyncio
import logging

import trafilatura

from ..schemas import FetchedContent, Source
from ..search import SearchProvider

logger = logging.getLogger(__name__)

_MIN_CHARS = 2_000
_TARGET_CHARS = 50_000
_TRAFILATURA_TIMEOUT_S = 30.0


async def fetch_web(source: Source, parallel: SearchProvider) -> FetchedContent:
    joined_excerpts = "\n\n".join(e for e in source.excerpts if e)
    if len(joined_excerpts) >= _MIN_CHARS:
        return FetchedContent(
            source_id=source.id,
            url=source.url,
            title=source.title,
            text=joined_excerpts[:_TARGET_CHARS],
            char_count=min(len(joined_excerpts), _TARGET_CHARS),
            fetch_method="parallel-excerpt",
        )

    # Try Parallel Extract next.
    try:
        response = await parallel.extract(urls=[source.url])
        if response.results:
            item = response.results[0]
            text = item.full_content or "\n\n".join(item.excerpts or [])
            if text and len(text) >= _MIN_CHARS // 2:
                return FetchedContent(
                    source_id=source.id,
                    url=source.url,
                    title=item.title or source.title,
                    text=text[:_TARGET_CHARS],
                    char_count=min(len(text), _TARGET_CHARS),
                    fetch_method="parallel-extract",
                )
    except Exception as exc:  # noqa: BLE001 - Extract failure shouldn't kill fetch
        logger.warning("Parallel extract failed for %s: %s", source.url, exc)

    # Last resort: trafilatura (offloaded to thread to avoid blocking).
    # A hard timeout guards against slow origins hanging the whole pipeline.
    try:
        text = await asyncio.wait_for(
            asyncio.to_thread(_trafilatura_fetch, source.url),
            timeout=_TRAFILATURA_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        logger.warning(
            "trafilatura fetch timed out after %.0fs for %s",
            _TRAFILATURA_TIMEOUT_S,
            source.url,
        )
        text = None
    except Exception as exc:  # noqa: BLE001
        logger.warning("trafilatura fetch failed for %s: %s", source.url, exc)
        text = None

    if not text:
        text = joined_excerpts  # whatever we had, even if short
    return FetchedContent(
        source_id=source.id,
        url=source.url,
        title=source.title,
        text=text[:_TARGET_CHARS],
        char_count=min(len(text), _TARGET_CHARS),
        fetch_method="trafilatura" if text and text != joined_excerpts else "parallel-excerpt",
    )


def _trafilatura_fetch(url: str) -> str | None:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    return trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
        favor_recall=True,
    )
