"""Search provider protocol and normalized result objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .config import SearchProviderName, Settings


@dataclass(frozen=True)
class SearchResultItem:
    url: str | None = None
    title: str | None = None
    publish_date: str | None = None
    excerpts: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SearchResponse:
    results: list[SearchResultItem] = field(default_factory=list)


@dataclass(frozen=True)
class ExtractResultItem:
    full_content: str | None = None
    excerpts: list[str] = field(default_factory=list)
    title: str | None = None


@dataclass(frozen=True)
class ExtractResponseData:
    results: list[ExtractResultItem] = field(default_factory=list)


class SearchProvider(Protocol):
    async def search(
        self,
        *,
        objective: str,
        search_queries: list[str] | None = None,
        max_chars_total: int = 30_000,
        mode: str = "advanced",
    ) -> SearchResponse:
        ...

    async def extract(
        self,
        *,
        urls: list[str],
        objective: str | None = None,
        max_chars_total: int = 20_000,
    ) -> ExtractResponseData:
        ...

    async def deep_research(
        self,
        *,
        input_text: str,
        processor: str = "pro-fast",
        metadata: dict[str, Any] | None = None,
        poll_interval_s: float = 10.0,
        max_wait_s: float = 60 * 25,
    ) -> Any:
        ...


def create_search_provider(settings: Settings) -> SearchProvider:
    return create_search_provider_by_name(settings.search_provider)


def create_search_provider_by_name(provider: SearchProviderName) -> SearchProvider:
    if provider == "parallel":
        from .parallel_client import ParallelClient

        return ParallelClient()
    raise ValueError(f"Unsupported search provider: {provider}")


def normalize_search_response(response: Any) -> SearchResponse:
    items: list[SearchResultItem] = []
    for item in getattr(response, "results", []) or []:
        publish_date = getattr(item, "publish_date", None)
        items.append(
            SearchResultItem(
                url=str(getattr(item, "url", "") or "") or None,
                title=getattr(item, "title", None),
                publish_date=str(publish_date) if publish_date else None,
                excerpts=list(getattr(item, "excerpts", []) or []),
            )
        )
    return SearchResponse(results=items)


def normalize_extract_response(response: Any) -> ExtractResponseData:
    items: list[ExtractResultItem] = []
    for item in getattr(response, "results", []) or []:
        items.append(
            ExtractResultItem(
                full_content=getattr(item, "full_content", None),
                excerpts=list(getattr(item, "excerpts", []) or []),
                title=getattr(item, "title", None),
            )
        )
    return ExtractResponseData(results=items)

