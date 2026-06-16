## Unified Ensemble "Solver": Best Predictor with Interpretable Rules + Uncertainty

**Setup.** For each outcome we built a common **5-fold CV leaderboard** (KFold, shuffle, seed=42) over 13 district-level features (sanitation, clean_fuel, fem_school10, literacy, anc4, electricity, women_overweight, urbanicity, pop_under15, sex_ratio, n_facilities, supply_gini, pct_zero_pins). Complete-case n = **425 districts** for both `stunting` and `inst_birth`. Five learners competed: an interpretable `DecisionTree(depth=4)`, `RandomForest`, `HistGradientBoostingRegressor` (our XGBoost-equivalent — note xgboost itself is blocked by missing libomp on this machine, and HistGBM uses the same histogram-based gradient-boosting algorithm), `ElasticNetCV`, and a **StackingRegressor** (RF + HistGBM + ElasticNet bases, RidgeCV meta-learner, internal 5-fold).

### Leaderboard (out-of-fold, 5-fold CV)

**stunting (n=425, mean=32.9, SD≈8.7)**

| Model | CV R² | CV RMSE |
|---|---|---|
| **Stacked** | **0.501** | **6.13** |
| RandomForest | 0.490 | 6.19 |
| ElasticNetCV | 0.489 | 6.19 |
| HistGBM (xgb-eq) | 0.440 | 6.48 |
| DecisionTree(d4) | 0.365 | 6.91 |

**inst_birth (n=425, mean=90.3, SD≈9.6)**

| Model | CV R² | CV RMSE |
|---|---|---|
| **Stacked** | **0.554** | **6.43** |
| RandomForest | 0.550 | 6.46 |
| HistGBM (xgb-eq) | 0.529 | 6.60 |
| ElasticNetCV | 0.526 | 6.63 |
| DecisionTree(d4) | 0.388 | 7.53 |

**Does stacking win?** Marginally, yes. Stacking is the top model for both outcomes but the gain over the best single model (RandomForest) is **tiny**: ΔR² = +0.011 for stunting (0.501 vs 0.490) and +0.004 for inst_birth (0.554 vs 0.550) — within CV noise. **Honest read: the ensemble does NOT meaningfully beat a single RandomForest.** A plain RF (or even the linear ElasticNet, which ties RF on stunting) is the pragmatic choice; stacking adds complexity for a fraction of a point. The depth-4 tree is clearly the weakest (R²≈0.37–0.39) — it is kept only for rule extraction, not prediction.

### Permutation feature importance (from best model = Stacked, refit on full data, 30 repeats)

- **stunting:** `women_overweight` (0.201) ≫ `pop_under15` (0.111) > `electricity` (0.077) ≈ `sanitation` (0.075) > `literacy` (0.057) > `fem_school10` (0.041) > `anc4` (0.038). Women's overweight prevalence acts as a nutrition-transition / affluence proxy (inversely related to stunting); a young age structure (high `pop_under15`) and infrastructure gaps drive stunting up.
- **inst_birth:** `pop_under15` (0.440) dominates — it is the single strongest signal — followed by `anc4` (0.157), then `clean_fuel` (0.054), `electricity` (0.039), `fem_school10` (0.036). Districts with younger populations and weak antenatal-care coverage have far fewer institutional births.

### Interpretable decision rules (DecisionTree depth=4)

**stunting** (district mean ≈ 32.9):
- **HIGH stunting → 47.0** (n=21): `women_overweight < 29.4 AND pop_under15 ≥ 35.1 AND literacy < 62.2` — poor, young, low-literacy districts.
- **HIGH → 43.2** (n=15): `women_overweight < 29.4 AND 31.6 ≤ pop_under15 < 35.1 AND literacy < 62.2`.
- **LOW stunting → 19.3** (n=14): `women_overweight ≥ 36.8 AND literacy ≥ 87.5 AND urbanicity < 22.2` — affluent, high-literacy districts.
- **LOW → 22.6** (n=20): `women_overweight ≥ 36.8 AND literacy ≥ 87.5 AND urbanicity ≥ 22.2`.

**inst_birth** (district mean ≈ 90.3):
- **HIGH inst_birth → 98.7** (n=74): `pop_under15 < 24.4 AND clean_fuel ≥ 66.0 AND sex_ratio ≥ 998.5` — near-universal institutional delivery.
- **HIGH → 95.4** (n=52): `pop_under15 < 24.4 AND clean_fuel < 66.0 AND anc4 ≥ 60.0`.
- **LOW inst_birth → 65.4** (n=10): `pop_under15 ≥ 28.3 AND anc4 < 22.6` — young districts with collapsed antenatal care; the clearest intervention target.
- **LOW → 75.5** (n=33): `pop_under15 ≥ 28.3 AND pop_under15 ≥ 32.2 AND electricity < 97.2`.

### Prediction-uncertainty band

| Outcome | CV residual SD | ~95% band (±1.96·SD) | GBR q10–q90 width | Empirical 80% coverage |
|---|---|---|---|---|
| stunting | 6.13 | ±12.0 | 13.4 | 0.69 |
| inst_birth | 6.44 | ±12.6 | 11.8 | 0.67 |

A point prediction carries roughly **±6 pp (1 SD)** of irreducible CV error, i.e. a ~±12 pp 95% interval. The GradientBoosting quantile band (alpha=0.10/0.90) gives a similar ~12–13 pp 80% width but **under-covers** (≈0.67–0.69 vs nominal 0.80) out-of-fold — quantile estimates are over-confident on this small n. **Use the residual-SD band as the honest uncertainty.**

### Bottom line / guardrails
The best predictor is the stacked ensemble, but it is a **statistical tie with a single RandomForest** (R²≈0.50 stunting, ≈0.55 inst_birth) — report RF as the practical model. Roughly half the district-level variance is explained; the rest is irreducible at this resolution. xgboost ≈ HistGBM here (libomp blocked). All findings are **ecological, cross-sectional, complete-case (n=425 of 706)** — rules describe *associations*, not causal levers, and the ±12 pp band must accompany any district forecast.

*Artifacts: `/Users/koushik/Desktop/health_analysis_outputs/ensemble_leaderboard.csv`, `/Users/koushik/Downloads/DAS_HACK/figures/ensemble_leaderboard.png`*
