"""Extra paragraphs appended to corpus part 1 and 2 docs.

Keeps each source doc above the 512-token fixed-chunk boundary without rewriting
the base text. Each addition is a distinct continuation, not boilerplate.
"""

EXTRA: dict[str, str] = {
"linear_algebra.md": """
A useful mental model is to treat every tensor operation as a statement about shapes.
When a computation goes wrong, the first thing to check is whether the dimensions line up,
because broadcasting rules can silently expand a mismatched operand and hide a bug.
Understanding broadcasting, and knowing when to insert an explicit dimension, prevents a
large share of practical errors. It also pays to remember that many apparently exotic
operations, from convolutions to attention, are at bottom batched matrix multiplications
with clever reshaping, so optimizing for efficient matrix products is often the single
most effective performance lever.
""",
"probability_statistics.md": """
A subtle but important point is the difference between the joint, marginal, and
conditional distributions. The joint describes two variables together, the marginal
integrates one out, and the conditional asks about one given the other. Independence means
the joint factorizes into a product of marginals, and conditional independence, which is
much weaker and far more common, is the assumption that makes graphical models and naive
Bayes tractable. Recognizing when a modeling assumption is truly needed, rather than
merely convenient, prevents the classic error of imposing independence where the data
clearly violates it.
""",
"gradient_descent.md": """
A practical diagnostic is to plot the loss curve and watch its shape. A smooth, steadily
decreasing curve suggests a healthy learning rate. Spikes and divergence point to a rate
that is too high, or to numerical instability such as exploding gradients. A curve that
falls quickly and then plateaus may indicate that the model has hit a capacity limit or
that the optimizer is stuck. Reading these curves is a skill that separates practitioners
who tune by understanding from those who tune by guessing, and it is often the fastest way
to find the real cause of a disappointing training run.
""",
"backpropagation.md": """
One consequence of backpropagation's structure is that the memory cost grows with network
depth, because activations must be kept for the backward pass. This is why very deep models
use techniques such as gradient checkpointing, which recomputes some activations instead of
storing them, trading compute for memory. Another consequence is that any operation you
insert must be differentiable, or the gradient graph breaks; this is why techniques such as
straight-through estimators exist for things like discrete sampling. Understanding these
graphs also makes it clear why detaching a tensor in PyTorch stops gradient flow, a
recurring source of silent bugs.
""",
"activation_functions.md": """
A frequent practical question is whether activation choice still matters now that
normalization and residual connections are ubiquitous. It matters less than it once did, but
it is not irrelevant. Smooth activations tend to pair well with transformers, while ReLU
variants remain common in convolutional networks where their efficiency is valuable. The
deeper lesson is that activations, initialization, and normalization form a coupled system:
changing one often requires reconsidering the others. Treating them as independent knobs
leads to confusing results, whereas reasoning about them together explains why certain
combinations are stable and others are not.
""",
"loss_functions.md": """
A practical warning is that optimizing a convenient loss does not guarantee the desired
behavior. A model trained to maximize likelihood becomes fluent, not truthful; a model
trained to match a reference text becomes similar, not necessarily correct. Metrics such as
BLEU or ROUGE measure surface overlap and can be gamed by verbose or repetitive output. This
gap between the training objective and the true goal is why evaluation must use
task-relevant measures, often judged by humans or by a separate model, and why techniques
such as reward modeling exist to bring the objective closer to what people actually want.
""",
"regularization.md": """
A useful way to think about regularization is as an expression of a prior. L2 regularization
corresponds to a Gaussian prior on the weights, and L1 to a Laplace prior, so choosing a
regularizer is a way of stating what kinds of solutions you expect to be reasonable before
seeing the data. This perspective, drawn from Bayesian reasoning, clarifies why different
regularizers produce different behaviors and why the strength of regularization should
reflect how much data you have. With abundant data, the likelihood dominates and
regularization can be light; with little data, the prior matters more and stronger
regularization helps.
""",
"optimization_algorithms.md": """
One subtlety is that the optimizer interacts with batch size and learning rate. Larger
batches give lower-variance gradients, which in principle permits larger steps, and the
linear scaling rule formalizes this by scaling the learning rate with the batch size. But
very large batches can hurt generalization unless the learning rate and schedule are
adjusted, which is why warmup and careful tuning accompany large-batch training. The
practical takeaway is that optimizer, learning rate, batch size, and schedule should be
tuned as a group. Changing one in isolation frequently produces a result that misleads you
about the others.
""",
"logistic_regression.md": """
A practical consideration is class imbalance. When one class is far rarer than the other,
the model can achieve high accuracy by predicting the majority class, which is useless. In
that setting, accuracy is the wrong metric; precision, recall, and the area under the
precision-recall curve are more informative. Thresholds can be tuned to trade precision
against recall according to the cost of each type of error, and the coefficients remain
interpretable, so logistic regression is often the model of choice when a decision must be
explained to a stakeholder. Its simplicity is a feature, not a limitation.
""",
"decision_trees.md": """
Trees have a distinctive relationship to feature engineering. Because they split on
thresholds, they are invariant to monotonic transformations of individual features, so
scaling and normalization are unnecessary. They also capture interactions automatically
through their branching structure. However, they struggle with smooth linear relationships,
which they approximate with many axis-aligned splits, and they cannot extrapolate beyond
the range of the training data, a limitation that matters for regression on trending
series. These characteristics explain why trees dominate tabular data while linear models
and neural networks remain preferable for problems with strong smooth structure.
""",
"random_forests.md": """
A valuable property of forests is their tolerance for messy data. Missing values can be
handled with surrogate splits or imputation, irrelevant features are largely ignored
because they rarely win the random feature selection at a split, and outliers exert little
influence because predictions are averages. This robustness makes forests a reliable first
model on a new tabular dataset, giving a strong baseline before investing in more elaborate
approaches. The main cost is that they are bulky, since each tree stores its structure, and
slower at inference than a single decision tree, though the trade-off is usually well worth
it for the accuracy and stability they provide.
""",
"support_vector_machines.md": """
The margin viewpoint offers a useful lesson that generalizes beyond SVMs. A classifier that
separates classes with the largest possible buffer tends to be robust, which is a
geometric intuition that also underlies modern techniques such as large-margin losses in
representation learning. The idea that only the difficult examples near the boundary drive
the solution is likewise echoed in hard-negative mining, where training focuses on the
examples the model currently gets wrong. Studying SVMs therefore pays off conceptually,
even when a neural network is the model actually deployed, because the underlying
principles of margins and support points recur throughout machine learning.
""",
"kmeans_clustering.md": """
Evaluating a clustering is inherently harder than evaluating a classifier, because there is
often no ground truth to compare against. When labels do exist, metrics such as adjusted
Rand index or normalized mutual information measure agreement with them. Without labels,
internal measures such as silhouette, Davies-Bouldin, or the Calinski-Harabasz index
quantify how compact and well-separated the clusters are. None of these fully captures
usefulness, since a clustering should ultimately serve a downstream purpose, whether
organization, compression, or seeding a search index. The practical habit is to combine a
quantitative measure with a visual inspection and a check against the downstream task.
""",
"principal_component_analysis.md": """
PCA connects to several other ideas worth recognizing. It is the optimal linear
compression scheme in the sense of minimizing reconstruction error for a given number of
dimensions, which is why it often serves as a sanity check and a preprocessing step. It
also relates to the failure modes of linear models: directions of very low variance are
often dominated by noise and should be discarded, while directions of extremely high
variance may indicate a feature that needs scaling. Understanding the eigenvalue spectrum,
and not just the top components, gives insight into the effective dimensionality of the
data and how much genuine structure it contains relative to noise.
""",
"neural_networks_intro.md": """
A common early mistake is to assume that a larger network always helps. Beyond a point,
adding capacity without adding data leads to overfitting, and the extra computation yields
no improvement in generalization. Conversely, a small network on a rich dataset underfits
and would benefit from more capacity. The art of applying neural networks is largely about
matching capacity to data and regularization, then iterating on the architecture only once
the fundamentals are sound. Most impressive results come from good data, sensible
architecture, and careful training, not from a clever trick, though clever tricks are what
get the attention.
""",
"convolutional_neural_networks.md": """
A recurring design question is how receptive field and resolution trade off. Deeper layers
see a larger region of the input, which is what allows them to recognize global objects,
but pooling and striding discard spatial detail that fine-grained tasks such as segmentation
and detection need. Architectures for those tasks therefore use skip connections that
combine deep, semantic features with shallow, high-resolution ones, recovering the detail
that pure downsampling loses. Understanding this tension, between semantic abstraction and
spatial precision, explains the design of most modern vision architectures and why a single
network often taps multiple layers for its final prediction.
""",
"rnn_fundamentals.md": """
A concept worth internalizing is that of the unrolled network. A recurrent model applied to
a sequence of length T is conceptually a very deep feedforward network with shared weights,
one copy per time step. This view explains both the power and the problem: shared weights
let the model reuse a single transformation across positions, but the depth grows with
sequence length, and backpropagation through that depth is where vanishing gradients
originate. Modern practice increasingly replaces this recurrence with attention, which
achieves the same contextual mixing without the sequential depth, but the unrolled view
remains the clearest explanation of why recurrent training is so delicate.
""",
"lstm_and_gru.md": """
A practical consideration is the computational profile of recurrent models. Their
per-step cost is constant and independent of sequence length, which makes them attractive
for streaming settings where inputs arrive over time and cannot be buffered. Attention, by
contrast, needs the whole sequence and scales quadratically. This is why gated recurrent
units still appear in edge deployment and real-time signal processing, where low and
predictable latency matters more than the raw quality of a large transformer. The lesson is
that architectural choice should follow the deployment constraints, and older architectures
often remain the right tool in particular niches long after they are no longer the default.
""",
"transformer_architecture.md": """
A practical insight is that the transformer's components can be scaled semi-independently,
which is a large part of why it is so adaptable. Width, depth, number of heads, and
feedforward ratio can each be tuned, and scaling laws guide how to allocate a compute
budget across them. The feedforward layer, often overlooked, holds a disproportionate share
of parameters and appears to act as a key-value memory of learned patterns, while attention
routes information between positions. Framing the block this way, attention for routing and
feedforward for storage, gives intuition for why both are necessary and why ablating either
degrades performance sharply.
""",
"attention_mechanism.md": """
Interpreting attention weights is tempting but must be done carefully. High attention from
one token to another suggests the model used that information, but the weights are only one
component of the computation, summed across heads and layers, and a low weight does not
prove a token was ignored, because information can flow through other paths. Some research
uses attention as a partial explanation, for example to find where a model looks when
resolving a reference, while other work cautions against over-reading it. The healthy
stance is to treat attention as a useful but incomplete window, and to confirm any
interpretation with causal experiments such as ablations rather than visualizations alone.
""",
}
