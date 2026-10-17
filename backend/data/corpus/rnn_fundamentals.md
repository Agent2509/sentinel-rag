# Recurrent Neural Networks

A recurrent neural network processes sequences by maintaining a hidden state that is
updated at each time step. The same weights are applied at every position, so the model
can handle inputs of any length and share statistical strength across time. This makes
recurrence a natural fit for text, speech, and time series.

At each step the network combines the current input with the previous hidden state
through a learned transformation and a nonlinearity, producing a new hidden state that
summarizes everything seen so far. For sequence labeling, an output is produced at each
step; for sequence classification, only the final hidden state is used. The recurrent
formulation means the network has an unbounded memory in principle, able to condition
on arbitrarily distant context.

In practice, training basic recurrent networks is difficult. Gradients are propagated
backward through many time steps, and repeated multiplication by the recurrent weight
matrix causes them to shrink toward zero or grow without bound. Exploding gradients are
handled by clipping their norm, but vanishing gradients are more insidious, causing the
network to forget long-range dependencies. This is why plain recurrent networks
struggle with tasks that require remembering information over hundreds of steps.

A deeper structural limitation is parallelism. Because each step depends on the previous
hidden state, the computation is inherently sequential and cannot be parallelized across
time, which makes training slow on modern hardware designed for parallel work. These two
problems, difficulty learning long-range dependencies and poor hardware utilization,
motivated the invention of gated recurrent units and ultimately attention-based
transformers, which replace recurrence with operations that compare all positions in
parallel.
A concept worth internalizing is that of the unrolled network. A recurrent model applied to
a sequence of length T is conceptually a very deep feedforward network with shared weights,
one copy per time step. This view explains both the power and the problem: shared weights
let the model reuse a single transformation across positions, but the depth grows with
sequence length, and backpropagation through that depth is where vanishing gradients
originate. Modern practice increasingly replaces this recurrence with attention, which
achieves the same contextual mixing without the sequential depth, but the unrolled view
remains the clearest explanation of why recurrent training is so delicate.
