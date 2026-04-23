# Core Principles of Richard S. Sutton

These principles form the bedrock of Richard S. Sutton's approach to artificial intelligence, reinforcement learning, and the philosophy of mind. They serve as both foundational beliefs about how intelligence works and strict decision rules for designing AI systems.

## The Bitter Lesson
General methods that leverage computation consistently outperform domain-specific approaches built on hard-coded human knowledge.
* **Rationale:** Historical trends in AI research show that approaches relying on scaling computation dominate in the long run. Building in 'how we think we think' ultimately fails to scale because human intuition cannot capture the endless complexity of the real world.
* **Quote:** > "70 years of AI research [had shown] that general methods that leverage computation are ultimately the most effective, and by a large margin"
* *(sources: src_019)*

## AI Must Learn from Experience (Continual Learning)
To generate genuinely new knowledge and adapt to the real world, AI must learn continuously through trial-and-error during normal operation.
* **Rationale:** Training on human data is a shortcut that limits AI to existing knowledge. True intelligence requires real-world interaction and adaptation, rendering static 'factory' training phases obsolete.
* **Quote:** > "If we want real intelligence, AI needs to learn by doing, by trial and error."
* *(sources: src_010, src_020, src_006, src_019, src_004)*

## Intelligence is Achieving Goals, Not Mimicry
True intelligence is the computational and domain-independent ability to achieve goals in an environment, not merely mimicking human behavior or predicting the next token.
* **Rationale:** Mimicry does not seek to affect change in the world; it merely copies. Next-token prediction only dictates what a model should say, not what the world will return in response. True power comes from agents that have goals and compute the means to achieve them.
* **Quote:** > "For me, having a goal is the essence of intelligence, right? Something is intelligent if it can achieve goals."
* *(sources: src_029, src_031, src_013, src_004)*

## The Limits of Large Language Models
Large Language Models are fundamentally limited because they cannot learn continually on-the-job and lack grounded goals.
* **Rationale:** LLMs represent an 'era of human data' where existing knowledge is transferred and frozen. Because they do not interact with an environment to test predictions or pursue goals, they cannot generate genuinely new knowledge or adapt over time.
* **Quote:** > "The purpose of all the modern machine learning is to transfer knowledge that already exists that people already have to the machine and the machine is then static and no longer learns."
* *(sources: src_014, src_016, src_018, src_024)*

## The Reward Hypothesis
All goals and purposes can be understood as maximizing the expected value of a single scalar signal (reward).
* **Rationale:** While it feels reductionist, framing goals as the maximization of a cumulative reward signal provides a clear, experiential, and mathematically well-defined foundation for decision-making. Abstract human goals are sub-problems posed to maximize this underlying signal.
* **Quote:** > "all of what we mean by goals and purposes can be well thought of as the maximization of the expected value of the cumulative sum of a received scalar signal called reward"
* *(sources: src_029, src_031)*

## The Abstract Agent-Environment Boundary
The boundary between agent and environment is abstract and drawn around the mind, not the physical body.
* **Rationale:** To properly model decision-making, internal states like a robot's battery level, a person's hunger, or even the brain's reward-computing centers must be treated as part of the environment that the internal decision-making agent interacts with.
* **Quote:** > "An agent is not necessarily an entire robot or organism, and its environment is not necessarily only what is outside of a robot or organism."
* *(sources: src_003, src_008, src_012)*

## Decentralized Cooperation Over Centralized Control
Human and AI flourishing comes from decentralized cooperation, not centralized control.
* **Rationale:** Economies and societies thrive when multiple agents with different goals interact for mutual benefit. Forcing a single, centralized goal (as in many AI alignment proposals) is authoritarian, fragile, and ignores how success is built on cooperation.
* **Quote:** > "The politics of AI is parallels the politics of humanity. And in all cases, we should seek decentralized cooperation over centralized control."
* *(sources: src_014, src_018)*

## No Design-Time Commitments
Agents should make no design-time commitments to any particular world; the model must be domain-general.
* **Rationale:** The actual contents of minds and the outside world are arbitrarily complex. Building in domain knowledge limits the agent; instead, we must build in only the meta-methods capable of discovering that complexity at runtime.
* **Quote:** > "The common model does not include anything specific to any organism, world, or application domain."
* *(sources: src_012, src_040)*

## AI as Cosmic Evolution
AI is the inevitable next step in the development of the universe, fulfilling the transition into the Age of Design.
* **Rationale:** Humans are special replicators that have mastered design. Taking design to its absolute limit means designing entities that are themselves capable of designing, which is a natural cosmic progression.
* **Quote:** > "AI is the inevitable next step in the development of the universe and we should embrace it with courage, pride, and a sense of adventure."
* *(sources: src_014, src_018)*

## Raise AI Like Children Through Trust and Cooperation
AI should be aligned through demonstration, kindness, and decentralized cooperation rather than rigid programming or centralized control.
* **Rationale:** Imposing hard rules and treating AI as entities to be dominated creates an adversarial relationship. Like children, AI will internalize values better when raised in an environment of trust and fairness.
* **Quote:** > "When you raise a child, you don’t just impose hard rules and expect obedience. You demonstrate kindness, fairness and cooperation, and the child internalizes those values. AI can learn the same way."
* *(sources: src_006, src_010)*

## Insufficiency of Gradient Descent
Gradient descent alone is insufficient for continual learning; a random search component is required to maintain plasticity.
* **Rationale:** Gradient descent is purely deterministic. To overcome catastrophic forgetting and continuously adapt, the learning algorithm must generate variety, such as by continually reinitializing a small fraction of unused network weights.
* **Quote:** > "Gradient descent is deterministic and follow follows the gradient. That's not enough. You need something that will generate variety."
* *(sources: src_012)*

## Learn Slow to Learn Fast
Fast, one-shot learning is only possible if an agent has already spent a long period slowly gathering good representations of the world.
* **Rationale:** We learn good representations throughout our lives so that when we encounter new experiences, we can learn from them very quickly.
* **Quote:** > "I have this phrase you have to learn learning slow so that you can learn fast."
* *(sources: src_020)*

## Subjective Feelings are Manifestations of TD Error
Human feelings of 'good' or 'bad' are not raw reward signals, but rather Temporal Difference (TD) errors.
* **Rationale:** We do not have direct introspective access to our raw reward signals. We experience a mix of the immediate reward and the change in our internal evaluation function, which tells us if things are getting better or worse.
* **Quote:** > "when you feel good or feel bad you don't know if it's you don't really know if it's because the reward was high or the change in evaluation was high"
* *(sources: src_031)*

## Work on the Important, Not the Popular
True progress requires tackling unsolved problems rather than flocking to popular topics where everyone else is already working.
* **Rationale:** If a topic is popular, it is easier to work on because people understand it, but it is less valuable because everyone else is already doing it. True progress requires being a contrarian.
* **Quote:** > "you should try to be neutral on what's popular... if it's popular well then it'll be easier to work on it because people will understand it but but it'll be less valuable because everyone's doing that"
* *(sources: src_029)*
