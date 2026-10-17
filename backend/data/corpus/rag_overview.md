# Retrieval-Augmented Generation

Retrieval-augmented generation, or RAG, augments a language model with an external
retriever. Given a query, the system fetches relevant passages from a corpus and
conditions the model's answer on them. This grounds generation in external knowledge,
reducing hallucination and allowing the model to answer questions about facts, documents,
or data it was never trained on.

A RAG system has two sides. On the ingestion side, documents are loaded, split into
chunks, embedded into vectors, and stored in an index, often alongside a lexical index
such as BM25. On the query side, the system embeds or otherwise encodes the query,
retrieves the most relevant chunks, optionally reranks them, and passes them to the
generator, which produces an answer, ideally with citations back to the sources.

The main advantage of RAG over fine-tuning is freshness and attribution. Updating the
corpus updates the system's knowledge without retraining, and citations let users verify
claims and trace them to sources. This makes RAG well suited to domains with changing or
proprietary information, where fine-tuning would be stale the moment it finished and
would offer no provenance.

The main weakness of RAG is that it inherits the failure modes of retrieval. If the right
passage is not retrieved, the generator cannot ground its answer, and a poorly designed
system may hallucinate confidently anyway. This is why the surrounding machinery matters:
grading the relevance of retrieved context, rewriting or expanding the query when
retrieval is weak, and evaluating the pipeline end to end. A self-correcting RAG system
detects when retrieval has failed and says so, rather than fabricating an answer. That
capacity to fail loudly, and to recover by adjusting its query, is what separates a
trustworthy RAG system from a demo that only works on carefully chosen questions.
A useful way to reason about a RAG pipeline is to separate the recall problem from the
precision problem. Retrieval must first be capable of finding the right passage somewhere in
its candidate set, which argues for generous retrieval and multiple strategies such as
hybrid search. Then it must rank the best passage highly enough to reach the generator,
which argues for reranking and grading. Improving recall without improving precision fills
the context with noise, and improving precision without improving recall cannot recover a
passage that was never fetched. Diagnosing whether a bad answer is a recall failure or a
precision failure is the first and most useful step when a RAG system underperforms.
