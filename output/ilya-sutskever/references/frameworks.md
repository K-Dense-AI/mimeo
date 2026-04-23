This document details the structured frameworks Ilya Sutskever uses to approach AI training, research direction, and long-term safety.

## Two-Stage AI Training (Pre-training + RLHF)
A methodology for building reliable and aligned AI assistants from raw data by separating world-model acquisition from behavioral alignment.
1. **Pre-training:** Train a large neural network to accurately predict the next word on vast amounts of internet text to learn a comprehensive world model.
2. **Alignment:** Apply fine-tuning and reinforcement learning from human and AI collaboration to communicate the desired behavior, guardrails, and intent to the model.
> "You can say that the pre training process, and you just train a language model, you want to learn everything about the world, then the reinforcement learning from human feedback. Now we care about the outputs."
(sources: src_015, src_020)

## Top-Down Research Taste
A framework for deciding which AI research directions to pursue and whether to persist through experimental failures.
1. Look for correct inspiration from the brain (e.g., neurons, distributed representation).
2. Ensure the idea possesses beauty, simplicity, and elegance.
3. Form a strong top-down belief based on these aesthetics.
4. Use this belief to sustain effort and keep debugging when initial experiments contradict you.
> "It's beauty, simplicity, elegance, correct inspiration from the brain. All of those things need to be present at the same time. The more they are present, the more confident you can be in a top-down belief."
(sources: src_035)

## Domain Randomization
A method for training an agent in an imperfect simulation with the goal of transferring its skills to the real, physical world.
1. Identify variables in the simulation that cannot be accurately measured (e.g., friction).
2. Randomize these values across a wide range during training.
3. Require the policy to solve the task regardless of the randomized values.
4. Deploy in the real world, treating reality as just another variation.
> "if there is something in your simulation which you can't measure you randomized it and you require your policy to be able to solve it for any value of the randomization"
(sources: src_019)

## The Three Challenges of Superintelligence
A categorization of the long-term risks of highly capable AI that must be solved sequentially.
1. Solve the scientific problem of alignment to contain the vast power of the system.
2. Prevent misuse by 'humans of interests' by having the superintelligence help solve the challenges it creates.
3. Navigate the long-term effects of natural selection on ideas and organizations, potentially via human-AI merging.
(sources: src_024)
