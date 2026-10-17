# Reranking

Reranking is a second retrieval stage that reorders an initial set of candidates using a
more accurate but more expensive model. The first stage is optimized for recall, quickly
fetching a generous candidate set. The reranker is optimized for precision, carefully
scoring each candidate against the query to put the best passages on top.

The most effective rerankers are cross-encoders. Instead of embedding the query and
passage independently as a dual encoder does, a cross-encoder feeds the query and passage
together through a transformer and produces a single relevance score. Because the model
sees both texts jointly, it can capture fine-grained interaction, negation, and precise
semantic alignment that separately computed embeddings cannot express. The cost is that
the cross-encoder must run once per query-passage pair, which is far too slow to apply to
an entire corpus, but perfectly affordable for a few dozen or a few hundred candidates.

The standard pattern is therefore retrieve-then-rerank: fetch the top fifty candidates
with hybrid search, rerank them with a cross-encoder, and keep the top five for
generation. This consistently improves answer quality and is often the single
highest-value addition after a solid first-stage retriever, because it directly addresses
the fact that the correct passage may be present in the candidate set but ranked too low
for the generator to see.

Reranking also provides a cleaner relevance signal. A calibrated cross-encoder score is a
better basis for deciding whether retrieved context is adequate than a fused rank score,
which is what a self-correcting loop needs when it decides whether to answer, rewrite the
query and retrieve again, or report that the corpus does not contain the answer.
A practical consideration is the cost and latency budget. A cross-encoder reranker adds a
forward pass per candidate, so the number of candidates directly affects latency. Tuning
that number is a trade-off between the chance of including the right passage and the time
spent reranking. A common approach is to retrieve a generous set, rerank, and keep the top
few, adjusting the candidate count based on measured latency. Caching reranker scores for
repeated queries helps under load. Because reranking often yields the largest quality gain
for the least architectural change, it is frequently the first optimization to add once a
basic retrieval pipeline is working, before more elaborate changes.
