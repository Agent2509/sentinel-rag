# Multi-Agent Systems

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
A practical pattern that works well is the reviewer or critic arrangement, where one agent
produces an answer and a second, independent agent evaluates it against criteria and returns
either approval or specific criticism that drives a revision. This is valuable because an
independent evaluation catches errors that the producing agent, committed to its own
output, tends to miss. Crucially, the critic must be genuinely independent, with a distinct
prompt and stance, or it simply echoes the first agent. When used this way, multi-agent
designs add real value by introducing a check rather than merely splitting work, which is
the difference between a useful committee and an expensive one.
