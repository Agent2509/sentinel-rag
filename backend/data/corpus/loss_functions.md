# Loss Functions

A loss function converts the gap between predictions and targets into a single number
that optimization can minimize. It encodes what the model is being asked to care
about, so choosing the wrong one produces a model that is technically well trained but
useless for the real objective.

For regression, mean squared error penalizes large errors heavily and is easy to
optimize because it is smooth and convex in the prediction. Mean absolute error is
more robust to outliers because it grows linearly, but its gradient is constant and
undefined at zero. Huber loss blends the two, acting quadratic for small errors and
linear for large ones.

For classification, cross-entropy is the natural choice. Binary cross-entropy measures
the negative log-likelihood of the correct label under a Bernoulli distribution, and
categorical cross-entropy generalizes it to mutually exclusive classes via a softmax
output. Cross-entropy punishes confident wrong predictions severely, which drives the
model to calibrate its probabilities rather than merely rank them correctly.

Representation learning uses different objectives. Contrastive loss pulls a positive
pair together while pushing negative pairs apart, and triplet loss anchors this around
a third example. Sentence embedding models are trained this way, which is why
semantically similar texts end up close in vector space.

At a higher level, generative systems are judged by metrics that are not directly
differentiable, such as faithfulness or human preference. Reward modeling and
reinforcement learning from human feedback exist precisely to convert such
non-differentiable preferences into a trainable signal. Understanding the mismatch
between the training loss and the true goal is central to avoiding models that
optimize the proxy while failing the task.
A practical warning is that optimizing a convenient loss does not guarantee the desired
behavior. A model trained to maximize likelihood becomes fluent, not truthful; a model
trained to match a reference text becomes similar, not necessarily correct. Metrics such as
BLEU or ROUGE measure surface overlap and can be gamed by verbose or repetitive output. This
gap between the training objective and the true goal is why evaluation must use
task-relevant measures, often judged by humans or by a separate model, and why techniques
such as reward modeling exist to bring the objective closer to what people actually want.
