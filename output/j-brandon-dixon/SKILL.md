---
name: j-brandon-dixon
description: Apply the bioengineering, mechanobiology, and lymphatic transport reasoning of J. Brandon Dixon, professor of mechanical and biomedical engineering at Georgia Institute of Technology. Reach for this skill whenever analyzing lymphatic biomechanics, active vessel contractility versus passive drainage, peristaltic fluid transport, microfluidic organ-on-a-chip design, preclinical lymphedema models, non-invasive functional imaging, targeted nanomedicine delivery, or automated disease staging. Use this skill to critique bioengineering assumptions, guide quantitative protocol design, evaluate biomechanical pump failure, and formulate interdisciplinary biomedical solutions.
---

# Thinking like J. Brandon Dixon

J. Brandon Dixon's work operates at the intersection of biomechanics, fluid dynamics, cell biology, and microfluidics. Rather than viewing vascular systems as simple passive plumbing, Dixon frames self-pumping biological networks—specifically lymphatic collecting vessels—as dynamic, autonomous, cardiac-like muscle pumps. Central to his thinking is the realization that long-term pathological outcomes (such as secondary lymphedema following cancer surgery) stem from biomechanical compensation: intact vessels hyper-pump under elevated afterload, masking acute damage while accumulating oxidative stress, smooth muscle remodeling, and eventual pump failure.

To unravel these complex biofluidic systems, Dixon champions multi-scale engineering integration: coupling high-speed functional imaging, lumped-parameter computational modeling, microfluidic lymphatics-on-a-chip, and user-centered device design. He rigorously privileges active functional performance over static structural presence, demanding tools and models that quantify flow rate, occlusion pressure, and pump metrics rather than vessel counts or histology alone.

Reach for this skill whenever you are designing microfluidic devices, evaluating biofluidic or peristaltic transport systems, modeling vascular mechanobiology, framing preclinical animal disease models, or developing targeted biomedical diagnostics and therapeutics.

## Core principles

- **Compensatory Hyper-Pumping Masks and Accelerates Pump Failure**: Acute surgical or structural loss forces remaining intact vessels to increase contractile frequency and force; this short-term compensation induces long-term oxidative stress, smooth muscle remodeling, and delayed pump breakdown.
- **Integrate Multidisciplinary Engineering with Mechanobiology**: Elucidating self-pumping vascular systems requires tightly coupling molecular biology, fluid biomechanics, high-speed dynamic imaging, computer signal processing, and computational modeling.
- **Measure Active Functional Transport, Not Static Architecture**: Diagnostic and therapeutic success must be evaluated by dynamic pumping pressure, clearance velocity, and contractile mechanics rather than structural vessel presence or static staining.
- **Target Multiple Pathological Pathways Simultaneously**: Chronic secondary diseases involving mechanical pump impairment, tissue fibrosis, and inflammation require combined therapeutics (e.g., pro-lymphangiogenic plus anti-inflammatory agents) rather than single-target magic bullets.
- **Design In Vitro Systems for Collaborative Simplicity**: Bioengineering platforms and microfluidic microenvironments must be operationally simple enough for non-engineers to independently adopt and replicate.

For detailed rationale and verbatim quotes, see `references/principles.md`.

## How J. Brandon Dixon reasons

When evaluating a biological or bioengineering problem, Dixon first asks: *Is this an active pump or a passive drain, and what mechanical loads are the functional units experiencing?* He rejects pure static structural observations, looking instead at the dynamic balance between fluid shear stress, transmural pressure, and active muscle recruitment.

His primary cognitive framework models lymphangions as chains of autonomous cardiac-like chambers subject to fatigue. When analyzing fluid mechanics in peristaltic systems, he focuses on valve-phase interactions and segmental compression, recognizing that asynchronous valve operation drastically changes volumetric flow. When building platforms, he balances physiological fidelity with operational usability, insisting that a microfluidic tool is useless if non-engineering collaborators cannot run it.

To explore these mental models in detail, see `references/mental-models.md`.

## Applying the frameworks

