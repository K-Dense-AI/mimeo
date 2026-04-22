"""Offline tests for :mod:`mimeo.distill`."""

from __future__ import annotations

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.distill import _MAX_CONTENT_CHARS, _pin_source_id, distill_all
from mimeo.schemas import Extraction, FetchedContent, Principle, Quote, Source

from .conftest import FakeLLMClient, sample_extraction, sample_fetched


def _source(sid: str = "src_000", title: str = "T") -> Source:
    return Source(id=sid, url=f"https://x.com/{sid}", title=title, bucket="essays")


def test_pin_source_id_overrides_drift() -> None:
    extraction = Extraction(
        source_id="wrong",
        summary="s",
        principles=[
            Principle(
                statement="p", rationale="r", source_id="also-wrong"
            )
        ],
        signature_quotes=[Quote(text="q", source_id="different")],
    )
    fixed = _pin_source_id(extraction, "correct")
    assert fixed.source_id == "correct"
    assert fixed.principles[0].source_id == "correct"
    assert fixed.signature_quotes[0].source_id == "correct"


@pytest.mark.asyncio
async def test_distill_all_happy_path(settings: Settings) -> None:
    ensure_dirs(settings)
    sources = [_source("src_000"), _source("src_001")]
    fetched = [sample_fetched("src_000"), sample_fetched("src_001")]
    llm = FakeLLMClient()
    llm.queue_structured(Extraction, sample_extraction("src_000"))
    llm.queue_structured(Extraction, sample_extraction("src_001"))

    out = await distill_all(
        sources=sources, fetched=fetched, settings=settings, llm=llm
    )
    assert [e.source_id for e in out] == ["src_000", "src_001"]
    # Per-source cache files written with model-scoped names.
    tag = settings.model_cache_id
    for sid in ("src_000", "src_001"):
        assert (settings.workspace_dir / "distilled" / f"{sid}.{tag}.json").exists()


@pytest.mark.asyncio
async def test_distill_all_reads_cache_and_skips_llm(settings: Settings) -> None:
    ensure_dirs(settings)
    tag = settings.model_cache_id
    cache = settings.workspace_dir / "distilled" / f"src_000.{tag}.json"
    cache.write_text(sample_extraction("src_000").model_dump_json(), encoding="utf-8")

    llm = FakeLLMClient()  # no queued responses - would blow up if called
    out = await distill_all(
        sources=[_source("src_000")],
        fetched=[sample_fetched("src_000")],
        settings=settings,
        llm=llm,
    )
    assert len(out) == 1
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_distill_all_recovers_from_corrupt_cache(settings: Settings) -> None:
    ensure_dirs(settings)
    tag = settings.model_cache_id
    cache = settings.workspace_dir / "distilled" / f"src_000.{tag}.json"
    cache.write_text("not valid json", encoding="utf-8")

    llm = FakeLLMClient()
    llm.queue_structured(Extraction, sample_extraction("src_000"))
    out = await distill_all(
        sources=[_source("src_000")],
        fetched=[sample_fetched("src_000")],
        settings=settings,
        llm=llm,
    )
    assert len(out) == 1


@pytest.mark.asyncio
async def test_distill_all_skips_fetched_without_matching_source(settings: Settings) -> None:
    ensure_dirs(settings)
    fetched = [sample_fetched("src_orphan")]  # no matching source
    llm = FakeLLMClient()
    out = await distill_all(
        sources=[_source("src_000")], fetched=fetched, settings=settings, llm=llm
    )
    assert out == []
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_distill_all_skips_empty_fetched_text(settings: Settings) -> None:
    ensure_dirs(settings)
    empty = FetchedContent(
        source_id="src_000",
        url="https://x.com/0",
        title="t",
        text="   ",
        char_count=0,
        fetch_method="parallel-excerpt",
    )
    llm = FakeLLMClient()
    out = await distill_all(
        sources=[_source("src_000")], fetched=[empty], settings=settings, llm=llm
    )
    assert out == []
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_distill_all_tolerates_llm_failure(settings: Settings) -> None:
    ensure_dirs(settings)

    class _BoomLLM(FakeLLMClient):
        async def structured(self, **_: object):  # type: ignore[override]
            raise RuntimeError("llm down")

    out = await distill_all(
        sources=[_source("src_000")],
        fetched=[sample_fetched("src_000")],
        settings=settings,
        llm=_BoomLLM(),
    )
    assert out == []


@pytest.mark.asyncio
async def test_distill_all_truncates_long_content(settings: Settings) -> None:
    ensure_dirs(settings)
    giant = FetchedContent(
        source_id="src_000",
        url="https://x.com/0",
        title="t",
        text="A" * (_MAX_CONTENT_CHARS + 1_000),
        char_count=_MAX_CONTENT_CHARS + 1_000,
        fetch_method="parallel-excerpt",
    )
    llm = FakeLLMClient()
    llm.queue_structured(Extraction, sample_extraction("src_000"))
    await distill_all(
        sources=[_source("src_000")], fetched=[giant], settings=settings, llm=llm
    )
    # The user prompt should contain the truncation marker we ship with.
    _, user, _ = llm.structured_calls[0]
    assert "[...truncated for length...]" in user
