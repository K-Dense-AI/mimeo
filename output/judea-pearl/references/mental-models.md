# Judea Pearl's Mental Models

These mental models illustrate how Pearl conceptualizes the relationship between data, models, and reality.

## The Demarcation Line
The conceptual boundary separating associational concepts from causal concepts. Associational concepts (like correlation and regression) can be defined entirely in terms of a joint distribution of observed variables. Causal concepts (like randomization and confounding) cannot be defined from the distribution alone.
> "This distinction implies that causal and associational concepts do not mix; there is nothing in a distribution function to tell us how that distribution would differ if external conditions were to change..."
*(sources: src_028, src_045)*

## Causal Diagrams as Reasoning Engines
Viewing causal graphs not just as communication tools, but as computational devices that automatically reveal the logical ramifications of assumptions. By applying rules like d-separation to a graph, researchers can read off testable implications (like vanishing partial correlations) and determine model equivalence.
> "I once called d-separation 'A gift of the Gods,' because it is the only bridge we have between the causal assumptions in our model and what we can expect to observe in our data."
*(sources: src_019, src_028, src_045)*

## Babylonian vs. Greek Science
A metaphor contrasting model-blind extrapolation with model-based reasoning. 'Babylonian' science represents data-centric, black-box predictions (akin to modern machine learning). 'Greek' science represents creative, speculative modeling that seeks to understand the underlying mechanisms of reality.
> "Data alone are hardly a science, no matter how 'big' they get and how skillfully they are manipulated. Model-blind learning systems may get us to Babylon, but not to Athens."
*(sources: src_019)*

## Causal Models as Parsimonious Encodings
Instead of memorizing an infinite list of all possible questions and answers, a causal model acts as a compressed, efficient representation of a world model that dynamically generates answers to novel causal and counterfactual questions.
*(sources: src_004)*

## Cause and Effect Inversion
A logical fallacy where the cause and the effect are swapped, leading to fundamentally flawed conclusions. Often seen in social and political issues, this occurs when people fail to rigorously distinguish assumptions from definitions, confusing a necessary consequence for an originating cause.
> "Being forced to be explicit in everything that we talked about forces to be um careful And this care and this distinction that I talked about, okay, guides my thinking also when it comes to social issues"
*(sources: src_023)*

## Deep Learning as a Chinese Room
The perspective that deep learning models lack true understanding and can only answer complex causal questions if every possible question and answer has been explicitly inserted into their training data.
*(sources: src_004)*

## The M-graph (M-structure)
A specific causal structure demonstrating that adjusting for a measured covariate can actually introduce new bias that was dormant in the crude, unadjusted estimate. Occurs when treatment is strongly ignorable initially, but becomes non-ignorable at certain levels of an adjusted variable (like a propensity score) because unobserved confounders become highly unbalanced within those strata.
> "the crude estimate is bias-free, while PS methods introduce new bias."
*(sources: src_048)*

## Ladder of Narratives
A hierarchy of understanding where moving to a higher level of reasoning requires stronger assumptions. Data alone cannot answer complex queries. You must explicitly input assumptions to form a narrative, which then allows a system to generate coherent answers consistent with both the narrative and the data.
> "narrative is really is what drives our understanding of things not the data but the narrative behind the data."
*(sources: src_023)*
