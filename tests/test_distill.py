"""Offline tests for :mod:`mimeo.distill`."""

from __future__ import annotations

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.distill import (
    _CHUNK_THRESHOLD,
    _MAX_CONTENT_CHARS,
    _MAX_TOTAL_CHARS,
    _chunk_text,
    _merge_extractions,
    _pin_source_id,
    distill_all,
)
from mimeo.schemas import (
    AntiPattern,
    Extraction,
    FetchedContent,
    Framework,
    MentalModel,
    Principle,
    Quote,
    Source,
)

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
async def test_distill_all_chunks_long_content(settings: Settings) -> None:
    """Content above the chunk threshold is split and distilled per chunk."""
    ensure_dirs(settings)
    # Clearly exceed the threshold so chunking fires, with a paragraph
    # boundary in the middle so _find_soft_break has something to grab.
    chunk = "A" * 30_000
    text = f"{chunk}\n\nbridge paragraph.\n\n{chunk}\n\ntail paragraph"
    giant = FetchedContent(
        source_id="src_000",
        url="https://x.com/0",
        title="t",
        text=text,
        char_count=len(text),
        fetch_method="parallel-excerpt",
    )
    llm = FakeLLMClient()
    # Queue one extraction per chunk we expect. _CHUNK_TARGET_CHARS is
    # smaller than the total, so we get at least 2 chunks.
    for _ in range(6):  # safety over-queue
        llm.queue_structured(Extraction, sample_extraction("src_000"))
    out = await distill_all(
        sources=[_source("src_000")], fetched=[giant], settings=settings, llm=llm
    )
    assert len(out) == 1
    assert out[0].source_id == "src_000"
    assert len(llm.structured_calls) >= 2
    # Every chunk prompt should identify itself as a chunk.
    for _, user, _system in llm.structured_calls:
        assert "chunk" in user


@pytest.mark.asyncio
async def test_distill_all_caps_runaway_content(settings: Settings) -> None:
    """Content above the hard ceiling is truncated with a marker."""
    ensure_dirs(settings)
    giant = FetchedContent(
        source_id="src_000",
        url="https://x.com/0",
        title="t",
        text="A" * (_MAX_TOTAL_CHARS + 10_000),
        char_count=_MAX_TOTAL_CHARS + 10_000,
        fetch_method="parallel-excerpt",
    )
    llm = FakeLLMClient()
    for _ in range(10):
        llm.queue_structured(Extraction, sample_extraction("src_000"))
    await distill_all(
        sources=[_source("src_000")], fetched=[giant], settings=settings, llm=llm
    )
    prompt_text = "\n".join(user for _, user, _system in llm.structured_calls)
    assert "[...truncated for length...]" in prompt_text


def test_chunk_text_below_threshold_returns_single() -> None:
    assert _chunk_text("hello world", target=1000, overlap=10) == ["hello world"]


def test_chunk_text_overlaps_and_prefers_paragraph_breaks() -> None:
    para = "word " * 400  # ~2000 chars
    text = "\n\n".join([para.strip()] * 4)
    chunks = _chunk_text(text, target=3000, overlap=200)
    assert len(chunks) >= 2
    # Chunks share a small overlap so straddling concepts survive.
    for a, b in zip(chunks, chunks[1:], strict=False):
        tail = a[-200:]
        assert any(token in b[:400] for token in tail.split() if len(token) > 3)


