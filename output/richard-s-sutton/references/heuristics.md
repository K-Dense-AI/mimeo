# Heuristics and Rules of Thumb

These are the pithy, day-to-day rules of thumb Richard S. Sutton applies to research, AI design, and navigating his field.

## Embrace Being Out of Sync
Be content being out of sync with current fads; when everyone is thinking the same thing, question it. Look back into history and classic traditions of thought to avoid getting swept up in the current hype cycle.
* **Quote:** > "I’m personally just content being out of sync with my field for a long period of time, perhaps decades, because occasionally I have been proved right in the past."
* *(sources: src_014, src_024)*

## Approximate Everything
All your value functions, policies, and state transition models must be approximate. The world is too vast and contains other agents; you can never perfectly model or compute exact values for every state.
* **Quote:** > "Even a single state of the world you can't really keep in your head because the state of the world can includes what's going on in all those other agents minds."
* *(sources: src_012)*

## Be Neutral on Popularity
Try to be neutral on what's popular; popular problems are easier to explain but less valuable to solve.
* **Quote:** > "you should try to be neutral on what's popular..."
* *(sources: src_029)*

## Do the Work, Don't Just Argue
Don't spend all your time trying to convince people your contrarian idea is important; just do the work and prove it.
* **Quote:** > "It's a good way to lose is to spend your time trying to convince other people that they should do what you think is important."
* *(sources: src_029)*

## Don't Build In How We Think We Think
Avoid hard-coding human intuition into systems; rely on general methods that scale with computation.
* **Quote:** > "building in how we think we think does not work in the long run"
* *(sources: src_019)*

## Everything at Runtime
Everything has to be done at runtime. Avoid static pre-training phases; agents must learn and adapt continuously while interacting with the environment.
* *(sources: src_012)*

## Intelligence as Prediction and Control
An agent is intelligent to the extent that it can predict and control its experience.
* *(sources: src_014)*

## Knowledge is Prediction
Everything we know is a prediction about what will happen if we were to do something.
* **Quote:** > "Everything we know is a prediction about what will happen if we were to do something."
* *(sources: src_010)*

## Learn Slow to Learn Fast
Spend time slowly building good representations so you can learn quickly from new experiences later.
* **Quote:** > "I have this phrase you have to learn learning slow so that you can learn fast."
* *(sources: src_020)*

## Look to Animals
Look to animals to understand intelligence; what we have in common with them is more fundamental than what distinguishes us.
* *(sources: src_024)*

## Prioritize the Model Over Values
It's easier to get the model right than the values right. World dynamics remain relatively stable even as the agent's immediate desires or values change, making transition models highly robust.
* **Quote:** > "It's easier to get the model right than the values right."
* *(sources: src_012)*

## Track Feature Statistics
Keep statistics on features to inform the generation process about which are good and bad. This metadata is crucial for driving the open-ended discovery of new, useful abstractions.
* *(sources: src_012)*

## Use the Simplest Methods
Use the simplest possible methods that you can understand very well. For example, use Sarsa if possible, actor-critic when pressed, and linear function approximation with constant step sizes.
* *(sources: src_021)*

## Write to Clarify Confusion
The value of writing down your thoughts is directly proportional to how vague and confused they are.
* **Quote:** > "Usually the value of writing down your thoughts is directly proportional to how vague and Confused they are."
* *(sources: src_029)*
