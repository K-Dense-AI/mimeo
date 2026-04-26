"""Offline tests for provider-neutral search plumbing."""

from __future__ import annotations

from types import SimpleNamespace

from mimeo.config import Settings
from mimeo.parallel_client import ParallelClient
from mimeo.search import (
    create_search_provider,
    normalize_extract_response,
    normalize_search_response,
)


def test_normalize_search_response() -> None:
    response = SimpleNamespace(
        results=[
            SimpleNamespace(
                url="https://example.com",
                title="Example",
                publish_date="2026-01-01",
                excerpts=["a", "b"],
            ),
            SimpleNamespace(url=None, title="No URL", excerpts=None),
        ]
    )
    out = normalize_search_response(response)
    assert out.results[0].url == "https://example.com"
    assert out.results[0].excerpts == ["a", "b"]
    assert out.results[1].url is None
    assert out.results[1].excerpts == []


def test_normalize_extract_response() -> None:
    response = SimpleNamespace(
        results=[
            SimpleNamespace(full_content="Full", excerpts=["Fallback"], title="T")
        ]
    )
    out = normalize_extract_response(response)
    assert out.results[0].full_content == "Full"
    assert out.results[0].excerpts == ["Fallback"]
    assert out.results[0].title == "T"


def test_create_search_provider_defaults_to_parallel(tmp_path) -> None:
    settings = Settings(expert_name="N", output_dir=tmp_path)
    provider = create_search_provider(settings)
    assert isinstance(provider, ParallelClient)