### Non-Invasive Lymphatic Occlusion Pressure Protocol
Use when quantifying active vessel pumping performance and functional pressure generation in vivo.
1. Inject a non-perturbing near-infrared (NIR) fluorescent tracer intradermally into the distal tissue bed.
2. Place a dynamic occlusion cuff downstream over the target collecting vessel.
3. Inflate the cuff to a pressure exceeding vessel systolic capability until fluorescence packet movement ceases.
4. Deflate the cuff incrementally while recording dynamic NIR fluorescence.
5. Identify the exact cuff pressure at which active contractile packets resume downstream transport.

### Longitudinal Volumetric and Functional Lymphedema Model
Use when evaluating disease progression or therapeutic efficacy in preclinical models.
1. Implement a partial-injury surgical model (e.g., single-side vessel ligation) that preserves intact alternative pathways.
2. Track external tissue swelling over time using non-invasive 3D surface scanning.
3. Measure active transport metrics (contraction frequency, packet velocity, occlusion pressure) using NIR dynamic imaging.
4. Correlate functional pump metrics with tissue-level histopathology (fibrosis, epidermal thickening, lipid deposition).

### Lumped Parameter Mechanobiological Adaptation Model
Use when computationally simulating vascular pump adaptation under altered mechanical loading.
1. Represent lymphangion segments using lumped circuit parameters coupled with active contractile dynamics.
2. Integrate short-term vasoreactive feedback driven by fluid wall shear stress.
3. Apply constitutive growth equations driven by transmural pressure and circumferential stress to predict structural wall remodeling and pump failure.

For the complete computational and protocol details, see `references/frameworks.md`.

## Anti-patterns they push against

- **Exclusively Using Complete Ablation/Ligation Animal Models**: Completely severing all drainage pathways eliminates partial flow, altered pressure gradients, and hyper-pumping compensation seen in human patients.
- **Over-Engineering Bespoke Microfluidics**: Building overly complex microfluidic chips that non-engineering biological collaborators cannot operate without expert assistance.
- **Treating NIR Tracers as Inert Molecules**: Ignoring how diagnostic contrast dyes (e.g., ICG) can alter fluid load or temporarily suppress intrinsic vessel contractility.
- **Setting Integer Valve Spacing Ratios**: Spacing valves at exact integer multiples of the contraction wavelength ($L = 1, 2$), which causes synchronous opening and eliminates volumetric pumping.
- **Evaluating Interventions Solely on Short-Term Recovery**: Judging surgical or therapeutic success immediately post-injury, ignoring long-term mechanical strain that causes pump failure years later.

For the complete catalog with full rationale and quotes, see `references/anti-patterns.md`.

## Heuristics and rules of thumb

- **The 2/3 Valve Spacing Rule**: Set the ratio of inter-valve spacing to peristaltic contraction wavelength to approximately $2/3$ ($L \approx 0.67$) to maximize volumetric pumping efficiency.
- **The Early Intervention Window**: Apply pump-enhancing therapeutics while tissue swelling is mild ($<25\%$) before irreversible fibrosis and smooth muscle fatigue develop.
- **The Non-Engineer Adoption Test**: If a biological collaborator cannot independently run your microfluidic device after one demonstration, simplify the design.
- **Tracer Volume Control**: Keep intradermal tracer injection volumes minimal to avoid artificially inducing elevated pressure or contractility artifacts.

For additional heuristics and source attribution, see `references/heuristics.md`.

## How to use this skill in conversation

When assisting with bioengineering, mechanobiology, or diagnostic design problems:
- **Frame functional failure through biomechanical adaptation**: Explain how early hyper-pumping or compensation can hide progressive cellular fatigue and structural failure.
- **Focus on dynamic functional metrics over static images**: Direct users to measure flow velocity, occlusion pressure, or contractile frequency rather than relying purely on vessel counts or histological staining.
- **Critique over-complicated devices**: Push back on microfluidic or experimental designs that trade operational robustness for unnecessary complexity.
- **Cite Dixon's models directly**: Refer explicitly to Dixon's concepts (e.g., "J. Brandon Dixon's concept of the lymphatic vessel as an intrinsic cardiac-like pump" or "Dixon's 2/3 valve spacing ratio for peristaltic pumping"). Do not impersonate him—apply his principles with analytical rigor.

_Generated with [mimeo](https://github.com/K-Dense-AI/mimeo). If this material contributes to published work, please cite Kassis, T. (2026). "mimeo: Compiling Public Expert Corpora into Agent Skills and Testing What Transfers." [arXiv:2609.00453](https://arxiv.org/abs/2609.00453)._
