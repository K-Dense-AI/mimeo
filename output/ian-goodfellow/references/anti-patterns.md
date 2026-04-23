This document outlines the practices and assumptions Ian Goodfellow explicitly warns against in machine learning and AI security.

## Hard-Coding Knowledge / Manual Feature Engineering
Attempting to hard-code knowledge about the world in formal languages or manually design features for complex tasks. People struggle to devise formal rules with enough complexity to accurately describe the real world, leading to unwieldy processes and brittle systems that fail on edge cases. It is consistently outperformed by neural networks allowed to figure out representations on their own.
(sources: src_033, src_043, src_001)

## Mode Collapse (The 'Helvetica Scenario')
Training the generator too much without updating the discriminator causes it to collapse too many noise values to the same output. The generator loses the diversity needed to accurately model the data distribution, mapping all inputs to the single output that the discriminator currently considers most likely to be real.
(sources: src_007, src_039)

## Chasing SOTA in Textbooks
Trying to document the absolute latest state-of-the-art benchmarks in reference materials for fast-moving fields. The specific architectures and performance levels become outdated quickly; it is pointless to summarize exactly which architecture got which level of performance.
(sources: src_022)

## Deploying Frozen Models
Deploying frozen, static machine learning models in production. Static models are 'sitting ducks'. If a model always outputs the same answer for the same input, adversaries can simply probe it until they find a mistake, and then exploit that same mistake repeatedly.
(sources: src_009)

## Generator Over-Optimization
Fully optimizing the generator while holding the discriminator constant. It results in mapping all points to the argmax of the discriminator, leading to severe mode collapse.
(sources: src_017)

## Naive Bias Removal
Attempting to achieve algorithmic fairness by simply removing sensitive variables (like race or gender) from the training data. The model can discover other characteristics in the data that are correlated with the sensitive variables and use them as intermediaries to replicate the human biases present in the training data.
(sources: src_005, src_009)

## Relying on Fake Detectors
Relying on 'fake detectors' to combat deepfakes and generated media. If an adversary successfully fools your fake detector, the detector's false validation makes the fake image even more credible than if the detector never existed.
(sources: src_009)

## Saturating GAN Objectives
Using the standard minimax objective early in GAN training. Early in learning, the generator is poor and the discriminator can reject samples with high confidence. This causes the objective to saturate, failing to provide sufficient gradient for the generator to learn.
(sources: src_017)

## Security Through Obscurity
Relying on hidden model parameters for security. Attackers can perform 'model theft' by observing the inputs and outputs of a target model to train a substitute model, which they can then use to generate adversarial examples that successfully transfer to the hidden target.
(sources: src_015)

## The Overfitting Fallacy
Assuming adversarial examples are caused by the model overfitting to the training data. If adversarial examples were just random artifacts of overfitting, they would be unique to each model. Instead, they transfer reliably across different models, datasets, and architectures, proving the root cause is the models' linear nature.
(sources: src_015)

## Using Mean Squared Error for Generative Tasks
Using Mean Squared Error (MSE) for generative tasks with multiple valid outcomes. MSE penalizes the model for picking one valid option over another, causing it to average all possible futures together. This results in blurry images or disappearing features.
(sources: src_039)
