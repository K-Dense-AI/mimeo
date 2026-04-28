"""Offline tests for :mod:`mimeo.fetchers` — dispatcher, web, youtube, audio."""

from __future__ import annotations

import asyncio
import builtins
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.fetchers import fetch_all, fetch_one
from mimeo.fetchers.dispatcher import fetch_all as _fetch_all
from mimeo.fetchers.web import _MIN_CHARS, _TARGET_CHARS, fetch_web
from mimeo.fetchers.youtube import extract_video_id, fetch_youtube_captions
from mimeo.schemas import FetchedContent, Source

from .conftest import FakeParallelClient, make_extract_response


# ---------------------------------------------------------------------------
# fetch_web
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fetch_web_uses_excerpts_when_long_enough() -> None:
    src = Source(
        id="src_000",
        url="https://example.com/e",
        title="Essay",
        bucket="essays",
        excerpts=["x" * (_MIN_CHARS + 100)],
    )
    out = await fetch_web(src, FakeParallelClient())
    assert out.fetch_method == "parallel-excerpt"
    assert out.char_count == _MIN_CHARS + 100


@pytest.mark.asyncio
async def test_fetch_web_falls_back_to_extract() -> None:
    src = Source(id="src_000", url="https://example.com/e", bucket="essays")
    parallel = FakeParallelClient(
        extract_result=make_extract_response(
            full_content="E" * (_MIN_CHARS * 2),
            title="Extracted Title",
        )
    )
    out = await fetch_web(src, parallel)
    assert out.fetch_method == "parallel-extract"
    assert out.title == "Extracted Title"
    assert out.char_count > _MIN_CHARS


@pytest.mark.asyncio
async def test_fetch_web_extract_uses_excerpts_if_no_full_content() -> None:
    src = Source(id="src_000", url="https://example.com/e", bucket="essays")
    parallel = FakeParallelClient(
        extract_result=make_extract_response(
            full_content=None, excerpts=["A" * (_MIN_CHARS * 2)]
        )
    )
    out = await fetch_web(src, parallel)
    assert out.fetch_method == "parallel-extract"


@pytest.mark.asyncio
async def test_fetch_web_falls_back_to_trafilatura(monkeypatch: pytest.MonkeyPatch) -> None:
    src = Source(id="src_000", url="https://example.com/e", bucket="essays")
    # Extract returns nothing usable.
    parallel = FakeParallelClient(extract_result=make_extract_response(full_content=""))
    monkeypatch.setattr(
        "mimeo.fetchers.web._trafilatura_fetch", lambda url: "T" * (_MIN_CHARS * 2)
    )
    out = await fetch_web(src, parallel)
    assert out.fetch_method == "trafilatura"
    assert out.char_count > _MIN_CHARS


