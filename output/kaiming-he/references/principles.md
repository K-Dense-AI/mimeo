# Core Principles of Kaiming He

These principles form the foundation of Kaiming He's approach to deep learning architecture, optimization, and the broader role of AI in science. They serve as both core beliefs and practical decision rules.

## Residual Learning
Network layers should learn residual functions referenced to their inputs rather than unreferenced functions.

**Rationale**: Without a structural change, adding layers makes optimization harder rather than improving accuracy. By reformulating layers to learn a residual (a delta or adjustment), deep networks become easier to optimize and can successfully gain accuracy from considerably increased depth.
> "We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions."
*(sources: src_042)*

## Depth is Central to Representation
The depth of neural network representations is of central importance for visual recognition tasks.

**Rationale**: Extremely deep representations yield massive improvements in object detection and classification tasks, driving the need for architectures like ResNet that can scale depth without degrading trainability.
> "The depth of representations is of central importance for many visual recognition tasks."
*(sources: src_042)*

## Activation-Aware Weight Initialization (He Initialization)
Weight initialization must explicitly account for the specific activation function being used to maintain constant variance across layers.

**Rationale**: If the variance of forward and backward signals is not maintained, deep networks suffer from exploding or vanishing gradients. Previous methods assumed linear activations, which fails for non-linear functions like ReLU. A robust initialization tailored to rectifiers enables training extremely deep models directly from scratch.
> "Second, we derive a robust initialization method that particularly considers the rectifier nonlinearities. This method enables us to train extremely deep rectified models directly from scratch."
*(sources: src_029, src_007, src_021)*

## Generative Models as Universal Solvers
Almost any real-world problem can be formulated as a generative model by framing it as a conditional distribution.

**Rationale**: By viewing problems as conditional distributions where you generate an output X based on a condition Y, you can apply generative models to anything from image creation to protein design and robotics, because there are no strict constraints on what X and Y can be.
> "in my opinion actually there is no any constraints or requirements about what can be X or what can be Y. so they conceptually they can be anything so that means we can use generative models to solve many kinds of real world problems"
*(sources: src_012)*

## Generative Modeling as Distribution Mapping
Generative modeling is fundamentally harder than discriminative modeling because it maps entire distributions, not just instances.

**Rationale**: Supervised learning maps paired inputs to outputs. Generative modeling is an unsupervised problem that must figure out how to map a simple noise distribution to a complex data distribution without explicit instance-to-instance pairing.
*(sources: src_012)*

## Generative Models as New Building Blocks
Generative models are the next level of abstraction in AI, serving as foundational primitives for higher-level systems.

**Rationale**: Just as individual layers (like ReLU or convolutions) were the building blocks for deep neural networks a decade ago, generative models are now the foundational abstractions used to build higher-level reasoning and agentic systems.
*(sources: src_012)*

## Recognition and Generation are Symmetrical
Recognition and generation are two sides of the same coin.

**Rationale**: Recognition is an abstraction process that flows from a complex data manifold to a simple embedding/label manifold. Generation is the exact reverse, flowing from an unstructured embedding (noise) to concretize a data point.
> "the problem of recognition and the problem of generation are just the uh two sides of the same coin."
*(sources: src_027)*

## The Need for End-to-End Generative Training
Today's generative models are conceptually trained layer-wise, lacking true end-to-end optimization.

**Rationale**: Models like diffusion or autoregressive networks have multi-step computational graphs at inference time, but during training, they only optimize one time step (or token) at a time. This mirrors the pre-AlexNet era of training deep networks one layer at a time.
> "today's most successful genative models are conceptually a kind of layer wise training if we compare it with um the classification models um before after uh the Alex net area."
*(sources: src_027)*

## AI as a Common Scientific Language
AI acts as a common language that breaks down the walls between disparate scientific disciplines.

**Rationale**: Machine learning tools translate domain-specific terminology into understandable concepts, allowing researchers from vastly different fields (e.g., biology, physics, computer science) to share tools, experiences, and solutions.
> "In this sense, these AI tools are like a common language between these scientific areas: the machine learning tools ‘translate’ their terminology and concepts into terms that I can understand"
*(sources: src_039)*

## Reciprocal Relationship of AI and Science
Science and AI evolve together; they should not be treated as isolated subjects.

**Rationale**: While AI helps scientists solve domain-specific problems, scientists provide new challenges that evolve AI tools. Furthermore, many foundational AI tools were directly inspired by scientific observations (e.g., neural networks from biology, diffusion from physics).
> "Science and AI are not isolated subjects. We have been approaching the same goal from different perspectives, and now we are getting together."
*(sources: src_039)*

## Simplicity in Complexity
Complex visual problems should be solved using simple and intuitive methods.

**Rationale**: Despite the intrinsic complexity of visual perception, the most effective deep learning solutions for tasks like object detection and segmentation are those designed to be straightforward and intuitive.
> "enabling deep learning to solve complex object detection and segmentation problems in simple and intuitive ways."
*(sources: src_005)*

## Quantization Distortion as a Universal Objective
Quantization distortion is a universal objective function that tightly correlates with Approximate Nearest Neighbor (ANN) search accuracy.

**Rationale**: Different ANN methods (like k-means, PQ, and ITQ) can all be viewed as optimizing the exact same distortion objective, just subject to different structural constraints. Stricter constraints inherently lead to higher quantization distortion.
> "The quantization distortion is a common objective function among the different methods studied. We can treat the specific configuration of each method as the constraints when optimizing the common objective function."
*(sources: src_031)*

## Optimal Space Decomposition
Optimal space decomposition in product quantization requires subspaces to be mutually independent and have balanced variances.

**Rationale**: Under a Gaussian assumption, the theoretical lower bound of quantization distortion is minimized when Fischer's inequality (independence) and the AM-GM inequality (balanced variances) are simultaneously satisfied.
> "We theoretically prove that this lower bound is minimized when (i) the subspaces are mutually independent, and simultaneously (ii) the vectors have balanced variances in all subspaces."
*(sources: src_031)*
