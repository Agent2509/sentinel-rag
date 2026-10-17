# AI Agents

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
A practical guideline is to start with the least agentic design that could work and add
autonomy only when a concrete failure demands it. A single retrieval call with a good prompt
is often sufficient, and adding a planning loop on top can introduce new failure modes
without improving results. When more structure is needed, a common path is to add one tool,
then a reflection step, then a planner, evaluating at each stage whether the added complexity
earns its cost. Frameworks make elaborate agents easy to assemble, which is precisely why
restraint is valuable: the ability to build a complicated system does not mean the task
requires one.
