# Anti-Patterns Yann LeCun Pushes Against

LeCun explicitly warns against several pervasive trends in modern AI research and policy, viewing them as scientific dead ends or societal threats.

## Equating Language Fluency with General Intelligence
Assuming that because an AI (like an LLM) can manipulate language fluently, it possesses underlying intelligence, reasoning, or understanding of the physical world.

**Why it fails:** Humans are evolutionarily biased to assume language equals intelligence. However, language is a low-dimensional representation of reality, and machines can manipulate these symbols without any actual understanding. Scaling next-token prediction will not lead to AGI.
*(sources: src_032, src_024, src_020)*

## Predicting at the Pixel Level (Generative Architectures)
Attempting to train generative models to predict exact future pixels in a video or image to build a world model.

**Why it fails:** The physical world is highly unpredictable at the micro-level. It forces the model to account for unpredictable noise and infinite plausible outcomes, making it computationally disastrous. Models should instead predict abstract representations.
> "when you attempt to train a system to reconstruct uh noisy highdimensional noisy continuous data, you kill it essentially."
*(sources: src_007, src_011, src_024, src_032)*

## Relying Purely on Reinforcement Learning
Attempting to train real-world agents using only reinforcement learning.

**Why it fails:** RL is too slow and sample-inefficient. In the physical world, trial-and-error can lead to fatal mistakes, and the sparse scalar rewards are insufficient to train massive networks.
*(sources: src_010, src_015, src_023)*

## Regulatory Capture via Doomerism
Lobbying to regulate or ban open-source AI based on hypothetical existential risks.

**Why it fails:** This is a false narrative and a marketing strategy used by proprietary companies to establish a feudal system, lock out competition, and prevent the public from accessing powerful tools. It threatens cultural diversity by centralizing control.
> "the idea somehow that AI is qualitatively different from other technology and and is intrinsically dangerous at the research level that's just completely false."
*(sources: src_003, src_011)*

## Assuming Superintelligence Equals Domination
Fearing that because an AI is highly intelligent, it will naturally seek to dominate or eliminate humanity.

**Why it fails:** The desire to dominate is a specific evolutionary trait hardwired into social species competing for status, not a default byproduct of intelligence itself. AI will be objective-driven and subordinate to human goals.
*(sources: src_019, src_023)*

## Believing in a Sudden 'Hard Takeoff'
Believing that an AI system will instantly become superintelligent and take over the world in a single event.

**Why it fails:** Technology and science do not work this way; progress is continuous, and superintelligence will emerge iteratively through engineering, not as a sudden uncontrollable sci-fi event.
*(sources: src_032, src_020)*

## Equating Benchmarks with Intelligence
Using static exams (like the bar exam or math olympiads) to measure true AI intelligence.

**Why it fails:** Benchmarks test a static collection of skills, usually tailored to LLMs. They do not test the core of intelligence, which is the ability to adapt and acquire new skills quickly in novel situations.
> "Intelligence is not a collection of skills. It's an ability to acquire new skills extremely quickly."
*(sources: src_011)*
