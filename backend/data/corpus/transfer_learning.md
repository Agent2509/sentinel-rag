# Transfer Learning

Transfer learning reuses knowledge from a model trained on one task to improve
performance on another. Instead of learning from scratch, you begin with pretrained
weights and adapt them to the new problem. This is essential whenever labeled data is
scarce, which is the common case in practice.

The intuition is that a model trained on a large, broad dataset has learned general
features that transfer to related tasks. In vision, early layers of a convolutional
network detect edges and textures that are useful for almost any image task. In
language, a pretrained transformer has absorbed grammar, world knowledge, and reasoning
patterns. Reusing these features means the new task needs far less data and compute.

The typical recipe is to freeze the early layers, which capture general features, and
fine-tune the later, more task-specific layers. How much to fine-tune depends on how
similar the new task is and how much data it has: with a lot of data and a very
different domain, updating more of the model helps; with little data, freezing more and
training only a small head avoids overfitting. Alternatively, the pretrained model can
serve purely as a frozen feature extractor, with a lightweight classifier on top.

Transfer learning underlies modern natural language processing, where a single
pretrained model is adapted to classification, question answering, summarization, and
generation. The embedding models used in retrieval are also produced this way: a general
sentence encoder is fine-tuned with contrastive objectives so that semantically similar
texts land close together. Transfer learning is arguably the most important practical
development in modern machine learning, because it turns the enormous cost of pretraining
into a one-time investment shared across countless downstream applications.
A useful distinction is between feature extraction and fine-tuning, which sit at opposite
ends of a spectrum. In feature extraction, the pretrained model is frozen and only a new
head is trained, which is fast and safe when data is scarce. In full fine-tuning, the whole
model is updated, which is powerful but risks overfitting and catastrophic forgetting. Most
practice lies between the extremes, unfreezing only the later layers or using a
parameter-efficient method. The right point on this spectrum depends on the size and
similarity of the new dataset, and a common efficient strategy is to start frozen, then
gradually unfreeze and lower the learning rate as accuracy improves.
