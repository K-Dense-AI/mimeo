# Frameworks

Karpathy uses structured frameworks to evaluate AI progress, design educational materials, and build agentic workflows.

## The Autonomy Slider
A framework for evaluating the impact of AI tools on programming and knowledge work by progressively raising the layer of abstraction.
Steps: 1. Provide a traditional interface for manual work. 2. Integrate LLMs to handle larger chunks of context. 3. Build an application-specific GUI to allow humans to easily audit the AI's work. 4. Provide varying levels of autonomy (e.g., tab completion vs. full repo rewrite) that the user can tune based on task complexity.
(sources: src_010, src_029, src_002, src_055)

## Vibe Coding
A new paradigm of software development where humans direct autonomous agents via natural language.
Steps: 1. Use a dedicated AI code editor (like Cursor) with access to your local file system. 2. Use the 'composer' feature. 3. Give high-level natural language commands. 4. Sit back and let the agent edit across multiple files autonomously, verifying the results.
> "Vibe coding just refers to letting um giving in giving the control to composer and just telling it what to do"
(sources: src_017, src_021, src_055)

## Untangling Knowledge
A pedagogical framework for designing educational material by isolating first-order components.
Identify the core essence of the system. Create the simplest possible implementation (e.g., a 100-line script). Present the pain/problem before the solution. Prompt the student to guess the solution. Tack on second-order terms (efficiency, scaling) only after the core is understood.
> "I'm trying to find, what is the thing that matters? What is the first-order component? How can I simplify it? How can I have a simplest thing that shows that thing, shows it in action, and then I can tack on the other terms?"
(sources: src_000)

## The March of Nines
A framework for evaluating the progress of safety-critical AI systems from demo to deployed product.
Recognize that a successful demo (working 90% of the time) is only the first 'nine'. Achieving each subsequent nine of reliability (99%, 99.9%, 99.99%) requires a constant, massive amount of additional work to patch edge cases.
> "What takes the long amount of time and the way to think about it is that it's a march of nines. Every single nine is a constant amount of work."
(sources: src_000)

## The Three Stages of LLM Training
The standard pipeline for transforming raw internet text into a helpful conversational AI assistant.
1. Pre-training: Train on internet documents to build a base model (an internet document simulator) that acts as a knowledge base. 2. Supervised Fine-Tuning (SFT): Train on human-curated conversations to create an assistant that imitates expert behavior and formatting. 3. Reinforcement Learning (RL): Allow the model to practice generating many solutions, checking answers, and reinforcing the token sequences that reliably lead to correct results.
(sources: src_012)
