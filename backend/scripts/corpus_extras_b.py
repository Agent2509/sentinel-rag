"""Extra paragraphs appended to corpus part 3, 4, and 5 docs.

Same purpose as corpus_extras_a: push each doc past the 512-token fixed-chunk
boundary with a distinct, relevant continuation.
"""

EXTRA: dict[str, str] = {
"positional_encoding.md": """
A practical consequence of the choice is how a model behaves when asked to handle longer
sequences than it saw in training. Absolute learned embeddings degrade abruptly beyond their
trained length, which is why researchers developed interpolation and rescaling tricks to
stretch them. Relative schemes such as rotary and ALiBi degrade more gracefully and are
therefore preferred when long context matters. The broader lesson is that positional
encoding is not a minor detail: it determines the length at which a model remains
competent, and it interacts with how attention is computed. When building or fine-tuning a
model for long documents, this choice is one of the first to reconsider.
""",
"transfer_learning.md": """
A useful distinction is between feature extraction and fine-tuning, which sit at opposite
ends of a spectrum. In feature extraction, the pretrained model is frozen and only a new
head is trained, which is fast and safe when data is scarce. In full fine-tuning, the whole
model is updated, which is powerful but risks overfitting and catastrophic forgetting. Most
practice lies between the extremes, unfreezing only the later layers or using a
parameter-efficient method. The right point on this spectrum depends on the size and
similarity of the new dataset, and a common efficient strategy is to start frozen, then
gradually unfreeze and lower the learning rate as accuracy improves.
""",
"fine_tuning.md": """
A practical discipline is to establish a baseline before fine-tuning at all. Prompting a
strong general model with well-chosen examples often reaches most of the achievable quality
at a fraction of the cost, and it is the honest comparison that justifies the expense of
fine-tuning. Only when prompting plateaus should fine-tuning be considered, and even then
the first experiment should be a small, parameter-efficient adaptation rather than a full
run. Measuring against a fixed evaluation set, with the same metric used for prompting,
keeps the comparison fair and prevents the common trap of adopting an expensive pipeline
that does not actually outperform a simpler one.
""",
"tokenization.md": """
A subtle practical issue is that tokenization introduces a mismatch between what a language
model sees and what a human sees. Character-level tasks, string manipulation, and arithmetic
are all harder for a model because its units are subwords, and asking a model to count
letters in a word is notoriously unreliable for this reason. Code and structured data
tokenize in ways that reflect the tokenizer's training data, so a model may be surprisingly
good at some programming languages and poor at others. Recognizing these artifacts helps
explain failures that otherwise look like reasoning errors, when they are in fact
tokenization effects baked in before the model ever runs.
""",
"word_embeddings.md": """
A common pitfall in practice is applying the wrong notion of similarity to embeddings.
Cosine similarity and Euclidean distance agree on normalized vectors but diverge otherwise,
and dot-product models such as those trained with inner-product objectives may care about
magnitude as well as direction. Mixing embeddings from two different models, or from a
model used without its expected instruction prefix, silently produces poor results without
any error. Treating the embedding pipeline, the model, its prefix convention, its
normalization, and its distance metric, as a single unit that must be consistent end to end
is the discipline that separates retrieval that works from retrieval that mysteriously does
not.
""",
"gpt_architecture.md": """
One practical reality is that most deployed decoder-only models differ from one another
less in architecture than in data, scale, and alignment. The block structure is broadly
shared, so the interesting variation lies in how many parameters, trained on what mixture,
and tuned with which objective and preference data. This is why two models of similar size
can behave very differently: the architecture is the skeleton, but the behavior comes from
what it was trained and tuned on. For a system builder, this means model selection is
primarily a question of capability, cost, and licensing rather than architectural pedigree,
and swapping the model behind a well-designed interface should be straightforward.
""",
"llm_pretraining.md": """
An important and sometimes overlooked stage is curriculum and data ordering, which can
affect final quality even when the total data and compute are fixed. Mixing sources,
controlling repetition, and deciding when to introduce higher-quality data all shape what
the model learns. Evaluation during pretraining uses held-out perplexity as a proxy, but
perplexity does not always track downstream task quality, which is why periodic fine-grained
evaluations are run on task suites. The gap between the training signal, next-token
prediction, and the desired capabilities is the recurring theme of language model
development, and it is why pretraining alone is never the end of the story.
""",
"instruction_tuning.md": """
A practical method for building instruction data is self-instruct: use a strong model to
generate diverse instructions and candidate responses from a small seed set, then filter
them for quality before training. This bootstrapping lets a modest team assemble useful data
without exhaustive manual authoring. The risk is that the resulting dataset inherits the
quirks and errors of the generator, which is why filtering, deduplication, and human review
of a sample remain important. The broader principle is that instruction tuning is as much a
data curation problem as a modeling one, and the effort spent on collecting and cleaning
examples tends to pay off more than architectural tweaks.
""",
"rlhf.md": """
An alternative and increasingly common approach replaces the reinforcement learning stage
with a direct objective on preference pairs. Rather than training a separate reward model
and then optimizing a policy against it, methods such as direct preference optimization
reformulate the problem so that the language model itself can be trained on pairs of
preferred and dispreferred responses with a supervised-style loss. This removes an entire
component and much of the instability, while retaining most of the benefit. The trade-off is
less flexibility than a full reinforcement learning setup, but for alignment at typical
scales the simpler methods are often the pragmatic choice, and they illustrate a recurring
pattern in machine learning where a clever reformulation replaces a complicated system.
""",
"prompt_engineering.md": """
A productive habit is to treat prompts as artifacts under version control, with each change
evaluated against a fixed test set before adoption. This turns prompt development from
intuition and anecdote into evidence, and it catches regressions when a model is upgraded.
It also surfaces a subtle failure mode: a prompt tuned against a handful of examples may
exploit idiosyncrasies of those examples rather than genuinely improving the task. A
well-constructed evaluation set, with inputs the prompt author did not have in mind, is the
antidote. In this sense prompt engineering is not so different from model training, and the
same discipline of measurement applies.
""",
"context_window.md": """
A practical technique for long inputs is retrieval over the context itself, sometimes called
needle search, where the system first locates the relevant spans within a large document
before reasoning over them. This avoids relying on the model to attend perfectly across a
huge context and instead reduces the problem to a size the model handles reliably. Another
technique is recursive summarization, where long material is summarized in pieces and the
summaries are combined. Both reflect the same insight: the effective context is much
smaller than the advertised maximum for most tasks, and managing the budget actively beats
trusting that a large window will be used well.
""",
"quantization.md": """
A practical workflow is to treat the target hardware as the starting constraint and work
backward. If the model must run on a laptop with limited memory, moderate quantization may
be the only way to fit it at all, and a small quality loss is acceptable. If it runs on
ample server GPUs, quantization may be unnecessary and the full-precision model is
preferable. Measuring the actual quality impact on the specific task, rather than trusting
generic benchmarks, is essential because the degradation is task-dependent and can be
negligible on some workloads while material on others. Quantization is a tool to fit a
deployment, not a universal improvement.
""",
"lora_and_peft.md": """
A practical detail is where to place adapters and how to merge them. Targeting all
attention projections tends to work well and provides a robust default, while adapting the
feedforward layers can add capacity at higher parameter cost. After training, the low-rank
matrices can be merged into the base weights, producing an ordinary model with no inference
overhead, or kept separate to allow swapping multiple adapters. Merging is convenient for
deployment, while keeping adapters separate is convenient for serving many tasks from a
shared base. Choosing between these depends on whether flexibility or simplicity matters
more, a recurring decision in system design.
""",
"rag_overview.md": """
A useful way to reason about a RAG pipeline is to separate the recall problem from the
precision problem. Retrieval must first be capable of finding the right passage somewhere in
its candidate set, which argues for generous retrieval and multiple strategies such as
hybrid search. Then it must rank the best passage highly enough to reach the generator,
which argues for reranking and grading. Improving recall without improving precision fills
the context with noise, and improving precision without improving recall cannot recover a
passage that was never fetched. Diagnosing whether a bad answer is a recall failure or a
precision failure is the first and most useful step when a RAG system underperforms.
""",
"chunking_strategies.md": """
A practical point is that chunk boundaries interact with the structure of the source
material. Documents with clear headings and sections should be split along those boundaries,
because the natural unit of meaning is the section, not an arbitrary token count. Ignoring
structure often scatters a single idea across chunks or merges unrelated ideas into one.
Many systems enrich each chunk with metadata such as its document title, section heading,
and position, and prepend a short header to the embedded text so the vector reflects the
context the chunk belongs to. These small enrichments frequently improve retrieval more
than switching strategies, because they give the embedding model the context that the raw
chunk text alone lacks.
""",
"embedding_models.md": """
A practical evaluation should mirror the target workload rather than rely solely on public
benchmarks. Build a small set of representative queries with known relevant passages,
measure retrieval quality directly, and compare candidate embedding models on that set. This
catches domain mismatch that benchmarks miss. It is also worth measuring latency and memory,
since a heavier model may offer only a marginal quality gain that does not justify its cost.
The decision is a balance among quality, speed, storage, and license, and the only way to
choose well is to measure on data that resembles what the system will actually see in
production, not on a leaderboard that may emphasize very different tasks.
""",
"vector_databases.md": """
A practical warning is that a vector database is not automatically the right answer to a
retrieval problem. For collections with thousands rather than millions of vectors, an
in-memory index is simpler, has no operational overhead, and is exact. Introducing an
external service adds a network hop, a schema to maintain, a consistency model to reason
about, and one more thing that can fail during a demonstration. The decision to adopt a
database should be driven by scale, filtering requirements, concurrency, and durability
needs that actually exist, not by the assumption that production requires one. Measuring the
straightforward solution first often reveals that it is sufficient, and adopting complexity
only when it is justified keeps the system maintainable.
""",
"hybrid_search.md": """
A practical refinement is to weight the two retrieval branches or vary how many candidates
each contributes. If a workload is heavily keyword-oriented, more weight on the lexical side
helps; if it is conversational and paraphrase-heavy, more weight on vectors helps.
Reciprocal rank fusion handles fusion elegantly but is not the only option, and some systems
combine normalized scores or use a learned fusion. The simplest robust default, however,
remains RRF over a generous candidate set from both branches, followed by a reranker. This
layering, cheap retrieval for recall and expensive reranking for precision, is a pattern
that recurs throughout information retrieval and explains much of why hybrid systems
outperform any single method.
""",
"reranking.md": """
A practical consideration is the cost and latency budget. A cross-encoder reranker adds a
forward pass per candidate, so the number of candidates directly affects latency. Tuning
that number is a trade-off between the chance of including the right passage and the time
spent reranking. A common approach is to retrieve a generous set, rerank, and keep the top
few, adjusting the candidate count based on measured latency. Caching reranker scores for
repeated queries helps under load. Because reranking often yields the largest quality gain
for the least architectural change, it is frequently the first optimization to add once a
basic retrieval pipeline is working, before more elaborate changes.
""",
"hyde.md": """
A practical variant is to generate several hypothetical documents and average their
embeddings, which smooths over the idiosyncrasies of any single generation and tends to be
more stable than relying on one. Another is to combine HyDE with the original query by
retrieving with both and merging the results, so a poor hypothetical document cannot
single-handedly derail retrieval. The general principle is that HyDE is one signal among
several, and it should be combined rather than substituted. Treating it as a contributor to
a fusion, alongside the raw query and lexical search, gets the benefit of bridging the
vocabulary gap without the full risk of a hallucinated passage dominating the results.
""",
"rag_evaluation.md": """
A practical pattern is to evaluate at the component level before the system level. Run
retrieval-only metrics such as context precision and recall to establish an upper bound on
what generation can achieve, because generation cannot be better than the context it
receives. If retrieval is the bottleneck, no amount of prompt tuning on the generator will
fix it. Only once retrieval is adequate does it make sense to evaluate and improve
generation. This decomposition turns a vague complaint that the system gives bad answers
into a specific, testable claim about which stage is failing, and it directs effort where it
will actually change the outcome rather than where it is most visible.
""",
"ai_agents.md": """
A practical guideline is to start with the least agentic design that could work and add
autonomy only when a concrete failure demands it. A single retrieval call with a good prompt
is often sufficient, and adding a planning loop on top can introduce new failure modes
without improving results. When more structure is needed, a common path is to add one tool,
then a reflection step, then a planner, evaluating at each stage whether the added complexity
earns its cost. Frameworks make elaborate agents easy to assemble, which is precisely why
restraint is valuable: the ability to build a complicated system does not mean the task
requires one.
""",
"tool_use.md": """
A practical detail is how the model's proposed calls are surfaced in the response. Most
providers return structured output indicating the requested tool and arguments, which the
application parses and dispatches, then feeds the result back as a new message. Handling the
case where the model requests a nonexistent tool, passes invalid arguments, or calls a tool
that fails is essential; each should produce a clear error observation so the model can
correct course rather than crashing the loop. Logging every call, its arguments, and its
result also builds an audit trail, which matters when tools have side effects and a
mistaken call can change real state.
""",
"react_pattern.md": """
A practical pitfall is prompt leakage of tool syntax. Because the model must emit
machine-parseable action strings, the prompt and parser must agree exactly on the format,
and any drift causes silent failures where the model produces text the parser cannot read.
Robust implementations use structured function calling rather than free-text action strings
precisely to avoid this fragility. Another pitfall is observation overflow: a tool may return
more text than the context can hold, so results should be truncated or summarized before
being fed back. These engineering details, not the reasoning concept itself, are usually
what separates a ReAct prototype that works on examples from one that holds up in use.
""",
"multi_agent_systems.md": """
A practical pattern that works well is the reviewer or critic arrangement, where one agent
produces an answer and a second, independent agent evaluates it against criteria and returns
either approval or specific criticism that drives a revision. This is valuable because an
independent evaluation catches errors that the producing agent, committed to its own
output, tends to miss. Crucially, the critic must be genuinely independent, with a distinct
prompt and stance, or it simply echoes the first agent. When used this way, multi-agent
designs add real value by introducing a check rather than merely splitting work, which is
the difference between a useful committee and an expensive one.
""",
"memory_systems.md": """
A practical design decision is whether memory is written explicitly or inferred. Explicit
memory stores what the application chooses to save, such as the user's stated preferences,
and is predictable and controllable. Inferred memory has the system decide what is worth
saving, often by summarizing at the end of a session, which is more automatic but can store
incorrect or irrelevant content. Many production systems combine both, with explicit memory
for facts the user wants retained and automatic summarization for conversational context.
Whichever is chosen, memory should be inspectable and editable, both to build user trust and
to correct the inevitable cases where the system remembers something it should not.
""",
"mlops_overview.md": """
A practical way to adopt MLOps without over-investing is to add one practice at a time,
starting with version control for data and configuration, since almost every other practice
depends on being able to reproduce a result. Next, add automated evaluation against a fixed
test set, so that improvements and regressions are measured rather than assumed. Then add
monitoring once the model is deployed, to detect when the world moves away from the training
data. Each step is independently valuable and does not require a platform. Building the full
stack before there is a working model is a common and expensive mistake; the discipline pays
off most when it is layered onto something that already functions.
""",
"model_serving.md": """
A practical decision is synchronous versus asynchronous processing. A synchronous endpoint
holds the connection open until the response is complete, which is simple but ties up
resources and offers no feedback during long generations. Asynchronous or streaming designs
return partial results and free the connection to serve other work, which is essential for
generative models. For a RAG pipeline, streaming the trace as each step completes is
particularly valuable, because it turns an opaque wait into a visible process and lets the
user see exactly where time is spent. Serving is therefore not only about raw throughput but
also about the experience of waiting, which good interfaces make legible.
""",
"monitoring_and_drift.md": """
A practical foundation for all monitoring is structured logging of complete requests. For a
RAG system, that means recording the query, the retrieved passages with their scores, any
grading decisions, the rewritten query if the correction loop fired, and the final answer
along with its citations. Without this record, diagnosing a complaint reduces to
speculation. With it, you can replay the exact decision path and identify whether retrieval,
grading, or generation went wrong. This log is also the raw material for building evaluation
sets from real traffic, closing the loop between production failures and the next round of
development, which is the essence of operating a system rather than merely deploying one.
""",
"cicd_for_ml.md": """
A practical starting point for a small project is a single automated job that regenerates
the corpus, rebuilds the indexes, runs a fixed set of test queries, and asserts that the
expected documents appear in the top results. This smoke test catches the most common
breakages, such as a chunking change that silently drops content or a model swap that
degrades retrieval, without requiring a full evaluation harness. It also establishes the
habit of treating the pipeline, not just the code, as something under test. From there,
evaluation gates on a labeled set can be added as the project matures, but even the modest
version delivers most of the value by preventing broken builds from being merged.
""",
}
