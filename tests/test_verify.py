"""Offline tests for :mod:`mimeo.verify`."""

from __future__ import annotations

from pathlib import Path

from mimeo.config import Settings, ensure_dirs
from mimeo.schemas import ClusteredCorpus, ClusteredItem, FetchedContent
from mimeo.verify import (
    _MATCH_THRESHOLD,
    _best_window_ratio,
    _normalize,
    verify_quotes,
)


def _fetched(source_id: str, text: str) -> FetchedContent:
    return FetchedContent(
        source_id=source_id,
        url=f"https://x.com/{source_id}",
        title="t",
        text=text,
        char_count=len(text),
        fetch_method="parallel-excerpt",
    )


def _corpus_with(quote: str | None, source_ids: list[str]) -> ClusteredCorpus:
    return ClusteredCorpus(
        expert_name="E",
        principles=[
            ClusteredItem(
                label="Seek leverage",
                summary="s",
                representative_quote=quote,
                source_ids=source_ids,
            )
        ],
    )


def test_normalize_straightens_smart_quotes_and_whitespace() -> None:
    n = _normalize("\u201cHello\u2014World\u201d\n  foo")
    assert n == '"hello-world" foo'


def test_best_window_ratio_matches_exact_substring() -> None:
    text = _normalize("The leverage is the key to wealth, some padding blah blah.")
    needle = _normalize("leverage is the key to wealth")
    assert _best_window_ratio(needle, text) == 1.0


def test_best_window_ratio_fuzzy_close_enough() -> None:
    text = _normalize("Leverage is the key to wealth creation over time.")
    needle = _normalize("leverage is the the key to wealth")  # light drift
    assert _best_window_ratio(needle, text) >= _MATCH_THRESHOLD


def test_verify_quotes_strips_unverifiable(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path, verify_quotes=True)
    ensure_dirs(settings)
    corpus = _corpus_with(
        quote="Totally fabricated line that the source never actually said.",
        source_ids=["src_000"],
    )
    fetched = [_fetched("src_000", "A completely unrelated source body." * 20)]

    cleaned, report = verify_quotes(
        corpus=corpus, fetched=fetched, settings=settings
    )
    assert report.total == 1
    assert report.verified == 0
    assert cleaned.principles[0].representative_quote is None
    # Markdown + JSON audit trail produced.
    workspace = settings.workspace_dir
    assert (workspace / "quote_verification.json").exists()
    assert (workspace / "quote_verification.md").exists()


def test_verify_quotes_accepts_verbatim_match(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path, verify_quotes=True)
    ensure_dirs(settings)
    quote = "Leverage is the key to wealth, used wisely."
    text = "Intro ... " + quote + " ... outro padding."
    corpus = _corpus_with(quote=quote, source_ids=["src_000"])
    fetched = [_fetched("src_000", text)]

    cleaned, report = verify_quotes(
        corpus=corpus, fetched=fetched, settings=settings
    )
    assert report.verified == 1
    assert report.total == 1
    assert cleaned.principles[0].representative_quote == quote
    # No markdown report when all passed.
    assert not (settings.workspace_dir / "quote_verification.md").exists()


def test_verify_quotes_fuzzy_match_typographic_drift(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path, verify_quotes=True)
    ensure_dirs(settings)
    # Source uses curly quotes and em-dash; clustered quote uses straight
    # quotes and a hyphen. Should still match.
    source_text = "Before \u201cSpecific knowledge \u2014 cannot be taught\u201d after."
    quote = 'Specific knowledge - cannot be taught'
    corpus = _corpus_with(quote=quote, source_ids=["src_000"])
    fetched = [_fetched("src_000", source_text)]

    _cleaned, report = verify_quotes(
        corpus=corpus, fetched=fetched, settings=settings
    )
    assert report.verified == 1


def test_verify_quotes_passes_short_quotes_through(tmp_path: Path) -> None:
    """Very short quotes are too ambiguous to fuzzy-match; we pass them."""
    settings = Settings(expert_name="E", output_dir=tmp_path, verify_quotes=True)
    ensure_dirs(settings)
    corpus = _corpus_with(quote="Go long.", source_ids=["src_000"])
    fetched = [_fetched("src_000", "Completely unrelated text." * 10)]

    _cleaned, report = verify_quotes(
        corpus=corpus, fetched=fetched, settings=settings
    )
    assert report.verified == 1


def test_verify_quotes_handles_missing_source_text(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path, verify_quotes=True)
    ensure_dirs(settings)
    corpus = _corpus_with(
        quote="A longer quote that cannot be verified anywhere at all.",
        source_ids=["src_missing"],
    )
    _cleaned, report = verify_quotes(
        corpus=corpus, fetched=[], settings=settings
    )
    assert report.total == 1
    assert report.verified == 0


def test_verify_quotes_ignores_items_without_quote(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path, verify_quotes=True)
    ensure_dirs(settings)
    corpus = _corpus_with(quote=None, source_ids=["src_000"])
    fetched = [_fetched("src_000", "Anything.")]
    _cleaned, report = verify_quotes(
        corpus=corpus, fetched=fetched, settings=settings
    )
    assert report.total == 0
    assert report.pass_rate == 1.0


def test_verify_quotes_no_report_when_disabled_in_caller(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path)
    ensure_dirs(settings)
    corpus = _corpus_with(
        quote="Something that will not be verified no matter what.",
        source_ids=["src_000"],
    )
    fetched = [_fetched("src_000", "Other text.")]
    _cleaned, _report = verify_quotes(
        corpus=corpus, fetched=fetched, settings=settings, write_report=False
    )
    assert not (settings.workspace_dir / "quote_verification.json").exists()


def test_normalize_empty_returns_empty() -> None:
    assert _normalize("") == ""


def test_best_window_ratio_empty_inputs() -> None:
    assert _best_window_ratio("", "haystack") == 0.0
    assert _best_window_ratio("needle", "") == 0.0
    # Haystack shorter than half the needle → skip.
    assert _best_window_ratio("long needle looking thing", "ab") == 0.0


def test_best_window_ratio_short_candidate_at_tail() -> None:
    """When the anchor lands near the end, the candidate gets truncated.

    The function should skip windows that are shorter than half the needle
    rather than scoring them.
    """
    needle = "the quick brown fox jumps over the lazy dog again"
    # Put the anchor right at the end so the candidate starts there and
    # gets cut off by the string bound.
    anchor_fragment = needle[len(needle) // 2 - 8 : len(needle) // 2 + 8]
    haystack = "x" * 10 + anchor_fragment  # candidate window will run off end
    # Just exercises the short-candidate continue branch; we don't care
    # about the numeric result.
    _ = _best_window_ratio(_normalize(needle), _normalize(haystack))


def test_verify_quotes_ignores_whitespace_only_quote(tmp_path: Path) -> None:
    settings = Settings(expert_name="E", output_dir=tmp_path)
    ensure_dirs(settings)
    corpus = _corpus_with(quote="   ", source_ids=["src_000"])
    fetched = [_fetched("src_000", "Body.")]
    _cleaned, report = verify_quotes(
        corpus=corpus, fetched=fetched, settings=settings
    )
    # Whitespace-only reads as "no quote": it should not be counted.
    assert report.total == 0
