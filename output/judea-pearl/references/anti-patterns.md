# Anti-Patterns Judea Pearl Pushes Against

Pearl explicitly warns against these practices, which often stem from a failure to distinguish between probability and causality.

## Answering Causal Questions with Data Alone
Attempting to answer causal questions from data or distributions alone without articulating causal assumptions. The laws of probability theory do not dictate how one property of a distribution ought to change when another property is modified by external intervention. Data alone is insufficient.
> "Every claim invoking causal concepts must rely on some premises that invoke such concepts; it cannot be inferred from, or even defined in terms statistical associations alone."
*(sources: src_019, src_028, src_045)*

## Scaling LLMs to Achieve AGI
Believing that simply scaling up current model-blind LLM architectures will eventually result in Artificial General Intelligence. Current transformer algorithms have mathematical limitations that prevent them from efficiently internalizing the causal world models required to reason about interventions and counterfactuals.
> "My general conclusion is that human-level AI cannot emerge solely from model-blind learning machines; it requires the symbiotic collaboration of data and models."
*(sources: src_010, src_019, src_023)*

## Using Probability Calculus for Causality
Relying solely on standard probability calculus (like marginalization) to express causal relationships or simulate interventions. Probability calculus is symmetric and cannot distinguish statistical dependence from directional causal dependence. Marginalizing over a confounder does not replicate the physical act of randomization.
> "You can perform the mathematical operation, but it will not return that."
*(sources: src_011, src_028, src_045)*

## Blindly Applying Propensity Scores
Assuming propensity score methods always reduce bias compared to crude, unadjusted estimates. In certain causal structures, like an M-graph, adjusting for a covariate can awaken dormant bias, making the adjusted estimate worse than the crude estimate.
> "the crude estimate is bias-free, while PS methods introduce new bias."
*(sources: src_048)*

## Hiding Assumptions Under the Rug
Keeping causal assumptions implicit or vague to avoid criticism. This prevents the assumptions from being explicitly tested or criticized, which hinders scientific progress and obscures what the world must actually be like for a statistical procedure to work.
> "Assumptions are self-destructive in their honesty. The more explicit the assumption, the more criticism it invites"
*(sources: src_036)*

## Ignoring Causal Directionality
Ignoring the directionality of cause and effect in science and social issues. Failing to distinguish between cause and effect leads to cause-and-effect inversion, making it impossible to correctly attribute outcomes to their actual origins.
> "all our equations are imprisoned by the connective of equality sign."
*(sources: src_023)*

## Treating Structural Equations as Regression
Interpreting structural coefficients merely as regression coefficients. Regression coefficients are artifacts of analysis that are by definition uncorrelated with regressors. Structural coefficients represent actual physical/causal effects and retain their meaning regardless of whether error terms are correlated.
*(sources: src_019, src_045)*

## Maximizing Population Survival over Individual Benefit
In medicine or policy, maximizing overall probability of a positive outcome instead of focusing on individual counterfactual benefit. Maximizing survival probability can lead to selecting already healthy or immune people who would survive anyway, wasting resources on those who don't actually need the intervention.
> "We care about harm and benefit to patients. We don’t care about maximizing the probability of survival."
*(sources: src_004)*

## No Causation Without Manipulation
Adhering strictly to the mantra that only manipulable variables can be treated as causes. This restricts analytical models unnecessarily. Defining causal effects on non-manipulable variables (like race or age) provides important, testable information about the causal effects of other manipulable variables.
> "The mantra 'No causation without manipulation', represents another hang-up of the potential outcome community, which has not been able to liberate itself from the experimental setup..."
*(sources: src_019)*

## Reducing Causality to Missing Data
Treating causal inference entirely as a statistical missing data problem (e.g., relying on Missing At Random assumptions). This fails because it ignores the transparency and power provided by structural equations and the do(x) operator, and relies on definitions that are incomprehensible to the typical user trying to map them to reality.
> "Should we continue to rejoice the reduction from causal to statistical conceptualization of the problem?"
*(sources: src_036)*

## Relying on LLMs for Causal Reasoning
Trusting Large Language Models (like ChatGPT) to perform reliable causal reasoning. LLMs perform causal reasoning in a 'very sloppy way' and often just regurgitate 'cookbook answers' based on prompting, rather than actually computing causal effects from a structural model.
*(sources: src_004)*
