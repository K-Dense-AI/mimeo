This document catalogs the approaches and assumptions that Ilya Sutskever explicitly pushes against in AI development.

## Blind Compute Scaling
Believing that simply scaling up the current recipe by 100x will automatically transform AI capabilities.
**Why it fails:** Pre-training data is finite, and current models suffer from fundamental generalization issues that raw compute scaling alone cannot fix without new research ideas.
(sources: src_000, src_035)

## AGI as an Omniscient Mind
Defining AGI as a finished system that inherently knows how to do every job uniformly out of the box.
**Why it fails:** It overshoots the target and ignores how intelligence actually works. Even humans rely heavily on continual learning and trial-and-error to acquire specific knowledge.
(sources: src_000, src_035)

## Dismissing Next-Word Prediction as Mere Statistics
Assuming that language models only learn statistical regularities and therefore possess no understanding of the real world.
**Why it fails:** It ignores that to perfectly predict the next word, the model must actually learn the underlying process and world model that generated the text.
(sources: src_015, src_020)

## Trusting Data Over Belief
Trusting the data and experiments all the time without a top-down aesthetic belief.
**Why it fails:** If you only trust the data, a simple bug in your code might convince you to abandon a correct and fundamental research direction because you don't know the bug is there.
(sources: src_035)

## Hardcoding Complex Rules
Hardcoding rules and assumptions into models for complex environments.
**Why it fails:** The problem space of the real world is too vast. Humans are not smart enough to anticipate and hardcode all the necessary rules for truly difficult problems; it is better to let the model learn from data.
(sources: src_019)

## Releasing Commercial Products Before Achieving Safe Superintelligence
Releasing revenue-generating products before achieving safe superintelligence.
**Why it fails:** It creates competing incentives that erode safety and trust in alignment protocols, distracting from the primary goal of safely developing superintelligence.
(sources: src_018)

## Hacking RL Evals
Designing RL environments specifically to pass public evals rather than to achieve true generalization.
**Why it fails:** It creates models that are single-minded and narrowly focused on benchmarks. They perform incredibly well on tests but fail at basic, real-world tasks because they lack true generalization.
(sources: src_000, src_035)

## Expecting Predictable Reasoning
Expecting reasoning AI to be as predictable as current deep learning models.
**Why it fails:** Current models replicate human intuition (gut feel), which is predictable. Reasoning inherently introduces unpredictability, as the system will draw conclusions or make moves that humans cannot foresee.
(sources: src_012)
