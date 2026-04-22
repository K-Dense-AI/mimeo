"""Typer CLI entry point."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.logging import RichHandler

from .config import DEFAULT_MODEL, Format, Mode, MissingCredentialError, Settings
from .identity import AmbiguousNameError
from .pipeline import run_pipeline

app = typer.Typer(
    add_completion=False,
    help="Turn an expert's body of work into a ready-to-use Agent Skill.",
    no_args_is_help=True,
)

console = Console()


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=verbose)],
    )
    # Tame noisy deps.
    for name in ("httpx", "httpcore", "openai", "urllib3", "parallel"):
        logging.getLogger(name).setLevel(logging.WARNING)


@app.command()
def build(
    expert: Annotated[str, typer.Argument(help="The expert's name, e.g. 'Naval Ravikant'.")],
    mode: Annotated[
        Mode,
        typer.Option(
            "--mode",
            help="text: web only. captions: web + YouTube captions. full: + audio transcription.",
            case_sensitive=False,
        ),
    ] = "captions",
    fmt: Annotated[
        Format,
        typer.Option(
            "--format",
            "-f",
            help="skill: SKILL.md + references/ (default). agents: AGENTS.md. both: emit both.",
            case_sensitive=False,
        ),
    ] = "skill",
    max_sources: Annotated[
        int, typer.Option("--max-sources", min=1, max=200, help="Cap on sources after dedup + rank.")
    ] = 25,
    deep_research: Annotated[
        bool,
        typer.Option(
            "--deep-research/--no-deep-research",
            help="Also run a Parallel Task API deep-research run and merge it in.",
        ),
    ] = False,
    model: Annotated[
        str,
        typer.Option("--model", help="Any OpenRouter model slug."),
    ] = DEFAULT_MODEL,
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", help="Where the generated skill directory lands."),
    ] = Path("./output"),
    concurrency: Annotated[
        int, typer.Option("--concurrency", min=1, max=20, help="Concurrent per-source LLM calls.")
    ] = 5,
    disambiguator: Annotated[
        str | None,
        typer.Option(
            "--disambiguator",
            "-d",
            help=(
                "Short qualifier that distinguishes the expert from namesakes "
                "(e.g. 'co-founder of AngelList, investor'). When set, the "
                "automatic disambiguation pre-flight is skipped."
            ),
        ),
    ] = None,
    assume_unambiguous: Annotated[
        bool,
        typer.Option(
            "--assume-unambiguous/--no-assume-unambiguous",
            help=(
                "Skip the identity-resolution pre-flight entirely. Use in "
                "non-interactive runs where you're confident the name is unique."
            ),
        ),
    ] = False,
    refresh: Annotated[
        bool,
        typer.Option(
            "--refresh/--no-refresh",
            help="Ignore cached intermediates and re-run everything.",
        ),
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose logging.")
    ] = False,
) -> None:
    """Build an Agent Skill for ``EXPERT`` from their body of work."""
    _setup_logging(verbose)

    settings = Settings(
        expert_name=expert,
        output_dir=output_dir.resolve(),
        mode=mode,
        format=fmt,
        max_sources=max_sources,
        deep_research=deep_research,
        model=model,
        concurrency=concurrency,
        refresh=refresh,
        expert_description=disambiguator,
        assume_unambiguous=assume_unambiguous,
    )

    try:
        out_path = asyncio.run(run_pipeline(settings, console=console))
    except MissingCredentialError as exc:
        console.print(f"[bold red]Missing credential:[/bold red] {exc}")
        raise typer.Exit(code=2)
    except AmbiguousNameError as exc:
        console.print(f"[bold yellow]Ambiguous name.[/bold yellow]\n{exc}")
        raise typer.Exit(code=2)
    except KeyboardInterrupt:
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(code=130)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[bold red]Pipeline failed:[/bold red] {exc}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)

    console.print(f"\n[bold green]Done.[/bold green] Output at: {out_path}")


def main() -> None:  # convenience wrapper used by main.py
    app()


if __name__ == "__main__":  # pragma: no cover - direct-invocation guard
    sys.exit(app() or 0)
