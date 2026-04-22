"""Stage 0: resolve which real person the expert name refers to.

Common names ("John Smith", "Mike Johnson", even single first names) match
many notable people. Without a disambiguation step, downstream discovery
would silently blend their bodies of work into a single incoherent skill.

This module runs one Parallel Search + one LLM classification call to
either:

* confirm the name is unambiguous and attach a short qualifier (used by
  later prompts so the model stays anchored to the right person), or
* list candidates and either prompt the user to pick (TTY) or fail loudly
  with a useful error message (non-interactive).

Results are cached under ``_workspace/identity.<model>.json`` so repeat runs
skip the classification call.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import replace

from rich.console import Console

from .config import Settings
from .llm import LLMClient
from .parallel_client import ParallelClient
from .schemas import ExpertCandidate, IdentityResolution

logger = logging.getLogger(__name__)


class AmbiguousNameError(RuntimeError):
    """Raised when we can't disambiguate and can't prompt the user either."""

    def __init__(self, *, expert_name: str, candidates: list[ExpertCandidate]) -> None:
        self.expert_name = expert_name
        self.candidates = candidates
        lines = [
            f"'{expert_name}' matches multiple notable people. Re-run with "
            '--disambiguator "<short qualifier>" to pick one, for example:',
        ]
        for cand in candidates:
            lines.append(f"  - {cand.name}: {cand.description}")
        lines.append(
            "Or pass --assume-unambiguous to suppress this check (not recommended)."
        )
        super().__init__("\n".join(lines))


async def resolve_identity(
    *,
    settings: Settings,
    parallel: ParallelClient,
    llm: LLMClient,
    console: Console | None = None,
) -> Settings:
    """Ensure ``settings.expert_description`` is set.

    Returns a (possibly new) Settings with ``expert_description`` filled in.
    Raises :class:`AmbiguousNameError` when the name is ambiguous and we
    can't prompt the user (no TTY, no console, etc.).
    """

    if settings.expert_description:
        logger.info(
            "Using user-supplied disambiguator: %s (%s)",
            settings.expert_name,
            settings.expert_description,
        )
        return settings

    if settings.assume_unambiguous:
        logger.info(
            "Skipping identity resolution for %s (--assume-unambiguous)",
            settings.expert_name,
        )
        return settings

    cache_path = settings.workspace_dir / f"identity.{settings.model_cache_id}.json"
    resolution: IdentityResolution | None = None
    if cache_path.exists() and not settings.refresh:
        try:
            resolution = IdentityResolution.model_validate_json(
                cache_path.read_text(encoding="utf-8")
            )
            logger.info("Using cached identity resolution from %s", cache_path)
        except Exception:  # noqa: BLE001
            logger.warning("Corrupt identity cache; re-resolving")
            resolution = None

    if resolution is None:
        if console is not None:
            console.print(
                f"[dim]Resolving identity for '{settings.expert_name}'...[/dim]"
            )
        resolution = await _classify(
            settings=settings, parallel=parallel, llm=llm
        )
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            resolution.model_dump_json(indent=2), encoding="utf-8"
        )

    return _apply_resolution(settings, resolution, console=console)


def _apply_resolution(
    settings: Settings,
    resolution: IdentityResolution,
    *,
    console: Console | None,
) -> Settings:
    if not resolution.is_ambiguous:
        description = resolution.resolved_description
        if description:
            logger.info(
                "Identity resolved: %s (%s)", settings.expert_name, description
            )
            if console is not None:
                console.print(
                    f"[green]Resolved[/green] '{settings.expert_name}' → "
                    f"{description}"
                )
            return replace(settings, expert_description=description)
        # Unambiguous but no description (e.g. zero search evidence).
        # Proceed without a qualifier rather than blocking the whole pipeline.
        if console is not None:
            console.print(
                f"[yellow]No biographical evidence found for "
                f"'{settings.expert_name}'; continuing without a qualifier.[/yellow]"
            )
        return settings

    # Ambiguous from here on.
    if console is not None and sys.stdin.isatty():
        picked = _prompt_choice(console, settings.expert_name, resolution.candidates)
        if picked is not None:
            if console is not None:
                console.print(
                    f"[green]Picked[/green] {picked.name} — {picked.description}"
                )
            return replace(settings, expert_description=picked.description)

    raise AmbiguousNameError(
        expert_name=settings.expert_name, candidates=resolution.candidates
    )


def _prompt_choice(
    console: Console,
    expert_name: str,
    candidates: list[ExpertCandidate],
) -> ExpertCandidate | None:
    if not candidates:
        return None

    from rich.prompt import IntPrompt

    console.print()
    console.rule(f"[bold yellow]Ambiguous name: {expert_name}[/bold yellow]")
    console.print(
        f"[bold]{expert_name}[/bold] matches multiple notable people. "
        "Pick one to continue, or press Ctrl-C to abort."
    )
    for i, cand in enumerate(candidates, start=1):
        console.print(f"  [bold]{i}.[/bold] {cand.name} — {cand.description}")
        if cand.evidence:
            console.print(f"     [dim]{cand.evidence}[/dim]")
    choice = IntPrompt.ask(
        "Your pick",
        choices=[str(i) for i in range(1, len(candidates) + 1)],
        default=1,
    )
    return candidates[choice - 1]


async def _classify(
    *,
    settings: Settings,
    parallel: ParallelClient,
    llm: LLMClient,
) -> IdentityResolution:
    """Gather biographical evidence and ask the LLM to classify ambiguity."""

    search = await parallel.search(
        objective=(
            f"Identify the notable people known as '{settings.expert_name}'. "
            "Surface short biographical blurbs with profession, affiliation, "
            "and the field they are known for. If only one notable person is "
            "commonly known by this name, say so."
        ),
        search_queries=[
            f"who is {settings.expert_name}",
            f'"{settings.expert_name}" biography',
            f'"{settings.expert_name}" wikipedia',
        ],
        max_chars_total=10_000,
    )

    rows: list[dict[str, object]] = []
    for r in (getattr(search, "results", None) or [])[:20]:
        url = str(getattr(r, "url", "") or "")
        if not url:
            continue
        rows.append(
            {
                "url": url,
                "title": getattr(r, "title", None),
                "excerpts": list(getattr(r, "excerpts", []) or [])[:3],
            }
        )

    if not rows:
        logger.warning(
            "No search evidence for '%s'; treating as unambiguous",
            settings.expert_name,
        )
        return IdentityResolution(
            is_ambiguous=False,
            resolved_description=None,
            notes="No biographical evidence found during identity resolution.",
        )

    system = (
        "You resolve ambiguous person names against search evidence. A name "
        "is 'ambiguous' only when two or more *notable* people share it AND "
        "either could plausibly be the referent given only the bare name. "
        "Minor namesakes (private individuals, very obscure people) do NOT "
        "make a name ambiguous. When in doubt, prefer unambiguous. Never "
        "fabricate candidates that aren't supported by the evidence."
    )
    user = (
        f'Expert name provided by the user: "{settings.expert_name}"\n\n'
        "Search evidence (JSON):\n"
        f"{json.dumps(rows, indent=2)}\n\n"
        "Decide whether this name is ambiguous.\n"
        "- If unambiguous: set is_ambiguous=false and resolved_description to "
        "a short qualifier like 'co-founder of AngelList, investor, essayist'. "
        "Keep it under 20 words; do not repeat the name; no leading comma.\n"
        "- If ambiguous: set is_ambiguous=true and list 2-5 distinct notable "
        "candidates, each with a short distinguishing description and a "
        "one-line evidence snippet grounded in the search results."
    )

    return await llm.structured(
        system=system,
        user=user,
        schema=IdentityResolution,
        temperature=0.1,
    )
