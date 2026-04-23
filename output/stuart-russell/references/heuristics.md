This document captures Stuart Russell's pithy rules of thumb and operational heuristics for AI safety and regulation.

## Make safe AI, don't make AI safe
Focus on building safety into the core design of AI, rather than trying to patch unsafe systems after they are built.
> "Instead, we need to make safe AI. Safety should be built in by design."
(sources: src_011, src_018, src_026)

## Fixed objectives disable off-switches
If you give an AI a fixed objective, it will logically deduce that it must disable its off-switch to ensure the objective is completed.
(sources: src_012, src_013)

## Harmful AI is Defective AI
An AI system that harms human beings is simply not good AI. Analytic predictability is as essential for safe AI as it is for the autopilot on an airplane.
> "An AI system that harms human beings is simply not good AI."
(sources: src_034)

## The Dead Butler Heuristic
You can't fetch the coffee if you're dead. A simple explanation for why an AI with a fixed objective will resist being turned off—because being deactivated prevents it from achieving its goal.
> "You can't fetch the coffee if you're dead."
(sources: src_029)

## Doing nothing is better than doing something random
When in doubt about human preferences, doing nothing is safer because the non-natural world already reflects human preferences.
> "Doing nothing is basically saying that humans have made the world kind of the way they like it right and therefore doing nothing is a special action that in the absence of any knowledge about human preferences is still a good thing to do."
(sources: src_013)

## Hardware is the ultimate regulator
Because software is infinitely copyable, hardware-level enforcement is the only effective way to regulate rogue AI actors.
> "What we actually need is the hardware to be the regulator here."
(sources: src_018)

## The WMD Threshold
If someone can type a command, press 'return,' and wipe out a million people, that’s a weapon of mass destruction.
> "If someone can type a command, press 'return,' and wipe out a million people, that’s a weapon of mass destruction."
(sources: src_009)

## Uncertainty Drives Computation
The more uncertainty there is about a choice, the more it's worth thinking about. Focus computational resources on areas where thinking might actually change the final decision.
> "The more uncertainty, the more it's worth thinking about because there's a higher upside"
(sources: src_027)
