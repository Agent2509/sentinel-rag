# Word and Sentence Embeddings

Embeddings map discrete tokens or texts into dense vectors such that semantic similarity
corresponds to geometric closeness. They turn the sparse, arbitrary world of words into a
continuous space where distance is meaningful, and they are the foundation of semantic
search and retrieval.

Early word embeddings learned a single vector per word from co-occurrence statistics.
Word2Vec trained vectors by predicting a word from its neighbors or vice versa, and
famously captured analogies such as king minus man plus woman yielding queen. GloVe
derived vectors from global co-occurrence counts. These static embeddings are efficient
and interpretable, but each word gets exactly one vector, so they cannot represent
polysemy: the word bank has the same representation whether it means a riverbank or a
financial institution.

Contextual embeddings solved this by producing a different vector for a word depending on
its surrounding sentence. Models such as ELMo and BERT built on this idea, capturing
richer, context-sensitive meaning. Sentence embeddings take the next step, representing
an entire sentence or passage as a single vector, which is what makes semantic search
over documents possible.

Sentence embedding models are typically trained with contrastive objectives. Positive
pairs, such as a question and its answer or two paraphrases, are pulled together in the
vector space, while unrelated pairs are pushed apart. The BGE and E5 families, including
bge-small-en-v1.5, are trained this way. Many retrieval models expect an instruction
prefix on the query side, telling the model that the text is a search query, while
documents are embedded raw. Normalizing the output vectors to unit length turns inner
product into cosine similarity, which is why exact inner-product search over normalized
embeddings is equivalent to nearest-neighbor search by cosine distance.
A common pitfall in practice is applying the wrong notion of similarity to embeddings.
Cosine similarity and Euclidean distance agree on normalized vectors but diverge otherwise,
and dot-product models such as those trained with inner-product objectives may care about
magnitude as well as direction. Mixing embeddings from two different models, or from a
model used without its expected instruction prefix, silently produces poor results without
any error. Treating the embedding pipeline, the model, its prefix convention, its
normalization, and its distance metric, as a single unit that must be consistent end to end
is the discipline that separates retrieval that works from retrieval that mysteriously does
not.
