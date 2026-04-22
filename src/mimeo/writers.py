"""Write a :class:`SkillOutput` to disk as a skill-creator-compliant directory."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from .config import Settings
from .schemas import AgentsOutput, SkillOutput, Source

logger = logging.getLogger(__name__)


def write_skill(
    *,
    output: SkillOutput,
    sources: list[Source],
    settings: Settings,
) -> Path:
    """Write SKILL.md + references/*.md; returns the skill directory path."""

    skill_dir = settings.skill_dir
    skill_dir.mkdir(parents=True, exist_ok=True)
    settings.references_dir.mkdir(parents=True, exist_ok=True)

    skill_md_path = skill_dir / "SKILL.md"
    skill_md_path.write_text(
        _assemble_skill_md(output),
        encoding="utf-8",
    )

    (settings.references_dir / "principles.md").write_text(
        output.principles_md.strip() + "\n", encoding="utf-8"
    )
    (settings.references_dir / "frameworks.md").write_text(
        output.frameworks_md.strip() + "\n", encoding="utf-8"
    )
    (settings.references_dir / "mental-models.md").write_text(
        output.mental_models_md.strip() + "\n", encoding="utf-8"
    )
    (settings.references_dir / "quotes.md").write_text(
        output.quotes_md.strip() + "\n", encoding="utf-8"
    )
    # heuristics / anti-patterns are optional: models historically produced
    # empty strings on corpora that didn't surface those categories. We still
    # write the file so the SKILL.md references resolve, but fall back to a
    # short placeholder so the reader isn't staring at a blank page.
    (settings.references_dir / "heuristics.md").write_text(
        _nonempty_markdown(
            output.heuristics_md,
            placeholder=(
                "# Heuristics\n\n"
                "No distinctive rules of thumb surfaced from the corpus for "
                f"{settings.expert_name}.\n"
            ),
        ),
        encoding="utf-8",
    )
    (settings.references_dir / "anti-patterns.md").write_text(
        _nonempty_markdown(
            output.anti_patterns_md,
            placeholder=(
                "# Anti-patterns\n\n"
                "No explicit anti-patterns surfaced from the corpus for "
                f"{settings.expert_name}.\n"
            ),
        ),
        encoding="utf-8",
    )
    (settings.references_dir / "sources.md").write_text(
        _render_sources(sources, expert=settings.expert_name),
        encoding="utf-8",
    )
    logger.info("Skill written to %s", skill_dir)
    return skill_dir


def write_agents(
    *,
    output: AgentsOutput,
    sources: list[Source],
    settings: Settings,
) -> Path:
    """Write AGENTS.md to the skill directory.

    The sources bibliography is appended as an inline section (rather than a
    separate file) since AGENTS.md is a single self-contained document.
    Returns the path to AGENTS.md.
    """
    skill_dir = settings.skill_dir
    skill_dir.mkdir(parents=True, exist_ok=True)

    content = output.content.rstrip()
    # Append the sources section if the model didn't include one already.
    if "## Sources" not in content and "# Sources" not in content:
        content = f"{content}\n\n{_render_sources_inline(sources, expert=settings.expert_name)}"
    else:
        content = f"{content}\n"

    agents_path = skill_dir / "AGENTS.md"
    agents_path.write_text(content.rstrip() + "\n", encoding="utf-8")
    logger.info("AGENTS.md written to %s", agents_path)
    return agents_path


def _render_sources_inline(sources: list[Source], *, expert: str) -> str:
    lines = [
        "## Sources",
        "",
        f"Grounded in the following {len(sources)} sources by or about {expert}. "
        "Ids match the `(src_XXX)` attributions above.",
        "",
    ]
    for s in sources:
        title = s.title or "(untitled)"
        bucket = f" — _{s.bucket}_" if s.bucket else ""
        score = f" (score {s.canonicity_score:.2f})" if s.canonicity_score is not None else ""
        date = f" [{s.publish_date}]" if s.publish_date else ""
        lines.append(f"- **{s.id}**{bucket}{score}: [{title}]({s.url}){date}")
    return "\n".join(lines)


def _nonempty_markdown(text: str, *, placeholder: str) -> str:
    stripped = text.strip()
    if not stripped:
        return placeholder
    return stripped + "\n"


def _assemble_skill_md(output: SkillOutput) -> str:
    frontmatter = yaml.safe_dump(
        {"name": output.skill_name, "description": output.description.strip()},
        sort_keys=False,
        allow_unicode=True,
        width=1000,
    ).strip()
    body = output.skill_body.strip()
    return f"---\n{frontmatter}\n---\n\n{body}\n"


def _render_sources(sources: list[Source], *, expert: str) -> str:
    lines = [
        f"# Sources used for {expert}",
        "",
        "Every source consulted while building this skill, in rank order. Ids "
        "match the attributions in the other reference files.",
        "",
    ]
    for s in sources:
        title = s.title or "(untitled)"
        bucket = f" — _{s.bucket}_" if s.bucket else ""
        score = f" (score {s.canonicity_score:.2f})" if s.canonicity_score is not None else ""
        date = f" [{s.publish_date}]" if s.publish_date else ""
        lines.append(f"- **{s.id}**{bucket}{score}: [{title}]({s.url}){date}")
    lines.append("")
    return "\n".join(lines)
