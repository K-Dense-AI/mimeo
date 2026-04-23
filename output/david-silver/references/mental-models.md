This document outlines the mental models David Silver uses to understand intelligence, learning, and the trajectory of AI development.

## Fossil Fuels vs. Sustainable Energy

A metaphor for AI training data: human data is like fossil fuels, while reinforcement learning is like sustainable energy.

Human data on the internet is cheap to exploit initially and provides a massive head start, but it is finite and running out. Experience (interaction with the world via RL) is like renewable energy: it allows an agent to keep generating data and learning forever with no limit.
*(sources: src_014, src_013, src_019)*

## Games as Microcosms

Viewing games not as mere entertainment, but as crystallized, simplified versions of reality used to test general intelligence.

Testing AI in the real physical world (like robotics) is slow. Games possess simple rules but vast emergent complexity, serving as perfect, fast-iterating laboratories for understanding how minds learn to achieve goals.

> "I think it's really important you know we're always trying to find like microcosms of the world that allow you to kind of um do research on important aspects of the world without having to do you know really build a robot"
*(sources: src_007, src_004)*

## The Cake Recipe Grounding Metaphor

A metaphor to distinguish true environmental grounding from human feedback.

True grounding is baking a cake and tasting it to see if it's good (environmental feedback). Human feedback (RLHF) is just a human looking at the recipe and guessing if it will be good. If an AI suggests a bizarre recipe, a human rater might reject it, but actual testing might reveal a novel, delicious cake.
*(sources: src_013)*

## The Shallow vs. Deep Problem of AI

Distinguishing between distilling existing knowledge (shallow) and agents learning for themselves (deep).

The 'shallow problem' is taking all existing human knowledge and putting it into an agent (which LLMs do well). The 'deep problem' is how an agent can adapt, acquire new knowledge directly from experience, and discover things humans don't know.

> "The shallow problem is basically you know how can you distill all the knowledge that's already out there into an agent."
*(sources: src_014)*

## Learning vs. Planning

A lens for distinguishing how an agent improves its behavior based on its access to the environment's rules.

Learning is trial-and-error in an unknown world; planning is internal look-ahead search in a perfectly known world.

> "in RL the environment is unknown in planning the environment is known"
*(sources: src_015, src_052)*

## The Value Function as an Oscilloscope

The value function acts as a real-time monitor of how well the agent is doing at any given moment, predicting future success based on the current state.

For example, in a video game, when a high-value target appears, the agent's value function spikes because it predicts a large future reward.

> "this thing is like it's a cillos scope of how well it's doing at any given moment in time it can be used to make decisions"
*(sources: src_015)*

## High-Dimensional Escapes

The intuition that in extremely high-dimensional spaces, what appears to be a local optimum usually has an escape route.

This explains why deep learning continues to perform well and optimize effectively. In massive neural networks, there is almost always another dimension that provides a pathway to continue learning and improving, preventing the system from getting permanently stuck.

> "...in high dimensions, when we make really big neural nets, there's always a way out and there's a way to go even lower."
*(sources: src_020)*
