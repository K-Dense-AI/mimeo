"""Fetch YouTube captions via ``youtube-transcript-api``."""

from __future__ import annotations

import asyncio
import logging
import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi

from ..schemas import FetchedContent, Source

logger = logging.getLogger(__name__)


def extract_video_id(url: str) -> str | None:
    """Parse a YouTube URL and return its video id."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/") or None
    if parsed.hostname and "youtube.com" in parsed.hostname:
        if parsed.path in ("/watch", "/watch/"):
            qs = parse_qs(parsed.query)
            v = qs.get("v", [None])[0]
            return v
        # Short URLs like /shorts/ID or /embed/ID
        m = re.match(r"^/(shorts|embed|live)/([^/?#]+)", parsed.path)
        if m:
            return m.group(2)
    return None


async def fetch_youtube_captions(source: Source) -> FetchedContent:
    video_id = extract_video_id(source.url)
    if not video_id:
        return _empty(source, reason="no-video-id")

    try:
        fetched = await asyncio.to_thread(_fetch_blocking, video_id)
    except Exception as exc:  # noqa: BLE001
        logger.warning("YouTube captions failed for %s: %s", source.url, exc)
        return _empty(source, reason=str(exc))

    text = "\n".join(snip.text for snip in fetched.snippets if snip.text)
    return FetchedContent(
        source_id=source.id,
        url=source.url,
        title=source.title,
        text=text,
        char_count=len(text),
        fetch_method="youtube-captions",
        language=fetched.language_code,
    )


def _fetch_blocking(video_id: str):
    api = YouTubeTranscriptApi()
    # Try English first, then any available.
    try:
        return api.fetch(video_id, languages=("en", "en-US", "en-GB"))
    except Exception:
        tracks = api.list(video_id)
        # Pick the first translatable track.
        for t in tracks:
            try:
                return t.fetch()
            except Exception:
                continue
        raise


def _empty(source: Source, reason: str) -> FetchedContent:
    # Fall back to excerpts we already have so downstream distill still has *something*.
    text = "\n\n".join(source.excerpts or [])
    return FetchedContent(
        source_id=source.id,
        url=source.url,
        title=source.title,
        text=text,
        char_count=len(text),
        fetch_method=f"youtube-unavailable:{reason[:40]}",
    )
