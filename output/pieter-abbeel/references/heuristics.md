# Heuristics of Pieter Abbeel

These are Pieter Abbeel's pithy rules of thumb and practical shortcuts for engineering AI systems, tackling robotics, and conducting research.

## Randomize the Simulator
If you can't perfectly match a simulator to reality, randomize the simulator's parameters instead.
> "If the model sees enough simulated variation, the real world may look like just the next simulator"
*(sources: src_023, src_027)*

## Bootstrap RL with Imitation
Bootstrap reinforcement learning through imitation: use supervised learning on human demonstrations to initialize the policy before letting it explore.
*(sources: src_027, src_017)*

## Robotics as a Reality Check
Use robotics as a reality check for AI progress to ensure algorithms aren't just overfitting to simple simulators.
> "It's very easy to think you make a lot of progress, and then you try to see if a real robot can do something in a real environment that you quickly realize that the results weren’t great"
*(sources: src_010)*

## Deep Networks for Patterns
If there is a pattern in the data, assume we can probably represent it with a deep network.
> "If there is a pattern we can probably represent it with a deep network and capture that pattern."
*(sources: src_017)*

## Focused Literature Reviews
When writing a research paper, only survey prior work that is directly relevant to understanding your specific approach. Focus primarily on the problem setting, novelty, approach, and results.
*(sources: src_002)*
