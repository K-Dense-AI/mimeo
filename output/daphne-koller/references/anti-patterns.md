# Daphne Koller's Anti-Patterns

This document catalogs the practices and mindsets Daphne Koller explicitly warns against, particularly in the realms of AI, biology, and organizational structure.

## Siloed Disciplines / Throwing data over the wall
Keeping machine learning scientists and biologists siloed, or having scientists generate datasets in isolation and hand them to computational teams. This fails because it doesn't encourage the kind of experimental design needed to drive innovative machine learning. ML scientists will solve biologically irrelevant problems, and biologists will only use ML for boring automation tasks.
*(sources: src_000, src_034, src_012)*

## Assuming data is fungible across domains
Dropping AI onto existing, incoherent data or assuming internet text data grants capabilities in biology. Having massive datasets in one domain doesn't automatically grant capabilities in domains where the necessary data hasn't even been generated yet. Systems must be re-architected around AI.
*(sources: src_014, src_048)*

## Artisanal Drug Discovery
Treating drug discovery as an artisanal, one-off process. It prevents the sharing of insights and infrastructure across different efforts, making every drug a 'snowflake' and slowing down overall progress.
*(sources: src_000)*

## Building persistent products in academia
Trying to build reusable pipelines or products within a university setting. The incentives are misaligned. Grad students and postdocs are incentivized to get data for papers and move on, not to build data pipelines, maintain reusability, or create something a hospital can actually buy.
*(sources: src_014)*

## Deep learning for everything
Assuming deep learning is the solution to every problem. It ignores the reality of fields like biology where datasets are small, highly heterogeneous, and require the integration of prior knowledge to compensate for the lack of sample size.
*(sources: src_034)*

## Focusing AI solely on molecule generation
Directing all AI efforts toward generating molecules while ignoring target discovery. While molecule generation is a well-defined problem, the most common reason drugs fail in the clinic is because the biological target itself was wrong.
*(sources: src_000)*

## Hallucinated Synthetic Data
Training AI models on purely hallucinated synthetic data. If you generate data entirely from nothing and train a model on it, you are merely reinforcing what the model already knew without anchoring it to ground truth.
*(sources: src_012)*

## Hyperbole and 'Fake it till you make it'
Relying on hyperbole and the 'fake it till you make it' mentality in science and deep tech. It creates a sense of distrust in the entire field when bold claims fail to materialize, which can lead to massive funding droughts (like historical 'AI winters'). In biology, it is especially dangerous because you are meddling with people's lives.
*(sources: src_006)*

## Hypothesis-driven drug discovery
Relying on the human brain to understand complex biological systems. It leads to a 90% failure rate when the drug finally reaches clinical trials because the target doesn't actually modulate the clinical outcome in humans.
*(sources: src_022)*

## Relying on correlational data for interventional tasks
Using purely observational data to answer causal questions in the physical world. You fall prey to false and misleading conclusions when you try to answer causal questions (like drug efficacy or physical world interventions) using purely observational data.
*(sources: src_014)*

## Siloing disciplines
Keeping computational scientists and life scientists separated in an organization. They use different jargon and think about the world in different ways, causing them to talk past each other rather than compounding their expertise.
*(sources: src_022)*

## Symptom-based Disease Definition
Defining diseases by coarse-grained symptomology (e.g., 'Alzheimer's'). It ignores the multiple different underlying biological mechanisms driving the disease in different people, forcing the use of lowest-common-denominator treatments with poor efficacy.
*(sources: src_012)*

## Trusting articulate AI outputs over experimental validation
Falling for the 'seductive plausibility' of generative AI and bypassing rigorous physical experiments. Generative models are optimized for fluency, not factual accuracy. This complacency silently erodes the scientific method and wastes years chasing beautifully worded mistakes.
*(sources: src_048)*