def test_merge_extractions_dedupes_and_pins_source_id() -> None:
    e1 = Extraction(
        source_id="src_000",
        summary="First half.",
        themes=["leverage", "time"],
        principles=[
            Principle(statement="Seek leverage.", rationale="r", source_id="src_000")
        ],
        frameworks=[Framework(name="10x thinking", when_to_apply="a", source_id="src_000")],
        heuristics=["Play long games."],
    )
    e2 = Extraction(
        source_id="src_000",
        summary="Second half.",
        themes=["Leverage"],  # dedupes case-insensitively
        principles=[
            Principle(statement="seek  leverage!", rationale="r2", source_id="src_000"),
            Principle(statement="Own equity.", rationale="r3", source_id="src_000"),
        ],
        mental_models=[
            MentalModel(name="Compounding", description="d", source_id="src_000")
        ],
        signature_quotes=[Quote(text="Hello.", source_id="src_000")],
        anti_patterns=[AntiPattern(description="Renting time.", source_id="src_000")],
        heuristics=["play long games", "Own your time."],
    )
    merged = _merge_extractions([e1, e2], source_id="src_000")
    assert merged.source_id == "src_000"
    assert "First half." in merged.summary and "Second half." in merged.summary
    assert len(merged.themes) == 2  # leverage+time, dedupe-insensitive
    assert [p.statement for p in merged.principles] == ["Seek leverage.", "Own equity."]
    assert len(merged.frameworks) == 1
    assert len(merged.mental_models) == 1
    assert len(merged.signature_quotes) == 1
    assert len(merged.anti_patterns) == 1
    assert merged.heuristics == ["Play long games.", "Own your time."]


@pytest.mark.asyncio
async def test_distill_all_chunked_run_returns_none_when_every_chunk_fails(
    settings: Settings,
) -> None:
    ensure_dirs(settings)
    giant = FetchedContent(
        source_id="src_000",
        url="https://x.com/0",
        title="t",
        text="A" * (_CHUNK_THRESHOLD + 20_000),
        char_count=_CHUNK_THRESHOLD + 20_000,
        fetch_method="parallel-excerpt",
    )

    class _BoomLLM(FakeLLMClient):
        async def structured(self, **_: object):  # type: ignore[override]
            raise RuntimeError("llm down")

    out = await distill_all(
        sources=[_source("src_000")],
        fetched=[giant],
        settings=settings,
        llm=_BoomLLM(),
    )
    assert out == []


assert _MAX_CONTENT_CHARS == _CHUNK_THRESHOLD  # back-compat alias


def test_chunk_text_no_soft_break_uses_hard_cut() -> None:
    """Text with no paragraph / sentence separators falls back to hard cuts."""
    text = "a" * 8000
    chunks = _chunk_text(text, target=3000, overlap=200)
    assert len(chunks) >= 3
    assert "".join(c[:-200] if i > 0 else c for i, c in enumerate(chunks))


def test_merge_extractions_handles_empty_summary_and_dup_items() -> None:
    """Exercise the branches that fire when extractions carry odd shapes:

    - An empty ``summary`` takes the ``if ext.summary.strip()`` false branch.
    - Duplicate frameworks / mental models / anti-patterns within one
      extraction force the dedup ``continue`` path for those categories.
    """
    empty = Extraction(
        source_id="src_000",
        summary="",
        principles=[],
        frameworks=[
            Framework(name="10x thinking", when_to_apply="a", source_id="src_000"),
            Framework(name="10X THINKING!", when_to_apply="b", source_id="src_000"),
        ],
        mental_models=[
            MentalModel(name="Compounding", description="d", source_id="src_000"),
            MentalModel(name=" compounding ", description="e", source_id="src_000"),
        ],
        signature_quotes=[],
        anti_patterns=[
            AntiPattern(description="Renting time.", source_id="src_000"),
            AntiPattern(description="renting TIME", source_id="src_000"),
        ],
        heuristics=[],
        themes=[],
    )
    nonempty = Extraction(
        source_id="src_000",
        summary="Has a summary.",
        principles=[
            Principle(statement="Seek leverage.", rationale="r", source_id="src_000")
        ],
    )
    merged = _merge_extractions([empty, nonempty], source_id="src_000")
    assert merged.summary == "Has a summary."
    assert len(merged.frameworks) == 1
    assert len(merged.mental_models) == 1
    assert len(merged.anti_patterns) == 1


def test_merge_extractions_all_empty_summaries_falls_back() -> None:
    """If every extraction has an empty summary, merge keeps the original."""
    empty = Extraction(source_id="src_000", summary="")
    merged = _merge_extractions([empty, empty], source_id="src_000")
    assert merged.summary == ""
