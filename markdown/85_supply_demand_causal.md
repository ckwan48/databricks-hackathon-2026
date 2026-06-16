## Supply → Demand: Do Health Facilities Drive Maternal & Child Service Uptake?

This section tests whether **district health-facility SUPPLY** (counts scraped from facility web data) is associated with **DEMAND-side service utilisation outcomes** — institutional birth rate (`inst_birth`), full child immunisation (`full_imm`), and caesarean rate (`csection`). Supply treatments: `n_facilities`, `n_hospital`, `sup_maternity_strong` (count of facilities flagged as having strong maternity capability). All three supply counts are heavily right-skewed (mean 9.3 facilities, max 330; 281 of 706 districts have **zero** scraped facilities), so they are entered as `log1p(count)`.

For every treatment→outcome pair we report (1) a **naive** Pearson correlation / OLS slope, and (2) a **confounder-adjusted** estimate controlling for `pop_under15`, `fem_school10`, `sanitation` **plus state fixed effects** (`C(state)`), with HC1 robust standard errors. n is reported per analysis (complete cases). Artifact: `/Users/koushik/Desktop/health_analysis_outputs/supply_demand_effects.csv`. Figure: `/Users/koushik/Downloads/DAS_HACK/figures/supply_demand_causal.png`.

### Headline: naive associations are positive, but they largely COLLAPSE or FLIP under adjustment

| Treatment | Outcome | n | Naive r | Naive slope (per log-unit) | Adj. slope (per SD log-supply) | Adj. 95% CI | Adj. β (std) | Adj. p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| n_facilities | inst_birth | 706 | **0.244** | +2.24 | **−0.50** | [−0.97, −0.02] | −0.041 | 0.042 |
| n_facilities | full_imm | 693 | 0.041 (ns) | +0.38 | **−1.36** | [−2.30, −0.43] | −0.113 | 0.004 |
| n_facilities | csection | 706 | **0.249** | +3.05 | **+1.33** | [+0.67, +1.99] | +0.083 | <0.001 |
| n_hospital | inst_birth | 706 | 0.256 | +2.71 | −0.40 (ns) | [−0.87, +0.07] | −0.033 | 0.097 |
| n_hospital | full_imm | 693 | 0.047 (ns) | +0.50 | **−1.22** | [−2.16, −0.27] | −0.101 | 0.011 |
| n_hospital | csection | 706 | **0.256** | +3.60 | **+1.35** | [+0.70, +2.00] | +0.085 | <0.001 |
| sup_maternity_strong | inst_birth | 706 | 0.259 | +3.27 | **−0.60** | [−1.00, −0.20] | −0.050 | 0.003 |
| sup_maternity_strong | full_imm | 693 | 0.026 (ns) | +0.33 | **−1.46** | [−2.35, −0.56] | −0.121 | 0.001 |
| sup_maternity_strong | csection | 706 | **0.249** | +4.20 | **+1.16** | [+0.60, +1.72] | +0.073 | <0.001 |

**How to read the effect sizes.** Naive slopes are per one log-unit of supply (~e-fold more facilities); adjusted slopes are **outcome percentage-points per +1 SD of log-supply**; β (std) is the fully standardised partial coefficient (comparable across rows).

Three patterns emerge:

1. **Institutional birth & full immunisation: the naive "more facilities → more uptake" story does not survive.** Raw correlations of supply with `inst_birth` are positive and significant (r ≈ 0.24–0.26), but once we hold population structure, female schooling, sanitation and **state** constant, the adjusted coefficient **shrinks to near-zero and even turns mildly negative** (e.g. n_facilities → inst_birth: +2.24 naive becomes −0.50 adjusted; β = −0.04). For `full_imm` the naive correlation is already null (r ≈ 0.03–0.05, ns) and the adjusted estimate is **negative** (β ≈ −0.10 to −0.12). Interpretation: districts with more scraped facilities tend to have higher schooling/sanitation/urbanisation, and those confounders — not facility counts — track service uptake. After conditioning, extra **scraped** facilities buy essentially **no additional** institutional-birth or immunisation uptake, and within-state the sign is, if anything, slightly negative (consistent with facilities clustering where private demand, not public health need, is highest).

