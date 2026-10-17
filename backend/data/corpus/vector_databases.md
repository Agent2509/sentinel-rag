# Vector Databases and Indexes

A vector index stores embeddings and supports fast nearest-neighbor search. Because an
exact search compares the query against every stored vector in turn, its cost grows
linearly with the collection size, which becomes prohibitive at scale. Approximate
nearest-neighbor methods trade a small, tunable loss in recall for large gains in speed,
and they are the backbone of modern semantic search.

FAISS is a widely used library that offers several index types. The flat inner-product
index performs exact search by computing inner products against all vectors; after
normalizing embeddings to unit length, this is equivalent to cosine similarity, and it is
ideal for small and medium collections where exactness is worth the linear cost and no
training is required. Inverted file indexes partition the vectors into clusters and
probe only the nearest clusters at query time, which speeds up search considerably at the
price of occasionally missing a true neighbor. Graph-based indexes such as HNSW build a
navigable small-world graph and provide an excellent trade-off between recall and
latency, at the cost of memory and build time. Product quantization compresses vectors
into short codes to save memory, often combined with the methods above.

Dedicated vector databases such as Pinecone, Weaviate, Qdrant, and Milvus wrap these
indexes with persistence, metadata filtering, replication, and horizontal scaling. They
are valuable for production systems with large, changing collections and complex
filtering needs.

For a local project with a few thousand chunks, an in-memory flat index is the simplest
and best choice: it is exact, requires no external service, and its linear scan is fast
enough that approximation would add complexity without benefit. Choosing the right index
is a matter of matching the method's trade-offs to the scale and accuracy requirements of
the problem, rather than defaulting to the most sophisticated option.
A practical warning is that a vector database is not automatically the right answer to a
retrieval problem. For collections with thousands rather than millions of vectors, an
in-memory index is simpler, has no operational overhead, and is exact. Introducing an
external service adds a network hop, a schema to maintain, a consistency model to reason
about, and one more thing that can fail during a demonstration. The decision to adopt a
database should be driven by scale, filtering requirements, concurrency, and durability
needs that actually exist, not by the assumption that production requires one. Measuring the
straightforward solution first often reveals that it is sufficient, and adopting complexity
only when it is justified keeps the system maintainable.
