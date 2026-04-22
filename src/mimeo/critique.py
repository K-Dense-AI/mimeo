"""Post-author critique: grade the generated artifact and surface issues.

After authoring a SKILL.md (and/or AGENTS.md), we run one more LLM pass
that plays the role of an adversarial editor. The critique is written to
``_workspace/critique.md`` as a human-readable report and to
``critique.json`` as a machine-readable :class:`CritiqueReport`.

We don't auto-rewrite based on the critique — that's a deliberate choice to
keep cost predictable. The critique is an artifact the human can read, not
an iterative rewrite loop.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

import yaml

from .config import Settings
from .llm import LLMClient, load_prompt, render_prompt
from .schemas import (
    AgentsOutput,
    ClusteredCorpus,
    CritiqueIssue,
    CritiqueReport,
    SkillOutput,
)

logger = logging.getLogger(__name__)

_ARTIFACT_CHAR_BUDGET = 40_000
_CORPUS_CHAR_BUDGET = 40_000


async def critique_skill(
    *,
    output: SkillOutput,
    corpus: ClusteredCorpus,
    settings: Settings,
    llm: LLMClient,
    write_report: bool = True,
) -> CritiqueReport:
    """Critique an authored SKILL.md + references bundle."""
    artifact = _render_skill_artifact(output)
    return await _critique(
        kind="skill",
        artifact=artifact,
        corpus=corpus,
        settings=settings,
        llm=llm,
        write_report=write_report,
    )


async def critique_agents(
    *,
    output: AgentsOutput,
    corpus: ClusteredCorpus,
    settings: Settings,
    llm: LLMClient,
    write_report: bool = True,
) -> CritiqueReport:
    """Critique an authored AGENTS.md."""
    return await _critique(
        kind="agents",
        artifact=output.content,
        corpus=corpus,
        settings=settings,
        llm=llm,
        write_report=write_report,
    )


async def _critique(
    *,
    kind: Literal["skill", "agents"],
    artifact: str,
    corpus: ClusteredCorpus,
    settings: Settings,
    llm: LLMClient,
    write_report: bool,
) -> CritiqueReport:
    template = load_prompt("critique")
    corpus_json = corpus.model_dump_json(indent=2, exclude_none=True)
    prompt = render_prompt(
        template,
        expert=settings.expert_name,
        expert_context=settings.expert_context,
        artifact=_truncate(artifact, _ARTIFACT_CHAR_BUDGET),
        corpus_json=_truncate(corpus_json, _CORPUS_CHAR_BUDGET),
    )
    system = (
        "You are an adversarial editor. You review drafts for voice, "
        "coverage, duplication, and accuracy. You are precise and concrete, "
        "never generic. Your job is to find real problems, not to reassure."
    )
    report = await llm.structured(
        system=system,
        user=prompt,
        schema=CritiqueReport,
        temperature=0.3,
        max_tokens=6_000,
    )

    if write_report:
        _write_report(report, settings=settings, kind=kind)
    logger.info(
        "Critique (%s): score %d/10, %d issues (%d high)",
        kind,
        report.overall_score,
        len(report.issues),
        sum(1 for i in report.issues if i.severity == "high"),
    )
    return report


def _render_skill_artifact(output: SkillOutput) -> str:
    """Assemble the authored skill into one text blob for the critic.

    We reconstruct roughly what the on-disk skill will look like so the
    reviewer judges what users will actually read rather than an abstract
    data structure.
    """
    frontmatter = yaml.safe_dump(
        {"name": output.skill_name, "description": output.description.strip()},
        sort_keys=False,
        allow_unicode=True,
        width=1000,
    ).strip()
    sections: list[str] = [
        f"---\n{frontmatter}\n---\n\n{output.skill_body.strip()}\n",
        f"\n---\n# references/principles.md\n\n{output.principles_md.strip()}\n",
        f"\n---\n# references/frameworks.md\n\n{output.frameworks_md.strip()}\n",
        f"\n---\n# references/mental-models.md\n\n{output.mental_models_md.strip()}\n",
        f"\n---\n# references/quotes.md\n\n{output.quotes_md.strip()}\n",
    ]
    if output.heuristics_md.strip():
        sections.append(
            f"\n---\n# references/heuristics.md\n\n{output.heuristics_md.strip()}\n"
        )
    if output.anti_patterns_md.strip():
        sections.append(
            f"\n---\n# references/anti-patterns.md\n\n{output.anti_patterns_md.strip()}\n"
        )
    return "".join(sections)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n... [truncated for length] ..."


def _write_report(
    report: CritiqueReport, *, settings: Settings, kind: Literal["skill", "agents"]
) -> None:
    json_path: Path = settings.workspace_dir / f"critique_{kind}.json"
    md_path: Path = settings.workspace_dir / f"critique_{kind}.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(report, kind=kind), encoding="utf-8")


def _render_markdown(
    report: CritiqueReport, *, kind: Literal["skill", "agents"]
) -> str:
    title = "SKILL.md" if kind == "skill" else "AGENTS.md"
    lines: list[str] = [
        f"# Critique of {title}",
        "",
        f"**Score:** {report.overall_score}/10",
        "",
        report.summary.strip(),
        "",
    ]
    if report.strengths:
        lines.append("## Strengths")
        lines.append("")
        for s in report.strengths:
            lines.append(f"- {s}")
        lines.append("")
    if report.issues:
        lines.append("## Issues")
        lines.append("")
        buckets: dict[str, list[CritiqueIssue]] = {"high": [], "medium": [], "low": []}
        for issue in report.issues:
            buckets.setdefault(issue.severity, []).append(issue)
        for severity in ("high", "medium", "low"):
            items = buckets.get(severity, [])
            if not items:
                continue
            lines.append(f"### {severity.title()}")
            lines.append("")
            for issue in items:
                lines.append(f"- **[{issue.category}]** _{issue.location}_")
                lines.append(f"  - {issue.description}")
                if issue.suggestion:
                    lines.append(f"  - _Suggestion:_ {issue.suggestion}")
            lines.append("")
    else:
        lines.append("_No issues reported._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
