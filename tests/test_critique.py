"""Offline tests for :mod:`mimeo.critique`."""

from __future__ import annotations

from pathlib import Path

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.critique import (
    _render_markdown,
    _render_skill_artifact,
    critique_agents,
    critique_skill,
)
from mimeo.schemas import CritiqueIssue, CritiqueReport

from .conftest import (
    FakeLLMClient,
    sample_agents_output,
    sample_clustered_corpus,
    sample_skill_output,
)


def _report(score: int = 7) -> CritiqueReport:
    return CritiqueReport(
        overall_score=score,
        summary="Mostly fine; two voice issues and one structural one.",
        issues=[
            CritiqueIssue(
                severity="high",
                category="voice",
                location="SKILL.md > Core principles",
                description="Principle #3 reads like generic motivational copy.",
                suggestion="Anchor it to the leverage concept explicitly.",
            ),
            CritiqueIssue(
                severity="medium",
                category="duplication",
                location="references/principles.md",
                description="Principles 2 and 5 cover the same ground.",
            ),
            CritiqueIssue(
                severity="low",
                category="structure",
                location="SKILL.md",
                description="Minor H2 spacing inconsistency.",
            ),
        ],
        strengths=["Clear trigger description.", "Good source attribution."],
    )


@pytest.mark.asyncio
async def test_critique_skill_writes_report(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path)
    ensure_dirs(settings)
    llm = FakeLLMClient()
    llm.queue_structured(CritiqueReport, _report())

    report = await critique_skill(
        output=sample_skill_output(),
        corpus=sample_clustered_corpus(),
        settings=settings,
        llm=llm,
    )
    assert report.overall_score == 7
    assert (settings.workspace_dir / "critique_skill.md").exists()
    assert (settings.workspace_dir / "critique_skill.json").exists()


@pytest.mark.asyncio
async def test_critique_agents_writes_report(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path)
    ensure_dirs(settings)
    llm = FakeLLMClient()
    llm.queue_structured(CritiqueReport, _report(score=9))

    report = await critique_agents(
        output=sample_agents_output(),
        corpus=sample_clustered_corpus(),
        settings=settings,
        llm=llm,
    )
    assert report.overall_score == 9
    assert (settings.workspace_dir / "critique_agents.md").exists()
    assert (settings.workspace_dir / "critique_agents.json").exists()


@pytest.mark.asyncio
async def test_critique_skill_suppresses_report_when_asked(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path)
    ensure_dirs(settings)
    llm = FakeLLMClient()
    llm.queue_structured(CritiqueReport, _report())

    await critique_skill(
        output=sample_skill_output(),
        corpus=sample_clustered_corpus(),
        settings=settings,
        llm=llm,
        write_report=False,
    )
    assert not (settings.workspace_dir / "critique_skill.md").exists()


def test_render_skill_artifact_includes_references() -> None:
    artifact = _render_skill_artifact(sample_skill_output())
    assert "references/principles.md" in artifact
    assert "references/heuristics.md" in artifact
    assert "references/anti-patterns.md" in artifact


def test_render_markdown_groups_issues_by_severity() -> None:
    md = _render_markdown(_report(), kind="skill")
    assert "### High" in md
    assert "### Medium" in md
    assert "### Low" in md
    assert "Strengths" in md
    assert "Score:** 7/10" in md


def test_render_markdown_handles_no_issues() -> None:
    md = _render_markdown(
        CritiqueReport(overall_score=10, summary="Clean.", issues=[], strengths=[]),
        kind="agents",
    )
    assert "No issues reported." in md


def test_render_markdown_skips_empty_severity_buckets() -> None:
    """A report with only medium issues should not render empty High/Low headers."""
    report = CritiqueReport(
        overall_score=6,
        summary="Only mediums.",
        issues=[
            CritiqueIssue(
                severity="medium",
                category="vagueness",
                location="X",
                description="d",
            )
        ],
    )
    md = _render_markdown(report, kind="skill")
    assert "### Medium" in md
    assert "### High" not in md
    assert "### Low" not in md


def test_render_skill_artifact_without_heuristics_or_anti_patterns() -> None:
    """Empty heuristics/anti-patterns sections are omitted from the artifact."""
    from mimeo.schemas import SkillOutput

    bare = SkillOutput(
        skill_name="x",
        description="d",
        skill_body="# b",
        principles_md="# p",
        frameworks_md="# f",
        mental_models_md="# m",
        quotes_md="# q",
        heuristics_md="",
        anti_patterns_md="   ",
    )
    artifact = _render_skill_artifact(bare)
    assert "references/heuristics.md" not in artifact
    assert "references/anti-patterns.md" not in artifact


@pytest.mark.asyncio
async def test_critique_skill_truncates_oversize_inputs(tmp_path: Path) -> None:
    """Artifact/corpus over the per-prompt budget is truncated, not dropped."""
    from mimeo.schemas import ClusteredCorpus, ClusteredItem, Principle, SkillOutput

    settings = Settings(expert_name="E", output_dir=tmp_path)
    ensure_dirs(settings)
    giant = "A" * 100_000
    output = SkillOutput(
        skill_name="x",
        description="d",
        skill_body=giant,
        principles_md="# p",
        frameworks_md="# f",
        mental_models_md="# m",
        quotes_md="# q",
    )
    # Build a big corpus to exercise the corpus truncation branch too.
    big_corpus = ClusteredCorpus(
        expert_name="E",
        principles=[
            ClusteredItem(
                label=f"Idea {i}",
                summary="a" * 200,
                source_ids=[f"src_{i:03d}"],
            )
            for i in range(500)
        ],
    )
    llm = FakeLLMClient()
    llm.queue_structured(CritiqueReport, _report())
    await critique_skill(
        output=output, corpus=big_corpus, settings=settings, llm=llm
    )
    # The prompt we handed to the LLM contains the truncation marker.
    _schema, user, _system = llm.structured_calls[0]
    assert "[truncated for length]" in user
