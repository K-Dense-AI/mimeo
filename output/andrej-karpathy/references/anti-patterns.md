# Anti-Patterns

Practices, assumptions, and workflows that Andrej Karpathy explicitly warns against when dealing with AI and software engineering.

## Jumping to Full Autonomy
Jumping straight to fully autonomous AI agents without human supervision. LLMs are fallible and hallucinate. If they generate massive outputs (like a 10,000-line code diff), the human becomes a bottleneck trying to verify it, defeating the purpose.
(sources: src_010, src_017)

## Assuming Linear Intelligence Scaling
Assuming LLM capabilities scale linearly like human intelligence. LLMs possess 'jagged intelligence'—they can solve complex math but fail at simple comparisons. Blind trust leads to catastrophic failures on seemingly easy tasks.
(sources: src_002, src_055)

## Relying on Automated Tools Without Understanding
Relying on automated tools (like PyTorch autograd) or copy-pasting code without building from scratch to understand the underlying math. It prevents the developer from building the strong intuitive understanding of gradient flow necessary to confidently debug and innovate on modern neural networks.
(sources: src_029, src_044)

## Anthropomorphizing LLMs
Thinking of ChatGPT as a magical, sentient AI or assuming artificial neural networks function exactly like biological brains. Biological neurons are complex dynamical processes with memory, whereas artificial neurons in an LLM are extremely simple, stateless mathematical expressions that just transform inputs to outputs to simulate a human labeler.
(sources: src_012)

## Endless Chat Threads
Keeping a single, endlessly long chat going for multiple unrelated topics. It fills up the context window with irrelevant tokens, which distracts the model, decreases its accuracy, and makes generating the next token slower and more expensive.
(sources: src_017)

## Forcing Complex Logic in a Single Token
Forcing an LLM to answer a complex math or logic question immediately in a single token. There is a finite, roughly fixed amount of computation (layers) that happens per token. The model cannot squeeze arbitrary amounts of computation into a single forward pass.
(sources: src_012)

## Trusting AI Demos
Trusting AI demos as proof of imminent product readiness. Demos only represent the first 90% of reliability. The remaining 'nines' require massive, constant amounts of work, especially in domains where the cost of failure is high.
(sources: src_000)
