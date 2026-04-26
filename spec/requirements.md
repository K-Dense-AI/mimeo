# Provider Refactor Requirements

## EARS Requirements

- [REQ-001] The system shall keep OpenRouter as the default LLM provider when no provider is configured.
- [REQ-002] The system shall keep Parallel as the default and only v1 search provider when no search provider is configured.
- [REQ-003] The system shall expose CLI and environment configuration for `llm_provider`, `search_provider`, and `image_provider`.
- [REQ-004] WHEN a user selects `openai`, `anthropic`, `xai`, or `google` as the LLM provider, the system shall use that provider's native model identifier and API key environment variable.
- [REQ-005] IF a non-OpenRouter LLM provider is selected without `--model`, `MIMEO_MODEL`, or `MIMEO_<PROVIDER>_MODEL`, THEN the system shall fail with an actionable configuration error.
- [REQ-006] IF a required API key is missing, THEN the system shall name the exact environment variable or variables that can satisfy the credential.
- [REQ-007] The system shall keep the existing `LLMClient.complete()` and `LLMClient.structured()` method signatures usable by pipeline callers and tests.
- [REQ-008] The system shall validate every structured LLM response with the requested Pydantic schema and retry schema repair before surfacing validation failure.
- [REQ-009] The system shall use provider-native JSON/schema response controls only where stable in v1: OpenRouter/OpenAI JSON mode and Google response JSON schema.
- [REQ-010] The system shall keep OpenRouter cache IDs based on model only for backward compatibility.
- [REQ-011] WHEN the selected LLM provider is not OpenRouter, the system shall include provider and model in LLM cache IDs.
- [REQ-012] The system shall expose a search provider interface with `search`, `extract`, and `deep_research` capabilities.
- [REQ-013] The system shall adapt Parallel search and extract responses into repo-owned normalized result objects.
- [REQ-014] The system shall keep current discovery, fetch, identity, and deep-research behavior unchanged when `search_provider=parallel`.
- [REQ-015] The system shall expose image generation as an optional provider concern independent of the text LLM provider.
- [REQ-016] IF avatar generation is enabled but no usable image provider is configured for the current run, THEN the system shall skip avatar generation without failing the pipeline.
- [REQ-017] The system shall update README, `.env.example`, and package dependencies to document provider setup.
- [REQ-018] The system shall keep live provider tests opt-in behind `MIMEO_LIVE=1`.

## Properties

- Provider selection must never silently fall back to a different text LLM provider after the user explicitly chooses one.
- Offline tests must not require real API credentials or network calls.
- Existing injected fakes in tests must continue to work or be replaced with equivalent provider-level fakes.
- No API keys may be logged, written to cache files, or added to documentation examples beyond placeholder values.

