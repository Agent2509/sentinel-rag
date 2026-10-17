# Random Forests

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
A valuable property of forests is their tolerance for messy data. Missing values can be
handled with surrogate splits or imputation, irrelevant features are largely ignored
because they rarely win the random feature selection at a split, and outliers exert little
influence because predictions are averages. This robustness makes forests a reliable first
model on a new tabular dataset, giving a strong baseline before investing in more elaborate
approaches. The main cost is that they are bulky, since each tree stores its structure, and
slower at inference than a single decision tree, though the trade-off is usually well worth
it for the accuracy and stability they provide.
