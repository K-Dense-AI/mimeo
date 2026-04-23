# Core Principles

These principles form the foundation of Christopher Manning's approach to AI, NLP, and research strategy. They serve as both core beliefs about how intelligence works and decision rules for how to build and evaluate systems.

## Adaptability as True Intelligence
True intelligence requires rapid adaptation and continuous learning, not just vast knowledge accumulation. LLMs appear highly intelligent because they have memorized centuries of hard-won human knowledge. However, they lack the human ability to quickly learn and adapt to novel, uncertain environments. Knowing a lot of facts or performing specific tasks well is not enough to constitute general intelligence.
> "the heart of human intelligence is being able to adapt to new situations to very quickly learn new things that's the real intelligence and that's not what large language models are doing"
*(sources: src_013, src_023, src_024, src_028)*

## Language Structure from Data
The hierarchical structure of human language can be learned from observed data alone, without innate machinery. Contrary to traditional Chomskian linguistics, which argues language structure is innate and unlearnable from data alone, modern neural networks (like Transformers) demonstrate that with enough data, models successfully learn syntax, context-free grammars, and coreference relations purely from positive evidence.
> "what precisely what large language models show is that actually you can learn the structure of a human language"
*(sources: src_020, src_028, src_042)*

## Compete on Ideas, Not Compute
Academic researchers should compete on novel ideas and architectural innovations rather than trying to out-compute massive tech companies. University students cannot out-compute massive tech companies. Instead of training huge models on hundreds of GPUs, they should focus on finding fresh problems or solving specific architectural gaps at a modest scale.
> "what a much scarce supply is good ideas and it's very easy to be successful doing things at a modest scale with good ideas"
*(sources: src_016, src_011)*

## NLP as a Domain Science
NLP is fundamentally a domain science focused on language problems, requiring linguistically sophisticated design, not just generic machine learning. Machine learning is not generic heavy lifting; it requires design. NLP researchers are the designers who understand the central domain problems (like compositionality and noncategorical representations), which will not go away regardless of the underlying ML method.
> "Our field is the domain science of language technology; it’s not about the best method of machine learning—the central issue remains the domain problems."
*(sources: src_022, src_044)*

## Modularity Over Pure End-to-End Learning
General intelligence requires modularity and compositional reasoning, not just massive monolithic end-to-end networks. Human brains have distinct regions and components that are repurposed for different tasks. A single monolithic network optimized end-to-end is unlikely to achieve flexible, general language understanding.
> "I believe ultimately that we have to have models of intelligence which have different components in different parts and there is a certain level of modularity"
*(sources: src_016)*

## Self-Supervised Word Prediction
Self-supervised word prediction is a powerful multidimensional signal that forces models to induce rich linguistic structures. Because predicting a missing word requires an understanding of syntax, semantics, and discourse, the simple task of word prediction acts as a profound supervision signal, allowing models to learn major aspects of linguistic structure without explicit manual labeling.
> "Despite its simple nature, the generality of word prediction, as a task that benefits from syntactic, semantic, and discourse information, leads to it being a very powerful multidimensional supervision signal."
*(sources: src_024, src_042)*
