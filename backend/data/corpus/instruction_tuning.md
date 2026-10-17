# Instruction Tuning

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
A practical method for building instruction data is self-instruct: use a strong model to
generate diverse instructions and candidate responses from a small seed set, then filter
them for quality before training. This bootstrapping lets a modest team assemble useful data
without exhaustive manual authoring. The risk is that the resulting dataset inherits the
quirks and errors of the generator, which is why filtering, deduplication, and human review
of a sample remain important. The broader principle is that instruction tuning is as much a
data curation problem as a modeling one, and the effort spent on collecting and cleaning
examples tends to pay off more than architectural tweaks.
