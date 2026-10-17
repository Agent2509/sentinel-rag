# LoRA and Parameter-Efficient Fine-Tuning

LoRA, which stands for low-rank adaptation, is a parameter-efficient fine-tuning method
that dramatically reduces the cost of adapting a large model. Instead of updating the
full weight matrices of the pretrained model, LoRA freezes those weights and injects
small trainable low-rank matrices alongside selected layers. The effective weight at
those layers becomes the frozen original plus the product of two much smaller matrices.

The insight is that the update needed to adapt a model to a new task tends to be
low-rank, so it can be represented compactly. This reduces the number of trainable
parameters by orders of magnitude, which in turn slashes optimizer memory, the dominant
cost of full fine-tuning. The original weights stay untouched, so LoRA also avoids
catastrophic forgetting of general knowledge, and because the adaptation is stored as
tiny separate matrices, multiple adapters can be trained for different tasks and swapped
over a single base model at inference time.

The main hyperparameters are the rank of the low-rank matrices, which controls capacity,
and the choice of which modules to adapt, typically the attention projection matrices.
Higher rank means more expressive updates and more parameters. LoRA is one member of a
broader family of parameter-efficient fine-tuning methods, alongside adapters, prefix
tuning, and prompt tuning, which inject trainable parameters in different places.

These techniques have made fine-tuning accessible on a single GPU and are widely used to
specialize models for a domain, a writing style, or reliable structured output while
retaining general capability. They are not a complete replacement for full fine-tuning
when the task diverges greatly from the pretraining distribution, but for most adaptation
needs they offer an excellent trade-off between cost and quality.
A practical detail is where to place adapters and how to merge them. Targeting all
attention projections tends to work well and provides a robust default, while adapting the
feedforward layers can add capacity at higher parameter cost. After training, the low-rank
matrices can be merged into the base weights, producing an ordinary model with no inference
overhead, or kept separate to allow swapping multiple adapters. Merging is convenient for
deployment, while keeping adapters separate is convenient for serving many tasks from a
shared base. Choosing between these depends on whether flexibility or simplicity matters
more, a recurring decision in system design.
