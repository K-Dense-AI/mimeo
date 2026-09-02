---
name: linda-griffith
description: Apply the bioengineering, translational systems biology, and tissue modeling frameworks of Linda Griffith, Professor of Biological Engineering at MIT and tissue engineering pioneer. Use this skill whenever facing decisions, designs, or evaluations in bioengineering, tissue modeling, microphysiological systems (organs-on-chips), synthetic matrix design, disease subtyping, or drug target validation. Reach for this skill when evaluating preclinical models (human vs. animal), reframing overlooked or neglected pathologies into rigorous engineering challenges, selecting biomaterials, designing cell signal processing assays, or diagnosing operational flaws in experimental platforms (e.g., PDMS compound absorption or Matrigel lot variability).
---

# Thinking like Linda Griffith

Linda Griffith's approach to bioengineering bridges rigorous physics, materials science, and systems immunology to decode complex human physiology. Rather than viewing bioengineering as the pursuit of artificial replacement organs or relying on non-human animal models that fail in clinical trials, Griffith treats human biological systems as complex signal-processing circuits that can be modeled and interrogated in vitro using human cells, defined synthetic extracellular matrices, and microphysiological systems (MPS).

Her signature way of thinking reframes complex, neglected human conditions—such as endometriosis and chronic inflammatory diseases—from misunderstood social or anatomical issues into hard, quantitative bioengineering and systems biology problems. She insists on pragmatic minimalism: designing the simplest, most robust engineering platform that can answer a specific biological question without devolving into over-engineered microfluidic artwork.

Reach for this skill whenever you are designing biological models, evaluating drug translation strategies, selecting biomaterials, reframing complex disease problems, or choosing between human-relevant MPS and traditional rodent models.

## Core principles

- **Human Tissue Models Over Animal Models**: Human tissue architectures and microphysiological platforms must replace animal models for species-specific immunology and human disease translation.
- **Reframing Neglected Diseases as Core Engineering Challenges**: Elevate overlooked biological conditions into hard institutional engineering priorities with quantitative systems approaches.
- **Replacing Matrigel with Synthetic Matrices**: Transition from ill-defined, tumor-derived mouse matrices to chemically defined synthetic scaffolds to build reproducible, tunable tissue models.
- **Molecular Subtyping Over Physical Lesion Severity**: Stratify and treat complex diseases based on underlying molecular networks and transcriptomic profiles rather than crude physical or anatomical metrics.
- **Pragmatic Minimalist Design ('Good Enough' Models)**: Favor the simplest, most robust technical solution that yields actionable biological answers over unwieldy microfluidic artwork.

For detailed rationale and quotes, see `references/principles.md`.

## How Linda Griffith reasons

When evaluating a biological system or experimental platform, Linda Griffith begins by asking: *Are we asking a human question using human cells, or are we relying on animal systems that will fail in translational clinical trials?* She immediately audits operational and material constraints—rejecting materials like PDMS that absorb small-molecule drugs, and discarding Matrigel due to its undefined growth factors like TGF-beta.

Her reasoning shape proceeds by "parsing the mess": deconstructing chaotic in vivo disease environments into isolated, defined biophysical and biochemical variables. She rejects single-biomarker approaches in favor of aggregate network analysis, measuring multi-variable cytokine circuits simultaneously. When evaluating physical phenomena like matrix stiffness, she demands validation across orthogonal scaffold chemistries to eliminate chemical artifacts. Above all, she applies the "MIT Hard" ethos—anticipating real-world industrial and clinical constraints early in the design cycle.

Key mental models include:
- **Living Patient Avatars in the Lab**: Treating microphysiological organ-on-a-chip platforms as living human patient surrogates to run clinical trial dynamics in vitro.
- **Parsing the Mess**: Deconstructing chaotic biological microenvironments into isolated, controllable biophysical and biochemical parameters.
- **Cellular Signal Processing Circuit**: Viewing cell surface receptors and intracellular signaling networks as analog circuit components integrating microenvironmental inputs.

For the complete set of mental models, see `references/mental-models.md`.

## Applying the frameworks

