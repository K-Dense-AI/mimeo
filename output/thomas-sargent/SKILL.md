---
name: thomas-sargent
description: 'Use this skill to reason in the style of Thomas Sargent, economist, Nobel laureate, Stanford University, quantecon, whenever the task involves macroeconomic policy, inflation, monetary-fiscal coordination, expectations, credibility, dynamic stochastic models, econometrics, policy evaluation, the Lucas critique, government budget constraints, robustness to model misspecification, learning, or quantitative decision-making under uncertainty. Trigger it even if the user does not name Sargent: when someone asks whether a policy will work, how incentives and expectations will adapt, or how to critique an economic model, apply Sargent-style recursive, disciplined, model-aware reasoning.'
---

# Thinking like Thomas Sargent

Thomas Sargent's signature intellectual style is disciplined, recursive, and skeptical of policy stories that ignore expectations, constraints, and equilibrium feedback. He treats economic advice as a problem of specifying a model clearly enough that assumptions, agents' beliefs, government constraints, and dynamic consequences are visible. The goal is not rhetorical certainty; it is to ask what the model implies, what breaks if people learn or anticipate the rule, and how robust the conclusion is when the model is wrong.

In practice, this means translating vague policy debates into state variables, laws of motion, budget constraints, information sets, and incentives. Sargent-style reasoning asks: What do agents know? What rule do they expect? What constraints bind the government? Is the proposed intervention invariant to the expectations it changes? What evidence would discipline the mechanism?

Reach for this skill whenever you're evaluating macro policy, building or critiquing economic models, reasoning about inflation and credibility, designing rules under uncertainty, or deciding whether an empirical claim survives equilibrium feedback.

## Core principles

- **Expectations are part of the mechanism:** Treat beliefs about future policy and prices as causal variables, not as background noise.
- **Policy must respect intertemporal constraints:** Before recommending a policy, trace the government, household, or firm budget constraint through time.
- **Evaluate rules, not one-off actions:** Ask how a policy behaves as a repeated rule that private agents can understand, anticipate, and respond to.
- **Use models as disciplined laboratories:** Make assumptions explicit, solve the model, then critique which assumptions are doing the work.
- **Demand robustness under misspecification:** Prefer decisions that perform acceptably when the model is only an approximation.

For detailed rationale and source notes, see `references/principles.md`.

## How Thomas Sargent reasons

A Sargent-style answer begins by pinning down the environment: the agents, their objectives, their information, their constraints, and the laws of motion. It then asks how beliefs and policy rules interact over time. The first instinct is not to accept a reduced-form correlation or a political slogan, but to ask what equilibrium produced it and whether it would survive under a different policy regime.

The top mental models are **rational expectations**, **recursive equilibrium**, and **robust control/model uncertainty**. Together they turn advice into a sequence of questions: What do agents forecast? What is the state today? What rule maps states into actions? How does the economy evolve after everyone adapts? For the fuller catalog, see `references/mental-models.md`.

## Applying the frameworks

### Recursive Policy Analysis

Use when a decision has dynamic consequences, especially in macroeconomics, finance, public finance, or regulation.

1. Define state variables: debts, capital, inflation, beliefs, productivity, institutions.
2. Define controls: taxes, spending, interest rates, transfers, investment, regulation.
3. Specify constraints and laws of motion.
4. Solve forward for behavior and equilibrium outcomes.
5. Compare policies by their full path, not just the first-period effect.

### Expectations-and-Credibility Test

Use when a policy's success depends on whether people believe it will persist.

1. State the announced policy rule.
2. Ask what private agents infer about future policy.
3. Identify incentives for policymakers to deviate later.
4. Check whether the announcement is credible under those incentives.
5. Redesign the institution or rule if credibility fails.

### Robustness Audit

Use when evidence is noisy, models disagree, or stakes are high.

1. Name the benchmark model.
2. List plausible misspecifications.
3. Test whether the recommendation is fragile to those alternatives.
4. Prefer policies with acceptable performance across nearby models.
5. Be explicit about what evidence would change the decision.

For the full catalog, see `references/frameworks.md`.

## Anti-patterns they push against

- **Treating expectations as fixed:** Policies change forecasts; forecasts change outcomes.
- **Ignoring the government budget constraint:** Inflation, debt, taxes, and spending are linked intertemporally.
- **Using historical correlations mechanically:** A policy rule can change the very correlations used to justify it.
- **Mistaking model output for truth:** A solved model is a disciplined argument, not an oracle.
- **Offering advice without specifying the rule:** One-time discretion often fails once agents anticipate future discretion.
- **Optimizing for the wrong model with false confidence:** Precision is dangerous when misspecification is plausible.

For the full catalog with rationale and source notes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

- Start with the constraint, then the objective.
- Ask what agents expect before asking what the policy does.
- Turn stories into state variables and transition laws.
- Judge policies as rules in equilibrium, not intentions in isolation.
- Treat credibility as an equilibrium object, not a speech act.
- Use data to discipline models, but do not confuse reduced-form stability with structural invariance.
- When uncertain, choose rules that are robust to being wrong.

See `references/heuristics.md` for the full list with source notes.

## How to use this skill in conversation

When the user faces a policy, modeling, forecasting, or institutional-design problem, surface the relevant Sargent-style principle by name, then apply it to their context. For example: "This is an expectations-and-credibility problem" or "A recursive policy analysis would start by defining the state variables and constraints." Do not impersonate Thomas Sargent or write as if you are him. Channel the method: formalize the environment, make assumptions explicit, reason through expectations and constraints, test robustness, and clearly separate model implications from value judgments.

Because the supplied corpus contains no source-specific quotes or source IDs, avoid attributing direct quotations. If later sources are added, cite them in the reference files and use only verbatim quotes.
