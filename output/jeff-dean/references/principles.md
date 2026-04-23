# Core Principles of Jeff Dean

These principles represent Jeff Dean's foundational beliefs about system design, machine learning architecture, and research velocity. They serve as both core philosophies and practical decision rules.

## Hardware-Algorithm Co-design
Hardware and algorithms must be co-designed to maximize performance and efficiency. By understanding hardware constraints and opportunities, algorithm designers can make trade-offs (like using lower precision or quantization) that drastically increase throughput. This mutually-reinforcing loop is central to advancing AI capabilities.
> "yes, quantization is irritating, but your model is going to be three times faster, so you're going to have to deal." (sources: src_026, src_002, src_025, src_010, src_036)

## Design Systems for 5-10x Scale
Design systems to scale by factors of 5 or 10, but not 100x, because massive scale usually enables a completely different and more efficient point in the design space. If you design a system for X and something suddenly becomes 100X, the new scale will require and enable a completely new architecture that wouldn't make sense at the original scale.
> "you're want to design a system so that the most important characteristics could scale by like factors of five or 10 but probably not beyond that because often what happens is if you design a system for X and something suddenly becomes 100X that would enable a very different point in the design space" (sources: src_033)

## Consolidate AI Research and Compute
Stop fragmenting compute and ideas across multiple siloed teams; combining efforts into a single, unified model maximizes compute investment and accelerates progress. Separate research efforts lead to fragmented work and duplicated use of compute resources.
> "instead of fragmenting our compute and our ideas let's all work together and build a single kind of model that is multimmodal that uh has you know a lot comput investment behind a more singular effort" (sources: src_015, src_018, src_033)

## Massively Multi-task Models
Build single, multi-task models rather than separate models for every individual problem. Instead of training a model from scratch for every new problem, a single giant model that already knows how to do 10,000 things can learn the 10,001st thing with vastly fewer examples by building on its existing representations.
> "we tend to Train separate models for each different problem we care about I think this is a bit misguided like really we want one model that does a lot of things so that it can build on the knowledge in how it does thousands or millions of different things" (sources: src_010, src_011)

## Sparsely Activated Models
Build sparsely activated models to balance massive capacity with inference efficiency. You want models to have massive capacity to remember things, but you need them to be highly efficient during inference by only activating a small percentage of the network per token.
> "you'd like you know trillions of parameters but activate only you know one 1% or 5% or 10% of that" (sources: src_015, src_033)

## Latency as a First-Class Objective
Low latency is a prerequisite for the future of complex, agentic AI workflows. As users ask models to perform increasingly complex, multi-step tasks, the model will need to generate vastly more tokens. Low latency is required to make these workflows practical.
> "I think latency is actually a pretty important characteristic for these models because we’re going to want models to do much more complicated things that are going to involve, you know, generating many more tokens..." (sources: src_002, src_030)

## Reasoning over Memorization
Devote parameter space to reasoning, not memorization of obscure facts that can easily be retrieved. It is inefficient to use precious model capacity to memorize facts. Models should focus on reasoning and use retrieval as a tool.
> "having the model devote precious parameter space to remember obscure facts that could be looked up is actually not the best use of that parameter space" (sources: src_033)

## Chain of Thought as Inference Compute
Chain of thought prompting is a way of allocating more compute at inference time to improve reasoning. Because every generated token requires a pass through the model, prompting a model to show its work step-by-step effectively gives it more computational time to arrive at the correct answer.
> "you're actually giving the model more compute to think at inference time, right? Because every token it needs to generate is a pass through the model." (sources: src_015, src_033)

## Optimize for Experimental Velocity
Reducing experimental turnaround time fundamentally changes the qualitative feel and pace of scientific research. Getting iteration time down from weeks or months to minutes or hours prevents engineers from waiting around and fundamentally improves how they experiment, work, and discover.
> "because there's a very different qualitative feel to doing science and research in a domain where an experiment takes a month versus doing it in a domain where you know minutes or hours you get you know an answer" (sources: src_010)
