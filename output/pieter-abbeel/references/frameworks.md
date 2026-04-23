# Frameworks of Pieter Abbeel

These frameworks represent Pieter Abbeel's structured methodologies for solving complex problems in reinforcement learning, robotics, and real-world AI deployment.

## Domain Randomization
A method for training robust neural networks in simulation that can successfully deploy to the real world without requiring a perfect simulator.

**Steps:**
1. Build many versions of the simulator.
2. Randomize physical parameters (friction, mass, camera position) rather than trying to match reality.
3. Train a single neural network to control the robot across all simulators.
4. Deploy to the real world, which the network treats as just another variation.
*(sources: src_023, src_027)*

## Hindsight Experience Replay
A technique for training reinforcement learning agents in sparse-reward environments by pretending that whatever outcome the agent accidentally achieved was its intended goal.

**Steps:**
1. Allow the robot to attempt a task.
2. Observe the actual outcome (e.g., falling down).
3. Pretend the achieved outcome was the intended goal and reward the robot.
4. Internalize these 'accidental' skills to build a broad repertoire that makes learning the actual target task easier.
*(sources: src_023)*

## Bootstrapped Reinforcement Learning Deployment
A pragmatic pipeline for deploying AI agents in real-world scenarios where safety and time are critical constraints.

**Steps:**
1. Start with supervised learning and behavioral cloning where humans do the work.
2. Have the ML system match human actions and make suggestions.
3. Once highly capable, gradually fuse in reinforcement learning by providing actual achievement objectives.
*(sources: src_017)*

## Learning Reward from Preferences
A framework for solving the reward design problem by putting non-expert humans in the agent learning loop.

**Steps:**
1. Collect samples via interactions with the environment.
2. Collect human preferences by showing two segments and getting a binary label.
3. Optimize a reward model using cross entropy loss.
4. Optimize a policy using off-policy algorithms. Repeat.

> "Step 1. Collect samples via interactions with environment Step 2. Collect human preferences Step 3. Optimize a reward model using cross entropy loss Step 4. Optimize a policy using off-policy algorithms"
*(sources: src_027)*

## Model-Based RL via Meta Policy Optimization (MB-MPO)
A method to overcome model-bias and training instability in model-based RL by learning an adaptive policy over an ensemble of simulators.

**Steps:**
1. Collect data under current adaptive policies.
2. Learn an ENSEMBLE of K simulators from all past data.
3. Perform meta-policy optimization over the ENSEMBLE.
4. Generate new meta-policy and new adaptive policies.

> "for iter = 1, 2, … collect data under current adaptive policies, learn ENSEMBLE of K simulators from all past data, meta-policy optimization over ENSEMBLE"
*(sources: src_032)*
