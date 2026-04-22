"""Offline end-to-end tests for :mod:`mimeo.pipeline`.

We drive the whole pipeline with injected fakes, covering each of the three
output formats plus the deep-research and empty-discovery branches.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from mimeo.config import Settings
from mimeo.pipeline import run_pipeline
from mimeo.schemas import (
    AgentsOutput,
    ClusteredCorpus,
    Extraction,
    FetchedContent,
    RankedSources,
    SkillOutput,
)

from .conftest import (
    FakeLLMClient,
    FakeParallelClient,
    make_search_result,
    sample_agents_output,
    sample_clustered_corpus,
    sample_extraction,
    sample_skill_output,
)


def _six_bucket_search() -> dict[str, Any]:
    """One result per bucket so discover_sources has 6 candidates."""
    return {
        "essays": make_search_result(
            [{"url": "https://a.com/e", "title": "Essay", "excerpts": ["x" * 3_000]}]
        ),
        "talks": make_search_result(
            [{"url": "https://a.com/t", "title": "Talk", "excerpts": ["x" * 3_000]}]
        ),
        "interviews": make_search_result(
            [{"url": "https://a.com/i", "title": "Interview", "excerpts": ["x" * 3_000]}]
        ),
        "podcasts": make_search_result(
            [{"url": "https://a.com/p", "title": "Podcast", "excerpts": ["x" * 3_000]}]
        ),
        "frameworks": make_search_result(
            [{"url": "https://a.com/f", "title": "Framework", "excerpts": ["x" * 3_000]}]
        ),
        "books": make_search_result(
            [{"url": "https://a.com/b", "title": "Book", "excerpts": ["x" * 3_000]}]
        ),
    }


def _build_llm(expert: str, *, include_skill: bool, include_agents: bool) -> FakeLLMClient:
    llm = FakeLLMClient()
    # 6 sources <= max_sources(6) so no ranking call needed; add one anyway as
    # a safety cushion (queue_structured entries are only consumed on demand).
    llm.queue_structured(RankedSources, RankedSources(sources=[]))
    for i in range(6):
        llm.queue_structured(Extraction, sample_extraction(f"src_{i:03d}"))
    llm.queue_structured(ClusteredCorpus, sample_clustered_corpus(expert))
    if include_skill:
        llm.queue_structured(SkillOutput, sample_skill_output())
    if include_agents:
        llm.queue_structured(AgentsOutput, sample_agents_output())
    return llm


@pytest.fixture
def full_settings(tmp_path: Path) -> Settings:
    # ``assume_unambiguous=True`` bypasses the identity-resolution pre-flight
    # that would otherwise demand its own Search + LLM round-trip.
    return Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
        assume_unambiguous=True,
    )


@pytest.mark.asyncio
async def test_pipeline_skill_format(full_settings: Settings) -> None:
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = _build_llm(full_settings.expert_name, include_skill=True, include_agents=False)

    stages: list[str] = []
    out = await run_pipeline(
        full_settings,
        parallel=parallel,
        llm=llm,
        on_stage=lambda name, _detail: stages.append(name),
    )
    assert out == full_settings.skill_dir
    assert (out / "SKILL.md").exists()
    assert (out / "references" / "principles.md").exists()
    assert not (out / "AGENTS.md").exists()
    # Stage labels should all count out of 5 (baseline 4 + 1 skill).
    assert all("/5" in s for s in stages)


@pytest.mark.asyncio
async def test_pipeline_agents_format(full_settings: Settings) -> None:
    full_settings_agents = Settings(
        expert_name=full_settings.expert_name,
        output_dir=full_settings.output_dir,
        max_sources=full_settings.max_sources,
        concurrency=full_settings.concurrency,
        format="agents",
        assume_unambiguous=True,
    )
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = _build_llm(full_settings.expert_name, include_skill=False, include_agents=True)

    out = await run_pipeline(full_settings_agents, parallel=parallel, llm=llm)
    assert (out / "AGENTS.md").exists()
    assert not (out / "SKILL.md").exists()


@pytest.mark.asyncio
async def test_pipeline_both_format_uses_six_stages(full_settings: Settings) -> None:
    both_settings = Settings(
        expert_name=full_settings.expert_name,
        output_dir=full_settings.output_dir,
        max_sources=full_settings.max_sources,
        concurrency=full_settings.concurrency,
        format="both",
        assume_unambiguous=True,
    )
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = _build_llm(full_settings.expert_name, include_skill=True, include_agents=True)

    stages: list[str] = []
    out = await run_pipeline(
        both_settings,
        parallel=parallel,
        llm=llm,
        on_stage=lambda name, _detail: stages.append(name),
    )
    assert (out / "SKILL.md").exists()
    assert (out / "AGENTS.md").exists()
    # Stage numerator runs 1..6 with author steps at 5 and 6.
    assert any(s.startswith("5/6 Author skill") for s in stages)
    assert any(s.startswith("6/6 Author AGENTS.md") for s in stages)
    # No duplicate stage number in the stream.
    author_labels = [s for s in stages if "Author" in s]
    assert len({s.split()[0] for s in author_labels}) == len(author_labels)


@pytest.mark.asyncio
async def test_pipeline_with_deep_research(full_settings: Settings) -> None:
    dr_settings = Settings(
        expert_name=full_settings.expert_name,
        output_dir=full_settings.output_dir,
        max_sources=full_settings.max_sources,
        concurrency=full_settings.concurrency,
        deep_research=True,
        assume_unambiguous=True,
    )
    parallel = FakeParallelClient(
        search_by_bucket=_six_bucket_search(),
        deep_research_result=SimpleNamespace(
            output=SimpleNamespace(content="Deep report body.")
        ),
    )
    llm = _build_llm(full_settings.expert_name, include_skill=True, include_agents=False)
    # One extra Extraction for the research pseudo-source.
    llm.queue_structured(Extraction, sample_extraction("src_research"))

    out = await run_pipeline(dr_settings, parallel=parallel, llm=llm)
    assert (out / "SKILL.md").exists()
    assert parallel.deep_research_calls, "deep_research should have been invoked"


@pytest.mark.asyncio
async def test_pipeline_with_deep_research_failure_is_tolerated(
    full_settings: Settings,
) -> None:
    dr_settings = Settings(
        expert_name=full_settings.expert_name,
        output_dir=full_settings.output_dir,
        max_sources=full_settings.max_sources,
        concurrency=full_settings.concurrency,
        deep_research=True,
        assume_unambiguous=True,
    )
    parallel = FakeParallelClient(
        search_by_bucket=_six_bucket_search(),
        deep_research_raises=RuntimeError("task down"),
    )
    llm = _build_llm(full_settings.expert_name, include_skill=True, include_agents=False)
    out = await run_pipeline(dr_settings, parallel=parallel, llm=llm)
    assert (out / "SKILL.md").exists()


@pytest.mark.asyncio
async def test_pipeline_raises_when_no_sources(full_settings: Settings) -> None:
    parallel = FakeParallelClient()  # every bucket returns empty
    llm = FakeLLMClient()
    with pytest.raises(RuntimeError, match="No sources discovered"):
        await run_pipeline(full_settings, parallel=parallel, llm=llm)


@pytest.mark.asyncio
async def test_pipeline_constructs_default_clients_when_omitted(
    full_settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When ``parallel``/``llm`` are ``None``, pipeline constructs real ones.

    We only check the construction happens — we short-circuit by patching
    ``discover_sources`` to an empty list so the pipeline exits early before
    making any network calls. ``assume_unambiguous`` skips identity resolution.
    """
    construct_log: list[str] = []

    def _fake_parallel_init(self):  # type: ignore[no-redef]
        construct_log.append("parallel")
        self._client = None

    def _fake_llm_init(self, model: str = "x"):  # type: ignore[no-redef]
        construct_log.append("llm")
        self.model = model
        self._client = None

    monkeypatch.setattr(
        "mimeo.pipeline.ParallelClient.__init__", _fake_parallel_init
    )
    monkeypatch.setattr("mimeo.pipeline.LLMClient.__init__", _fake_llm_init)

    async def _no_sources(**_: object):
        return []

    monkeypatch.setattr("mimeo.pipeline.discover_sources", _no_sources)

    with pytest.raises(RuntimeError, match="No sources discovered"):
        await run_pipeline(full_settings)

    assert construct_log == ["parallel", "llm"]


