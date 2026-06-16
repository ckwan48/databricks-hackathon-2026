## Sensitivity, Difference-in-Differences Design & Triangulation

*Synthesis of the causal workstream. This section stress-tests the two flagship adjusted effects with E-values, lays out the difference-in-differences (DiD) upgrade that breaks the cross-sectional ceiling, and issues a verdict for each main relationship by triangulating across structure learning, regression adjustment, and matching. All numbers are computed on the complete national table (706 districts, 0 missing on the core variables), reproducible via `statsmodels` OLS with state fixed effects, `causal-learn` PC, and 1-NN propensity matching.*

**Read this first — the honesty banner.** Every estimate below is **ecological** (district aggregates, not individuals — a district-level slope does NOT license an individual-level claim; this is the ecological fallacy). The data are **cross-sectional** (one NFHS-5 snapshot — no temporal precedence, so "treatment before outcome" is assumed, not observed). There is **unobserved confounding** (no income, no caste, no wealth quintile in the table). And suppression is **MNAR** (small/remote districts drop out deterministically when cases <25). These methods estimate causal **evidence**, not causal **proof**.

---

### (a) Sensitivity: re-estimated effects + E-values

Two adjusted models, OLS with confounders (% pop <15, sex ratio, literacy, plus the competing exposures) and **state fixed effects** (`C(state)`), complete cases **n = 706** each:

