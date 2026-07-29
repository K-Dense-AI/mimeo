"""Orchestrator: run all stages end-to-end for one expert."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .avatar import generate_avatar
from .cache import store_cache
from .config import Settings, ensure_dirs
from .discovery import discover_sources
from .distill import distill_all
from .fetchers import fetch_all
from .identity import resolve_identity
from .llm import LLMClient
from .parallel_client import ParallelClient
from .refine import refine_agents, refine_skill
from .research import deep_research
from .schemas import CritiqueReport, Extraction, FetchedContent, Source
from .synthesize import cluster_cache_fingerprint, cluster_corpus
from .verify import verify_quotes
from .writers import write_agents, write_skill

logger = logging.getLogger(__name__)


async def run_pipeline(
    settings: Settings,
    *,
    console: Console | None = None,
    on_stage: Callable[[str, str], None] | None = None,
    parallel: ParallelClient | None = None,
    llm: LLMClient | None = None,
) -> Path:
    """Run the whole pipeline and return the path to the generated skill.

    ``parallel`` and ``llm`` are injectable so tests can pass fakes. In real
    use both default to freshly constructed clients that read their API keys
    from the environment.
    """

    console = console or Console()
    ensure_dirs(settings)
    run_started = time.perf_counter()
    stage_seconds: dict[str, float] = {}
    quality_summary: dict[str, dict[str, object]] = {}
    verification_summary: dict[str, object] | None = None
    avatar_status = "disabled"

    def stage(name: str, detail: str = "") -> None:
        console.rule(f"[bold cyan]{name}")
        if detail:
            console.print(detail)
        if on_stage:
            on_stage(name, detail)

    expert_line = settings.expert_name
    if settings.expert_description:
        expert_line = f"{settings.expert_name} ({settings.expert_description})"
    console.print(
        Panel(
            (
                f"[bold]Expert:[/bold] {expert_line}\n"
                f"[bold]Format:[/bold] {settings.format}\n"
                f"[bold]Mode:[/bold] {settings.mode}\n"
                f"[bold]Max sources:[/bold] {settings.max_sources}\n"
                f"[bold]Deep research:[/bold] {'yes' if settings.deep_research else 'no'}\n"
                f"[bold]Verify quotes:[/bold] {'yes' if settings.verify_quotes else 'no'}\n"
                f"[bold]Critique:[/bold] {'yes' if settings.critique else 'no'}\n"
                f"[bold]Refine:[/bold] {('yes (bar ' + str(settings.quality_bar) + '/10, up to ' + str(settings.max_revisions) + ' rev)') if settings.refine else 'no'}\n"
                f"[bold]Avatar:[/bold] {'yes (' + settings.avatar_model + ')' if settings.generate_avatar else 'no'}\n"
                f"[bold]Model:[/bold] {settings.model}\n"
                f"[bold]Output:[/bold] {settings.skill_dir}"
            ),
            title="mimeo",
            border_style="cyan",
        )
    )

    if parallel is None:
        parallel = ParallelClient()
    if llm is None:
        llm = LLMClient(model=settings.model)

    # Stage 0: disambiguate the name before spending money on discovery.
    # Cheap (one search + one LLM call) and short-circuits with an error
    # instead of silently blending two different people's work.
    stage_started = time.perf_counter()
    settings = await resolve_identity(
        settings=settings, parallel=parallel, llm=llm, console=console
    )
    stage_seconds["identity"] = time.perf_counter() - stage_started

    write_skill_flag = settings.format in ("skill", "both")
    write_agents_flag = settings.format in ("agents", "both")
    # Baseline = discover, fetch, distill, cluster. Refinement is part of each
    # artifact's authoring stage, so progress reflects actual execution.
    # Verify-quotes is a side-step and doesn't count. Deep research is the
    # same.
    total_stages = 4 + int(write_skill_flag) + int(write_agents_flag)

    stage(
        f"1/{total_stages} Discovery",
        "Searching across essays, talks, interviews, podcasts, frameworks, books...",
    )
    stage_started = time.perf_counter()
    sources: list[Source] = await discover_sources(
        settings=settings, parallel=parallel, llm=llm
    )
    stage_seconds["discovery"] = time.perf_counter() - stage_started
    discovered_count = len(sources)
    console.print(f"Selected [bold]{len(sources)}[/bold] sources.")
    if not sources:
        raise RuntimeError(
            "No sources discovered. Check PARALLEL_API_KEY and the expert name."
        )

    stage(f"2/{total_stages} Fetch", "Fetching full content for each source...")
    stage_started = time.perf_counter()
    fetched: list[FetchedContent] = await fetch_all(
        sources, settings=settings, parallel=parallel
    )
    stage_seconds["fetch"] = time.perf_counter() - stage_started
    primary_fetched_count = len(fetched)
    console.print(
        f"Fetched content for [bold]{len(fetched)}[/bold] / {len(sources)} sources "
        f"({sum(f.char_count for f in fetched):,} chars total)."
    )
    if not fetched:
        raise RuntimeError(
            "No usable source content was fetched. Check source availability and fetch settings."
        )

    if settings.deep_research:
        stage(
            f"2.5/{total_stages} Deep research",
            "Running Parallel Task API pro-fast (this can take a few minutes)...",
        )
        stage_started = time.perf_counter()
        pair = await deep_research(settings=settings, parallel=parallel)
        stage_seconds["deep_research"] = time.perf_counter() - stage_started
        if pair:
            research_source, research_content = pair
            sources.append(research_source)
            fetched.append(research_content)
            console.print(
                f"Deep-research report added as [bold]{research_source.id}[/bold] "
                f"({research_content.char_count:,} chars)."
            )
        else:
            console.print(
                "[yellow]Deep research failed or returned empty; continuing without it.[/yellow]"
            )

    stage(
        f"3/{total_stages} Distill",
        "Extracting principles, frameworks, and quotes from each source...",
    )
    stage_started = time.perf_counter()
    extractions: list[Extraction] = await distill_all(
        sources=sources, fetched=fetched, settings=settings, llm=llm
    )
    stage_seconds["distill"] = time.perf_counter() - stage_started
    console.print(
        f"Distilled [bold]{len(extractions)}[/bold] sources into structured extractions."
    )
    if not extractions:
        raise RuntimeError(
            "No usable extractions were produced. Check fetched content and model responses."
        )

    stage(f"4/{total_stages} Cluster", "Merging extractions into a unified corpus...")
    stage_started = time.perf_counter()
    corpus = await cluster_corpus(extractions=extractions, settings=settings, llm=llm)
    stage_seconds["cluster"] = time.perf_counter() - stage_started
    console.print(
        f"Clustered into {len(corpus.principles)} principles, "
        f"{len(corpus.frameworks)} frameworks, "
        f"{len(corpus.mental_models)} mental models, "
        f"{len(corpus.signature_quotes)} quotes."
    )

    if settings.verify_quotes:
        console.rule("[bold cyan]Verifying quotes")
        stage_started = time.perf_counter()
        corpus, verify_report = verify_quotes(
            corpus=corpus, fetched=fetched, settings=settings
        )
        stage_seconds["verify"] = time.perf_counter() - stage_started
        verification_summary = {
            "total": verify_report.total,
            "verified": verify_report.verified,
            "unverified": len(verify_report.unverified),
            "pass_rate": verify_report.pass_rate,
        }
        if verify_report.total == 0:
            console.print("[dim]No quotes to verify.[/dim]")
        else:
            pass_pct = verify_report.pass_rate * 100
            style = "green" if verify_report.pass_rate >= 0.9 else "yellow"
            console.print(
                f"[{style}]{verify_report.verified}/{verify_report.total} "
                f"quotes verified ({pass_pct:.0f}%).[/{style}]"
            )
            if verify_report.unverified:
                console.print(
                    f"[yellow]Stripped {len(verify_report.unverified)} "
                    "unverified quote(s); report in "
                    "_workspace/quote_verification.md.[/yellow]"
                )
        # Re-persist the cleaned corpus so downstream authoring and any
        # ``--refresh`` re-runs see the post-verification state.
        cluster_cache = settings.workspace_dir / "clustered_corpus.json"
        store_cache(
            cluster_cache,
            cluster_cache_fingerprint(extractions, settings),
            corpus,
        )

    authoring_index = 5

    written: list[str] = []

    if write_skill_flag:
        stage(
            f"{authoring_index}/{total_stages} Author skill",
            "Authoring, critiquing/refining, and writing SKILL.md...",
        )
        authoring_index += 1
        stage_started = time.perf_counter()
        skill_output, skill_report, skill_traj = await refine_skill(
            corpus=corpus, settings=settings, llm=llm
        )
        skill_path = write_skill(
            output=skill_output, sources=sources, settings=settings
        )
        written.append(
            f"SKILL.md + references/ at [bold green]{skill_path}[/bold green]"
        )
        stage_seconds["author_skill"] = time.perf_counter() - stage_started
        # A report exists whenever a critique ran — i.e. --critique, or --refine
        # (which critiques internally even under --no-critique). Surface it so
        # the score / refinement trajectory isn't silently hidden.
        if skill_report is not None:
            quality_summary["skill"] = {
                "score": skill_report.overall_score,
                "trajectory": skill_traj,
            }
            console.print(
                _refine_summary(
                    skill_report, skill_traj, label="SKILL.md", settings=settings
                )
            )

    if write_agents_flag:
        stage(
            f"{authoring_index}/{total_stages} Author AGENTS.md",
            "Authoring, critiquing/refining, and writing AGENTS.md...",
        )
        authoring_index += 1
        stage_started = time.perf_counter()
        agents_output, agents_report, agents_traj = await refine_agents(
            corpus=corpus, settings=settings, llm=llm
        )
        agents_path = write_agents(
            output=agents_output, sources=sources, settings=settings
        )
        written.append(f"AGENTS.md at [bold green]{agents_path}[/bold green]")
        stage_seconds["author_agents"] = time.perf_counter() - stage_started
        if agents_report is not None:
            quality_summary["agents"] = {
                "score": agents_report.overall_score,
                "trajectory": agents_traj,
            }
            console.print(
                _refine_summary(
                    agents_report, agents_traj, label="AGENTS.md", settings=settings
                )
            )

    if settings.generate_avatar:
        console.rule("[bold cyan]Avatar")
        console.print(f"Generating avatar with [bold]{settings.avatar_model}[/bold]...")
        stage_started = time.perf_counter()
        try:
            avatar_path = await generate_avatar(settings=settings)
        except Exception as exc:  # noqa: BLE001 - avatar is best-effort
            avatar_status = "failed"
            logger.warning("Avatar generation failed: %s", exc)
            console.print(
                f"[yellow]Avatar generation failed ({exc}); continuing.[/yellow]"
            )
        else:
            if avatar_path is not None:
                avatar_status = "written"
                console.print(f"Avatar saved to [bold green]{avatar_path}[/bold green]")
                written.append(f"avatar at [bold green]{avatar_path}[/bold green]")
            else:
                avatar_status = "no-image"
                console.print(
                    "[yellow]Avatar model returned no image; skipping.[/yellow]"
                )
        stage_seconds["avatar"] = time.perf_counter() - stage_started

    total_seconds = time.perf_counter() - run_started
    _write_run_summary(
        settings=settings,
        payload={
            "expert": {
                "name": settings.expert_name,
                "description": settings.expert_description,
            },
            "configuration": {
                "mode": settings.mode,
                "format": settings.format,
                "model": settings.model,
                "max_sources": settings.max_sources,
                "deep_research": settings.deep_research,
                "verify_quotes": settings.verify_quotes,
                "critique": settings.critique,
                "refine": settings.refine,
                "quality_bar": settings.quality_bar,
                "max_revisions": settings.max_revisions,
            },
            "counts": {
                "discovered": discovered_count,
                "primary_fetched": primary_fetched_count,
                "total_fetched": len(fetched),
                "extractions": len(extractions),
            },
            "verification": verification_summary,
            "quality": quality_summary,
            "avatar_status": avatar_status,
            "stage_seconds": {
                name: round(seconds, 3) for name, seconds in stage_seconds.items()
            },
            "total_seconds": round(total_seconds, 3),
        },
    )

    console.print(
        Panel(
            "\n".join(written) if written else "[yellow]Nothing written.[/yellow]",
            title="Done",
            border_style="green",
        )
    )
    return settings.skill_dir


def _write_run_summary(*, settings: Settings, payload: dict[str, object]) -> None:
    """Persist a machine-readable summary for successful runs."""
    path = settings.workspace_dir / "run_summary.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _critique_summary(report: CritiqueReport, *, label: str) -> str:
    """One-line console summary for a critique pass."""
    highs = sum(1 for i in report.issues if i.severity == "high")
    mediums = sum(1 for i in report.issues if i.severity == "medium")
    colour = (
        "green"
        if report.overall_score >= 8
        else "yellow"
        if report.overall_score >= 6
        else "red"
    )
    return (
        f"[{colour}]{label} score: {report.overall_score}/10[/{colour}] "
        f"— {highs} high, {mediums} medium issues. "
        "Full report in _workspace/."
    )


def _refine_summary(
    report: CritiqueReport,
    trajectory: list[int],
    *,
    label: str,
    settings: Settings,
) -> str:
    """Console summary for an authored artifact.

    Single-pass critique → the plain one-line score summary. A multi-iteration
    refine run additionally prepends the score trajectory (e.g. ``5 → 9``).
    """
    base = _critique_summary(report, label=label)
    if len(trajectory) > 1:
        arrow = " → ".join(str(s) for s in trajectory)
        return (
            f"[bold]{label} refinement:[/bold] {arrow} "
            f"(bar {settings.quality_bar}/10)\n{base}"
        )
    return base
