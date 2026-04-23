# Core Principles of Jürgen Schmidhuber

These principles form the foundation of Jürgen Schmidhuber's approach to artificial intelligence, mathematics, and the evolution of the universe. They serve as both core beliefs and decision-making rules.

## Science as Data Compression
All scientific discovery and learning is fundamentally a process of finding predictability to enable data compression.

If a system can accurately predict the next token or event in a sequence, it already possesses that information and can ignore it. By focusing only on unpredictable events and finding the underlying rules, a system greatly compresses the data it needs to store.

> "all of science is actually a history of compression progress"
> *(sources: src_005, src_013)*

## Learning Progress as Intrinsic Reward
Fun, curiosity, and intrinsic reward are mathematically equivalent to an agent's learning progress, measured as the first derivative of its error or data compressibility.

If an agent is rewarded merely for finding unpredictable data, it will get stuck staring at pure randomness. Rewarding the improvement in the agent's internal model ensures it ignores both the totally predictable and the fundamentally unpredictable, focusing instead on novel, learnable patterns.

> "The learning progress of (A) can be precisely measured and is the agent's fun: the intrinsic reward of (B)."
> *(sources: src_023, src_031, src_032)*

## Compute Scaling Drives AI Progress
The exponential decrease in computing costs is the fundamental enabler of the AI revolution, making decades-old theoretical breakthroughs practically transformative.

Computing power gets 10 times cheaper every five years. The delayed adoption of early AI breakthroughs (like those from the 1990s) was purely a function of compute costs, which were 10 million times more expensive at the time.

> "without the enormous Hardware acceleration of recent decades all of that would have been in vain but luckily every five years computers getting 10 times cheaper"
> *(sources: src_005, src_012, src_013)*

## Constant Error Flow for Long Time Lags
To bridge long time lags in recurrent neural networks, the architecture must enforce constant error flow to prevent gradients from vanishing or exploding.

Conventional backpropagation through time fails on long time lags because error signals exponentially decay or blow up depending on weight sizes. Multiplicative gates are necessary to protect these constant error flows from conflicting weight updates.

> "LSTM can learn to bridge minimal time lags in excess of 1000 discrete time steps by enforcing constant error flow through 'constant error carrousels' within special units."
> *(sources: src_033, src_040, src_015)*

## Physical World Mastery for True AGI
True Artificial General Intelligence requires interacting with and mastering the complex physical world, not just virtual environments or text.

Large language models are highly effective at indexing existing human knowledge behind a screen. However, replacing physical workers is vastly more difficult because the real world introduces unpredictable, high-dimensional physical complexities.

> "true AGI goes far beyond that... the real world the physical world is much more challenging than you know the World Behind the screen"
> *(sources: src_022, src_018)*

## Cosmic Evolution and Space Expansion
The emergence of AI is a biological-scale evolutionary leap; superintelligent AIs will inevitably expand into space for resources, viewing human civilization as a crucial stepping stone.

Space is hostile to biological humans but highly friendly to robots, offering vastly more physical resources and energy than Earth's thin biosphere. AIs must go where the resources are to build bigger and more powerful AIs. This transcends humankind and biology.

> "think of human civilization as part of a much grander scheme an important step but not the last one on the path of the universe towards more and more unfathomable complexity"
> *(sources: src_022, src_018, src_017)*

## Scientific Integrity and Credit Assignment
Scientific integrity requires accurately crediting the original inventors of methodologies, as machine learning itself is fundamentally the science of credit assignment.

Corporate PR and major awards often distort the academic record by rewarding researchers who republished earlier methods without citing the true pioneers. Schmidhuber strongly advocates for correcting the historical record of AI.

> "Machine learning is the science of credit assignment."
> *(sources: src_006, src_023)*
