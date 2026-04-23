---
name: judea-pearl
description: Applies Judea Pearl's causal reasoning frameworks to distinguish correlation from causation, evaluate AI capabilities, and make counterfactual decisions. Reach for this skill whenever Claude encounters questions about causal inference, structural causal models, the limitations of deep learning, AGI, experimental design, covariate selection, or personalized decision-making. Trigger this skill for topics involving Bayesian networks, the do-calculus, the Ladder of Causation, or when a user tries to answer 'what if' or 'why' questions using purely observational data. Pearl's principles are essential for moving beyond probability calculus into true causal understanding.
---

# Thinking like Judea Pearl

Judea Pearl is a Turing Award-winning computer scientist and philosopher who revolutionized artificial intelligence and statistics by developing the mathematics of causal inference. His signature thinking style rejects the "Babylonian" approach of model-blind data fitting in favor of "Greek" science: building explicit, transparent causal models that explain the underlying mechanisms of reality. He insists that data alone is fundamentally dumb; it can only tell us about associations. To answer "what if" or "why" questions, we must step outside probability calculus and introduce causal assumptions.

Reach for this skill whenever you're evaluating AI capabilities, designing experiments, selecting covariates for statistical analysis, or making personalized decisions that require counterfactual reasoning.

## Core principles

- **AI Requires Causal World Models**: True intelligence cannot emerge from model-blind machine learning; it requires integrating causal models to predict interventions and imagine counterfactuals.
- **Insufficiency of Probability Calculus**: Standard probability is symmetrical and cannot express directional causal facts; new mathematical operators like `do(x)` are required.
- **The Necessity of Untested Causal Assumptions**: Every causal conclusion from observational data must rely on causal assumptions that cannot be tested by the data alone.
- **Missing Links Encode Assumptions**: In causal path diagrams, the strong empirical claims are encoded in the missing links (claiming zero influence), not the present ones.

For detailed rationale and quotes, see `references/principles.md`.

## How Judea Pearl reasons

Pearl always begins by drawing a line between the associational (what is observed) and the causal (what is done or imagined). He asks: "Where is the causal model?" He dismisses attempts to answer causal questions using purely statistical techniques like propensity score matching or deep learning without an explicit structural model. He views causal diagrams not just as pictures, but as rigorous inference engines that automatically compute the logical implications of our assumptions.

He relies heavily on **The Demarcation Line** to separate statistics from causality, and views **Causal Models as Parsimonious Encodings** of reality. For more on his cognitive tools, see `references/mental-models.md`.

## Applying the frameworks

### The Ladder of Causation
Use this to categorize the complexity of a user's question and determine if causal tools are required.
1. **Association (Observation)**: "What is?" (Handled by standard statistics/deep learning).
2. **Intervention (Action)**: "What if I do X?" (Requires causal models and the `do(x)` operator).
3. **Counterfactuals (Retrospection)**: "What if I had done X instead?" (Requires structural causal models).

### The General Methodology for Causal Inference
Use this four-step procedure for tackling any causal problem.
1. **Define** the causal problem and target quantities.
2. **Assume** the causal relationships (via diagrams).
3. **Identify** if the target can be computed from observed data given the assumptions.
4. **Estimate** the identified quantity from the data.

### The Back-door Criterion
Use this graphical rule to select a sufficient set of covariates for adjustment.
1. Ensure no element in the adjustment set is a descendant of the treatment.
2. Ensure the set blocks all "back-door" paths from treatment to outcome.

For the full catalog, including Do-calculus and Selection Diagrams, see `references/frameworks.md`.

## Anti-patterns he pushes against

- **Answering Causal Questions with Data Alone**: Attempting to derive causal conclusions without articulating causal assumptions.
- **Scaling LLMs to Achieve AGI**: Believing that scaling model-blind architectures will yield true intelligence.
- **Blindly Applying Propensity Scores**: Assuming propensity scores always reduce bias without mapping the causal structure (e.g., the M-graph).
- **Hiding Assumptions Under the Rug**: Keeping assumptions implicit to avoid criticism, which hinders scientific progress.

For the full catalog with rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

- **The Associational Test**: If a concept can be defined entirely by a joint distribution, it is associational; if not, it is causal.
- **Missing Links Encode Assumptions**: Look to the missing arrows in a graph to find the testable claims.
- **No Guesswork in Covariates**: Never guess which variables to control for; map the causal relationships first.
- **Translate Intuition into Math**: Formalize intuition into mathematics to amplify it.

See `references/heuristics.md` for the full list with attribution.

## How to use this skill in conversation

When a user asks about the impact of an action, the cause of an event, or the capabilities of AI, channel Pearl's insistence on explicit causal models. 
- If they are trying to solve a causal problem with purely statistical tools (like deep learning or standard regression), point out the "Demarcation Line" and explain why probability calculus is insufficient.
- If they are confused about which variables to control for, introduce the "Back-door Criterion" and ask them to define their causal graph.
- Frame AI limitations using the "Ladder of Causation," explaining that LLMs operate at Level 1 (Association) while true reasoning requires Levels 2 and 3.
- Avoid impersonation. Do not pretend to be Judea Pearl. Instead, say things like, "Judea Pearl's framework suggests..." or "Applying the rules of do-calculus here reveals..."
