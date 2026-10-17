# Principal Component Analysis

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
PCA connects to several other ideas worth recognizing. It is the optimal linear
compression scheme in the sense of minimizing reconstruction error for a given number of
dimensions, which is why it often serves as a sanity check and a preprocessing step. It
also relates to the failure modes of linear models: directions of very low variance are
often dominated by noise and should be discarded, while directions of extremely high
variance may indicate a feature that needs scaling. Understanding the eigenvalue spectrum,
and not just the top components, gives insight into the effective dimensionality of the
data and how much genuine structure it contains relative to noise.
