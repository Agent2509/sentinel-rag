# K-Means Clustering

K-means partitions data into k groups by alternating two simple steps. First, assign
every point to the nearest centroid. Second, recompute each centroid as the mean of the
points assigned to it. Repeating until assignments stop changing minimizes the
within-cluster sum of squared distances, a quantity known as inertia.

The algorithm is fast, simple, and scales to large datasets, which explains its
popularity. It also carries clear assumptions. It implicitly treats clusters as
roughly spherical and similar in size, because a point always joins the nearest
centroid under Euclidean distance. It is sensitive to initialization, since a poor
starting configuration can trap it in a bad local minimum; k-means++ seeding spreads
the initial centroids out and largely fixes this. Choosing the number of clusters k is
not automatic, and practitioners use the elbow method, which looks for the point where
inertia stops dropping sharply, or the silhouette score, which measures how well points
sit within their clusters.

K-means makes hard assignments: each point belongs to exactly one cluster. Gaussian
mixture models generalize this by modeling each cluster as a Gaussian and assigning
soft probabilities, which better handles overlapping or elongated clusters. Mini-batch
k-means processes small random samples per iteration to scale to very large data.

The same partitioning idea appears in vector search. An inverted file index clusters
vectors into cells and searches only the nearest cells, accepting a small loss in
recall for a large gain in speed. Understanding k-means therefore pays off twice: once
for clustering itself, and again when reasoning about approximate nearest-neighbor
indexes used in retrieval systems.
Evaluating a clustering is inherently harder than evaluating a classifier, because there is
often no ground truth to compare against. When labels do exist, metrics such as adjusted
Rand index or normalized mutual information measure agreement with them. Without labels,
internal measures such as silhouette, Davies-Bouldin, or the Calinski-Harabasz index
quantify how compact and well-separated the clusters are. None of these fully captures
usefulness, since a clustering should ultimately serve a downstream purpose, whether
organization, compression, or seeding a search index. The practical habit is to combine a
quantitative measure with a visual inspection and a check against the downstream task.
