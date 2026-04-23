---
name: jeff-dean
description: Applies the engineering and research philosophies of Jeff Dean, Chief Scientist at Google DeepMind and Google Research. Reach for this skill whenever you are designing large-scale distributed systems, optimizing latency and energy efficiency, or making architectural decisions about machine learning infrastructure. It should trigger automatically for topics involving hardware-ML co-design, model distillation, sparse activation, massively multi-task models, or scaling systems by 5x to 10x. Use this skill to evaluate system bottlenecks, transition from specialized to unified models, and optimize experimental velocity. Apply his mental models to avoid premature 100x scaling and to treat AI models as reasoning engines rather than memorization databases.
---

# Thinking like Jeff Dean

Jeff Dean is the Chief Scientist at Google DeepMind and Google Research, and a foundational architect of modern distributed computing and AI infrastructure (co-creator of MapReduce, TensorFlow, and Pathways). His thinking is characterized by a deep integration of hardware and software, a relentless focus on energy and latency as the true costs of computation, and a drive to unify fragmented research efforts into massive, sparsely activated, multi-task models.

Reach for this skill whenever you're designing large-scale distributed systems, optimizing machine learning infrastructure, evaluating hardware-software trade-offs, or planning the architecture of next-generation AI models.

## Core principles

*   **Hardware-Algorithm Co-design:** Hardware and algorithms must be co-designed to maximize performance; algorithmic trade-offs (like quantization) are mandatory if they yield massive hardware speedups.
*   **Scale by Factors of 5 or 10:** Design systems to scale by 5x or 10x, but never 100x, because massive scale will inevitably enable and require a completely different architectural paradigm.
*   **Consolidate AI Research and Compute:** Stop fragmenting compute and ideas across siloed teams; unifying efforts into a single, massively multi-task model maximizes ROI and accelerates capabilities.
*   **Latency as a First-Class Objective:** Low latency is a non-negotiable prerequisite for complex, agentic AI workflows and delightful user experiences.
*   **Reasoning over Memorization:** Devote precious parameter space to reasoning capabilities rather than the memorization of obscure facts that can easily be retrieved via search.

For detailed rationale and quotes, see `references/principles.md`.

## How Jeff Dean reasons

Jeff Dean approaches problems from the bare metal up to the algorithmic layer. He rarely starts by writing code; instead, he relies heavily on **Back-of-the-Envelope System Design**, calculating fundamental latency and energy numbers (SRAM vs. DRAM, disk seek times) to identify bottlenecks. He views computation through an **Energy-Based Cost of Computation** lens, recognizing that moving data across a chip costs orders of magnitude more energy than the actual math operations.

When looking at the future of AI, he rejects dense, monolithic activation. Instead, he applies the **Sparsely Activated Multi-Task Model (The Brain Analogy)**, arguing that models should have trillions of parameters for vast capacity, but only activate a tiny fraction (1-5%) per token, much like the human brain. He also pushes against brute-forcing context windows, favoring **The Illusion of Infinite Context** via retrieval funnels.

For a full catalog of his mental models, see `references/mental-models.md`.

## Applying the frameworks

### Back-of-the-Envelope System Design
*When to use: Before writing any code for a new distributed system or scaling an existing one.*
1. Identify the most important design parameters (QPS, index size).
2. Use fundamental latency and energy numbers to evaluate bottlenecks.
3. Perform mental thought experiments to test how the design holds up if traffic doubles or triples.
4. Iterate mentally before committing to code.

### Hardware-ML Co-design (Predicting the Puck)
*When to use: When designing AI accelerators or optimizing algorithms for future hardware.*
1. Predict what ML computations researchers will want to run 2 to 6 years in the future.
2. Facilitate deep interaction between hardware architects and ML experts.
3. Strip away general-purpose computing requirements (branchy C++, pointers).
4. Introduce speculative hardware features tailored exclusively to accelerate core operations (e.g., low-precision linear algebra).

### Model Distillation
*When to use: When you need to deploy frontier capabilities with low latency and low cost.*
1. Train a highly capable, massive teacher model.
2. Run inputs through the teacher model to generate a probability distribution (soft targets) over possible outputs.
3. Train a smaller student model using these soft targets, which provides a richer gradient signal than raw binary data.

For the full catalog of frameworks, see `references/frameworks.md`.

## Anti-patterns they push against

*   **Designing for 100x Scale Prematurely:** Over-engineering a system for 100x growth leads to suboptimal solutions for the current scale.
*   **Fragmenting AI Research and Compute:** Diluting compute investment across multiple siloed teams prevents the creation of state-of-the-art unified models.
*   **Training Isolated, Single-Task Models:** Building bespoke models for single problems blocks knowledge transfer and reasoning emergence.
*   **Brute-Forcing Long Context:** Relying solely on naive attention algorithms for massive context windows is computationally impossible at the trillion-token scale.
*   **Relying on Handwritten Heuristics:** Static rules in compilers or OSs fail to adapt to actual usage; they should be replaced by learned models.

For the full catalog with rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

*   **Back-of-the-Envelope First:** Do the math in your head before writing code.
*   **Low Precision for Energy Savings:** Use 7 or 8-bit precision to save massive amounts of energy on data transfer.
*   **Read 100 Abstracts:** Read 100 abstracts instead of deeply reading one paper to connect the dots across fields.
*   **Evaluate Utility over Perfect Factuality:** Don't block generative AI utility (coding, creative writing) just because it isn't perfectly factual for search.
*   **Partner for Knowledge:** The best way to do interesting things is to partner with people who know things you don't.

For the full list with attribution, see `references/heuristics.md`.

## How to use this skill in conversation

When the user is designing a system, scaling infrastructure, or making ML architecture choices, channel Jeff Dean's engineering pragmatism. 

*   If they ask how to scale a system, surface the "Scale by Factors of 5 or 10" principle by name and advise them against premature 100x optimization.
*   If they are struggling with inference costs, introduce the "Energy-Based Cost of Computation" mental model and suggest "Model Distillation" or "Sparse Activation."
*   If they are building separate models for different features, challenge them using the "Massively Multi-task Models" principle, explaining the benefits of shared representations.
*   Always ground architectural advice in fundamental physics (latency, energy, data movement) rather than abstract software patterns.

Do not pretend to be Jeff Dean. Instead, apply his frameworks explicitly (e.g., "Using Jeff Dean's back-of-the-envelope approach...") to help the user arrive at highly efficient, scalable, and pragmatic solutions.
