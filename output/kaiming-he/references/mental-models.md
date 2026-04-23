# Mental Models of Kaiming He

These mental models illustrate how Kaiming He conceptualizes problems, draws analogies, and reframes complex systems into simpler, solvable abstractions.

## Residual vs. Unreferenced Functions
Viewing network layers not as learning a complete mapping from scratch, but as learning a residual (a delta or adjustment) with reference to the layer's input.

**Details**: This mental shift allows networks to be scaled to extreme depths (e.g., 152 layers) while remaining easy to optimize and maintaining lower complexity.
> "We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions."
*(sources: src_042)*

## The Abstraction Stack
Viewing AI progress as a stack of increasingly complex building blocks, where each era's final product becomes the next era's primitive component.

**Details**: Layers (ReLU, Softmax) built Deep Neural Networks. Deep Neural Networks build Generative Models. Generative Models build Reasoning Agents.
*(sources: src_012)*

## The Pre-AlexNet Analogy for Generative Models
Viewing the current paradigm of training diffusion and autoregressive models as analogous to the pre-2012 era of computer vision.

**Details**: Just as researchers used to train deep networks one layer at a time (e.g., denoising autoencoders) before AlexNet popularized end-to-end backpropagation, today's generative models are trained one time-step at a time rather than optimizing the full multi-step inference trajectory.
> "today's most successful genative models are conceptually a kind of layer wise training if we compare it with um the classification models um before after uh the Alex net area."
*(sources: src_027)*

## Instantaneous vs. Average Velocity
Borrowing from physics, instantaneous velocity only describes the tangent direction at a single point in time, whereas average velocity is required for large steps.

**Details**: To take large steps (like one-step generation from noise to image), one must use average velocity, which characterizes the total displacement between a starting point and an end point, rather than following hundreds of tiny instantaneous tangents.
*(sources: src_027)*

## AI as a Common Language
Viewing artificial intelligence methodologies as a universal translator that bridges disparate scientific disciplines.

**Details**: A computer scientist and a biologist might not understand each other's core research, but they can sit together and use deep learning and neural network models as a shared framework to discuss and solve problems.
> "In this sense, these AI tools are like a common language between these scientific areas: the machine learning tools ‘translate’ their terminology and concepts into terms that I can understand"
*(sources: src_039)*

## Vector Quantization as Constrained Optimization
Viewing various Approximate Nearest Neighbor (ANN) methods not as fundamentally different algorithms, but as the exact same optimization problem subject to different structural constraints.

**Details**: For example, k-means has no constraints, Product Quantization constrains codewords to a Cartesian product of sub-codebooks, and Iterative Quantization constrains codewords to the vertices of a rotating hyper-cube.
> "The quantization distortion is a common objective function among the different methods studied. We can treat the specific configuration of each method as the constraints when optimizing the common objective function"
*(sources: src_031)*

## Discriminative Tasks as Generative Tasks
Reframing traditional classification (predicting a fixed label) as conditional generation (generating text conditioned on an image).

**Details**: Instead of a closed-vocabulary classifier outputting 'bird', a generative model can output 'flamingo' or 'red color', enabling open-vocabulary recognition and rich image captioning.
*(sources: src_012)*

## Neural ODEs as ResNets
The realization that while Neural ODEs are theoretically formulated as continuous integration over time, practical computational constraints force them to be implemented as finite sums, making them conceptually identical to ResNets.

**Details**: When building a Neural ODE to solve an integral, the actual operation performed by the computer is a finite sum addition, mirroring the discrete time operation of a ResNet.
> "we want to do integration but what we are doing is still a finite sum."
*(sources: src_027)*
