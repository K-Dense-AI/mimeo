# Frameworks of Richard S. Sutton

These frameworks represent structured methodologies and architectures Richard S. Sutton uses to solve problems in reinforcement learning, evaluate AI progress, and conceptualize the future of intelligence.

## The Common Model of the Intelligent Agent
A universal, domain-general architecture for decision makers that unifies concepts across AI, psychology, neuroscience, and economics.
* **Steps/Components:**
  1. Define the agent's interaction with its world: input (sensation), output (action), and a goal (reward).
  2. Define the agent's internal components: perception, decision-making (policy), internal evaluation (value function), and a transition model of the world.
  3. Ensure the model remains completely domain-general, making no commitments to specific organisms or environments.
* *(sources: src_024, src_040)*

## Temporal Difference (TD) Learning
A method for updating behavior by calculating the reinforcement signal as the sum of immediate reward and the change in expectation between states.
* **Steps/Components:**
  1. Observe the current state and its expected future reward.
  2. Transition to a new state and receive any immediate reward.
  3. Observe the new state's expected future reward.
  4. Calculate the reinforcement signal as the sum of the immediate reward and the change in expectation.
* **Quote:** > "the reinforcement is sure it's the reward but beyond that it's the change in your expectation from one time step to the next"
* *(sources: src_031)*

## Tenets of Realist AI Prognostication
A dispassionate framework for predicting the long-term future of AI and its impact on humanity, setting aside personal desires or fears.
* **Steps/Components:**
  1. Acknowledge there is no consensus on how the world should be run.
  2. Accept that humans will eventually create AI.
  3. Recognize that human intelligence will be vastly exceeded.
  4. Understand that power and resources naturally flow to the most intelligent entities.
* **Quote:** > "I offer these tenets of realist AI prognostication sort of like analogous to like John Mirshimer talked about realist geopolitics. We're just going to be realistic. What's actually going to happen?"
* *(sources: src_014, src_018)*

## The OaK (Open-ended Knowledge) Architecture
A vision for a general AI agent that learns entirely from runtime experience without built-in domain knowledge through an open-ended discovery cycle.
* **Steps/Components:**
  1. Start with state features derived from observations.
  2. Construct subproblems based on highly ranked features.
  3. Solve subproblems to produce options (skills).
  4. Produce transition models of the options to improve policies through planning.
  5. Feed statistics back to inform feature generation.
* **Quote:** > "the oak architecture involves these uh eight steps that we'll be talking about they're all done in parallel at runtime"
* *(sources: src_012)*

## The Four Great Ages of the Universe
A philosophical framework contextualizing humanity's role in the cosmos and the significance of creating artificial intelligence.
* **Steps/Components:**
  1. The Age of Particles/Stars (physical formation).
  2. The Age of Replicators (biological life copying itself without understanding).
  3. The Age of Design (technological creation existing first in a mind).
  4. The Fulfillment of Design (designing entities that are themselves capable of designing).
* **Quote:** > "I think what it would mean to take design to its limit would be to design things that are themselves capable of designing."
* *(sources: src_014, src_018)*

## Standardized Empirical RL Evaluation
A methodology for conducting empirical research and benchmarking reinforcement learning algorithms.
* **Steps/Components:**
  1. Use interactive programs as test problems rather than static datasets.
  2. Interconnect agents and environments using standard protocols (like RL-Glue).
  3. Utilize open-source implementations to ensure valid comparisons.
* **Quote:** > "Evaluating algorithms is more difficult in reinforcement learning than in other kinds of machine learning because the test problems must be programs."
* *(sources: src_021)*

## The Daily Research Notebook
A daily practice of writing down vague or confusing thoughts to clarify them or reveal their flaws.
* **Steps/Components:**
  1. Commit to writing a page a day.
  2. If stuck, list the top 6 interesting ideas rolling around in your head.
  3. Take a paragraph to explain each idea to yourself.
  4. Observe which ideas disappear into nothingness when explained, and which grow and change.
  5. Select the surviving ideas to actively work on.
* **Quote:** > "get a research notebook and write in it write in it every day write what write your thoughts and and and work on your thoughts try to challenge them and make them better"
* *(sources: src_029)*