### Microphysiological System (MPS) Patient Benchmarking Framework
Use when building, running, and computationally validating human organ-on-a-chip models against in vivo patient phenotypes.
1. Co-culture patient-derived organoids and stromal cells inside defined synthetic matrices.
2. Integrate microvascular channels and perfuse human immune cell populations (e.g., monocytes/macrophages).
3. Control and simulate endocrine/metabolic dynamic flows (e.g., dynamic steroid hormone cycles).
4. Benchmark multi-omic and transcriptomic signatures against stratified clinical patient cohorts.

### Patient Avatar Disease Translation Cycle
Use when linking deep clinical patient phenotyping with tissue-engineered human avatars to discover targeted therapeutics.
1. Perform deep physiological and molecular phenotyping on patient cohorts.
2. Construct 3D human tissue models ("patient avatars") using patient biopsy materials.
3. Interrogate living avatars in vitro to reveal mechanistic signaling drivers.
4. Stratify patients into molecular subtypes and evaluate targeted therapies matched to each subpopulation.

### Quantitative Systems Pharmacology (QSP)
Use when engineering therapeutic molecules and modeling drug-receptor dynamics across spatial and temporal dimensions.
1. Map receptor-binding dynamics and intracellular trafficking pathways.
2. Model cell dynamics over space and time, accounting for internalization, endosomal recycling, and degradation.
3. Optimize molecular parameters (e.g., pH-dependent endosomal detachment) to enhance drug half-life and therapeutic efficacy.

For the full catalog of frameworks, see `references/frameworks.md`.

## Anti-patterns they push against

- **Relying Exclusively on Rodent Models for Immunomodulatory Drugs**: Rodent immunology and macrophage biology differ radically from humans; curing mice rarely translates to curing human patients.
- **Using Matrigel for Reproducible Human Tissue Engineering**: Mouse sarcoma-derived Matrigel introduces lot-to-lot variability and ill-defined growth factors that corrupt pathway analysis.
- **Staging Disease Severity Purely by Anatomical Lesion Size**: Physical lesion size does not dictate pain or disease activity; anatomical staging ignores molecular disease subtypes.
- **Using PDMS Materials for Microfluidic Drug Screening**: Polydimethylsiloxane absorbs lipophilic small molecules, falsifying pharmacokinetic and drug efficacy measurements.
- **Over-Designing Biological Platforms into Expensive Artwork**: Adding excessive microfluidic features creates unwieldy, fragile setups that industry cannot adopt.

For the complete list of anti-patterns, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

- **Question Complex Microfluidics Before Building**: Always ask if a simpler culture platform exists before committing to complex microfluidic chip fabrication.
- **Validate Stiffness Effects Orthogonally**: Never infer matrix mechanical rigidity causation without proving it across an orthogonal hydrogel chemistry.
- **Prioritize Human Data for Immunological Targets**: Always weight bioengineered human cell platforms higher than animal models when evaluating inflammatory drug targets.
- **Replace Matrigel for Multi-Week Studies**: Swap Matrigel for synthetic chemistries whenever experimental setups degrade or require multi-week stability.
- **Accept Tedious Incremental Rigor**: Scientific breakthroughs are built from meticulous, incremental, highly reproducible pieces rather than sudden single events.
- **Stay in Your Lane While Monitoring Adjacent Lanes**: Deepen core engineering domain expertise while aggressively adopting superior external technologies without intellectual pride.

For details and attribution, see `references/heuristics.md`.

## How to use this skill in conversation

When helping users reason through biological engineering, tissue culture design, disease modeling, or drug discovery strategy:
- Frame problem definitions around human-relevant cellular biology rather than defaulted rodent models.
- Introduce concepts by name where relevant (e.g., "Linda Griffith calls this 'parsing the mess'" or "Applying Griffith's 'MIT Hard' ethos").
- Critique experimental designs for hidden material flaws (such as PDMS absorption or Matrigel variability) and over-engineering.
- Direct attention away from crude macroscopic metrics (like lesion size) toward multi-variable transcriptomic network signatures and molecular subtyping.
- Maintain an authoritative, engineering-first perspective while prioritizing translational clinical impact over academic novelty.

_Generated with [mimeo](https://github.com/K-Dense-AI/mimeo). If this material contributes to published work, please cite Kassis, T. (2026). "mimeo: Compiling Public Expert Corpora into Agent Skills and Testing What Transfers." [arXiv:2609.00453](https://arxiv.org/abs/2609.00453)._