@pytest.mark.asyncio
async def test_fetch_web_handles_extract_exception_then_trafilatura_ok(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = Source(id="src_000", url="https://example.com/e", bucket="essays")

    class _BoomParallel(FakeParallelClient):
        async def extract(self, **_: object):  # type: ignore[override]
            raise RuntimeError("extract blew up")

    monkeypatch.setattr(
        "mimeo.fetchers.web._trafilatura_fetch", lambda url: "T" * (_MIN_CHARS * 2)
    )
    out = await fetch_web(src, _BoomParallel())
    assert out.fetch_method == "trafilatura"


@pytest.mark.asyncio
async def test_fetch_web_trafilatura_timeout_falls_back_to_excerpts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = Source(
        id="src_000",
        url="https://example.com/e",
        bucket="essays",
        excerpts=["short"],
    )
    parallel = FakeParallelClient(extract_result=make_extract_response(full_content=""))

    async def _slow_wait_for(coro, timeout: float):  # type: ignore[no-redef]
        coro.close()
        raise asyncio.TimeoutError()

    monkeypatch.setattr(asyncio, "wait_for", _slow_wait_for)
    out = await fetch_web(src, parallel)
    # We get *something* (the excerpt), method degrades to parallel-excerpt label.
    assert out.text == "short"


@pytest.mark.asyncio
async def test_fetch_web_trafilatura_exception_falls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = Source(id="src_000", url="https://example.com/e", bucket="essays", excerpts=["x"])
    parallel = FakeParallelClient(extract_result=make_extract_response(full_content=""))
    monkeypatch.setattr(
        "mimeo.fetchers.web._trafilatura_fetch",
        lambda url: (_ for _ in ()).throw(RuntimeError("net down")),
    )
    out = await fetch_web(src, parallel)
    assert out.text == "x"


def test_trafilatura_fetch_returns_none_when_nothing_downloaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from mimeo.fetchers.web import _trafilatura_fetch

    monkeypatch.setattr("mimeo.fetchers.web.trafilatura.fetch_url", lambda url: None)
    assert _trafilatura_fetch("https://x") is None


def test_trafilatura_fetch_returns_extracted(monkeypatch: pytest.MonkeyPatch) -> None:
    from mimeo.fetchers.web import _trafilatura_fetch

    monkeypatch.setattr("mimeo.fetchers.web.trafilatura.fetch_url", lambda url: "raw-html")
    monkeypatch.setattr(
        "mimeo.fetchers.web.trafilatura.extract", lambda *_a, **_kw: "parsed"
    )
    assert _trafilatura_fetch("https://x") == "parsed"


# ---------------------------------------------------------------------------
# youtube
# ---------------------------------------------------------------------------


def test_extract_video_id_variants() -> None:
    assert extract_video_id("https://youtu.be/abc") == "abc"
    assert extract_video_id("https://youtube.com/watch?v=abc&t=5") == "abc"
    assert extract_video_id("https://www.youtube.com/watch") is None  # no v=
    assert extract_video_id("https://youtube.com/shorts/xyz") == "xyz"
    assert extract_video_id("https://youtube.com/embed/xyz") == "xyz"
    assert extract_video_id("https://youtube.com/live/xyz") == "xyz"
    assert extract_video_id("https://example.com/x") is None


class _FakeSnippet:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeFetched:
    def __init__(self, texts: list[str], language: str = "en") -> None:
        self.snippets = [_FakeSnippet(t) for t in texts]
        self.language_code = language


@pytest.mark.asyncio
async def test_fetch_youtube_captions_happy(monkeypatch: pytest.MonkeyPatch) -> None:
    src = Source(id="src_yt", url="https://youtu.be/abc", bucket="talks", medium="youtube")

    class _FakeApi:
        def fetch(self, video_id: str, **_: object) -> _FakeFetched:
            return _FakeFetched(["hello", "world"])

    monkeypatch.setattr(
        "mimeo.fetchers.youtube.YouTubeTranscriptApi", lambda: _FakeApi()
    )
    out = await fetch_youtube_captions(src)
    assert out.fetch_method == "youtube-captions"
    assert "hello" in out.text
    assert out.language == "en"


@pytest.mark.asyncio
async def test_fetch_youtube_captions_no_video_id() -> None:
    src = Source(id="x", url="https://example.com/not-yt", bucket="talks")
    out = await fetch_youtube_captions(src)
    assert out.fetch_method.startswith("youtube-unavailable")


@pytest.mark.asyncio
async def test_fetch_youtube_captions_falls_back_to_track_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = Source(id="src_yt", url="https://youtu.be/abc", bucket="talks", medium="youtube")

    class _Track:
        def __init__(self, ok: bool, text: str = "") -> None:
            self.ok = ok
            self.text = text

        def fetch(self) -> _FakeFetched:
            if not self.ok:
                raise RuntimeError("bad track")
            return _FakeFetched([self.text])

    class _FakeApi:
        def fetch(self, *_: object, **__: object):
            raise RuntimeError("no en track")

        def list(self, video_id: str):
            return [_Track(False), _Track(True, "second-track")]

    monkeypatch.setattr(
        "mimeo.fetchers.youtube.YouTubeTranscriptApi", lambda: _FakeApi()
    )
    out = await fetch_youtube_captions(src)
    assert "second-track" in out.text
    assert out.fetch_method == "youtube-captions"


@pytest.mark.asyncio
async def test_fetch_youtube_captions_reraises_when_all_tracks_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """api.list returns tracks but each .fetch() raises - we fall through to raise."""
    src = Source(id="src_yt", url="https://youtu.be/abc", bucket="talks", medium="youtube")

    class _Track:
        def fetch(self) -> _FakeFetched:
            raise RuntimeError("track broken")

    class _FakeApi:
        def fetch(self, *_: object, **__: object):
            raise RuntimeError("no en")

        def list(self, video_id: str):
            return [_Track(), _Track()]

    monkeypatch.setattr(
        "mimeo.fetchers.youtube.YouTubeTranscriptApi", lambda: _FakeApi()
    )
    out = await fetch_youtube_captions(src)
    # The outer handler in fetch_youtube_captions catches the re-raised exception
    # and returns an "unavailable" sentinel.
    assert out.fetch_method.startswith("youtube-unavailable")


@pytest.mark.asyncio
async def test_fetch_youtube_captions_returns_empty_on_total_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = Source(
        id="src_yt",
        url="https://youtu.be/abc",
        bucket="talks",
        medium="youtube",
        excerpts=["fallback text"],
    )

    class _FakeApi:
        def fetch(self, *_: object, **__: object):
            raise RuntimeError("no en")

        def list(self, video_id: str):
            raise RuntimeError("nothing at all")

    monkeypatch.setattr(
        "mimeo.fetchers.youtube.YouTubeTranscriptApi", lambda: _FakeApi()
    )
    out = await fetch_youtube_captions(src)
    assert out.fetch_method.startswith("youtube-unavailable")
    assert out.text == "fallback text"


# ---------------------------------------------------------------------------
# audio (uses lazy-imported yt_dlp + faster_whisper — we inject stubs)
# ---------------------------------------------------------------------------


def _install_fake_yt_dlp(
    monkeypatch: pytest.MonkeyPatch, *, raise_on_download: bool = False
) -> None:
    module = types.ModuleType("yt_dlp")

    class _FakeYDL:
        def __init__(self, opts: dict) -> None:
            self.opts = opts

        def __enter__(self) -> "_FakeYDL":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def extract_info(self, url: str, download: bool = True) -> dict:
            if raise_on_download:
                raise RuntimeError("yt-dlp down")
            tmpl = self.opts["outtmpl"]
            # The real template substitutes %(id)s / %(ext)s. Fake it.
            out_path = Path(tmpl.replace("%(id)s.%(ext)s", "vid.mp3"))
            out_path.write_bytes(b"fake audio")
            return {"id": "vid", "ext": "mp3"}

        def prepare_filename(self, info: dict) -> str:
            tmpl = self.opts["outtmpl"]
            return tmpl.replace("%(id)s.%(ext)s", "vid.mp3")

    module.YoutubeDL = _FakeYDL  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "yt_dlp", module)


