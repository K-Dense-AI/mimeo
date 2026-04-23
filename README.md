# mimeo

> *mim·e·o* — to reproduce, to copy, to imitate.

**Clone an expert's way of thinking into your coding agent.**

![mimeo pipeline](docs/mimeo-explainer.png)

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
3. **Distills** each source with a frontier model via [OpenRouter](https://openrouter.ai) (default: Google Gemini 3.1 Pro Preview; override with `--model` or `MIMEO_MODEL`) into a structured extraction (principles, frameworks, mental models, quotes, heuristics, anti-patterns). Long sources (books, conference transcripts, PDFs) are chunked on paragraph boundaries, distilled in parallel, and merged so nothing gets silently dropped to a truncation.
4. **Clusters** across sources — merging duplicates, ranking by cross-source frequency. Long corpora are batched under a prompt-size budget and stitched back together in memory, so `--max-sources 40` on a prolific writer still fits.
5. **Verifies** every clustered quote against the source text we already fetched. Quotes that don't appear (allowing typographic normalization) are stripped from the corpus and surfaced in a human-readable `_workspace/quote_verification.md` audit trail. Disable with `--no-verify-quotes`.
6. **Authors** the skill + optional `AGENTS.md`, emitting `heuristics.md` and `anti-patterns.md` reference files alongside the existing principles / frameworks / mental-models / quotes / sources bundle.
7. **Critiques** the authored artifact with one more adversarial-editor LLM pass, writing a 0-10 score and a categorized issue list to `_workspace/critique_skill.md` (and `critique_agents.md` when relevant). The report is informational — mimeo doesn't auto-rewrite based on it — but gives you an honest second opinion before you ship. Disable with `--no-critique`.
8. **Illustrates** the expert with a painterly head-and-shoulders portrait via an OpenRouter image model (default: `openai/gpt-5.4-image-2`), saved as `avatar.png` alongside the other outputs. The step is best-effort — image-endpoint failures are logged and swallowed so they never fail the main run. Disable with `--no-avatar` or swap models with `--avatar-model`.

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
| `--verify-quotes` / `--no-verify-quotes` | on | Check every clustered quote against its source text before authoring; strip ones that don't match. |
| `--critique` / `--no-critique` | on | Adversarial-editor review of the authored skill, written to `_workspace/critique_*.md`. |
| `--avatar` / `--no-avatar` | on | Generate a painterly portrait avatar for the expert via an OpenRouter image model and save it as `avatar.<ext>` alongside the other outputs. |
| `--avatar-model SLUG` | `openai/gpt-5.4-image-2` | OpenRouter image-capable model slug used for the avatar. |

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
│   ├── heuristics.md
│   ├── anti-patterns.md
│   ├── quotes.md
│   └── sources.md
├── avatar.png          # omit with --no-avatar
└── _workspace/         # cached intermediates (identity, discovery, raw, distilled)
                        # + quote_verification.{json,md} and critique_skill.{json,md}
```

With `--format agents`:

```
output/naval-ravikant/
├── AGENTS.md           # self-contained, always-on (no frontmatter)
├── avatar.png          # omit with --no-avatar
└── _workspace/
```

With `--format both` you get both `SKILL.md` + `references/` **and** `AGENTS.md` in the same directory; they share the cached discovery / fetch / distill / cluster stages (and a single avatar), so the second format is cheap.

## Architecture

See [the plan](.cursor/plans/) or the source under [`src/mimeo/`](src/mimeo/). Roughly:

```
cli -> pipeline -> identity   (Parallel search + LLM: ambiguous? which person?)
                -> discovery  (Parallel search, 8 buckets)
                -> fetch      (web / youtube / audio)
                -> distill    (per-source extraction, chunk-and-merge on long sources)
                -> research?  (Parallel deep research pseudo-source)
                -> cluster    (merge + rank cross-source, batched when corpus is large)
                -> verify?    (fuzzy-match every quote against its source text)
                -> author     (skill | agents | both) + writers
                -> critique?  (adversarial-editor review → _workspace/critique_*.md)
                -> avatar?    (OpenRouter image model → avatar.png)
```

## Star History

<a href="https://www.star-history.com/?repos=K-Dense-AI%2Fmimeo">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=K-Dense-AI/mimeo&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=K-Dense-AI/mimeo&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=K-Dense-AI/mimeo&type=date&legend=top-left" />
 </picture>
</a>

