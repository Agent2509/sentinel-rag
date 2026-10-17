# Decision Trees

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
Trees have a distinctive relationship to feature engineering. Because they split on
thresholds, they are invariant to monotonic transformations of individual features, so
scaling and normalization are unnecessary. They also capture interactions automatically
through their branching structure. However, they struggle with smooth linear relationships,
which they approximate with many axis-aligned splits, and they cannot extrapolate beyond
the range of the training data, a limitation that matters for regression on trending
series. These characteristics explain why trees dominate tabular data while linear models
and neural networks remain preferable for problems with strong smooth structure.
