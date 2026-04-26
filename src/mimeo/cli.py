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

from .config import (
    DEFAULT_AVATAR_MODEL,
    DEFAULT_IMAGE_PROVIDER,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_SEARCH_PROVIDER,
    Format,
    ImageProviderName,
    LLMProvider,
    MissingConfigurationError,
    Mode,
    MissingCredentialError,
    SearchProviderName,
    Settings,
)
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
    for name in ("httpx", "httpcore", "openai", "anthropic", "urllib3", "parallel"):
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
        str | None,
        typer.Option(
            "--model",
            help=(
                "Provider-native model id. Required for non-OpenRouter providers "
                "unless MIMEO_MODEL or MIMEO_<PROVIDER>_MODEL is set."
            ),
        ),
    ] = None,
    llm_provider: Annotated[
        LLMProvider,
        typer.Option(
            "--llm-provider",
            help="Text LLM provider.",
            case_sensitive=False,
        ),
    ] = DEFAULT_LLM_PROVIDER,
    search_provider: Annotated[
        SearchProviderName,
        typer.Option(
            "--search-provider",
            help="Search provider. Parallel is the only v1 implementation.",
            case_sensitive=False,
        ),
    ] = DEFAULT_SEARCH_PROVIDER,
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
    verify_quotes: Annotated[
        bool,
        typer.Option(
            "--verify-quotes/--no-verify-quotes",
            help=(
                "After clustering, check every representative quote against "
                "the fetched source text and strip ones that don't match. "
                "Defends the 'every quote is verbatim' promise."
            ),
        ),
    ] = True,
    critique: Annotated[
        bool,
        typer.Option(
            "--critique/--no-critique",
            help=(
                "After authoring, run an adversarial-editor LLM pass and "
                "write a critique report to _workspace/critique_*.md."
            ),
        ),
    ] = True,
    avatar: Annotated[
        bool,
        typer.Option(
            "--avatar/--no-avatar",
            help=(
                "Generate a painterly avatar portrait of the expert and "
                "save it alongside the other outputs as avatar.<ext>. On "
                "by default; pass --no-avatar to skip the extra image call."
            ),
        ),
    ] = True,
    image_provider: Annotated[
        ImageProviderName,
        typer.Option(
            "--image-provider",
            help="Avatar image provider.",
            case_sensitive=False,
        ),
    ] = DEFAULT_IMAGE_PROVIDER,
    avatar_model: Annotated[
        str,
        typer.Option(
            "--avatar-model",
            help=(
                "OpenRouter model slug for avatar generation. Must be an "
                "image-capable model."
            ),
        ),
    ] = DEFAULT_AVATAR_MODEL,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Verbose logging.")
    ] = False,
) -> None:
    """Build an Agent Skill for ``EXPERT`` from their body of work."""
    _setup_logging(verbose)

    try:
        settings = Settings(
            expert_name=expert,
            output_dir=output_dir.resolve(),
            mode=mode,
            format=fmt,
            max_sources=max_sources,
            deep_research=deep_research,
            model=model,
            llm_provider=llm_provider,
            search_provider=search_provider,
            image_provider=image_provider,
            concurrency=concurrency,
            refresh=refresh,
            expert_description=disambiguator,
            assume_unambiguous=assume_unambiguous,
            verify_quotes=verify_quotes,
            critique=critique,
            generate_avatar=avatar,
            avatar_model=avatar_model,
        )
        out_path = asyncio.run(run_pipeline(settings, console=console))
    except MissingCredentialError as exc:
        console.print(f"[bold red]Missing credential:[/bold red] {exc}")
        raise typer.Exit(code=2)
    except MissingConfigurationError as exc:
        console.print(f"[bold red]Missing configuration:[/bold red] {exc}")
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
