# Jeff Dean's Mental Models

These mental models illustrate how Jeff Dean conceptualizes complex systems, the true cost of computation, and the future architecture of artificial intelligence.

## Energy-Based Cost of Computation
Evaluating system bottlenecks in terms of energy (picojoules per bit) rather than just FLOPs, recognizing that data movement is vastly more expensive than computation. The actual math (multiplying numbers) is incredibly cheap, but moving the data from memory to the compute unit is orders of magnitude more expensive. This explains why batching is necessary: you must reuse a parameter across a batch of inputs to amortize the massive energy cost of moving it.
> "Ideally you'd like to use batch size one because the latency would be great but the energy cost and the compute cost inefficiency that you get is quite large." (sources: src_002, src_030, src_033)

## Sparsely Activated Multi-Task Model (The Brain Analogy)
Viewing a machine learning model as a vast network of specialized components where only a tiny percentage of parameters activate per task. Instead of a monolithic block, the system searches for a 'pathway' through existing components that already have relevant expertise. This mirrors the efficiency and storage capacity of the human brain, allowing models to scale to trillions of parameters efficiently.
> "I think what we actually want is a model that's very very big like think you know 100 billion trillion parameters but where for any given thing you activate only a tiny fraction of it 1% of it 5% of it you know your brain works this way" (sources: src_010, src_011, src_025)

## The Illusion of Infinite Context
Using lightweight retrieval funnels to narrow millions of tokens to a small relevant context window, rather than scaling quadratic attention. Instead of trying to scale quadratic attention mechanisms to trillions of tokens (which is computationally infeasible), build a funnel system analogous to search ranking to feed only the most relevant documents into the heavy LLM.
> "I think if you could give the illusion that you can attend to trillions of tokens, that would be amazing." (sources: src_002, src_030)

## AI Agents as a Managed Team of Interns
Shifting the paradigm of AI interaction from a 1:1 chatbot to a human manager coordinating a large, hierarchical team of specialized virtual assistants or interns. Instead of interacting with 50 individual agents directly, a developer might manage 5 sub-teams of agents, similar to managing a 50-person human organization.
> "the human coordinating the activities of a dozen or hundred AI agents doing stuff on their behalf where they've probably the human is probably weekly specified what it is they want." (sources: src_015, src_033)

## Heuristics as Learning Problems
Viewing handwritten heuristics inside traditional computer systems as machine learning problems that should adapt to actual usage patterns. Instead of writing static rules in compilers, operating systems, or storage systems, use learned models that automatically recognize and adapt to specific usage contexts.
> "I think there's huge potential for the thousands, and thousands, and thousands of heuristics in computer systems to really mostly be learned and adapt to how they're actually being used." (sources: src_036)

## Ideas in the Air
A lens for viewing research progress: breakthroughs are rarely entirely novel, but rather combinations of floating concepts. New breakthroughs usually come from 'squinting at' several existing, separate research ideas and combining them with one missing piece to solve a new problem.
> "I like to think of a lot of ideas as being partially in the air, where there are a few different, maybe separate research ideas that one is squinting at when you’re trying to solve a new problem." (sources: src_026)

## Squishy Weights vs. Sharp Context
Understanding how LLMs store information: trained parameters are 'squishy' and prone to hallucination, while the context window is 'sharp'. When a model relies on its 'squishy' trained parameters for specific facts, it might hallucinate. But information placed directly in the input context window remains 'sharp and clear' because the attention mechanism can pinpoint exact text.
> "The information in the context window of the model the input that you give it is very crisp because you haven't mixed it with anything else." (sources: src_015, src_026)
