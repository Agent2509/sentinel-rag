# Backpropagation

Backpropagation is the algorithm that makes training deep networks practical. It
computes the gradient of a scalar loss with respect to every parameter by applying
the chain rule of calculus backward through the network's computational graph. Without
it, differentiating each of millions of parameters independently would be hopeless.

The procedure has two passes. The forward pass computes the output and caches every
intermediate activation. The backward pass then propagates the gradient of the loss
from the output layer toward the input, and at each layer multiplies the incoming
gradient by the local derivative of that layer's operation. Because each layer only
needs the gradient flowing from the layer above, the total cost is roughly the same
as one forward pass. This efficiency is the key insight.

Modern frameworks implement reverse-mode automatic differentiation, a generalization
of backpropagation that works on arbitrary compositions of differentiable operations.
You build a graph of operations, and the framework records how to differentiate each
one, then replays the graph in reverse. This is why you rarely derive gradients by
hand; you describe the forward computation and the library handles the rest.

Backpropagation also explains many training pathologies. If activations saturate,
their local gradients shrink toward zero, and the signal decays as it travels
backward, causing the vanishing-gradient problem that stalled early deep networks.
Exploding gradients occur when repeated multiplication amplifies the signal, and are
managed with gradient clipping. Residual connections provide a shortcut path that lets
gradients flow directly, which is a large part of why very deep transformers train at
all. Understanding backprop turns mysterious training failures into diagnosable
numerical issues.
One consequence of backpropagation's structure is that the memory cost grows with network
depth, because activations must be kept for the backward pass. This is why very deep models
use techniques such as gradient checkpointing, which recomputes some activations instead of
storing them, trading compute for memory. Another consequence is that any operation you
insert must be differentiable, or the gradient graph breaks; this is why techniques such as
straight-through estimators exist for things like discrete sampling. Understanding these
graphs also makes it clear why detaching a tensor in PyTorch stops gradient flow, a
recurring source of silent bugs.
