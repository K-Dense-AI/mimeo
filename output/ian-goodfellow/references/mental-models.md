This document captures the mental models Ian Goodfellow uses to conceptualize machine learning problems, spanning game theory, adversarial dynamics, and cognitive analogies.

## Optimization vs. Games (Minimax)
Shifting from traditional optimization (finding a single minimum) to game theory (finding a Nash equilibrium between competing networks). Traditional optimization seeks a single minimum for one cost function. A game involves multiple players controlling different parameters, each trying to minimize their own cost function, requiring the system to find an equilibrium (e.g., GANs, adversarial training).
> Finding Nash equilibria in high-dimensional, continuous, non-convex games is an important open research problem
(sources: src_015, src_017, src_022, src_021, src_005)

## Counterfeiters vs. Police
A metaphor for the adversarial training process in GANs. The generative model acts as a counterfeiter trying to create fake data that looks real, while the discriminative model acts as the police trying to distinguish real data from fakes. The competition forces both to improve until the fakes are perfect.
> The generative model can be thought of as analogous to a team of counterfeiters, trying to produce fake currency and use it without detection, while the discriminative model is analogous to the police, trying to detect the counterfeit currency.
(sources: src_007, src_039, src_043)

## Deep Learning as Sequential Programming
Viewing a neural network's architecture as a flowchart where depth equals sequential steps. Instead of viewing a deep layer as a 'grandmother cell' that recognizes a specific object, it is viewed as the Nth update in a program that is iteratively refining a state of understanding.
> I think of deep learning as basically learning programs that have more than one step.
(sources: src_033, src_009)

## Cooperative View of GANs
Viewing the discriminator not just as an adversary, but as a guide that helps the generator improve. Instead of viewing the generator and discriminator as purely adversarial enemies, view them as cooperating entities where the discriminator estimates the ratio of the data and model distributions to inform and guide the generator.
> A cooperative rather than adversarial view of GANs: the discriminator tries to estimate the ratio of the data and model distributions, and informs the generator of its estimate in order to guide its improvements.
(sources: src_017)

## Deliberate Practice
Viewing machine learning optimization through the lens of human psychology and expert coaching. Effective learning requires focusing on the most difficult subtasks and receiving expert feedback. In GANs, the discriminator acts as an expert coach, telling the generator exactly what it should have done instead of providing a generic error metric.
> rather than just training and lots and lots of training examples your training on the worst case inputs that are really hard for the model and in the case of generative adverts or networks you have an expert the discriminator coaching the generator
(sources: src_039)

## Factors of Variation
Thinking of observed data as being influenced by separate, unobserved sources or forces that need to be disentangled. When analyzing an image of a car, the factors of variation include the position of the car, its color, and the angle and brightness of the sun.
> It is not surprising that the choice of representation has an enormous effect on the performance of machine learning algorithms.
(sources: src_033)

## Machine Learning as Sherlock Holmes
Models can infer highly private, unstated attributes from seemingly innocuous public data. Much like Sherlock Holmes deducing a client's life story from minor clues like marks on their shoes, ML models can predict sensitive traits (like personality) better than friends or family simply by analyzing public social media activity.
> Machine learning is kind of like the modern-day version of Sherlock Holmes it is able to infer things that we don't realize we're broadcasting to the world
(sources: src_015)

## Optical Illusions as Human Adversarial Examples
The human visual system has specific vulnerabilities analogous to adversarial examples in machine learning. When asked if adversarial examples exist in the human brain, Goodfellow points to optical illusions (like concentric circles that look like intertwining spirals) as the human equivalent.
> a lot of people ask me if there are adversarial examples in the human brain and the short answer is yes we call them optical illusions
(sources: src_015)

## The Clever Hans Effect
ML models often maximize their objective by latching onto spurious correlations rather than learning true reality. Just as the horse Clever Hans appeared to do math but was actually reading audience reactions, ML models appear to classify images correctly until tested out-of-distribution with adversarial examples, revealing they rely on unintended side channels.
> we asked them to maximize the log likelihood of the training set labels and they find a way of doing that and it happens not to be one that corresponds very well to reality
(sources: src_015)
