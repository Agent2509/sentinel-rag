# Support Vector Machines

A support vector machine finds the hyperplane that separates two classes with the
largest possible margin. Intuitively, a wide margin leaves room for error and tends to
generalize well. Only the points closest to the boundary, called support vectors,
determine the position of the hyperplane, which gives the method a sparse and elegant
geometric interpretation.

Real data is rarely perfectly separable, so the soft-margin formulation allows some
points to violate the margin, controlled by a penalty parameter usually denoted C. A
large C prioritizes classifying every training point correctly and risks overfitting; a
small C tolerates more violations and produces a wider, more robust margin. Tuning C is
central to using an SVM well.

The kernel trick is the SVM's signature idea. Instead of explicitly mapping data into a
higher-dimensional space where it becomes linearly separable, the algorithm uses a
kernel function that computes inner products in that space implicitly. The linear,
polynomial, and radial basis function kernels cover most needs, with the RBF kernel
being a strong general-purpose choice. This lets SVMs learn nonlinear boundaries while
remaining grounded in a linear formulation.

SVMs were the dominant classifier before deep learning and still excel on small,
high-dimensional datasets, such as text with thousands of features and few examples.
Their main limitations are training time, which scales poorly with the number of
samples, and the fact that they output decision values rather than probabilities, so
calibration is needed for probabilistic use. They remain a valuable tool when data is
scarce and a margin-based classifier is appropriate.
The margin viewpoint offers a useful lesson that generalizes beyond SVMs. A classifier that
separates classes with the largest possible buffer tends to be robust, which is a
geometric intuition that also underlies modern techniques such as large-margin losses in
representation learning. The idea that only the difficult examples near the boundary drive
the solution is likewise echoed in hard-negative mining, where training focuses on the
examples the model currently gets wrong. Studying SVMs therefore pays off conceptually,
even when a neural network is the model actually deployed, because the underlying
principles of margins and support points recur throughout machine learning.
