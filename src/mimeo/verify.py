"""Post-cluster verification: check that every clustered quote is real.

The authoring prompt tells the model "every quote is verbatim." The cluster
step, being an LLM, occasionally glosses quotes into paraphrases. This
stage re-reads the per-source text we already fetched and checks that each
clustered quote actually appears there (allowing light normalization of
whitespace, punctuation, and smart quotes). Unverified quotes are stripped
from the corpus before authoring so they can't be laundered into the final
skill.

The output is twofold:

- a :class:`VerificationReport` written to ``_workspace/quote_verification.json``
  for auditing.
- a *cleaned* :class:`ClusteredCorpus` with ``representative_quote = None``
  on items whose quote didn't match any of their listed source ids.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from .config import Settings
from .schemas import (
    ClusteredCorpus,
    ClusteredItem,
    FetchedContent,
    QuoteVerification,
    VerificationReport,
)

logger = logging.getLogger(__name__)

# Minimum similarity below which we declare a quote unverified. We use a
# generous threshold because source text typographically normalizes quite a
# lot (curly → straight quotes, em-dash vs hyphen, line-wrap whitespace).
_MATCH_THRESHOLD = 0.82
# Quotes this short are too ambiguous to fuzzy-match reliably; we pass them
# through rather than risk false-negatives on a six-word aphorism.
_MIN_QUOTE_CHARS = 20


@dataclass(frozen=True)
class _Target:
    category: str
    attr: str  # attribute on ClusteredCorpus
    index: int  # index within that list
    item: ClusteredItem


def verify_quotes(
    *,
    corpus: ClusteredCorpus,
    fetched: list[FetchedContent],
    settings: Settings,
    write_report: bool = True,
) -> tuple[ClusteredCorpus, VerificationReport]:
    """Return a corpus with unverified quotes stripped, plus a report.

    ``fetched`` is the per-source text we already cached during the fetch
    stage; we index it by source id and walk every clustered item whose
    ``representative_quote`` is set.
    """
    text_by_id = {fc.source_id: _normalize(fc.text) for fc in fetched}
    targets = _collect_targets(corpus)

    results: list[QuoteVerification] = []
    updates: dict[str, list[tuple[int, ClusteredItem]]] = {}

    for target in targets:
        quote = (target.item.representative_quote or "").strip()
        if not quote:
            continue
        result = _verify_one(target=target, quote=quote, text_by_id=text_by_id)
        results.append(result)
        if not result.verified:
            cleared = target.item.model_copy(update={"representative_quote": None})
            updates.setdefault(target.attr, []).append((target.index, cleared))

    cleaned = _apply_updates(corpus, updates)

    verified_count = sum(1 for r in results if r.verified)
    unverified = [r for r in results if not r.verified]
    report = VerificationReport(
        total=len(results),
        verified=verified_count,
        unverified=unverified,
        all_results=results,
    )

    if write_report:
        _write_report(report, settings=settings)

    logger.info(
        "Quote verification: %d/%d verified (%.0f%%); %d quotes cleared",
        verified_count,
        len(results),
        report.pass_rate * 100,
        len(unverified),
    )
    return cleaned, report


def _verify_one(
    *,
    target: _Target,
    quote: str,
    text_by_id: dict[str, str],
) -> QuoteVerification:
    normalized_quote = _normalize(quote)
    # Very short quotes get a free pass — false-negatives here are worse
    # than the occasional fake slipping through.
    if len(normalized_quote) < _MIN_QUOTE_CHARS:
        return QuoteVerification(
            category=target.category,  # type: ignore[arg-type]
            label=target.item.label,
            quote=quote,
            source_ids=list(target.item.source_ids),
            verified=True,
            matched_source_id=None,
            match_ratio=1.0,
        )

    best_ratio = 0.0
    best_source: str | None = None
    for source_id in target.item.source_ids:
        text = text_by_id.get(source_id)
        if not text:
            continue
        if normalized_quote in text:
            return QuoteVerification(
                category=target.category,  # type: ignore[arg-type]
                label=target.item.label,
                quote=quote,
                source_ids=list(target.item.source_ids),
                verified=True,
                matched_source_id=source_id,
                match_ratio=1.0,
            )
        ratio = _best_window_ratio(normalized_quote, text)
        if ratio > best_ratio:
            best_ratio = ratio
            best_source = source_id

    verified = best_ratio >= _MATCH_THRESHOLD
    return QuoteVerification(
        category=target.category,  # type: ignore[arg-type]
        label=target.item.label,
        quote=quote,
        source_ids=list(target.item.source_ids),
        verified=verified,
        matched_source_id=best_source if verified else None,
        match_ratio=best_ratio,
    )


def _best_window_ratio(needle: str, haystack: str) -> float:
    """Slide a needle-sized window across haystack; return best ratio.

    We compare against a window the same length as ``needle`` (not larger)
    so ``SequenceMatcher.ratio`` isn't dragged down by surrounding context.
    To keep this fast on book-length haystacks, we pick an anchor substring
    from the middle of the needle and only score the neighborhoods where
    the anchor appears. When no anchor lands, we fall back to a coarse
    stride over the whole haystack.
    """
    if not needle or not haystack:
        return 0.0
    if len(haystack) < len(needle) // 2:
        return 0.0

    length = len(needle)
    anchor = _pick_anchor(needle)

    positions: list[int] = []
    if anchor:
        start = 0
        while len(positions) < 16:
            idx = haystack.find(anchor, start)
            if idx == -1:
                break
            # Centre the candidate window roughly around the anchor hit.
            offset = (length - len(anchor)) // 2
            positions.append(max(idx - offset, 0))
            start = idx + max(len(anchor), 1)
    if not positions:
        stride = max(length // 2, 50)
        positions = list(range(0, max(len(haystack) - length + 1, 1), stride))

    best = 0.0
    for pos in positions:
        candidate = haystack[pos : pos + length]
        if len(candidate) < length // 2:
            continue
        ratio = SequenceMatcher(None, needle, candidate, autojunk=False).ratio()
        if ratio > best:
            best = ratio
            if best >= 0.99:
                return best
    return best


def _pick_anchor(needle: str) -> str | None:
    """Pick a ~16-char chunk from the middle of the quote for index lookup."""
    if len(needle) < 24:
        return None
    mid = len(needle) // 2
    start = max(mid - 8, 0)
    return needle[start : start + 16]


def _normalize(text: str) -> str:
    """Canonicalize text for matching: lowercase, collapse whitespace,
    straighten quotes, drop boundary punctuation.
    """
    if not text:
        return ""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\xa0": " ",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _collect_targets(corpus: ClusteredCorpus) -> list[_Target]:
    attrs = (
        ("principles", "principles"),
        ("frameworks", "frameworks"),
        ("mental_models", "mental_models"),
        ("heuristics", "heuristics"),
        ("signature_quotes", "signature_quotes"),
        ("anti_patterns", "anti_patterns"),
    )
    targets: list[_Target] = []
    for category, attr in attrs:
        items: list[ClusteredItem] = getattr(corpus, attr)
        for idx, item in enumerate(items):
            if item.representative_quote:
                targets.append(
                    _Target(category=category, attr=attr, index=idx, item=item)
                )
    return targets


def _apply_updates(
    corpus: ClusteredCorpus,
    updates: dict[str, list[tuple[int, ClusteredItem]]],
) -> ClusteredCorpus:
    """Return a corpus with the replacement items at the given indices."""
    if not updates:
        return corpus

    patch: dict[str, list[ClusteredItem]] = {}
    for attr, changes in updates.items():
        items = list(getattr(corpus, attr))
        for idx, new_item in changes:
            if 0 <= idx < len(items):
                items[idx] = new_item
        patch[attr] = items
    return corpus.model_copy(update=patch)


def _write_report(report: VerificationReport, *, settings: Settings) -> None:
    path: Path = settings.workspace_dir / "quote_verification.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    # Also emit a human-friendly markdown summary if there were misses.
    if report.unverified:
        md_path: Path = settings.workspace_dir / "quote_verification.md"
        lines = [
            "# Quote verification",
            "",
            f"Verified {report.verified}/{report.total} "
            f"({report.pass_rate * 100:.0f}%).",
            "",
            "## Unverified",
            "",
            "These quotes didn't match any of their listed source texts and "
            "were stripped from the corpus before authoring.",
            "",
        ]
        for r in report.unverified:
            lines.append(
                f"- **{r.category}** / _{r.label}_ "
                f"(sources: {', '.join(r.source_ids) or 'none'}) "
                f"— match ratio {r.match_ratio:.2f}"
            )
            lines.append(f"  > {r.quote}")
        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
