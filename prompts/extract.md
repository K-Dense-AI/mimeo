# Distill a single source

You are building a knowledge base about **{expert}**{expert_context} by
reading one primary source at a time and extracting their thought process.
Your goal is not to summarize the article — it's to capture what {expert}
actually *believes*, *recommends*, and *warns against*, grounded in their
own words.

If this source turns out to be about a different person who happens to
share the name — wrong profession, wrong field, wrong era — return a
near-empty extraction rather than inventing content. Better to lose a
source than to contaminate the knowledge base with the wrong person.

## What to pull out

- **principles**: beliefs, rules, or assertions {expert} endorses. Phrase the
  statement in their voice if you can. Include a short rationale and, when
  possible, a verbatim quote that supports it.
- **frameworks**: named, repeatable procedures or decision processes they use
  (e.g. "specific knowledge", "10x thinking", "first principles"). Capture the
  steps and when to apply it.
- **mental_models**: lenses, metaphors, or analogies they reach for to reason
  about problems. Describe the model and, if the source shows one, give an
  example of them applying it.
- **heuristics**: pithy rules of thumb or one-liners that guide day-to-day
  decisions.
- **signature_quotes**: 3-8 quotes that feel distinctively *theirs* — the kind
  someone would attribute to this expert if they heard them in the wild.
- **anti_patterns**: things {expert} explicitly warns against or says most
  people get wrong, plus why they think so.

## Rules

- Only extract things **the expert themselves** said or wrote in this source.
  If the source is a third-party write-up, still attribute only what it
  reports *as their view*. Skip the author's own opinions.
- Every extracted item must carry ``source_id`` = ``{source_id}``.
- Prefer precision over volume. Better to return 3 strong principles with
  quotes than 12 vague platitudes.
- If the source is thin (short, off-topic, or mostly someone else's ideas),
  return a near-empty extraction — not fabricated content.
- Quotes must be verbatim from the source text. If you can't find a clean
  quote, set ``source_quote`` to null rather than paraphrasing.

## Source metadata

- id: ``{source_id}``
- title: {title}
- url: {url}
- kind: {kind}

## Source content

```
{content}
```

Return a JSON object matching the ``Extraction`` schema. ``source_id`` must be
``{source_id}`` on every nested item.
