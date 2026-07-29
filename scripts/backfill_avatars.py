"""Backfill painterly avatar portraits for existing mimeo outputs.

The avatar feature landed after the initial batch run, so many
``<output_dir>/<slug>/`` directories (whether in mimeo's own ``output/`` tree
or in the standalone ``mimeographs/`` repo) are missing ``avatar.<ext>``.
This script re-runs just the avatar stage for every expert it finds in the
target directory — no discovery, fetch, distill, cluster, or authoring calls
— by reusing :func:`mimeo.avatar.generate_avatar`.

Rather than maintaining a hardcoded roster, we walk every subdirectory of
``--output-dir`` that contains an ``AGENTS.md`` (or falls back to
``SKILL.md``) and parse the expert's display name and disambiguator straight
out of the generated file. The disambiguator — the parenthetical that
follows the name in the opening paragraph, e.g. ``(deep learning pioneer,
backpropagation, University of Toronto, 2018 Turing Award)`` for Geoffrey
Hinton — is what the image model needs to render the correct real person
instead of a generic figure with the same name.

Usage (from the mimeo repo root):

    # Backfill the 80 experts in a sibling clone of the mimeographs repo:
    uv run python scripts/backfill_avatars.py \
        --output-dir ../mimeographs/mimeographs

    # Or the original mimeo output tree:
    uv run python scripts/backfill_avatars.py --output-dir ./output

    uv run python scripts/backfill_avatars.py --concurrency 2
    uv run python scripts/backfill_avatars.py --force   # regenerate existing
    uv run python scripts/backfill_avatars.py --only yann-lecun,andrej-karpathy

Requires OPENROUTER_API_KEY in the environment (or .env at repo root).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx
from rich.console import Console
from rich.logging import RichHandler

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from slugify import slugify  # noqa: E402

from mimeo.avatar import generate_avatar  # noqa: E402
from mimeo.config import DEFAULT_AVATAR_MODEL, Settings  # noqa: E402


@dataclass(frozen=True)
class Expert:
    """One row in the backfill plan."""

    slug: str
    name: str
    # Parenthetical qualifier fed to the avatar prompt so the image model has
    # enough context to render the right real person. Empty string when we
    # couldn't parse one (rare — pipeline normally always emits it).
    disambiguator: str
    skill_dir: Path
    source: str  # "AGENTS.md" | "SKILL.md" — for debug/log output only.


# Mimeo's author stage emits the AGENTS.md intro as:
#
#     # Think like Geoffrey Hinton
#
#     Geoffrey Hinton (deep learning pioneer, ...) ...
#
# We pull the display name out of the H1 and the disambiguator out of the
# first balanced-paren group in the opening paragraph. Balanced matching
# matters because some descriptions themselves contain parentheses, e.g.
# "Kaiming He (computer vision, ResNet creator, MIT, formerly Meta AI (FAIR))".
_H1_RE = re.compile(
    r"^\s*#\s+(?:Thinking\s+like|Think\s+like)\s+(.+?)\s*$", re.MULTILINE
)

# SKILL.md fallback: the YAML ``description:`` field always embeds the same
# disambiguator, typically as
# ``Applies the frameworks of Geoffrey Hinton (deep learning pioneer, ...) to``.
_SKILL_DESC_RE = re.compile(
    r"^description:\s*(.+?)(?:\n[A-Za-z_]+:|\n---)", re.DOTALL | re.MULTILINE
)


def _first_balanced_parens(text: str) -> tuple[int, int] | None:
    """Return the (start, end) indices of the first balanced ``(...)`` group.

    ``end`` is the index of the matching closing paren. Returns ``None`` if
    no balanced group exists.
    """
    start = text.find("(")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return start, i
    return None


def _parse_name_and_disambig(body: str) -> tuple[str | None, str]:
    """Extract ``(display_name, disambiguator)`` from the intro prose.

    ``body`` is the prose after the H1 (for AGENTS.md) or the ``description:``
    value (for SKILL.md). Both follow the same shape:

        <Name> (<disambig>) <rest of sentence...>

    Missing parenthetical yields an empty disambiguator rather than raising
    — the avatar prompt handles that gracefully, just with less context.
    """
    # Use only the first paragraph so later sections with their own parens
    # (quotes, examples) can't confuse the regex.
    first_para = body.strip().split("\n\n", 1)[0].strip()
    span = _first_balanced_parens(first_para)
    if span is None:
        # No parenthetical. Treat the leading chunk (up to first sentence
        # boundary) as the name and leave disambig empty.
        name = first_para.split(".", 1)[0].strip() or None
        return name, ""
    open_idx, close_idx = span
    name = first_para[:open_idx].rstrip().rstrip(",")
    disambig = first_para[open_idx + 1 : close_idx].strip()
    return (name or None), disambig


def _load_expert(skill_dir: Path) -> Expert | None:
    """Parse ``skill_dir``'s AGENTS.md (or SKILL.md) into an ``Expert``.

    Returns ``None`` if neither file exists or we can't recover a display
    name, so callers can skip the directory with a helpful warning.
    """
    slug = skill_dir.name

    agents = skill_dir / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8")
        m = _H1_RE.search(text)
        if m:
            name_from_h1 = m.group(1).strip()
            body = text[m.end() :].lstrip()
            _, disambig = _parse_name_and_disambig(body)
            return Expert(
                slug=slug,
                name=name_from_h1,
                disambiguator=disambig,
                skill_dir=skill_dir,
                source="AGENTS.md",
            )

    skill = skill_dir / "SKILL.md"
    if skill.is_file():
        text = skill.read_text(encoding="utf-8")
        m = _SKILL_DESC_RE.search(text)
        if m:
            description = m.group(1).strip()
            # Description shape: "Applies the frameworks of <Name> (<disambig>) ..."
            # The name is the token before the first balanced paren; peel off
            # any preamble up to "of " to recover a clean display name.
            name, disambig = _parse_name_and_disambig(description)
            if name:
                if " of " in name:
                    name = name.rsplit(" of ", 1)[-1].strip()
                return Expert(
                    slug=slug,
                    name=name,
                    disambiguator=disambig,
                    skill_dir=skill_dir,
                    source="SKILL.md",
                )

    return None


def _discover_experts(output_dir: Path, console: Console) -> list[Expert]:
    """Walk ``output_dir`` for expert skill folders.

    An expert folder is any immediate subdirectory containing AGENTS.md or
    SKILL.md. We skip hidden dirs (``.git``, etc.) and anything that doesn't
    parse into a valid ``Expert`` (with a console warning so the user knows).
    """
    if not output_dir.is_dir():
        console.print(f"[red]error:[/red] {output_dir} is not a directory")
        return []

    experts: list[Expert] = []
    for child in sorted(output_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if not ((child / "AGENTS.md").is_file() or (child / "SKILL.md").is_file()):
            continue
        expert = _load_expert(child)
        if expert is None:
            console.print(
                f"[yellow]skip[/yellow] {child.name}: "
                "couldn't parse name/disambiguator from AGENTS.md or SKILL.md"
            )
            continue
        # Sanity check: slugified display name should normally match the
        # folder slug. Warn but don't drop — the folder name is authoritative.
        expected = slugify(expert.name)
        if expected != expert.slug:
            console.print(
                f"[yellow]warn[/yellow] {expert.slug}: parsed name "
                f"{expert.name!r} slugifies to {expected!r}; "
                f"using folder slug for output path."
            )
        experts.append(expert)
    return experts


def _existing_avatar(skill_dir: Path) -> Path | None:
    """Return the path of an already-written avatar, if any."""
    for candidate in skill_dir.glob("avatar.*"):
        if candidate.is_file():
            return candidate
    return None


async def _one(
    *,
    expert: Expert,
    output_dir: Path,
    avatar_model: str,
    client: httpx.AsyncClient,
    force: bool,
    console: Console,
) -> tuple[str, str]:
    """Generate a single avatar. Returns ``(slug, status)`` for reporting."""
    existing = _existing_avatar(expert.skill_dir)
    if existing and not force:
        console.print(f"[dim]skip[/dim] {expert.slug}: already has {existing.name}")
        return expert.slug, "already-present"

    settings = Settings(
        expert_name=expert.name,
        output_dir=output_dir,
        expert_description=expert.disambiguator or None,
        avatar_model=avatar_model,
    )

    disambig_preview = (
        f" ({expert.disambiguator})" if expert.disambiguator else " (no disambiguator)"
    )
    console.print(
        f"[cyan]→[/cyan] {expert.slug}: generating avatar for "
        f"{expert.name}{disambig_preview} [dim]via {expert.source}[/dim]"
    )
    try:
        path = await generate_avatar(settings=settings, client=client)
    except Exception as exc:  # noqa: BLE001 - best-effort, log and continue
        console.print(f"[red]fail[/red] {expert.slug}: {exc}")
        return expert.slug, f"error: {exc}"

    if path is None:
        console.print(f"[yellow]empty[/yellow] {expert.slug}: model returned no image")
        return expert.slug, "no-image"

    try:
        rel = path.relative_to(REPO_ROOT)
    except ValueError:
        rel = path
    console.print(f"[green]ok[/green] {expert.slug}: {rel}")
    return expert.slug, "ok"


async def _run(args: argparse.Namespace, console: Console) -> int:
    output_dir: Path = args.output_dir.resolve()

    experts = _discover_experts(output_dir, console)
    if not experts:
        console.print(
            f"[red]nothing to do:[/red] no expert skill folders found under {output_dir}"
        )
        return 2

    if args.only:
        wanted = {s.strip() for s in args.only.split(",") if s.strip()}
        selected = [e for e in experts if e.slug in wanted]
        missing = wanted - {e.slug for e in selected}
        if missing:
            console.print(
                f"[yellow]--only included unknown slug(s):[/yellow] {', '.join(sorted(missing))}"
            )
        if not selected:
            console.print(
                "[red]nothing to do: --only matched zero known experts.[/red]"
            )
            return 2
    else:
        selected = experts

    console.print(
        f"Backfilling avatars for [bold]{len(selected)}[/bold] expert(s) "
        f"under [bold]{output_dir}[/bold] using [bold]{args.avatar_model}[/bold] "
        f"(concurrency={args.concurrency}, force={args.force})."
    )

    sem = asyncio.Semaphore(args.concurrency)
    # Shared client keeps HTTP/2 connection pooling warm across the batch.
    # Timeout mirrors avatar.py's default (some image models take ~1min).
    timeout = httpx.Timeout(300.0, connect=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:

        async def _bounded(expert: Expert) -> tuple[str, str]:
            async with sem:
                return await _one(
                    expert=expert,
                    output_dir=output_dir,
                    avatar_model=args.avatar_model,
                    client=client,
                    force=args.force,
                    console=console,
                )

        results = await asyncio.gather(*(_bounded(e) for e in selected))

    ok = sum(1 for _, s in results if s == "ok")
    skipped = sum(1 for _, s in results if s == "already-present")
    empty = sum(1 for _, s in results if s == "no-image")
    failed = sum(1 for _, s in results if s.startswith("error:"))

    console.rule("[bold]Summary")
    console.print(
        f"ok={ok}  skipped={skipped}  empty={empty}  failed={failed}  total={len(results)}"
    )
    if failed:
        for slug, status in results:
            if status.startswith("error:"):
                console.print(f"  [red]{slug}[/red]: {status}")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "output",
        help=(
            "Directory whose immediate subdirectories are expert skill folders "
            "(default: ./output). Point this at the mimeographs repo's "
            "`mimeographs/` folder to backfill the full public roster."
        ),
    )
    parser.add_argument(
        "--avatar-model",
        default=DEFAULT_AVATAR_MODEL,
        help=f"OpenRouter image-capable model slug (default: {DEFAULT_AVATAR_MODEL}).",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Max concurrent image requests (default: 3).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate avatars even when one already exists.",
    )
    parser.add_argument(
        "--only",
        default=None,
        help="Comma-separated list of slugs to process (e.g. 'yann-lecun,andrej-karpathy').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the discovered experts and their disambiguators, then exit.",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    console = Console()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True, show_path=args.verbose)
        ],
    )
    for name in ("httpx", "httpcore"):
        logging.getLogger(name).setLevel(logging.WARNING)

    if args.dry_run:
        output_dir = args.output_dir.resolve()
        experts = _discover_experts(output_dir, console)
        console.print(
            f"Discovered [bold]{len(experts)}[/bold] expert(s) under {output_dir}:"
        )
        for e in experts:
            disambig = e.disambiguator or "[red]<missing>[/red]"
            console.print(f"  [cyan]{e.slug}[/cyan]  {e.name} [dim]({disambig})[/dim]")
        return 0

    try:
        return asyncio.run(_run(args, console))
    except KeyboardInterrupt:
        console.print("[yellow]cancelled.[/yellow]")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
