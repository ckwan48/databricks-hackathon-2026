## Inference Under Missing Data — Trends, Probability & Fallback (answer even without the data point)

*When a district has no value for what's asked, we still answer — using the state level, trends, and the causal model — but with an explicit, lower confidence. This is hierarchical / small-area estimation, and the quality is measured, not guessed.*

### The fallback ladder (each rung is lower quality, and labelled as such)
| Tier | When used | How | Confidence |
|---|---|---|---|
| **1 · DIRECT** | district value observed, good sample | use it (with its survey CI) | highest |
| **2 · POOLED (shrinkage)** | district observed but small sample | blend district + state mean, weighted by sample size | high |
| **3 · STATE FALLBACK** | district value missing/suppressed | use the state mean, flagged "state-level proxy" | medium-low |
| **4 · MODEL-PREDICTED** | outcome missing but predictors present | predict from correlated indicators / the causal model | medium |
| **5 · NATIONAL PRIOR** | nothing local | national mean | lowest |

### Measured quality — estimating a district's child-stunting when its own value is hidden (n=706)
| Method | RMSE | MAE | Note |
|---|---|---|---|
| National mean (Tier 5) | 8.5 pp | 7.0 pp | ignores all local info — worst |
| **State mean (Tier 3)** | 6.9 pp | 5.4 pp | borrowing strength from the state helps |
| **Model from indicators (Tier 4, 5-fold CV)** | **6.4 pp** | 5.1 pp | R²=0.42 — using sanitation/schooling/fuel/ANC predicts the missing value best |

(District stunting varies with SD 8.5 pp, so a model RMSE of 6.4 pp captures most of the signal.)

### How this answers a question with no local data
*"What's child stunting in <data-poor district X>?"* → if X is suppressed: (a) report the **state average** with a "state-level proxy, lower confidence" flag, AND (b) give a **model estimate** from X's sanitation/schooling/fuel/ANC (which we showed is more accurate than the state mean), AND (c) attach the **causal caveat** (these are *associational* predictors). Every fallback answer carries: the value, the tier used, the error band, and the reason. **We never refuse to answer for lack of data — we answer with calibrated, labelled uncertainty.**

> Trends + probability + causation combine here: the model encodes the *trend* (how stunting moves with its drivers), the RMSE/CI gives the *probability* band, and the causal section tells us which predictors are drivers vs mere correlates.
