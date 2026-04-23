# Frameworks of Demis Hassabis

These frameworks represent the structured methodologies Demis Hassabis uses to evaluate problems, design AI systems, and scale technologies from theoretical research to real-world scientific breakthroughs.

## Criteria for a Suitable AI Problem
A three-step checklist for evaluating whether a real-world problem or scientific challenge is suitable for modern AI methods.
1. Ensure the problem can be couched as finding a path through a massively combinatorial search space.
2. Specify a clear objective function or metric to optimize or hill-climb against.
3. Ensure there is a lot of data available to learn the neural network model, or an accurate and efficient simulator to generate synthetic data.
> "What makes for a suitable problem for AI? Massive combinatorial search space. Clear objective function (metric) to optimise against. Either lots of data and/or an accurate and efficient simulator" (sources: src_012, src_038)

## Deep Reinforcement Learning (Model-Guided Search)
A framework for making massive combinatorial search spaces tractable by combining deep learning models with reinforcement learning.
1. Use deep learning to process raw data streams and learn a model of the environment.
2. Overlay a reinforcement learning system to determine actions that maximize a reward.
3. Use the deep learning model to predict future states, narrowing down the search space so the RL system only evaluates the most fruitful paths.
> "Finding the optimal solution in an enormous combinatorial space. Learn a model of that environment (from data or simulation). Use that model to guide a search according to an objective function" (sources: src_023, src_026, src_038)

## Tabula Rasa (Blank Slate) Learning
A method for discovering novel, optimal solutions by removing human-crafted knowledge and biases.
1. Remove all human heuristics and historical data.
2. Provide only the fundamental rules of the environment.
3. Allow the system to play randomly to create its own dataset.
4. Train successive versions via self-play until it surpasses expert performance.
(sources: src_016)

## DeepMind's AI Development Pipeline
A structured approach to scaling AI capabilities from theoretical research to real-world products.
1. Start with a fundamental research question.
2. Look to neuroscience for inspiration and validation.
3. Implement concepts in machine learning to build a practical prototype (e.g., playing Atari).
4. Scale the system and interface it with real-world products.
> "You start with the research question and find that answer. Then we do some major neuroscience and then we look at it in machine learning and we implement a practical system... and then that’s ready to scale." (sources: src_033)

## In Silico Drug Discovery Pipeline
A framework for developing pharmaceuticals by maximizing computational search before physical lab validation.
1. Predict 3D protein structure.
2. Identify functional surface targets.
3. Design binding compounds.
4. Perform virtual screens for toxicity.
5. Iteratively modify in silico.
6. Validate final compounds in a wet lab.
(sources: src_016)

## Targeted Data Gathering via Frontier Modeling
Using cutting-edge AI models to identify exactly what expensive experimental data needs to be collected.
1. Build proprietary models pushing the limits of possibility.
2. Evaluate where the system underperforms.
3. Deduce that underperformance is caused by specific missing data.
4. Commission that specific experimental data to fill the gaps.
> "you see where does that system overall perform well where does it not perform well and then usually where it doesn't perform well that's because you need more data" (sources: src_036)
