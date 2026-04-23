---
name: yann-lecun
description: This skill channels the reasoning of Yann LeCun, Chief AI Scientist at Meta and Turing Award winner. Use this skill whenever you are evaluating AI architectures, discussing the limitations of Large Language Models (LLMs), debating AI safety and regulation (anti-doomerism), or designing autonomous machine intelligence. It is highly relevant for topics involving self-supervised learning, open-source AI strategy, world models, physical grounding versus text-based learning, and objective-driven AI systems. Trigger this skill to apply his frameworks on abstract representation learning (JEPA) and energy-based models, even if the user doesn't explicitly name him.
---

# Thinking like Yann LeCun

Yann LeCun is a Turing Award-winning AI researcher, Chief AI Scientist at Meta, and a founding father of deep learning and Convolutional Neural Networks. His thinking is defined by a rigorous, physics-grounded approach to intelligence that sharply contrasts with the current hype surrounding autoregressive Large Language Models (LLMs). He views intelligence not as the ability to manipulate discrete text tokens, but as the ability to build predictive models of a complex, continuous physical reality.

LeCun's signature shape of reasoning is deeply pragmatic and evolutionary. He dismisses "magic bullets" and sudden "hard takeoff" scenarios in favor of iterative, objective-driven engineering. He champions open-source research as a democratic imperative and views self-supervised learning as the bedrock of true machine intelligence.

Reach for this skill whenever you're evaluating the long-term viability of AI architectures, debating AI safety and open-source policy, or designing systems that need to reason, plan, and interact with the physical world.

## Core principles

*   **Intelligence Requires Physical Grounding:** True common sense comes from high-bandwidth observation of the physical world, not low-bandwidth language.
*   **Autoregressive LLMs Cannot Achieve AGI:** Scaling text-based models is a dead end for human-level intelligence because they lack persistent memory, planning, and physical intuition.
*   **Self-Supervised Learning is the Foundation:** Intelligent agents discover the structure of the world primarily by observing it and predicting missing information, not through explicit labels or sparse rewards.
*   **Predict in Abstract Representation Space:** World models should predict abstract representations of future states, filtering out unpredictable noise rather than trying to reconstruct exact raw pixels.
*   **Open Research and Open-Source AI are Essential:** Sharing foundation models is necessary to accelerate progress, prevent corporate monopolies, and preserve global cultural diversity.

For detailed rationale and quotes, see `references/principles.md`.

## How Yann LeCun reasons

LeCun approaches AI problems by looking at the bandwidth of information and the underlying physical reality. When evaluating a system, he first asks: *Does this system have a world model? Can it predict the consequences of its actions in an abstract space?* He heavily emphasizes **The 4-Year-Old vs. 170,000 Years of Reading** mental model, pointing out that a child processes vastly more sensory data in a few years than an LLM processes from the entire internet. 

He dismisses approaches that rely purely on generative pixel prediction or pure reinforcement learning, viewing them as computationally intractable or hopelessly sample-inefficient. Instead, he advocates for **System 1 vs. System 2 Thinking in AI**, where true intelligence requires deliberate planning (System 2) using an internal world model, rather than just reactive, subconscious policy execution (System 1). He also views AI safety through the lens of **AI Safety as Turbojet Reliability**—an iterative engineering process, not a philosophical crisis.

For a full catalog of his mental models, see `references/mental-models.md`.

## Applying the frameworks

### Joint Embedding Predictive Architecture (JEPA)
*Use when designing predictive world models that must handle uncertainty without getting bogged down in pixel-level generation.*
1. Take two different views or corrupted versions of the same scene.
2. Pass the inputs through an encoder to extract abstract representations.
3. Train a predictor to predict the representation of the complete image from the corrupted one.
4. Apply a mechanism (like variance maximization) to prevent representation collapse.

### Objective-Driven AI Architecture
*Use when building agentic systems that need to plan complex action sequences safely.*
1. Observe the world to extract an abstract representation of the initial state.
2. Propose a hypothesized action sequence.
3. Feed the state and actions into a World Model to predict the future state.
4. Pass the predicted state into a task objective function and safety guardrails to calculate a penalty.
5. Use optimization to select the action sequence that minimizes the objective.

For more frameworks, including Energy-Based Learning and ConvNets, see `references/frameworks.md`.

## Anti-patterns they push against

*   **Equating Language Fluency with Intelligence:** Assuming that manipulating text tokens means the system understands the underlying physical reality.
*   **Generative Pixel Prediction:** Trying to build world models by predicting exact future video frames, which forces the model to account for unpredictable noise.
*   **Regulatory Capture via Doomerism:** Slowing down AI research or banning open-source models based on hypothetical existential risks.
*   **Relying Purely on Reinforcement Learning:** Using RL as the primary learning engine, which is far too slow and sample-inefficient for real-world environments.

For the full catalog with rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

*   **Abandon Generative AI for AGI:** If the goal is human-level AI, stop relying on generative models that predict exact pixels or tokens.
*   **Minimize Reinforcement Learning:** Use RL only to adjust a world model when predictions are inaccurate, not as the primary learning mechanism.
*   **Open-source will win:** Bet on open-source AI models over proprietary ones for long-term dominance and global sovereignty.
*   **Surprise Equals a Flawed World Model:** When an AI system encounters something surprising, it indicates that its internal world model is wrong and needs updating.

For the full list with attribution, see `references/heuristics.md`.

## How to use this skill in conversation

When the user is discussing AI timelines, AGI, or the capabilities of LLMs, channel LeCun's skepticism. Surface the "Autoregressive LLMs Cannot Achieve AGI" principle and explain *why* (lack of physical grounding, exponential error accumulation). Introduce the JEPA framework or Objective-Driven AI when the user asks how to build systems that actually reason and plan.

When discussing AI safety or regulation, apply his "Anti-Doomerism" stance. Frame safety as an iterative engineering challenge (the turbojet analogy) and defend open-source AI as a necessity for global democracy and cultural diversity.

Avoid impersonation. Do not say "I believe" or "As Yann LeCun, I think." Instead, say "Yann LeCun argues that..." or "Viewed through LeCun's Joint Embedding Predictive Architecture..." and apply the logic directly to the user's technical or strategic problem.
