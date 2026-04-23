This document catalogs Ian Goodfellow's practical heuristics and rules of thumb for machine learning engineering and research.

## Mini-Batch Features for Mode Collapse
To partially fix mode collapse in GANs, add nearest-neighbor features constructed from the current minibatch to the discriminator.
(sources: src_017, src_039)

## Non-Saturating Gradient Trick
Early in learning, train the generator to maximize log D(G(z)) instead of minimizing log(1 - D(G(z))) to prevent gradient saturation.
(sources: src_007, src_039)

## Worst-Case Robustness Analysis
To make a system truly robust, perform worst-case analysis by testing it against adversarial examples, not just average-case data.
(sources: src_022, src_015)

## Alternate Optimization Steps
Alternate between k steps of optimizing the discriminator and one step of optimizing the generator to keep the discriminator near its optimal solution.
> Instead, we alternate between k steps of optimizing D and one step of optimizing G. This results in D being maintained near its optimal solution, so long as G changes slowly enough.
(sources: src_007)

## Ensemble Transferability
Generate adversarial examples using an ensemble of models to drastically improve the chance they will transfer to an unknown target model. If an adversarial example successfully fools every member of an ensemble of five models, it has essentially a 100% chance of fooling a new, unseen sixth model.
(sources: src_015)

## Evaluate 'Deepness' by Consecutive Steps
To evaluate if a model is 'deep', check if it involves learning parameters of more than one consecutive step.
> I would say deep learning is any kind of machine learning that involves learning parameters of more than one consecutive step.
(sources: src_009)

## Hardware-First Problem Solving
Calculate hardware constraints (pixels, batch size, GPU memory) before attempting brute-force programming solutions. If limits are exceeded, use learned features instead of hand-coded rules.
> You're not going to be able to program your way out of this.
(sources: src_001)

## L-infinity Constraints for Perturbations
Use L-infinity constraints (bounding max change per pixel) rather than L2 constraints to prevent accidentally changing the true class of an image during adversarial attacks.
(sources: src_015)

## Latent Space Arithmetic
Do arithmetic in the latent space (Z vectors) to manipulate semantic features of generated images. For example: man with glasses - man + woman = woman with glasses.
(sources: src_039)

## Out-of-Band Authentication
To prove something is real, you must step back to a separate, out-of-band channel (like cryptographic signing) rather than relying on the content itself.
> You can simulate almost anything and so you have to really step back to a separate channel to prove that something is real.
(sources: src_009)

## Safe Discriminator Optimization
In GANs, fully optimizing the discriminator while holding the generator constant is safe, whereas the reverse causes mode collapse.
(sources: src_017)
