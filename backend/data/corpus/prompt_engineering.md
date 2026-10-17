# Prompt Engineering

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
A productive habit is to treat prompts as artifacts under version control, with each change
evaluated against a fixed test set before adoption. This turns prompt development from
intuition and anecdote into evidence, and it catches regressions when a model is upgraded.
It also surfaces a subtle failure mode: a prompt tuned against a handful of examples may
exploit idiosyncrasies of those examples rather than genuinely improving the task. A
well-constructed evaluation set, with inputs the prompt author did not have in mind, is the
antidote. In this sense prompt engineering is not so different from model training, and the
same discipline of measurement applies.
