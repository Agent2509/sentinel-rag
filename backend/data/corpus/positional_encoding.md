# Positional Encoding

Self-attention is permutation invariant: if you shuffle the tokens of a sequence, the
attention output is the same up to the corresponding shuffle. The mechanism has no
inherent notion of order, yet language depends heavily on order. The phrase "the dog bit
the man" means something very different from "the man bit the dog". Transformers resolve
this by injecting positional information into the token representations before the first
attention layer.

The original transformer uses sinusoidal positional encodings: fixed functions of
position and dimension, with sine waves of different frequencies. Because the patterns
are smooth and periodic, the model can generalize to sequence lengths beyond those seen
during training, and relative offsets are encoded implicitly through the linear
relationships between sinusoids at different positions.

An alternative is learned positional embeddings, a lookup table with one vector per
position, trained alongside the model. This is simple and common in decoder-only
architectures, but the table is fixed to the maximum length seen in training, so
extending context requires retraining or interpolation of the embeddings.

Modern large models increasingly use rotary position embeddings, known as RoPE. RoPE
rotates the query and key vectors by an angle proportional to their position, so the dot
product between them depends on their relative distance. This encodes relative position
elegantly and extrapolates to longer contexts more gracefully than absolute embeddings.
Another approach, ALiBi, adds a distance-based bias directly to the attention scores,
penalizing far-apart tokens. Handling very long context robustly is an active research
area, and the choice of positional scheme is one of the main determinants of how well a
model generalizes beyond its training window.
A practical consequence of the choice is how a model behaves when asked to handle longer
sequences than it saw in training. Absolute learned embeddings degrade abruptly beyond their
trained length, which is why researchers developed interpolation and rescaling tricks to
stretch them. Relative schemes such as rotary and ALiBi degrade more gracefully and are
therefore preferred when long context matters. The broader lesson is that positional
encoding is not a minor detail: it determines the length at which a model remains
competent, and it interacts with how attention is computed. When building or fine-tuning a
model for long documents, this choice is one of the first to reconsider.
