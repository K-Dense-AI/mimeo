"""Tests for versioned cache envelopes and fingerprints."""

from __future__ import annotations

from pathlib import Path

from mimeo.cache import (
    CACHE_LAYOUT_VERSION,
    canonical_data,
    digest,
    fingerprint,
    load_cache,
    prompt_digest,
    store_cache,
)
from mimeo.schemas import Source


def test_digest_is_stable_for_equivalent_mapping_order() -> None:
    assert digest({"a": 1, "b": [2, 3]}) == digest({"b": [2, 3], "a": 1})


def test_canonical_data_handles_paths_tuples_and_sets(tmp_path: Path) -> None:
    normalized = canonical_data(
        {
            "path": tmp_path,
            "tuple": (2, 1),
            "set": {"b", "a"},
        }
    )
    assert normalized == {
        "path": str(tmp_path),
        "set": ["a", "b"],
        "tuple": [2, 1],
    }


def test_prompt_digest_accepts_names_with_or_without_extension() -> None:
    assert prompt_digest("extract") == prompt_digest("extract.md")


def test_fingerprint_changes_with_any_input() -> None:
    first = fingerprint("fetch", mode="captions", source_id="src_001")
    second = fingerprint("fetch", mode="full", source_id="src_001")
    assert first != second


def test_cache_round_trip_supports_models(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    fp = fingerprint("source", source_id="src_001")
    source = Source(id="src_001", url="https://example.com", bucket="essays")

    store_cache(path, fp, source)

    loaded = load_cache(path, fp)
    assert Source.model_validate(loaded) == source


def test_cache_rejects_wrong_fingerprint_legacy_and_corruption(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    fp = fingerprint("stage", value=1)
    store_cache(path, fp, {"value": 1})
    assert load_cache(path, fingerprint("stage", value=2)) is None

    path.write_text('{"value": 1}', encoding="utf-8")
    assert load_cache(path, fp) is None

    path.write_text("{bad", encoding="utf-8")
    assert load_cache(path, fp) is None


def test_cache_rejects_missing_file_non_mapping_layout_and_data(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    fp = fingerprint("stage", value=1)
    assert load_cache(path, fp) is None

    path.write_text("[]", encoding="utf-8")
    assert load_cache(path, fp) is None

    path.write_text(
        f'{{"version": {CACHE_LAYOUT_VERSION + 1}, "fingerprint": "{fp}", "data": 1}}',
        encoding="utf-8",
    )
    assert load_cache(path, fp) is None

    path.write_text(
        f'{{"version": {CACHE_LAYOUT_VERSION}, "fingerprint": "{fp}"}}',
        encoding="utf-8",
    )
    assert load_cache(path, fp) is None
