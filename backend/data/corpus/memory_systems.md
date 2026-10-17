# Memory in LLM Systems

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
A practical design decision is whether memory is written explicitly or inferred. Explicit
memory stores what the application chooses to save, such as the user's stated preferences,
and is predictable and controllable. Inferred memory has the system decide what is worth
saving, often by summarizing at the end of a session, which is more automatic but can store
incorrect or irrelevant content. Many production systems combine both, with explicit memory
for facts the user wants retained and automatic summarization for conversational context.
Whichever is chosen, memory should be inspectable and editable, both to build user trust and
to correct the inevitable cases where the system remembers something it should not.
