# Introduction to Neural Networks

A neural network stacks layers of simple units, each computing a weighted sum of its
inputs followed by a nonlinear activation. A feedforward network alternates linear
layers with nonlinearities, letting it approximate complex functions. Universal
approximation theorems guarantee that a wide enough network can represent any
continuous function to arbitrary accuracy, though they say nothing about whether
training will find those weights.

Training is a loop of three steps. Forward propagation computes predictions from
inputs. A loss function measures how far predictions are from targets. Backpropagation
computes gradients, and an optimizer updates the weights. Repeating this over the
dataset gradually reduces the loss. The network learns by adjusting millions of
parameters in response to error.

Depth is what makes neural networks powerful. Early layers tend to capture simple,
local patterns, and later layers compose them into abstract, task-relevant features.
This hierarchical representation learning is why a deep network can solve problems
that defeated hand-engineered feature pipelines.

Success depends more on practical details than on novelties in architecture.
Initialization schemes such as Xavier and He keep the variance of activations and
gradients stable across layers, preventing them from vanishing or exploding at the
start of training. Normalization layers, including batch normalization and layer
normalization, stabilize the distribution of layer inputs and allow higher learning
rates. Activation choices, residual connections, and regularization all interact to
determine whether training converges. These same building blocks scale up to form the
large language models at the frontier, so understanding a small feedforward network is
the first step toward understanding the field.
A common early mistake is to assume that a larger network always helps. Beyond a point,
adding capacity without adding data leads to overfitting, and the extra computation yields
no improvement in generalization. Conversely, a small network on a rich dataset underfits
and would benefit from more capacity. The art of applying neural networks is largely about
matching capacity to data and regularization, then iterating on the architecture only once
the fundamentals are sound. Most impressive results come from good data, sensible
architecture, and careful training, not from a clever trick, though clever tricks are what
get the attention.
