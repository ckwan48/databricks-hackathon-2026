## Spectral & Manifold Geometric Methods + Spatial Spillover

**Setup.** Geographic k-NN graph (haversine metric, k=8, symmetrized to an undirected neighbour set) over the **N=569** districts with recovered centroids in `district_geo.csv`, merged to the cleaned causal table. All analyses are ecological and cross-sectional; the graph encodes pure geographic adjacency, so results describe spatial structure, not mechanism.

### (1) Graph-Laplacian spectral embedding (eigenmaps)
`SpectralEmbedding(n_components=3, affinity='precomputed')` on the binary adjacency. The Laplacian eigenmaps **recover the geographic manifold of India almost perfectly from connectivity alone**: embedding axis 1 ≈ longitude (r = **+0.92** with lon, ~0 with lat) and axis 2 ≈ latitude (r = **−0.92** with lat, ~0 with lon). The 2D embedding (left panel of the figure) is essentially a rubber-sheet map of the country, validating that k=8 haversine neighbours capture the true spatial layout.

Colouring the embedding by **stunting** shows the burden is **not aligned with the first two (purely geographic) eigen-axes** — SE1 vs stunting r ≈ 0.00, SE2 vs stunting r = −0.07. The signal instead loads on the **3rd eigenvector** (SE3 vs stunting r = **−0.47**), i.e. stunting varies along a higher-order, non-trivial spatial corridor rather than a simple east–west or north–south line. Visually (centre panel, map coloured by stunting) the gradient runs as a **high-burden central belt — the Madhya Pradesh / Bihar / Jharkhand / Gujarat–Rajasthan core — flanked by lower-burden South-Indian and far-Northern/North-Western rims**. The corridor structure, not a monotone gradient, is the headline.

### (2) Contiguous "health regions"
`AgglomerativeClustering(n_clusters=6, linkage='ward')` on the 3D embedding with **graph connectivity = the k-NN adjacency**, which forces clusters to be spatially contiguous. Regions relabelled R1 (worst stunting) → R6 (best):

| Region | n | stunting | sanitation | fem_school10 | inst_birth | full_imm | child_marriage | Top states |
|---|---|---|---|---|---|---|---|---|
| **R1** | 129 | **37.7** | 66.1 | 30.9 | 90.3 | 75.8 | 22.5 | Madhya Pradesh, Uttar Pradesh, Gujarat, Rajasthan |
| **R2** | 119 | **36.5** | 60.9 | 34.0 | 84.6 | 78.2 | 27.4 | Bihar, Odisha, Jharkhand, Chhattisgarh |
| **R3** | 96 | 32.4 | 78.6 | 35.1 | 76.4 | 66.9 | 21.9 | Assam, Arunachal, Nagaland, Manipur (NE) |
| **R4** | 111 | 30.5 | 76.0 | 50.8 | 97.0 | 82.9 | 17.9 | Tamil Nadu, Telangana, Karnataka, Kerala (South) |
| **R5** | 66 | 29.9 | 81.3 | 46.2 | 89.2 | 79.2 | 13.2 | Uttar Pradesh, Haryana, Delhi, Rajasthan |
| **R6** | 48 | **26.8** | 80.6 | 56.1 | 92.2 | 83.7 | 7.2 | Punjab, J&K, Himachal, Haryana (NW/Himalayan) |

The two worst regions are the **Central plateau (R1)** and the **Eastern plains (R2)** — together 248 districts averaging ~37% stunting, low sanitation (61–66%), low female schooling (31–34%), and the highest child-marriage rates (22–27%). The **far-NE (R3)** is a distinct cluster: moderate stunting but the *lowest institutional birth (76%) and immunisation (67%)* — an access-driven burden profile rather than a poverty/schooling one. The **South (R4)** and **NW/Himalayan (R6)** are the low-burden frontier, with R6 best on every indicator (stunting 27%, child marriage 7%, schooling 56%). The clusters are clean and contiguous (right panel) and align with well-known socio-geographic macro-regions, confirming the embedding + connectivity recovered meaningful structure.

### (3) Spatial spillover (spatial-lag-style OLS)
Row-normalized weight **W** from the same k=8 neighbour set; spatial lag **Wy = neighbour-mean stunting**. Model: `stunting ~ own covariates + Wy` (HC1 robust SE, n=569, no missing in this set).

- **Spillover coefficient (Wy): β = +0.589, SE = 0.063, t = 9.4, p ≈ 7×10⁻²¹.** A district's stunting rises by ~0.59 points for each 1-point increase in its neighbours' average stunting, **holding its own sanitation/fuel/schooling/literacy/ANC/electricity/overweight/urbanicity/age-structure/sex-ratio fixed**. Neighbours' outcomes strongly predict a district's own beyond its covariates — the dominant term in the model by a wide margin.
- **Incremental value of the spatial lag:** R² rises from **0.487 (covariates only) → 0.564** with Wy; adj-R² 0.478 → 0.556; **AIC improves 3715 → 3624 (Δ≈91)**. The geographic spillover term adds ~8 points of explained variance and decisively improves fit.
- Among own covariates, only `pop_under15` (+0.37), `electricity` (−0.18), `women_overweight` (−0.14, a wealth proxy), and `anc4` (+0.04) are individually significant once Wy is included; sanitation and literacy weaken to marginal — much of their apparent effect is absorbed by the spatially-lagged term, the classic signature of spatial confounding in ecological data.

### Moran's I (context)
On the row-normalized k=8 graph, **Moran's I for stunting = +0.46 (999-permutation p = 0.001)** — strong, highly significant positive spatial autocorrelation, consistent with the +0.47 reported in the data brief and with the dominant spillover term above.

### Headline
Laplacian eigenmaps reconstruct India's geography from connectivity alone (axes = lon/lat, r≈0.92), but **stunting loads on a higher-order eigenvector (SE3, r=−0.47) — a central-belt corridor, not a simple gradient.** Contiguity-constrained clustering yields six interpretable health regions; the **Central plateau (R1, ~38%) and Eastern plains (R2, ~37%)** carry the heaviest burden, the far-NE (R3) shows a distinct *access*-driven profile, and the NW/Himalayan rim (R6, ~27%) is best. The spatial-lag model is unambiguous: **neighbour-mean stunting is the single strongest predictor (β=0.59, p≈1e-20), lifting R² from 0.49→0.56 and cutting AIC by 91** — a district's stunting is governed as much by where it sits as by its own conditions (Moran's I = +0.46, p=0.001). Caveat: ecological, cross-sectional, n=569 recovered centroids; spillover ≠ causal contagion and own-covariate effects are likely attenuated by spatial confounding.

**Artifacts:** `/Users/koushik/Downloads/DAS_HACK/figures/spectral_embedding.png` (embedding coloured by stunting | geographic map | region map); `/Users/koushik/Desktop/health_analysis_outputs/spatial_regions.csv` (per-district SE1–SE3, health_region, neighbour-mean stunting).
