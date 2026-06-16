# Correlation vs. Causation — the causal layer, explained

The hardest, most honest part of the app. A raw correlation tells you two things move together; it does **not** tell you that changing one will change the other. This doc explains every concept — what **r** is, how we compute it, what a **confounder** is, how we remove it, and what it all means — using the **NFHS-5 district health indicators (706 districts)**.

---

## 1. What is **r** (the correlation coefficient)?

**r** is **Pearson's correlation coefficient** — one number from **−1 to +1** measuring how tightly two variables move together in a straight line:

- **+1** perfect positive · **0** no linear link · **−1** perfect negative.

**Formula:**

```
        Σ (xᵢ − x̄)(yᵢ − ȳ)                cov(X, Y)
r = ─────────────────────────────  =  ─────────────
    √Σ(xᵢ − x̄)² · √Σ(yᵢ − ȳ)²            σ_X · σ_Y
```

i.e. the **covariance** of X and Y (how they vary together) divided by each variable's **standard deviation** (how much it varies alone), which rescales it to −1…+1.

**How we compute it.** `gold_nfhs` holds **one row per district (706)**; each column is an NFHS percentage (sanitation %, stunting %, women's schooling %, …). The app computes the pairwise matrix with `nf[cols].corr()` (pandas, Pearson) — the **Correlation Explorer heatmap** — and verifies key pairs with SQL `corr(x, y)`. So `r = −0.51` for sanitation↔stunting means: *across 706 districts, more improved sanitation goes with less child stunting, moderately-to-strongly and roughly linearly.*

**Strength tiers** (used by `explain_r`): |r| < 0.1 none · 0.1–0.3 weak · 0.3–0.5 moderate · 0.5–0.7 strong · > 0.7 very strong.

## 2. Why correlation is **not** causation

`r` only says two columns move together. It cannot tell you that changing one will change the other — because a **third variable** can drive both. Acting on a correlation as if it were a cause is how planners waste money.

## 3. What is a **confounder** — and "wealth confounding"?

A **confounder** is a variable **Z** that **causes both X and Y**, manufacturing an X–Y correlation even when X does not cause Y.

```
            Wealth (Z)
           ↙          ↘
   Sanitation (X) ····→  Stunting (Y)
              (apparent, partly spurious link)
```

**Worked example.** Wealthier districts **install more toilets** (↑ sanitation) **and** can **feed children better** (↓ stunting). So sanitation and stunting correlate at **r = −0.51** — but much of that is just **both being downstream of wealth.** Sanitation may not be *causing* the stunting drop; wealth is. That is wealth confounding. (We proxy wealth with district **electrification %**, a standard NFHS wealth indicator.)

## 4. How we **remove** the confounder — the causal ladder

We re-estimate each effect while *holding wealth (and other covariates) constant*, three independent ways. Survive all three → likely causal. Collapse toward 0 → confounded.

| Method | In plain words | Technically |
|---|---|---|
| **Association** (Pearson r, Moran's I) | "Do they move together / cluster in space?" | raw correlation; Moran's I flags spatial autocorrelation |
| **PC structure-learning → DAG** | "Which variables plausibly cause which?" | constraint-based conditional-independence tests (`causal-learn`) build a directed acyclic graph, so we adjust for the *right* confounders |
| **OLS + state fixed-effects** | "Compare districts at the *same* wealth, *within the same state*." | regress `Y ~ X + wealth + state-dummies`; read X's coefficient (dummies absorb state-level policy/geography) |
| **Double-ML** | "Let ML strip out everything wealth/covariates explain from *both* X and Y, then see what's left." | predict treatment & outcome from confounders with ML, regress the **residuals** (Frisch–Waugh–Lovell) with **cross-fitting** — robust to *non-linear* confounding |
| **Propensity-Score Matching** | "Pair each high-X district with a similar low-X one (same wealth), like a natural experiment." | estimate P(high X | covariates), match treated↔control on it, compare outcomes |
| **E-values** | "How strong an unmeasured confounder would it take to explain this away?" | the minimum association an unknown confounder needs with both X and Y to nullify the effect — high = robust |
| **GAM / quantile regression** | "Is the effect non-linear or different in high-burden districts?" | smooth dose-response + tail (high-quantile) effects |

## 5. What we found (naive vs. adjusted, standardized −1…+1)

| Relationship | Naive r | OLS+FE | Double-ML | PSM | Verdict |
|---|---:|---:|---:|---:|---|
| sanitation → stunting | −0.51 | −0.15 | −0.11 | **−0.01** | **Confounded** — collapses to ~0 |
| clean fuel → stunting | −0.42 | −0.16 | −0.14 | −0.06 | Mostly confounded |
| **schooling → child marriage** | −0.65 | −0.18 | −0.17 | **−0.40** | **Likely causal** — survives |
| **ANC4 → institutional birth** | +0.60 | +0.16 | +0.13 | **+0.36** | **Likely causal** — survives |
| **women overweight → high BP/sugar** | +0.57 | +0.29 | +0.35 | **+0.44** | **Causal** — even strengthens |

Live Pearson checks on `gold_nfhs` reproduce the naive column (sanitation~stunting −0.51, schooling~child-marriage −0.65, ANC4~inst-birth +0.60, overweight~blood-sugar +0.62).

**Reading it:** a bar that *shrinks toward 0* as you add adjustment was driven by a confounder (sanitation→stunting). A bar that *holds* is a likely real cause (schooling, ANC4, overweight).

## 6. The result that connects to facilities

> **Facility count is only weakly linked to health outcomes after adjustment.**

Supply follows demand, and scraped facility data carries visibility bias. So in **Medical Desert**, before recommending *"build more facilities,"* a planner sees the causal pathway for the outcome — and the real lever is often **demand-side** (female schooling, antenatal care), not supply. That's why the causal DAG lives in *Medical Desert* (it answers *"will more facilities fix this gap?"*), not on a facility card.

## 7. How it surfaces in the app

- **Data Science Lab → Correlation explorer**: live `r` heatmap over any indicators.
- **Data Science Lab → Confounding tab**: scatter of any two indicators coloured by a confounder, with a *dynamic* plain-language reading (`explain_r`).
- **Data Science Lab → Causal & ML tab**: pick a relationship → naive-vs-adjusted bars with a "confounded vs likely-causal" verdict; pick an outcome → its causal DAG.
- **Medical Desert**: the causal DAG + 4-estimator chart, framed as *"will building more help?"*.

## 8. Honest caveats

- NFHS-5 is **cross-sectional** (one wave) → these are *adjusted associations*, the strongest causal claim one wave supports. Two waves (NFHS-4 → 5) enable **difference-in-differences** (roadmap).
- Apparent spatial autocorrelation can be an omitted-variable artifact (Olsson/McMillen) — we treat Moran's I as a **diagnostic**, not proof.
- Suppressed NFHS values are MNAR; we flag, never silently impute.

See [`METHODOLOGY.md`](METHODOLOGY.md) for the trust engine and [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for the tables.
