# Fine-Tuning

Fine-tuning continues training a pretrained model on a narrower dataset so that it
specializes for a target task or domain. Where transfer learning may freeze most of the
model, fine-tuning updates its weights, adjusting both the internal representations and
the output behavior to fit the new data.

The procedure is straightforward: load the pretrained weights, train on the new dataset
with a small learning rate to avoid destroying the pretrained knowledge, and monitor a
validation split to prevent overfitting. The learning rate is critical, because too
large a step can catastrophically forget the general capabilities learned during
pretraining, while too small a step wastes the adaptation.

Full fine-tuning updates every parameter and generally yields the best quality, but it
requires substantial memory and compute, since optimizer states roughly triple the
parameter footprint. Parameter-efficient methods such as LoRA, adapters, and prefix
tuning freeze the base model and train only a small number of additional parameters,
cutting cost dramatically with modest quality loss. These methods have made fine-tuning
accessible on a single GPU and are now the default for many applications.

Different goals call for different flavors of fine-tuning. Supervised fine-tuning on
instruction and response pairs teaches a base model to follow prompts and adopt an
assistant persona. Preference-based methods such as reinforcement learning from human
feedback further align outputs with human judgment, improving helpfulness and safety.
The recurring risks are catastrophic forgetting and overfitting on small datasets, and
the standard mitigations are mixing in general-purpose data, early stopping, and careful
evaluation on held-out tasks before deployment.
A practical discipline is to establish a baseline before fine-tuning at all. Prompting a
strong general model with well-chosen examples often reaches most of the achievable quality
at a fraction of the cost, and it is the honest comparison that justifies the expense of
fine-tuning. Only when prompting plateaus should fine-tuning be considered, and even then
the first experiment should be a small, parameter-efficient adaptation rather than a full
run. Measuring against a fixed evaluation set, with the same metric used for prompting,
keeps the comparison fair and prevents the common trap of adopting an expensive pipeline
that does not actually outperform a simpler one.
