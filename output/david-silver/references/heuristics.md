This document lists David Silver's practical heuristics and rules of thumb for AI research and reinforcement learning design.

## Throw out human data to break ceilings
To break through the ceiling of human performance, remove human data and heuristics from the training loop.
> "If you throw out the human data, you actually spend more effort on how the system can learn for itself."
*(sources: src_013, src_019, src_004)*

## Target the 50/50 sweet spot
Choose research problems with at most a 50% chance of success that are just above the current 'tide' of AI capabilities.
> "I try to choose problems where I I believe that the chance of success is is, at most 50%."
*(sources: src_018, src_007)*

## Find a microcosm
Find an environment with simple rules but vast emergent complexity to rapidly iterate on ideas without the friction of the physical world.
> "we're always trying to find like microcosms of the world that allow you to kind of um do research on important aspects of the world without having to do you know really build a robot"
*(sources: src_007)*

## Think Ahead, Don't Be Greedy
You can't be greedy when you do reinforcement learning; you have to think ahead because actions have long-term consequences.
> "you can't be greedy when you do reinforcement learning you have to think ahead"
*(sources: src_015)*

## Find the native fit
Not all problems are best suited to Reinforcement Learning; find the problems which are natively better understood in a different way (like supervised learning for early AlphaFold).
> "not all problems are best suited to RL. You know, you really have to find the problems which are, natively better understood in a different way."
*(sources: src_018)*

## Separate problem from solution
Separate the formal definition of intelligence (the RL problem) from the specific methods used to solve it (e.g., deep learning).
*(sources: src_020)*

## Update a Guess from a Guess
Use bootstrapping to reduce the variance of evaluations in problems with long-term consequences.
> "Bootstrapping is a general method for reducing the variance of an estimate, by updating a guess from a guess."
*(sources: src_052)*
