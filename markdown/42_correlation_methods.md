## Better Correlation Techniques (to get the *correct* information)

*Pearson alone misleads on this data — indicators are bounded proportions, carry outlier districts, and are confounded by wealth/region. Here is the right toolkit, demonstrated on `sanitation ~ child stunting` using the FULL national data (n=706).*

### Demonstration — the same pair, five methods (national)
| Method | Value | What it tells you |
|---|---|---|
| Pearson r | **−0.507** | linear, outlier-sensitive baseline |
| Spearman ρ | **−0.500** | rank-based, robust to outliers & 0–100 bounds (≈Pearson ⇒ no outlier distortion) |
| Kendall τ | **−0.350** | most robust rank measure; lower by construction |
| Distance correlation | **0.485** | =0 only if truly independent ⇒ confirms a real dependence |
| **Partial r** (control: schooling, clean fuel, electricity) | **−0.250** | the *direct* link after removing shared SES — **~50% of the raw correlation was confounding** |

### The decisive lesson: a sample can invent correlations
On the 100-row sample, `sanitation ~ alcohol` showed **r=+0.60**; on the full national data it is **−0.01 (p=0.84)** — the relationship never existed; it was a regional sampling artifact. **Bivariate correlation from a non-representative slice is untrustworthy.** The fix is the workflow below: full data + rank methods + partial correlation + FDR control.

### The toolkit, matched to this data's problems
1. **Rank methods (Spearman, Kendall τ)** — for outliers and bounded proportions. A large Pearson–Spearman gap flags outlier-driven results.
2. **Partial correlation / regression adjustment** — the key upgrade: conditions on confounders (SES proxies + **state fixed effects**) to isolate the direct association. Demonstrated: it halved sanitation↔stunting.
3. **Distance correlation & mutual information** — detect **non-linear/non-monotonic** dependence Pearson scores ≈0; MI handles mixed types.
4. **Reliability/precision-weighted correlation** — weight districts by sample reliability (full=1, small-sample `(x)`≈0.5, suppressed=0) so the MNAR-suppressed cells don't drive r.
5. **Categorical/mixed pairs** — point-biserial, Cramér's V, polychoric — needed once facility type/operator/state enter.
6. **Multiplicity control** — with **5,356 pairs tested**, ~268 clear p<0.05 by chance. Apply **Benjamini-Hochberg FDR** and prefer **effect size (|r|) over p-values** (e.g. literacy↔contraception is "significant" at p=0.02 yet practically null at r=0.09).
7. **Gaussian Graphical Model (GLASSO / precision matrix)** — a **partial-correlation network** (every edge conditions on all other variables); the natural **bridge to the causal phase** (its skeleton seeds the PC algorithm).

### Recommended workflow for "correct information"
1. Clean + reliability-weight → 2. Spearman/Kendall robust screen → 3. BH-FDR filter → 4. distance-corr/MI pass for non-linear pairs → 5. **partial correlation with state FE + SES** on survivors → 6. **GLASSO network** for the multivariate, confounding-aware picture → 7. hand the skeleton to PC / Bayesian-network structure learning. **Never report a bivariate correlation as causal without step 5** — the sanitation↔alcohol phantom shows why.
