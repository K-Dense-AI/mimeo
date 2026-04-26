# Provider Refactor Tasks

- [x] Task 1: Add SDD and steering docs. Traceability: `REQ-001` through `REQ-018`.
- [x] Task 2: Extend runtime settings, provider literals, credential helpers, model resolution, and cache scoping. Traceability: `REQ-001`, `REQ-003`, `REQ-004`, `REQ-005`, `REQ-006`, `REQ-010`, `REQ-011`.
- [x] Task 3: Refactor `LLMClient` to support OpenRouter, OpenAI, Anthropic, xAI, and Google behind the existing app-facing API. Traceability: `REQ-004`, `REQ-007`, `REQ-008`, `REQ-009`.
- [x] Task 4: Introduce search provider protocol and normalized result objects, then adapt Parallel. Traceability: `REQ-002`, `REQ-012`, `REQ-013`, `REQ-014`.
- [x] Task 5: Introduce image provider protocol and optional OpenRouter avatar provider. Traceability: `REQ-015`, `REQ-016`.
- [x] Task 6: Wire provider settings through CLI and pipeline. Traceability: `REQ-003`, `REQ-014`, `REQ-016`.
- [x] Task 7: Update README, `.env.example`, dependencies, and live/offline tests. Traceability: `REQ-017`, `REQ-018`.

## GitHub Issue Templates

Each checked task can be copied into a GitHub issue with:

- Requirement IDs from the task line.
- Acceptance criteria from `spec/requirements.md`.
- Owned files matching the subsystem.
- Test command: `uv run pytest`.
- Conflict note: tasks 2, 3, and 6 all touch provider wiring and should merge before docs-only changes.

