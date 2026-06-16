## Hierarchical / Multilevel Models: Borrowing Strength Across Geography (Partial Pooling)

**Question.** District health indicators are noisy, and some states are represented by only one or two
districts. How do we estimate a district's "true" level without (a) trusting tiny samples blindly
(no pooling) or (b) ignoring real state-to-state differences (complete pooling)? The principled
answer is **partial pooling** via a multilevel model with a random intercept by state.

### Model

`stunting ~ sanitation + fem_school10 + urbanicity + pop_under15` with a **random intercept by state**,
fit with statsmodels `MixedLM` (REML). Complete cases: **N = 569 districts across 33 states**
(137 districts dropped for missing pincode-derived `urbanicity`).

**Fixed effects (population-average associations):**

| Term | Coef. | Std.Err. | z | p |
|---|---:|---:|---:|---:|
| Intercept | 31.171 | 4.141 | 7.53 | <0.001 |
| sanitation | **-0.148** | 0.027 | -5.53 | <0.001 |
| fem_school10 | **-0.094** | 0.036 | -2.59 | 0.010 |
| urbanicity | -0.019 | 0.026 | -0.73 | 0.463 |
| pop_under15 | **+0.628** | 0.097 | +6.48 | <0.001 |

After accounting for clustering within states, each +1 percentage-point of household sanitation is
associated with **-0.15 pp stunting**, and each +1 pp of women with 10+ years schooling with
**-0.09 pp stunting**. A younger age structure (`pop_under15`) strongly co-moves with higher stunting
(+0.63 pp per point). `urbanicity` adds little once the others are in the model.

### Variance decomposition and intraclass correlation (ICC)

| Component | Variance | SD |
|---|---:|---:|
| Between-state (random intercept) | 12.16 | **3.49** |
| Within-state (residual) | 33.46 | 5.78 |

**ICC = 12.16 / (12.16 + 33.46) = 0.27.** About **27%** of the *residual* variation in stunting (after the
fixed covariates) lives **between states**; the remaining 73% is within-state, between-district. In a
covariate-free (intercept-only) model the raw clustering is even stronger: **ICC = 0.37**, i.e. roughly a
third of total stunting variation is between states before any predictors are added. Either way, the
state-level clustering is substantial and large enough that ignoring it (treating 569 districts as
independent) would overstate precision — the multilevel structure is warranted.

### Partial pooling = the principled, sample-size-weighted shrinkage

The shrinkage weight for each state is
**λ = τ² / (τ² + σ²/n)**, where τ² is between-state variance, σ² is within-state variance, and *n* is the
number of districts in that state. The shrunk estimate is
**state_shrunk = grand_mean + λ · (state_mean_raw − grand_mean)** (grand mean = 31.58).

- λ → **1** when *n* is large: the state has enough districts to speak for itself, so its estimate stays
  put. Uttar Pradesh (n=63, λ=0.97), Madhya Pradesh (n=48, λ=0.97), Bihar (n=37, λ=0.96) barely move
  (pull < 0.5 pp).
- λ → **τ²/(τ²+σ²) ≈ 0.37** when *n* = 1: a single-district state is unreliable, so its estimate is pulled
  ~63% of the way toward the national mean.

**Small-sample / extreme states (the cases where pooling matters most):**

| State | n districts | raw state mean | shrunk estimate | λ | pull toward grand |
|---|---:|---:|---:|---:|---:|
| Andaman & Nicobar | 1 | 21.60 | 27.91 | 0.37 | -6.31 |
| Ladakh | 1 | 36.50 | 33.39 | 0.37 | +3.11 |
| Chandigarh | 1 | 25.30 | 29.27 | 0.37 | -3.97 |
| Goa | 2 | 26.25 | 28.71 | 0.54 | -2.46 |
| Sikkim | 3 | 22.60 | 25.87 | 0.64 | -3.27 |
| Puducherry | 3 | 32.90 | 32.42 | 0.64 | +0.48 |
| Mizoram | 7 | 28.61 | 29.20 | 0.80 | -0.59 |
| West Bengal | 7 | 33.17 | 32.86 | 0.80 | +0.31 |

A lone district reporting an unusually low (Andaman, 21.6) or high (Ladakh, 36.5) value is treated with
appropriate skepticism: the model nudges it several points toward the national level because one
observation is weak evidence about that state's true level. By contrast, an extreme district *inside a
large, well-sampled state* keeps most of its signal — e.g. Bahraich, UP (raw 52.1) stays at 51.5 because
UP's 63 districts make its state context trustworthy.

### Why this is the right way to borrow strength across geography

This is the **principled, sample-size-weighted version of the "section-87 fallback"** — the heuristic of
substituting a parent (state) value when a unit's own data are thin. Instead of an all-or-nothing rule
("use the district value if you have it, else use the state value"), the multilevel model does a
**continuous, automatically-tuned blend**:

1. **Small / extreme districts shrink toward their state (and weak states toward the nation).** Their own
   estimates are noisy, so the model leans on the broader pool — exactly the situation the fallback was
   trying to handle, but graded by how noisy each unit actually is.
2. **Large, well-sampled districts/states stay put.** They carry enough information to stand on their own,
   so no information is thrown away by over-aggregating.
3. **The blend weight (λ) is estimated from the data**, not hand-set: it is the optimal (minimum
   mean-squared-error / empirical-Bayes) trade-off between within- and between-group variance. This
   guards against both overfitting tiny samples (no pooling) and erasing real geographic differences
   (complete pooling).

In short, partial pooling generalizes the fallback rule into a statistically optimal estimator: every
district is a weighted average of "what its own data say" and "what its neighbors (state) say," with the
weight set by how much we can trust each.

**Artifacts.** `multilevel_shrinkage.csv` (569 districts: raw value, state mean, state-shrunk prior,
district-shrunk estimate, full-model fitted value, λ, n_districts);
figure `multilevel_shrinkage.png`.

### Guardrails

- **Ecological & cross-sectional.** Coefficients are district-level associations from a single
  NFHS-style cross-section; they are not individual-level and not causal. `pop_under15`'s positive
  coefficient is structural co-variation, not a lever to pull.
- **Residual confounding.** Only four covariates are adjusted; omitted factors (poverty, diet, caste
  composition, altitude for Ladakh-type outliers) likely remain.
- **Shrinkage caveat.** Partial pooling deliberately biases small-state estimates toward the mean to
  reduce variance. This *improves* accuracy on average but can mask a genuinely exceptional small state
  (e.g. Ladakh's high altitude / Andaman's island profile may be real, not noise). The shrunk number is
  the best *predictive* estimate, not a denial that the raw value could be true.
- **Missingness.** 137/706 districts dropped for missing `urbanicity`; if urbanicity-missing districts
  differ systematically, the fixed effects could shift. Re-running without `urbanicity` is advisable as a
  sensitivity check.
