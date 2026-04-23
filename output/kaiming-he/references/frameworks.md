# Frameworks of Kaiming He

These frameworks represent Kaiming He's structured approaches to solving problems in deep learning, generative modeling, and optimization.

## Residual Learning Framework
A method for training substantially deeper neural networks by reformulating layers to learn residual functions.

**Steps**:
1. Reformulate layers to learn residual functions with reference to the layer inputs, rather than unreferenced functions.
2. Optimize the network, leveraging the fact that these residual connections make the deep network easier to train.
3. Scale up the depth of the network to gain accuracy without increasing complexity beyond manageable levels.

> "We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously."
*(sources: src_042)*

## Conditional Distribution Formulation
A framework for applying generative AI to solve novel real-world problems by framing them as conditional probability estimations.

**Steps**:
1. Identify the condition 'Y' (usually abstract, less informative, or lower-dimensional, such as a text prompt).
2. Identify the target data 'X' (usually concrete, higher-dimensional, such as a 3D protein structure).
3. Formulate the problem as estimating the conditional probability distribution of X given Y.
4. Apply modern generative modeling tools to learn this mapping.

> "we can just try to formulate all these real world problems as kind of conditional distribution problem and then we can try to apply the latest advance in generative models as a tool for this problem"
*(sources: src_012)*

## Mean Flows Algorithm
A framework for training generative models to perform one-step generation by learning average velocity rather than instantaneous velocity.

**Steps**:
1. Define a neural network to predict average velocity, conditioned on start and end times.
2. Sample data, time steps, and noise.
3. Interpolate between data and noise to compute instantaneous conditional velocity.
4. Compute the time derivative of velocity using a Jacobian Vector Product (JVP).
5. Modify the regression target using the mean flow identity.
6. Optimize using a conditional flow matching objective.

> "conceptually it's just two line modification of the original flow matching algorithm"
*(sources: src_027)*

## Optimized Product Quantization (OPQ)
A framework for optimizing product quantization codebooks and space decomposition to minimize quantization distortion.

**Non-parametric steps**:
1. Fix the space decomposition matrix R and optimize sub-codebooks via k-means.
2. Fix sub-codebooks and optimize R by solving the Orthogonal Procrustes problem using SVD.
3. Iterate until convergence.

**Parametric initialization (Eigenvalue Allocation)**:
Align data using PCA, sort eigenvalues, and sequentially allocate the largest available eigenvalue to the bucket with the minimum product of eigenvalues to form balanced, independent subspaces.

> "In the first solution, we iteratively solve two simpler sub-problems: solving for the space decomposition with the codewords fixed, and vice versa."
*(sources: src_031)*
