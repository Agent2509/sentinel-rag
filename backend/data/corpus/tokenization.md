# Tokenization

Tokenization converts raw text into the discrete units a language model processes. Since
models operate on numbers, each token maps to an integer identifier through a fixed
vocabulary. The choice of tokenization scheme shapes how efficiently and how accurately
a model handles language.

The dominant approach is subword tokenization, with byte-pair encoding and its variants
being the most common. Byte-pair encoding starts from individual characters or bytes and
repeatedly merges the most frequent adjacent pair into a new token. Over many merges this
produces a vocabulary of common words, morphemes, and byte sequences. Subword
tokenization gracefully handles rare and unseen words by decomposing them into smaller
known pieces, while keeping the vocabulary bounded. WordPiece, used by BERT, and
SentencePiece, used by many multilingual models, are close relatives with different
merging criteria.

The trade-offs are subtle. A larger vocabulary shortens sequences, which reduces compute
and lets more content fit in the context window, but it enlarges the embedding table and
can make rare tokens poorly trained. A smaller vocabulary lengthens sequences and may
split common words into awkward pieces. Tokenization also introduces quirks: numbers and
code tokenize inconsistently, arithmetic becomes unreliable because digits are not
cleanly separated, and non-English text often requires many more tokens per word, raising
cost and hurting quality relative to English.

In retrieval-augmented generation, token counts, not word counts, determine chunk sizes
and how many passages fit in the context window. The cl100k_base encoding, used by recent
OpenAI models, is a common choice, and it is the tokenizer used throughout this project
for chunking and budget accounting.
A subtle practical issue is that tokenization introduces a mismatch between what a language
model sees and what a human sees. Character-level tasks, string manipulation, and arithmetic
are all harder for a model because its units are subwords, and asking a model to count
letters in a word is notoriously unreliable for this reason. Code and structured data
tokenize in ways that reflect the tokenizer's training data, so a model may be surprisingly
good at some programming languages and poor at others. Recognizing these artifacts helps
explain failures that otherwise look like reasoning errors, when they are in fact
tokenization effects baked in before the model ever runs.
