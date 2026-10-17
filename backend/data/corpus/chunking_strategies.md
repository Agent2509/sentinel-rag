# Chunking Strategies

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
A practical point is that chunk boundaries interact with the structure of the source
material. Documents with clear headings and sections should be split along those boundaries,
because the natural unit of meaning is the section, not an arbitrary token count. Ignoring
structure often scatters a single idea across chunks or merges unrelated ideas into one.
Many systems enrich each chunk with metadata such as its document title, section heading,
and position, and prepend a short header to the embedded text so the vector reflects the
context the chunk belongs to. These small enrichments frequently improve retrieval more
than switching strategies, because they give the embedding model the context that the raw
chunk text alone lacks.
