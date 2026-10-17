# Context Windows

The context window is the maximum number of tokens a model can attend to at once,
covering both the prompt and the generated output. It bounds how much retrieved text,
conversation history, and instruction can be supplied in a single call, making it one of
the most important practical constraints in building applications on top of language
models.

Early transformers supported a few thousand tokens. Modern models advertise windows of
hundreds of thousands, and some claim millions. Longer windows let a model read entire
documents, maintain long conversations, and reason over large codebases without
chunking. But length is not free. Attention cost grows quadratically with sequence
length, so latency and memory rise sharply, and even architectures with efficient
attention often slow down considerably at long context. A large window also does not
guarantee effective use: models exhibit a lost-in-the-middle effect, attending less
reliably to information buried in the center of a long context than to content near the
beginning or end.

Effective systems manage the token budget deliberately rather than filling the window.
They retrieve only the most relevant passages, summarize or compress conversation
history, and place the most important instructions near the end where attention is
strongest. Redundant or low-value context is actively harmful, because it dilutes
attention and increases cost.

In retrieval-augmented generation, the context window is the direct constraint on how
many passages, and how large a parent context, can be passed to the generator. This is
why retrieval precision matters so much: every irrelevant chunk that occupies part of the
window is a slot that a more relevant chunk could have used. Good chunking, reranking,
and grading all exist in part to make the most of a limited context budget.
A practical technique for long inputs is retrieval over the context itself, sometimes called
needle search, where the system first locates the relevant spans within a large document
before reasoning over them. This avoids relying on the model to attend perfectly across a
huge context and instead reduces the problem to a size the model handles reliably. Another
technique is recursive summarization, where long material is summarized in pieces and the
summaries are combined. Both reflect the same insight: the effective context is much
smaller than the advertised maximum for most tasks, and managing the budget actively beats
trusting that a large window will be used well.
