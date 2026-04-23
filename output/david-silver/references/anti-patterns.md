This document outlines the approaches and paradigms that David Silver explicitly warns against in AI development.

## Relying Exclusively on Human Data

Training AI solely on human data (like internet text) restricts the system to what humans already know.

It only solves the 'shallow problem' of distilling existing knowledge. It prevents the system from discovering radically new solutions, breaking into new frontiers of science, or doing things outside the realm of human experience, and the 'fuel' (data) is running out.
*(sources: src_014, src_007, src_013, src_019, src_004)*

## Hardcoding Human Knowledge

Building human heuristics and knowledge directly into AI algorithms.

It leads to the 'knowledge acquisition bottleneck,' creating brittle systems fitted to human data rather than optimizing the system's ability to learn for itself. It places a hard ceiling on capabilities.
*(sources: src_020, src_013, src_004)*

## Relying Solely on RLHF for Evaluation

Using Reinforcement Learning from Human Feedback as the ultimate ground truth for AI outputs.

Human raters might not recognize or appreciate a novel, superior sequence of actions. If the human prejudges the output as bad, the system will never learn to find those breakthrough sequences. It provides only superficial grounding.
*(sources: src_013, src_019)*

## Choosing Safe, Incremental Research

Selecting research problems that are guaranteed to succeed but only offer minor improvements.

It wastes precious time and ignores the fast rate of progress in AI, which often makes highly ambitious problems solvable within a few years anyway.
*(sources: src_018)*

## Relying on Toy Domains for AI Development

Exclusively using simple microworlds to test and develop AI algorithms.

The simplicity of microworlds is misleading; sophisticated ideas that work well there often fail to scale up to the memory, computation, and practical challenges of larger, more realistic domains.
*(sources: src_052, src_050)*

## Monte-Carlo for Off-Policy Control

Using Monte-Carlo learning for off-policy control is ineffective because the target and behavior policies diverge too much over many steps.

Over many steps, the target policy and the behavior policy diverge too much, meaning they 'never match enough to be useful.'

> "Monte-Carlo learning is a really bad idea off-policy, it does not work because over many steps, your target policy and your behavior policy never match enough to be useful"
*(sources: src_036)*

## Treating RL Data as IID

Assuming reinforcement learning data is Independent and Identically Distributed.

In RL, data is highly correlated over time (sequential), and the agent's actions actively change the distribution of the data it will see next.
*(sources: src_015)*

## Using Full History as Agent State

Using the complete history of an agent's experience to determine its next action.

While technically a valid Markov state, the history grows enormously over time, making it computationally impractical for long-lived agents dealing with microsecond interactions.
*(sources: src_015)*
