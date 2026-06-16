# Correlation vs. Causation — the causal layer

The hardest, most honest part of the app. A raw correlation tells you two things move together; it does **not** tell you that changing one will change the other. We built a full causal ladder on the **NFHS-5 district health indicators (706 districts)** so a planner knows which levers are *real causes* and which are *coincidences* — and, crucially, whether **building more facilities will actually fix a care gap.**

---

## 1. Why correlation isn't enough — the worked example

Across 706 districts, **improved sanitation and child stunting correlate at r = −0.51** (more toilets → less stunting). It looks like a strong, actionable relationship.

But **wealthier districts have both** better sanitation *and* less stunting. Wealth is a **confounder** — a common cause of both. Once we statistically remove wealth, the sanitation→stunting effect **collapses toward 0**. So sanitation here was largely a *proxy for wealth*, not the cause of the stunting reduction.

By contrast, **female schooling → less child marriage (r = −0.65)** and **ANC4 visits → institutional birth (r = +0.60)** *survive* the same adjustment — those are likely **real causes.**

## 2. The causal ladder we climbed

| Rung | Method | What it buys |
|---|---|---|
| Association | Pearson **r**, Moran's I (spatial autocorrelation) | the raw relationships + whether they cluster in space |
| Structure | **PC algorithm** (constraint-based structure learning) → a Bayesian network / DAG | which variables plausibly cause which |
| Effect estimation | **OLS with state fixed-effects**, **Double-ML**, **Propensity-Score Matching** | the effect size *after* removing confounders, three independent ways |
| Sensitivity | **E-values** | how strong an unmeasured confounder would have to be to overturn the result |
| Non-linearity | **GAM + quantile regression** | dose-response curves and tail (high-burden district) effects |
| Spillover | **spatial GNN / graph methods** | whether a district's outcome depends on its neighbours |

## 3. Effect estimates — naive vs. adjusted (standardized, −1…+1)

This is the table behind the "Causal & ML experiments" tab. Watch what happens to each relationship as we add adjustment:

| Relationship | Naive (raw r) | OLS + state FE | Double-ML | Matching (PSM) | Verdict |
|---|---:|---:|---:|---:|---|
| sanitation → stunting | −0.51 | −0.15 | −0.11 | **−0.01** | **Confounded** — collapses to ~0 |
| clean fuel → stunting | −0.42 | −0.16 | −0.14 | −0.06 | Mostly confounded |
| **schooling → child marriage** | −0.65 | −0.18 | −0.17 | **−0.40** | **Likely causal** — survives |
| **ANC4 → institutional birth** | +0.60 | +0.16 | +0.13 | **+0.36** | **Likely causal** — survives |
| **women overweight → high BP/sugar** | +0.57 | +0.29 | +0.35 | **+0.44** | **Causal** — even strengthens |

(Live Pearson checks on `gold_nfhs` reproduce the naive column: sanitation~stunting −0.51, schooling~child-marriage −0.65, ANC4~inst-birth +0.60, overweight~high-blood-sugar +0.62.)

**Reading it:** a bar that *shrinks toward 0* as you move right was driven by a confounder (sanitation→stunting). A bar that *holds* is a likely real cause (schooling, ANC4, overweight).

## 4. The result that connects to facilities

> **Facility count is only weakly linked to health outcomes after adjustment.**

Supply tends to follow demand, and scraped facility data carries visibility bias. So in the **Medical Desert** track, before recommending *"build more facilities,"* a planner sees the causal pathway for the outcome — and often the real lever is **demand-side** (female schooling, antenatal care), not supply. That is why the causal DAG lives in *Medical Desert*, not on a facility card: it answers *"will more facilities actually fix this gap?"*, not *"does this hospital have an ICU?"*.

## 5. How it surfaces in the app

- **Data Science Lab → Confounding tab**: plot any two NFHS indicators, colour by a confounder, and read a *dynamic*, plain-language interpretation of the correlation (`explain_r`).
- **Data Science Lab → Causal & ML tab**: pick a relationship → naive-vs-adjusted bars with a "confounded vs likely-causal" verdict; pick an outcome → its causal DAG.
- **Medical Desert**: the causal DAG + 4-estimator chart framed as *"will building more help?"*.

## 6. Honest caveats

- NFHS-5 is **cross-sectional** (one wave) — these are *adjusted associations*, the strongest causal claim a single wave supports. Two waves (NFHS-4 → 5) would enable **difference-in-differences**; that's on the roadmap.
- Apparent spatial autocorrelation can be an artifact of omitted variables (Olsson/McMillen) — we treat Moran's I as a **diagnostic**, not proof of a spatial process.
- Suppressed NFHS values are MNAR; we flag, never silently impute.

See [`METHODOLOGY.md`](METHODOLOGY.md) for the trust engine and [`design_research.md`](design_research.md) for the interface techniques.
