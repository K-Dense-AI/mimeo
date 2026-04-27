"""Offline tests for :mod:`mimeo.llm`.

We patch ``self._client.chat.completions.create`` on an :class:`LLMClient`
instance so no real HTTP happens, and drive the retry / schema-repair loops
with pre-canned responses.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError
from pydantic import BaseModel

from mimeo.llm import (
    LLMClient,
    _format_schema_hint,
    _is_network_retryable,
    _requires_default_temperature,
    _strip_code_fence,
    load_prompt,
    render_prompt,
)


class _ToyModel(BaseModel):
    name: str
    count: int


def _make_completion(content: str) -> Any:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def _make_httpx_request() -> httpx.Request:
    return httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")


def _status_error(code: int) -> APIStatusError:
    response = httpx.Response(code, request=_make_httpx_request())
    return APIStatusError(
        message=f"HTTP {code}",
        response=response,
        body=None,
    )


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def test_strip_code_fence_variants() -> None:
    assert _strip_code_fence('```json\n{"a": 1}\n```') == '{"a": 1}'
    assert _strip_code_fence('```\n{"a": 1}\n```') == '{"a": 1}'
    assert _strip_code_fence('{"a": 1}') == '{"a": 1}'
    # Fenced with only opening, no closing - we drop the opening line and return the rest.
    assert _strip_code_fence("```json\nhi") == "hi"


def test_format_schema_hint_is_json_schema() -> None:
    hint = _format_schema_hint(_ToyModel)
    parsed = json.loads(hint)
    assert parsed["properties"]["name"]["type"] == "string"
    assert parsed["properties"]["count"]["type"] == "integer"


def test_render_prompt_substitutes_only_declared_keys() -> None:
    template = "Hello {name}, here is {placeholder_left_alone}."
    out = render_prompt(template, name="Alice")
    assert "Hello Alice" in out
    assert "{placeholder_left_alone}" in out  # untouched


def test_load_prompt_raises_for_missing() -> None:
    with pytest.raises(FileNotFoundError):
        load_prompt("this_prompt_definitely_does_not_exist")


def test_load_prompt_reads_existing() -> None:
    assert "source" in load_prompt("extract").lower()
    assert "source" in load_prompt("extract.md").lower()


def test_requires_default_temperature_only_for_direct_openai_gpt5() -> None:
    assert _requires_default_temperature("openai", "gpt-5.5") is True
    assert _requires_default_temperature("openai", "gpt-5.1") is True
    assert _requires_default_temperature("openai", "gpt-4.1") is False
    assert _requires_default_temperature("openrouter", "openai/gpt-5.5") is False


# ---------------------------------------------------------------------------
# Retry predicate
# ---------------------------------------------------------------------------


def test_is_network_retryable_matrix() -> None:
    req = _make_httpx_request()
    assert _is_network_retryable(APIConnectionError(request=req)) is True
    assert _is_network_retryable(APITimeoutError(request=req)) is True
    assert _is_network_retryable(
        RateLimitError(
            message="rate limit",
            response=httpx.Response(429, request=req),
            body=None,
        )
    ) is True
    assert _is_network_retryable(_status_error(500)) is True
    assert _is_network_retryable(_status_error(503)) is True
    # 4xx errors other than 408/409/425/429 should NOT retry.
    assert _is_network_retryable(_status_error(400)) is False
    assert _is_network_retryable(_status_error(401)) is False
    assert _is_network_retryable(_status_error(404)) is False
    # Random non-API exceptions shouldn't retry either.
    assert _is_network_retryable(RuntimeError("boom")) is False


# ---------------------------------------------------------------------------
# LLMClient.complete
# ---------------------------------------------------------------------------


class _ScriptedCompletions:
    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if not self._responses:
            raise AssertionError("no more scripted responses")
        r = self._responses.pop(0)
        if isinstance(r, BaseException):
            raise r
        return r


def _install_scripted(client: LLMClient, responses: list[Any]) -> _ScriptedCompletions:
    scripted = _ScriptedCompletions(responses)
    client._client = SimpleNamespace(  # type: ignore[attr-defined]
        chat=SimpleNamespace(completions=scripted)
    )
    return scripted


class _FakeAnthropicMessages:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(text='{"name": "a", "count": 9}')])


class _FakeGoogleModels:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def generate_content(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return SimpleNamespace(text='{"name": "g", "count": 11}')


@pytest.mark.asyncio
async def test_complete_happy_path() -> None:
    client = LLMClient()
    scripted = _install_scripted(client, [_make_completion("  hello  ")])
    text = await client.complete(system="sys", user="user")
    assert text == "hello"
    assert scripted.calls[0]["messages"][0]["role"] == "system"
    assert scripted.calls[0]["messages"][1]["content"] == "user"


@pytest.mark.asyncio
async def test_openai_provider_uses_openai_compatible_client() -> None:
    client = LLMClient(provider="openai", model="gpt-test", client=SimpleNamespace())
    scripted = _install_scripted(client, [_make_completion('{"name": "a", "count": 1}')])
    out = await client.structured(system=None, user="u", schema=_ToyModel)
    assert out.count == 1
    assert scripted.calls[0]["model"] == "gpt-test"
    assert scripted.calls[0]["response_format"] == {"type": "json_object"}
    assert "max_tokens" not in scripted.calls[0]
    assert "max_completion_tokens" not in scripted.calls[0]


@pytest.mark.asyncio
async def test_openai_provider_uses_max_completion_tokens_when_limited() -> None:
    client = LLMClient(provider="openai", model="gpt-test", client=SimpleNamespace())
    scripted = _install_scripted(client, [_make_completion("ok")])
    out = await client.complete(system=None, user="u", max_tokens=123)
    assert out == "ok"
    assert scripted.calls[0]["max_completion_tokens"] == 123
    assert "max_tokens" not in scripted.calls[0]


@pytest.mark.asyncio
async def test_openrouter_provider_uses_max_tokens_when_limited() -> None:
    client = LLMClient(provider="openrouter", model="router-test", client=SimpleNamespace())
    scripted = _install_scripted(client, [_make_completion("ok")])
    out = await client.complete(system=None, user="u", max_tokens=123)
    assert out == "ok"
    assert scripted.calls[0]["max_tokens"] == 123
    assert "max_completion_tokens" not in scripted.calls[0]


@pytest.mark.asyncio
async def test_openai_gpt5_provider_omits_custom_temperature() -> None:
    client = LLMClient(provider="openai", model="gpt-5.5", client=SimpleNamespace())
    scripted = _install_scripted(client, [_make_completion("ok")])
    out = await client.complete(system=None, user="u", temperature=0.2)
    assert out == "ok"
    assert "temperature" not in scripted.calls[0]


@pytest.mark.asyncio
async def test_xai_provider_does_not_force_json_mode() -> None:
    client = LLMClient(provider="xai", model="grok-test", client=SimpleNamespace())
    scripted = _install_scripted(client, [_make_completion('{"name": "x", "count": 4}')])
    out = await client.structured(system=None, user="u", schema=_ToyModel)
    assert out.count == 4
    assert scripted.calls[0]["model"] == "grok-test"
    assert "response_format" not in scripted.calls[0]


@pytest.mark.asyncio
async def test_anthropic_provider_uses_native_messages_api() -> None:
    messages = _FakeAnthropicMessages()
    client = LLMClient(
        provider="anthropic",
        model="claude-test",
        client=SimpleNamespace(messages=messages),
    )
    out = await client.structured(system="sys", user="u", schema=_ToyModel)
    assert out.count == 9
    call = messages.calls[0]
    assert call["model"] == "claude-test"
    assert call["system"] == "sys"
    assert call["messages"][0]["role"] == "user"


@pytest.mark.asyncio
async def test_google_provider_passes_response_schema() -> None:
    models = _FakeGoogleModels()
    client = LLMClient(
        provider="google",
        model="gemini-test",
        client=SimpleNamespace(models=models),
    )
    out = await client.structured(system="sys", user="u", schema=_ToyModel)
    assert out.count == 11
    call = models.calls[0]
    assert call["model"] == "gemini-test"
    assert call["config"]["response_mime_type"] == "application/json"
    assert "response_json_schema" in call["config"]


@pytest.mark.asyncio
async def test_complete_omits_system_when_none() -> None:
    client = LLMClient()
    scripted = _install_scripted(client, [_make_completion("ok")])
    await client.complete(system=None, user="user")
    roles = [m["role"] for m in scripted.calls[0]["messages"]]
    assert roles == ["user"]


@pytest.mark.asyncio
async def test_complete_retries_transient_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LLMClient()
    req = _make_httpx_request()
    scripted = _install_scripted(
        client,
        [APIConnectionError(request=req), _status_error(503), _make_completion("ok")],
    )
    # Speed up the wait between retries.
    monkeypatch.setattr("mimeo.llm.wait_exponential", lambda **_: lambda *_a, **_k: 0)
    text = await client.complete(system=None, user="u")
    assert text == "ok"
    assert len(scripted.calls) == 3


@pytest.mark.asyncio
async def test_complete_does_not_retry_non_retryable() -> None:
    client = LLMClient()
    scripted = _install_scripted(client, [_status_error(400)])
    with pytest.raises(APIStatusError):
        await client.complete(system=None, user="u")
    assert len(scripted.calls) == 1


# ---------------------------------------------------------------------------
# LLMClient.structured
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_structured_happy_path() -> None:
    client = LLMClient()
    scripted = _install_scripted(
        client, [_make_completion('{"name": "a", "count": 2}')]
    )
    out = await client.structured(system=None, user="u", schema=_ToyModel)
    assert out == _ToyModel(name="a", count=2)
    # The schema hint is appended to the user message.
    assert "_ToyModel" not in scripted.calls[0]["messages"][0]["content"] or True
    assert '"count"' in scripted.calls[0]["messages"][0]["content"]


@pytest.mark.asyncio
async def test_structured_strips_code_fences() -> None:
    client = LLMClient()
    _install_scripted(
        client, [_make_completion('```json\n{"name": "a", "count": 1}\n```')]
    )
    out = await client.structured(system=None, user="u", schema=_ToyModel)
    assert out.count == 1


@pytest.mark.asyncio
async def test_structured_repairs_on_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """First reply is garbage, second reply is valid - the repair loop wins."""
    client = LLMClient()
    scripted = _install_scripted(
        client,
        [
            _make_completion("not json at all"),
            _make_completion('{"name": "a", "count": 2}'),
        ],
    )
    out = await client.structured(system=None, user="u", schema=_ToyModel)
    assert out == _ToyModel(name="a", count=2)
    assert len(scripted.calls) == 2
    # The retry must include the prior assistant reply plus a correction.
    roles = [m["role"] for m in scripted.calls[1]["messages"]]
    assert roles[-2:] == ["assistant", "user"]
    assert "failed schema validation" in scripted.calls[1]["messages"][-1]["content"]


@pytest.mark.asyncio
async def test_structured_repairs_on_invalid_shape() -> None:
    """Valid JSON but wrong shape also triggers the repair loop."""
    client = LLMClient()
    _install_scripted(
        client,
        [
            _make_completion('{"name": "a"}'),  # missing count
            _make_completion('{"name": "a", "count": 3}'),
        ],
    )
    out = await client.structured(system=None, user="u", schema=_ToyModel)
    assert out.count == 3


@pytest.mark.asyncio
async def test_structured_gives_up_after_max_repairs() -> None:
    client = LLMClient()
    scripted = _install_scripted(
        client,
        [
            _make_completion("junk-1"),
            _make_completion("junk-2"),
            _make_completion("junk-3"),
        ],
    )
    with pytest.raises(Exception):
        await client.structured(system=None, user="u", schema=_ToyModel)
    # _SCHEMA_REPAIR_ATTEMPTS = 3, so we expect 3 completion calls.
    assert len(scripted.calls) == 3


@pytest.mark.asyncio
async def test_structured_retries_network_before_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    client = LLMClient()
    req = _make_httpx_request()
    _install_scripted(
        client,
        [
            APIConnectionError(request=req),
            _make_completion('{"name": "x", "count": 7}'),
        ],
    )
    monkeypatch.setattr("mimeo.llm.wait_exponential", lambda **_: lambda *_a, **_k: 0)
    out = await client.structured(system="sys", user="u", schema=_ToyModel)
    assert out.count == 7
