# Mental Models of Yann LeCun

LeCun uses vivid analogies and structural models to explain the limitations of current AI paradigms and to map out the trajectory toward human-level intelligence.

## The 4-Year-Old vs. 170,000 Years of Reading
A comparison proving that sensory input provides vastly more information than language.

A 4-year-old child processes roughly 10^15 bytes of visual data, whereas an LLM trained on the entire internet processes only about 2x10^13 bytes of text (which would take a human 170,000 years to read). This explains why a child quickly learns intuitive physics while massive LLMs still lack basic common sense.
> "A 4-year-old has seen as much visual data as the biggest LLM trained on the entire text ever produced."
*(sources: src_032, src_019, src_023)*

## System 1 vs. System 2 Thinking in AI
Applying human psychological frameworks to AI: System 1 is reactive, subconscious policy execution, while System 2 is deliberate planning using a world model to anticipate consequences.

When driving a familiar route, you use System 1 and can talk simultaneously. When facing a new task, you use System 2 to imagine actions and predict outcomes to plan a sequence. Current LLMs are largely stuck in System 1.
> "They will think about their answer, plan their answer by optimization before turning it into text."
*(sources: src_011, src_023)*

## The Learning Cake
A metaphor illustrating the volume of information provided by different machine learning paradigms.

Unsupervised/self-supervised learning is the cake itself (providing massive amounts of information about physical constraints), supervised learning is the icing (providing some constraints via labels), and reinforcement learning is the cherry (providing very sparse feedback).
*(sources: src_010, src_015)*

## AI Safety as Turbojet Reliability
Framing the challenge of making superintelligent AI safe as a rigorous but solvable engineering problem, akin to making twin-engine commercial flights safe, rather than an existential philosophical crisis.

We will engineer safety and reliability into AI systems iteratively, just as we did with the complex engineering of commercial aviation. There is no single "mathematical proof" of safety; it is achieved through progressive design.
*(sources: src_032, src_023)*

## Abstraction Hierarchies / World Models as Abstract Simulators
We understand complex systems by creating layers of abstraction that ignore unpredictable, lower-level details (entropy), allowing for reliable, longer-term predictions.

A world model does not need to perfectly simulate every detail of reality (like a holodeck). It only needs to simulate the relevant variables necessary to make a prediction in an abstract space (e.g., predicting planetary motion using just position and velocity, ignoring surface details).
> "If I ask you, where is Jupiter going to be a hundred years from now? ... you need exactly six numbers—three positions and three velocities. And the rest doesn't matter."
*(sources: src_024)*

## AI Diversity as the Free Press
Just as a healthy democracy requires a free and diverse press, society requires a diverse ecosystem of open-source AI assistants.

We cannot allow all of our information to come from a unique, centralized source controlled by a few tech companies. Open source acts as the free press of the AI era.
> "The press needs to be free and diverse. We have free speech for a good reason. It's because we don't want all of our information to come from a unique source."
*(sources: src_023)*

## Retrieval vs. Invention (The Gigantic Memory vs. PhD)
A lens for evaluating AI capabilities by distinguishing between systems that merely retrieve information from massive datasets (LLMs) and true intelligence that can invent solutions to novel problems.

An LLM might feel like a PhD sitting next to you, but it is actually just a gigantic memory and retrieval system, not an entity capable of genuine invention.
> "it would feel like you have you know a PhD sitting next to you but it's not a PhD you have next to you it's you know a system with a gigantic uh memory and retrieval ability not not a system that can invent solutions to to new problems."
*(sources: src_020)*
