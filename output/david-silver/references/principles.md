This document outlines David Silver's core principles for designing intelligent systems. These principles serve as both foundational beliefs about the nature of intelligence and practical decision rules for engineering AI.

## The Era of Experience Over Human Data

To achieve superhuman intelligence, AI must transition from learning via finite human data to learning continuously from its own experience.

Human data is excellent for bootstrapping, but it inherently caps a system's performance at the maximum level humans have achieved. Breaking through this ceiling requires agents to interact with environments, generating their own experience through trial and error to discover novel knowledge.

> "human data, the era of human data in itself leads to AI systems that can't in isolation go all the way to super intelligence. Why is that? Well, it's because they can't discover new knowledge."
*(sources: src_014, src_007, src_013, src_019, src_021)*

## Tabula Rasa Learning Surpasses Human Expertise

Pure reinforcement learning without human knowledge can surpass systems trained on human expert data.

Human expert data is often expensive, unreliable, or unavailable, and it imposes a ceiling on performance. Reinforcement learning from self-play allows systems to exceed human capabilities by learning from their own experience and discovering novel strategies.

> "Our results comprehensively demonstrate that a pure reinforcement learning approach is fully feasible, even in the most challenging of domains: it is possible to train to superhuman level, without human examples or guidance, given no knowledge of the domain beyond basic rules."
*(sources: src_049, src_044, src_041, src_012)*

## The Purity of Self-Learning (The Bitter Lesson)

Hardcoding human knowledge into algorithms limits their potential; throwing out human data forces the creation of infinitely scalable self-learning mechanisms.

When we build human heuristics into systems, we fit the algorithm to human biases rather than optimizing its ability to learn. Removing human influence and relying purely on rules and reinforcement learning allows AI to discover novel, superior approaches.

> "If you throw out the human data, you actually spend more effort on how the system can learn for itself. And that's the part which can then learn and learn and learn forever."
*(sources: src_020, src_004, src_013, src_019)*

## Generality Over Domain Specificity

General-purpose reinforcement learning algorithms can achieve superhuman performance across multiple challenging domains without domain-specific knowledge.

A truly generic algorithm should reuse the same hyper-parameters across different domains without game-specific tuning. AlphaZero mastered chess, shogi, and Go starting from random play, given only the rules, outperforming highly tuned, domain-specific engines.

> "...a general-purpose reinforcement learning algorithm can achieve, tabula rasa, superhuman performance across many challenging domains."
*(sources: src_044, src_041)*

## RLHF is Fundamentally Ungrounded

Relying on human feedback (RLHF) prejudges outputs and prevents the discovery of novel, counterintuitive solutions. True grounding requires environmental interaction.

In RLHF, human raters judge the AI's output before it is tested in the real world. This prevents the system from discovering breakthrough sequences that humans might mistakenly assume are bad. Real grounding comes from facing real-world consequences.
*(sources: src_013, src_019)*

## The Reward Hypothesis

All goals can be described by the maximization of expected cumulative reward.

To make a decision between conflicting goals, an agent must be able to compare them on a single axis. This necessitates converting all objectives into a single scalar reward signal that can be maximized over time. Risk is automatically accounted for when optimizing for expected future reward.

> "all goals can be described by the maximization of expected cumulative reward."
*(sources: src_015)*

## Glorious Failure Over Incremental Success

Researchers should aim for highly ambitious problems rather than safe, incremental ones.

Because AI progresses incredibly fast, ambitious problems might become solvable during your research timeline. It is better to attempt something that makes a real difference than to guarantee success on a trivial problem.

> "it's much better, in my opinion, to, try and do something glorious in research, and maybe fail, than it is to do something you know is incremental, and be guaranteed to succeed."
*(sources: src_018)*
