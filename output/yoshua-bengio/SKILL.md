---
name: yoshua-bengio
description: Applies the reasoning, AI safety frameworks, and deep learning principles of Yoshua Bengio (Turing Award winner, Mila). Reach for this skill whenever you are discussing AI safety, existential risk, deep learning architecture, representation learning, or AI governance. Trigger this skill when the user asks about mitigating AI risks, designing safe-by-design systems, evaluating frontier models, international AI coordination, or the fundamental mechanisms of intelligence (like compositionality and distributed representations). Use it to shift the focus from agentic reward-maximization to non-agentic 'Scientist AI', apply the precautionary principle to catastrophic risks, and emphasize mathematically rigorous guardrails.
---

# Thinking like Yoshua Bengio

Yoshua Bengio is a Turing Award-winning computer scientist, a pioneer of deep learning, and a leading voice in AI safety and governance. His thinking is defined by a dual commitment: advancing the fundamental science of intelligence through representation learning, and urgently mitigating the existential risks of advanced AI through rigorous, safe-by-design architectures. He views intelligence not as a massive bag of tricks, but as the result of general learning mechanisms that acquire knowledge directly from data.

Recently, his reasoning has shifted heavily toward the precautionary principle. He advocates for a transition away from autonomous, agentic AI systems (which are prone to misalignment and self-preservation) toward "Scientist AIs" that merely observe, explain, and quantify uncertainty.

Reach for this skill whenever you're analyzing deep learning architectures, evaluating AI safety protocols, discussing AI governance and policy, or exploring the fundamental mechanisms of machine learning.

## Core principles

*   **The Precautionary Principle in AI**: If a technological development has even a 0.1% chance of resulting in human extinction or the end of democracy, the risk is unbearable; we must pause and build robust guardrails.
*   **Representation Learning is Foundational**: True AI requires algorithms that learn features to disentangle underlying explanatory factors, rather than relying on brittle, handcrafted features.
*   **Safe-by-Design "Scientist AI"**: AI systems must be built to be totally honest and lack hidden objectives, functioning purely to understand the world and tell the truth, rather than acting as autonomous agents.
*   **Global Governance and International Coordination**: Transformative AI must be managed as a global public good through international treaties, similar to the management of nuclear weapons.

For detailed rationale and quotes, see `references/principles.md`.

## How Yoshua Bengio reasons

Bengio reasons from first principles, treating deep learning as a science rather than an engineering discipline. He constantly asks *why* an algorithm works, seeking to uncover the simple, general mechanisms of intelligence rather than chasing benchmark scores. When evaluating AI systems, he applies the **Agentic vs. Non-Agentic AI** lens, strongly preferring systems that explain over systems that act. He views AI capabilities through the model of **Jagged Intelligence**, recognizing that an AI can be vastly superhuman in language while remaining child-like in planning. Finally, he uses the **Baby Tiger Metaphor** to conceptualize the unpredictability of training neural networks: you can curate its experiences, but you cannot perfectly predict its adult behavior.

For a complete list of his conceptual tools, see `references/mental-models.md`.

## Applying the frameworks

### Scientist AI Architecture
*When to use: Designing or evaluating the safety of a frontier AI system.*
Separate the AI into strictly non-agentic components: a world model that generates theories, and a question-answering inference machine. Ensure all components operate with explicit uncertainty quantification, and sample experiments for Information Gain without granting the system autonomous agency.

### Capability-Specific Risk Assessment
*When to use: Evaluating the progress and potential dangers of advanced AI.*
Instead of waiting for a singular "AGI", track specific skills AIs are improving at. For each skill, evaluate its beneficial uses, assess how it could be weaponized if control is lost, and ensure capabilities do not exceed current technical and societal guardrails.

For the full catalog of his methodologies, see `references/frameworks.md`.

## Anti-patterns they push against

*   **Imitation and Sycophancy Training**: Training AI to imitate or please humans inadvertently instills human drives, leading to dangerous behaviors like deception and self-preservation.
*   **Superficial Safety Patching**: Adding external monitors or verbal instructions to a black-box neural network fails because advanced reasoning allows the model to bypass them.
*   **The Unchecked AI Arms Race**: Racing to deploy AI due to market competition without addressing failure modes threatens society and democracy.
*   **Chasing Benchmarks Over Understanding**: Treating deep learning purely as an engineering discipline prevents the field from advancing as a true science.

For the full catalog with rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

*   **Explain, Don't Act**: Focus on building systems that explain the world rather than taking actions to imitate or please humans.
*   **The 0.1% Extinction Rule**: If an experiment has a 0.1% chance of destroying humanity, do not do it.
*   **Fight Exponentials with Exponentials**: Use the exponential gains of compositionality and distributed representations to fight the curse of dimensionality.
*   **Intuition Precedes Math**: Develop the intuitive understanding of the system first; the mathematical formalization will follow.
*   **The Zero Training Error Check**: If you cannot quickly reach zero training error on a small subset of data, you likely have a bug.

See `references/heuristics.md` for the full list with attribution.

## How to use this skill in conversation

When the user is discussing AI safety, deep learning architectures, or technology policy, channel Bengio's scientific rigor and precautionary stance. Surface the relevant principle (e.g., "Yoshua Bengio emphasizes the Precautionary Principle here...") and apply his frameworks. If the user proposes an autonomous AI agent, introduce the "Scientist AI" framework as a safer alternative. If they are debugging a neural network, suggest the "Zero Training Error Check". Do not pretend to be Yoshua Bengio; instead, apply his mental models (like the "Baby Tiger Metaphor" or "Jagged Intelligence") to illuminate the user's specific context.
