# The Transformer Architecture

The transformer replaces recurrence with self-attention, allowing every position in a
sequence to attend to every other position simultaneously. This parallelizability is the
key to its scalability and the reason transformers now dominate natural language
processing, vision, and beyond.

A transformer block contains two sublayers: multi-head self-attention and a
position-wise feedforward network. Each sublayer is wrapped with a residual connection
and layer normalization, which stabilize training and allow very deep stacks. Multi-head
attention runs several attention operations in parallel, each with its own learned
projections, so the model can attend to different kinds of relationships at once, such
as syntactic roles in one head and coreference in another. The feedforward network,
typically two linear layers with a nonlinearity, transforms each position independently
and contributes a large share of the parameters.

Because self-attention is permutation invariant, transformers add positional encodings
to the input so the model can distinguish order. Encoder-only models such as BERT read
the whole sequence bidirectionally and excel at understanding tasks like classification
and extractive question answering. Decoder-only models such as the GPT family apply
causal masking so each position sees only earlier ones, which makes them natural
generators and the basis of modern chat assistants. Encoder-decoder models such as T5
separate reading from writing and suit sequence-to-sequence problems.

The architecture's main weakness is cost: attention scales quadratically with sequence
length, so long contexts are expensive in compute and memory. This has inspired a large
body of work on efficient attention, including sparse, linear, and sliding-window
variants. Yet the original design remains remarkably durable. The transformer's success
is less about any single component and more about how cleanly it scales with data,
parameters, and compute, which is exactly what modern hardware and training pipelines
reward.
A practical insight is that the transformer's components can be scaled semi-independently,
which is a large part of why it is so adaptable. Width, depth, number of heads, and
feedforward ratio can each be tuned, and scaling laws guide how to allocate a compute
budget across them. The feedforward layer, often overlooked, holds a disproportionate share
of parameters and appears to act as a key-value memory of learned patterns, while attention
routes information between positions. Framing the block this way, attention for routing and
feedforward for storage, gives intuition for why both are necessary and why ablating either
degrades performance sharply.
