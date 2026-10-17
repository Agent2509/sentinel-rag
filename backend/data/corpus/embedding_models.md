# Embedding Models

Embedding models convert text into vectors such that semantically similar texts are close
in the vector space. They are the core of semantic retrieval, allowing a system to find
passages related in meaning rather than only in keywords.

Older embedding models were trained as dual encoders with contrastive objectives over
large collections of related text pairs. A question encoder and a passage encoder, or a
single shared encoder, learned to place a question near passages that answer it. Modern
retrieval models add instruction tuning. The BGE and E5 families expect a short task
prefix on the query side, such as a sentence telling the model to represent the query for
the purpose of retrieval, while documents are embedded without the prefix. Omitting the
query prefix, or applying it to documents as well, measurably degrades retrieval, because
the model was trained with that asymmetry. Getting this detail right is one of the most
common and consequential mistakes in building a retrieval pipeline.

Quality is measured on benchmarks such as the Massive Text Embedding Benchmark, which
spans retrieval, reranking, clustering, and classification across many languages and
domains. But benchmark scores are a starting point, not a guarantee. Domain fit matters
enormously: a general model may underperform a smaller model fine-tuned on the target
corpus. Beyond the model, several engineering details affect results. Normalizing vectors
to unit length turns inner product into cosine similarity and makes scores comparable.
Truncation length determines how much of a long chunk is actually encoded, and batch size
affects throughput. The embedding dimension trades storage and search cost against
expressiveness.

For retrieval-augmented generation, choosing an embedding model that matches the language
and domain of the corpus, and using it correctly with respect to query prefixes and
normalization, is at least as important as choosing the generator, because a retrieval
failure cannot be recovered by even the best generator.
A practical evaluation should mirror the target workload rather than rely solely on public
benchmarks. Build a small set of representative queries with known relevant passages,
measure retrieval quality directly, and compare candidate embedding models on that set. This
catches domain mismatch that benchmarks miss. It is also worth measuring latency and memory,
since a heavier model may offer only a marginal quality gain that does not justify its cost.
The decision is a balance among quality, speed, storage, and license, and the only way to
choose well is to measure on data that resembles what the system will actually see in
production, not on a leaderboard that may emphasize very different tasks.
