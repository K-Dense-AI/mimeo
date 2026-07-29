"""Stage 6.5: close the critique loop.

Authoring produces a draft; :mod:`mimeo.critique` grades it. Historically that
score was informational only. This module turns it into a feedback loop:

    author → critique → (if below the bar) re-author against the critique →
    critique again → keep the best-scoring draft.

The loop is bounded (``settings.max_revisions``), stops early once the score
clears ``settings.quality_bar`` or a revision fails to improve, and always
keeps the highest-scoring draft seen. It is on by default.

``settings.critique`` is the master switch:

* ``critique`` off → author once, no scoring (refine is meaningless without a
  score, so it is implicitly off too).
* ``critique`` on, ``refine`` off → a single critique pass (the historical
  ``--no-refine`` behavior).
* ``critique`` on, ``refine`` on → the full rewrite loop.

The best draft is cached under ``*_output.refined.<model>.json`` so a repeat
``--refine`` run short-circuits, and the best draft's critique is written to the
canonical ``_workspace/critique_<kind>.{json,md}`` so the on-disk report matches
the artifact that actually ships.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Literal, TypeVar

from pydantic import BaseModel

from .cache import fingerprint, load_cache, prompt_digest, schema_digest, store_cache
from .config import Settings
from .critique import (
    critique_agents,
    critique_skill,
    render_skill_artifact,
    write_report,
)
from .llm import LLMClient
from .schemas import AgentsOutput, ClusteredCorpus, CritiqueReport, SkillOutput
from .synthesize import author_agents, author_skill

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Return shape shared by both public entry points: the best draft, its critique
# (``None`` only when refine is off and critique is off, or on a cache hit), and
# the score for each iteration (draft first, then each revision).
RefineResult = tuple[T, CritiqueReport | None, list[int]]


async def refine_skill(
    *,
    corpus: ClusteredCorpus,
    settings: Settings,
    llm: LLMClient,
) -> RefineResult[SkillOutput]:
    """Author + (optionally) refine a SKILL.md bundle."""

    async def author_fn(
        *, feedback: CritiqueReport | None, previous_artifact: str | None
    ) -> SkillOutput:
        return await author_skill(
            corpus=corpus,
            settings=settings,
            llm=llm,
            feedback=feedback,
            previous_artifact=previous_artifact,
        )

    async def critique_fn(output: SkillOutput, *, write_report: bool) -> CritiqueReport:
        return await critique_skill(
            output=output,
            corpus=corpus,
            settings=settings,
            llm=llm,
            write_report=write_report,
        )

    return await _run_loop(
        kind="skill",
        corpus=corpus,
        settings=settings,
        author_fn=author_fn,
        critique_fn=critique_fn,
        render_artifact=render_skill_artifact,
        model_cls=SkillOutput,
    )


async def refine_agents(
    *,
    corpus: ClusteredCorpus,
    settings: Settings,
    llm: LLMClient,
) -> RefineResult[AgentsOutput]:
    """Author + (optionally) refine an AGENTS.md."""

    async def author_fn(
        *, feedback: CritiqueReport | None, previous_artifact: str | None
    ) -> AgentsOutput:
        return await author_agents(
            corpus=corpus,
            settings=settings,
            llm=llm,
            feedback=feedback,
            previous_artifact=previous_artifact,
        )

    async def critique_fn(
        output: AgentsOutput, *, write_report: bool
    ) -> CritiqueReport:
        return await critique_agents(
            output=output,
            corpus=corpus,
            settings=settings,
            llm=llm,
            write_report=write_report,
        )

    return await _run_loop(
        kind="agents",
        corpus=corpus,
        settings=settings,
        author_fn=author_fn,
        critique_fn=critique_fn,
        render_artifact=lambda o: o.content,
        model_cls=AgentsOutput,
    )


async def _run_loop(
    *,
    kind: Literal["skill", "agents"],
    corpus: ClusteredCorpus,
    settings: Settings,
    author_fn: Callable[..., Awaitable[T]],
    critique_fn: Callable[..., Awaitable[CritiqueReport]],
    render_artifact: Callable[[T], str],
    model_cls: type[T],
) -> RefineResult[T]:
    refined_cache = settings.workspace_dir / f"{kind}_output.refined.json"
    refined_fingerprint = fingerprint(
        f"refine-{kind}",
        code=2,
        expert=settings.expert_name,
        expert_description=settings.expert_description,
        model=settings.model,
        critique=settings.critique,
        refine=settings.refine,
        quality_bar=settings.quality_bar,
        max_revisions=settings.max_revisions,
        prompts=prompt_digest(
            "critique",
            "revision",
            "synthesize_skill" if kind == "skill" else "synthesize_agents",
        ),
        schemas=schema_digest(model_cls, CritiqueReport),
        corpus=corpus,
    )
    # The loop only runs (and only caches) when critique is on; --no-critique
    # is a hard off-switch for the whole quality stage.
    do_refine = settings.refine and settings.critique

    # A completed refine run is cached whole; a repeat run skips every LLM call.
    if do_refine and not settings.refresh:
        try:
            cached = load_cache(refined_cache, refined_fingerprint)
            if cached is not None:
                if not isinstance(cached, dict):
                    raise ValueError("refined cache payload must be an object")
                best = model_cls.model_validate(cached["output"])
                report = CritiqueReport.model_validate(cached["report"])
                trajectory = [int(score) for score in cached["trajectory"]]
                logger.info(
                    "Using cached refined %s output from %s", kind, refined_cache
                )
                write_report(report, settings=settings, kind=kind)
                _write_trajectory(
                    kind=kind,
                    trajectory=trajectory,
                    best=report.overall_score,
                    settings=settings,
                )
                return best, report, trajectory
        except Exception:  # noqa: BLE001 - validation failure is a safe miss
            logger.warning("Corrupt refined-%s cache; re-refining", kind)

    # Draft 0 uses the canonical author cache (feedback=None), so it is shared
    # across critique/refine/no-critique runs.
    best_output = await author_fn(feedback=None, previous_artifact=None)

    # --no-critique: author only, no scoring.
    if not settings.critique:
        return best_output, None, []

    # Critique on but refine off: a single critique pass.
    if not settings.refine:
        report = await critique_fn(best_output, write_report=True)
        return best_output, report, [report.overall_score]

    # Full loop. Intermediate reports are not written to disk.
    best_report = await critique_fn(best_output, write_report=False)
    trajectory = [best_report.overall_score]

    revisions = 0
    while (
        best_report.overall_score < settings.quality_bar
        and revisions < settings.max_revisions
    ):
        revisions += 1
        candidate = await author_fn(
            feedback=best_report,
            previous_artifact=render_artifact(best_output),
        )
        candidate_report = await critique_fn(candidate, write_report=False)
        trajectory.append(candidate_report.overall_score)
        if candidate_report.overall_score > best_report.overall_score:
            best_output, best_report = candidate, candidate_report
        else:
            # No improvement: keep the best so far and stop burning budget.
            logger.info(
                "Revision %d did not improve %s (%d <= %d); keeping best",
                revisions,
                kind,
                candidate_report.overall_score,
                best_report.overall_score,
            )
            break

    # The shipped artifact's report lives at the canonical path; the best draft
    # is cached for cheap re-runs; the trajectory is left as an audit trail.
    write_report(best_report, settings=settings, kind=kind)
    store_cache(
        refined_cache,
        refined_fingerprint,
        {
            "output": best_output,
            "report": best_report,
            "trajectory": trajectory,
        },
    )
    _write_trajectory(
        kind=kind,
        trajectory=trajectory,
        best=best_report.overall_score,
        settings=settings,
    )
    logger.info(
        "Refine (%s): %s → best %d/10 after %d revision(s)",
        kind,
        " → ".join(str(s) for s in trajectory),
        best_report.overall_score,
        revisions,
    )
    return best_output, best_report, trajectory


def _write_trajectory(
    *,
    kind: Literal["skill", "agents"],
    trajectory: list[int],
    best: int,
    settings: Settings,
) -> None:
    title = "SKILL.md" if kind == "skill" else "AGENTS.md"
    revisions = max(len(trajectory) - 1, 0)
    path: Path = settings.workspace_dir / f"refine_{kind}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Refinement trajectory: {title}",
        "",
        f"Scores (draft → revisions): {' → '.join(str(s) for s in trajectory)}",
        "",
        f"**Best:** {best}/10 after {revisions} revision(s) "
        f"(quality bar {settings.quality_bar}/10).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
