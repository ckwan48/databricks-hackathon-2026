## Geometric (Spatial) Deep Learning: Graph Neural Nets for Stunting

**Question.** Does a *geographic* graph — districts wired to their physical neighbours — help predict child stunting beyond ordinary non-spatial models? Given strong spatial autocorrelation in the data (Moran's I = +0.47 for stunting, +0.59 sanitation, +0.68 schooling, all p<0.01), a spatial inductive bias *should* help, in principle. We test this directly.

**Setup.** Merged `causal_analytic_table_v2.csv` with `district_geo.csv` on (state, district), keeping the **n = 569** districts that have recovered centroids, a stunting value, and all 9 node features. Built a **geographic graph** by haversine k-NN (k = 8) on (lat, lon), symmetrized (5,488 directed edges). Node features (standardized): `sanitation, clean_fuel, fem_school10, literacy, anc4, electricity, women_overweight, urbanicity, pop_under15`. Single random split: train 341 / val 113 / test 115 (seed 42). Target standardized on the training fold; all metrics reported in original percentage-point units. Best epoch chosen by validation RMSE.

**Models.** Spatial GNNs on the geographic graph — GAT (2× GATConv, 4 heads), GraphSAGE (2× SAGEConv), and a spatial GCN. Non-spatial comparators on the *same split* — Ridge, HistGradientBoostingRegressor (xgboost stand-in), and a GCN on a **feature-space** k-NN graph (a graph that ignores geography).

**Results (test set, n=115).**

| Model | Graph | Spatial? | Test R² | Test RMSE (pp) |
|---|---|---|---|---|
| **Ridge** | none | no | **0.385** | **6.29** |
| GraphSAGE | haversine-kNN | yes | 0.351 | 6.46 |
| GCN | feature-kNN | no | 0.336 | 6.54 |
| GAT | haversine-kNN | yes | 0.263 | 6.88 |
| GCN | haversine-kNN | yes | 0.242 | 6.98 |
| HistGBR | none | no | 0.200 | 7.17 |

**Verdict — the spatial graph does NOT clearly improve prediction.** On the primary split, the best non-spatial model (Ridge, R² = 0.385) edges out the best spatial GNN (GraphSAGE, R² = 0.351); the difference (ΔR² = −0.035) is small and within run-to-run noise. A 5-seed robustness check tells the more honest story: GraphSAGE-geo averages **R² = 0.468 (sd 0.066)** vs Ridge **0.422 (sd 0.084)** — the spatial GNN's mean is slightly *higher*, but the distributions overlap heavily (within ~1 sd). With only ~115 test districts, **the two are statistically indistinguishable.** The spatial inductive bias neither reliably helps nor hurts.

**Why the modest payoff, despite strong Moran's I.** The 9 node features are themselves strongly spatially autocorrelated (sanitation, schooling). A plain regression on those features already absorbs most of the geographic signal, leaving little *residual* spatial structure for message-passing to exploit. The geographic graph and the feature-kNN graph also perform comparably (0.351 vs 0.336), reinforcing that "who is nearby" and "who is similar" carry overlapping information here.

**GAT attention — which neighbours matter.** Attention is fairly diffuse (mean max-share per node = 0.108, near the k=8 uniform value of ~0.125) but tilts toward the **nearest, same-state** neighbours. The highest-attention edges are all tight intra-Sikkim links at 20–28 km (e.g. South↔West, East↔West Sikkim, attention ≈ 0.20). So when the GAT does lean on geography, it leans on close, administratively-similar districts — consistent with the spatial autocorrelation finding.

**Guardrails.** Ecological, cross-sectional, small-n (569 districts, 115 in test) — DL here is exploratory, not confirmatory. The honest takeaway: geometric deep learning is *justified* by the spatial autocorrelation and is *competitive*, but on this dataset it does **not** beat a well-tuned linear model, because the predictive spatial signal is already embedded in the features.

**Artifacts.** `gnn_geometric_results.json` (all model metrics, 5-seed robustness, GAT top-attention edges), `figures/gnn_geometric.png` (test-R² bar chart, spatial vs non-spatial). torch_geometric (PyG 2.8.0) ran cleanly — no fallback needed.
