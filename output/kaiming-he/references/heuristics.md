# Heuristics and Rules of Thumb

These are Kaiming He's pithy rules of thumb and practical shortcuts for navigating complex machine learning problems.

## Condition vs. Output Dimensionality
In conditional generation, the condition (Y) is usually abstract and low-dimensional, while the output (X) is concrete and high-dimensional.
*(sources: src_012)*

## Generative over Discriminative for Multiple Truths
If a problem has multiple plausible correct answers (like robot trajectories or image generation), it should be modeled as a generative probability distribution rather than a single prediction.
*(sources: src_012)*

## Integral vs. Finite Sum Reality
In theory we want to do integrals, but in practice we can only do finite sums.
> "we want to do integration but what we are doing is still a finite sum."
*(sources: src_027)*

## Parametric Initialization for OPQ
If no other prior knowledge is available, use the parametric solution (Eigenvalue Allocation) to initialize the non-parametric iterative solution for space decomposition.
*(sources: src_031)*

## Predicting ANN Accuracy via Distortion
Evaluate quantization distortion directly to predict ANN search accuracy across different methods.
> "We empirically verify that the distortion is tightly correlated to the ANN search accuracy of different methods."
*(sources: src_031)*