@pytest.mark.asyncio
async def test_pipeline_with_preset_expert_description_shows_qualifier(
    tmp_path: Path,
) -> None:
    """A preset ``expert_description`` flows into the banner and skips identity."""
    s = Settings(
        expert_name="Naval Ravikant",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
        expert_description="AngelList, investor",
    )
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = _build_llm("Naval Ravikant", include_skill=True, include_agents=False)

    out = await run_pipeline(s, parallel=parallel, llm=llm)
    assert (out / "SKILL.md").exists()


@pytest.mark.asyncio
async def test_pipeline_runs_identity_resolution_when_not_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without ``assume_unambiguous``, the identity stage is invoked."""
    from mimeo.schemas import IdentityResolution

    called: dict[str, int] = {"n": 0}

    async def _fake_resolve(*, settings, parallel, llm, console=None):
        called["n"] += 1
        from dataclasses import replace as _replace
        return _replace(settings, expert_description="the one")

    monkeypatch.setattr("mimeo.pipeline.resolve_identity", _fake_resolve)
    s = Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
    )
    parallel = FakeParallelClient()
    llm = FakeLLMClient()
    with pytest.raises(RuntimeError, match="No sources discovered"):
        await run_pipeline(s, parallel=parallel, llm=llm)
    assert called["n"] == 1
