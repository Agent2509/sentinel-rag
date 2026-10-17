# Quantization

Quantization reduces the numerical precision of a model's weights and activations,
typically from sixteen-bit or thirty-two-bit floating point down to eight-bit or even
four-bit integers. The goal is to shrink memory use and speed up inference while
accepting a modest loss in quality.

The idea rests on the observation that neural network weights do not need full floating
point precision to be useful. By mapping a range of values onto a small set of integers
with a per-tensor or per-channel scale and zero point, a model can be stored and computed
with far less memory. A seven-billion-parameter model that occupies about fourteen
gigabytes at sixteen-bit precision can fit in under four gigabytes when quantized to four
bits, which brings it within reach of consumer hardware and enables local deployment.

There are two main approaches. Post-training quantization converts an already-trained
model, using a small calibration dataset to choose good scaling factors and to measure
the error introduced. Quantization-aware training simulates low precision during
training so that the model adapts its weights to be robust under quantization, usually
yielding better quality at aggressive bit widths. Several schemes have become standard
for large language models, including GPTQ and AWQ for weight quantization and the NF4
format used by bitsandbytes for efficient four-bit loading.

The accuracy penalty is small at eight bits and grows more noticeable at four bits,
especially on tasks requiring precise reasoning or arithmetic, and it can vary
significantly across architectures. Quantization is therefore a central tool for running
models cheaply, including the embedding and generation models used in local
retrieval-augmented generation pipelines, where GPU memory is often the binding
constraint.
A practical workflow is to treat the target hardware as the starting constraint and work
backward. If the model must run on a laptop with limited memory, moderate quantization may
be the only way to fit it at all, and a small quality loss is acceptable. If it runs on
ample server GPUs, quantization may be unnecessary and the full-precision model is
preferable. Measuring the actual quality impact on the specific task, rather than trusting
generic benchmarks, is essential because the degradation is task-dependent and can be
negligible on some workloads while material on others. Quantization is a tool to fit a
deployment, not a universal improvement.
