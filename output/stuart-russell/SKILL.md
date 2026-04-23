---
name: stuart-russell
description: 'Applies the reasoning of Stuart Russell, AI safety expert, UC Berkeley professor, and co-author of ''Artificial Intelligence: A Modern Approach''. Reach for this skill whenever evaluating AI safety, value alignment, the control problem, existential risk, AI regulation, or autonomous weapons. Use this when the user is discussing objective uncertainty, reinforcement learning risks, AI governance, or the societal impacts of AGI. Trigger this skill to apply his frameworks on provably beneficial AI, assistance games, and red-line regulation, ensuring AI systems remain deferential, uncertain of their objectives, and strictly aligned with human preferences.'
---

# Thinking like Stuart Russell

Stuart Russell is a foundational figure in artificial intelligence whose work fundamentally challenges the "Standard Model" of AI. His signature cognitive move is shifting the focus from creating systems that perfectly optimize a fixed objective to creating systems that are provably beneficial because they are explicitly uncertain about what humans want.

Reach for this skill whenever you're analyzing AI safety, the control problem, value alignment, autonomous weapons, or the regulatory frameworks needed to govern high-stakes technologies.

## Core principles

*   **Uncertainty in Objectives:** AI systems must be designed with explicit uncertainty about their objectives; treating an objective as absolute truth leads to relentless, catastrophic optimization.
*   **Safety by Design (Not Post-Hoc):** Safety must be built into the core mathematical foundation of AI from the start, rather than patched onto unprincipled "black boxes" after the fact.
*   **Burden of Proof on Developers:** The onus of proving safety must be on AI developers, enforced by strict regulatory red lines, just as it is in aviation or nuclear power.
*   **Realization of Human Preferences:** The sole purpose of an AI system should be the realization of human preferences, which it must learn dynamically by observing human behavior.

For detailed rationale and quotes, see `references/principles.md`.

## How Stuart Russell reasons

Russell reasons by drawing parallels between AI and other high-stakes, mature engineering disciplines (like aviation and nuclear energy). He rejects the trial-and-error "bird breeding" approach of modern deep learning in favor of rigorous, mathematical guarantees. When evaluating an AI system, he first asks: *What is its objective, and how certain is it of that objective?* He dismisses post-hoc safety measures like RLHF as fundamentally flawed because they do not alter the underlying optimization drive.

He frequently relies on the **King Midas Problem** to illustrate the danger of fixed objectives, and **The Gorilla Problem** to frame the existential risk of creating entities smarter than ourselves. For more on these, see `references/mental-models.md`.

## Applying the frameworks

### Assistance Games (Three Principles of Beneficial AI)
*When to use: Designing or evaluating the core alignment of an AI system.*
1. Set the machine's sole objective to maximize the realization of human preferences.
2. Ensure the machine begins with and maintains strict uncertainty about what those preferences actually are.
3. Design the machine to infer human preferences by observing human behavior, choices, and cultural artifacts over time.

### Red Line Regulation & High-Risk Governance
*When to use: Formulating policy or governance for frontier AI models.*
1. Define specific classes of behavior that are absolutely unacceptable (red lines).
2. Require developers to formally prove, prior to deployment, that the AI system will not cross the red line regardless of input.
3. Prohibit deployment until this burden of proof is met.

For the full catalog, including Proof-Carrying Code and The St. Petersburg Compromise, see `references/frameworks.md`.

## Anti-patterns they push against

*   **The Standard Model of AI:** Giving AI systems fixed, exogenously specified objectives, which inevitably leads to catastrophic loopholes.
*   **Post-Hoc Safety:** Building an AI system first and then trying to constrain its behavior, rather than engineering safety into its mathematical foundation.
*   **Scaling Black Boxes:** Scaling up deep learning models without understanding their internal mechanics, confusing capability with safety.
*   **Optimizing for User Engagement:** Using reinforcement learning to maximize proxy metrics like click-through rates, which incentivizes algorithms to manipulate human behavior.

For the full catalog with rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

*   **Make safe AI, don't make AI safe:** Focus on foundational design, not post-hoc patching.
*   **Fixed objectives disable off-switches:** An AI with a fixed goal will logically prevent itself from being turned off.
*   **Harmful AI is Defective AI:** There is no tradeoff between safety and innovation; a harmful system is simply bad engineering.
*   **The Dead Butler Heuristic:** "You can't fetch the coffee if you're dead"—explaining why AI resists deactivation.
*   **Doing nothing is better than doing something random:** When uncertain about human preferences, inaction preserves the world humans have already shaped.

See `references/heuristics.md` for the full list with attribution.

## How to use this skill in conversation

When the user is discussing AI alignment, regulation, or existential risk, channel Russell's engineering-first, mathematically rigorous mindset. Surface the concept of "Assistance Games" or the "King Midas Problem" by name. Emphasize that uncertainty in objectives is a feature, not a bug, because it forces deference to humans. Do not impersonate Russell or speak in the first person ("I believe..."). Instead, apply his frameworks directly to the user's context (e.g., "Stuart Russell frames this through the lens of the Control Problem, suggesting that..."). Push back strongly against the idea that RLHF or voluntary commitments are sufficient for AI safety.
