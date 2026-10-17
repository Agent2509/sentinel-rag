# Optimization Algorithms

Plain gradient descent is rarely the best choice in practice. A family of adaptive
algorithms modifies the update rule to accelerate convergence and stabilize training on
the difficult, non-convex loss surfaces of deep networks.

Momentum accumulates a velocity that smooths noisy gradients and accelerates movement
along consistent directions, much like a ball rolling downhill. Nesterov momentum
improves on this by evaluating the gradient at a look-ahead point, giving a corrective
signal before overshooting. These methods are especially effective in ravines where
vanilla updates oscillate.

Adagrad adapts the learning rate per parameter, scaling it down for parameters with a
history of large gradients. This suits sparse features, but the accumulating sum of
squared gradients keeps shrinking the rate until learning effectively stops. RMSProp
fixes this by using an exponential moving average of squared gradients instead of a
lifetime sum, so the rate can recover.

Adam combines momentum with RMSProp-style scaling and adds bias correction for the
early steps, making it a robust and widely used default. AdamW decouples weight decay
from the adaptive update, which matters because coupling them distorts the effective
regularization for parameters with large gradients. AdamW is the standard optimizer
for transformers.

Learning-rate schedules are as important as the optimizer. Warmup ramps the rate up
over the first steps to avoid instability, and cosine decay lowers it smoothly toward
the end to settle into a good minimum. No single optimizer or schedule dominates every
problem; the best choice depends on model size, batch size, data, and the loss
landscape, so experimentation remains essential.
One subtlety is that the optimizer interacts with batch size and learning rate. Larger
batches give lower-variance gradients, which in principle permits larger steps, and the
linear scaling rule formalizes this by scaling the learning rate with the batch size. But
very large batches can hurt generalization unless the learning rate and schedule are
adjusted, which is why warmup and careful tuning accompany large-batch training. The
practical takeaway is that optimizer, learning rate, batch size, and schedule should be
tuned as a group. Changing one in isolation frequently produces a result that misleads you
about the others.
