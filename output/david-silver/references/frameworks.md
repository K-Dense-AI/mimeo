This document catalogs David Silver's frameworks for structuring AI research, designing reinforcement learning agents, and building self-play loops.

## Zero-Knowledge Self-Play Loop (AlphaZero)

A method for mastering complex, formalizable domains from scratch without human bias.

**Steps:**
1. Throw away all human knowledge and provide only the fundamental rules of the environment.
2. Run a Monte Carlo tree search using a policy network (actions) and value network (evaluating states).
3. Update the policy towards the best action found by the search.
4. Update the value function towards the actual outcome of the self-play games.
5. Iterate millions of times to generate a superhuman agent.
*(sources: src_014, src_004, src_013, src_019)*

## The Rising Tide Problem Selection

A framework for selecting the right research problems by targeting the '50/50 sweet spot' just above the current capabilities of AI.

**Steps:**
1. Assess the current 'water level' of AI progress (what is already mastered).
2. Identify problems that are 'just the right height above the tide'—feasible to crack within a couple of years.
3. Ensure the problem is not straightforward, targeting a perceived chance of success of at most 50%.
4. Commit boldly, trusting the rapid background rate of AI progress to help make it solvable.

> "picking a good problem is about picking something which is just the right height above the tide that you know it's it's feasible like it's going to be cracked within the next you know a couple of years."
*(sources: src_007, src_018)*

## RL Agent Decomposition

A structural approach to designing solution methods for an agent interacting with a complex environment.

**Steps:**
1. Decompose the agent's decision-making process into learnable components.
2. Decide whether to explicitly represent a value function (predicting future reward).
3. Decide whether to explicitly represent a policy (choosing actions).
4. Decide whether to explicitly represent a model (predicting the environment).
*(sources: src_020)*

## Autonomous RL Rule Discovery (DiscoRL)

A meta-learning framework for discovering new, general-purpose reinforcement learning algorithms.

**Steps:**
1. Instantiate a population of agents interacting with diverse environments.
2. Define an expressive space of predictions.
3. Use a meta-network to process trajectories and output targets.
4. Update agent parameters to minimize distance to targets (Agent Optimization).
5. Use meta-gradients to update the meta-network to maximize cumulative rewards (Meta-Optimization).
*(sources: src_050)*

## Dyna-2 Architecture

A framework combining general domain knowledge with highly specific, situational tactics.

**Steps:**
1. Acquire general domain knowledge offline from past interactions (Long-term memory).
2. Acquire local knowledge specialized to the current state online by simulating future interactions (Short-term memory).
3. Combine both to evaluate positions and select actions.

> "The temporal-difference learning algorithm acquires general domain knowledge from its past interactions with the world. In contrast, the temporal-difference search algorithm acquires local knowledge that is specialised to the current state... We combine both forms of knowledge together in the Dyna-2 architecture."
*(sources: src_052)*
