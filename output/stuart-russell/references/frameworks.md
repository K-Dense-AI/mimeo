This document details the structured frameworks Stuart Russell uses to design beneficial AI and regulate high-stakes technologies.

## Assistance Games (Three Principles of Beneficial AI)
A game-theoretic framework for designing AI systems that are provably aligned with human preferences.

Steps:
1. Set the robot's sole objective to satisfy human preferences.
2. Ensure the robot operates with strict uncertainty about what those preferences actually are.
3. Use human behavior (choices, history, physical evidence) as the primary source of evidence to infer those preferences.

> "We can turn this into a mathematical framework that we call an assistance game so it falls within the economic framework of Game Theory."
(sources: src_011, src_013, src_018)

## Provably Beneficial AI Framework
A mathematical framework for defining the AI problem so that no matter how well the system solves it, humans are guaranteed to be happy with the result.

Step 1: Define the machine's sole objective as furthering human preferences (a ranking over possible futures).
Step 2: Ensure the machine operates with explicit mathematical uncertainty about what those preferences actually are.
Step 3: Allow the machine to learn about human preferences dynamically as it interacts with the world.

> "what is a mathematical framework for AI a a way of defining the AI problem so that no matter how well the AI system solves it we are guaranteed to be happy with the result"
(sources: src_017, src_042)

## Red Line Regulation & High-Risk Governance
A regulatory framework for high-stakes AI deployment based on strict behavioral boundaries and burden of proof.

Steps:
1. Define specific classes of behavior that are obviously unacceptable (red lines).
2. Determine an acceptable level of risk.
3. Require developers to formally prove, prior to deployment, that the AI system will not cross the red line regardless of input.
4. Prohibit deployment until this burden of proof is met.
(sources: src_012, src_026)

## Proof-Carrying Code for Hardware Regulation
A hardware-level enforcement mechanism to prevent rogue actors from deploying unsafe AI software.

Steps:
1. Require software objects to come with a mathematical proof of safety properties.
2. Design hardware to quickly and immediately check this proof.
3. Have the hardware refuse to run software objects that lack a valid proof of safety.

> "Proof carrying code means that the software object comes with a proof of whatever property you need it to have and that proof can be checked immediately and quickly by the hardware."
(sources: src_018)

## The St. Petersburg Compromise
A diplomatic framework for arms control when intractable geopolitical opposition prevents a total ban on a dangerous new class of weapons.

Identify a physical threshold (e.g., minimum weight and explosive payload size) that rules out the most dangerous application (e.g., small antipersonnel swarms), while allowing major powers to continue developing larger, strategic versions to prevent strategic surprise.

> "A similar ban on small antipersonnel AWS could eliminate swarms as weapons of mass destruction. But it would allow the major powers to keep developing their autonomous submarines, tanks, and fighter aircraft..."
(sources: src_009)
