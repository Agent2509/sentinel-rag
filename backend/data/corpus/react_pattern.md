# The ReAct Pattern

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
A practical pitfall is prompt leakage of tool syntax. Because the model must emit
machine-parseable action strings, the prompt and parser must agree exactly on the format,
and any drift causes silent failures where the model produces text the parser cannot read.
Robust implementations use structured function calling rather than free-text action strings
precisely to avoid this fragility. Another pitfall is observation overflow: a tool may return
more text than the context can hold, so results should be truncated or summarized before
being fed back. These engineering details, not the reasoning concept itself, are usually
what separates a ReAct prototype that works on examples from one that holds up in use.
