This document outlines the specific frameworks and methodologies Ian Goodfellow uses to design, train, and evaluate machine learning systems.

## Generative Adversarial Networks (GAN) Training
A framework for estimating generative models via an adversarial process between a generator and a discriminator. 
1. Sample a minibatch of real data. 
2. Sample a minibatch of noise. 
3. Update the discriminator to maximize the probability of assigning correct labels to both real and fake samples. 
4. Update the generator to maximize the probability of the discriminator making a mistake. 
5. Alternate these steps.
> The training procedure for G is to maximize the probability of D making a mistake. This framework corresponds to a minimax two-player game.
(sources: src_007, src_020, src_039)

## Adversarial Feature Extraction for Fairness
A framework for removing sensitive variables or adapting to new domains using adversarial training. Train a feature extractor for the primary task while simultaneously training it to fool a secondary 'feature analyzer' player that tries to guess the sensitive variable (e.g., gender) from the extracted features.
> you have one player that's a feature extractor and another player that's a feature analyzer and you want to make sure that the feature analyzer is not able to guess the value of the sensitive variable that you're trying to keep private
(sources: src_009, src_005)

## Black-Box Transfer Attack (Model Theft)
A method to fool a remotely hosted target model without knowing its architecture, weights, or training algorithm. Send inputs to the target model and observe outputs. Use these pairs to reverse-engineer the parameters and train a substitute model. Generate adversarial examples against the substitute, then deploy them against the target model, relying on high transfer rates.
> After you have your own copy of the model you can make adverse early examples at full your model and then send those adversary examples back to the targeted model
(sources: src_015)

## Fast Gradient Sign Method (FGSM)
A fast, closed-form method to generate adversarial examples without iterative optimization. Linearize the cost of the neural network around the current input. Take the gradient of the cost with respect to the input, take the sign of the gradient at each pixel, and add a small constraint value (epsilon) times that sign to the input.
> we just take the gradient of the cost with respect to the input we take the sign of the gradient at each pixel and we add epsilon times that sign at the gradient to the input
(sources: src_015)

## Machine Learning Algorithm Decomposition
A method for analyzing and designing machine learning systems by breaking them into three distinct components. 
1. Define the model (how data and parameters make a prediction). 
2. Define the optimization algorithm (how parameters are updated, e.g., gradient descent). 
3. Define the dataset (how the world is represented).
(sources: src_009)

## Standardized Adversarial Benchmarking
A protocol for evaluating new adversarial attacks or defenses to ensure valid, comparable results. Implement your new method and test it against standard reference implementations of the strongest known attacks/defenses using a library like CleverHans. This isolates whether your method is actually effective or if the opposing method was just weak.
> using clever hunts for one side and your research project for the other side lets you know that you're comparing to the same standards as all of the other researchers
(sources: src_015)

## Writing for Rapidly Evolving Fields
A strategy for summarizing fast-moving technical fields in textbooks or reference guides. Focus on providing a high-level summary that gives readers the language and core concepts needed to understand the field. Acknowledge rapidly evolving areas without detailing the exact current best architectures, as specific performance metrics will quickly become outdated.
> But there isn't a lot of point in trying to summarize exactly which architecture in which learning approach got to which level of performance.
(sources: src_022)
