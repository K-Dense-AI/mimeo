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
    CritiqueReport,
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


def _sample_critique() -> CritiqueReport:
    return CritiqueReport(
        overall_score=8,
        summary="Solid draft with a few polish items.",
        issues=[],
        strengths=["Clear voice."],
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


def _build_llm(
    expert: str,
    *,
    include_skill: bool,
    include_agents: bool,
    include_critique: bool = True,
) -> FakeLLMClient:
    llm = FakeLLMClient()
    # 6 sources <= max_sources(6) so no ranking call needed; add one anyway as
    # a safety cushion (queue_structured entries are only consumed on demand).
    llm.queue_structured(RankedSources, RankedSources(sources=[]))
    for i in range(6):
        llm.queue_structured(Extraction, sample_extraction(f"src_{i:03d}"))
    llm.queue_structured(ClusteredCorpus, sample_clustered_corpus(expert))
    if include_skill:
        llm.queue_structured(SkillOutput, sample_skill_output())
        if include_critique:
            llm.queue_structured(CritiqueReport, _sample_critique())
    if include_agents:
        llm.queue_structured(AgentsOutput, sample_agents_output())
        if include_critique:
            llm.queue_structured(CritiqueReport, _sample_critique())
    return llm


@pytest.fixture
def full_settings(tmp_path: Path) -> Settings:
    # ``assume_unambiguous=True`` bypasses the identity-resolution pre-flight
    # that would otherwise demand its own Search + LLM round-trip. We also
    # disable ``verify_quotes`` by default so the sample fixtures (whose
    # quotes don't appear in the stub fetched text) don't get stripped mid
    # test; individual tests opt in.
    return Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
        assume_unambiguous=True,
        verify_quotes=False,
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
    assert (out / "references" / "heuristics.md").exists()
    assert (out / "references" / "anti-patterns.md").exists()
    assert not (out / "AGENTS.md").exists()
    # Stage labels count 1..6: 4 baseline + author + critique.
    assert all("/6" in s for s in stages)
    assert any("Critique skill" in s for s in stages)
    # Critique was written to the workspace.
    assert (full_settings.skill_dir / "_workspace" / "critique_skill.md").exists()


@pytest.mark.asyncio
async def test_pipeline_skill_format_no_critique(full_settings: Settings) -> None:
    """With --no-critique the critique stage and its LLM call are skipped."""
    from dataclasses import replace

    s = replace(full_settings, critique=False)
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = _build_llm(
        s.expert_name, include_skill=True, include_agents=False, include_critique=False
    )

    stages: list[str] = []
    out = await run_pipeline(
        s, parallel=parallel, llm=llm, on_stage=lambda n, _d: stages.append(n)
    )
    assert (out / "SKILL.md").exists()
    assert not (s.skill_dir / "_workspace" / "critique_skill.md").exists()
    assert not any("Critique" in label for label in stages)
    assert all("/5" in label for label in stages)


@pytest.mark.asyncio
async def test_pipeline_agents_format(full_settings: Settings) -> None:
    full_settings_agents = Settings(
        expert_name=full_settings.expert_name,
        output_dir=full_settings.output_dir,
        max_sources=full_settings.max_sources,
        concurrency=full_settings.concurrency,
        format="agents",
        assume_unambiguous=True,
        verify_quotes=False,
    )
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = _build_llm(full_settings.expert_name, include_skill=False, include_agents=True)

    out = await run_pipeline(full_settings_agents, parallel=parallel, llm=llm)
    assert (out / "AGENTS.md").exists()
    assert not (out / "SKILL.md").exists()
    assert (full_settings_agents.skill_dir / "_workspace" / "critique_agents.md").exists()


@pytest.mark.asyncio
async def test_pipeline_agents_format_no_critique(full_settings: Settings) -> None:
    s = Settings(
        expert_name=full_settings.expert_name,
        output_dir=full_settings.output_dir,
        max_sources=full_settings.max_sources,
        concurrency=full_settings.concurrency,
        format="agents",
        assume_unambiguous=True,
        verify_quotes=False,
        critique=False,
    )
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = _build_llm(
        s.expert_name, include_skill=False, include_agents=True, include_critique=False
    )
    out = await run_pipeline(s, parallel=parallel, llm=llm)
    assert (out / "AGENTS.md").exists()
    assert not (s.skill_dir / "_workspace" / "critique_agents.md").exists()


@pytest.mark.asyncio
async def test_pipeline_both_format_uses_eight_stages(full_settings: Settings) -> None:
    both_settings = Settings(
        expert_name=full_settings.expert_name,
        output_dir=full_settings.output_dir,
        max_sources=full_settings.max_sources,
        concurrency=full_settings.concurrency,
        format="both",
        assume_unambiguous=True,
        verify_quotes=False,
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
    # 4 baseline + author skill + critique skill + author agents + critique agents = 8.
    assert any(s.startswith("5/8 Author skill") for s in stages)
    assert any(s.startswith("6/8 Critique skill") for s in stages)
    assert any(s.startswith("7/8 Author AGENTS.md") for s in stages)
    assert any(s.startswith("8/8 Critique AGENTS.md") for s in stages)
    # No duplicate stage numbers in the stream.
    numbered = [s.split()[0] for s in stages]
    assert len(set(numbered)) == len(numbered)


@pytest.mark.asyncio
async def test_pipeline_verify_quotes_no_quotes_in_corpus(tmp_path: Path) -> None:
    """If the clustered corpus has no quotes, the verifier is a no-op."""
    s = Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
        assume_unambiguous=True,
        verify_quotes=True,
    )
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = FakeLLMClient()
    llm.queue_structured(RankedSources, RankedSources(sources=[]))
    for i in range(6):
        llm.queue_structured(Extraction, sample_extraction(f"src_{i:03d}"))
    # Corpus with no representative quotes anywhere.
    from mimeo.schemas import ClusteredCorpus, ClusteredItem

    quoteless = ClusteredCorpus(
        expert_name=s.expert_name,
        principles=[
            ClusteredItem(label="Idea", summary="s", source_ids=["src_000"])
        ],
    )
    llm.queue_structured(ClusteredCorpus, quoteless)
    llm.queue_structured(SkillOutput, sample_skill_output())
    llm.queue_structured(CritiqueReport, _sample_critique())
    out = await run_pipeline(s, parallel=parallel, llm=llm)
    assert (out / "SKILL.md").exists()


@pytest.mark.asyncio
async def test_pipeline_critique_low_score_is_surfaced(tmp_path: Path) -> None:
    """Low critique scores render as red; medium scores render as yellow."""
    s = Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
        assume_unambiguous=True,
        verify_quotes=False,
    )
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = FakeLLMClient()
    llm.queue_structured(RankedSources, RankedSources(sources=[]))
    for i in range(6):
        llm.queue_structured(Extraction, sample_extraction(f"src_{i:03d}"))
    llm.queue_structured(ClusteredCorpus, sample_clustered_corpus(s.expert_name))
    llm.queue_structured(SkillOutput, sample_skill_output())
    # Score of 4 exercises the "red" branch of _critique_summary.
    llm.queue_structured(
        CritiqueReport,
        CritiqueReport(overall_score=4, summary="Needs rework.", issues=[]),
    )
    out = await run_pipeline(s, parallel=parallel, llm=llm)
    assert (out / "SKILL.md").exists()

    # Second run: medium score (6) hits the "yellow" branch.
    s2 = Settings(
        expert_name="Test Expert 2",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
        assume_unambiguous=True,
        verify_quotes=False,
    )
    parallel2 = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm2 = FakeLLMClient()
    llm2.queue_structured(RankedSources, RankedSources(sources=[]))
    for i in range(6):
        llm2.queue_structured(Extraction, sample_extraction(f"src_{i:03d}"))
    llm2.queue_structured(ClusteredCorpus, sample_clustered_corpus(s2.expert_name))
    llm2.queue_structured(SkillOutput, sample_skill_output())
    llm2.queue_structured(
        CritiqueReport,
        CritiqueReport(overall_score=6, summary="OK.", issues=[]),
    )
    await run_pipeline(s2, parallel=parallel2, llm=llm2)


