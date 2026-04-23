# Anti-Patterns Jeff Dean Pushes Against

These are the specific practices, architectural choices, and research habits that Jeff Dean explicitly warns against, along with his rationale for why they fail at scale.

## Designing for 100x Scale Prematurely
Designing a system to scale 100x from the start. A 100x scale usually enables a completely different, more efficient point in the design space that wouldn't make sense at the current scale (e.g., moving from disk-based to in-memory indexes). Over-designing for 100x prematurely leads to suboptimal solutions.
(sources: src_002, src_033)

## Fragmenting AI Research and Compute
Fragmenting compute and ideas across multiple siloed model teams. It dilutes compute investment, divides the best people and ideas, and prevents the creation of a powerful, unified, state-of-the-art multimodal model.
(sources: src_015, src_018, src_033)

## Training Isolated, Single-Task Models
Training a bespoke model to do only one specific thing. It prevents the model from transferring knowledge to new domains, requires massive amounts of data for every new problem, and blocks the emergence of reasoning capabilities.
(sources: src_010, src_011)

## Brute-Forcing Long Context
Relying solely on bigger context windows or naive attention algorithms for trillion-token context. Naive attention scales quadratically, making it computationally impossible to run on trillions of tokens. True scale requires retrieval systems that give the illusion of infinite context.
(sources: src_026, src_030)

## Dense Activation for Every Token
Activating the entire dense model for every single inference or token. It is computationally inefficient and limits the total capacity the model can have given a fixed inference budget.
(sources: src_015)

## Relying on Handwritten Heuristics
Relying on handwritten heuristics in core computer systems (like OS or compilers). Handwritten heuristics have to work well in the general case and cannot dynamically adapt to how the system is actually being used in specific contexts. They should be replaced by learned models.
(sources: src_036)

## Chasing SOTA with Limited Compute
Chasing state-of-the-art (SOTA) results with limited compute by making incremental tweaks. It prevents researchers from exploring truly unique and interesting ideas. Small-scale research should focus on the "slope" (trend) of an idea rather than its absolute performance against a baseline.
(sources: src_015)

## Ignoring Energy Costs at Batch Size 1
Running inference at batch size 1 without considering energy costs. While latency is great at batch size 1, the energy cost of moving weights from memory to the compute unit is massive compared to the compute itself. Without batching, you waste massive amounts of energy.
(sources: src_002)

## Deeply Reading Single Papers for General Learning
Deeply reading a single research paper as a primary method for general learning. It prevents you from getting a broad overview of many techniques, making it harder to connect the dots across different fields and problems. Reading 100 abstracts is better.
(sources: src_036)

## Letting Fear of Mistakes Delay Releases
Letting the fear of AI models making mistakes prevent or delay the release of AI products. It allows competitors to capture the market and launch viral products first, causing the cautious company to lose its advantage and be perceived as a laggard.
(sources: src_041)
