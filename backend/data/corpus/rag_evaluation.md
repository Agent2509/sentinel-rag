# Evaluating RAG Systems

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
A practical pattern is to evaluate at the component level before the system level. Run
retrieval-only metrics such as context precision and recall to establish an upper bound on
what generation can achieve, because generation cannot be better than the context it
receives. If retrieval is the bottleneck, no amount of prompt tuning on the generator will
fix it. Only once retrieval is adequate does it make sense to evaluate and improve
generation. This decomposition turns a vague complaint that the system gives bad answers
into a specific, testable claim about which stage is failing, and it directs effort where it
will actually change the outcome rather than where it is most visible.