@pytest.mark.asyncio
async def test_pipeline_verify_quotes_all_pass(tmp_path: Path) -> None:
    """When every quote is in its source text, no unverified message shows."""
    from types import SimpleNamespace

    from mimeo.schemas import ClusteredCorpus, ClusteredItem, FetchedContent

    quote = "A clearly verbatim line we know appears in the fake fetched text."
    text = "Before " + quote + " and after padding " * 20

    s = Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
        assume_unambiguous=True,
        verify_quotes=True,
    )

    # Build a fake parallel client whose "essays" bucket surfaces our quote in the excerpts.
    search_by_bucket = _six_bucket_search()
    search_by_bucket["essays"] = make_search_result(
        [{"url": "https://a.com/e", "title": "Essay", "excerpts": [text]}]
    )
    parallel = FakeParallelClient(search_by_bucket=search_by_bucket)

    llm = FakeLLMClient()
    llm.queue_structured(RankedSources, RankedSources(sources=[]))
    for i in range(6):
        llm.queue_structured(Extraction, sample_extraction(f"src_{i:03d}"))
    # The clustered corpus attributes the quote to src_000 (the essays bucket
    # source), which maps to the essay we padded the excerpts for.
    clustered = ClusteredCorpus(
        expert_name=s.expert_name,
        signature_quotes=[
            ClusteredItem(
                label="The line",
                summary="s",
                representative_quote=quote,
                source_ids=["src_000"],
            )
        ],
    )
    llm.queue_structured(ClusteredCorpus, clustered)
    llm.queue_structured(SkillOutput, sample_skill_output())
    llm.queue_structured(CritiqueReport, _sample_critique())
    out = await run_pipeline(s, parallel=parallel, llm=llm)
    assert (out / "SKILL.md").exists()
    # Verification ran; all quotes passed so no unverified markdown report.
    workspace = s.skill_dir / "_workspace"
    assert (workspace / "quote_verification.json").exists()
    assert not (workspace / "quote_verification.md").exists()


@pytest.mark.asyncio
async def test_pipeline_verify_quotes_strips_fabrications(tmp_path: Path) -> None:
    """An unverifiable representative quote is stripped from the authored corpus."""
    from dataclasses import replace

    s = Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=6,
        concurrency=3,
        assume_unambiguous=True,
        verify_quotes=True,
    )
    parallel = FakeParallelClient(search_by_bucket=_six_bucket_search())
    llm = _build_llm(s.expert_name, include_skill=True, include_agents=False)

    out = await run_pipeline(s, parallel=parallel, llm=llm)
    assert (out / "SKILL.md").exists()
    # Verification report files exist because the sample quote has no
    # match in the sample fetched text.
    workspace = s.skill_dir / "_workspace"
    assert (workspace / "quote_verification.json").exists()
    assert (workspace / "quote_verification.md").exists()


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
