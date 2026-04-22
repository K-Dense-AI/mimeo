# mimeo

> *mim·e·o* — to reproduce, to copy, to imitate.

**Clone an expert's way of thinking into your coding agent.**

Every field has people who've spent decades publicly working out how to think about it — Feynman on physics and first-principles reasoning, Darwin on observation and slow hypothesis-building, Marie Curie on experimental rigor, Turing on computation and formal proof, E. O. Wilson on synthesis across disciplines. Their lectures, papers, letters, and interviews contain genuinely useful mental models, but they're scattered across thousands of pages and hundreds of hours of content no one has time to absorb, let alone apply consistently.

Meanwhile, coding agents are hungry for exactly this kind of guidance. A well-crafted `SKILL.md` or `AGENTS.md` is a lever: it reshapes how an agent reasons, what trade-offs it weighs, and which patterns it reaches for by default. The problem is that writing one by hand — reading everything, synthesizing frameworks, surfacing the non-obvious moves — is itself a multi-week project.

**mimeo automates that project.** Point it at a name and it goes off and reads the internet on your behalf: surfaces the canonical sources, pulls full transcripts and articles, distills each one with a frontier model, clusters the recurring ideas across dozens of sources, and emits a production-ready artifact your agent can load.

The output comes in two flavors:

- an **Agent Skill** — a `SKILL.md` with YAML frontmatter plus a `references/` folder following the [skill-creator](https://github.com/anthropics/skills) anatomy (good for libraries of on-demand skills triggered by description matching), or
- an **`AGENTS.md`** — a single always-on markdown file read at the start of every agent session in a directory (good for installing an expert's defaults into the agent's everyday behavior).

Pick one with `--format skill` (default), `--format agents`, or `--format both`.

The pipeline:

0. **Disambiguates** the name with one Parallel Search + one LLM classification call, so "John Smith" doesn't silently blend an economist, a basketball coach, and a novelist into one Frankenstein skill.
1. **Discovers** sources using the [Parallel](https://parallel.ai) Search API across eight intent buckets (essays, talks/lectures, interviews, podcasts, frameworks, books, papers, letters) so both modern operators *and* historical scientists — whose legacy lives in journals and archival correspondence — are well-covered.
2. **Fetches** full content — Parallel excerpts/extract for web pages, `youtube-transcript-api` for YouTube captions, and optional local Whisper transcription for podcasts.
3. **Distills** each source with Claude Opus 4.7 via [OpenRouter](https://openrouter.ai) into a structured extraction (principles, frameworks, mental models, quotes, anti-patterns).
4. **Synthesizes** everything into a single coherent skill — clustering duplicates, ranking by cross-source frequency, and emitting a skill directory.

## Setup

```bash
# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .

# For podcast audio transcription (optional, slower, heavier)
uv sync --extra full
```

Copy `.env.example` to `.env` and fill in:

```env
OPENROUTER_API_KEY=sk-or-...
PARALLEL_API_KEY=...
```

## Usage

```bash
uv run mimeo "Naval Ravikant"
```

Flags:

| Flag | Default | Description |
|------|---------|-------------|
| `--format {skill,agents,both}` / `-f` | `skill` | `skill`: SKILL.md + references/. `agents`: single AGENTS.md. `both`: emit both. |
| `--mode {text,captions,full}` | `captions` | `text`: web only. `captions`: web + YouTube captions. `full`: web + captions + audio transcription. |
| `--max-sources N` | `25` | Cap on distinct sources after dedup + ranking. |
| `--deep-research` | off | Additionally run a Parallel Task API deep-research run and inject its report as a pseudo-source. |
| `--disambiguator TEXT` / `-d` | auto | Short qualifier that pins a common name to the right person (e.g. `"co-founder of AngelList, investor"`). When set, skips the automatic disambiguation pre-flight. |
| `--assume-unambiguous` | off | Skip the disambiguation pre-flight entirely. Useful in non-interactive scripts where you're confident the name is unique. |
| `--model SLUG` | `google/gemini-3.1-pro-preview` | Any OpenRouter model slug. |
| `--output-dir PATH` | `./output` | Where the generated skill lands. |
| `--refresh` | off | Ignore cached intermediates in `_workspace/` and re-run everything. |
| `--concurrency N` | `5` | Concurrent per-source distillation calls. |

### Ambiguous names

When a name could refer to multiple notable people, mimeo surfaces the ambiguity before burning API budget on discovery:

```bash
# Interactive: prompts you to pick from the candidates
uv run mimeo "John Smith"

# Scripted: pin the right person up front
uv run mimeo "John Smith" -d "head basketball coach, Michigan State"

# Unambiguous name + non-interactive CI run: skip the check entirely
uv run mimeo "Naval Ravikant" --assume-unambiguous
```

If the check fires in a non-TTY environment without a `--disambiguator`, mimeo exits with a list of candidates and the exact flag to pass. The resolution is cached under `_workspace/identity.<model>.json`, so repeat runs don't re-pay for it; use `--refresh` to invalidate.

Example producing a richer skill:

```bash
uv run mimeo "Jensen Huang" \
  --mode full \
  --max-sources 40 \
  --deep-research
```

## Output layout

With `--format skill` (default):

```
output/naval-ravikant/
├── SKILL.md
├── references/
│   ├── principles.md
│   ├── frameworks.md
│   ├── mental-models.md
│   ├── quotes.md
│   └── sources.md
└── _workspace/         # cached intermediates (identity, discovery, raw, distilled)
```

With `--format agents`:

```
output/naval-ravikant/
├── AGENTS.md           # self-contained, always-on (no frontmatter)
└── _workspace/
```

With `--format both` you get both `SKILL.md` + `references/` **and** `AGENTS.md` in the same directory; they share the cached discovery / fetch / distill / cluster stages, so the second one is cheap.

## Architecture

See [the plan](.cursor/plans/) or the source under [`src/mimeo/`](src/mimeo/). Roughly:

```
cli -> pipeline -> identity  (Parallel search + LLM: ambiguous? which person?)
                -> discovery (Parallel search, 8 buckets)
                -> fetch     (web / youtube / audio)
                -> distill   (per-source Opus extraction)
                -> research? (Parallel deep research pseudo-source)
                -> cluster   (merge + rank cross-source)
                -> author    (skill | agents | both) + writers
```

## Tests

```bash
# Offline tests (no API calls, always safe)
uv run pytest --ignore=tests/test_live.py

# Live smoke tests (hit Parallel + OpenRouter + YouTube - requires .env)
MIMEO_LIVE=1 uv run pytest tests/test_live.py
```

## License

MIT.
