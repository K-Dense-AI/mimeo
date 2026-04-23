# Frameworks

These are the concrete methodologies and structural approaches Christopher Manning uses to solve problems in NLP, evaluate models, and guide research.

## Critical Reading for Research
A method for reading scientific papers to cultivate creativity by actively questioning assumptions and aiming to 'break' the authors' ideas.
**Steps:**
1. Take a critical mindset.
2. Actively ask what the authors are assuming.
3. Question why they chose their specific method.
4. Aim to find why their ideas aren't the best way.
5. Explore modifications or 'second vectors' off current practices.
> "...you really want to be concentrating, on being awake as you read, and trying to think well what are they assuming, why are they doing it this way rather than some other way..."
*(sources: src_020)*

## Interactive Linguistic Web Agent Loop
A framework for building AI agents that navigate and perform tasks on the web using accessibility trees and interactive learning.
**Steps:**
1. Define the agent's action space.
2. Provide an explicit objective.
3. Supply a history of past events.
4. Provide the current state using a textual accessibility tree (not raw pixels).
5. Allow the agent to learn interactively by building trajectories.
*(sources: src_011)*

## The Structural Probe Method
A technique to investigate whether discrete hierarchical structures (like syntax trees) are embedded in the continuous internal representations of neural networks.
**Steps:**
1. View a tree as a metric space where distance equals path length.
2. Define a distance metric with tunable parameters for the vector space.
3. Use supervised data to find the linear transformation that best fits tree path distances.
4. Construct minimum-spanning trees to recreate syntax trees from continuous space.
> "At a high level, this method finds a single distance metric on which, when applied to any two word representations constructed by the model for the same sentence, approximates the result of the distance metric defined by the syntax tree of that sentence"
*(sources: src_042)*

## Layer-Grouped Universal Transformer
An architectural design for transformers to achieve better systematic generalization and parameter efficiency.
**Steps:**
1. Replace standard MLPs with a mixture of experts using individual sigmoids.
2. Extend MoE down to the attention layer.
3. Apply 'per-layer norm'.
4. Group 2 to 3 layers together to implement complex circuits recurrently across the network.
> "we could get a lot further in uni using universal transformers if instead we had a group of layers which could implement circuits or universal computation and then we can repeat that group of layers recurrently going up."
*(sources: src_011)*

## Unsupervised Open-Ended Goal Discovery
A method for autonomous web agents to explore unknown websites, propose goals, and fine-tune smaller models without prior human demonstration.
**Steps:**
1. Provide a base LLM with a textual accessibility tree.
2. Prompt it to explore and follow the trajectory.
3. Use the LLM to propose a goal and evaluate progress.
4. Use rejection sampling to optimize trajectories.
5. Fine-tune a smaller model on the collected data.
> "we are able to learn by unsupervised interaction from any site that you show. So, it tries to discover what you can do with a website. It then works out ways of satisfying goals and that can then build a strong system for a web agent."
*(sources: src_011)*
