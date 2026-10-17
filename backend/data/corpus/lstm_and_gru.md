# LSTM and GRU

Long short-term memory networks were designed to solve the vanishing-gradient problem
that plagues basic recurrent networks. An LSTM maintains two states: the hidden state
that is exposed to the rest of the network and a cell state that acts as a long-term
memory. Three gates control the flow of information. The input gate decides what new
information to write, the forget gate decides what to discard, and the output gate
decides what part of the cell state to expose.

The crucial design choice is the additive update to the cell state. Because information
flows along the cell state through addition rather than repeated multiplication,
gradients can propagate across many time steps without shrinking. This allows LSTMs to
learn dependencies spanning hundreds of steps, a major advance when they were
introduced.

The gated recurrent unit, or GRU, simplifies the LSTM by merging the cell and hidden
states and using two gates instead of three. It has fewer parameters and often trains
faster, while matching LSTM accuracy on many tasks. The choice between them is
empirical, and neither strictly dominates.

Both architectures powered a generation of results in machine translation, speech
recognition, and language modeling. Bidirectional variants read the sequence in both
directions and concatenate the representations, which helps for tasks where the whole
sequence is available, such as encoding text. Encoder-decoder setups with attention over
the encoder states became the leading approach to translation before transformers
displaced them. Despite being largely superseded for large-scale language modeling, LSTMs
and GRUs remain valuable for streaming and resource-constrained settings, where their
constant per-step cost and small memory footprint are attractive compared to the
quadratic attention of transformers.
A practical consideration is the computational profile of recurrent models. Their
per-step cost is constant and independent of sequence length, which makes them attractive
for streaming settings where inputs arrive over time and cannot be buffered. Attention, by
contrast, needs the whole sequence and scales quadratically. This is why gated recurrent
units still appear in edge deployment and real-time signal processing, where low and
predictable latency matters more than the raw quality of a large transformer. The lesson is
that architectural choice should follow the deployment constraints, and older architectures
often remain the right tool in particular niches long after they are no longer the default.
