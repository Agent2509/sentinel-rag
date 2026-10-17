# Activation Functions

Activation functions introduce the nonlinearity that lets a network model complex
relationships. Without them, stacking linear layers would collapse into a single
linear transformation, no matter how deep the network. The choice of activation
affects gradient flow, training stability, and final accuracy.

The sigmoid function squashes its input into the range zero to one, which makes it a
natural fit for probabilities. Its weakness is saturation: for large positive or
negative inputs the gradient approaches zero, so deep networks built from sigmoids
suffer vanishing gradients. The hyperbolic tangent, or tanh, is similar but centered
at zero, which keeps activations better conditioned, though it still saturates.

The rectified linear unit, ReLU, returns the input when positive and zero otherwise.
It is cheap to compute and, crucially, does not saturate for positive values, which
made deep networks trainable. Its drawback is the dying-ReLU problem: a unit whose
weights push all inputs negative receives zero gradient forever. Leaky ReLU and
parametric ReLU address this by allowing a small slope in the negative region, and
ELU smooths the transition.

Smooth activations such as GELU and SiLU, or Swish, are now standard in transformers.
They approximate ReLU but have nonzero curvature and gradient everywhere, which
interacts favorably with normalization and attention. Output activations are chosen by
the task: softmax for mutually exclusive classes, a sigmoid for independent binary
labels, and no activation at all for regression. The best practice is to pick an
activation that pairs well with the rest of the architecture and normalization scheme
rather than optimizing it in isolation, since these components are deeply coupled.
A frequent practical question is whether activation choice still matters now that
normalization and residual connections are ubiquitous. It matters less than it once did, but
it is not irrelevant. Smooth activations tend to pair well with transformers, while ReLU
variants remain common in convolutional networks where their efficiency is valuable. The
deeper lesson is that activations, initialization, and normalization form a coupled system:
changing one often requires reconsidering the others. Treating them as independent knobs
leads to confusing results, whereas reasoning about them together explains why certain
combinations are stable and others are not.
