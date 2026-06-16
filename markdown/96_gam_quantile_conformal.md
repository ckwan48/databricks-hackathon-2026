## Distribution-Aware Statistical Learning: GAM Dose-Response, Quantile Regression, and Conformal Intervals

**Outcome:** stunting (% children <5). **Analysis n = 569 districts** (complete cases on stunting + sanitation + controls; 137 of 706 dropped for missingness, mostly small union territories and districts lacking female-schooling/sex-ratio fields). Cross-sectional, ecological (district-level) associations — see guardrails.

This section answers the user's "distribution view" question with three complementary lenses: (1) does sanitation act *linearly* on stunting or does it *flatten/threshold*; (2) do the drivers matter *more in the worst-off districts* than at the median; (3) can we attach *calibrated* uncertainty to a stunting prediction.

### (1) Nonlinear dose-response (GLMGam, cubic B-splines, df=6)

Fitting a penalized cubic B-spline in sanitation (smoothing penalty alpha selected by AIC = 100, the most-penalized i.e. smoothest end of the grid) with linear controls (fem_school10, literacy, pop_under15, sex_ratio, urbanicity) gives a partial-effect curve that is **monotone-decreasing and very close to a straight line**. Formal test: adding a quadratic term to the linear OLS does **not** significantly improve fit (nested F-test p = 0.124; quadratic coef ≈ +0.0018, negligible). The effect is **essentially LINEAR with no detectable plateau or threshold** over the observed sanitation range (~30–100%).

Local slopes from the spline (per +1 percentage-point sanitation, controls at mean):

| Sanitation level | Local slope (Δ stunting per +1pp) |
|---|---|
| Q1 = 61.7% | -0.071 |
| Median = 74.0% | -0.109 |
| Q3 = 83.6% | -0.146 |

If anything the curve *steepens slightly* at high coverage (more negative slope), i.e. the opposite of diminishing returns — but the curvature is not statistically distinguishable from linear (p = 0.124). **Practical read: there is no "good-enough" saturation point; marginal gains in sanitation coverage are associated with continued stunting reduction across the whole range.** Linear OLS slope for reference: -0.100 pp stunting per +1pp sanitation (p = 0.0003).

### (2) Quantile regression — do drivers bite harder in high-burden districts? (QuantReg, predictors standardized to +1 SD)

Coefficients are pp change in stunting per +1 SD of each standardized predictor, at the 10th, 50th, and 90th percentile of the stunting distribution (tau = 0.9 = the *highest-stunting / worst-off* districts). Full table in `quantile_coefs.csv` (includes SEs, p-values, 95% CIs, and an OLS-mean row).

| Predictor | tau=0.10 (low-burden) | tau=0.50 (median) | tau=0.90 (high-burden) | OLS mean |
|---|---|---|---|---|
| **sanitation** | -1.69* | -2.91*** | -2.70*** | -2.61*** |
| **fem_school10** | -2.52*** | -3.13*** | **-3.62*** | -3.16*** |
| **urbanicity** | +0.50 (ns) | +0.14 (ns) | -0.25 (ns) | +0.05 (ns) |

(* p<0.05, *** p<0.001, ns = not significant)

Findings:
- **Female secondary schooling (fem_school10) is the standout: its protective slope grows monotonically as burden rises** — from -2.5 pp/SD at tau=0.10 to **-3.6 pp/SD at tau=0.90**. In the worst-off districts, girls' education is the single strongest lever and matters *more* there than at the median. This directly confirms the user's hypothesis that drivers can act differently across the outcome distribution.
- **Sanitation matters everywhere** but its slope is flat-to-slightly-smaller at tau=0.90 (-2.70) vs the median (-2.91); it is weakest (and only marginally significant) in the *low-burden* tail (tau=0.10, -1.69). So sanitation's leverage is concentrated in median-to-high burden districts, not the already-low-stunting ones.
- **Urbanicity is not a significant predictor at any quantile** once sanitation and schooling are held fixed — its sign even flips from + (low tail) to - (high tail) but the CIs all straddle zero. Urban/rural classification adds little beyond what sanitation and schooling already capture.

**Interpretation for triage:** an intervention portfolio aimed at the *highest-stunting* districts should weight female-schooling most heavily (its return rises exactly where the problem is worst), with sanitation as a strong co-lever. A mean-only (OLS) model would have hidden the fact that schooling's payoff is ~15% larger in the high-burden tail.

### (3) Split-conformal 90% prediction intervals (calibrated uncertainty)

Predictor: RidgeCV (standardized features: sanitation, fem_school10, literacy, clean_fuel, anc4, electricity, pop_under15, urbanicity) on a 60/20/20 train/calibration/test split (n = 341 / 113 / 115). Split-conformal using absolute residuals on the held-out calibration set:

- Conformal half-width q-hat = **14.36 pp** -> interval width = **28.73 pp** for a 90% target.
- **Empirical coverage on the held-out test set: 96.5%** (single seed-42 split).
- **Mean coverage over 200 random splits: 91.6% (sd 3.6%)** — essentially the nominal 90%, confirming the procedure is **well-calibrated** rather than the single split being a fluke. Test R^2 ≈ 0.49.

The wide interval (~±14 pp) is itself an honest finding: district-level covariates explain about half the variance in stunting, so any *point* prediction for a new district carries large irreducible uncertainty. Conformal makes that uncertainty **distribution-free and finite-sample valid** — exactly the calibrated guarantee needed for "fallback answers" when a district is missing primary data: we can state a 90% range we genuinely cover ~90% of the time, regardless of model misspecification.

### Bottom line / how this ties together
- **Distribution *shape* matters.** Sanitation's dose-response is effectively linear (no threshold/saturation) — keep investing across the whole coverage range, no "done at X%" cutoff is supported.
- **Drivers act differently across the outcome distribution.** Quantile regression shows female-schooling's protective effect is *strongest in the highest-burden districts* (tau=0.9), a pattern invisible to mean regression — so worst-off districts should prioritize girls' education.
- **Conformal gives calibrated uncertainty.** 90% prediction intervals achieve ~91.6% empirical coverage, providing trustworthy ranges for fallback/imputed answers.

**Artifacts:** `quantile_coefs.csv` (quantile + OLS coefficients with CIs); figure `gam_quantile.png` (Panel A = spline vs linear dose-response with local slopes; Panel B = quantile slopes with 95% bands vs OLS mean).

**Caveats:** Ecological & cross-sectional — coefficients are district-level associations, not individual causal effects, and are vulnerable to residual/unmeasured confounding (the ecological fallacy applies). 137 districts dropped for missingness, which may bias toward better-resourced areas. The selected GAM smoothing penalty sat at the smooth end of the grid, so a true sharp threshold could in principle be over-smoothed away — but the independent quadratic F-test (p=0.124) corroborates linearity. Quantile slopes near the tails (tau=0.10, 0.90) have wider CIs; the QuantReg solver hit its iteration limit on one tail fit (coefficients stable, but treat extreme-tail SEs as approximate).
