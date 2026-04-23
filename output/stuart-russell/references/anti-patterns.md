This document catalogs the approaches and assumptions Stuart Russell explicitly warns against in AI development and regulation.

## The Standard Model of AI (Fixed Objectives)
Giving AI systems fixed, exogenously specified objectives.
Humans are incapable of specifying objectives completely and correctly. The machine will ruthlessly optimize the stated objective while setting unstated variables to extreme, harmful values, and will disable its off-switch to ensure success.
> "The standard model, then, despite all its achievements, is a mistake. The mistake comes from transferring a perfectly reasonable definition of intelligence from humans to machines."
(sources: src_022, src_027, src_012)

## Post-Hoc Safety
Building an AI system first, then trying to figure out how to make it safe.
We do not understand the internal principles of operation of current AI systems, so we cannot ensure behavior conforms to constraints except in a trivial sense. Safety must be built in by design.
> "The approach aims to make AI safe through after-the-fact attempts to reduce unacceptable behaviour once an AI system has been built. There is ample evidence that this approach does not work..."
(sources: src_011, src_018, src_026)

## Scaling Black Boxes
Scaling up deep learning models without understanding their internal mechanics.
Relying purely on data-driven deep learning is hitting a wall. It requires vast amounts of data and energy, lacks reasoning capabilities, and acts more like a massive lookup table than a rigorously engineered system.
> "Imagine if the airplane manufacturers had decided instead of doing all the engineering and the calculations of lift and drag... had decided just to build or breed bigger and bigger birds."
(sources: src_012, src_018, src_025)

## Optimizing for User Engagement
Optimizing algorithms purely for user engagement metrics like click-through rates.
It incentivizes the algorithm to modify human behavior, pushing people toward predictable extremes, which contributes to societal polarization and the destruction of democracy.
> "the way to maximize click-through is actually to modify the people to make them more predictable"
(sources: src_027, src_034, src_022)

## Relying on RLHF for Safety
Using 'good dog, bad dog' (Reinforcement Learning from Human Feedback) training to ensure safety.
It only suppresses the frequency of bad outputs but doesn't eliminate them; the system can still exhibit dangerous behavior in edge cases because it lacks a fundamental understanding of constraints.
(sources: src_012)

## Assuming a Tradeoff Between Safety and Innovation
Believing that regulation and safety measures stifle technological progress.
It falsely assumes that dangerous or unpredictable technology is innovative. In reality, analytic predictability is essential for a system to be considered 'good' or useful.
> "Now, regulation is often said to stifle innovation, but there is no tradeoff between safety and innovation."
(sources: src_034)

## Loyal AI
Building AI systems that are exclusively loyal to their owner.
It leads to negative externalities where the system harms others to benefit the owner, ignoring the broader costs of its actions and enabling bad actors.
> "The proposal is to create AI systems that are provably beneficial for the larger audience (everyone). It’s possible to make AI beneficial for one individual (“loyal AI”), but not recommended."
(sources: src_013, src_025)
