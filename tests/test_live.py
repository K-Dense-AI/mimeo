"""Live tests that hit real APIs. Opt in with ``MIMEO_LIVE=1``.

These are intentionally small (cheap) smoke checks. They verify that each
external integration is wired correctly end-to-end. The full pipeline is
exercised separately via the CLI.
"""

from __future__ import annotations

import os

import pytest

from mimeo.fetchers.youtube import fetch_youtube_captions
from mimeo.llm import LLMClient
from mimeo.parallel_client import ParallelClient
from mimeo.schemas import ClusteredItem, Source

LIVE = os.environ.get("MIMEO_LIVE") == "1"
pytestmark = pytest.mark.skipif(not LIVE, reason="MIMEO_LIVE=1 not set")


@pytest.mark.asyncio
async def test_parallel_search() -> None:
    """Smallest possible Parallel Search API round-trip."""
    parallel = ParallelClient()
    result = await parallel.search(
        objective="Short biographical pages about Naval Ravikant on his own site or Wikipedia.",
        search_queries=["Naval Ravikant bio", "Naval Ravikant about"],
        max_chars_total=4_000,
    )
    assert result.results, "Search returned no results"
    first = result.results[0]
    assert first.url, "first result has no URL"
    # Either excerpts or title should be present on any reasonable result.
    assert first.title or first.excerpts


LLM_PROVIDER_CASES = [
    ("openrouter", None, ("OPENROUTER_API_KEY",)),
    ("openai", "MIMEO_OPENAI_MODEL", ("OPENAI_API_KEY",)),
    ("anthropic", "MIMEO_ANTHROPIC_MODEL", ("ANTHROPIC_API_KEY",)),
    ("xai", "MIMEO_XAI_MODEL", ("XAI_API_KEY",)),
    ("google", "MIMEO_GOOGLE_MODEL", ("GEMINI_API_KEY", "GOOGLE_API_KEY")),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("provider, model_env, key_envs", LLM_PROVIDER_CASES)
async def test_llm_provider_structured(
    provider: str,
    model_env: str | None,
    key_envs: tuple[str, ...],
) -> None:
    """Selected LLM providers return JSON that validates against a pydantic schema."""
    if not any(os.environ.get(name) for name in key_envs):
        pytest.skip(f"{' or '.join(key_envs)} not set")
    model = os.environ.get(model_env) if model_env else None
    if provider != "openrouter" and not model:
        pytest.skip(f"{model_env} not set")

    llm = LLMClient(provider=provider, model=model)  # type: ignore[arg-type]
    item = await llm.structured(
        system="You extract structured data.",
        user=(
            "Return a ClusteredItem describing the idea 'compounding' with "
            "label='Compounding', a 1-sentence summary, source_ids=['src_000']."
        ),
        schema=ClusteredItem,
        temperature=0.0,
    )
    assert item.label
    assert item.summary
    assert item.source_ids == ["src_000"]


@pytest.mark.asyncio
async def test_youtube_captions() -> None:
    """Pull captions for a well-known, long-lived, captioned video."""
    # Andrej Karpathy - State of GPT (public, has captions).
    source = Source(
        id="live_yt_0",
        url="https://www.youtube.com/watch?v=bZQun8Y4L2A",
        title="State of GPT",
        kind="talk",
        medium="youtube",
        bucket="talks",
    )
    fetched = await fetch_youtube_captions(source)
    # We tolerate no-captions-today by checking the method field. The real
    # assertion is "code path executed without raising".
    assert fetched.fetch_method.startswith("youtube")
    if fetched.fetch_method == "youtube-captions":
        assert fetched.char_count > 1_000, "expected non-trivial transcript"
