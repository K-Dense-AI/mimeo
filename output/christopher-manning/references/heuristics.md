# Heuristics and Rules of Thumb

These are Christopher Manning's pithy rules of thumb for navigating AI research, evaluating models, and building systems.

## Avoid the Kaggle Game
Focus on fundamental problems, architectures, and cognitive science rather than just chasing state-of-the-art numbers on benchmark tasks. Over-focusing on incremental benchmark improvements distracts the field from solving actual domain problems.
> "Recently at ACL conferences, there has been an over-focus on numbers, on beating the state of the art. Call it playing the Kaggle game."
*(sources: src_044)*

## Build from Scratch
Reimplementing models yourself from scratch is the best way to deeply understand AI, even if you are just replicating existing frameworks. You learn significantly more by building the underlying mechanics than by merely using off-the-shelf packages.
> "just by building things for yourself from scratch even if they um replicate something that someone has done or a big framework from a tech company you just learn so much"
*(sources: src_024)*

## The Landmine Test
If a proposed definition of artificial intelligence also accurately describes a landmine, it is a flawed definition. Definitions that merely require a machine to 'infer from input to generate outputs that influence environments' are too broad and mechanistic.
*(sources: src_013)*

## The Worst Technology
The AI technology you use today is the worst technology you will ever deal with in the future; it will only improve. A reminder to project current capabilities forward rather than judging the ultimate potential of AI solely by its present limitations.
> "The technology we're going to see for the rest of these two days is the worst technology that we're ever going to deal with in the future. It's going to keep on getting better from here."
*(sources: src_023)*

## Don't bet against LLMs
It's a mistake to bet against large language models; despite their flaws, we consistently find ways to do more with them. Dismissing them ignores the huge order-of-magnitude productivity gains they offer.
*(sources: src_023)*

## Small Models for Web Latency
To solve latency in web agents, use smaller models (like 8B parameters) that can eventually run on-device rather than round-tripping to a server.
*(sources: src_011)*
