# Convolutional Neural Networks

Convolutional neural networks exploit the spatial structure of data by sliding small
learnable filters, or kernels, across the input. Each filter computes a dot product at
every position, producing a feature map that highlights where its pattern occurs. The
same filter is reused everywhere, a property called weight sharing, which dramatically
reduces the number of parameters compared to a fully connected layer and bakes in
translation equivariance.

A typical convolutional block combines convolution, a nonlinearity, and pooling.
Pooling reduces spatial resolution by summarizing local regions, which lowers compute
and grants a degree of translation invariance. Stacking blocks builds a hierarchy:
early layers detect edges and simple textures, middle layers detect parts and motifs,
and late layers detect whole objects. Padding preserves spatial dimensions, while
stride controls how aggressively the input is downsampled.

Convolutional networks transformed computer vision and remain strong for images, video,
and audio. Residual connections, which add the input of a block to its output, allow
networks to grow very deep without degrading, and are the backbone of architectures
such as ResNet. Depthwise separable convolutions factor a standard convolution into two
cheaper operations, enabling efficient models for mobile devices. Techniques such as
batch normalization, data augmentation, and transfer learning from large pretrained
models are standard practice.

Vision transformers now compete with and sometimes surpass convolutional networks on
large datasets, but convolutions retain a useful inductive bias about locality that
helps when data is limited. In many production settings, a hybrid approach or a
well-tuned convolutional backbone remains the pragmatic choice, and understanding
convolution is essential context for interpreting modern vision architectures.
A recurring design question is how receptive field and resolution trade off. Deeper layers
see a larger region of the input, which is what allows them to recognize global objects,
but pooling and striding discard spatial detail that fine-grained tasks such as segmentation
and detection need. Architectures for those tasks therefore use skip connections that
combine deep, semantic features with shallow, high-resolution ones, recovering the detail
that pure downsampling loses. Understanding this tension, between semantic abstraction and
spatial precision, explains the design of most modern vision architectures and why a single
network often taps multiple layers for its final prediction.
