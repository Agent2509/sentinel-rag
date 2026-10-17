# LLM Pretraining

Pretraining trains a language model on a very large text corpus using a self-supervised
objective, typically next-token prediction for decoder-only models or masked-token
prediction for encoder models. The crucial property is that no human labels are required:
the text itself provides the training signal, which is what makes pretraining scalable to
the size of the internet.

The pipeline begins with data collection and heavy filtering. Web text is deduplicated at
the document and near-duplicate level, filtered for quality and safety, and mixed across
domains according to a carefully chosen ratio. Data quality has proven at least as
important as raw quantity; a smaller, cleaner, better-balanced corpus can outperform a
larger, noisier one. The filtered text is tokenized into a flat stream of token ids, and
training consumes that stream over many passes with large batch sizes distributed across
many accelerators.

Scaling laws describe how loss falls predictably as parameters, data, and compute
increase together. Modern practice uses these laws to allocate a compute budget
optimally, often training smaller models on more data than early models did. The
resulting base model has absorbed broad linguistic structure and a great deal of world
knowledge, but it is not yet reliable at following instructions or answering questions
directly; it simply continues text in a plausible way.

Pretraining is extraordinarily expensive, so most practitioners start from an existing
checkpoint rather than train from scratch. Understanding pretraining clarifies where a
model's knowledge and biases come from, why the data mixture matters, and why the base
model must still be aligned through instruction tuning and preference learning before it
becomes a useful assistant.
An important and sometimes overlooked stage is curriculum and data ordering, which can
affect final quality even when the total data and compute are fixed. Mixing sources,
controlling repetition, and deciding when to introduce higher-quality data all shape what
the model learns. Evaluation during pretraining uses held-out perplexity as a proxy, but
perplexity does not always track downstream task quality, which is why periodic fine-grained
evaluations are run on task suites. The gap between the training signal, next-token
prediction, and the desired capabilities is the recurring theme of language model
development, and it is why pretraining alone is never the end of the story.
