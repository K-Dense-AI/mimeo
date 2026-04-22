"""Thin wrapper around the official ``parallel-web`` Python SDK.

Exposes three high-level operations:

* :meth:`ParallelClient.search` — single Search API call.
* :meth:`ParallelClient.extract` — LLM-optimized full content for known URLs.
* :meth:`ParallelClient.deep_research` — create + poll a Task API run.

All calls are async and retried on transient errors via ``tenacity``.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from parallel import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncParallel,
    RateLimitError,
)
from parallel.types import ExtractResponse, SearchResult, TaskRun, TaskRunResult
from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_exponential,
)

from .config import require_parallel_key

logger = logging.getLogger(__name__)


# Status codes that indicate a transient server-side problem and are worth
# retrying. 4xx class errors (except 408/425/429) generally won't succeed on
# retry and should surface immediately.
_RETRYABLE_STATUS_CODES = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (APIConnectionError, APITimeoutError, RateLimitError)):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code in _RETRYABLE_STATUS_CODES
    return False


def _retryer(attempts: int = 4) -> AsyncRetrying:
    from tenacity import retry_if_exception

    return AsyncRetrying(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )


class ParallelClient:
    """Facade that keeps a single ``AsyncParallel`` under the hood."""

    def __init__(self) -> None:
        self._client = AsyncParallel(api_key=require_parallel_key())

    async def search(
        self,
        *,
        objective: str,
        search_queries: list[str] | None = None,
        max_chars_total: int = 30_000,
        mode: str = "advanced",
    ) -> SearchResult:
        """Run one Search API call.

        ``objective`` is a natural-language description of what we want.
        ``search_queries`` are optional targeted keyword queries.
        """
        queries = search_queries or [objective]
        async for attempt in _retryer():
            with attempt:
                return await self._client.search(
                    objective=objective,
                    search_queries=queries,
                    max_chars_total=max_chars_total,
                    mode=mode,  # type: ignore[arg-type]
                )
        raise RuntimeError("unreachable")  # pragma: no cover - tenacity reraises

    async def extract(
        self,
        *,
        urls: list[str],
        objective: str | None = None,
        max_chars_total: int = 20_000,
    ) -> ExtractResponse:
        """Get LLM-optimized full content for specific URLs."""
        async for attempt in _retryer():
            with attempt:
                return await self._client.extract(
                    urls=urls,
                    objective=objective,
                    max_chars_total=max_chars_total,
                )
        raise RuntimeError("unreachable")  # pragma: no cover - tenacity reraises

    async def deep_research(
        self,
        *,
        input_text: str,
        processor: str = "pro-fast",
        metadata: dict[str, Any] | None = None,
        poll_interval_s: float = 10.0,
        max_wait_s: float = 60 * 25,
    ) -> TaskRunResult:
        """Create a Task API run and poll until it completes.

        Processors (from Parallel docs):

        * ``pro-fast`` — 30s-5min, good default
        * ``ultra-fast`` — 1-10min, deeper
        * ``ultra`` — 5-25min, maximum depth
        """
        # Cast metadata values to str|int|float|bool only (the SDK restricts).
        safe_metadata: dict[str, str | float | bool] | None = None
        if metadata:
            safe_metadata = {
                k: v
                for k, v in metadata.items()
                if isinstance(v, (str, int, float, bool))
            }

        run: TaskRun = await self._client.task_run.create(
            input=input_text,
            processor=processor,
            metadata=safe_metadata,  # type: ignore[arg-type]
        )
        run_id = run.run_id
        logger.info("Started Parallel deep-research run %s (processor=%s)", run_id, processor)

        deadline = asyncio.get_event_loop().time() + max_wait_s
        while True:
            try:
                # Use the server-side long-poll via api_timeout.
                return await self._client.task_run.result(
                    run_id, api_timeout=int(min(poll_interval_s * 3, 540))
                )
            except APITimeoutError:
                pass
            except APIStatusError as exc:
                # 408/425-style "still running" surfaces as a status error on
                # some deployments; retry until our overall deadline hits.
                if exc.status_code in (408, 425, 504):
                    logger.debug("Task %s not ready yet (%s), continuing", run_id, exc.status_code)
                else:
                    raise

            if asyncio.get_event_loop().time() > deadline:
                raise TimeoutError(
                    f"Parallel deep-research run {run_id} exceeded {max_wait_s:.0f}s deadline"
                )
            await asyncio.sleep(poll_interval_s)