2. **Caesarean rate is the one outcome robustly, positively tied to supply** — both naive (slope +3.0 to +4.2) **and** adjusted (+1.16 to +1.35 pp per SD log-supply; β ≈ +0.07–0.09; all p < 0.001). More facilities (especially hospitals and strong-maternity facilities) predict **higher C-section rates** even within the same state and after controls. This is the most internally consistent signal and is plausible: surgical-capable supply enables (and, via private-sector incentives, may over-supply) caesarean delivery. It is **not** evidence of better outcomes — high C-section is widely a marker of over-medicalisation, not unmet need.

3. **The sign-flip itself is diagnostic of confounding / reverse causation** (see panel A of the figure: the positive naive trend is driven by high-supply urban districts that already had near-100% institutional birth).

### Most UNDER-served vs OVER-served districts (n = 706)

We built a **need index** (z-score of: low `inst_birth` + high `teen_preg`) and a **supply index** (z of log `n_facilities`); under-served = high need / low supply, over-served = high supply / low need (figure panel B). Rankings saved to `supply_demand_underserved.csv` and `supply_demand_overserved.csv`.

**Most UNDER-served (high demand pressure, zero/low scraped supply)** — every one of the top 15 has **0 scraped facilities** (median inst_birth = 42.2%):
- **Meghalaya:** South West / West Khasi Hills (inst_birth ≈ 41.7%, teen_preg ≈ 13%), West & East Jaintia Hills.
- **Nagaland:** Kiphire, Mon, Phek, Longleng, Zunheboto (inst_birth 21–39%).
- **Assam** South Salmara Mancachar, **Jharkhand** Sahibganj, **Tripura** Unakoti/Dhalai/Sepahijala, **Manipur** Ukhrul.

**Most OVER-served (very high scraped supply, low residual need)** — all are **major metros** (median n_facilities = 106, median inst_birth = 97.5%):
- **Chennai** (269 facilities), **Hyderabad** (212), **Jaipur** (187), **Ahmadabad** (330), **Ernakulam** (106), **Kolkata** (183), **Surat** (161), **Lucknow** (147), plus Rajkot, Varanasi, Thrissur, Ludhiana, Bhopal, Dehradun.

The near-perfect rural-Northeast-vs-metro split is exactly what the visibility-bias caveat predicts (below) — so this map is **at least as much a map of where the web data can see facilities as a map of where facilities actually are.**

### CRITICAL CAVEATS — read this as SUGGESTIVE evidence, NOT causal proof

- **Web-SCRAPED supply ⇒ severe VISIBILITY BIAS.** Counts come from facility web data: urban and private facilities (which maintain online listings, directories, map presence) are **over-counted**; rural and public facilities are **under-counted or invisible**. 281/706 districts show **zero** facilities — implausible as true absence, almost certainly missing-not-at-random visibility. This bias **alone** can manufacture the metro-over-served / rural-under-served pattern and the positive naive correlations.
- **REVERSE CAUSATION.** Facilities (and especially private ones) **locate where demand and ability-to-pay already exist**. So a supply→uptake arrow is confounded by an uptake/wealth→supply arrow; the cross-sectional data cannot separate them.
- **ECOLOGICAL (district-level) effects.** These are **district averages, not individuals** — associations may not hold for any person (ecological fallacy).
- **CROSS-SECTIONAL, no temporal precedence** — we cannot establish that supply *preceded* uptake.
- **Unobserved confounding** — no income, caste, or wealth controls; the adjusted models lean on state FE + schooling/sanitation as proxies, which is incomplete.
- **MNAR suppression** in both the health indicators and the facility scrape.

Net: the most defensible reading is that **scraped facility counts do not independently raise institutional-birth or immunisation uptake once development confounders and state are controlled, that they track higher C-section rates, and that the under/over-served ranking primarily reflects data visibility (metro vs rural Northeast).** Treat the under-served list as a hypothesis-generating flag for districts needing **ground-truth supply verification**, not as a settled needs assessment.
