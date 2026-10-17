# Monitoring and Data Drift

After a model is deployed, its performance can degrade silently as the world changes.
Monitoring detects this degradation and triggers corrective action before users notice,
which is why it is one of the most important and most neglected parts of a production
machine learning system.

Data drift is a change in the distribution of inputs. Users begin asking about new topics,
a domain introduces new vocabulary, or upstream data pipelines shift in subtle ways.
Concept drift is a change in the relationship between inputs and the correct output, so
that even familiar inputs now require different answers. Both can hurt accuracy even when
the model's code and weights are unchanged, which makes them easy to miss.

Because ground-truth labels often arrive late or not at all, monitoring relies heavily on
proxies. Teams track the distribution of predictions, model confidence, input statistics,
and business metrics, comparing them against the training distribution using statistics
such as the population stability index or Kullback-Leibler divergence. When a metric
crosses a threshold, an alert fires, prompting investigation or an automatic retraining
job. A common failure mode is alert fatigue, where too many noisy alerts train the team to
ignore them, so thresholds must be chosen with care.

Retrieval-augmented generation adds its own monitoring concerns. A stale corpus degrades
answers even when the language model is perfectly healthy, so monitoring must include
retrieval quality, such as the relevance of retrieved passages, and answer faithfulness,
such as whether the generated text is supported by the retrieved context. Logging complete
traces, with the query, the retrieved chunks, the grades, and the final answer, is what
makes it possible to diagnose a bad response after the fact and to build the datasets that
drive the next round of improvement.
A practical foundation for all monitoring is structured logging of complete requests. For a
RAG system, that means recording the query, the retrieved passages with their scores, any
grading decisions, the rewritten query if the correction loop fired, and the final answer
along with its citations. Without this record, diagnosing a complaint reduces to
speculation. With it, you can replay the exact decision path and identify whether retrieval,
grading, or generation went wrong. This log is also the raw material for building evaluation
sets from real traffic, closing the loop between production failures and the next round of
development, which is the essence of operating a system rather than merely deploying one.
