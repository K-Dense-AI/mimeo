# Mental Models

Karpathy's mental models demystify AI, stripping away the magic to reveal the underlying statistical and computational realities.

## Jagged Intelligence
The unintuitive reality that state-of-the-art LLMs can perform highly complex tasks while simultaneously failing at very simple, dumb problems. Because LLMs spike in capability around verifiable domains (like math or code), they can simultaneously act as a genius polymath and a confused grade schooler. Their capabilities do not correlate linearly like human intelligence.
> "Some things work extremely well (by human standards) while some things fail catastrophically (again by human standards), and it's not always obvious which is which"
(sources: src_010, src_002, src_055)

## Weights as 'Hazy Recollection' vs. Context Window as 'Working Memory'
Information stored in a neural network's weights is highly compressed and hazily recalled, whereas information placed in the context window is directly and immediately accessible. Asking an LLM about a book from its training data yields roughly correct but hazy answers (long-term memory). Pasting a full chapter into the context window yields precise, accurate answers (working memory).
> "knowledge in the parameters of the neural network is a vague recollection the knowledge in the tokens that make up the context window is the working memory"
(sources: src_000, src_029, src_012)

## Anterograde Amnesia / People Spirits
Treating LLMs as stochastic simulations of humans that possess encyclopedic memory but suffer from severe cognitive deficits, like the inability to form new long-term memories. LLMs are like a coworker who cannot consolidate long-running expertise after training. They rely entirely on their short-term memory (the context window), much like the protagonists in Memento or 50 First Dates.
> "LLMs are a bit like a coworker with Anterograde amnesia - they don't consolidate or build long-running knowledge or expertise once training is over and all they have is short-term memory (context window)."
(sources: src_010, src_002)

## The Iron Man Suit
A metaphor for partial autonomy: AI products should act as an extension of the user, providing augmentation while keeping the human in the driver's seat. Instead of building fully autonomous robots that operate entirely on their own, we should build 'suits' that augment human capabilities (strength, tools, sensors, information) and allow the user to tune the level of autonomy.
> "It's less Iron Man robots and more Iron Man suits that you want to build."
(sources: src_010, src_002)

## First-Order Approximations (The Spherical Cow)
Identifying the fundamental mechanism of a system and intentionally ignoring noise, edge cases, and efficiency details until the core is understood. For example, Micrograd is a 100-line Python script that serves as the first-order approximation of neural network training, showing backpropagation perfectly while ignoring tensors and memory movement.
> "I'm trying to find, what is the thing that matters? What is the first-order component? How can I simplify it?"
(sources: src_000)

## Tokens, not Characters
LLMs do not see text the way human eyes do; they see chunks of text (tokens), which explains their failure at simple character-level tasks. When asked to print every third character of a word or count the 'r's in 'strawberry', the model fails because it only sees a few token IDs, not the individual letters.
> "I really encourage you to think of these not as numbers but as unique IDs or like unique symbols so maybe it's a bit more maybe it's better to actually think of these to replace every one of these with a unique Emoji"
(sources: src_012)

## Summoning Ghosts vs. Evolving Animals
A lens for understanding that LLM intelligence is fundamentally alien compared to human intelligence. Unlike human neural nets optimized for jungle survival (animals), LLMs are optimized for imitating text and solving math puzzles, resulting in alien entities (ghosts) that shouldn't be judged through an evolutionary lens.
> "We're not \"evolving/growing animals\", we are \"summoning ghosts\"."
(sources: src_055)
