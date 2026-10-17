"""Corpus part 1: math fundamentals and the first classical models."""

DOCS: dict[str, str] = {
"linear_algebra.md": """# Linear Algebra for Machine Learning

Linear algebra is the language of machine learning. Almost every operation in a
model, from a forward pass to a gradient update, can be written as a combination of
vectors, matrices, and their products. Data points are vectors, datasets are
matrices, and learned parameters are tensors. Fluency with these objects makes the
rest of the field far easier to reason about.

A vector is an ordered list of numbers that can represent a point in space or a
direction. A matrix is a rectangular grid of numbers that acts as a linear
transformation: multiplying a vector by a matrix produces another vector. The shape
of a matrix tells you the dimension of the space it maps from and to. Matrix
multiplication composes transformations, and it is associative but not commutative,
which is why the order of operations matters in deep architectures.

The dot product measures alignment between two vectors and is the foundation of
similarity. When both vectors are unit length, the dot product equals the cosine of
the angle between them, which is exactly what cosine similarity uses in retrieval.
The rank of a matrix quantifies how much independent information it carries; a
low-rank matrix compresses many numbers into a compact structure, which is the idea
behind dimensionality reduction and low-rank adaptation.

Eigenvectors and eigenvalues describe special directions that a transformation only
stretches, without rotating. They reveal the dominant axes of variation in data and
underpin principal component analysis, spectral clustering, and the analysis of
optimization landscapes. The singular value decomposition generalizes this to any
matrix and is widely used for compression and noise reduction.

Norms measure the size of a vector. The L2 norm is the familiar Euclidean length and
drives weight decay and distance metrics. The L1 norm sums absolute values and
encourages sparse solutions. Frobenius norm extends this to matrices. Understanding
norms clarifies why certain regularizers produce sparse weights while others simply
shrink them uniformly. Together, these primitives form the vocabulary you will use
again and again when implementing and debugging models.
""",
"probability_statistics.md": """# Probability and Statistics

Probability is the framework for reasoning under uncertainty, and machine learning
is fundamentally a study of uncertainty. A random variable maps outcomes to numbers,
and its probability distribution specifies how likely each value is. Understanding a
few distributions covers most practical cases. The Bernoulli models a single binary
event, the Categorical models a choice among several, the Binomial counts successes,
and the Gaussian describes continuous quantities that cluster around a mean.

Summary statistics compress a distribution into digestible numbers. The expectation
is the long-run average, and the variance measures spread. Covariance captures how
two variables move together, which is central to correlation analysis and to the
covariance matrices used in PCA and Gaussian models. Standard deviation is the square
root of variance and lives on the same scale as the data.

Bayes' theorem is the engine of probabilistic inference. It converts a prior belief
into a posterior after observing evidence, weighting the likelihood of the evidence
under each hypothesis. This single rule underlies naive Bayes classifiers, Bayesian
networks, and much of modern uncertainty quantification. In language modeling, the
chain rule of probability decomposes the probability of a sequence into a product of
next-token probabilities, which is precisely what a language model learns to predict.

Sampling connects probability to practice. Monte Carlo methods estimate quantities by
averaging over random samples, and this idea powers importance sampling, dropout as
approximate Bayesian inference, and stochastic gradient estimates. Estimation
theorems such as maximum likelihood direct how to choose parameters that best explain
observed data.

Statistics also governs honest evaluation. Confidence intervals, hypothesis tests,
and the distinction between training and validation error determine whether an
observed improvement is real or just noise. When comparing retrieval strategies on a
small benchmark, a difference of a few points may be within the noise floor, and only
statistical reasoning tells you when to trust it.
""",
"gradient_descent.md": """# Gradient Descent

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
""",
"backpropagation.md": """# Backpropagation

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
""",
"activation_functions.md": """# Activation Functions

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
""",
"loss_functions.md": """# Loss Functions

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
""",
"regularization.md": """# Regularization

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
""",
"optimization_algorithms.md": """# Optimization Algorithms

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
""",
"logistic_regression.md": """# Logistic Regression

Logistic regression predicts the probability of a binary outcome from a linear
combination of features passed through a sigmoid. Despite the name, it is a
classification algorithm. It is one of the simplest models in machine learning and
remains a strong, interpretable baseline.

The model computes a weighted sum of the inputs, adds a bias, and squashes the result
into the range zero to one with the logistic function. A threshold, usually one half,
converts the probability into a class label. Training maximizes the likelihood of the
observed labels, which is equivalent to minimizing binary cross-entropy. This loss is
convex, so gradient descent reliably finds the global optimum, a guarantee that more
complex models cannot offer.

The decision boundary is linear in the feature space, so logistic regression captures
only linearly separable patterns unless nonlinear features are engineered or a kernel
is applied. Its coefficients are directly interpretable: the exponential of a weight
is the odds ratio for that feature, quantifying how the odds change with a one-unit
increase. Regularization is usually applied to control overfitting, and L1
regularization produces sparse models that select a subset of features.

Logistic regression scales well, trains quickly even on large datasets, and needs
comparatively little data. It is often competitive with more sophisticated models on
small tabular problems, which is why it belongs in every baseline suite. It also
reappears inside neural networks, where a final linear layer followed by softmax plays
the same role for multiple classes: producing calibrated scores that a cross-entropy
loss can optimize.
""",
"decision_trees.md": """# Decision Trees

A decision tree recursively partitions the data by asking a sequence of yes-or-no
questions about feature values. Each internal node tests a feature threshold, each
branch corresponds to an outcome, and each leaf holds a prediction. The result is a set
of if-then rules that is easy to visualize and explain, a rarity in machine learning.

At each split the algorithm chooses the feature and threshold that best separate the
targets. For classification, common criteria are Gini impurity and information gain
based on entropy; both reward splits that produce purer child nodes. For regression,
variance reduction is used instead. The tree grows greedily by selecting the best split
at each step, which is efficient but not guaranteed to yield the globally optimal tree.

Trees handle numeric and categorical features together, require no feature scaling, and
capture nonlinear interactions naturally. Left unchecked, however, they keep splitting
until every training example is isolated in its own leaf, perfectly fitting the data
and overfitting badly. Pre-pruning limits growth through maximum depth, minimum samples
per leaf, or a minimum improvement in impurity. Post-pruning grows the tree fully and
then removes branches that add little value, using a validation set to decide.

A single tree has high variance: small perturbations in the data can produce a
completely different set of splits, because the greedy choices cascade. This
instability is the motivation for ensembles. Bagging averages many trees grown on
bootstrap samples to reduce variance, yielding random forests, while boosting grows
trees sequentially to correct earlier mistakes. Understanding the single tree makes
those powerful ensembles far easier to understand.
""",
}
