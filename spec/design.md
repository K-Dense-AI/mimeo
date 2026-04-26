# Provider Refactor Design

## Architecture

Add provider selection to `Settings` and route client creation through small factories:

- `llm_provider`: `openrouter`, `openai`, `anthropic`, `xai`, or `google`.
- `search_provider`: `parallel` for v1.
- `image_provider`: `openrouter` or `none`.

`LLMClient` remains the single app-facing client. It owns provider-specific request translation but preserves `complete()` and `structured()`. OpenRouter, OpenAI, and xAI use the OpenAI Python SDK with different base URLs and credentials. Anthropic uses the native `anthropic` SDK. Google uses `google-genai`.

Search gains repo-owned normalized result types plus a `SearchProvider` protocol. `ParallelClient` becomes the Parallel adapter and returns normalized search/extract objects, while preserving attribute names used by the pipeline.

Avatar generation gains an `ImageProvider` protocol. The OpenRouter image implementation remains available and `none` becomes an explicit no-op provider. When a direct text LLM provider is selected and no OpenRouter key is available for images, avatar generation returns `None` and the pipeline continues.

## Configuration

`Settings.__post_init__` resolves and validates provider settings at construction time. For OpenRouter, the default model remains `google/gemini-3.1-pro-preview` unless `MIMEO_MODEL`, `MIMEO_OPENROUTER_MODEL`, or `--model` overrides it. For other providers, a model must be supplied by `--model`, `MIMEO_MODEL`, or `MIMEO_<PROVIDER>_MODEL`.

Credential helpers map providers to environment variables:

- OpenRouter: `OPENROUTER_API_KEY`
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- xAI: `XAI_API_KEY`
- Google: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- Parallel: `PARALLEL_API_KEY`

## Error Handling

Missing provider models raise a configuration error before network work starts. Missing API keys raise credential errors naming the required env var. Avatar failures remain best-effort and do not fail the main pipeline.

LLM network retries preserve the current OpenAI-compatible transient retry behavior. Structured-output schema repair remains provider-independent and runs after provider text generation returns.

## Compatibility

Default CLI behavior remains equivalent to the pre-refactor implementation. Existing OpenRouter cache filenames continue to use the model-only hash. New provider cache filenames use a hash of `provider:model` to prevent reuse across providers.

