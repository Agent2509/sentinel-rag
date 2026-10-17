# Logistic Regression

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
A practical consideration is class imbalance. When one class is far rarer than the other,
the model can achieve high accuracy by predicting the majority class, which is useless. In
that setting, accuracy is the wrong metric; precision, recall, and the area under the
precision-recall curve are more informative. Thresholds can be tuned to trade precision
against recall according to the cost of each type of error, and the coefficients remain
interpretable, so logistic regression is often the model of choice when a decision must be
explained to a stakeholder. Its simplicity is a feature, not a limitation.
