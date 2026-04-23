# Frameworks of Jürgen Schmidhuber

These frameworks represent Schmidhuber's structural approaches to solving complex problems in artificial intelligence, sequence learning, and autonomous exploration.

## Artificial Curiosity (Adversarial Learning)
A framework for training an autonomous agent to explore its environment and build a world model from scratch by pitting two networks against each other.

**Steps:**
1. Create a 'world model' (prediction machine) that learns to predict environmental inputs given past actions.
2. Create a 'controller' (action selector) that generates actions.
3. Define the world model's error based on prediction accuracy.
4. Reward the controller proportionally to the error of the world model.
5. The controller is thus motivated to invent new experiments that lead to surprising data, forcing the world model to learn.

> "So I said okay let's just give the controller a reward that is proportional to the error of the model network. So suddenly the controller and the model of the world are fighting each other."
> *(sources: src_005, src_013, src_022, src_018)*

## Long Short-Term Memory (LSTM)
An architecture designed to solve complex sequence learning tasks that require bridging long time lags by preventing error decay.

**Steps:**
1. Identify the need to bridge long time lags in sequence data.
2. Use special units with constant error carousels to enforce constant error flow.
3. Implement multiplicative gate units to learn to open and close access to the constant error flow, protecting memory from irrelevant inputs.
4. Apply a gradient-based learning algorithm that is local in space and time.

> "Multiplicative gate units learn to open and close access to the constant error flow. LSTM is local in space and time."
> *(sources: src_033, src_040, src_015)*

## Upside Down Reinforcement Learning (UDRL)
A paradigm that transforms reinforcement learning into supervised learning by treating rewards as input commands.

**Steps:**
1. Provide rewards, time horizons, and desired future data as task-defining inputs.
2. Use supervised learning on past experience to map these inputs to actions.
3. Generalize to achieve goals by issuing specific input commands.

> "UDRL learns to interpret these input observations as commands, mapping them to actions (or action probabilities) through SL on past (possibly accidental) experience."
> *(sources: src_039)*

## Fast Weight Programmers (Linear Transformers)
A neural network architecture that rapidly adapts to incoming sequences while scaling linearly with compute, rather than quadratically.

**Steps:**
1. Train a 'slow network' via gradient descent to generate a 'key' and a 'value'.
2. Pass the key to the input side and the value to the output side of a separate 'fast network'.
3. Rapidly change the weights of the fast network using the outer product of the key and value.
4. Apply the fast network to incoming queries to minimize the error function.

> "there are two networks. There's a slow network and there's a fast network and the slow network how does it program the weights of the fast network which is then being applied to queries as they are coming in"
> *(sources: src_005)*

## Hierarchical RL with Subgoal Generators
A framework for solving complex RL problems by hierarchically decomposing them into easier subproblems using neural networks.

**Steps:**
1. Provide the RL machine with extra inputs defining a (start, goal) pair.
2. Train an evaluator NN to predict rewards/costs of going from start to goal.
3. Use an RNN-based subgoal generator to learn a sequence of cost-minimizing intermediate subgoals.
4. Use these subgoal sequences to achieve final goals.

> "An (R)NN-based subgoal generator also sees (start, goal), and uses (copies of) the evaluator NN to learn by gradient descent a sequence of cost-minimising intermediate subgoals."
> *(sources: src_023, src_022)*
