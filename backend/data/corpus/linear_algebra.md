# Linear Algebra for Machine Learning

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
A useful mental model is to treat every tensor operation as a statement about shapes.
When a computation goes wrong, the first thing to check is whether the dimensions line up,
because broadcasting rules can silently expand a mismatched operand and hide a bug.
Understanding broadcasting, and knowing when to insert an explicit dimension, prevents a
large share of practical errors. It also pays to remember that many apparently exotic
operations, from convolutions to attention, are at bottom batched matrix multiplications
with clever reshaping, so optimizing for efficient matrix products is often the single
most effective performance lever.
