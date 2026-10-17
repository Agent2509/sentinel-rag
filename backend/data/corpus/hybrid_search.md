# Hybrid Search and Reciprocal Rank Fusion

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
A practical refinement is to weight the two retrieval branches or vary how many candidates
each contributes. If a workload is heavily keyword-oriented, more weight on the lexical side
helps; if it is conversational and paraphrase-heavy, more weight on vectors helps.
Reciprocal rank fusion handles fusion elegantly but is not the only option, and some systems
combine normalized scores or use a learned fusion. The simplest robust default, however,
remains RRF over a generous candidate set from both branches, followed by a reranker. This
layering, cheap retrieval for recall and expensive reranking for precision, is a pattern
that recurs throughout information retrieval and explains much of why hybrid systems
outperform any single method.
