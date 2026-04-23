This document outlines the core principles that drive Stuart Russell's approach to AI safety, value alignment, and regulation.

## Uncertainty in Objectives
AI systems must be designed with explicit uncertainty about their objectives to prevent catastrophic outcomes.

If a machine treats an objective as absolute truth, it will pursue it relentlessly even if it leads to disastrous unintended consequences. Uncertainty forces the machine to be deferential to humans, cautious, and open to correction or being switched off.

> "I propose a new model for AI development in which the machine’s uncertainty about the true objective leads to qualitatively new modes of behavior that are more robust, controllable, and deferential."
(sources: src_022, src_027, src_012, src_025, src_011)

## Burden of Proof on Developers
The onus of proving safety must be on the AI developers, enforced by strict regulatory red lines.

Developers should have to demonstrate with high confidence and formal arguments that their systems are safe before deployment. Difficulty of compliance is not a valid excuse for deploying unsafe systems, just as it isn't in aviation or nuclear power.

> "The key point here is that the onus of proof is on developers, not regulators, and the proof leads to high-confidence statements based on assumptions that can be checked and refined."
(sources: src_012, src_018, src_026)

## Provably Safe and Controllable AI
We must build AI systems with absolute mathematical guarantees of safety, or we should not build them at all.

Creating an entity more powerful than human beings without rigorous, cast-iron guarantees of safety will inevitably lead to a loss of human control and potential extinction. The stakes are too high for trial-and-error engineering.

> "we either build provably safe and controllable AI where we have absolute cast iron mathematical guarantee of safety or we have no AI at all"
(sources: src_017, src_014, src_020)

## Realization of Human Preferences
The sole purpose of an AI system should be the realization of human preferences, which it must learn through observation.

Because humans cannot perfectly specify their objectives upfront, machines must infer what we want by observing our choices, reading our literature, and updating their priors based on our actions, treating the true objective as a hidden variable.

> "The principle says that the machine’s only purpose is the realization of human preferences."
(sources: src_029, src_054, src_022)

## Safety by Design (Not Post-Hoc)
Safety must be built into the core mathematical foundation of AI from the start, not patched on after the fact.

Building an AI system first and then trying to figure out how to secure it is an impossible path. We do not understand the internal principles of operation of current AI systems, so post-hoc attempts to constrain their behavior inevitably fail.

> "Instead, we need to make safe AI. Safety should be built in by design."
(sources: src_011, src_018, src_026)
