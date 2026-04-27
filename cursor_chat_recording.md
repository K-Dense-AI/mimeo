# Cursor Chat Recording

## 2026-04-27

User reported a pipeline error from terminal output:

```text
Pipeline failed: Error code: 400 - {'error': {'message': "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.", 'type': 'invalid_request_error', 'param': 'max_tokens', 'code': 'unsupported_parameter'}}
```

Assistant began systematic debugging by tracing the failing command and inspecting the LLM provider wrapper.

User reproduced the issue. Runtime debug log confirmed direct OpenAI calls for `gpt-5.5` were sending `max_tokens`:

- Calls with `max_tokens: null` failed with `invalid_type`.
- The authoring call with `max_tokens: 16000` failed with `unsupported_parameter` and instructed using `max_completion_tokens`.

Assistant applied a targeted LLM parameter-mapping fix: omit token limit parameters when no limit is provided, and send `max_completion_tokens` for direct OpenAI when a limit is provided.

Focused verification: `uv run pytest tests/test_llm.py` passed with 22 tests.

User reproduced again. Runtime debug log showed the token fix worked (`max_tokens` absent and authoring used `max_completion_tokens`), then exposed a new `gpt-5.5` API constraint: custom `temperature` values `0.2` and `0.4` are rejected because only the default temperature is supported.

Assistant applied a targeted temperature compatibility fix for direct OpenAI `gpt-5*` models: omit `temperature` so the API default is used.

Focused verification: `uv run pytest tests/test_llm.py` passed with 24 tests.
