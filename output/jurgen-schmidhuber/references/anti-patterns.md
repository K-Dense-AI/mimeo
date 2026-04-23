# Anti-Patterns Schmidhuber Pushes Against

These are the specific traps, misconceptions, and bad practices that Jürgen Schmidhuber explicitly warns against in AI research and philosophy.

## Equating LLMs with true AGI
Believing that mastering text and virtual environments is equivalent to mastering the vastly more complex physical world.

LLMs are merely clever ways of indexing existing human-generated knowledge. True AGI requires the much harder task of interacting with and mastering the physical world, which is why automating plumbing is harder than automating desktop work.
> "At the moment the only AI that works well is behind the screen and it's good for desktop workers but not really for people working in the physical world."
> *(sources: src_022, src_018)*

## Obsessing over AI existential risk over nuclear weapons
Focusing on hypothetical AI doomsday scenarios while ignoring the proven, immediate threat of existing hydrogen bombs.

Hydrogen bombs already have the capacity to wipe out civilization in a few hours without any AI, making them a far more immediate and proven existential threat.
> "The threat coming from AI weapons seems to pale in comparison to the much older threat from nuclear hydrogen bombs that don’t need AI at all."
> *(sources: src_022, src_018)*

## Rewarding compression performance instead of progress
In intrinsic motivation, rewarding an agent for finding perfectly predictable data rather than rewarding the improvement in its ability to predict novel patterns.

If you just reward compression performance, the agent will seek out perfectly predictable but boring data (like a blank wall). The important thing is the *improvements* of the compressor/predictor, which drives the agent to seek novel, learnable patterns.
> "Generate intrinsic curiosity reward or creativity reward for the controller in response to improvements of the predictor or history compressor."
> *(sources: src_045)*

## Plagiarism and Corporate PR in Science
Republishing existing methodologies without citing the original creators, or allowing corporate PR to dictate scientific history.

It distorts the academic record, turns unintentional omissions into deliberate plagiarism, and deprives the true pioneers of scientific credit.
> "Sadly, the Nobel Prize in Physics 2024 for Hopfield & Hinton is a Nobel Prize for plagiarism. They republished methodologies developed in Ukraine and Japan... without citing the original papers."
> *(sources: src_006, src_023)*

## Treating Symbolic and Sub-symbolic AI as Opposed
Treating symbolic AI and sub-symbolic (neural network) AI as fundamentally different or opposed fields.

It ignores the mathematical reality that neural networks can emulate logic gates (NAND gates) and CPUs, making the boundary between the two approaches artificial and blurred.
> "For me, there is no difference between symbolic AI and sub symbolic AI because I cannot see the boundary between them."
> *(sources: src_005)*

## Using Standard Recurrent Backpropagation for Long Time Lags
Relying on traditional recurrent network algorithms for complex, long-time-lag tasks.

It suffers from 'insufficient, decaying error backflow,' causing the learning process to take a very long time or fail entirely on complex tasks. LSTM's constant error flow is required instead.
> "Learning to store information over extended time intervals by recurrent backpropagation takes a very long time, mostly because of insufficient, decaying error backflow."
> *(sources: src_033, src_040)*

## Fearing a monolithic superintelligence
Assuming AI will become a single, human-exterminating entity, ignoring that it will form a diverse, competitive, and collaborative ecology.

It ignores the reality of AI ecology, which will be highly diverse, featuring intense competition and collaboration among AIs with rapidly evolving, self-invented goals.
> "expect an incredibly diverse variety of AIS trying to achieve all kinds of self-invented goals"
> *(sources: src_022)*
