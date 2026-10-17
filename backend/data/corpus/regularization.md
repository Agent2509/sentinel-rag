# Regularization

Regularization is the set of techniques that stop a model from memorizing its training
data. A model with enough capacity can fit noise, achieving low training error while
generalizing poorly. Regularization biases the model toward simpler, more robust
solutions.

L2 regularization, also called weight decay, adds the squared magnitude of the weights
to the loss, shrinking them toward zero and smoothing the function the network
represents. L1 regularization adds the sum of absolute weights and tends to drive many
weights exactly to zero, performing feature selection along the way. Elastic net
combines both.

Dropout randomly disables a fraction of activations during training, preventing the
network from relying on any single unit and effectively training an ensemble of
thinned subnetworks. At inference time dropout is disabled and activations are scaled,
so the ensemble's expected output is used. Batch normalization stabilizes the
distribution of layer inputs and has a mild regularizing side effect, as does its
successor layer normalization.

Early stopping is a simple and effective regularizer: monitor validation loss and stop
when it begins to rise, before the model starts to overfit. Data augmentation is
another form, expanding the effective dataset by applying label-preserving
transformations such as cropping images or paraphrasing text.

The recurring theme is a trade-off between fitting the data and constraining the
model. Too little regularization and the model overfits; too much and it underfits,
failing to capture real structure. Cross-validation and a held-out test set, never the
training set, are how you verify that regularization is genuinely helping rather than
merely making the numbers look good.
A useful way to think about regularization is as an expression of a prior. L2 regularization
corresponds to a Gaussian prior on the weights, and L1 to a Laplace prior, so choosing a
regularizer is a way of stating what kinds of solutions you expect to be reasonable before
seeing the data. This perspective, drawn from Bayesian reasoning, clarifies why different
regularizers produce different behaviors and why the strength of regularization should
reflect how much data you have. With abundant data, the likelihood dominates and
regularization can be light; with little data, the prior matters more and stronger
regularization helps.
