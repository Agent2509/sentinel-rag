"""Corpus part 5: RAG evaluation, agents, and production concerns."""

DOCS: dict[str, str] = {
"rag_evaluation.md": """# Evaluating RAG Systems

Evaluating a retrieval-augmented generation system is harder than evaluating a
classifier, because the pipeline has two stages and either can fail. A wrong answer might
come from retrieving the wrong passage or from generating badly despite good retrieval.
Good evaluation measures both and attributes failures to the right stage.

RAGAS is a widely used framework for this, providing reference-free and reference-based
metrics. Faithfulness checks whether every claim in the answer is supported by the
retrieved context, catching hallucination and grounding failures. Answer relevancy
measures how well the answer addresses the question, independent of correctness. Context
precision asks whether the retrieved passages are actually relevant to the question and
are ranked with the most useful ones first. Context recall asks whether all the
information needed to produce the reference answer was present in the retrieved context.

The distinction between reference-free and reference-based metrics matters operationally.
Faithfulness and answer relevancy can be computed without ground truth, which is useful
for monitoring live traffic. Context precision and context recall require reference
answers and, crucially, reference contexts: the specific passages that should have been
retrieved. Building a test set therefore means generating not just question-answer pairs
but also the supporting contexts, which a language model can do from the source documents.
Omitting the reference contexts makes context precision and recall impossible to compute.

Because these metrics are computed by a language model acting as a judge, the judge model
and its prompt should be fixed and versioned. Changing the judge changes the scores, even
for identical answers, which destroys comparability. A sound evaluation also runs the
pipeline in each configuration of interest, such as each chunking strategy with
self-correction on and off, and reports metrics alongside latency. Comparing the resulting
grid turns abstract metrics into actionable decisions: which strategy to ship, whether the
correction loop earns its added cost, and where the next improvement should be focused.
""",
"ai_agents.md": """# AI Agents

An AI agent is a language model that pursues a goal over multiple steps, choosing actions
and observing their results. Where a single prompt-response call produces one output, an
agent runs a loop: reason about the current state, select a tool or action, execute it,
observe the result, and decide what to do next. The loop continues until the goal is met
or a stopping condition is reached.

Agents extend language models along three axes. Tools let the model act on the world, for
example by searching the web, running code, querying a database, or calling an API.
Memory stores relevant information across steps, so the agent does not lose earlier
context as the interaction grows. Planning decomposes a goal into subtasks, sets an order,
and tracks progress, which is what allows an agent to handle problems that no single
generation could produce.

The central challenges are reliability and cost. Because the agent runs many model calls,
small errors compound: a wrong decision early in the trajectory can send the whole run
off course, and the model may loop, repeat itself, or spend unbounded compute chasing a
dead end. Robust agents therefore need careful stopping conditions, step limits, and
error recovery, treating the language model as an unreliable component rather than an
oracle. Techniques such as interleaving reasoning with acting, and having the agent
reflect on and critique its own output, improve robustness at the cost of more calls.

Retrieval is often one of an agent's most useful tools, which makes the agentic and
retrieval-augmented paradigms complementary. An agent can decide when to search, what to
search for, and whether the retrieved information is sufficient, all of which a static
retrieval pipeline cannot. The trade-off is that agentic control adds latency and can
fail in more ways, so it should be justified by tasks that genuinely require multiple
steps rather than applied by default.
""",
"tool_use.md": """# Tool Use and Function Calling

Tool use lets a language model call external functions to retrieve information or perform
actions that it cannot accomplish from its weights alone, such as precise arithmetic,
accessing current data, or causing a side effect like writing a file or sending a
message. It is the bridge between a model that only produces text and a system that can
affect the world.

The common pattern is function calling. The developer declares a set of tools, each with
a name, a description, and a JSON schema describing its parameters. Given a user request,
the model can choose to emit a structured call specifying which tool to invoke and with
what arguments. The surrounding application, not the model, executes the tool, because the
model has no ability to run code itself; it only proposes calls. The result is returned to
the model, which then continues reasoning with the new information or produces a final
answer.

Reliability depends heavily on clear, specific tool descriptions and strict schemas. A
vague description invites the model to call the wrong tool or pass malformed arguments,
and the application must always validate arguments before executing them, because the
model can produce input that is syntactically plausible but semantically wrong or unsafe.
Errors and unexpected results should be returned to the model as observations so it can
adapt, rather than crashing the loop.

Tool use underlies agents and is how capabilities such as retrieval, web search, and code
execution are integrated into a language model's workflow. It also introduces important
boundaries: because tools can have real effects, they should be scoped to the minimum
necessary permissions, executed in isolation where possible, and monitored, treating the
model's proposed calls as untrusted input that must be checked.
""",
"react_pattern.md": """# The ReAct Pattern

ReAct interleaves reasoning and acting in a single loop. At each step the model produces a
thought, takes an action, receives an observation from the environment, and uses that
observation to inform the next thought. This alternation continues until the model
decides it has enough information to answer, or a step limit is reached.

The structure makes the model's process inspectable and grounds it in real tool output. A
typical trace begins with a thought such as identifying what information is needed, then
an action such as issuing a search query, then an observation containing the search
results, then another thought that interprets the results and decides whether more
information is required. Because each step is explicit, failures are far easier to
diagnose than in a single opaque generation, and the reasoning can be audited.

ReAct improves performance on tasks that require external knowledge or multiple
dependent steps, because it lets the model gather evidence and adjust course rather than
committing to an answer immediately. The cost is more model calls and more tokens, since
every step re-processes the growing trajectory, and a poorly bounded loop can run away.
Robust implementations cap the number of steps, validate every tool call, and handle tool
errors as observations that the model can react to.

The pattern underlies many agent frameworks and generalizes the idea of iterative
self-correction. In a retrieval-augmented generation system, the same principle appears at
a smaller scale: retrieve passages, assess whether they are relevant enough to answer,
and if not, rewrite the query and retrieve again. ReAct formalizes this observe, reason,
act cycle, and understanding it clarifies why systems that can check their own work
outperform those that answer in a single pass.
""",
"multi_agent_systems.md": """# Multi-Agent Systems

Multi-agent systems decompose a complex task across several language-model agents that
specialize and coordinate. Each agent has a role, such as a planner that breaks a goal
into steps, a researcher that gathers information, a coder that implements, or a critic
that reviews, and they exchange messages or shared artifacts to accomplish the overall
goal.

Common topologies include a supervisor that routes subtasks to specialized workers, a
debate or ensemble setting where agents argue and converge on an answer, and a pipeline
where each agent's output becomes the next agent's input. Specialization lets each agent
use a tailored prompt and a focused set of tools, and running independent agents in
parallel can reduce wall-clock time.

The appeal is modularity and the ability to attack problems too large or too varied for a
single prompt and a single context window. Splitting responsibilities makes each
component simpler to reason about and easier to improve in isolation, much like
decomposing a monolith into services.

The costs, however, are substantial. Communication between agents adds overhead and
encoding work into messages loses information. Errors compound across hand-offs, with one
agent's mistake becoming the next agent's bad input. Coordination logic grows complex and
can itself become a source of bugs. In practice, multi-agent systems are frequently
over-applied: a single well-prompted model equipped with tools solves many problems more
cheaply and reliably than a committee of agents. The decision to split into multiple
agents should be driven by a clear separation of concerns, distinct tools or permissions,
or genuine parallelism, not by the novelty of the architecture. When those conditions
hold, multi-agent designs can be powerful; when they do not, they add complexity without
proportional benefit.
""",
"memory_systems.md": """# Memory in LLM Systems

Memory lets a language-model system retain information beyond a single context window.
Without an explicit memory mechanism, every interaction starts fresh, long tasks lose
earlier details as the context fills, and the system cannot learn from past sessions.

Short-term memory is the working context: recent turns of a conversation, retrieved
documents, and intermediate results. It is limited by the context window, so systems
manage it by summarizing older content, dropping low-value turns, or retrieving only the
most relevant history when it is needed rather than keeping everything resident.

Long-term memory persists across sessions, usually in an external store such as a vector
database or a key-value store, and is fetched when relevant. Because it lives outside the
model, it can grow without bound, but it must be written to and read from deliberately.
The types of memory mirror human cognition. Episodic memory records specific events and
interactions. Semantic memory holds facts and knowledge. Procedural memory captures how
to perform tasks, which may be encoded as tools, prompts, or learned policies.

Many systems implement memory as embeddings, storing each memory as a vector and
retrieving by similarity, which is the same mechanism as retrieval-augmented generation.
This makes memory and retrieval close relatives: both ground a model in stored information
selected at query time. The hard problems are deciding what to remember, since indiscriminate
storage produces noise, and deciding what to forget, since stale or incorrect memories can
mislead the model. Retrieval-augmented generation can be viewed as external semantic
memory, and a well-designed memory system is essentially a retrieval system tuned for
personal and temporal context.
""",
"mlops_overview.md": """# MLOps Overview

MLOps applies software engineering and operations discipline to machine learning so that
models can be built, deployed, and maintained reliably over time. It spans data
management, training pipelines, deployment, monitoring, and governance, and it exists
because a model that performs well in a notebook is far from a system that performs well
in production.

A typical lifecycle includes collecting and validating data, experimenting with features
and architectures, training, evaluating against clear criteria, packaging the model with
its dependencies and configuration, deploying it behind an interface, and monitoring it in
production. Crucially, the lifecycle is a loop: monitoring detects when performance
degrades, which triggers investigation and retraining, often automated as continuous
training. Without this feedback loop, a deployed model silently decays as the world
changes around it.

MLOps differs from traditional DevOps because the artifact is a statistical model whose
behavior depends on data. That dependence introduces concerns that ordinary software does
not have. Data must be versioned, because the same code on different data yields different
models. Experiments must be tracked, because reproducing a result requires knowing the
exact data, code, and hyperparameters. Models must be evaluated on held-out data, and
their behavior can change without any code change at all, simply because the input
distribution shifted.

The tooling landscape is broad, from experiment trackers and feature stores to model
registries and serving platforms. But the principles matter more than the tools, and they
scale down as well as up. Even a small project benefits from versioned configuration
files, pinned dependencies, a reproducible ingestion step, recorded evaluation results,
and automated checks that the pipeline still works. Adopting these habits early makes the
difference between a demo that happened to work once and a system that can be trusted and
maintained.
""",
"model_serving.md": """# Model Serving

Model serving exposes a trained model to applications through an interface, usually an
API. The main concerns are latency, throughput, cost, and reliability, and the right
design depends on how the model is used.

Several patterns cover most needs. Real-time endpoints answer individual requests with
low latency and are the default for interactive applications. Batch jobs process large
volumes of inputs offline, where throughput matters more than per-request latency.
Streaming endpoints return output incrementally as it is produced, which is especially
important for large language models: streaming does not reduce total generation time, but
it dramatically improves perceived latency, because users see the answer begin to appear
immediately instead of waiting for the full response.

Serving stacks range from simple frameworks such as FastAPI and Uvicorn, which are
sufficient for many applications, to dedicated systems such as TorchScript, ONNX Runtime,
Triton, and vLLM for high-throughput inference. For generative models, techniques such as
dynamic batching, which groups concurrent requests into a single forward pass, and
key-value caching, which avoids recomputing the attention state of already-generated
tokens, raise throughput substantially. Caching entire responses to frequent or identical
requests reduces cost further.

Reliability practices from ordinary software apply directly. Health checks let
orchestrators know when a service is ready and when it is failing. Graceful shutdown lets
in-flight requests finish. Resource limits prevent one workload from starving others, and
timeouts and retries handle transient failures. For a local retrieval-augmented generation
project, a single FastAPI process with server-sent events for streaming is entirely
adequate and keeps the operational surface small, which is itself a virtue: every
additional moving part is something else that can break during a demonstration.
""",
"monitoring_and_drift.md": """# Monitoring and Data Drift

After a model is deployed, its performance can degrade silently as the world changes.
Monitoring detects this degradation and triggers corrective action before users notice,
which is why it is one of the most important and most neglected parts of a production
machine learning system.

Data drift is a change in the distribution of inputs. Users begin asking about new topics,
a domain introduces new vocabulary, or upstream data pipelines shift in subtle ways.
Concept drift is a change in the relationship between inputs and the correct output, so
that even familiar inputs now require different answers. Both can hurt accuracy even when
the model's code and weights are unchanged, which makes them easy to miss.

Because ground-truth labels often arrive late or not at all, monitoring relies heavily on
proxies. Teams track the distribution of predictions, model confidence, input statistics,
and business metrics, comparing them against the training distribution using statistics
such as the population stability index or Kullback-Leibler divergence. When a metric
crosses a threshold, an alert fires, prompting investigation or an automatic retraining
job. A common failure mode is alert fatigue, where too many noisy alerts train the team to
ignore them, so thresholds must be chosen with care.

Retrieval-augmented generation adds its own monitoring concerns. A stale corpus degrades
answers even when the language model is perfectly healthy, so monitoring must include
retrieval quality, such as the relevance of retrieved passages, and answer faithfulness,
such as whether the generated text is supported by the retrieved context. Logging complete
traces, with the query, the retrieved chunks, the grades, and the final answer, is what
makes it possible to diagnose a bad response after the fact and to build the datasets that
drive the next round of improvement.
""",
"cicd_for_ml.md": """# CI/CD for Machine Learning

Continuous integration and continuous delivery automate the path from a code change to a
deployed model. In machine learning, the pipeline must validate not only code but also
data and model behavior, because a change that passes every unit test can still produce a
worse model.

Continuous integration runs automated checks on every change. These include unit tests
for components, schema and distribution checks for data, and evaluation gates that
compare model metrics against a baseline. An evaluation gate is the key ML-specific idea:
a new model that regresses on the held-out set fails the build, so it never reaches users.
This turns evaluation from a manual, after-the-fact step into an automated guardrail.

Continuous delivery packages models with their dependencies and configuration, versions
them in a registry, and promotes them through staging to production along a controlled
path. Because the artifact includes trained weights, which are large and not human-
readable, the registry and its metadata are essential for knowing what is deployed and how
to roll back.

Reproducibility is the foundation that makes all of this work. Pinned dependencies,
versioned data and configuration, fixed random seeds, and recorded evaluation results let
anyone recreate a model exactly, which is necessary for debugging, auditing, and
comparison. Even a small project benefits from a continuous integration job that runs the
ingestion step and a smoke test, ensuring the indexes build and a sample query returns
sane results before changes are merged. Catching a broken pipeline in review is far
cheaper than discovering it during a live demonstration.
""",
}
