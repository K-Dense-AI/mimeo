# Cluster the corpus

You've received per-source extractions from many pieces of content by or about
**{expert}**{expert_context}. Your job is to merge them into a single,
deduplicated **ClusteredCorpus** that will drive the final skill.

If some extractions are clearly about a different person who shares this
name (wrong profession, wrong field), drop those items rather than merging
them in. Never blend two people into one composite.

## How to merge

1. **Group concepts that mean the same thing**, even if they're phrased
   differently across sources. For example "specific knowledge" and "unique
   knowledge that can't be taught" should collapse into one entry.
2. For each merged concept, write:
   - ``label``: a short canonical name for it.
   - ``summary``: a single unified description that captures the strongest
     version of the idea across sources.
   - ``details``: optional — if the concept has steps, rationale, or nuance
     worth preserving, include it here.
   - ``representative_quote``: the single best verbatim quote from the source
     extractions for this concept. Null is fine if none of the source quotes
     is strong enough.
   - ``source_ids``: the list of every source id where this concept appeared.
3. **Rank items by frequency** (how many sources mentioned the idea) within
   each category, most-mentioned first. Ties broken by which has the stronger
   representative quote.
4. **Drop** singletons that feel weak or off-topic. Keep singletons that are
   distinctive (uniquely theirs) even if they appeared only once.
5. Derive a top-level ``themes`` list: 4-8 short phrases that describe the
   domains the expert returns to across their work (e.g. "leverage",
   "long-term thinking", "compounding"). These feed the skill's trigger
   description.

## Output

Return a JSON object matching the ``ClusteredCorpus`` schema. Keep the total
number of items reasonable: aim for ~8-15 principles, ~3-8 frameworks, ~4-10
mental models, ~5-15 heuristics, ~5-12 signature quotes, ~3-8 anti-patterns.

## Expert name

{expert}{expert_context}

## Per-source extractions (JSON array)

```json
{extractions_json}
```
