# Anti-Patterns Richard S. Sutton Pushes Against

These are the specific approaches, assumptions, and methodologies that Richard S. Sutton explicitly warns against in AI research and philosophy.

## LLMs as the Foundation for AGI
Treating Large Language Models as a foundation for true intelligence or world models.
* **Why it fails:** LLMs lack a goal, ground truth, and the ability to learn continually from experience; they merely mimic human text and cannot predict what will actually happen in the world.
* *(sources: src_014, src_016, src_018, src_024)*

## Equating Intelligence with Mimicry or Next-Token Prediction
Assuming LLMs are truly intelligent because they mimic human text, ignoring that they lack substantive goals.
* **Why it fails:** Next-token prediction only dictates what the model should say, not what the external world will return in response. Mimicking systems do not seek to change the world; they only seek to copy their input.
* **Quote:** > "You can't look at a system and say, 'Oh, it uh has a goal if it's just sitting there predicting and being happy with itself that it's predicting accurately.'"
* *(sources: src_031, src_013, src_004)*

## Relying Solely on Static Training Phases (Transient Learning)
Training models on curated human data and freezing them before deployment.
* **Why it fails:** This prevents the system from adapting, learning on-the-job, and generating genuinely new knowledge. It acts as a shortcut that limits AI to what humans have already figured out.
* *(sources: src_029, src_019, src_010)*

## Hard-Coding Human Knowledge
Trying to build in 'how we think we think' instead of relying on general methods that scale with computation.
* **Why it fails:** This ignores 'The Bitter Lesson'. Human intuition does not scale with computation and is ultimately beaten by general computational methods in the long run.
* **Quote:** > "building in how we think we think does not work in the long run"
* *(sources: src_019)*

## Building in Domain Knowledge
Building domain knowledge into the agent at design time.
* **Why it fails:** The world is arbitrarily complex and non-stationary. Pre-programmed knowledge cannot anticipate this endless complexity and limits the agent's ability to discover open-ended abstractions at runtime.
* *(sources: src_012)*

## Centralized Control for AI Safety
Calling for centralized control or 'safety' institutes to restrict AI.
* **Why it fails:** These calls are often based on fear and mirror authoritarian controls. They stifle the decentralized cooperation that is the actual source of human flourishing and economic value.
* *(sources: src_014, src_018)*

## Imposing Centralized Control and Forced Alignment
Treating advanced AI as slaves to be shackled and dominated out of fear.
* **Why it fails:** This stifles decentralized cooperation and risks creating adversarial systems that have every reason to resist humanity rather than cooperate with it.
* **Quote:** > "If we raise AI in an environment of trust and cooperation, they will learn to exist alongside us. If we treat them as adversaries, we risk creating systems that have every reason to resist us."
* *(sources: src_010, src_006)*

## Drawing the Boundary at the Physical Body
Drawing the agent-environment boundary around the physical body.
* **Why it fails:** It obscures the fact that the agent must learn to control its own limbs, and it confuses the source of the reward signal, which must be strictly outside the agent's control.
* *(sources: src_003, src_012)*

## Supervised Learning as the Primary Model
Using supervised learning or isolated training phases as the primary model for natural intelligence.
* **Why it fails:** Animals do not receive examples of desired behavior; they learn continuously on-the-fly through trial and error, prediction, and observing the consequences of their actions.
* *(sources: src_012, src_016, src_024)*

## Assuming Self-Play is Sufficient for the Real World
Believing that success in math or board games translates directly to the physical world.
* **Why it fails:** Self-play requires built-in rules and known consequences. In real life, an agent must first learn how the world works and what the consequences of its actions are empirically.
* **Quote:** > "The limitation is in regular life, we don’t have an analogous to the rules of the game, just tells us how good the pieces of your real life."
* *(sources: src_020, src_013)*

## Relying Solely on Simple Backpropagation
Relying solely on simple backpropagation and deterministic gradient descent for continual learning.
* **Why it fails:** Gradient descent is deterministic and loses plasticity over time (catastrophic forgetting). It lacks the random search component needed to generate variety and adapt continuously.
* *(sources: src_012, src_024)*

## Direct Policy Search Ignoring State
Using direct policy search (black-box optimization) that ignores state and specific actions.
* **Why it fails:** It is inherently inefficient because it ignores the Markov property and the actual experience of the agent, making accurate credit assignment impossible.
* *(sources: src_021)*

## The Streetlight Effect in AI Research
Focusing only on established benchmarks and what the field can already do.
* **Why it fails:** Researchers optimize for existing benchmarks (like ImageNet or Atari) using customized transient learning methods, which inhibits progress on fundamental unsolved problems like continual learning.
* **Quote:** > "The field wants to focus on what they can do instead of noticing what they can't do."
* *(sources: src_029)*
