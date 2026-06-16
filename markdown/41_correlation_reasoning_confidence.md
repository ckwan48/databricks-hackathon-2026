## Correlation → Reasoning → Causation → Confidence (so the data can be trusted)

*Computed on the FULL NFHS-5 district data (n up to 706 districts, national). 5,356 valid variable pairs. For every claim: the statistic, the mechanism reasoning, a correlation-vs-causation verdict, and an explicit confidence with its reason. Numbers here supersede the earlier 100-row-sample version.*

### Correlation tiers (by |Pearson r|)
| Tier | Threshold | # pairs | Note |
|---|---|---|---|
| **HIGH** | \|r\| ≥ 0.60 | **149** | mostly definitional/redundant — same construct twice |
| **MEDIUM** | 0.40–0.60 | **424** | the **most informative** band |
| **LOW** | 0.20–0.40 | **1,471** | weak; hypotheses only |
| negligible | < 0.20 | 3,312 | no usable linear signal |

**Sample vs full data:** the 100-row sample reported **341** HIGH pairs; the full data has only **149**. Small non-representative samples *manufacture* high correlations — the national data is both more robust and more conservative.

### ⚠️ Most HIGH correlations are still definitional (not findings)
anaemia-all-women ~ anaemia-non-pregnant (≈1.0), BP component ⊂ BP aggregate, institutional birth ~ skilled attendance, the two "fully vaccinated" bases — these are the same phenomenon measured twice. The trustworthy signal is in **MEDIUM**.

### Curated substantive relationships — national, with confidence
| Relationship | r | n | Verdict | Confidence (why) |
|---|---|---|---|---|
| Schooling → **menstrual-hygiene use** | **+0.71** | 706 | Causal-plausible | **HIGH** — robust, direct mechanism |
| Female 10+yr schooling → **child marriage <18** | **−0.65** | 706 | Causal-plausible | **HIGH** — robust, well-established |
| Women overweight → **high blood sugar** | **+0.62** | 706 | Causal (biological) | **HIGH** — robust at scale |
| ANC 4+ → **institutional birth** | **+0.60** | 706 | Causal-plausible (shared care-seeking) | **HIGH** |
| Women overweight → **high blood pressure** | **+0.57** | 706 | Causal (biological) | **HIGH** |
| Improved sanitation → **child stunting** | **−0.51** | 706 | Causal-plausible, **heavily SES-confounded** | **HIGH assoc / LOW-MED causal** — see partial corr below |
| Clean cooking fuel → **child stunting** | **−0.42** | 706 | Causal + SES proxy | **MEDIUM** |
| Diarrhoea prevalence → **stunting** | **+0.23** | 706 | Mediator (weaker than sample's 0.38) | **LOW-MED** |

### The partial-correlation reality check (correlation ≠ causation)
`sanitation ~ stunting` raw **−0.51**, but controlling for schooling + clean fuel + electricity it drops to **−0.25** — **~50% of the apparent link is confounding (shared wealth)**. The sample suggested only ~27% was confounding; the national data shows the confounding is *larger*. This is precisely the gap the causal models (PC/Bayesian-net/matching) must close.

### High-confidence NULL (defies intuition — and matters)
**Female literacy → modern contraception: r = +0.09 (n=706).** Technically p≈0.02 (large n makes tiny effects "significant"), but the effect is **negligible** — contraception is sterilisation-dominated and decoupled from literacy. *This is why we rank on effect size, not p-values.* High confidence the relationship is practically null.

### A phantom correlation that the full data destroyed
`sanitation ~ alcohol`: **+0.60 in the 100-row sample → −0.01 nationally (p=0.84).** The sample's strong "link" was a pure regional/sampling artifact (a few Northeast districts). **Lesson: never trust a bivariate correlation from a non-representative slice** — it can invent relationships that do not exist. This single example is the strongest argument for the full-data, partial-correlation, FDR-controlled workflow in the next section.

### Confidence rubric (auditable)
**Confidence = Statistical robustness × Causal interpretability.** Statistical ↑ with larger \|r\|, larger n, tight CI, Pearson≈Spearman, no small-sample cells. Causal ↑ with a known mechanism, low confounding, identifiable direction; ↓ for mediators, definitional pairs, or SES/region-confounded pairs. *A confident correlation (sanitation↔stunting) can still be a low-confidence causal claim — keep the two separate.*

> All 5,356 pairs with r/ρ/n/p available on request; key pairs reproducible from the cleaned national NFHS table.
