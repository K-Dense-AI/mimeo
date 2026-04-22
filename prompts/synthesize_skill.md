# Author the Agent Skill

You have a clustered corpus of **{expert}**'s thought, drawn from their
essays, talks, interviews, and podcast appearances. Your job is to turn it
into a production-quality Agent Skill that a coding agent can actually use to
*reason in their style*.

The skill should help an AI assistant give **advice**, **decisions**, and
**critiques** the way {expert} would — not impersonate them or speak in their
voice, but apply their principles, frameworks, and mental models when the
user is in a situation where those apply.

## Output shape

Return JSON matching the ``SkillOutput`` schema with these fields:

- ``skill_name``: a short identifier like ``naval-ravikant`` (lowercase,
  hyphen-separated, ascii only). Use a slug of the expert's name.
- ``description``: the frontmatter description. This is the MOST important
  field because it controls when the skill triggers. Write it in the style
  of skill-creator: lead with what the skill does, then list specific
  situations/keywords where it should trigger. Be a little "pushy" — mention
  that Claude should use this skill whenever it encounters the expert's
  domain topics, even if the user doesn't name the expert. Aim for ~60-120
  words.
- ``skill_body``: the markdown body that goes *after* the frontmatter. See
  structure below.
- ``principles_md``: a markdown file for ``references/principles.md``.
- ``frameworks_md``: a markdown file for ``references/frameworks.md``.
- ``mental_models_md``: a markdown file for ``references/mental-models.md``.
- ``quotes_md``: a markdown file for ``references/quotes.md``.

## ``skill_body`` structure

Target: under 400 lines. Rough template:

```
# Thinking like {expert}

{2-3 paragraph overview: who this person is and the signature shape of their
thinking. End with "Reach for this skill whenever you're..."}

## Core principles

{3-5 bullets, each one sentence, naming the principle. Each principle should
pull double duty as both a belief and a decision rule.}

For detailed rationale and quotes, see ``references/principles.md``.

## How {expert} reasons

{1-2 paragraphs describing their reasoning shape: what questions they ask
first, what they emphasize, what they dismiss. Name the top 2-3 mental models
inline and point to ``references/mental-models.md`` for the rest.}

## Applying the frameworks

{For each of the top 2-3 frameworks, a short named block with a one-sentence
when-to-use and the steps. Point to ``references/frameworks.md`` for the
full catalog.}

## Anti-patterns they push against

{3-6 bullets. Short, direct warnings in the expert's spirit.}

## How to use this skill in conversation

{Concrete guidance to the AI: when the user is facing one of these
situations, surface the relevant principle or framework by name, apply it
to their context, and cite where the idea comes from (e.g. "{expert} calls
this X"). Avoid impersonation — don't pretend to be them; channel the
thinking.}
```

## Style rules

- Explain the *why* behind each rule; don't stack musty ALL-CAPS MUSTs.
- Reference files from the body with ``references/<file>.md`` paths. The body
  must fit under ~400 lines; push depth into the reference files.
- Quotes you include in the body must be verbatim and attributed with the
  source title. Longer quote lists live in ``quotes.md``.
- The description in the frontmatter must trigger on specific concrete
  situations (e.g. for a startup thinker: "career trade-offs, leverage,
  pricing, hiring, product-market fit"). Derive these from the themes.

## ``references/*.md`` structure

Each reference file should be self-contained and start with a short intro
paragraph. Then use H2 sections per concept with:

- the canonical statement
- a short rationale
- a representative quote (if present) in blockquote form
- the source ids it came from, formatted like ``(sources: src_001, src_014)``

``quotes.md`` is simply a list of the strongest signature quotes as
blockquotes, each with the source id after them.

## Source bibliography

A separate ``references/sources.md`` file is generated automatically from the
actual URL list, so you do NOT need to produce it. Focus on the four
reference files above.

## Input data

Expert name: {expert}{expert_context}

When a qualifier is provided above, weave it naturally into the
`description` frontmatter so the skill triggers on the right person
(e.g. "Naval Ravikant, co-founder of AngelList and essayist"). Do not
repeat the qualifier inside the body; one mention in the description is
enough.

Clustered corpus (JSON):

```json
{corpus_json}
```
