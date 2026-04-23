# Frameworks of Yann LeCun

LeCun's frameworks provide architectural blueprints for building systems that can learn representations, predict the future, and plan actions without falling victim to the inefficiencies of generative pixel prediction or pure reinforcement learning.

## Joint Embedding Predictive Architecture (JEPA)
An architecture for building predictive world models that handle uncertainty by making predictions entirely in an abstract representation space, rather than generating pixel-level reconstructions.

**Steps:**
1. Take two different views or corrupted versions of the same scene.
2. Pass the inputs through an encoder to get abstract representations.
3. Train a predictor to predict the representation of the complete image from the corrupted one.
4. Apply a mechanism to prevent representation collapse (e.g., variance maximization).
5. Freeze the encoder and train a simple classifier or action-conditioned predictor on top.
*(sources: src_023, src_007, src_019, src_024, src_011, src_003)*

## Objective-Driven AI Architecture (Inference by Optimization)
An architecture for building agentic systems that plan complex action sequences (System 2 thinking) to accomplish new tasks in the physical world.

**Steps:**
1. Observe the world to extract an abstract representation of the initial state.
2. Propose a hypothesized action sequence.
3. Feed the state and actions into a World Model to predict the future state.
4. Pass the predicted state into a task objective function and safety guardrails to calculate a penalty.
5. Use optimization to select the action sequence that minimizes the objective.

> "The inference procedure is by optimization the system finds an action sequence that minimizes this uh objective function."
*(sources: src_003, src_011)*

## Energy-Based Learning (EBM)
A theoretical framework that views learning as shaping a topographical energy landscape, where correct configurations are assigned low energy and incorrect ones are assigned high energy. It bypasses intractable probabilistic normalization.

**Steps:**
1. Define an energy function for the model.
2. Perform inference by searching for output variables that minimize the energy function.
3. Perform learning by shaping the energy function so desired configurations sit in low-energy valleys.

> "Inference in EBMs consists in searching for the value of the output variables that minimize an energy function. Learning consists in shaping that energy function in such a way that desired configuration have lower energy than undesired ones."
*(sources: src_062, src_007)*

## Convolutional Neural Networks (ConvNets)
A deep learning architecture designed to process data that comes in the form of multiple arrays with local correlations and location-invariant statistics (e.g., images, video).

Relies on four key ideas: local connections (units connected to local patches), shared weights (detecting the same pattern across the array), pooling (merging semantically similar features for shift invariance), and the use of many layers to build a compositional hierarchy.

> "There are four key ideas behind ConvNets that take advantage of the properties of natural signals: local connections, shared weights, pooling and the use of many layers."
*(sources: src_042)*
