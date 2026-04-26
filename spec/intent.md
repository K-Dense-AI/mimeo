# Provider Refactor Intent

mimeo currently assumes OpenRouter for all text LLM calls and Parallel for web search, extract, and deep research. Users should be able to choose direct API providers for text LLM calls while preserving the existing OpenRouter + Parallel default behavior.

The first version will support OpenRouter, OpenAI, Anthropic, xAI, and Google for text LLM calls. Search will become provider-shaped but Parallel remains the only fully implemented search/extract/deep-research provider. Avatar generation remains optional and becomes a separate image-provider concern so direct text LLM providers are not forced to support image generation.

Primary goals:

- Preserve the existing default CLI behavior and environment variables.
- Add explicit provider settings for LLM, search, and image generation.
- Keep `LLMClient.complete()` and `LLMClient.structured()` as the stable app-facing API.
- Keep the local Pydantic validation and repair loop for structured output across all LLM providers.
- Make missing credentials and missing provider-specific models actionable.
- Scope caches by provider and model where needed to avoid cross-provider reuse.
- Document the new configuration and add offline tests that do not hit provider APIs.

