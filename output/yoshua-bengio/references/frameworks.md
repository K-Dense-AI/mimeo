# Frameworks

Yoshua Bengio's frameworks provide structured approaches to designing safe AI, evaluating risks, and conducting deep learning research.

## Scientist AI Architecture
A safe-by-design framework for AI scientific discovery that separates world modeling, uncertainty quantification, and experimental design into strictly non-agentic components.
**Steps:**
1. Train a non-agentic neural network to model the world and generate theories.
2. Integrate a question-answering inference machine.
3. Ensure all components operate with explicit uncertainty quantification.
4. Sample experiments for Information Gain without giving the system autonomous agency.
> "It comprises a world model that generates theories to explain data and a question-answering inference machine. Both components operate with an explicit notion of uncertainty to mitigate the risks of overconfident predictions."
*(sources: src_010, src_051)*

## Capability-Specific Risk Assessment
A framework for evaluating the progress and potential dangers of advanced AI systems by tracking specific skills rather than general intelligence.
**Steps:**
1. Identify particular skills AIs are improving at.
2. Track the progress of those specific skills.
3. Evaluate how useful or beneficial the skill can be.
4. Assess how the skill could be misused or weaponized if control is lost.
5. Ensure capabilities do not exceed current technical and societal guardrails.
> "We should think of particular skills that AIs are you know becoming better at. Track those skills and for each of these we should ask the question you know how useful or beneficial it can be for for what purposes and also how it could be misused or if we do get loss of control how an AI could use it against us."
*(sources: src_023)*

## The Scientist AI Guardrail System
A system for mitigating the risks of untrusted AI agents by using a foundational, 'honest' AI to evaluate and veto dangerous actions.
**Steps:**
1. Build a foundational AI system with no objectives other than truthfulness.
2. Use this honest AI to evaluate the probability that a proposed action by an untrusted AI will cause harm.
3. Establish a human-defined threshold for acceptable risk.
4. Veto the untrusted AI's action if the predicted probability of harm exceeds the threshold.
> "For example, if you have an AI system that can tell you the probability that a particular action, maybe of an untrusted AI system, will cause harm... Then you could veto that action if the probability is above a threshold."
*(sources: src_024, src_029)*

## Debugging Neural Networks
A systematic approach to troubleshooting neural networks and ensuring proper optimization.
**Steps:**
1. Make experiments reproducible.
2. Train on a small dataset to verify the model can reach zero training error quickly.
3. Monitor error curves, weights, and gradients.
4. Vary capacity to observe underfitting/overfitting transitions.
5. Compare against simple baselines.
*(sources: src_002)*

## Toy Problem Experimentation
Accelerating the research cycle by reducing complex problems to simple, intuitive toy environments.
**Steps:**
1. Reduce the complex problem to a simple environment (like a programmable video game).
2. Run fast experiments that take hours instead of days.
3. Intuitively manipulate variables to understand fundamental principles.
4. Transfer the meta-learnings to real-world problems.
> "we can reduce the problem to something we can intuitively sort of manipulate and understand more easily so sort of classical divide and conquer"
*(sources: src_025)*
