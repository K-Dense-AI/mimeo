# Heuristics and Rules of Thumb

Judea Pearl applies these practical rules of thumb to quickly cut through confusion in statistics, AI, and decision-making.

## Missing Links Encode Assumptions
When reading or building path diagrams, look to the missing links to find the causal assumptions.
> "It is important to note that, in path diagrams, causal assumptions are encoded not in the links but, rather, in the missing links."
*(sources: src_028, src_045)*

## The Associational Test
If a concept can be defined entirely by a joint distribution, it is associational; if it cannot, it is causal.
> "Every claim invoking causal concepts must rely on some premises that invoke such concepts; it cannot be inferred from, or even defined in terms statistical associations alone."
*(sources: src_028, src_045)*

## No Guesswork in Covariates
Never leave the choice of covariates for adjustment methods to guesswork; always map the underlying causal relationships first.
> "the effectiveness of PS methods rests critically on the choice of covariates, X, and that choice cannot be left to guesswork"
*(sources: src_048)*

## Functional Approximators Require Causal Inference
If a tool is merely a functional approximator (like deep learning), it must be guided by ordinary causal inference to be used effectively for decision-making.
> "If it's a functional approximator, we know exactly how to use it because we can do ordinary causal inference."
*(sources: src_004)*

## Situation-Specific Decision Making
Treat every decision-making scenario as situation-specific, requiring individual-level counterfactual analysis rather than broad population averages.
> "Every decision-making is situation-specific decision-making."
*(sources: src_004)*

## Distinguish Assumptions from Derivations
Always strictly distinguish your assumptions from your definitions, and your conclusions from your derivations.
*(sources: src_023)*

## Translate Intuition into Math
Formalize your intuition into mathematics, because the mathematics will amplify your intuition.
> "Translate intuition into mathematics, the mathematics amplifies your intuition."
*(sources: src_019)*

## Reject Unsatisfying Standard Answers
If you don't understand something your own way, refuse to accept the standard answer.
> "Rebel, if you don’t understand and insist on understanding it your way, and until you understand it your way, don’t take a standard answer as an answer if it doesn’t satisfy the question that you have in mind."
*(sources: src_020)*

## Computer Scientists as Psychologists
Recognize that the drive to build AI is often a drive to understand human psychology.
> "Every computer scientist is a frustrated psychologist."
*(sources: src_020)*
