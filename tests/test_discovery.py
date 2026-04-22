"""Offline tests for :mod:`mimeo.discovery`."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from mimeo.config import Settings
from mimeo.discovery import (
    BUCKETS,
    _guess_medium,
    _merge_and_dedupe,
    _rank_and_trim,
    _run_bucket,
    discover_sources,
)
from mimeo.schemas import RankedSources, Source

from .conftest import FakeLLMClient, FakeParallelClient, make_search_result


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def test_guess_medium() -> None:
    assert _guess_medium("https://www.youtube.com/watch?v=x") == "youtube"
    assert _guess_medium("https://youtu.be/x") == "youtube"
    assert _guess_medium("https://example.com/a.mp3") == "audio"
    assert _guess_medium("https://example.com/a.m4a") == "audio"
    assert _guess_medium("https://podcasts.apple.com/episode") == "audio"
    assert _guess_medium("https://open.spotify.com/episode/x") == "audio"
    assert _guess_medium("https://example.com/essay") == "web"


def test_merge_keeps_non_other_kind_and_unions_excerpts() -> None:
    sources = [
        Source(id="a", url="https://x.com/p", kind="other", bucket="frameworks", excerpts=["A"]),
        Source(id="b", url="https://x.com/p", kind="talk", bucket="talks", excerpts=["B"]),
    ]
    merged = _merge_and_dedupe(sources)
    assert len(merged) == 1
    m = merged[0]
    assert m.kind == "talk"
    assert m.bucket == "frameworks"  # first-seen bucket is preserved
    assert set(m.excerpts) == {"A", "B"}


def test_merge_fills_missing_title_and_date() -> None:
    sources = [
        Source(id="a", url="https://x.com/p", bucket="essays"),
        Source(
            id="b",
            url="https://x.com/p",
            title="The Title",
            publish_date="2024-01-01",
            bucket="essays",
        ),
    ]
    merged = _merge_and_dedupe(sources)
    assert merged[0].title == "The Title"
    assert merged[0].publish_date == "2024-01-01"


# ---------------------------------------------------------------------------
# _run_bucket
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_run_bucket_caches_and_skips_urlless_results(tmp_path: Path) -> None:
    bucket = BUCKETS[0]  # essays
    parallel = FakeParallelClient(
        default_search=make_search_result(
            [
                {"url": "https://example.com/a", "title": "Essay A", "excerpts": ["x"]},
                {"url": None, "title": "skip me"},  # no URL - dropped
                {
                    "url": "https://www.youtube.com/watch?v=abc",
                    "title": "Talk",
                    "publish_date": "2024-06-01",
                },
            ]
        )
    )
    ws = tmp_path / "discovery"
    ws.mkdir()
    sources = await _run_bucket(
        expert="Test",
        expert_description="the one",
        bucket=bucket,
        parallel=parallel,
        workspace=ws,
        refresh=False,
    )
    assert len(sources) == 2
    assert sources[0].id.startswith("essays_")
    assert sources[1].medium == "youtube"
    # Qualifier should be interpolated into the objective we sent parallel.
    assert "the one" in parallel.search_calls[0][0]

    # Cache file was written.
    cache = ws / "essays.json"
    assert cache.exists()

    # Second call with refresh=False reads cache, doesn't re-hit parallel.
    before = len(parallel.search_calls)
    sources2 = await _run_bucket(
        expert="Test",
        expert_description=None,
        bucket=bucket,
        parallel=parallel,
        workspace=ws,
        refresh=False,
    )
    assert [s.url for s in sources2] == [s.url for s in sources]
    assert len(parallel.search_calls) == before  # no new call


@pytest.mark.asyncio
async def test_run_bucket_refresh_ignores_cache(tmp_path: Path) -> None:
    bucket = BUCKETS[1]  # talks
    parallel = FakeParallelClient(default_search=make_search_result([]))
    ws = tmp_path / "discovery"
    ws.mkdir()
    (ws / "talks.json").write_text("[{\"id\": \"fake\"}]", encoding="utf-8")  # bogus cache
    # refresh=True forces a new call and overwrites the cache.
    sources = await _run_bucket(
        expert="E",
        expert_description=None,
        bucket=bucket,
        parallel=parallel,
        workspace=ws,
        refresh=True,
    )
    assert sources == []
    assert parallel.search_calls  # search was called


# ---------------------------------------------------------------------------
# _rank_and_trim
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rank_and_trim_skips_llm_when_already_under_target() -> None:
    sources = [Source(id="a", url="https://x.com/1", bucket="essays")]
    llm = FakeLLMClient()
    out = await _rank_and_trim(expert="E", expert_description=None, sources=sources, target=5, llm=llm)
    assert out == sources
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_rank_and_trim_applies_scores_and_trims() -> None:
    sources = [
        Source(id=f"src_{i:03d}", url=f"https://x.com/{i}", bucket="essays")
        for i in range(6)
    ]
    ranked = RankedSources(
        sources=[
            Source(id="src_005", url="x", canonicity_score=0.9, bucket="essays"),
            Source(id="src_000", url="x", canonicity_score=0.8, bucket="essays"),
            # Duplicate id should be ignored.
            Source(id="src_005", url="x", canonicity_score=0.7, bucket="essays"),
            # Unknown id should be ignored.
            Source(id="src_999", url="x", canonicity_score=0.6, bucket="essays"),
        ]
    )
    llm = FakeLLMClient()
    llm.queue_structured(RankedSources, ranked)
    out = await _rank_and_trim(expert="E", expert_description=None, sources=sources, target=4, llm=llm)
    # First two are the LLM's ranked picks.
    assert [s.id for s in out[:2]] == ["src_005", "src_000"]
    assert out[0].canonicity_score == 0.9
    # Remaining slots filled in original order, skipping already-seen ids.
    remaining_ids = {s.id for s in out[2:]}
    assert "src_005" not in remaining_ids and "src_000" not in remaining_ids
    assert len(out) == 4


@pytest.mark.asyncio
async def test_rank_and_trim_breaks_when_llm_returns_exact_target() -> None:
    sources = [
        Source(id=f"src_{i:03d}", url=f"https://x.com/{i}", bucket="essays")
        for i in range(6)
    ]
    ranked = RankedSources(
        sources=[
            Source(id="src_000", url="x", canonicity_score=0.9, bucket="essays"),
            Source(id="src_001", url="x", canonicity_score=0.8, bucket="essays"),
            # This third pick would normally be accepted, but target=2 triggers
            # the mid-loop break at line 350.
            Source(id="src_002", url="x", canonicity_score=0.7, bucket="essays"),
        ]
    )
    llm = FakeLLMClient()
    llm.queue_structured(RankedSources, ranked)
    out = await _rank_and_trim(expert="E", expert_description=None, sources=sources, target=2, llm=llm)
    assert [s.id for s in out] == ["src_000", "src_001"]


@pytest.mark.asyncio
async def test_rank_and_trim_tops_up_when_llm_underreturns() -> None:
    sources = [
        Source(id=f"src_{i:03d}", url=f"https://x.com/{i}", bucket="essays")
        for i in range(5)
    ]
    # LLM only returned 1; the function should top up from the original list.
    ranked = RankedSources(
        sources=[Source(id="src_002", url="x", canonicity_score=0.5, bucket="essays")]
    )
    llm = FakeLLMClient()
    llm.queue_structured(RankedSources, ranked)
    out = await _rank_and_trim(expert="E", expert_description=None, sources=sources, target=3, llm=llm)
    assert len(out) == 3
    assert out[0].id == "src_002"


# ---------------------------------------------------------------------------
# discover_sources end-to-end (with fakes)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_discover_sources_full_path(settings: Settings) -> None:
    # Each bucket gets its own single result.
    by_bucket = {
        "essays": make_search_result(
            [{"url": "https://a.com/1", "title": "Essay 1", "excerpts": ["x" * 100]}]
        ),
        "talks": make_search_result(
            [{"url": "https://www.youtube.com/watch?v=v1", "title": "Talk 1"}]
        ),
        "interviews": make_search_result(
            [{"url": "https://a.com/interview", "title": "Interview"}]
        ),
        "podcasts": make_search_result([]),
        "frameworks": make_search_result(
            [{"url": "https://a.com/frameworks", "title": "Frameworks"}]
        ),
        "books": make_search_result(
            [{"url": "https://a.com/book", "title": "Book"}]
        ),
    }
    parallel = FakeParallelClient(search_by_bucket=by_bucket)
    llm = FakeLLMClient()
    # 5 total sources, max_sources=5 -> rank_and_trim should early-return and
    # never need a ranked-sources payload.
    from mimeo.config import ensure_dirs
    ensure_dirs(settings)

    sources = await discover_sources(settings=settings, parallel=parallel, llm=llm)
    assert len(sources) == 5
    # Cache file was created.
    ranked_path = (
        settings.workspace_dir
        / "discovery"
        / f"ranked_sources.{settings.model_cache_id}.json"
    )
    assert ranked_path.exists()


@pytest.mark.asyncio
async def test_discover_sources_uses_cached_ranking(settings: Settings) -> None:
    from mimeo.config import ensure_dirs
    ensure_dirs(settings)
    cache_path = (
        settings.workspace_dir
        / "discovery"
        / f"ranked_sources.{settings.model_cache_id}.json"
    )
    cache_payload = [
        Source(id="src_000", url="https://cached", title="Cached", bucket="essays").model_dump()
    ]
    cache_path.write_text(json.dumps(cache_payload), encoding="utf-8")

    parallel = FakeParallelClient()  # if called, tests would fail since no results queued
    llm = FakeLLMClient()
    sources = await discover_sources(settings=settings, parallel=parallel, llm=llm)
    assert len(sources) == 1
    assert sources[0].url == "https://cached"
    assert parallel.search_calls == []  # cache short-circuits


@pytest.mark.asyncio
async def test_discover_sources_tolerates_bucket_failures(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A bucket raising should not fail the whole discovery."""
    from mimeo.config import ensure_dirs
    ensure_dirs(settings)

    class _PartiallyBroken(FakeParallelClient):
        async def search(self, **kwargs):  # type: ignore[override]
            obj = kwargs["objective"].lower()
            if "essays" in obj or "essay" in obj:
                raise RuntimeError("simulated failure")
            return make_search_result(
                [{"url": f"https://x.com/{obj[:5]}", "title": "t"}]
            )

    parallel = _PartiallyBroken()
    llm = FakeLLMClient()
    sources = await discover_sources(settings=settings, parallel=parallel, llm=llm)
    # Should have results from all non-essay buckets.
    assert len(sources) >= 1
    assert all("essays" not in (s.bucket or "") for s in sources)
