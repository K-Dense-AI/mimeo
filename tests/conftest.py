"""Shared fixtures and fakes for the offline test suite.

The goal is to be able to exercise every module — including the full
pipeline — without making real API calls. Tests that *must* hit the network
live in ``test_live.py`` and are opt-in via ``MIMEO_LIVE=1``.
"""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import BaseModel

from mimeo.config import Settings
from mimeo.llm import LLMClient
from mimeo.parallel_client import ParallelClient
from mimeo.schemas import (
    AgentsOutput,
    ClusteredCorpus,
    ClusteredItem,
    Extraction,
    FetchedContent,
    Principle,
    Quote,
    RankedSources,
    SkillOutput,
    Source,
)


@pytest.fixture(autouse=True)
def _stub_api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every test gets dummy keys so client construction doesn't blow up.

    Real network calls are blocked by the fakes below; the keys are just
    there to satisfy the ``require_*_key`` gates during ``__init__``.

    In live mode (``MIMEO_LIVE=1``) we leave whatever keys the developer
    loaded from ``.env`` intact so the tests in ``test_live.py`` can hit
    real APIs.
    """
    if os.environ.get("MIMEO_LIVE") == "1":
        return
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-dummy")
    monkeypatch.setenv("PARALLEL_API_KEY", "plx-test-dummy")


class FakeLLMClient:
    """Drop-in stand-in for :class:`mimeo.llm.LLMClient`.

    Tests push expected outputs onto ``queue`` (one per schema type, in the
    order the pipeline will request them). ``structured`` pops the next
    matching item; ``complete`` uses ``complete_replies`` the same way.

    The fake also records every call for assertion purposes.
    """

    def __init__(
        self,
        *,
        model: str = "anthropic/claude-opus-4.7",
        structured_by_schema: dict[type[BaseModel], list[BaseModel]] | None = None,
        complete_replies: list[str] | None = None,
    ) -> None:
        self.model = model
        self._structured_by_schema: dict[type[BaseModel], list[BaseModel]] = (
            structured_by_schema or {}
        )
        self._complete_replies: list[str] = list(complete_replies or [])
        self.structured_calls: list[tuple[type[BaseModel], str, str | None]] = []
        self.complete_calls: list[tuple[str, str | None]] = []

    def queue_structured(self, schema: type[BaseModel], value: BaseModel) -> None:
        self._structured_by_schema.setdefault(schema, []).append(value)

    async def structured(
        self,
        *,
        system: str | None,
        user: str,
        schema: type[BaseModel],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> BaseModel:
        self.structured_calls.append((schema, user, system))
        queue = self._structured_by_schema.get(schema)
        if not queue:
            raise AssertionError(
                f"FakeLLMClient has no queued response for schema {schema.__name__}"
            )
        return queue.pop(0)

    async def complete(
        self,
        *,
        system: str | None,
        user: str,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> str:
        self.complete_calls.append((user, system))
        if not self._complete_replies:
            raise AssertionError("FakeLLMClient has no queued complete replies")
        return self._complete_replies.pop(0)


class FakeParallelClient:
    """Drop-in stand-in for :class:`mimeo.parallel_client.ParallelClient`."""

    def __init__(
        self,
        *,
        search_by_bucket: dict[str, Any] | None = None,
        default_search: Any | None = None,
        extract_result: Any | None = None,
        deep_research_result: Any | None = None,
        deep_research_raises: BaseException | None = None,
    ) -> None:
        self._search_by_bucket = search_by_bucket or {}
        self._default_search = default_search
        self._extract_result = extract_result
        self._deep_research_result = deep_research_result
        self._deep_research_raises = deep_research_raises
        self.search_calls: list[tuple[str, list[str]]] = []
        self.extract_calls: list[list[str]] = []
        self.deep_research_calls: list[str] = []

    async def search(
        self,
        *,
        objective: str,
        search_queries: list[str] | None = None,
        max_chars_total: int = 30_000,
        mode: str = "advanced",
    ) -> Any:
        self.search_calls.append((objective, list(search_queries or [])))
        # Route by the leading keyword of the first query, which contains the
        # bucket name (see BUCKETS in discovery.py).
        for key, val in self._search_by_bucket.items():
            if key in objective.lower():
                return val
        if self._default_search is None:
            return SimpleNamespace(results=[])
        return self._default_search

    async def extract(
        self,
        *,
        urls: list[str],
        objective: str | None = None,
        max_chars_total: int = 20_000,
    ) -> Any:
        self.extract_calls.append(list(urls))
        if self._extract_result is None:
            return SimpleNamespace(results=[])
        return self._extract_result

    async def deep_research(
        self,
        *,
        input_text: str,
        processor: str = "pro-fast",
        metadata: dict[str, Any] | None = None,
        poll_interval_s: float = 10.0,
        max_wait_s: float = 60 * 25,
    ) -> Any:
        self.deep_research_calls.append(input_text)
        if self._deep_research_raises is not None:
            raise self._deep_research_raises
        return self._deep_research_result


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        max_sources=5,
        concurrency=2,
    )


@pytest.fixture
def fake_llm() -> FakeLLMClient:
    return FakeLLMClient()


def make_search_result(items: list[dict[str, Any]]) -> Any:
    """Build a parallel-web SearchResult-like object from simple dicts."""
    results = [
        SimpleNamespace(
            url=item.get("url"),
            title=item.get("title"),
            publish_date=item.get("publish_date"),
            excerpts=item.get("excerpts", []),
        )
        for item in items
    ]
    return SimpleNamespace(results=results)


def make_extract_response(
    full_content: str | None = None,
    excerpts: list[str] | None = None,
    title: str | None = None,
) -> Any:
    item = SimpleNamespace(
        full_content=full_content,
        excerpts=excerpts or [],
        title=title,
    )
    return SimpleNamespace(results=[item])


def sample_ranked_sources(expert_name: str = "Test Expert") -> RankedSources:
    return RankedSources(
        sources=[
            Source(
                id="src_000",
                url="https://example.com/essay",
                title="The Canonical Essay",
                kind="essay",
                bucket="essays",
                canonicity_score=0.95,
                excerpts=["Leverage is the key to wealth."],
            )
        ]
    )


def sample_extraction(source_id: str = "src_000") -> Extraction:
    return Extraction(
        source_id=source_id,
        summary="A short summary.",
        themes=["leverage", "compounding"],
        principles=[
            Principle(
                statement="Seek leverage.",
                rationale="Leverage multiplies effort.",
                source_quote="Leverage is the key.",
                source_id=source_id,
            )
        ],
        signature_quotes=[
            Quote(
                text="Leverage is the key.",
                context="On wealth creation.",
                source_id=source_id,
            )
        ],
    )


def sample_clustered_corpus(expert_name: str = "Test Expert") -> ClusteredCorpus:
    return ClusteredCorpus(
        expert_name=expert_name,
        themes=["leverage"],
        principles=[
            ClusteredItem(
                label="Seek leverage",
                summary="Use tools, capital, and content to multiply effort.",
                representative_quote="Leverage is the key.",
                source_ids=["src_000"],
            )
        ],
        signature_quotes=[
            ClusteredItem(
                label="Leverage quote",
                summary="Leverage is the key.",
                source_ids=["src_000"],
            )
        ],
    )


def sample_skill_output() -> SkillOutput:
    return SkillOutput(
        skill_name="test-expert",
        description=(
            "Think like Test Expert. Use when the user is deciding about "
            "leverage, compounding, or long-term strategy."
        ),
        skill_body="# Thinking like Test Expert\n\nOverview.\n",
        principles_md="# Principles\n\n## Seek leverage\n\nUse tools.\n",
        frameworks_md="# Frameworks\n\nNone yet.\n",
        mental_models_md="# Mental models\n\nNone yet.\n",
        quotes_md="# Quotes\n\n> Leverage is the key.\n",
    )


def sample_agents_output() -> AgentsOutput:
    return AgentsOutput(
        content=(
            "# Think like Test Expert\n\n"
            "Overview.\n\n"
            "## Default stance\n\n- Favor leverage.\n"
        )
    )


def sample_fetched(source_id: str = "src_000") -> FetchedContent:
    return FetchedContent(
        source_id=source_id,
        url="https://example.com/essay",
        title="The Canonical Essay",
        text="Leverage is the key to wealth. " * 200,
        char_count=5_000,
        fetch_method="parallel-excerpt",
    )
