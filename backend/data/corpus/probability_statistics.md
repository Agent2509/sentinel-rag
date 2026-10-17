# Probability and Statistics

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
A subtle but important point is the difference between the joint, marginal, and
conditional distributions. The joint describes two variables together, the marginal
integrates one out, and the conditional asks about one given the other. Independence means
the joint factorizes into a product of marginals, and conditional independence, which is
much weaker and far more common, is the assumption that makes graphical models and naive
Bayes tractable. Recognizing when a modeling assumption is truly needed, rather than
merely convenient, prevents the classic error of imposing independence where the data
clearly violates it.
