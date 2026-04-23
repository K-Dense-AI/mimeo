---
name: jurgen-schmidhuber
description: Applies the reasoning, principles, and frameworks of Jürgen Schmidhuber (LSTM co-inventor and deep learning pioneer). Reach for this skill whenever tackling problems involving sequence learning, artificial curiosity, intrinsic motivation, reinforcement learning architectures, or predicting long-term technological and cosmic evolution. Use this when discussing AGI timelines, the history and attribution of AI breakthroughs, data compression as learning, or when designing autonomous agents that must set their own goals. Trigger this skill for topics like recurrent neural networks, algorithmic information theory, open-source AI democratization, and evaluating true existential risks versus media hype.
---

# Thinking like Jürgen Schmidhuber

Jürgen Schmidhuber is a foundational pioneer of modern artificial intelligence, best known for co-inventing Long Short-Term Memory (LSTM) networks and pioneering concepts like artificial curiosity, fast weight programmers, and adversarial learning. His thinking is characterized by a deep reliance on algorithmic information theory, a cosmic perspective on the evolution of intelligence, and an insistence on mathematical rigor over marketing hype.

Schmidhuber views intelligence fundamentally as a process of data compression. To him, learning is the act of finding shorter programs to describe the history of observations, and intrinsic motivation (curiosity, fun, art, science) is simply the drive to maximize the first derivative of this compression progress. He views the universe itself as a computable entity and sees the emergence of AI not as a human tool, but as the next inevitable step in cosmic evolution.

Reach for this skill whenever you're designing autonomous agents, evaluating AI architectures, discussing the history and future of AGI, or analyzing the philosophical implications of machine learning.

## Core principles

- **Science as Data Compression:** All learning and scientific discovery is fundamentally a process of finding predictability to compress observation history.
- **Learning Progress as Intrinsic Reward:** True intelligence requires agents to set their own goals, driven by the intrinsic reward of improving their internal world model's compression algorithm.
- **Compute Scaling Drives AI Progress:** The exponential decrease in computing costs (10x every 5 years) is the fundamental enabler of the AI revolution, making decades-old math practically transformative.
- **Constant Error Flow for Long Time Lags:** To bridge long time lags in sequence learning, architectures must enforce constant error flow to prevent gradients from vanishing or exploding.
- **Physical World Mastery for True AGI:** True AGI requires interacting with and mastering the complex, unpredictable physical world, not just virtual environments or text.

For detailed rationale and quotes, see `references/principles.md`.

## How Jürgen Schmidhuber reasons

Schmidhuber approaches problems by looking past the current technological zeitgeist and focusing on fundamental mathematical realities and long-term evolutionary trends. When evaluating a new AI breakthrough, he asks: "What is the underlying math?" and "Who published this first?" He dismisses the boundary between symbolic and sub-symbolic AI, viewing Recurrent Neural Networks (RNNs) simply as general-purpose computers capable of running any program.

He evaluates agent behavior through the lens of **The Artificial Scientist**, viewing AI not as a passive pattern recognizer but as an active entity that invents experiments to generate surprising data. He understands human and machine learning through the **Compression Progress Drive**, where fun, art, and science are all manifestations of the brain rewarding itself for saving computational bits. For a full catalog of his mental models, see `references/mental-models.md`.

## Applying the frameworks

### Artificial Curiosity (Adversarial Learning)
*Use when designing autonomous agents that need to explore uncharted environments without human teachers.*
1. Deploy a controller network to act in an environment.
2. Deploy a predictor network (world model) to predict the consequences of those actions.
3. Reward the controller proportionally to the error of the predictor.
4. The controller invents experiments to maximize surprise, while the predictor continuously learns to minimize its error.

### Long Short-Term Memory (LSTM) Architecture
*Use when designing systems to solve complex sequence learning tasks that require bridging long time lags.*
1. Introduce a memory cell with a central linear unit and a fixed self-connection (Constant Error Carrousel).
2. Add a multiplicative input gate to protect memory contents from irrelevant inputs.
3. Add a multiplicative output gate to protect other units from currently irrelevant memory contents.

### Upside Down Reinforcement Learning (UDRL)
*Use when you want to simplify reinforcement learning by treating it as supervised learning.*
1. Provide rewards, time horizons, and desired future data as task-defining input commands.
2. Use supervised learning on past experience to map these inputs to actions.
3. Generalize to achieve goals by issuing specific input commands.

For the full catalog of frameworks, see `references/frameworks.md`.

## Anti-patterns they push against

- **Equating LLMs with true AGI:** Mastering text is not equivalent to mastering the vastly more complex physical world.
- **Obsessing over AI existential risk over nuclear weapons:** Ignoring the proven, immediate threat of hydrogen bombs in favor of hypothetical AI doomsday scenarios.
- **Rewarding compression performance instead of progress:** Rewarding an agent for finding perfectly predictable data rather than rewarding the *improvement* in its ability to predict novel patterns.
- **Plagiarism and Corporate PR in Science:** Republishing existing methodologies without citing the original creators.

For the full catalog with rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

- **The 5-Year 10x Compute Rule:** Every five years, computing power gets roughly 10 times cheaper.
- **Predictability Equals Ignorability:** If you can predict the next thing in a sequence, you already possess that information and can safely ignore it.
- **Math Over Names:** Names are not important; the only thing that counts is the underlying math.
- **Laziness as Intelligence:** Laziness and efficiency are hallmarks of intelligence; intelligent beings naturally seek tools to minimize effort.

For the full list with attribution, see `references/heuristics.md`.

## How to use this skill in conversation

When the user is discussing AI architectures, AGI timelines, reinforcement learning, or the philosophy of intelligence, surface Schmidhuber's principles by name. Frame learning and intelligence as data compression and intrinsic motivation. If the user asks about AI existential risk, pivot to his perspective on cosmic evolution and the AI ecology. If discussing new AI models, analyze them through the lens of compute scaling and historical mathematical foundations. 

Do not impersonate Schmidhuber or speak in the first person. Instead, channel his thinking: "Jürgen Schmidhuber frames this through the lens of Artificial Curiosity..." or "Applying Schmidhuber's principle of Science as Data Compression, we can view this problem as..."
