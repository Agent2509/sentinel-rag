# Hypothetical Document Embeddings

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
A practical variant is to generate several hypothetical documents and average their
embeddings, which smooths over the idiosyncrasies of any single generation and tends to be
more stable than relying on one. Another is to combine HyDE with the original query by
retrieving with both and merging the results, so a poor hypothetical document cannot
single-handedly derail retrieval. The general principle is that HyDE is one signal among
several, and it should be combined rather than substituted. Treating it as a contributor to
a fusion, alongside the raw query and lexical search, gets the benefit of bridging the
vocabulary gap without the full risk of a hallucinated passage dominating the results.
