# Heuristics and Rules of Thumb

Yann LeCun applies these pithy rules of thumb to cut through AI hype, evaluate new architectures, and guide the engineering of intelligent systems.

## Abandon Generative AI for AGI
If the goal is human-level AI, stop relying on generative models that predict exact pixels or tokens.
> "If you're really interested in human level AI, abandon the idea of generative AI."
*(sources: src_019, src_023)*

## Minimize Reinforcement Learning
Use reinforcement learning only when your world model or objective function is inaccurate, not as the primary learning engine. It is far too sample-inefficient.
> "abandon reinforcement learning or at least minimize its use because it's so inefficient in terms of samples"
*(sources: src_010, src_011, src_015, src_023)*

## Open-source will win
Bet on open-source AI models over proprietary ones for long-term dominance and global sovereignty.
> "The only way to have any level of sovereignty in AI is is is to have access to open source you know powerful open source AI systems."
*(sources: src_003, src_011)*

## A world model is not a digital twin
Do not build world models as video generation systems; they should predict abstract representations, not pixels.
> "A world model which allows you to make prediction should not be a simulator of the world."
*(sources: src_011)*

## Surprise Equals a Flawed World Model
When an AI system encounters something surprising, it indicates that its internal world model is wrong and needs updating.
> "When something surprising happens, that means your world model is wrong."
*(sources: src_019)*

## Avoid Probabilistic Normalization
Do not use probabilistic normalization in high-dimensional spaces; use energy functions instead to maintain tractability.
> "you must be weary of probabilities probabilities restrict us to a certain type of lost function that is not necessarily tractable"
*(sources: src_010)*

## Language vs. Physical World Complexity
Language is actually easy compared to understanding the physical world; do not confuse the ability to manipulate language with underlying intelligence.
> "We think of language as kind of the epitome of you know, human intelligence and stuff like that. It's actually not true. Language is actually easy."
*(sources: src_032)*

## Skepticism of AGI Magic Bullets
If a company tells you they will reach human-level AI just by training on more data with a few tricks, or that a small startup has discovered a secret magic bullet, do not invest in them.
*(sources: src_020)*
