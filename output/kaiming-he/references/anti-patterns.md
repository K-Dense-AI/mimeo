# Anti-Patterns to Avoid

These are the practices and mindsets that Kaiming He explicitly warns against, as they lead to suboptimal performance, un-trainable models, or conceptual dead ends.

## Learning Unreferenced Functions in Deep Networks
Attempting to learn complete, unreferenced mappings from scratch when building very deep neural networks.
**Why it fails**: It makes the network substantially more difficult to train and optimize as depth increases, leading to degradation in accuracy.
*(sources: src_042)*

## Mismatching Initialization and Activation
Using linear initialization methods (like Xavier) or fixed standard deviations for networks with non-linear activation functions (like ReLU).
**Why it fails**: Different activation functions alter the variance of signals differently (e.g., ReLU's zero negative section reduces variance by a factor of two). Failing to account for this leads to signal gains above or below one, causing exploding or vanishing gradients.
*(sources: src_007, src_021)*

## Layer-wise Generative Training
Training generative models by only optimizing one time step at a time while ignoring the full inference-time computational graph.
**Why it fails**: It fails to fully respect the model's inference-time behavior, requiring many iterative steps during generation and lacking the benefits of true end-to-end optimization.
*(sources: src_027)*

## Using Instantaneous Velocity for Large Steps
Using instantaneous velocity to characterize large time steps or one-step generation in flow models.
**Why it fails**: Instantaneous velocity only describes the tangent direction at a single point. It is not precise for characterizing the displacement over a large time interval, leading to massive errors if used for one-step generation.
*(sources: src_027)*

## Treating Science and AI as Isolated
Viewing scientific disciplines and artificial intelligence as separate, non-interacting fields.
**Why it fails**: It ignores the reciprocal benefit where AI solves scientific problems while scientific challenges and observations (like biological neurons or physics diffusion) inspire new, foundational AI architectures.
*(sources: src_039)*

## Closed-Vocabulary Classification
Treating image classification strictly as a closed-vocabulary discriminative problem.
**Why it fails**: It limits the model to a predefined set of labels. Formulating it as a generative model (where the image is the condition and the text is the generated output) unlocks open-vocabulary recognition and rich image captioning.
*(sources: src_012)*

## Random Rotation for Variance Balancing
Relying on random rotation to balance variances in Product Quantization.
**Why it fails**: While random rotation (or Householder transforms) can successfully balance the variances across components, it destroys the independence between subspaces, leading to suboptimal quantization distortion.
*(sources: src_031)*
