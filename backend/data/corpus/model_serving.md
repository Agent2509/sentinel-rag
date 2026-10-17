# Model Serving

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
A practical decision is synchronous versus asynchronous processing. A synchronous endpoint
holds the connection open until the response is complete, which is simple but ties up
resources and offers no feedback during long generations. Asynchronous or streaming designs
return partial results and free the connection to serve other work, which is essential for
generative models. For a RAG pipeline, streaming the trace as each step completes is
particularly valuable, because it turns an opaque wait into a visible process and lets the
user see exactly where time is spent. Serving is therefore not only about raw throughput but
also about the experience of waiting, which good interfaces make legible.
