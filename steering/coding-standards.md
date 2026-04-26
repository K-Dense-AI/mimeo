# Coding Standards

- Keep provider-specific code behind small factories and adapters.
- Preserve existing public method names unless a requirement explicitly changes them.
- Prefer repo-owned normalized data objects at integration boundaries.
- Keep external API keys in environment variables only.
- Tests must use fakes or mocked transports unless explicitly marked live and gated by `MIMEO_LIVE=1`.
- Keep defaults backward-compatible unless a requirement explicitly changes them.

