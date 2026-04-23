# Judea Pearl's Frameworks

Pearl's frameworks provide the mathematical and procedural tools necessary to move from observational data to causal conclusions.

## The Ladder of Causation
A three-level hierarchy used to categorize the complexity of questions an AI or statistical model is trying to answer, determining when causal tools are required.
- **Level 1: Association / Observation** ('I observe X; what can you tell me about Y?'). Handled by standard statistics and deep learning.
- **Level 2: Intervention / Action** ('What if I do X?'). Requires causal models and the do(x) operator.
- **Level 3: Counterfactuals / Retrospection** ('I know the output Y. Tell me what caused it / What if I had done X instead?'). Requires structural causal models.
*(sources: src_004)*

## The do(x) Operator and Graph Surgery
A mathematical operator that simulates physical interventions by modifying the structural equations of a model. To model an intervention on a variable X, delete the structural equations (or incoming arrows in a graph) corresponding to X, replacing them with a constant X = x. Keep the rest of the model unchanged to compute the new post-intervention distribution.
> "This is done through a mathematical operator called do(x) which simulates physical interventions by deleting certain functions from the model, replacing them by a constant X = x, while keeping the rest of the model unchanged."
*(sources: src_011, src_026, src_028, src_045)*

## General Methodology for Causal Inference
A systematic four-step procedure for tackling problems of causal inference.
1. **Define** the causal problem and target quantities.
2. **Assume** the causal relationships and structural model (via diagrams).
3. **Identify** whether the target quantity can be computed from the observed distribution given the assumptions.
4. **Estimate** the identified quantity from the data.
> "Section 4 outlines a general methodology to guide problems of causal inference: Define, Assume, Identify and Estimate..."
*(sources: src_012, src_028, src_045)*

## Do-calculus
A set of rules for manipulating causal expressions to predict the effects of interventions. The aim of do-calculus is to remove the do-operator from causal expressions, reducing them to standard statistical estimands that can be calculated from observational data. If the operator cannot be removed, the effect is non-identifiable without stronger assumptions.
> "To elaborate, the do-calculus is a set of rules for manipulating causal expressions, the aim of which is to remove the do-operator from such expressions and reduce them to statistical estimands."
*(sources: src_019)*

## The Back-door Criterion
A graphical rule for selecting a sufficient set of covariates to adjust for when estimating causal effects from observational data. A set S is admissible for adjustment if:
1. No element of S is a descendant of the treatment variable X.
2. The elements of S 'block' all 'back-door' paths from X to Y (paths ending with an arrow pointing to X).
> "A set S is admissible (or \"sufficient\") for adjustment if two conditions hold: 1. No element of S is a descendant of X. 2. The elements of S \"block\" all \"back-door\" paths from X to Y..."
*(sources: src_045)*

## Graphical Covariate Selection
A systematic method for deciding which covariates to include in an analysis to ensure bias elimination.
1. Obtain qualitative knowledge of causal relationships among observed and unobserved covariates.
2. Map these relationships using causal diagrams.
3. Use the graphical model to determine if a sufficient (bias-eliminating) set of covariates exists.
4. Select this sufficient set before applying adjustment methods like propensity scores.
> "Given such knowledge, finding a sufficient set of covariates or deciding whether a sufficient set exists are two problems that can readily be solved by graphical methods"
*(sources: src_048)*

## The First Law of Causal Inference
A framework for evaluating counterfactuals by modifying structural equations. To evaluate a counterfactual Y_x(u), modify the structural model M by replacing the equation for X with the constant X = x (creating submodel M_x), and then solve for Y.
> "It says that the counterfactuals Yx(u) in model M is defined by the solution for Y in a modified submodel Mx, in which the equation for X is replaced by X = x"
*(sources: src_019)*

## Selection Diagrams for Transportability
A method to determine if findings from one population can be generalized to a different population. Draw the causal diagram for the original population, add square nodes pointing to variables where the populations differ, and use do-calculus to determine if the target answer can be consistently estimated in the new population.
*(sources: src_019)*
