# GPT Architecture

GPT models are decoder-only transformers trained to predict the next token in a
sequence. They apply causal masking so that each position can attend only to itself and
earlier positions, which prevents the model from seeing the future. This makes generation
autoregressive: the model produces one token at a time and appends each new token to the
context before predicting the next.

The architecture stacks decoder blocks, each containing masked self-attention followed by
a feedforward network, with residual connections and layer normalization. The causal mask
is what enforces the left-to-right generation order. At inference, a key-value cache
stores the attention keys and values from previous steps so that generating each new
token does not require recomputing the entire prefix, which is essential for making
generation tractable.

The model is trained with a simple objective, predicting the next token across a huge
corpus. Scaling laws show that increasing parameters, data, and compute together yields
predictable gains in capability, with performance following a smooth curve. GPT-3
demonstrated that a sufficiently large decoder-only model can perform many tasks from a
prompt alone, an ability known as in-context learning, without any change to its weights.

Because the training and generation objectives align exactly, decoder-only models are
natural generators and form the basis of most modern chat assistants. Their main costs
are the quadratic attention over long contexts and the sequential nature of token-by-token
generation, which limits throughput and makes latency grow with output length. Techniques
such as key-value caching, quantization, and speculative decoding mitigate these costs,
but the fundamental tension between context length, latency, and quality remains central
to deploying these models in practice.
One practical reality is that most deployed decoder-only models differ from one another
less in architecture than in data, scale, and alignment. The block structure is broadly
shared, so the interesting variation lies in how many parameters, trained on what mixture,
and tuned with which objective and preference data. This is why two models of similar size
can behave very differently: the architecture is the skeleton, but the behavior comes from
what it was trained and tuned on. For a system builder, this means model selection is
primarily a question of capability, cost, and licensing rather than architectural pedigree,
and swapping the model behind a well-designed interface should be straightforward.
