"""Offline tests for :mod:`mimeo.parallel_client`."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from parallel import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from mimeo.parallel_client import ParallelClient, _is_retryable


def _req() -> httpx.Request:
    return httpx.Request("POST", "https://api.parallel.ai/v1/alpha/search")


def _status(code: int) -> APIStatusError:
    return APIStatusError(
        message=f"HTTP {code}",
        response=httpx.Response(code, request=_req()),
        body=None,
    )


# ---------------------------------------------------------------------------
# Retry predicate
# ---------------------------------------------------------------------------


def test_is_retryable_matrix() -> None:
    req = _req()
    assert _is_retryable(APIConnectionError(request=req)) is True
    assert _is_retryable(APITimeoutError(request=req)) is True
    assert _is_retryable(
        RateLimitError(
            message="rl",
            response=httpx.Response(429, request=req),
            body=None,
        )
    ) is True
    assert _is_retryable(_status(500)) is True
    assert _is_retryable(_status(408)) is True
    assert _is_retryable(_status(401)) is False
    assert _is_retryable(_status(404)) is False
    assert _is_retryable(RuntimeError("x")) is False


# ---------------------------------------------------------------------------
# ParallelClient scripted-SDK tests
# ---------------------------------------------------------------------------


class _ScriptedCallable:
    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        r = self._responses.pop(0)
        if isinstance(r, BaseException):
            raise r
        return r


def _install(client: ParallelClient, **attrs: Any) -> None:
    """Replace ``client._client`` with a namespace containing scripted methods."""
    client._client = SimpleNamespace(**attrs)  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_search_passes_through() -> None:
    client = ParallelClient()
    scripted = _ScriptedCallable([SimpleNamespace(results=[])])
    _install(client, search=scripted)
    result = await client.search(objective="find things", search_queries=["q1"])
    assert result.results == []
    assert scripted.calls[0]["objective"] == "find things"
    assert scripted.calls[0]["search_queries"] == ["q1"]


@pytest.mark.asyncio
async def test_search_defaults_queries_to_objective() -> None:
    client = ParallelClient()
    scripted = _ScriptedCallable([SimpleNamespace(results=[])])
    _install(client, search=scripted)
    await client.search(objective="solo")
    assert scripted.calls[0]["search_queries"] == ["solo"]


@pytest.mark.asyncio
async def test_search_retries_on_transient(monkeypatch: pytest.MonkeyPatch) -> None:
    client = ParallelClient()
    scripted = _ScriptedCallable(
        [_status(503), APIConnectionError(request=_req()), SimpleNamespace(results=[])]
    )
    _install(client, search=scripted)
    monkeypatch.setattr(
        "mimeo.parallel_client.wait_exponential", lambda **_: lambda *_a, **_k: 0
    )
    result = await client.search(objective="x")
    assert result.results == []
    assert len(scripted.calls) == 3


@pytest.mark.asyncio
async def test_search_surfaces_4xx_immediately() -> None:
    client = ParallelClient()
    scripted = _ScriptedCallable([_status(401)])
    _install(client, search=scripted)
    with pytest.raises(APIStatusError):
        await client.search(objective="x")
    assert len(scripted.calls) == 1


@pytest.mark.asyncio
async def test_extract_passes_through() -> None:
    client = ParallelClient()
    scripted = _ScriptedCallable([SimpleNamespace(results=[])])
    _install(client, extract=scripted)
    await client.extract(urls=["https://a", "https://b"], objective="obj")
    assert scripted.calls[0]["urls"] == ["https://a", "https://b"]
    assert scripted.calls[0]["objective"] == "obj"


# ---------------------------------------------------------------------------
# deep_research poll loop
# ---------------------------------------------------------------------------


class _DeepResearchHarness:
    """Builds a scripted ``task_run`` namespace for the poll loop."""

    def __init__(self, *, create: Any, results: list[Any]) -> None:
        self._results = list(results)
        self.create_calls: list[dict[str, Any]] = []
        self.result_calls: list[dict[str, Any]] = []

        harness = self

        class _TaskRun:
            async def create(self, **kwargs: Any) -> Any:
                harness.create_calls.append(kwargs)
                if isinstance(create, BaseException):
                    raise create
                return create

            async def result(self, run_id: str, **kwargs: Any) -> Any:
                harness.result_calls.append({"run_id": run_id, **kwargs})
                r = harness._results.pop(0)
                if isinstance(r, BaseException):
                    raise r
                return r

        self.task_run = _TaskRun()


@pytest.mark.asyncio
async def test_deep_research_returns_first_success() -> None:
    client = ParallelClient()
    harness = _DeepResearchHarness(
        create=SimpleNamespace(run_id="run_123"),
        results=[SimpleNamespace(output=SimpleNamespace(content="done"))],
    )
    _install(client, task_run=harness.task_run)
    result = await client.deep_research(
        input_text="hello",
        metadata={"expert": "Naval", "skip": ["list", "is"], "n": 3, "flag": True},
    )
    assert result.output.content == "done"
    assert harness.create_calls[0]["input"] == "hello"
    # Unsafe metadata values (list) filtered out; safe values kept.
    md = harness.create_calls[0]["metadata"]
    assert md == {"expert": "Naval", "n": 3, "flag": True}


@pytest.mark.asyncio
async def test_deep_research_retries_on_timeout_and_status(monkeypatch: pytest.MonkeyPatch) -> None:
    client = ParallelClient()
    success = SimpleNamespace(output=SimpleNamespace(content="ok"))
    harness = _DeepResearchHarness(
        create=SimpleNamespace(run_id="run_999"),
        results=[APITimeoutError(request=_req()), _status(408), success],
    )
    _install(client, task_run=harness.task_run)
    # Skip the sleep between polls so the test runs fast.
    monkeypatch.setattr(asyncio, "sleep", lambda *_a, **_k: _noop())
    result = await client.deep_research(input_text="q", poll_interval_s=0.01)
    assert result is success
    assert len(harness.result_calls) == 3


@pytest.mark.asyncio
async def test_deep_research_raises_on_non_retryable_status() -> None:
    client = ParallelClient()
    harness = _DeepResearchHarness(
        create=SimpleNamespace(run_id="run_500"),
        results=[_status(500)],
    )
    _install(client, task_run=harness.task_run)
    with pytest.raises(APIStatusError):
        await client.deep_research(input_text="q")


@pytest.mark.asyncio
async def test_deep_research_respects_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    client = ParallelClient()
    harness = _DeepResearchHarness(
        create=SimpleNamespace(run_id="run_slow"),
        # Infinite supply of timeouts would loop forever if the deadline check didn't fire.
        results=[APITimeoutError(request=_req()) for _ in range(20)],
    )
    _install(client, task_run=harness.task_run)

    # Fast-forward the monotonic clock so the first loop iteration blows the deadline.
    fake_now = [1000.0]

    def _time() -> float:
        fake_now[0] += 100.0
        return fake_now[0]

    class _Loop:
        def time(self) -> float:
            return _time()

    monkeypatch.setattr(asyncio, "get_event_loop", lambda: _Loop())
    monkeypatch.setattr(asyncio, "sleep", lambda *_a, **_k: _noop())

    with pytest.raises(TimeoutError):
        await client.deep_research(input_text="q", max_wait_s=1.0, poll_interval_s=0.01)


async def _noop() -> None:
    return None
