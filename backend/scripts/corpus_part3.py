"""Corpus part 3: embeddings, transfer learning, and large language models."""

DOCS: dict[str, str] = {
"positional_encoding.md": """# Positional Encoding

Self-attention is permutation invariant: if you shuffle the tokens of a sequence, the
attention output is the same up to the corresponding shuffle. The mechanism has no
inherent notion of order, yet language depends heavily on order. The phrase "the dog bit
the man" means something very different from "the man bit the dog". Transformers resolve
this by injecting positional information into the token representations before the first
attention layer.

The original transformer uses sinusoidal positional encodings: fixed functions of
position and dimension, with sine waves of different frequencies. Because the patterns
are smooth and periodic, the model can generalize to sequence lengths beyond those seen
during training, and relative offsets are encoded implicitly through the linear
relationships between sinusoids at different positions.

An alternative is learned positional embeddings, a lookup table with one vector per
position, trained alongside the model. This is simple and common in decoder-only
architectures, but the table is fixed to the maximum length seen in training, so
extending context requires retraining or interpolation of the embeddings.

Modern large models increasingly use rotary position embeddings, known as RoPE. RoPE
rotates the query and key vectors by an angle proportional to their position, so the dot
product between them depends on their relative distance. This encodes relative position
elegantly and extrapolates to longer contexts more gracefully than absolute embeddings.
Another approach, ALiBi, adds a distance-based bias directly to the attention scores,
penalizing far-apart tokens. Handling very long context robustly is an active research
area, and the choice of positional scheme is one of the main determinants of how well a
model generalizes beyond its training window.
""",
"transfer_learning.md": """# Transfer Learning

Transfer learning reuses knowledge from a model trained on one task to improve
performance on another. Instead of learning from scratch, you begin with pretrained
weights and adapt them to the new problem. This is essential whenever labeled data is
scarce, which is the common case in practice.

The intuition is that a model trained on a large, broad dataset has learned general
features that transfer to related tasks. In vision, early layers of a convolutional
network detect edges and textures that are useful for almost any image task. In
language, a pretrained transformer has absorbed grammar, world knowledge, and reasoning
patterns. Reusing these features means the new task needs far less data and compute.

The typical recipe is to freeze the early layers, which capture general features, and
fine-tune the later, more task-specific layers. How much to fine-tune depends on how
similar the new task is and how much data it has: with a lot of data and a very
different domain, updating more of the model helps; with little data, freezing more and
training only a small head avoids overfitting. Alternatively, the pretrained model can
serve purely as a frozen feature extractor, with a lightweight classifier on top.

Transfer learning underlies modern natural language processing, where a single
pretrained model is adapted to classification, question answering, summarization, and
generation. The embedding models used in retrieval are also produced this way: a general
sentence encoder is fine-tuned with contrastive objectives so that semantically similar
texts land close together. Transfer learning is arguably the most important practical
development in modern machine learning, because it turns the enormous cost of pretraining
into a one-time investment shared across countless downstream applications.
""",
"fine_tuning.md": """# Fine-Tuning

Fine-tuning continues training a pretrained model on a narrower dataset so that it
specializes for a target task or domain. Where transfer learning may freeze most of the
model, fine-tuning updates its weights, adjusting both the internal representations and
the output behavior to fit the new data.

The procedure is straightforward: load the pretrained weights, train on the new dataset
with a small learning rate to avoid destroying the pretrained knowledge, and monitor a
validation split to prevent overfitting. The learning rate is critical, because too
large a step can catastrophically forget the general capabilities learned during
pretraining, while too small a step wastes the adaptation.

Full fine-tuning updates every parameter and generally yields the best quality, but it
requires substantial memory and compute, since optimizer states roughly triple the
parameter footprint. Parameter-efficient methods such as LoRA, adapters, and prefix
tuning freeze the base model and train only a small number of additional parameters,
cutting cost dramatically with modest quality loss. These methods have made fine-tuning
accessible on a single GPU and are now the default for many applications.

Different goals call for different flavors of fine-tuning. Supervised fine-tuning on
instruction and response pairs teaches a base model to follow prompts and adopt an
assistant persona. Preference-based methods such as reinforcement learning from human
feedback further align outputs with human judgment, improving helpfulness and safety.
The recurring risks are catastrophic forgetting and overfitting on small datasets, and
the standard mitigations are mixing in general-purpose data, early stopping, and careful
evaluation on held-out tasks before deployment.
""",
"tokenization.md": """# Tokenization

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
""",
"word_embeddings.md": """# Word and Sentence Embeddings

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
""",
"gpt_architecture.md": """# GPT Architecture

GPT models are decoder-only transformers trained to predict the next token in a
sequence. They apply causal masking so that each position can attend only to itself and
earlier positions, which prevents the model from seeing the future. This makes generation
autoregressive: the model produces one token at a time and appends each new token to the
context before predicting the next.

The architecture stacks decoder blocks, each containing masked self-attention followed by
a feedforward network, with residual connections and layer normalization. The causal mask
is what enforces the left-to-right generation order. At inference, a key-value cache
stores the attention keys and values from previous steps so that generating each new
token does not require recomputing the entire prefix, which is essential for making
generation tractable.

The model is trained with a simple objective, predicting the next token across a huge
corpus. Scaling laws show that increasing parameters, data, and compute together yields
predictable gains in capability, with performance following a smooth curve. GPT-3
demonstrated that a sufficiently large decoder-only model can perform many tasks from a
prompt alone, an ability known as in-context learning, without any change to its weights.

Because the training and generation objectives align exactly, decoder-only models are
natural generators and form the basis of most modern chat assistants. Their main costs
are the quadratic attention over long contexts and the sequential nature of token-by-token
generation, which limits throughput and makes latency grow with output length. Techniques
such as key-value caching, quantization, and speculative decoding mitigate these costs,
but the fundamental tension between context length, latency, and quality remains central
to deploying these models in practice.
""",
"llm_pretraining.md": """# LLM Pretraining

Pretraining trains a language model on a very large text corpus using a self-supervised
objective, typically next-token prediction for decoder-only models or masked-token
prediction for encoder models. The crucial property is that no human labels are required:
the text itself provides the training signal, which is what makes pretraining scalable to
the size of the internet.

The pipeline begins with data collection and heavy filtering. Web text is deduplicated at
the document and near-duplicate level, filtered for quality and safety, and mixed across
domains according to a carefully chosen ratio. Data quality has proven at least as
important as raw quantity; a smaller, cleaner, better-balanced corpus can outperform a
larger, noisier one. The filtered text is tokenized into a flat stream of token ids, and
training consumes that stream over many passes with large batch sizes distributed across
many accelerators.

Scaling laws describe how loss falls predictably as parameters, data, and compute
increase together. Modern practice uses these laws to allocate a compute budget
optimally, often training smaller models on more data than early models did. The
resulting base model has absorbed broad linguistic structure and a great deal of world
knowledge, but it is not yet reliable at following instructions or answering questions
directly; it simply continues text in a plausible way.

Pretraining is extraordinarily expensive, so most practitioners start from an existing
checkpoint rather than train from scratch. Understanding pretraining clarifies where a
model's knowledge and biases come from, why the data mixture matters, and why the base
model must still be aligned through instruction tuning and preference learning before it
becomes a useful assistant.
""",
"instruction_tuning.md": """# Instruction Tuning

A pretrained language model is a text completer, not a helpful assistant. Ask it a
question and it might invent a plausible continuation of the question rather than answer
it. Instruction tuning closes this gap by fine-tuning the model on datasets of
instruction and response pairs, teaching it to interpret and follow requests.

The training data is typically a large, diverse collection of tasks phrased as natural
language instructions, spanning summarization, question answering, rewriting,
classification, and open-ended chat. By training on many tasks in a uniform
instruction-response format, the model learns to generalize to instructions it has never
seen, rather than memorizing a fixed set of commands. This generalization to unseen tasks
is the central benefit and is sometimes called instruction following.

The quality and diversity of instruction data matter more than sheer volume. A few
thousand carefully written examples, covering a wide range of tasks and formats, can
shift a base model's behavior substantially. Poorly curated data, with repetitive or
low-quality responses, teaches the model to produce repetitive or low-quality output, so
data curation is a first-class part of the process.

Instruction-tuned models follow formatting requests much more reliably, which is
practically important. When a system needs the model to emit JSON, or to answer in a
specific structure, instruction tuning makes that behavior dependable. This reliability
is why the router and grader in a retrieval-augmented generation pipeline can be built as
instruction-tuned prompts that request structured output.

Instruction tuning is usually the first of two alignment stages. It teaches the model
what kind of behavior is expected. The second stage, preference alignment, refines the
model to prefer better responses among plausible ones, improving helpfulness, honesty,
and safety. Together, these stages transform a raw base model into the chat models users
interact with, and they illustrate how the same underlying architecture can exhibit very
different behavior depending on the data it is tuned on.
""",
"rlhf.md": """# Reinforcement Learning from Human Feedback

Reinforcement learning from human feedback, or RLHF, aligns a language model's behavior
with human preferences. It addresses a fundamental problem: the qualities we want in a
response, such as helpfulness, honesty, and harmlessness, are hard to specify as a
differentiable loss, but humans can compare two responses and say which is better.

RLHF proceeds in three stages. First, supervised fine-tuning teaches the model to follow
instructions using demonstration data. Second, a reward model is trained on human
comparisons: given two responses to the same prompt, it learns to predict which one
humans prefer, turning pairwise preferences into a scalar score. Third, the language
model is optimized against the reward model using a reinforcement learning algorithm,
most classically proximal policy optimization, while a penalty on divergence from the
original model keeps it from drifting too far and gaming the reward.

The reward model is the heart of the method, and also its main vulnerability. Because the
policy is optimized to maximize the reward, it can learn to exploit weaknesses in the
reward model, producing outputs that score highly without being genuinely better. This
phenomenon, called reward hacking or over-optimization, is why the divergence penalty and
careful reward-model validation are essential.

RLHF is powerful but complex and notoriously unstable, sensitive to hyperparameters and
reward-model quality. Direct Preference Optimization simplifies the process by fitting
human preferences directly with a supervised objective, removing the separate reward
model and the reinforcement learning loop. This and related methods have become popular
for aligning modern models, but the underlying goal remains the same: converting the
non-differentiable notion of human preference into a signal that training can follow.
""",
"prompt_engineering.md": """# Prompt Engineering

Prompt engineering designs inputs that steer a language model toward desired outputs
without changing its weights. It is the fastest and least expensive way to improve
behavior, and it is often the first thing to try before considering fine-tuning or
architectural changes.

Clear, specific instructions are the foundation. Telling the model its role, the format
of the desired output, and any constraints focuses it on the task. Zero-shot prompting
asks directly; few-shot prompting includes a handful of worked examples in the prompt,
which strongly shapes style and format and is especially effective for classification and
structured extraction.

Reasoning can be elicited with chain-of-thought prompting, which asks the model to work
through a problem step by step before giving a final answer. This improves performance on
tasks that require multi-step logic, arithmetic, or planning, because the intermediate
steps provide the model with a scratchpad it can condition on. Equivalent strategies ask
the model to think first and answer last, or to produce a plan before executing it.

Prompt engineering is powerful but brittle. Small rewordings can shift results, behavior
varies across model versions, and a prompt tuned on one model may fail on another. For
production systems, prompts should be versioned and evaluated like code, and any
structured output the model produces should be validated rather than trusted blindly,
because the model can emit malformed or out-of-range values even when instructed
otherwise. Prompting is a complement to, not a replacement for, fine-tuning and
retrieval: it shapes behavior at inference time, while fine-tuning changes the model
itself and retrieval grounds it in external knowledge.
""",
}