| Relationship | β (per 1 pp of treatment) | SE | p | 95% CI | per-1-SD effect (Cohen's d) |
|---|---|---|---|---|---|
| sanitation → stunting | **−0.0885** | 0.0261 | 7.5e-04 | [−0.140, −0.037] | d = −0.149 |
| fem_school10 → child_marriage | **−0.1587** | 0.0563 | 5.0e-03 | [−0.269, −0.048] | d = −0.181 |

Both are significant and protective: a 10-pp rise in district sanitation coverage is associated with **~0.9 pp lower stunting**; a 10-pp rise in female 10+-schooling with **~1.6 pp less child marriage**, *after* state FE and confounders.

**E-value** (VanderWeele & Ding 2017) = the minimum strength, on the **risk-ratio scale**, that an unmeasured confounder would need to have with *both* the treatment *and* the outcome (above and beyond measured covariates) to fully explain away the observed effect. Continuous outcomes are mapped to an approximate RR via RR ≈ exp(0.91 · d) per 1-SD of exposure; E = RR + √(RR(RR−1)).

| Relationship | approx RR (per 1-SD) | **E-value (point)** | **E-value (CI limit)** |
|---|---|---|---|
| sanitation → stunting | 0.873 | **1.55** | **1.31** |
| fem_school10 → child_marriage | 0.848 | **1.64** | **1.28** |

**Interpretation — these E-values are MODEST, and that is the headline.** An unmeasured district-level confounder associated with both sanitation and stunting by a risk ratio of only **~1.55** (and ~1.31 to move the confidence interval to the null) would suffice to erase the sanitation effect. For schooling→child-marriage the bar is ~1.64 (~1.28 for the CI). **Household wealth / SES — the exact variable we do NOT have — plausibly clears that bar**: richer districts have more sanitation, more schooling, less stunting, and less child marriage simultaneously, and a wealth–exposure / wealth–outcome RR of 1.3–1.6 is entirely ordinary. So these effects are **not robust** to a single realistic omitted confounder. A high E-value (say >3–4) would let us shrug off confounding; **1.3–1.6 means we cannot.** This is the quantitative statement of the cross-sectional ceiling. Artifact: `sensitivity_evalues.csv`.

---

### (b) Difference-in-Differences design — the single biggest upgrade

The cross-sectional E-values are small **because one snapshot cannot separate the effect from time-invariant district traits** (entrenched poverty, caste composition, terrain, historical infrastructure). DiD across two NFHS waves removes that entire class of confounding.

- **Data to request:** the **NFHS-4 (2015–16) District Fact Sheets** — the per-district Excel/PDF factsheet set published by IIPS/MoHFW (the NFHS-4 analogue of the NFHS-5 district factsheets already used here). Request the *full national district factsheet workbook* (all states/UTs, ~640 districts on 2011 boundaries) plus the **NFHS-4→NFHS-5 district crosswalk** (boundaries changed: post-2011 district splits/renames must be reconciled via LGD codes before any wave can be differenced).
- **Estimand — change-on-change.** For each district *d*, form the within-district change Δ across waves and regress the change in the outcome on the change in the exposure:
  ΔY_d = α + β·ΔT_d + γ·ΔX_d + state-FE + ε_d, where Δ = (NFHS-5 value − NFHS-4 value). β is the DiD estimand: *the effect of the change in treatment on the change in outcome*. (Equivalently, a two-way fixed-effects panel with district + wave FE on the stacked district×wave table.)
- **Parallel-trends assumption (the new identifying assumption).** Absent the treatment change, districts that gained sanitation/schooling would have followed the **same outcome trajectory** as districts that did not. This *replaces* the cross-sectional "no unmeasured confounders" assumption with a weaker, more defensible one — and with ≥2 pre-periods (NFHS-3, 2005–06, where comparable) it becomes partially **testable** (check pre-trends).
- **WHY two waves remove ALL time-invariant confounding.** First-differencing (or district FE) **algebraically cancels every district characteristic that is constant across the two waves** — observed *and* unobserved. District wealth level, caste structure, agro-climate, distance to a city, baseline cultural norms: all difference out, because each appears identically in the NFHS-4 and NFHS-5 terms. We no longer need to *measure* income or caste; we only need them to be **stable over the ~4-year gap**, which they largely are. What survives DiD is only **time-varying** confounding (a shock that simultaneously moved both the exposure and the outcome between 2016 and 2020 — e.g. Swachh Bharat toilet construction co-timed with a nutrition campaign), a far narrower and more inspectable threat than the open-ended cross-sectional confounding above.
- **Why this is the biggest upgrade.** The current ceiling is structural: with one wave, E-values of ~1.5 are the *best attainable* honesty, because wealth is unmeasured and uncancellable. DiD converts the question from "is there an omitted confounder?" (almost certainly yes) to "did the exposure and outcome trends move together for a reason *other than* the causal link?" (a specific, often-rejectable hypothesis). It moves verdicts from SUGGESTIVE toward LIKELY-CAUSAL without collecting a single new covariate — just the second wave.

---

### (c) Triangulation & verdicts

A relationship earns confidence only if it survives **three independent lenses**: (1) **structure learning** — does a PC algorithm (`causal-learn`, FisherZ, α=0.05, n=706, 10 core standardized variables) keep an edge between the two after conditioning on the rest? (2) **adjustment** — does the OLS+confounders+state-FE coefficient stay significant with the expected sign? (3) **matching** — does a 1-NN propensity match (high vs low exposure split at the median, matched on confounders) preserve the sign of the effect? Convergence across all three = LIKELY-CAUSAL; partial = SUGGESTIVE; collapse under adjustment = CONFOUNDED. Full table: `triangulation_verdicts.csv`; figure: `figures/86_sensitivity_triangulation.png`.

| Relationship | Bivariate r | PC edge survives? | OLS+FE (sign, sig) | Matched ATT (sign kept?) | E-value | **Verdict** |
|---|---|---|---|---|---|---|
| **sanitation → stunting** | −0.507 | **Yes — directed `sanitation → stunting`** | −0.089, p<0.001 (YES) | −0.61 pp (YES) | 1.55 | **LIKELY-CAUSAL** (but fragile to wealth; needs DiD) |
| **fem_school10 → child_marriage** | −0.652 | **Yes — adjacency retained, undirected** | −0.159, p=0.005 (YES) | −2.25 pp (YES) | 1.64 | **LIKELY-CAUSAL**; PC cannot orient the arrow (could be reverse / common cause) |

Both relationships **survive all three lenses with a consistent protective sign**, which is why neither is graded CONFOUNDED. Two cautions temper the verdict, and both show up directly in the numbers:

- **Massive attenuation as control tightens.** The bivariate signal is large (r = −0.51 and −0.65); the matched ATT is small (−0.61 pp and −2.25 pp). The honest reading is that **most of the raw correlation is confounding** (state context, literacy, co-located infrastructure) and only a residual slice plausibly causal. The PC algorithm keeping the edge tells us that residual slice is *not zero* after conditioning on the other 8 variables — but it cannot see the unmeasured wealth axis.
- **Orientation is not identified for schooling→child-marriage.** PC leaves that edge **undirected**: with cross-sectional data the arrow could run schooling→marriage, marriage→schooling (girls who marry leave school), or both could be driven by a common norm. Direction is exactly what the DiD/temporal design in (b) would resolve.

**Restated limits (carry these into any decision):**
- **Ecological fallacy.** A −0.089 district slope is a between-district aggregate; it does NOT mean an individual household gaining a toilet sees −0.089 pp stunting. Do not transmute these into individual or facility-level promises.
- **MNAR suppression.** Cells <25 cases were dropped deterministically (small/remote districts), so the analyzed 706 districts over-represent larger/better-measured districts; effects in the suppressed tail are unobserved and possibly different.
- **Cross-sectional.** No temporal precedence — every "→" assumes, rather than demonstrates, that the treatment preceded the outcome. The E-values (~1.3–1.6) quantify how thin that assumption is, and the DiD design in (b) is the prescribed remedy.

**Bottom line:** the two flagship links are the best-supported in the dataset — they clear structure learning, adjustment, and matching with a stable protective sign — yet their E-values are low enough that a single unmeasured wealth/caste confounder could explain them away. Treat them as **strong causal evidence, not proof**, and prioritize the NFHS-4 second wave to convert "likely" into "identified."
