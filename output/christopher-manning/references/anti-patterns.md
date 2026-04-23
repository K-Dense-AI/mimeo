# Anti-Patterns

These are the traps, misconceptions, and flawed approaches that Christopher Manning explicitly warns against in AI research and discourse.

## Assuming Scaling Leads to AGI
Believing that simply making current Transformer models bigger will inevitably lead to Artificial General Intelligence. Current models lack actionable world models and true reasoning/planning capabilities. They rely on advanced pattern matching, which hits a ceiling for higher-level cognition. Meta-learning and adaptability are more promising paths.
> "people have been trying to sell the story that just keep with what we have and make it bigger and bigger and bigger and we'll solve AI which I don't actually believe myself"
*(sources: src_020, src_028)*

## Manually Encoding Linguistic Rules
Explicitly building formal grammars or hardcoding rules of human language into computing systems. Modern machine learning approaches have shifted away from hardcoded rules toward building models directly from data. Formal grammars are idealizations that miss nuance, whereas large neural networks naturally learn grammar on their own.
*(sources: src_019, src_011)*

## The Stochastic Parrot Dismissal
Claiming language models cannot possess meaning or learn structure because they only process form. This relies on an overly strict internalist philosophy of language and underestimates the capacity of large neural networks to induce rich, hierarchical linguistic structures purely from self-supervised word prediction.
*(sources: src_013, src_042)*

## Trusting LLM Reasoning Blindly
Assuming LLMs can truly reason or that everything they say is correct. LLMs are often just pattern-matching reasoning templates. If you change the variables slightly in a way that breaks the template, they make glaring, non-sensical errors and can confidently hallucinate false information.
> "I actually don't think we should say at the moment that large language models can reason they can behave in ways that it looks like they can reason"
*(sources: src_023, src_028)*

## Academic Compute Chasing
Academic researchers trying to compete with big tech companies by building massive models that require huge amounts of compute. Universities have vastly fewer resources (GPUs and compute) than industry labs, making it impossible to win on scale or speed.
*(sources: src_016)*

## Confusing Vast Knowledge with Intelligence
Assuming that memorizing massive amounts of information equates to intelligence. Memorizing massive amounts of information allows a system to interpolate across what it has seen, but it does not equip the system to adapt, learn, or infer causality in new, unseen circumstances.
*(sources: src_011)*

## Near-term AGI Doomerism
Making governance or leadership decisions based on 'EA-infused fantasy lands' or believing in near-term AGI timelines. It leads to irrational fears, such as believing there is a 50/50 chance everyone gets 'paperclipped & dies', which undermines sound leadership and ignores historical realities of AI progress.
*(sources: src_018)*

## Relying on Formal Reasoning Systems
Historically assuming AI needed formal representations and knowledge graphs to achieve intelligence. Human language text itself proved to be a far more effective, scalable, and natural knowledge encoding than formal logic systems.
> "this informal ubiquitous probably 100,000 years old technology invented by humans of human languages has completely won over the formal languages of recent centuries"
*(sources: src_011)*
