"""Corpus part 4: deployment of LLMs and the retrieval-augmented generation stack."""

DOCS: dict[str, str] = {
"context_window.md": """# Context Windows

The context window is the maximum number of tokens a model can attend to at once,
covering both the prompt and the generated output. It bounds how much retrieved text,
conversation history, and instruction can be supplied in a single call, making it one of
the most important practical constraints in building applications on top of language
models.

Early transformers supported a few thousand tokens. Modern models advertise windows of
hundreds of thousands, and some claim millions. Longer windows let a model read entire
documents, maintain long conversations, and reason over large codebases without
chunking. But length is not free. Attention cost grows quadratically with sequence
length, so latency and memory rise sharply, and even architectures with efficient
attention often slow down considerably at long context. A large window also does not
guarantee effective use: models exhibit a lost-in-the-middle effect, attending less
reliably to information buried in the center of a long context than to content near the
beginning or end.

Effective systems manage the token budget deliberately rather than filling the window.
They retrieve only the most relevant passages, summarize or compress conversation
history, and place the most important instructions near the end where attention is
strongest. Redundant or low-value context is actively harmful, because it dilutes
attention and increases cost.

In retrieval-augmented generation, the context window is the direct constraint on how
many passages, and how large a parent context, can be passed to the generator. This is
why retrieval precision matters so much: every irrelevant chunk that occupies part of the
window is a slot that a more relevant chunk could have used. Good chunking, reranking,
and grading all exist in part to make the most of a limited context budget.
""",
"quantization.md": """# Quantization

Quantization reduces the numerical precision of a model's weights and activations,
typically from sixteen-bit or thirty-two-bit floating point down to eight-bit or even
four-bit integers. The goal is to shrink memory use and speed up inference while
accepting a modest loss in quality.

The idea rests on the observation that neural network weights do not need full floating
point precision to be useful. By mapping a range of values onto a small set of integers
with a per-tensor or per-channel scale and zero point, a model can be stored and computed
with far less memory. A seven-billion-parameter model that occupies about fourteen
gigabytes at sixteen-bit precision can fit in under four gigabytes when quantized to four
bits, which brings it within reach of consumer hardware and enables local deployment.

There are two main approaches. Post-training quantization converts an already-trained
model, using a small calibration dataset to choose good scaling factors and to measure
the error introduced. Quantization-aware training simulates low precision during
training so that the model adapts its weights to be robust under quantization, usually
yielding better quality at aggressive bit widths. Several schemes have become standard
for large language models, including GPTQ and AWQ for weight quantization and the NF4
format used by bitsandbytes for efficient four-bit loading.

The accuracy penalty is small at eight bits and grows more noticeable at four bits,
especially on tasks requiring precise reasoning or arithmetic, and it can vary
significantly across architectures. Quantization is therefore a central tool for running
models cheaply, including the embedding and generation models used in local
retrieval-augmented generation pipelines, where GPU memory is often the binding
constraint.
""",
"lora_and_peft.md": """# LoRA and Parameter-Efficient Fine-Tuning

LoRA, which stands for low-rank adaptation, is a parameter-efficient fine-tuning method
that dramatically reduces the cost of adapting a large model. Instead of updating the
full weight matrices of the pretrained model, LoRA freezes those weights and injects
small trainable low-rank matrices alongside selected layers. The effective weight at
those layers becomes the frozen original plus the product of two much smaller matrices.

The insight is that the update needed to adapt a model to a new task tends to be
low-rank, so it can be represented compactly. This reduces the number of trainable
parameters by orders of magnitude, which in turn slashes optimizer memory, the dominant
cost of full fine-tuning. The original weights stay untouched, so LoRA also avoids
catastrophic forgetting of general knowledge, and because the adaptation is stored as
tiny separate matrices, multiple adapters can be trained for different tasks and swapped
over a single base model at inference time.

The main hyperparameters are the rank of the low-rank matrices, which controls capacity,
and the choice of which modules to adapt, typically the attention projection matrices.
Higher rank means more expressive updates and more parameters. LoRA is one member of a
broader family of parameter-efficient fine-tuning methods, alongside adapters, prefix
tuning, and prompt tuning, which inject trainable parameters in different places.

These techniques have made fine-tuning accessible on a single GPU and are widely used to
specialize models for a domain, a writing style, or reliable structured output while
retaining general capability. They are not a complete replacement for full fine-tuning
when the task diverges greatly from the pretraining distribution, but for most adaptation
needs they offer an excellent trade-off between cost and quality.
""",
"rag_overview.md": """# Retrieval-Augmented Generation

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
""",
"chunking_strategies.md": """# Chunking Strategies

Chunking splits documents into passages small enough to embed and retrieve efficiently
but large enough to carry meaning. The choice of strategy strongly affects retrieval
quality, and it is one of the highest-leverage decisions in a retrieval-augmented
generation system.

Fixed-size chunking divides text into equal token windows, optionally with overlap
between consecutive windows. It is simple, predictable, and cheap, but it is blind to
content, so it can split a sentence, a definition, or a line of reasoning across a
boundary. Overlap, for example fifty tokens shared between neighbors, preserves some
context across boundaries at the cost of storing redundant text and retrieving duplicate
information.

Hierarchical chunking builds two levels at once: small child chunks for precise matching
and large parent chunks for richer context. The retriever matches at the child level,
where vectors are focused, then expands the winning children to their parents before
passing them to the generator, which gets coherent surrounding context. This separates
the granularity of search from the granularity of generation, and is a common way to get
both precision and context.

Semantic chunking detects topic shifts rather than fixed lengths. It splits text into
sentences, embeds each, and measures similarity between consecutive sentences, breaking
where similarity drops below a threshold such as the twenty-fifth percentile. This keeps
coherent ideas together and cuts where the subject changes, producing variable-length
chunks that respect meaning. The cost is an embedding pass over every sentence at ingest
time and a dependence on the quality of the sentence embeddings.

No strategy dominates. Short queries and precise facts favor small chunks, while
explanatory questions favor larger context. The right choice depends on the documents,
the questions, and the generator's context budget, which is exactly why a laboratory that
can compare strategies side by side and measure them is more valuable than any single
heuristic.
""",
"embedding_models.md": """# Embedding Models

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
""",
"vector_databases.md": """# Vector Databases and Indexes

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
""",
"hybrid_search.md": """# Hybrid Search and Reciprocal Rank Fusion

Hybrid search combines lexical retrieval, such as BM25, with semantic vector search.
Lexical retrieval matches exact terms and excels at names, rare keywords, acronyms, and
queries where the precise wording matters. Semantic retrieval matches meaning and excels
at paraphrases, synonyms, and questions phrased very differently from the documents.
Together they cover each other's weaknesses, which is why hybrid retrieval is a strong
default for production systems.

BM25 scores documents by term frequency with saturation, combined with inverse document
frequency that rewards terms rare across the corpus, and a length normalization. It
requires no training, is fast and transparent, and is difficult to beat on keyword-heavy
queries. Vector search embeds the query and finds nearby documents, handling vocabulary
mismatch and capturing topical similarity. Neither alone is sufficient: pure lexical
search misses paraphrases, and pure vector search can miss exact matches that a user
clearly intended.

Fusing the two result lists requires a method that combines rankings expressed on
incomparable scales, since BM25 scores are unbounded and cosine similarities lie in a
fixed range. Reciprocal rank fusion sidesteps this by ignoring the raw scores entirely.
Each document receives a contribution for every list it appears in, equal to one over a
constant plus its rank in that list. The constant, typically sixty, softens the influence
of the very top ranks. The contributions are summed across lists, and the fused ranking
is sorted and truncated to the final top-k.

Reciprocal rank fusion is simple, effective, and robust, and it needs no score
normalization or tuning of relative weights. The fused results are often passed to a
reranker for a final, more careful ordering. For a self-correcting retrieval system, the
fused candidate set is also what a grader inspects to decide whether the retrieved
context is good enough to answer or whether the query must be rewritten.
""",
"reranking.md": """# Reranking

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
""",
"hyde.md": """# Hypothetical Document Embeddings

Hypothetical document embeddings, or HyDE, improves retrieval for queries that are short,
ambiguous, or phrased very differently from the documents they should match. Instead of
embedding the raw query, HyDE first asks a language model to write a hypothetical passage
that would answer the query, and then embeds that generated passage for the search.

The intuition is a form of distributional alignment. A terse question and its answer
often live in different regions of embedding space, because a question and a document
statement have different surface forms. A generated answer passage, by contrast, looks
much like a real stored document, so its embedding lands closer to the relevant passages.
This bridges the vocabulary and style gap between how users ask and how documents are
written, and it is especially helpful for zero-shot retrieval and for questions that
contain few useful keywords.

The costs are an additional generation call and the risk that the hypothetical document
drifts off topic. If the generated passage is inaccurate or generic, its embedding may
pull retrieval toward irrelevant content, making results worse rather than better. HyDE
is therefore most effective when the generator has enough knowledge to produce a
plausible passage, and least effective when the query concerns obscure or rapidly
changing facts the model does not know.

Because of this, the best use of HyDE is as a fallback rather than a default. The system
retrieves normally, grades the retrieved context for relevance, and only when the grade is
poor generates a hypothetical document and retrieves again. This self-correcting loop
pays the extra generation cost only when the first attempt fails, and it gives the system
a principled way to recover from the vocabulary gap without degrading the many queries
that are already handled well by straightforward retrieval.
""",
}
