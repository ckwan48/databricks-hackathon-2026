## Deep Learning: Graph Neural Network for District Stunting

**Bottom line: graph structure did NOT help.** A plain ridge regression on the
same 8 features beat the 2-layer GCN on held-out test data. With only 706 (569
usable) district nodes this is an exploratory exercise, not a deep-learning
success story — and the honest result is the conventional baseline wins.

### Setup
- **Nodes:** 569 districts (706 input, 137 dropped for missing `urbanicity`;
  the missingness is itself a caveat — see below).
- **Features (X):** standardized `sanitation, fem_school10, clean_fuel,
  urbanicity, pop_under15, electricity, anc4, literacy`.
- **Graph (A):** no geographic adjacency available, so a **k-NN graph (k=8)** on
  the standardized features via `sklearn.NearestNeighbors`, then symmetrized
  (A = max(A, Aᵀ)); resulting average degree ≈ 10.9. This is a
  **feature-similarity graph, not a spatial graph** — it can only impose
  smoothing across districts that are already alike on the inputs.
- **GCN:** minimal 2-layer implementation in raw torch (no torch-geometric).
  Â = D̃^(−½)(A+I)D̃^(−½); H = relu(Â X W₁); ŷ = Â H W₂; hidden=16, dropout=0.3,
  Adam (lr=0.01, weight_decay=5e-4), MSE loss, early stopping on a validation
  mask. Split: 343 train / 113 val / 113 test (seed 42); baselines trained on
  train+val, all evaluated on the identical 113-district test set.

### Results (held-out test, N=113)

| Model | Test R² | Test RMSE (pp stunting) |
|---|---|---|
| **Ridge regression** | **0.490** | **5.97** |
| GCN (2-layer) | 0.458 | 6.16 |
| GradientBoosting | 0.413 | 6.41 |

- **Ridge > GCN > GBM.** The graph/feature-smoothing of the GCN does not beat the
  linear baseline; `graph_structure_helps = false`.
- That the *linear* model wins over both the GCN and the boosted-tree model
  suggests the feature→stunting relationship here is largely **linear and
  smooth**, with little exploitable nonlinearity or graph locality at this
  sample size. The GCN's own validation R² (0.33) trailing its test R² (0.46)
  indicates an unstable, small-data fit rather than a robust gain.

### Learned embeddings — cluster structure
K-means on the 16-d hidden embeddings is cleanest at **k=2** (silhouette 0.395),
recovering an intuitive split rather than novel geography:
- **Cluster 0 (n=183): high-burden** — mean stunting 40.4 pp, sanitation 57.7%,
  female 10-yr schooling 28.3%.
- **Cluster 1 (n=386): lower-burden** — mean stunting 29.9 pp, sanitation 78.8%,
  schooling 45.6%.

The embedding simply re-encodes the dominant sanitation/schooling gradient that
also drives the predictions — consistent with the linear model winning. No
surprising sub-structure emerged.

### Interpretation
The k-NN-on-features graph offers no information beyond the features themselves,
so the GCN's smoothing is at best redundant and at worst adds variance on a tiny
node set. A GNN would be more justified with a *true spatial adjacency* graph
(geographic neighbors), which is unavailable here.

### Guardrails (restated)
- **Ecological:** districts, not individuals — no individual-level inference.
- **Cross-sectional:** a single snapshot; no temporal/causal dynamics.
- **Residual unobserved confounding** remains; this is predictive modeling, it is
  **causal evidence, not proof**.
- **MNAR:** 137 districts dropped for missing `urbanicity`; if missingness
  correlates with the outcome, the usable sample is biased.
- **Small-n for DL:** 569 nodes is tiny for graph deep learning — treat the GCN
  as exploratory; the linear baseline is the trustworthy summary.

Artifacts: `gnn_results.json`, `figures/gnn_vs_baseline.png`.
