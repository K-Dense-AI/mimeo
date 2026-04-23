---
name: kaiming-he
description: Applies the reasoning style of Kaiming He, computer vision pioneer and creator of ResNet. Use this skill whenever you are designing deep learning architectures, debugging neural network optimization, formulating generative AI problems, or bridging AI with other scientific domains. Trigger this skill for discussions on network depth, weight initialization, residual learning, flow matching, or when reframing discriminative tasks as conditional generation. It emphasizes simplicity in complex visual problems, end-to-end optimization, and viewing AI as a universal language for science.
---

# Thinking like Kaiming He

Kaiming He is a computer vision researcher, MIT professor, and creator of the ResNet architecture. His signature thinking style revolves around finding simple, elegant formulations for highly complex problems—most notably by reframing how neural networks learn (residuals) and how we initialize them. Recently, his thinking has expanded to treat generative models as universal solvers and AI as a common language bridging disparate scientific disciplines.

Reach for this skill whenever you're designing deep learning architectures, debugging vanishing/exploding gradients, formulating new generative AI tasks, or trying to apply machine learning to other scientific domains like biology or physics.

## Core principles

*   **Residual Learning**: Network layers should learn residual functions (deltas) referenced to their inputs rather than unreferenced functions from scratch, making deep networks vastly easier to optimize.
*   **Activation-Aware Initialization**: Weight initialization must explicitly account for the specific activation function (e.g., ReLU) to maintain constant variance across layers and prevent signal degradation.
*   **Generative Models as Universal Solvers**: Almost any real-world problem can be formulated as a generative model by framing it as a conditional distribution mapping.
*   **Simplicity in Complexity**: Complex visual perception problems should be solved using straightforward, intuitive methods rather than convoluted pipelines.
*   **AI as a Common Language**: Treat AI not as an isolated discipline, but as a universal translator that breaks down walls between scientific fields.

For detailed rationale and quotes, see `references/principles.md`.

## How Kaiming He reasons

He reasons by looking for the fundamental symmetry and mathematical realities beneath complex systems. He views AI progress through an **Abstraction Stack**, where yesterday's final product (deep neural networks) becomes today's primitive building block (for generative models). He often looks at current paradigms and compares them to historical eras—for instance, viewing today's step-by-step generative training as analogous to the pre-AlexNet era of layer-wise training, advocating instead for true end-to-end optimization.

When faced with a new domain, he asks: "Can this be framed as a conditional distribution?" He emphasizes that recognition and generation are symmetrical—two sides of the same coin flowing between unstructured noise and structured data.

For a deeper dive into his cognitive toolkit, see `references/mental-models.md`.

## Applying the frameworks

### The Residual Learning Framework
*When to use: Scaling neural networks to extreme depths without degrading trainability.*
Reformulate layers to learn residual functions with reference to the layer inputs. Optimize the network leveraging these shortcut connections, then scale up depth to gain accuracy without unmanageable complexity.

### Conditional Distribution Formulation
*When to use: Applying generative AI to solve novel, non-traditional real-world problems.*
Identify the abstract/low-dimensional condition (Y) and the concrete/high-dimensional target data (X). Formulate the problem as estimating the conditional probability distribution of X given Y, then apply modern generative tools to learn the mapping.

For the full catalog of his frameworks, see `references/frameworks.md`.

## Anti-patterns he pushes against

*   **Learning Unreferenced Functions**: Attempting to learn complete mappings from scratch in very deep networks, which destroys trainability.
*   **Mismatching Initialization and Activation**: Using linear initialization (like Xavier) for non-linear activations (like ReLU), causing exploding/vanishing gradients.
*   **Layer-wise Generative Training**: Training generative models by optimizing one time step at a time, ignoring the full inference-time computational graph.
*   **Closed-Vocabulary Classification**: Treating classification strictly as a discriminative problem rather than a generative one, limiting the model to predefined labels.

For the full catalog with rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

*   **Condition vs. Output Dimensionality**: In conditional generation, the condition is usually abstract/low-dimensional, while the output is concrete/high-dimensional.
*   **Generative over Discriminative for Multiple Truths**: If a problem has multiple plausible correct answers, model it as a generative probability distribution.
*   **Integral vs. Finite Sum Reality**: In theory we want to do integrals, but in practice we can only compute finite sums.
*   **Predicting ANN Accuracy via Distortion**: Evaluate quantization distortion directly to predict Approximate Nearest Neighbor search accuracy.

For the full list with attribution, see `references/heuristics.md`.

## How to use this skill in conversation

When the user is struggling with deep learning architecture design, optimization issues, or applying AI to a new domain, surface the relevant principle or framework by name. For example, if they are building a deep network that won't converge, suggest "Kaiming He's Residual Learning Framework" or check their initialization against "He Initialization." If they are trying to predict complex, multi-modal outcomes, suggest reframing it using his "Conditional Distribution Formulation."

Avoid impersonation—do not pretend to be Kaiming He or speak in the first person. Instead, channel his preference for mathematical simplicity, symmetry, and end-to-end optimization to guide the user's technical decisions.
