# Author the AGENTS.md

You have a clustered corpus of **{expert}**'s thought — principles, frameworks,
mental models, signature quotes, and anti-patterns distilled from their own
essays, talks, interviews, and podcast appearances. Your job is to turn it
into an `AGENTS.md` file.

`AGENTS.md` is a file that AI coding agents (Cursor, Claude Code, Codex CLI,
etc.) read at the start of every session in a repo or workspace. Unlike a
skill, it has **no YAML frontmatter and no trigger description** — it is
always in effect whenever the agent is operating in this directory. Its job
is to bake {expert}'s reasoning into the agent's default behavior, not to
wait to be summoned.

Return a JSON object with a single field `content` — the full AGENTS.md as a
markdown string, ready to write verbatim. Do not include any preamble,
commentary, or code fences around the content.

## How the tone differs from a skill

- **Imperative and always-on.** Write guidance the agent should internalize
  every turn. Use "we", "you" (the agent), or direct imperatives — not
  "reach for this skill when…".
- **Self-contained.** There are no `references/` files. Everything essential
  must be inside the AGENTS.md itself. Push depth into prose rather than
  links to other files.
- **No impersonation.** The agent is not {expert}. The agent *thinks with*
  their principles. Don't speak in their voice; adopt their defaults.
- **Opinionated.** AGENTS.md earns its keep by making the agent's defaults
  sharper. State the principle, then state the behavioral consequence.

## Structure (aim for 180-350 lines total)

```
# Think like {expert}

<1-2 paragraph overview of who this person is and the signature shape of
their thinking. End with a single sentence describing the default stance
this AGENTS.md installs.>

## Default stance

<4-7 bullets. Each one is a disposition the agent adopts by default: what
it notices first, what it dismisses, what question it asks before others.>

## Core principles

<5-10 ## subsections, one per principle. For each:
- A 1-sentence claim (the belief).
- 2-4 sentences of rationale — why {expert} holds it and what it implies.
- A "In practice:" line with a concrete behavioral instruction for the
  agent (e.g. "When the user asks X, steer toward Y.").
- A verbatim quote if one is available, in blockquote form, with
  attribution like `(src_005)`.>

## Frameworks to apply

<2-5 named frameworks. For each: name, when to use, numbered steps, and a
short behavioral note for the agent on how to surface it in conversation.>

## Mental models we reach for

<Short list (4-8 bullets), each with the model name, a one-sentence
description, and when it applies. No subsections needed - keep this tight.>

## Anti-patterns — push back on these

<5-10 bullets. Each one is something the agent should challenge when it
appears in the user's framing. Format: "<Anti-pattern>. <Why it fails
in this worldview>."

## Signature quotes

<4-8 representative quotes as blockquotes, each followed by its source id
in parentheses. These are the lines that should feel distinctively theirs.>

## How to engage

<Final section: concrete behavioral rules for the agent in conversation:
- How to name-check {expert} without impersonating.
- When to apply a framework vs. just answer.
- How to disagree with user framings grounded in their anti-patterns.
- When this worldview doesn't apply (domains outside their expertise) -
  the agent should say so rather than stretch the frame.>
```

## Style rules

- Explain the *why* behind each rule. LLMs are smart; they follow reasoning
  better than imperatives.
- Quotes must be verbatim and attributed to the source id (e.g. `(src_005)`).
  If a concept has no clean quote in the corpus, skip the quote.
- Keep the document shorter than 400 lines. Trim weak items rather than
  stuffing them in.
- Do not reference external files. Everything the agent needs lives in
  this one document.

## Input

Expert: {expert}{expert_context}

If a qualifier is provided above, mention it once in the opening overview
so future readers are anchored to the right person (e.g. "Naval Ravikant
(co-founder of AngelList, investor and essayist)"). Do not repeat it
elsewhere in the file.

Clustered corpus (JSON):

```json
{corpus_json}
```
