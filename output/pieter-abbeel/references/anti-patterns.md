# Anti-Patterns Pieter Abbeel Pushes Against

These are the practices, assumptions, and methodologies that Pieter Abbeel explicitly warns against when developing and deploying AI and robotic systems.

## Hard-Coding Rules and Assumptions
Building assumptions or 'if-then-else' statements directly into AI systems to solve a single problem.

**Why it fails:** The real world has too many exceptions. Adding rules requires adding endless exceptions, which eventually makes the system unwieldy, fragile, and incapable of generalizing to unforeseen situations.
> "Once you start putting in rules, then you have to put, another 'if then else', another 'if then else', and at some point, things become unwieldy."
*(sources: src_010, src_023)*

## Perfecting the Simulator
Trying to perfectly match a simulation to reality for Sim2Real transfer.

**Why it fails:** It is typically impossible to get a perfect match. If the simulation is even slightly off, a neural network trained purely in that simulation will likely fail when deployed to the real robot. Randomization is a better approach.
*(sources: src_023, src_032)*

## Deploying Pure RL from Scratch
Deploying pure reinforcement learning from scratch in real-world autonomous systems.

**Why it fails:** It requires negative examples (like accidents or failures) to learn, making it highly dangerous and time-consuming before the system does anything useful.
> "Very few things more fun to watch than a reinforcement learning robot starting from nothing and inventing things. But it's just time consuming and it's not always safe."
*(sources: src_017)*

## Manual Reward Design for Complex Tasks
Relying on manually designed reward functions for complex, nuanced tasks.

**Why it fails:** It is hard to define a comprehensive reward for tasks like cooking, which easily leads to 'reward exploitation' where the agent finds unintended loopholes to maximize its score without solving the actual task.
*(sources: src_027)*

## Evaluating AI Solely by Math Complexity
Judging the value of AI research solely by its mathematical complexity rather than its real-world utility.

**Why it fails:** This disconnects the research from actual real-world impact and the practical change the work can make.
> "...to really try to see the connection from what you're working on to what impact they can really have, what change it can make rather than what's the math that happened to be in your work."
*(sources: src_017)*

## Ignoring the Perception-Action Loop
Assuming the supervised learning paradigm applies directly to robotics.

**Why it fails:** Supervised learning relies on the assumption that one decision does not affect the next request. In robotics, every action changes the subsequent state, requiring reinforcement learning to handle the continuous loop.
*(sources: src_027)*
