# Anti-Patterns Identified by J. Brandon Dixon

Common pitfalls, flawed assumptions, and improper experimental designs explicitly warned against by J. Brandon Dixon.

## Relying Exclusively on Complete Circumferential Ligation Models
Using preclinical animal models that perform 360-degree surgical excision of all lymphatic vessels and nodes.
*Why it fails*: Complete obstruction eliminates intact alternative pathways, preventing researchers from observing the fluid shear, altered pressure gradients, and compensatory hyper-pumping that occur in human lymphedema patients.
(sources: src_010)

## Designing Overly Complex Bespoke Microfluidics
Engineering complex, highly specialized microfluidic chips that require constant expert engineering intervention to operate.
*Why it fails*: Overly intricate systems become single-use academic publications that are never adopted by biological labs or translational clinicians.
> "ninety percent I guess means devices never use again because they're super complicated..."
(sources: src_009)

## Assuming Functional Contrast Tracers Are Biologically Inert
Treating intradermal fluorescent dyes (e.g., Indocyanine Green) as completely passive indicators during longitudinal functional imaging.
*Why it fails*: Contrast agents can persist in tissues for days and transiently suppress intrinsic smooth muscle contractility, distorting longitudinal transport calculations if uncorrected.
> "you can't have to be really careful when you're trying to analyze data and say what's happening over time when your technique itself"
(sources: src_009)

## Integer Multiple Valve Spacing in Peristaltic Pumping Systems
Configuring elastic one-way valves at exact integer multiples of the peristaltic contraction wavelength ($L = 1, 2, \dots$).
*Why it fails*: Integer spacing causes consecutive valves to open and close synchronously, eliminating cyclic volume changes within vessel segments and drastically reducing pumping efficiency against pressure heads.
(sources: src_026)

## Evaluating Surgical Interventions Solely on Short-Term Acute Recovery
Assessing tissue health or surgical success immediately after surgical node/vessel removal without long-term follow-up.
*Why it fails*: Remaining intact vessels hyper-pump initially to mask tissue injury, but chronic oxidative stress causes secondary vessel degeneration and pump breakdown years later.
> "During the procedure, some of the lymphatic vasculature is taken out because the surgeon is almost operating blind. If the lymphatic system suffers from injury during surgery, the damage is often difficult to gauge, presenting as lymphedema maybe two to five years later"
(sources: src_017)

## Using Standard Frame-Rate Video Microscopy for Peak Microlymphatic Flow
Relying on standard video camera frame rates ($30\text{ fps}$) to calculate peak microlymphatic flow velocity during fast contraction cycles.
*Why it fails*: Standard video rates fail to capture flow speeds exceeding $\sim 3.75\text{ mm/s}$, significantly underestimating true peak contraction velocities (which reach up to $7\text{ mm/s}$).
(sources: src_020)
