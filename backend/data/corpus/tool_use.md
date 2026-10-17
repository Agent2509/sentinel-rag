# Tool Use and Function Calling

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
A practical detail is how the model's proposed calls are surfaced in the response. Most
providers return structured output indicating the requested tool and arguments, which the
application parses and dispatches, then feeds the result back as a new message. Handling the
case where the model requests a nonexistent tool, passes invalid arguments, or calls a tool
that fails is essential; each should produce a clear error observation so the model can
correct course rather than crashing the loop. Logging every call, its arguments, and its
result also builds an audit trail, which matters when tools have side effects and a
mistaken call can change real state.
