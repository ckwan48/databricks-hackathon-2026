## Penalized Regression and Stability Selection (Robust Driver Selection)

**Goal.** Identify which district-level predictors are robustly *predictively associated* with three outcomes — `stunting`, `inst_birth` (institutional birth), and `child_marriage` — using L1/elastic-net regularization plus bootstrap stability selection. All 13 candidate predictors were standardized (mean 0, SD 1) before fitting, so coefficients are directly comparable in SD-per-SD units. `LassoCV` and `ElasticNetCV` use 5-fold CV; the reported R² is an out-of-fold cross-validated R² (not in-sample fit).

**Sample.** Complete-case n = **425 districts** for every outcome (identical because the binding missingness is in two predictors: `supply_gini`, 281 missing, and `urbanicity`, 137 missing). The original table has 706 districts, so ~40% are dropped — results describe the supply-data-complete subset, not all districts.

### Cross-validated fit and selected predictors

| Outcome | n | Lasso CV R² | ElasticNet CV R² | ENet l1_ratio | Lasso α | # nonzero (Lasso / ENet) |
|---|---|---|---|---|---|---|
| stunting | 425 | 0.487 | 0.489 | 0.90 | 0.239 | 9 / 9 |
| inst_birth | 425 | 0.525 | 0.525 | 0.10 | 0.026 | 13 / 13 |
| child_marriage | 425 | 0.549 | 0.549 | 0.50 | 0.098 | 11 / 12 |

Lasso and ElasticNet agree closely on both fit and coefficients. For `inst_birth` the chosen elastic net is near-ridge (l1_ratio = 0.10), so it keeps all 13 predictors — a sign of correlated, jointly-informative predictors rather than a small sparse signal.

**Selected (nonzero) standardized coefficients — Lasso (sign = direction of association):**

- **stunting** (higher = worse): `women_overweight` −2.54, `pop_under15` +1.76, `sanitation` −1.24, `electricity` −1.11, `improved_water` +0.80, `supply_gini` −0.55, `fem_school10` −0.48, `literacy` −0.44, `sex_ratio` −0.09. (`anc4`, `urbanicity`, `clean_fuel`, `n_facilities` shrunk to 0.) The positive `improved_water` sign is counter-intuitive and likely reflects collinearity / ecological confounding, not a protective-reversed effect.
- **inst_birth** (higher = better): `anc4` +2.37, `pop_under15` −4.68, `clean_fuel` +1.14, `fem_school10` +1.06, `sanitation` −0.96, `improved_water` +0.82, `supply_gini` +0.75, `electricity` +0.68, `sex_ratio` −0.67, `women_overweight` −0.45, `urbanicity` −0.47, `n_facilities` +0.11. All 13 retained.
- **child_marriage** (higher = worse): `fem_school10` −5.78 (dominant protective), `sanitation` −2.97, `literacy` −1.86, `clean_fuel` +1.57, `electricity` +1.39, `sex_ratio` +1.28, `pop_under15` +1.26, `anc4` −0.94, `supply_gini` +0.76, `urbanicity` +0.69, `n_facilities` +0.47. (`women_overweight`, `improved_water` ≈ 0.)

Full coefficients in `penalized_coefs.csv`.

### Stability selection (200 bootstrap Lasso refits, robust = selected >80%)

Each outcome was refit with Lasso (at the LassoCV-chosen α) on 200 bootstrap resamples; the table reports each feature's selection frequency. A driver is **robust** if it is nonzero in >80% of resamples. Full frequencies in `stability_selection.csv`; bars in `figures/stability_selection.png`.

| Outcome | Robust drivers (>80%, freq) |
|---|---|
| stunting | sanitation 1.00, electricity 1.00, women_overweight 1.00, pop_under15 1.00, improved_water 0.97, supply_gini 0.90 |
| inst_birth | anc4 1.00, improved_water 1.00, pop_under15 1.00, sanitation 0.99, electricity 0.99, sex_ratio 0.99, clean_fuel 0.98, supply_gini 0.98, fem_school10 0.97, urbanicity 0.96, literacy 0.94, women_overweight 0.91, n_facilities 0.88 (all 13 robust) |
| child_marriage | sanitation 1.00, fem_school10 1.00, sex_ratio 1.00, clean_fuel 1.00, literacy 1.00, electricity 1.00, supply_gini 0.98, n_facilities 0.96, urbanicity 0.96, pop_under15 0.94, anc4 0.94 |

### Comparison to the causal-surviving set {fem_school10, anc4, women_overweight, urbanicity}

The penalized/stability lens (predictive) and the causal-surviving set diverge meaningfully, by outcome:

- **stunting:** Only **women_overweight** from the causal set is robust here. `fem_school10` is selected by Lasso (coef −0.48) but **drops below the 80% bootstrap threshold** (unstable, collinear with literacy). `anc4` and `urbanicity` are *not selected at all*. Conversely, predictive-but-not-causal drivers `sanitation`, `electricity`, `pop_under15`, `improved_water`, `supply_gini` are robustly selected — these are strong correlates that the causal analysis attributes to confounding.
- **inst_birth:** All four causal-set members (**anc4, fem_school10, women_overweight, urbanicity**) are robust — but so is *every other* predictor (all 13 >80%). Selection here is uninformative for discriminating causal from predictive: institutional birth is densely predicted by the whole development bundle.
- **child_marriage:** **fem_school10** (robust, 1.00, dominant coefficient) and **urbanicity** (0.96) overlap with the causal set; **anc4** is borderline-robust (0.94); **women_overweight** is *not selected*. Many other socioeconomic predictors (sanitation, literacy, clean_fuel, electricity, sex_ratio) are also robust.

**Net:** The robust *predictive* set is consistently **broader** than the causal-surviving set. fem_school10 and anc4 recur as robust drivers (matching the causal story for inst_birth and child_marriage), and women_overweight is robust for stunting; but the causal members do not dominate, and several non-causal correlates (sanitation, electricity, pop_under15, supply_gini) are at least as stable. This is exactly the expected pattern: regularization + bootstrap rewards predictive stability among correlated development indicators, which is **not** causal identification.

### Caveats

- **Predictive, not causal.** Selection frequency reflects predictive association under collinearity, not effect identification; high stability of a correlate (e.g., `sanitation`, `electricity`) does not imply a manipulable causal effect.
- **Collinearity drives instability/swaps.** fem_school10 ↔ literacy and sanitation ↔ electricity ↔ improved_water are highly correlated; Lasso arbitrarily keeps one of a correlated cluster, which both inflates some selection frequencies and explains fem_school10's sub-threshold instability for stunting.
- **Ecological + cross-sectional + residual confounding.** District-level associations need not hold within districts; no temporality; unmeasured confounders remain. The counter-intuitive `improved_water` (+) sign for stunting is a likely symptom.
- **Subset bias.** n = 425 of 706 (complete-case on supply_gini/urbanicity). If supply-data availability correlates with development, the selected set may not generalize to the full 706 districts.
- α was chosen by CV and stability was assessed at that fixed α; a different α (or the classic Meinshausen–Bühlmann randomized-lambda variant) would shift the frequency thresholds somewhat.
