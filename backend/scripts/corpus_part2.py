"""Corpus part 2: classical ensembles and the deep learning core."""

DOCS: dict[str, str] = {
"random_forests.md": """# Random Forests

A random forest is an ensemble of decision trees that reduces variance by averaging
many decorrelated trees. Each tree is trained on a bootstrapped sample of the data and,
at every split, considers only a random subset of features. This double randomness
ensures the trees make different mistakes, so their errors cancel when combined.

For classification the forest takes a majority vote, and for regression it averages the
predictions. Because each tree sees a different bootstrap sample, the examples left out
of a given tree form its out-of-bag set, which provides a free validation estimate
without holding data aside. The out-of-bag error is often a reliable proxy for test
performance and is one reason random forests need little tuning.

Feature importance can be extracted by measuring how much each feature reduces impurity
across all trees. This is useful for interpretation, though impurity-based importances
are biased toward high-cardinality features; permutation importance is a more robust
alternative. The number of trees is a hyperparameter, but performance tends to plateau,
so more trees rarely hurt beyond added compute. Maximum depth, minimum samples per
leaf, and the number of features considered at each split are the knobs that matter
most.

Random forests are robust to noisy features, handle mixed data types without scaling,
and are resistant to overfitting given enough trees. They are an excellent default for
tabular data and a reliable benchmark. Gradient-boosted trees, which build trees
sequentially to fit the residual errors of previous ones, often achieve higher accuracy
on structured data, but they require more careful tuning and are more prone to
overfitting if left unchecked. Knowing both, and when each shines, is core tabular
machine learning knowledge.
""",
"support_vector_machines.md": """# Support Vector Machines

A support vector machine finds the hyperplane that separates two classes with the
largest possible margin. Intuitively, a wide margin leaves room for error and tends to
generalize well. Only the points closest to the boundary, called support vectors,
determine the position of the hyperplane, which gives the method a sparse and elegant
geometric interpretation.

Real data is rarely perfectly separable, so the soft-margin formulation allows some
points to violate the margin, controlled by a penalty parameter usually denoted C. A
large C prioritizes classifying every training point correctly and risks overfitting; a
small C tolerates more violations and produces a wider, more robust margin. Tuning C is
central to using an SVM well.

The kernel trick is the SVM's signature idea. Instead of explicitly mapping data into a
higher-dimensional space where it becomes linearly separable, the algorithm uses a
kernel function that computes inner products in that space implicitly. The linear,
polynomial, and radial basis function kernels cover most needs, with the RBF kernel
being a strong general-purpose choice. This lets SVMs learn nonlinear boundaries while
remaining grounded in a linear formulation.

SVMs were the dominant classifier before deep learning and still excel on small,
high-dimensional datasets, such as text with thousands of features and few examples.
Their main limitations are training time, which scales poorly with the number of
samples, and the fact that they output decision values rather than probabilities, so
calibration is needed for probabilistic use. They remain a valuable tool when data is
scarce and a margin-based classifier is appropriate.
""",
"kmeans_clustering.md": """# K-Means Clustering

K-means partitions data into k groups by alternating two simple steps. First, assign
every point to the nearest centroid. Second, recompute each centroid as the mean of the
points assigned to it. Repeating until assignments stop changing minimizes the
within-cluster sum of squared distances, a quantity known as inertia.

The algorithm is fast, simple, and scales to large datasets, which explains its
popularity. It also carries clear assumptions. It implicitly treats clusters as
roughly spherical and similar in size, because a point always joins the nearest
centroid under Euclidean distance. It is sensitive to initialization, since a poor
starting configuration can trap it in a bad local minimum; k-means++ seeding spreads
the initial centroids out and largely fixes this. Choosing the number of clusters k is
not automatic, and practitioners use the elbow method, which looks for the point where
inertia stops dropping sharply, or the silhouette score, which measures how well points
sit within their clusters.

K-means makes hard assignments: each point belongs to exactly one cluster. Gaussian
mixture models generalize this by modeling each cluster as a Gaussian and assigning
soft probabilities, which better handles overlapping or elongated clusters. Mini-batch
k-means processes small random samples per iteration to scale to very large data.

The same partitioning idea appears in vector search. An inverted file index clusters
vectors into cells and searches only the nearest cells, accepting a small loss in
recall for a large gain in speed. Understanding k-means therefore pays off twice: once
for clustering itself, and again when reasoning about approximate nearest-neighbor
indexes used in retrieval systems.
""",
"principal_component_analysis.md": """# Principal Component Analysis

Principal component analysis, or PCA, is a linear method for reducing dimensionality by
finding the directions along which the data varies most. The first principal component
is the direction of maximum variance, the second is the next most variable direction
orthogonal to the first, and so on. These directions are the eigenvectors of the data's
covariance matrix, and the corresponding eigenvalues measure how much variance each
captures.

By keeping only the top components, you project the data onto a lower-dimensional
subspace that preserves as much variation as possible. This compresses the data,
removes redundancy between correlated features, and can denoise by discarding
low-variance directions that are mostly noise. PCA is widely used for visualization,
preprocessing, and speeding up downstream models.

Two preprocessing details matter. Features must be standardized first, because PCA is
sensitive to scale and would otherwise be dominated by variables measured in large
units. And PCA assumes linear structure; it finds global directions rather than the
curved manifolds that nonlinear methods such as t-SNE and UMAP reveal. For
visualization of complex data, t-SNE and UMAP often produce more interpretable
embedding plots, at the cost of being slower and not preserving global distances.

In retrieval, dimensionality reduction is used cautiously. Shrinking embeddings saves
storage and speeds search, but it can distort the semantic similarity that embeddings
were trained to encode, degrading retrieval quality. A related transform, whitening,
scales components to unit variance and is occasionally applied in embedding pipelines
to spread information more evenly across dimensions. PCA is best understood as a
powerful, interpretable linear tool whose limitations come precisely from its linearity
and its focus on variance rather than task-relevant signal.
""",
"neural_networks_intro.md": """# Introduction to Neural Networks

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
""",
"convolutional_neural_networks.md": """# Convolutional Neural Networks

Convolutional neural networks exploit the spatial structure of data by sliding small
learnable filters, or kernels, across the input. Each filter computes a dot product at
every position, producing a feature map that highlights where its pattern occurs. The
same filter is reused everywhere, a property called weight sharing, which dramatically
reduces the number of parameters compared to a fully connected layer and bakes in
translation equivariance.

A typical convolutional block combines convolution, a nonlinearity, and pooling.
Pooling reduces spatial resolution by summarizing local regions, which lowers compute
and grants a degree of translation invariance. Stacking blocks builds a hierarchy:
early layers detect edges and simple textures, middle layers detect parts and motifs,
and late layers detect whole objects. Padding preserves spatial dimensions, while
stride controls how aggressively the input is downsampled.

Convolutional networks transformed computer vision and remain strong for images, video,
and audio. Residual connections, which add the input of a block to its output, allow
networks to grow very deep without degrading, and are the backbone of architectures
such as ResNet. Depthwise separable convolutions factor a standard convolution into two
cheaper operations, enabling efficient models for mobile devices. Techniques such as
batch normalization, data augmentation, and transfer learning from large pretrained
models are standard practice.

Vision transformers now compete with and sometimes surpass convolutional networks on
large datasets, but convolutions retain a useful inductive bias about locality that
helps when data is limited. In many production settings, a hybrid approach or a
well-tuned convolutional backbone remains the pragmatic choice, and understanding
convolution is essential context for interpreting modern vision architectures.
""",
"rnn_fundamentals.md": """# Recurrent Neural Networks

A recurrent neural network processes sequences by maintaining a hidden state that is
updated at each time step. The same weights are applied at every position, so the model
can handle inputs of any length and share statistical strength across time. This makes
recurrence a natural fit for text, speech, and time series.

At each step the network combines the current input with the previous hidden state
through a learned transformation and a nonlinearity, producing a new hidden state that
summarizes everything seen so far. For sequence labeling, an output is produced at each
step; for sequence classification, only the final hidden state is used. The recurrent
formulation means the network has an unbounded memory in principle, able to condition
on arbitrarily distant context.

In practice, training basic recurrent networks is difficult. Gradients are propagated
backward through many time steps, and repeated multiplication by the recurrent weight
matrix causes them to shrink toward zero or grow without bound. Exploding gradients are
handled by clipping their norm, but vanishing gradients are more insidious, causing the
network to forget long-range dependencies. This is why plain recurrent networks
struggle with tasks that require remembering information over hundreds of steps.

A deeper structural limitation is parallelism. Because each step depends on the previous
hidden state, the computation is inherently sequential and cannot be parallelized across
time, which makes training slow on modern hardware designed for parallel work. These two
problems, difficulty learning long-range dependencies and poor hardware utilization,
motivated the invention of gated recurrent units and ultimately attention-based
transformers, which replace recurrence with operations that compare all positions in
parallel.
""",
"lstm_and_gru.md": """# LSTM and GRU

Long short-term memory networks were designed to solve the vanishing-gradient problem
that plagues basic recurrent networks. An LSTM maintains two states: the hidden state
that is exposed to the rest of the network and a cell state that acts as a long-term
memory. Three gates control the flow of information. The input gate decides what new
information to write, the forget gate decides what to discard, and the output gate
decides what part of the cell state to expose.

The crucial design choice is the additive update to the cell state. Because information
flows along the cell state through addition rather than repeated multiplication,
gradients can propagate across many time steps without shrinking. This allows LSTMs to
learn dependencies spanning hundreds of steps, a major advance when they were
introduced.

The gated recurrent unit, or GRU, simplifies the LSTM by merging the cell and hidden
states and using two gates instead of three. It has fewer parameters and often trains
faster, while matching LSTM accuracy on many tasks. The choice between them is
empirical, and neither strictly dominates.

Both architectures powered a generation of results in machine translation, speech
recognition, and language modeling. Bidirectional variants read the sequence in both
directions and concatenate the representations, which helps for tasks where the whole
sequence is available, such as encoding text. Encoder-decoder setups with attention over
the encoder states became the leading approach to translation before transformers
displaced them. Despite being largely superseded for large-scale language modeling, LSTMs
and GRUs remain valuable for streaming and resource-constrained settings, where their
constant per-step cost and small memory footprint are attractive compared to the
quadratic attention of transformers.
""",
"transformer_architecture.md": """# The Transformer Architecture

The transformer replaces recurrence with self-attention, allowing every position in a
sequence to attend to every other position simultaneously. This parallelizability is the
key to its scalability and the reason transformers now dominate natural language
processing, vision, and beyond.

A transformer block contains two sublayers: multi-head self-attention and a
position-wise feedforward network. Each sublayer is wrapped with a residual connection
and layer normalization, which stabilize training and allow very deep stacks. Multi-head
attention runs several attention operations in parallel, each with its own learned
projections, so the model can attend to different kinds of relationships at once, such
as syntactic roles in one head and coreference in another. The feedforward network,
typically two linear layers with a nonlinearity, transforms each position independently
and contributes a large share of the parameters.

Because self-attention is permutation invariant, transformers add positional encodings
to the input so the model can distinguish order. Encoder-only models such as BERT read
the whole sequence bidirectionally and excel at understanding tasks like classification
and extractive question answering. Decoder-only models such as the GPT family apply
causal masking so each position sees only earlier ones, which makes them natural
generators and the basis of modern chat assistants. Encoder-decoder models such as T5
separate reading from writing and suit sequence-to-sequence problems.

The architecture's main weakness is cost: attention scales quadratically with sequence
length, so long contexts are expensive in compute and memory. This has inspired a large
body of work on efficient attention, including sparse, linear, and sliding-window
variants. Yet the original design remains remarkably durable. The transformer's success
is less about any single component and more about how cleanly it scales with data,
parameters, and compute, which is exactly what modern hardware and training pipelines
reward.
""",
"attention_mechanism.md": """# Attention Mechanism

Attention computes a weighted sum of values, where the weights express how relevant each
value is to a given query. It is the mechanism that lets a model dynamically focus on
the most useful parts of its input rather than compressing everything into a single
fixed vector.

In scaled dot-product attention, queries and keys are compared using dot products to
produce scores. Those scores are divided by the square root of the key dimension, a
scaling that keeps the values in a range where the softmax gradients behave well, and
then passed through a softmax to yield weights that sum to one. The output is the
weighted average of the values. The three inputs, queries, keys, and values, are linear
projections of the same or different sequences, which is why the same operation serves
both self-attention and cross-attention.

Self-attention applies the operation within a single sequence, letting each token gather
context from every other token. Cross-attention uses queries from one sequence and keys
and values from another, which is how an encoder-decoder model aligns the input with the
output being generated. Multi-head attention repeats the operation in parallel with
different learned projections, allowing the model to represent several relationships at
once and then combine them.

The central advantage of attention over recurrence is the direct path between any two
positions. In a recurrent network, information must travel step by step, so long-range
dependencies fade; in attention, every pair interacts in a single step. Attention
weights are also inspectable, offering a partial window into what the model attends to.
The cost is quadratic scaling in sequence length, and the mechanism's great strength,
its ability to relate distant tokens, is inseparable from that expense. Efficient
attention research aims to keep the benefit while taming the cost.
""",
}
