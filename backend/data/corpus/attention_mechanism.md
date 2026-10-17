# Attention Mechanism

Attention computes a weighted sum of values, where the weights express how relevant each
value is to a given query. It is the mechanism that lets a model dynamically focus on
the most useful parts of its input rather than compressing everything into a single
fixed vector.

In scaled dot-product attention, queries and keys are compared using dot products to
produce scores. Those scores are divided by the square root of the key dimension, a
scaling that keeps the values in a range where the softmax gradients behave well, and
then passed through a softmax to yield weights that sum to one. The output is the
weighted average of the values. The three inputs, queries, keys, and values, are linear
projections of the same or different sequences, which is why the same operation serves
both self-attention and cross-attention.

Self-attention applies the operation within a single sequence, letting each token gather
context from every other token. Cross-attention uses queries from one sequence and keys
and values from another, which is how an encoder-decoder model aligns the input with the
output being generated. Multi-head attention repeats the operation in parallel with
different learned projections, allowing the model to represent several relationships at
once and then combine them.

The central advantage of attention over recurrence is the direct path between any two
positions. In a recurrent network, information must travel step by step, so long-range
dependencies fade; in attention, every pair interacts in a single step. Attention
weights are also inspectable, offering a partial window into what the model attends to.
The cost is quadratic scaling in sequence length, and the mechanism's great strength,
its ability to relate distant tokens, is inseparable from that expense. Efficient
attention research aims to keep the benefit while taming the cost.
Interpreting attention weights is tempting but must be done carefully. High attention from
one token to another suggests the model used that information, but the weights are only one
component of the computation, summed across heads and layers, and a low weight does not
prove a token was ignored, because information can flow through other paths. Some research
uses attention as a partial explanation, for example to find where a model looks when
resolving a reference, while other work cautions against over-reading it. The healthy
stance is to treat attention as a useful but incomplete window, and to confirm any
interpretation with causal experiments such as ablations rather than visualizations alone.
