"""Orchestrator: run all stages end-to-end for one expert."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from rich.console import Console
from rich.panel import Panel

from .avatar import generate_avatar
from .config import Settings, ensure_dirs
from .critique import critique_agents, critique_skill
from .discovery import discover_sources
from .distill import distill_all
from .fetchers import fetch_all
from .identity import resolve_identity
from .llm import LLMClient
from .parallel_client import ParallelClient
from .research import deep_research
from .schemas import Extraction, FetchedContent, Source
from .synthesize import author_agents, author_skill, cluster_corpus
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
    settings = await resolve_identity(
        settings=settings, parallel=parallel, llm=llm, console=console
    )

    write_skill_flag = settings.format in ("skill", "both")
    write_agents_flag = settings.format in ("agents", "both")
    # Baseline = discover, fetch, distill, cluster. Each output artifact adds
    # one authoring step, plus an optional critique step per artifact.
    # Verify-quotes is a side-step and doesn't count. Deep research is the
    # same.
    total_stages = (
        4
        + int(write_skill_flag)
        + int(write_agents_flag)
        + (int(write_skill_flag) + int(write_agents_flag)) * int(settings.critique)
    )

    stage(
        f"1/{total_stages} Discovery",
        "Searching across essays, talks, interviews, podcasts, frameworks, books...",
    )
    sources: list[Source] = await discover_sources(
        settings=settings, parallel=parallel, llm=llm
    )
    console.print(f"Selected [bold]{len(sources)}[/bold] sources.")
    if not sources:
        raise RuntimeError("No sources discovered. Check PARALLEL_API_KEY and the expert name.")

    stage(f"2/{total_stages} Fetch", "Fetching full content for each source...")
    fetched: list[FetchedContent] = await fetch_all(
        sources, settings=settings, parallel=parallel
    )
    console.print(
        f"Fetched content for [bold]{len(fetched)}[/bold] / {len(sources)} sources "
        f"({sum(f.char_count for f in fetched):,} chars total)."
    )

    if settings.deep_research:
        stage(
            f"2.5/{total_stages} Deep research",
            "Running Parallel Task API pro-fast (this can take a few minutes)...",
        )
        pair = await deep_research(settings=settings, parallel=parallel)
        if pair:
            research_source, research_content = pair
            sources.append(research_source)
            fetched.append(research_content)
            console.print(
                f"Deep-research report added as [bold]{research_source.id}[/bold] "
                f"({research_content.char_count:,} chars)."
            )
        else:
            console.print("[yellow]Deep research failed or returned empty; continuing without it.[/yellow]")

    stage(
        f"3/{total_stages} Distill",
        "Extracting principles, frameworks, and quotes from each source...",
    )
    extractions: list[Extraction] = await distill_all(
        sources=sources, fetched=fetched, settings=settings, llm=llm
    )
    console.print(
        f"Distilled [bold]{len(extractions)}[/bold] sources into structured extractions."
    )

    stage(f"4/{total_stages} Cluster", "Merging extractions into a unified corpus...")
    corpus = await cluster_corpus(
        extractions=extractions, settings=settings, llm=llm
    )
    console.print(
        f"Clustered into {len(corpus.principles)} principles, "
        f"{len(corpus.frameworks)} frameworks, "
        f"{len(corpus.mental_models)} mental models, "
        f"{len(corpus.signature_quotes)} quotes."
    )

    if settings.verify_quotes:
        console.rule("[bold cyan]Verifying quotes")
        corpus, verify_report = verify_quotes(
            corpus=corpus, fetched=fetched, settings=settings
        )
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
        cluster_cache = (
            settings.workspace_dir / f"clustered_corpus.{settings.model_cache_id}.json"
        )
        cluster_cache.write_text(corpus.model_dump_json(indent=2), encoding="utf-8")

    authoring_index = 5

    written: list[str] = []

    if write_skill_flag:
        stage(
            f"{authoring_index}/{total_stages} Author skill",
            "Writing SKILL.md and references/*.md...",
        )
        authoring_index += 1
        skill_output = await author_skill(corpus=corpus, settings=settings, llm=llm)
        skill_path = write_skill(
            output=skill_output, sources=sources, settings=settings
        )
        written.append(f"SKILL.md + references/ at [bold green]{skill_path}[/bold green]")

        if settings.critique:
            stage(
                f"{authoring_index}/{total_stages} Critique skill",
                "Adversarial review of the authored skill...",
            )
            authoring_index += 1
            report = await critique_skill(
                output=skill_output, corpus=corpus, settings=settings, llm=llm
            )
            console.print(
                _critique_summary(report, label="SKILL.md")
            )

    if write_agents_flag:
        stage(
            f"{authoring_index}/{total_stages} Author AGENTS.md",
            "Writing AGENTS.md...",
        )
        authoring_index += 1
        agents_output = await author_agents(corpus=corpus, settings=settings, llm=llm)
        agents_path = write_agents(
            output=agents_output, sources=sources, settings=settings
        )
        written.append(f"AGENTS.md at [bold green]{agents_path}[/bold green]")

        if settings.critique:
            stage(
                f"{authoring_index}/{total_stages} Critique AGENTS.md",
                "Adversarial review of the authored AGENTS.md...",
            )
            authoring_index += 1
            report = await critique_agents(
                output=agents_output, corpus=corpus, settings=settings, llm=llm
            )
            console.print(
                _critique_summary(report, label="AGENTS.md")
            )

    if settings.generate_avatar:
        console.rule("[bold cyan]Avatar")
        console.print(
            f"Generating avatar with [bold]{settings.avatar_model}[/bold]..."
        )
        try:
            avatar_path = await generate_avatar(settings=settings)
        except Exception as exc:  # noqa: BLE001 - avatar is best-effort
            logger.warning("Avatar generation failed: %s", exc)
            console.print(
                f"[yellow]Avatar generation failed ({exc}); continuing.[/yellow]"
            )
        else:
            if avatar_path is not None:
                console.print(f"Avatar saved to [bold green]{avatar_path}[/bold green]")
                written.append(f"avatar at [bold green]{avatar_path}[/bold green]")
            else:
                console.print(
                    "[yellow]Avatar model returned no image; skipping.[/yellow]"
                )

    console.print(
        Panel(
            "\n".join(written) if written else "[yellow]Nothing written.[/yellow]",
            title="Done",
            border_style="green",
        )
    )
    return settings.skill_dir


def _critique_summary(report, *, label: str) -> str:  # type: ignore[no-untyped-def]
    """One-line console summary for a critique pass."""
    highs = sum(1 for i in report.issues if i.severity == "high")
    mediums = sum(1 for i in report.issues if i.severity == "medium")
    colour = "green" if report.overall_score >= 8 else "yellow" if report.overall_score >= 6 else "red"
    return (
        f"[{colour}]{label} score: {report.overall_score}/10[/{colour}] "
        f"— {highs} high, {mediums} medium issues. "
        "Full report in _workspace/."
    )
