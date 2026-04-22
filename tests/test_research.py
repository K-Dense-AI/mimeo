"""Offline tests for :mod:`mimeo.research`."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.research import _stringify_output, deep_research

from .conftest import FakeParallelClient


# ---------------------------------------------------------------------------
# _stringify_output
# ---------------------------------------------------------------------------


def test_stringify_output_none() -> None:
    assert _stringify_output(None) == ""


def test_stringify_output_prefers_content_attr() -> None:
    obj = SimpleNamespace(content="hello", text=None)
    assert _stringify_output(obj) == "hello"


def test_stringify_output_tries_alt_attrs() -> None:
    obj = SimpleNamespace(content="   ", text="via-text")
    assert _stringify_output(obj) == "via-text"


def test_stringify_output_dict_fallback() -> None:
    assert _stringify_output({"text": "hi"}) == "hi"


def test_stringify_output_pydantic_dump_fallback() -> None:
    class _Obj:
        def model_dump_json(self, **_: object) -> str:
            return "{\"dumped\": true}"

    out = _stringify_output(_Obj())
    assert "dumped" in out


def test_stringify_output_str_fallback() -> None:
    class _Bare:
        def __str__(self) -> str:
            return "bare-string"

    assert _stringify_output(_Bare()) == "bare-string"


# ---------------------------------------------------------------------------
# deep_research
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deep_research_happy(settings: Settings) -> None:
    ensure_dirs(settings)
    parallel = FakeParallelClient(
        deep_research_result=SimpleNamespace(
            output=SimpleNamespace(content="Full synthesis text.")
        )
    )
    pair = await deep_research(settings=settings, parallel=parallel)
    assert pair is not None
    src, content = pair
    assert src.id == "src_research"
    assert content.text == "Full synthesis text."
    # Cache written.
    assert (settings.workspace_dir / "research" / "report.json").exists()


@pytest.mark.asyncio
async def test_deep_research_cache_round_trip(settings: Settings) -> None:
    ensure_dirs(settings)
    parallel = FakeParallelClient(
        deep_research_result=SimpleNamespace(
            output=SimpleNamespace(content="Initial run.")
        )
    )
    first = await deep_research(settings=settings, parallel=parallel)
    assert first is not None

    # Second call with refresh=False returns cached without re-invoking parallel.
    before = len(parallel.deep_research_calls)
    second = await deep_research(settings=settings, parallel=parallel)
    assert second is not None
    assert second[1].text == "Initial run."
    assert len(parallel.deep_research_calls) == before


@pytest.mark.asyncio
async def test_deep_research_returns_none_on_error(settings: Settings) -> None:
    ensure_dirs(settings)
    parallel = FakeParallelClient(
        deep_research_raises=RuntimeError("task API down")
    )
    pair = await deep_research(settings=settings, parallel=parallel)
    assert pair is None


@pytest.mark.asyncio
async def test_deep_research_returns_none_on_empty_output(settings: Settings) -> None:
    ensure_dirs(settings)
    parallel = FakeParallelClient(
        deep_research_result=SimpleNamespace(output=None)
    )
    pair = await deep_research(settings=settings, parallel=parallel)
    assert pair is None
