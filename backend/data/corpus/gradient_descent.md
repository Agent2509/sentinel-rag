# Gradient Descent

Gradient descent is the workhorse algorithm for training nearly every model. It
iteratively adjusts parameters in the direction that most steeply decreases the loss
function. The gradient is the vector of partial derivatives, pointing uphill, so the
algorithm steps in the opposite direction, scaled by a learning rate.

The learning rate is the single most important hyperparameter. If it is too large,
the updates overshoot and training diverges, with the loss oscillating or exploding.
If it is too small, convergence crawls and may stall in a poor region. Schedules that
start large and decay over time, or that warm up gradually, often strike the best
balance. The shape of the loss landscape matters too: narrow ravines cause plain
gradient descent to zigzag, which motivates momentum.

There are three main variants. Batch gradient descent computes the gradient over the
entire dataset, producing a stable but expensive and slow update. Stochastic gradient
descent computes it from a single example, which is fast but noisy and can escape
shallow local minima. Mini-batch gradient descent averages over a small batch and is
the default in practice, because it balances the variance of the estimate against the
efficiency of vectorized hardware. The noise in mini-batch updates is not purely a
nuisance; it acts as a mild regularizer.

Gradient descent is not guaranteed to find the global optimum of a non-convex loss,
but in high-dimensional neural networks the many saddle points and flat regions are
usually good enough. Initialization, normalization, and architectural choices shape
the landscape to make optimization tractable. Recognizing when training is limited by
optimization rather than by data or model capacity is one of the most valuable
debugging instincts in deep learning.
A practical diagnostic is to plot the loss curve and watch its shape. A smooth, steadily
decreasing curve suggests a healthy learning rate. Spikes and divergence point to a rate
that is too high, or to numerical instability such as exploding gradients. A curve that
falls quickly and then plateaus may indicate that the model has hit a capacity limit or
that the optimizer is stuck. Reading these curves is a skill that separates practitioners
who tune by understanding from those who tune by guessing, and it is often the fastest way
to find the real cause of a disappointing training run.
