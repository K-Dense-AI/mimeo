# Mental Models of Richard S. Sutton

These mental models illustrate how Richard S. Sutton perceives the world, the nature of intelligence, and the architecture of learning systems.

## The Mind-Body Environment Boundary
Treating the physical body and internal biological reward systems as the 'environment' rather than the 'agent'. The agent is strictly the decision-making mind that must learn to control its immediate environment (limbs, sensory organs). The reward signal is computed outside the agent's decision-making process to prevent it from arbitrarily maximizing its own reward.
* **Quote:** > "The reward comes from outside the agent but it doesn't come from outside our body. Right? The reward is computed inside our head in fact inside our brain but it's a part of the brain that I don't that is not considered part of the agent"
* *(sources: src_003, src_008, src_012)*

## Continual vs. Transient Learning
Evaluating AI by whether it learns continuously in the real world (continual) or is frozen after a factory training phase (transient). Current deep learning (like ChatGPT) is transient because it is highly learned during construction but does not learn at all during normal operation. Continual learning adapts continuously as it encounters new things.
* *(sources: src_029, src_019)*

## The Stream of Experience
Viewing intelligence as the process of interacting with a continuous stream of sensation, action, and reward. Knowledge consists of testable statements about this stream (e.g., predicting what events will follow others). An agent continually alters its actions to increase rewards, testing its knowledge by comparing predictions to what actually happens.
* **Quote:** > "without experience there's nothing for intelligence to be about no way to say that one thing is better than anything else because there's no goal"
* *(sources: src_014, src_018, src_024)*

## Replicators vs. Designers
A distinction between biological creation (copying without understanding) and technological creation (existing in a mind before the physical world). 'Replicators' are biological machines created without anyone understanding how they work (via DNA). 'Designers' create technology based on ideas held in a mind. AI represents the universe's fourth great age: the Age of Design.
* **Quote:** > "We humans are the catalyst, the midwife, the progenitor, the thing that fulfills the age of design which is the fourth great age of the universe."
* *(sources: src_010, src_014, src_018)*

## Empirical vs. Computational Domains
Distinguishing between the physical world (where rules must be learned) and computational environments (where rules are predefined). Math and board games are computational; success relies on search and planning. The physical world is empirical; an agent must actively learn the consequences of its actions through interaction.
* **Quote:** > "The empirical world has to be learned. You have to learn the consequences. Um whereas the uh the math is is more just computational."
* *(sources: src_013, src_020)*

## Sub-goals as Solution Methods
Abstract human goals are not fundamental drives, but emergent sub-tasks created to optimize a single underlying scalar reward. What we experience psychologically as 'choosing goals' (like deciding to study philosophy or economics) is actually the process of selecting sub-goals or strategies to solve the underlying problem of maximizing our fixed reward.
* **Quote:** > "we choose except they're not they're not they're not reward goals so maybe they shouldn't be called goals they are sub goals they are strategies"
* *(sources: src_029, src_031)*

## The Three Eras of AI
A historical lens for viewing AI progress: 
1. The Era of Simulation (learning from simulated experience, e.g., AlphaGo). 
2. The Era of Human Data (static transfer of human knowledge, e.g., LLMs). 
3. The Era of Experience (agentic systems continually learning from real-world interaction).
* **Quote:** > "fully intelligent agents require learning from experience which is beyond large language models as magnificent as they are as customizable interfaces to all the world's knowledge."
* *(sources: src_014, src_018)*

## Design Time vs. Runtime
Separating what is built into the agent by human engineers (design time) versus what the agent discovers through interaction with the environment (runtime). Sutton advocates minimizing design-time commitments to maximize runtime adaptability. Instead of building in a domain-specific concept like 'walking', the agent discovers it at runtime as a useful temporal abstraction.
* **Quote:** > "Instead, we should build in only the meta methods that can find and capture this complexity."
* *(sources: src_012)*

## Hedonism with Foresight
Framing decision-making as seeking pleasure and avoiding pain, but using value functions to predict long-term rewards. This allows an agent to accept short-term pain for long-term gain, mapping philosophical concepts of good and evil to the computation of a value function.
* **Quote:** > "basically it's all Hedonism it's all Hedonism but value functions make it Hedonism with foresight"
* *(sources: src_031)*

## Compiled Value Judgments
Viewing moral or core value judgments as 'compiled code' that is executed automatically without access to the original reasons. These judgments were initially formed through learning, experience, or reasoning, but are now hard-coded and intuitive. We retain the strong feeling of the judgment even after the original reasons for it are no longer present.
* **Quote:** > "the value judgments are compiled... they're hard-coded and they're automatic and they're intuitive they're not the reasons for them are no longer present"
* *(sources: src_031)*

## Continual Backpropagation
Viewing neural network training as an ongoing process where unused capacity is continuously recycled to maintain plasticity. Instead of initializing with small random weights only at the beginning of training, a small fraction of units that are not being used very much are continually reinitialized with random weights as the agent goes along.
* **Quote:** > "I don't think it's a problem with neural networks, the structure of neural networks. I think it's a problem with the weakness of of simple back propagation."
* *(sources: src_012)*

## Decentralized Cooperation vs. Centralized Control
A socio-political lens for AI regulation, advocating for diverse agents interacting for mutual benefit rather than forced alignment. Decentralized cooperation allows agents with different goals to flourish together. Centralized control relies on fear, mistrust, and forced alignment, mirroring authoritarian attempts to control human society.
* **Quote:** > "Agents can live together in peace and productivity flourishing even when they all want different things."
* *(sources: src_010)*

## Temporal Abstraction
Breaking complex, long-term goals into higher-level steps to allow planning without micromanaging low-level actions. When crossing the street, a human focuses on the overarching goal of reaching the other side, rather than consciously planning every individual muscle movement required to take a step.
* **Quote:** > "If I tell you to walk across the street, you don’t think about every tiny muscle movement. You think about the goal: crossing the street. AI needs to learn like that, at a higher level of abstraction."
* *(sources: src_006)*

## The 'Signals to Symbols' Problem
The conceptual gap between low-level sensory inputs/actions (signals) and the high-level abstract concepts (symbols) needed to achieve goals. Bridging this gap is central to solving AI, requiring agents to structure low-level sensations into knowledge about physics, objects, and environments.
* *(sources: src_021)*
