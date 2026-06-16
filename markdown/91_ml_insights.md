## Machine-Learning Insights: Prediction, Typology & Anomalies

**Scope & method.** This section uses ML/statistics to find *patterns*, not causes. We train predictive
models, group districts into archetypes, and flag outliers across 706 districts (per-analysis dropna; n
reported below). **Feature importance here is PREDICTIVE, not causal** — a feature can rank high because it
co-varies with the outcome or with a true driver, not because changing it would move the outcome.

### (1) What predicts each outcome — GradientBoostingRegressor + permutation importance

Gradient-boosted trees were trained on all 26 treatment/confounder/urbanicity/supply features
(complete-case n=425 after dropping rows missing pincode/supply features). Performance is 5-fold
cross-validated R²; importances are permutation-based (mean R² drop on a held-out 30% test split when a
feature is shuffled, 30 repeats).

| Outcome | n | CV R² (mean ± sd) | Top predictive features (perm. importance) |
|---|---|---|---|
| **stunting** | 425 | **0.51 ± 0.04** | women_overweight (0.19), menstrual_hygiene (0.11), pop_under15 (0.07), insurance (0.04), literacy (0.04), electricity (0.03) |
| **inst_birth** | 425 | **0.60 ± 0.04** | pop_under15 (0.41), anc4 (0.08), electricity (0.04), clean_fuel (0.04), sanitation (0.03), insurance (0.02) |

Readings (predictive, not causal):
- **Stunting** is best predicted by the *socioeconomic/nutrition gradient*: `women_overweight` (a proxy for
  affluence/over-nutrition transition — high values track *low* stunting) and `menstrual_hygiene` /
  `literacy` / `insurance` dominate. These proxy a district's development level rather than acting as direct
  child-stunting levers.
- **Institutional birth** is overwhelmingly predicted by `pop_under15` (the share of population under 15 —
  high young-population share marks higher-fertility, lower-access districts) followed by antenatal care
  (`anc4`) and household infrastructure (electricity, clean fuel, sanitation). Supply-count features
  (n_facilities, n_hospital) and urbanicity rank low once these are in the model.
- Urbanicity and the raw supply/pincode counts contribute modestly to prediction — the SES/demographic
  proxies absorb most of their signal. Artifact: `ml_feature_importance.csv`; figure:
  `figures/ml_feature_importance.png`.

### (2) District typology — KMeans archetypes

Twelve standardized indicators (stunting, inst_birth, full_imm, anaemia_women, sanitation, clean_fuel,
fem_school10, literacy, urbanicity, n_facilities, pct_zero_pins, women_overweight) were clustered over
n=559 complete-case districts. **k=4** chosen by silhouette (sil: k3=0.245, **k4=0.256**, k5=0.176,
k6=0.150).

| Cluster | Archetype | n | Stunting | InstBirth | Sanitation | FemSchool10 | Urbanicity | n_facilities | women_OW |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Urban-affluent, low-stunting** | 38 | 29.0 | 94.1 | 82.8 | 58.8 | 54.1 | 85.2 | 37.8 |
| 2 | **Mixed-affluent, low-stunting** | 217 | 27.8 | 94.6 | 80.5 | 49.4 | 16.0 | 10.2 | 30.5 |
| 0 | **Mixed-poor, high-burden** | 272 | 38.6 | 85.5 | 61.8 | 29.7 | 10.6 | 3.0 | 15.5 |
| 3 | **Rural-poor, low-access** | 32 | 33.7 | **56.3** | 85.6 | 37.0 | 7.4 | 0.6 | 17.5 |

- **Cluster 1 (urban-affluent, n=38):** the metros — high urbanicity, dense supply (85 facilities avg), high
  schooling/sanitation, lowest burden. Best-off group.
- **Cluster 2 (mixed-affluent, n=217):** the large "healthy middle" — low stunting and high inst_birth
  despite modest urbanicity and thin facility counts; strong household infrastructure carries them.
- **Cluster 0 (mixed-poor, n=272):** the *largest* group and the priority cohort — highest stunting (38.6),
  lowest sanitation/schooling, low facility counts. Classic rural-poor high-burden profile.
- **Cluster 3 (rural-poor, low-access, n=32):** a distinctive *access-failure* archetype — sanitation is
  actually high (85.6) but institutional birth collapses to **56.3** and immunization is lowest (60.7); near-
  zero facilities (0.6) and lowest urbanicity. These are remote/tribal districts where the binding
  constraint is *physical access to care*, not household poverty. Artifact: `district_clusters.csv`.

### (3) Anomaly detection — IsolationForest

IsolationForest (300 trees, 5% contamination) over the same 12-indicator space flagged **28 of 559**
districts as multivariate outliers. Reference means: stunting 33.5, inst_birth 87.9.

- **GOOD outliers** (low stunting + high inst_birth, unusual *because* they outperform): **Chennai**
  (stunting 20.4, inst_birth 100), **Hyderabad**, **Kolkata**, and the Kerala districts **Ernakulam /
  Thiruvananthapuram (19.5) / Alappuzha**. Two distinct reasons: metros are anomalous on
  urbanicity+supply density; Kerala districts are anomalous because they combine very low stunting with very
  high `pct_zero_pins` (65–82% of pincodes lack a facility) — strong outcomes *despite* sparse mapped
  supply, reflecting an unusually effective primary-care system rather than facility counts.
- **BAD outliers** (high stunting + low inst_birth): **Tuensang, Nagaland** (inst_birth 34.8) and **East
  Kameng, Arunachal Pradesh** (inst_birth 76.0, urbanicity ~1) — remote NE hill districts; the
  "rural-poor low-access" archetype at its extreme.
- **MIXED outliers**: Delhi sub-districts (West/East/Central/North-East — anomalous on extreme urbanicity
  with only mid outcomes), **Mahe, Puducherry** (stunting 48.2 with inst_birth 100 — internally
  contradictory profile), and **Ahmadabad**. Of the 28 flags: ~5 clearly good, ~2 clearly bad, the rest
  mixed/structural.

### Caveats (restated)
- **Ecological**: all units are districts, not individuals — relationships need not hold at the person level.
- **Predictive ≠ causal**: importance ranks reflect co-variation; high-ranked features (e.g.
  women_overweight, pop_under15) are largely *development/demographic proxies*, not intervention levers.
- **Cross-sectional**, single snapshot; no temporal dynamics.
- **Residual unobserved confounding** and **MNAR**: pincode/supply features are missing for ~19–40% of
  districts (n drops to 425/559); missingness may be non-random (often the most remote districts), biasing
  who enters each model. **Small-n** for ML — silhouette is modest (0.26), so cluster boundaries are soft.
- Treat all of this as **evidence and hypothesis generation, not proof**.
