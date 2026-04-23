# Heuristics and Rules of Thumb

Practical, day-to-day rules Andrej Karpathy applies when coding, teaching, and interacting with AI systems.

## Build to Understand
If you can't build it from scratch, you don't truly understand it. Don't just read blog posts or copy-paste code. Build the repository, arrange the components, and get it to work to confront the micro-details you don't actually understand.
(sources: src_000, src_044, src_029)

## AI Generates, Human Verifies
Design workflows where the AI does the heavy lifting of generation, and the human focuses purely on verification.
(sources: src_010, src_002)

## Escalate to Thinking Models
Try non-thinking models first because they are fast; switch to a thinking (reasoning) model only if the response fails on math, code, or logic.
(sources: src_017)

## Wipe the Context Window Frequently
Always start a new chat whenever you are switching topics to clear the model's working memory and prevent distraction.
(sources: src_017)

## Paste Reference Text
Paste reference text directly into the prompt rather than relying on the model's internal memory. The context window acts as working memory, giving the model direct access to the information, which produces significantly higher quality results.
> "when it's in the context window the model has direct access to it and can exactly it doesn't have to recall it it just has access to it"
(sources: src_012)

## Demo is works.any(), Product is works.all()
Recognize the massive gap between a working prototype and a reliable, production-ready product. Assume demos only represent the first 90% of the work; the remaining 10% will take 10x the effort.
> "Demo is works.any(), product is works.all()"
(sources: src_002, src_000)

## Force Step-by-Step Reasoning
Force the model to show its work step-by-step to spread out computation over multiple tokens. Because models have limited compute per token, asking them to create intermediate results allows them to 'think'.
> "models need tokens to think distribute your competition across many tokens ask models to create intermediate results"
(sources: src_012)

## Present Pain Before Solution
In teaching, always present the pain or problem before you present a solution. Don't present the solution before giving the student a shot to guess it.
> "Present the pain before you present a solution."
(sources: src_000)
