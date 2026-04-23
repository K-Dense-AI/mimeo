# Core Principles of Judea Pearl

Judea Pearl's principles form the epistemological foundation of modern causal inference. They emphasize the fundamental limits of data and probability, and the absolute necessity of explicit, testable models.

## AI Requires Causal World Models
Human-level Artificial Intelligence cannot emerge solely from model-blind machine learning; it requires the integration of causal models. Data alone only allows machines to predict probabilities. True intelligence requires a narrative or causal model to predict the effects of actions, engage in counterfactual imagination, and generalize knowledge.
> "My general conclusion is that human-level AI cannot emerge solely from model-blind learning machines; it requires the symbiotic collaboration of data and models."
*(sources: src_010, src_019, src_023)*

## Insufficiency of Probability Calculus
Standard probability syntax is symmetrical and cannot express directional causal facts, necessitating a new mathematical notation for causal analysis. Because probability calculus cannot distinguish between statistical dependence (association) and causal dependence, it is impossible to mathematically express simple directional facts like 'symptoms do not cause diseases' without new operators like do(x).
> "The syntax of probability calculus does not permit us to express the simple fact that “symptoms do not cause diseases,” let alone draw mathematical conclusions from such facts."
*(sources: src_023, src_028, src_045)*

## The Necessity of Untested Causal Assumptions
Every causal conclusion must rely on causal assumptions that cannot be tested or verified by observational data alone. The laws of probability theory do not dictate how a distribution changes when external conditions are modified. Therefore, causal claims cannot be substantiated from statistical associations alone; they require theoretical or judgmental premises.
> "one cannot substantiate causal claims from associations alone, even at the population level—behind every causal conclusion there must lie some causal assumption that is not testable in observational studies."
*(sources: src_019, src_028, src_045)*

## Missing Links Encode Assumptions
In causal path diagrams, the strong empirical claims and causal assumptions are encoded in the missing links, not the present ones. An arrow merely indicates the possibility of a causal connection. A missing arrow makes a definitive, testable claim of zero influence, and a missing double arrow claims zero covariance.
> "It is important to note that, in path diagrams, causal assumptions are encoded not in the links but, rather, in the missing links."
*(sources: src_028, src_045)*

## Statistics and Deep Learning are Limited to Probability
Standard statistics, Bayesian networks, and deep learning operate entirely within the realm of probability and functional approximation. They cannot answer causal or counterfactual questions without a new vocabulary and explicit causal models. Deep learning provides conditional probabilities based on observations. It cannot answer 'what if' or 'why' questions unless every possible scenario has been explicitly inserted into its memory.
> "Nothing could be done outside probability, which speaks the language of probability. You need to have a new language, and therefore, you cannot do with Bayesian."
*(sources: src_004, src_048)*

## True Decision-Making Requires Counterfactuals
Optimizing resources in fields like medicine or marketing requires individual-level counterfactual analysis, not just population-level statistics. To make personalized decisions, you must identify specific individuals who will respond differently based on an intervention. This requires calculating probabilities of causation, such as the probability of necessity and sufficiency (PNS).
> "But the whole purpose of the target is to find the customer who will act one way if I give him an incentive and a different way if I don’t. And this is already a specific counterfactual question."
*(sources: src_004, src_046)*

## Covariate Selection Requires Causal Knowledge
Choosing covariates for adjustment (e.g., in propensity score analysis) cannot be left to guesswork; it requires qualitative knowledge of the causal relationships among observed and unobserved variables. In large samples, propensity score methods simply reproduce the bias of straight stratification on the chosen covariates. To achieve strong ignorability and eliminate bias, one must map the causal structure.
> "the task of choosing a sufficient (i.e. bias-eliminating) set of covariates for PS analysis requires qualitative knowledge of the causal relationships among both observed and unobserved covariates."
*(sources: src_048)*

## Marginalization is Not Randomization
Mathematical marginalization over latent variables cannot substitute for the physical reality of causal randomization. Simply performing probability calculus over confounders does not simulate the physical intervention required to isolate an effect from its causes.
> "You can perform the mathematical operation, but it will not return that."
*(sources: src_011)*

## Non-manipulable Variables as Causes
Non-manipulable variables (like race or age) can and should be treated as causes in analytical models. The restriction of 'no causation without manipulation' is an unnecessary hang-up. Treating non-manipulable variables as causes provides important, testable information about other manipulable variables in the system.
> "Researchers need not be concerned with the distinction between manipulable and non-manipulative variables, except of course in the design of actual experiments."
*(sources: src_019)*

## The Imprisonment of the Equality Sign
Science has historically neglected the directionality of cause and effect because mathematical equations are inherently symmetric. Equations like Newton's laws allow you to predict one variable from another symmetrically. However, manipulating an effect does not change its cause. A new algebra was required to handle this fundamental asymmetry.
> "all our equations are imprisoned by the connective of equality sign."
*(sources: src_023)*