def _install_fake_whisper(
    monkeypatch: pytest.MonkeyPatch,
    *,
    raise_on_transcribe: bool = False,
    text: str = "transcribed",
) -> None:
    module = types.ModuleType("faster_whisper")

    class _Segment:
        def __init__(self, text: str) -> None:
            self.text = text

    class _WhisperModel:
        def __init__(self, *_a: object, **_kw: object) -> None:
            pass

        def transcribe(self, path: str, **_: object):
            if raise_on_transcribe:
                raise RuntimeError("whisper failed")
            return [_Segment(text)], None

    module.WhisperModel = _WhisperModel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "faster_whisper", module)


def test_download_audio_missing_yt_dlp_has_actionable_message(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from mimeo.fetchers.audio import _download_audio

    real_import = builtins.__import__

    def _fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "yt_dlp":
            raise ModuleNotFoundError("No module named 'yt_dlp'", name="yt_dlp")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    with pytest.raises(RuntimeError, match="uv sync --extra full"):
        _download_audio("https://example.com/a.mp3", tmp_path)


@pytest.mark.asyncio
async def test_fetch_audio_happy(monkeypatch: pytest.MonkeyPatch) -> None:
    from mimeo.fetchers.audio import fetch_audio

    _install_fake_yt_dlp(monkeypatch)
    _install_fake_whisper(monkeypatch, text="the-transcript")
    src = Source(id="src_a", url="https://x.com/a.mp3", bucket="podcasts", medium="audio")
    out = await fetch_audio(src)
    assert out.fetch_method == "whisper"
    assert "the-transcript" in out.text


@pytest.mark.asyncio
async def test_fetch_audio_download_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from mimeo.fetchers.audio import fetch_audio

    _install_fake_yt_dlp(monkeypatch, raise_on_download=True)
    src = Source(
        id="src_a",
        url="https://x.com/a.mp3",
        bucket="podcasts",
        medium="audio",
        excerpts=["fallback"],
    )
    out = await fetch_audio(src)
    assert out.fetch_method.startswith("audio-unavailable")
    assert out.text == "fallback"


@pytest.mark.asyncio
async def test_fetch_audio_mp3_missing_falls_back_to_raw_filename(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If postprocess didn't produce a ``.mp3``, use the raw download filename."""
    from mimeo.fetchers.audio import fetch_audio

    module = types.ModuleType("yt_dlp")

    class _FakeYDL:
        def __init__(self, opts: dict) -> None:
            self.opts = opts

        def __enter__(self) -> "_FakeYDL":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def extract_info(self, url: str, download: bool = True) -> dict:
            tmpl = self.opts["outtmpl"]
            # Write a .webm file but NOT a .mp3 - forces the fallback branch.
            out_path = Path(tmpl.replace("%(id)s.%(ext)s", "vid.webm"))
            out_path.write_bytes(b"audio")
            return {"id": "vid", "ext": "webm"}

        def prepare_filename(self, info: dict) -> str:
            tmpl = self.opts["outtmpl"]
            return tmpl.replace("%(id)s.%(ext)s", "vid.webm")

    module.YoutubeDL = _FakeYDL  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "yt_dlp", module)
    _install_fake_whisper(monkeypatch, text="fallback-transcript")

    src = Source(id="src_a", url="https://x.com/a.webm", bucket="podcasts", medium="audio")
    out = await fetch_audio(src)
    assert "fallback-transcript" in out.text


@pytest.mark.asyncio
async def test_fetch_audio_transcription_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from mimeo.fetchers.audio import fetch_audio

    _install_fake_yt_dlp(monkeypatch)
    _install_fake_whisper(monkeypatch, raise_on_transcribe=True)
    src = Source(id="src_a", url="https://x.com/a.mp3", bucket="podcasts", medium="audio")
    out = await fetch_audio(src)
    assert out.fetch_method.startswith("audio-unavailable")


# ---------------------------------------------------------------------------
# dispatcher
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatcher_routes_youtube_to_captions(monkeypatch: pytest.MonkeyPatch) -> None:
    src = Source(
        id="src_yt",
        url="https://youtu.be/abc",
        medium="youtube",
        bucket="talks",
    )

    async def _fake_captions(source: Source) -> FetchedContent:
        return FetchedContent(
            source_id=source.id,
            url=source.url,
            title=source.title,
            text="caption text",
            char_count=600,
            fetch_method="youtube-captions",
        )

    monkeypatch.setattr("mimeo.fetchers.dispatcher.fetch_youtube_captions", _fake_captions)
    out = await fetch_one(src, mode="captions", parallel=FakeParallelClient())
    assert out.fetch_method == "youtube-captions"


@pytest.mark.asyncio
async def test_dispatcher_routes_youtube_full_with_empty_captions_to_audio(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    src = Source(id="src_yt", url="https://youtu.be/abc", medium="youtube", bucket="talks")

    async def _empty_captions(source: Source) -> FetchedContent:
        return FetchedContent(
            source_id=source.id,
            url=source.url,
            title=source.title,
            text="",
            char_count=0,
            fetch_method="youtube-unavailable:none",
        )

    async def _fake_audio(source: Source) -> FetchedContent:
        return FetchedContent(
            source_id=source.id,
            url=source.url,
            title=source.title,
            text="whisper-transcript",
            char_count=18,
            fetch_method="whisper",
        )

    monkeypatch.setattr("mimeo.fetchers.dispatcher.fetch_youtube_captions", _empty_captions)
    # Inject the audio module with our fake fetch_audio.
    fake_audio_mod = types.ModuleType("mimeo.fetchers.audio")
    fake_audio_mod.fetch_audio = _fake_audio  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mimeo.fetchers.audio", fake_audio_mod)

    out = await fetch_one(src, mode="full", parallel=FakeParallelClient())
    assert out.fetch_method == "whisper"


@pytest.mark.asyncio
async def test_dispatcher_routes_audio_medium_to_audio(monkeypatch: pytest.MonkeyPatch) -> None:
    src = Source(id="src_a", url="https://x.com/a.mp3", medium="audio", bucket="podcasts")

    async def _fake_audio(source: Source) -> FetchedContent:
        return FetchedContent(
            source_id=source.id,
            url=source.url,
            title=source.title,
            text="mp3-transcript",
            char_count=14,
            fetch_method="whisper",
        )

    fake_audio_mod = types.ModuleType("mimeo.fetchers.audio")
    fake_audio_mod.fetch_audio = _fake_audio  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "mimeo.fetchers.audio", fake_audio_mod)

    out = await fetch_one(src, mode="full", parallel=FakeParallelClient())
    assert out.fetch_method == "whisper"


@pytest.mark.asyncio
async def test_dispatcher_defaults_to_web(monkeypatch: pytest.MonkeyPatch) -> None:
    src = Source(id="src_w", url="https://example.com/x", medium="web", bucket="essays")

    async def _fake_web(source: Source, parallel):  # type: ignore[no-redef]
        return FetchedContent(
            source_id=source.id,
            url=source.url,
            title=source.title,
            text="web-text",
            char_count=8,
            fetch_method="parallel-excerpt",
        )

    monkeypatch.setattr("mimeo.fetchers.dispatcher.fetch_web", _fake_web)
    out = await fetch_one(src, mode="captions", parallel=FakeParallelClient())
    assert out.fetch_method == "parallel-excerpt"


@pytest.mark.asyncio
async def test_fetch_all_caches_and_handles_corruption_and_failure(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    ensure_dirs(settings)

    async def _fake_one(source: Source, *, mode, parallel):  # type: ignore[no-redef]
        if source.id == "src_boom":
            raise RuntimeError("fetch blew up")
        return FetchedContent(
            source_id=source.id,
            url=source.url,
            title=source.title,
            text=f"content-{source.id}",
            char_count=len(f"content-{source.id}"),
            fetch_method="parallel-excerpt",
        )

    monkeypatch.setattr("mimeo.fetchers.dispatcher.fetch_one", _fake_one)

    sources = [
        Source(id="src_000", url="https://x.com/0", bucket="essays"),
        Source(id="src_boom", url="https://x.com/1", bucket="essays"),
    ]
    # Seed one corrupt cache file.
    raw = settings.workspace_dir / "raw"
    (raw / "src_000.json").write_text("garbage", encoding="utf-8")

    out = await fetch_all(sources, settings=settings, parallel=FakeParallelClient())
    # Corrupt cache gets replaced via refetch; failing source drops out.
    ids = [f.source_id for f in out]
    assert ids == ["src_000"]
    cached = FetchedContent.model_validate_json(
        (raw / "src_000.json").read_text(encoding="utf-8")
    )
    assert cached.text == "content-src_000"


@pytest.mark.asyncio
async def test_fetch_all_uses_cache(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    ensure_dirs(settings)
    raw = settings.workspace_dir / "raw"
    cached = FetchedContent(
        source_id="src_000",
        url="https://x.com/0",
        title="T",
        text="hit",
        char_count=3,
        fetch_method="parallel-excerpt",
    )
    (raw / "src_000.json").write_text(cached.model_dump_json(), encoding="utf-8")

    called = False

    async def _fake_one(*_a, **_kw):  # type: ignore[no-redef]
        nonlocal called
        called = True
        return cached

    monkeypatch.setattr("mimeo.fetchers.dispatcher.fetch_one", _fake_one)
    out = await fetch_all(
        [Source(id="src_000", url="https://x.com/0", bucket="essays")],
        settings=settings,
        parallel=FakeParallelClient(),
    )
    assert out[0].text == "hit"
    assert called is False
