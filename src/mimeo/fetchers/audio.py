"""Audio transcription fallback (only used in ``--mode full``).

Dependencies are imported lazily so installing the base package without the
``[full]`` extra still works.
"""

from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
from pathlib import Path

from ..schemas import FetchedContent, Source

logger = logging.getLogger(__name__)

_MODEL_NAME = "base"  # good speed/quality balance; user can swap later
_YTDLP_INSTALL_HINT = (
    "Missing optional audio dependency 'yt-dlp' (Python import name 'yt_dlp'). "
    "Install audio transcription support with `uv sync --extra full` or "
    "`pip install -e '.[full]'`, or run without `--mode full`."
)


async def fetch_audio(source: Source) -> FetchedContent:
    """Download + transcribe the audio for ``source`` using yt-dlp + faster-whisper."""
    work_dir = Path(tempfile.mkdtemp(prefix="mimeo-audio-"))
    try:
        try:
            audio_path = await asyncio.to_thread(_download_audio, source.url, work_dir)
        except Exception as exc:  # noqa: BLE001
            logger.warning("yt-dlp download failed for %s: %s", source.url, exc)
            return _empty(source, reason=str(exc))

        try:
            text = await asyncio.to_thread(_transcribe, audio_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Whisper transcription failed for %s: %s", source.url, exc)
            return _empty(source, reason=str(exc))

        return FetchedContent(
            source_id=source.id,
            url=source.url,
            title=source.title,
            text=text,
            char_count=len(text),
            fetch_method="whisper",
        )
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def _download_audio(url: str, out_dir: Path) -> Path:
    """Use yt-dlp to pull a best-effort audio-only file into ``out_dir``."""
    try:
        from yt_dlp import YoutubeDL  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        if exc.name == "yt_dlp":
            raise RuntimeError(_YTDLP_INSTALL_HINT) from exc
        raise

    template = str(out_dir / "%(id)s.%(ext)s")

    opts = {
        "format": "bestaudio/best",
        "outtmpl": template,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "128"},
        ],
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    audio_path = Path(filename).with_suffix(".mp3")
    if not audio_path.exists():
        # Fall back to the raw filename (no postprocessing on some formats).
        audio_path = Path(filename)
    return audio_path


def _transcribe(audio_path: Path) -> str:
    from faster_whisper import WhisperModel  # type: ignore[import-not-found]

    model = WhisperModel(_MODEL_NAME, device="auto", compute_type="int8")
    segments, _info = model.transcribe(str(audio_path), vad_filter=True)
    return "\n".join(seg.text.strip() for seg in segments if seg.text)


def _empty(source: Source, reason: str) -> FetchedContent:
    text = "\n\n".join(source.excerpts or [])
    return FetchedContent(
        source_id=source.id,
        url=source.url,
        title=source.title,
        text=text,
        char_count=len(text),
        fetch_method=f"audio-unavailable:{reason[:40]}",
    )
