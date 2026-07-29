"""Route a ``Source`` to the right fetcher based on mode + medium."""

from __future__ import annotations

import asyncio
import logging

from ..cache import fingerprint, load_cache, store_cache
from ..config import Mode, Settings
from ..parallel_client import ParallelClient
from ..schemas import FetchedContent, Source
from ..url_safety import validate_public_http_url
from .web import fetch_web
from .youtube import fetch_youtube_captions

logger = logging.getLogger(__name__)


async def fetch_one(
    source: Source,
    *,
    mode: Mode,
    parallel: ParallelClient,
) -> FetchedContent:
    validate_public_http_url(source.url)
    if source.medium == "youtube" and mode in ("captions", "full"):
        fetched = await fetch_youtube_captions(source)
        # If captions were empty but we're in full mode, try audio.
        if mode == "full" and fetched.char_count < 500:
            logger.info("Captions empty for %s; trying audio transcription", source.url)
            from .audio import fetch_audio  # lazy import - optional dep

            fetched = await fetch_audio(source)
        if fetched.fetch_method.startswith(
            ("youtube-unavailable", "audio-unavailable")
        ):
            logger.info(
                "YouTube media fetch unavailable for %s; trying page extraction",
                source.url,
            )
            web_fetched = await fetch_web(source, parallel)
            if web_fetched.char_count > fetched.char_count:
                fetched = web_fetched
        return fetched

    if source.medium == "audio" and mode == "full":
        from .audio import fetch_audio  # lazy import

        return await fetch_audio(source)

    # Fallback: treat as web (works for essays, articles, podcast show notes).
    return await fetch_web(source, parallel)


async def fetch_all(
    sources: list[Source],
    *,
    settings: Settings,
    parallel: ParallelClient,
) -> list[FetchedContent]:
    raw_dir = settings.workspace_dir / "raw"
    sem = asyncio.Semaphore(settings.concurrency)

    async def _task(src: Source) -> FetchedContent | None:
        cache = raw_dir / f"{src.id}.json"
        cache_fingerprint = fingerprint(
            "fetch",
            code=2,
            mode=settings.mode,
            source=src,
        )
        if not settings.refresh:
            try:
                cached = load_cache(cache, cache_fingerprint)
                if cached is not None:
                    return FetchedContent.model_validate(cached)
            except Exception:  # noqa: BLE001 - validation failure is a safe miss
                logger.warning("Corrupt fetch cache for %s; re-fetching", src.id)

        async with sem:
            try:
                fetched = await fetch_one(src, mode=settings.mode, parallel=parallel)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Fetch failed for %s: %s", src.url, exc)
                return None
        store_cache(cache, cache_fingerprint, fetched)
        return fetched

    results = await asyncio.gather(*(_task(s) for s in sources))
    return [r for r in results if r is not None and r.char_count > 0]
