"""Provider-routed LLM client with a structured-output helper.

OpenRouter remains the default, while OpenAI, Anthropic, xAI, and Google can
be selected explicitly. Structured output always validates locally against a
Pydantic model; providers with stable JSON/schema response controls use them
as an additional hint.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, TypeVar

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)
from pydantic import BaseModel, ValidationError
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from .config import (
    DEFAULT_LLM_PROVIDER,
    LLMProvider,
    OPENROUTER_BASE_URL,
    PROMPTS_DIR,
    XAI_BASE_URL,
    openrouter_default_headers,
    require_llm_key,
    resolve_llm_model,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
_DEBUG_LOG_PATH = Path("/Users/antoniomele/Dropbox/github/mimeo/.cursor/debug-96396b.log")
_DEBUG_SESSION_ID = "96396b"


def _agent_debug_log(
    *,
    run_id: str,
    hypothesis_id: str,
    location: str,
    message: str,
    data: dict[str, Any],
) -> None:
    # region agent log
    timestamp = int(time.time() * 1000)
    payload = {
        "sessionId": _DEBUG_SESSION_ID,
        "id": f"log_{timestamp}",
        "timestamp": timestamp,
        "location": location,
        "message": message,
        "data": data,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
    }
    try:
        _DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _DEBUG_LOG_PATH.open("a", encoding="utf-8") as debug_file:
            debug_file.write(json.dumps(payload, default=str) + "\n")
    except OSError:
        pass
    # endregion


class LLMClient:
    """Provider-routed LLM client with a stable app-facing API."""

    def __init__(
        self,
        model: str | None = None,
        *,
        provider: LLMProvider = DEFAULT_LLM_PROVIDER,
        client: Any | None = None,
    ) -> None:
        self.provider = provider
        self.model = resolve_llm_model(provider, model)
        self._client = client if client is not None else self._build_client(provider)

    async def complete(
        self,
        *,
        system: str | None,
        user: str,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> str:
        """Plain text completion."""
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        return await self._complete_messages(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            json_schema=None,
        )

    async def structured(
        self,
        *,
        system: str | None,
        user: str,
        schema: type[T],
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> T:
        """Request JSON that validates against ``schema``.

        We give the model the schema inline (so it knows the shape), apply
        provider JSON/schema controls where supported, and validate locally.
        If the response fails validation we retry up to
        :data:`_SCHEMA_REPAIR_ATTEMPTS` times, each retry sending the model
        its previous reply plus the error so it can self-correct.
        """
        schema_hint = _format_schema_hint(schema)
        augmented_user = (
            f"{user}\n\n"
            f"Return ONLY a JSON object matching this Pydantic schema:\n"
            f"{schema_hint}\n\n"
            f"Do not include any commentary, code fences, or prose - JSON only."
        )

        base_messages: list[dict[str, str]] = []
        if system:
            base_messages.append({"role": "system", "content": system})
        base_messages.append({"role": "user", "content": augmented_user})

        last_raw: str | None = None
        last_error: str | None = None

        for repair_attempt in range(_SCHEMA_REPAIR_ATTEMPTS):
            messages = list(base_messages)
            if last_raw is not None and last_error is not None:
                messages.append({"role": "assistant", "content": last_raw})
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            "Your previous response failed schema validation:\n"
                            f"{last_error}\n"
                            "Return corrected JSON matching the schema exactly, "
                            "with no commentary or code fences."
                        ),
                    }
                )

            # Inner retry handles transient network/5xx errors.
            raw = await self._complete_messages(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                json_schema=schema,
            )

            try:
                data = json.loads(_strip_code_fence(raw))
                return schema.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_raw = raw
                last_error = str(exc)[:1500]
                remaining = _SCHEMA_REPAIR_ATTEMPTS - repair_attempt - 1
                logger.warning(
                    "Schema validation failed (%d repair attempts left): %s",
                    remaining,
                    exc,
                )
                if remaining == 0:
                    raise

        raise RuntimeError("unreachable")  # pragma: no cover - loop always returns or raises

    def _build_client(self, provider: LLMProvider) -> Any:
        if provider == "openrouter":
            return AsyncOpenAI(
                api_key=require_llm_key(provider),
                base_url=OPENROUTER_BASE_URL,
                default_headers=openrouter_default_headers() or None,
            )
        if provider == "openai":
            return AsyncOpenAI(api_key=require_llm_key(provider))
        if provider == "xai":
            return AsyncOpenAI(
                api_key=require_llm_key(provider),
                base_url=XAI_BASE_URL,
            )
        if provider == "anthropic":
            try:
                from anthropic import AsyncAnthropic
            except ImportError as exc:  # pragma: no cover - dependency installed in normal env
                raise RuntimeError(
                    "The anthropic package is required for --llm-provider anthropic."
                ) from exc

            return AsyncAnthropic(api_key=require_llm_key(provider))
        if provider == "google":
            try:
                from google import genai
            except ImportError as exc:  # pragma: no cover - dependency installed in normal env
                raise RuntimeError(
                    "The google-genai package is required for --llm-provider google."
                ) from exc

            return genai.Client(api_key=require_llm_key(provider))
        raise ValueError(f"Unsupported LLM provider: {provider}")

    async def _complete_messages(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None,
        json_schema: type[BaseModel] | None,
    ) -> str:
        async for attempt in _network_retryer():
            with attempt:
                if self.provider in ("openrouter", "openai", "xai"):
                    return await self._complete_openai_compatible(
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        json_mode=json_schema is not None
                        and self.provider in ("openrouter", "openai"),
                    )
                if self.provider == "anthropic":
                    return await self._complete_anthropic(
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                if self.provider == "google":
                    return await self._complete_google(
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        json_schema=json_schema,
                    )
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        raise RuntimeError("unreachable")  # pragma: no cover - tenacity reraises

    async def _complete_openai_compatible(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None,
        json_mode: bool,
    ) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if not _requires_default_temperature(self.provider, self.model):
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            if self.provider == "openai":
                kwargs["max_completion_tokens"] = max_tokens
            else:
                kwargs["max_tokens"] = max_tokens
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        # region agent log
        _agent_debug_log(
            run_id="pre-fix",
            hypothesis_id="H1,H2,H3,H4",
            location="src/mimeo/llm.py:_complete_openai_compatible:before_create",
            message="About to call OpenAI-compatible chat completion",
            data={
                "provider": self.provider,
                "model": self.model,
                "max_tokens": max_tokens,
                "json_mode": json_mode,
                "kwargs_keys": sorted(kwargs),
            },
        )
        # endregion
        try:
            resp = await self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            # region agent log
            _agent_debug_log(
                run_id="pre-fix",
                hypothesis_id="H1,H2,H3,H4",
                location="src/mimeo/llm.py:_complete_openai_compatible:error",
                message="OpenAI-compatible chat completion raised",
                data={
                    "provider": self.provider,
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "json_mode": json_mode,
                    "exception_type": type(exc).__name__,
                    "status_code": getattr(exc, "status_code", None),
                    "body": getattr(exc, "body", None),
                },
            )
            # endregion
            raise
        return (resp.choices[0].message.content or "").strip()

    async def _complete_anthropic(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        api_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] != "system"
        ]
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
            "max_tokens": max_tokens or _DEFAULT_NATIVE_MAX_TOKENS,
            "temperature": temperature,
        }
        if system:
            kwargs["system"] = system
        response = await self._client.messages.create(**kwargs)
        return _extract_anthropic_text(response)

    async def _complete_google(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int | None,
        json_schema: type[BaseModel] | None,
    ) -> str:
        prompt = _flatten_messages_for_prompt(messages)
        config: dict[str, Any] = {"temperature": temperature}
        if max_tokens is not None:
            config["max_output_tokens"] = max_tokens
        if json_schema is not None:
            config["response_mime_type"] = "application/json"
            config["response_json_schema"] = json_schema.model_json_schema()

        def _call() -> Any:
            return self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

        response = await asyncio.to_thread(_call)
        return str(getattr(response, "text", "") or "").strip()


# Status codes where a retry has a reasonable chance of succeeding. 4xx
# errors like 401 (bad key) or 400 (bad request) will keep failing, so we
# surface them immediately rather than burning the budget.
_RETRYABLE_STATUS_CODES = frozenset({408, 409, 425, 429, 500, 502, 503, 504})

# How many times we'll ask the model to repair a response that parsed but
# didn't match the schema. Network-level retries are separate and happen
# inside each attempt.
_SCHEMA_REPAIR_ATTEMPTS = 3
_DEFAULT_NATIVE_MAX_TOKENS = 8192


def _is_network_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (APIConnectionError, APITimeoutError, RateLimitError)):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code in _RETRYABLE_STATUS_CODES
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int):
        return status_code in _RETRYABLE_STATUS_CODES
    return False


def _network_retryer() -> AsyncRetrying:
    """Retry only on transient network / 5xx errors, not schema failures."""
    return AsyncRetrying(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        retry=retry_if_exception(_is_network_retryable),
        reraise=True,
    )


def _requires_default_temperature(provider: LLMProvider, model: str) -> bool:
    """OpenAI GPT-5 models currently reject custom temperature values."""
    return provider == "openai" and model.startswith("gpt-5")


def _strip_code_fence(text: str) -> str:
    """Some models still wrap JSON in ```json ... ``` even when told not to."""
    t = text.strip()
    if t.startswith("```"):
        # drop the opening fence (```json or ```)
        first_nl = t.find("\n")
        if first_nl != -1:
            t = t[first_nl + 1 :]
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


def _format_schema_hint(schema: type[BaseModel]) -> str:
    """Compact JSON-schema description the model can follow."""
    return json.dumps(schema.model_json_schema(), indent=2)


def _extract_anthropic_text(response: Any) -> str:
    parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        text = getattr(block, "text", None)
        if isinstance(text, str):
            parts.append(text)
        elif isinstance(block, dict) and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "".join(parts).strip()


def _flatten_messages_for_prompt(messages: list[dict[str, str]]) -> str:
    labels = {"system": "System", "user": "User", "assistant": "Assistant"}
    return "\n\n".join(
        f"{labels.get(m['role'], m['role'].title())}:\n{m['content']}"
        for m in messages
    )


def load_prompt(name: str) -> str:
    """Load a prompt template from the ``prompts/`` directory.

    ``name`` may or may not include the ``.md`` extension.
    """
    filename = name if name.endswith(".md") else f"{name}.md"
    path: Path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def render_prompt(template: str, **values: str) -> str:
    """Substitute ``{name}`` placeholders in ``template`` with ``values``.

    Unlike ``str.format``, this only touches exact ``{key}`` tokens for keys
    we pass in, so the template body can contain literal ``{...}`` skeleton
    braces (e.g. ``{2-3 paragraph overview}``) without escaping.
    """
    out = template
    for key, val in values.items():
        out = out.replace("{" + key + "}", val)
    return out
