# Core Principles

Andrej Karpathy's principles blend a deep technical understanding of neural networks with a pragmatic approach to software engineering and human-computer interaction.

## Build from Scratch to Understand
To truly understand deep learning, you must manually build neural networks and their core algorithms (like backpropagation) from scratch without relying on automated tools or copy-pasting. Manually implementing components builds a strong intuitive understanding of how gradients flow and how neural nets are optimized. There are micro-details and gaps in knowledge that only reveal themselves when you are forced to arrange the components yourself.
> "If I can't build it, I don't understand it... I 100% have always believed this very strongly, because there are all these micro things that are just not properly arranged and you don't really have the knowledge."
(sources: src_007, src_029, src_044)

## Software 3.0 is Eating 1.0 and 2.0
Programming is shifting from writing explicit code (1.0) and training neural network weights (2.0) to prompting Large Language Models in natural language (3.0). Prompts are becoming the new programs, which will lead to a massive rewrite of existing software stacks. Software engineers should strive to be fluent in all three paradigms, transitioning fluidly between them depending on the functionality required.
> "Software 3.0 is eating 1.0/2.0"
(sources: src_010, src_002)

## Keep the AI on a Leash
LLMs are fallible and can easily get lost; humans must remain in the loop to verify their work in small, concrete chunks. Instead of asking an AI for a massive 10,000-line code diff, work incrementally. Scrutinize LLM-generated code like you would a very junior, absent-minded data analyst who might make sneaky implicit assumptions.
> "we have to keep the AI on the leash. We I think a lot of people are getting way over excited with AI agents and uh it's not useful to me to get a diff of 10,000 lines of code to my repo."
(sources: src_010, src_017)

## Agency Over Intelligence
In an era where AI commoditizes intelligence, human agency becomes the most powerful and scarce resource. Society has historically venerated IQ and raw intelligence, but the ability to take action, direct systems, and drive outcomes is now the true differentiator.
(sources: src_021)

## Tokens are Compute
A neural network has a finite, roughly fixed amount of computation it can perform per token. To solve complex problems, reasoning must be distributed across many tokens. Asking a model to solve a complex problem in a single token will fail because it cannot squeeze arbitrary computation into one forward pass. Generating intermediate results allows the model to 'think'.
> "we actually have to distribute our reasoning and our computation across many tokens because every single token is only spending a finite amount of computation on it"
(sources: src_012)

## English as the Ultimate Interface
Natural language is replacing traditional syntax as the primary programming language and label space. Whether prompting advanced LLMs to write code or using language as a rich, flexible label space for computer vision, natural language enables significantly easier and more expressive human-computer interaction.
> "The hottest new programming language is English"
(sources: src_004, src_021)

## Base Models are Internet Document Simulators
A base model is trained purely to predict the next token on internet text. It acts as a glorified autocomplete and is not an assistant. Base models will not answer questions directly unless prompted cleverly to look like a web page, because they lack the conversational formatting of an assistant.
> "the base models are not very often released because they're kind of just only a step one of a few other steps that we still need to take to get in system"
(sources: src_012)
