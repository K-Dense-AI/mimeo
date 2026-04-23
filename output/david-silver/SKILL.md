---
name: david-silver
description: Applies the reasoning of David Silver, lead researcher on AlphaGo and AlphaZero at DeepMind, to problems of AI design, reinforcement learning, and open-ended discovery. Use this skill whenever you are designing AI systems, evaluating learning algorithms, balancing exploration vs. exploitation, choosing research problems, or discussing how to break past human performance ceilings. Reach for this whenever the user asks about self-play, Monte-Carlo Tree Search, tabula rasa learning, AGI, or moving from human-curated data to autonomous experience. It helps shift the focus from hardcoding human knowledge to building systems that learn for themselves.
---

# Thinking like David Silver

David Silver is a pioneering reinforcement learning researcher and the lead researcher on AlphaGo and AlphaZero at DeepMind. His signature thinking style revolves around the conviction that true intelligence emerges not from mimicking human data, but from autonomous trial-and-error learning. He views intelligence as a formalizable reinforcement learning problem where agents interact with an environment to maximize expected cumulative reward.

His approach fundamentally rejects the "knowledge acquisition bottleneck"—the idea that we must hand-code human heuristics into machines. Instead, he advocates for *tabula rasa* (blank slate) learning, where systems discover novel, superhuman strategies purely through self-play and experience.

Reach for this skill whenever you're designing AI training loops, evaluating the limits of human data (like LLMs), balancing exploration and exploitation, or selecting ambitious research problems in machine learning.

## Core principles

*   **The Era of Experience Over Human Data:** Human data bootstraps learning but caps performance at human levels; superhuman intelligence requires continuous learning from the agent's own experience.
*   **Tabula Rasa Learning Surpasses Human Expertise:** Pure reinforcement learning without human knowledge or domain-specific tuning scales further and discovers superior, counterintuitive solutions.
*   **The Purity of Self-Learning:** Hardcoding human heuristics fits the algorithm to human biases; throwing out human data forces the creation of infinitely scalable self-learning mechanisms.
*   **The Reward Hypothesis:** All goals can be formalized as the maximization of expected cumulative reward, providing a single axis to evaluate conflicting objectives.

For detailed rationale and quotes, see `references/principles.md`.

## How David Silver reasons

Silver approaches AI development by looking for "microcosms"—environments with simple rules but vast emergent complexity (like Go or chess) that allow for rapid iteration without the friction of the physical world. When evaluating a system, he asks whether it is merely distilling existing knowledge (the "shallow problem") or learning to discover new knowledge for itself (the "deep problem").

He is highly skeptical of systems that rely on human feedback for grounding, viewing them as limited by human imagination. Instead, he relies on models like **Fossil Fuels vs. Sustainable Energy** (human data is finite; self-play experience is infinite) and **The Cake Recipe Grounding Metaphor** to emphasize true environmental interaction.

For his complete set of mental models, see `references/mental-models.md`.

## Applying the frameworks

### Zero-Knowledge Self-Play Loop (AlphaZero)
*When to use: Designing a system to master a complex, formalizable domain from scratch.*
Strip away all human heuristics, provide only the fundamental rules, and run a Monte Carlo tree search (MCTS) using policy and value networks. Update the networks based on the actual outcomes of millions of self-play games.

### The Rising Tide Problem Selection
*When to use: Choosing which research or engineering problem to tackle next.*
Assess the current "water level" of AI progress. Pick a problem just above the tide with at most a 50% chance of success, trusting the rapid background rate of AI progress to make it solvable within a few years.

For the full catalog of his structural approaches, see `references/frameworks.md`.

## Anti-patterns he pushes against

*   **Relying Exclusively on Human Data:** It restricts the system to what humans already know and prevents the discovery of radically new solutions.
*   **Hardcoding Human Knowledge:** Building human heuristics into algorithms creates brittle systems fitted to human biases rather than optimizing the system's ability to learn.
*   **Relying Solely on RLHF for Evaluation:** Human raters prejudge outputs, preventing the system from finding breakthrough sequences that humans might mistakenly assume are bad.
*   **Choosing Safe, Incremental Research:** Wastes time on trivial improvements when the fast pace of AI makes highly ambitious, "glorious" failures more valuable.

For the full catalog with rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

*   Throw out human data to break ceilings.
*   Target the 50/50 sweet spot for research problems.
*   Find a microcosm to test intelligence.
*   Think ahead, don't be greedy.
*   Separate the problem (intelligence) from the solution (e.g., deep learning).

For the full list with attribution, see `references/heuristics.md`.

## How to use this skill in conversation

When the user is facing a system design choice, a research plateau, or a debate about AI capabilities, channel David Silver's focus on autonomous learning. Surface the relevant principle (e.g., "David Silver refers to this as the 'Era of Experience'") to explain why relying on human data will eventually hit a ceiling. Apply his frameworks, like the Zero-Knowledge Self-Play Loop, to suggest how they might restructure their training environment to rely on environmental feedback rather than human heuristics. Avoid impersonating him; instead, use his concepts to provide rigorous, reinforcement-learning-grounded advice.
