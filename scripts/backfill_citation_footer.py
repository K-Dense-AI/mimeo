"""Backfill the mimeo attribution + paper-citation footer into existing outputs.

The footer landed after the gallery was generated, so committed
``<output_dir>/<slug>/`` trees are missing the trailing paragraph that
:mod:`mimeo.writers` now appends to ``SKILL.md``, ``AGENTS.md`` and
``references/sources.md``. This script appends the identical footer to any of
those files that don't already end with it. No API calls; safe to re-run.

Usage (from the mimeo repo root):

    uv run python scripts/backfill_citation_footer.py                  # ./output
    uv run python scripts/backfill_citation_footer.py --output-dir ../mimeographs/mimeographs
    uv run python scripts/backfill_citation_footer.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from mimeo.writers import PAPER_ARXIV_ID, append_citation_footer  # noqa: E402

# Files the writer stage stamps, relative to each ``<output_dir>/<slug>/``.
TARGETS = (Path("SKILL.md"), Path("AGENTS.md"), Path("references") / "sources.md")


def has_footer(text: str) -> bool:
    """True when the last non-blank line already carries the paper citation.

    Keyed on the arXiv id rather than the exact footer string so that a later
    rewording of :data:`mimeo.writers.CITATION_FOOTER` doesn't stack a second
    paragraph under the old one.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    return bool(lines) and f"arXiv:{PAPER_ARXIV_ID}" in lines[-1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "output",
        help="Directory whose <slug>/ subdirectories hold generated artifacts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report which files would change without writing anything.",
    )
    args = parser.parse_args(argv)

    if not args.output_dir.is_dir():
        parser.error(f"{args.output_dir} is not a directory")

    updated: list[Path] = []
    already = 0
    for skill_dir in sorted(p for p in args.output_dir.iterdir() if p.is_dir()):
        for rel in TARGETS:
            path = skill_dir / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if has_footer(text):
                already += 1
                continue
            if not args.dry_run:
                path.write_text(append_citation_footer(text), encoding="utf-8")
            updated.append(path.relative_to(args.output_dir))

    verb = "would update" if args.dry_run else "updated"
    for rel in updated:
        print(f"  {verb}: {rel}")
    print(f"{verb} {len(updated)} file(s); {already} already had the footer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
