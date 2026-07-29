"""Offline tests for :mod:`mimeo.refine` — the critique loop."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.refine import refine_agents, refine_skill
from mimeo.schemas import AgentsOutput, CritiqueReport, SkillOutput

from .conftest import FakeLLMClient, sample_clustered_corpus

# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _skill(marker: str) -> SkillOutput:
    """A SkillOutput tagged so we can tell drafts apart."""
    return SkillOutput(
        skill_name="test-expert",
        description="Think like Test Expert.",
        skill_body=f"# {marker}\n",
        principles_md="# Principles\n",
        frameworks_md="# Frameworks\n",
        mental_models_md="# Mental models\n",
        quotes_md="# Quotes\n",
    )


def _agents(marker: str) -> AgentsOutput:
    return AgentsOutput(content=f"# Think like Test Expert\n\n{marker}\n")


def _critique(score: int) -> CritiqueReport:
    return CritiqueReport(overall_score=score, summary="s", issues=[])


def _settings(tmp_path: Path, **kw) -> Settings:
    s = Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=5,
        concurrency=2,
        **kw,
    )
    ensure_dirs(s)
    return s


# ---------------------------------------------------------------------------
# Refine OFF: reproduces historical behavior
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refine_off_with_critique_runs_single_pass(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=False, critique=True)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("draft0"))
    llm.queue_structured(CritiqueReport, _critique(7))

    output, report, trajectory = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert output.skill_body.strip() == "# draft0"
    assert report is not None and report.overall_score == 7
    assert trajectory == [7]
    # The single critique wrote the canonical report (write_report defaulted on).
    assert (s.workspace_dir / "critique_skill.md").exists()
    # No refine artifacts.
    assert not (s.workspace_dir / "refine_skill.md").exists()


@pytest.mark.asyncio
async def test_refine_off_without_critique_authors_only(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=False, critique=False)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("draft0"))

    output, report, trajectory = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert output.skill_body.strip() == "# draft0"
    assert report is None
    assert trajectory == []
    assert len(llm.structured_calls) == 1  # author only, no critique


# ---------------------------------------------------------------------------
# Refine ON
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_first_draft_meets_bar_skips_revision(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=8, max_revisions=2)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("draft0"))
    llm.queue_structured(CritiqueReport, _critique(9))

    output, report, trajectory = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert output.skill_body.strip() == "# draft0"
    assert report.overall_score == 9
    assert trajectory == [9]
    # Author + one critique only: no revision happened.
    assert len(llm.structured_calls) == 2
    # Refine artifacts written, and the canonical report reflects the best draft.
    assert (s.workspace_dir / "refine_skill.md").exists()
    persisted = CritiqueReport.model_validate_json(
        (s.workspace_dir / "critique_skill.json").read_text()
    )
    assert persisted.overall_score == 9


@pytest.mark.asyncio
async def test_revision_improves_and_is_selected(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=8, max_revisions=2)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("draft0"))
    llm.queue_structured(SkillOutput, _skill("draft1"))
    llm.queue_structured(CritiqueReport, _critique(5))  # draft0
    llm.queue_structured(CritiqueReport, _critique(9))  # draft1 clears the bar

    output, report, trajectory = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert output.skill_body.strip() == "# draft1"  # the improved revision shipped
    assert report.overall_score == 9
    assert trajectory == [5, 9]
    traj_md = (s.workspace_dir / "refine_skill.md").read_text()
    assert "5 → 9" in traj_md


@pytest.mark.asyncio
async def test_regression_keeps_best_and_stops(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=10, max_revisions=3)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("draft0"))
    llm.queue_structured(SkillOutput, _skill("draft1"))
    llm.queue_structured(CritiqueReport, _critique(7))  # draft0
    llm.queue_structured(CritiqueReport, _critique(6))  # draft1 regresses

    output, report, trajectory = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert output.skill_body.strip() == "# draft0"  # best draft kept
    assert report.overall_score == 7
    assert trajectory == [7, 6]
    # Stopped after one revision despite max_revisions=3 and bar unmet.
    assert len(llm.structured_calls) == 4


@pytest.mark.asyncio
async def test_max_revisions_zero_does_not_revise(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=8, max_revisions=0)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("draft0"))
    llm.queue_structured(CritiqueReport, _critique(3))

    output, _report, trajectory = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert output.skill_body.strip() == "# draft0"
    assert trajectory == [3]
    assert len(llm.structured_calls) == 2  # author + one critique, no revision


@pytest.mark.asyncio
async def test_no_critique_disables_refine(tmp_path: Path) -> None:
    """--no-critique is the master off-switch: author only, even with refine on."""
    s = _settings(tmp_path, refine=True, critique=False, quality_bar=8, max_revisions=1)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("draft0"))

    output, report, trajectory = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert output.skill_body.strip() == "# draft0"
    assert report is None and trajectory == []
    # Nothing critiqued or refined.
    assert len(llm.structured_calls) == 1
    assert not (s.workspace_dir / "critique_skill.md").exists()
    assert not (s.workspace_dir / "refine_skill.md").exists()


# ---------------------------------------------------------------------------
# Caching
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refined_cache_short_circuits_rerun(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=8, max_revisions=1)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("draft0"))
    llm.queue_structured(CritiqueReport, _critique(9))
    await refine_skill(corpus=sample_clustered_corpus(), settings=s, llm=llm)

    # Second run with an empty LLM: any structured call would raise. A clean
    # short-circuit means zero calls.
    fresh = FakeLLMClient()
    output, report, trajectory = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=fresh
    )
    assert output.skill_body.strip() == "# draft0"
    assert report is not None and report.overall_score == 9
    assert trajectory == [9]
    assert fresh.structured_calls == []


@pytest.mark.asyncio
async def test_refined_cache_misses_when_quality_settings_change(
    tmp_path: Path,
) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=8, max_revisions=0)
    corpus = sample_clustered_corpus()
    seeded = FakeLLMClient()
    seeded.queue_structured(SkillOutput, _skill("draft0"))
    seeded.queue_structured(CritiqueReport, _critique(9))
    await refine_skill(corpus=corpus, settings=s, llm=seeded)

    stricter = replace(s, quality_bar=10)
    fresh = FakeLLMClient()
    fresh.queue_structured(CritiqueReport, _critique(9))
    _output, report, trajectory = await refine_skill(
        corpus=corpus,
        settings=stricter,
        llm=fresh,
    )

    assert report is not None and report.overall_score == 9
    assert trajectory == [9]
    assert len(fresh.structured_calls) == 1


@pytest.mark.asyncio
async def test_refresh_ignores_refined_cache(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=8, max_revisions=0)
    cache = s.workspace_dir / "skill_output.refined.json"
    cache.write_text(_skill("stale").model_dump_json(), encoding="utf-8")

    s2 = replace(s, refresh=True)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("fresh"))
    llm.queue_structured(CritiqueReport, _critique(9))
    output, _report, _traj = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s2, llm=llm
    )
    assert output.skill_body.strip() == "# fresh"


@pytest.mark.asyncio
async def test_corrupt_refined_cache_re_refines(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=8, max_revisions=0)
    cache = s.workspace_dir / "skill_output.refined.json"
    seeded = FakeLLMClient()
    seeded.queue_structured(SkillOutput, _skill("stale"))
    seeded.queue_structured(CritiqueReport, _critique(9))
    await refine_skill(
        corpus=sample_clustered_corpus(),
        settings=s,
        llm=seeded,
    )
    payload = json.loads(cache.read_text(encoding="utf-8"))
    payload["data"] = []
    cache.write_text(json.dumps(payload), encoding="utf-8")
    (s.workspace_dir / "skill_output.json").unlink()

    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, _skill("rebuilt"))
    llm.queue_structured(CritiqueReport, _critique(9))
    output, _report, _traj = await refine_skill(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert output.skill_body.strip() == "# rebuilt"
    # Cache was overwritten with a valid envelope.
    payload = json.loads(cache.read_text(encoding="utf-8"))
    SkillOutput.model_validate(payload["data"]["output"])


# ---------------------------------------------------------------------------
# Agents variant
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refine_agents_loop(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=True, quality_bar=8, max_revisions=2)
    llm = FakeLLMClient()
    llm.queue_structured(AgentsOutput, _agents("draft0"))
    llm.queue_structured(AgentsOutput, _agents("draft1"))
    llm.queue_structured(CritiqueReport, _critique(6))
    llm.queue_structured(CritiqueReport, _critique(9))

    output, report, trajectory = await refine_agents(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert "draft1" in output.content
    assert report.overall_score == 9
    assert trajectory == [6, 9]
    assert (s.workspace_dir / "critique_agents.json").exists()
    assert (s.workspace_dir / "refine_agents.md").exists()


@pytest.mark.asyncio
async def test_refine_agents_off_authors_only(tmp_path: Path) -> None:
    s = _settings(tmp_path, refine=False, critique=False, format="agents")
    llm = FakeLLMClient()
    llm.queue_structured(AgentsOutput, _agents("draft0"))
    output, report, trajectory = await refine_agents(
        corpus=sample_clustered_corpus(), settings=s, llm=llm
    )
    assert "draft0" in output.content
    assert report is None and trajectory == []
