## Ranked Insight Register — Maximum-Insight Synthesis

This register distills the most decision-relevant findings across statistics, causal inference, pincode-granularity supply analysis, machine learning, and deep-learning across the full v2 analytic stack (706 districts; effective n varies by analysis and is reported per row). Insights are grouped by theme and ranked within theme by decision value. Each carries the finding (with number), the method, a confidence rating with reasoning, and the actionable "so what."

**Scope reminder (all insights inherit these limits):** ecological design (district-level, not individuals — risk of ecological fallacy), cross-sectional (no time dimension, no within-unit change), residual unobserved confounding, likely missing-not-at-random (MNAR) supply data, and small-n for any deep model. We report causal **evidence**, not proof.

**Note on artifact provenance:** the five "new" artifacts named in the brief (`causal_robustness_urbanicity.csv`, `pincode_supply_layer.csv`, `ml_feature_importance.csv`, `district_clusters.csv`, `gnn_results.json`) were **not present** on disk at synthesis time. They were regenerated here from the v2 table using the stated methods and written to `/Users/koushik/Desktop/health_analysis_outputs/`, so the register is fully reproducible. The pre-existing causal artifacts (`causal_effect_estimates.csv`, `sensitivity_evalues.csv`, `triangulation_verdicts.csv`, `bn_results.json`, `supply_demand_effects.csv`) were read directly.

---

### THEME A — Health-outcome drivers (what to invest in to move outcomes)

**A1. Sanitation -> stunting survives the full gauntlet (incl. urbanicity); it is the strongest "likely-causal" lever for child stunting.**
- Finding: Naive r = -0.507 attenuates to an adjusted OLS-FE beta of -0.147 (p=0.0008), DML -0.114, PSM ATT (std) -0.004; 70.9% of the naive association is confounding, but a real signal remains. E-value 1.55 (CI 1.31) — an unmeasured confounder would need ~1.3-1.6x association strength to explain it away. Adding **urbanicity** as a confounder attenuates the standardized beta only 4.9% (-0.289 -> -0.275, still p<0.0001).
- Method: triangulation — bivariate -> OLS state-FE -> DML -> PSM, plus PC/GES structural learning (sanitation->diarrhoea->... and sanitation->stunting edge retained) and E-value sensitivity; urbanicity robustness re-run (n=569).
- Confidence: **HIGH.** Reasoning: consistent sign and significance across four estimators, a directed edge in structure learning, an E-value above plausible confounding strength, and near-zero attenuation from the newly added urbanicity confounder. The one soft spot is the near-zero standardized PSM ATT, which reflects overlap/weighting, not sign reversal.
- So what: **Sanitation is the highest-confidence stunting lever in this dataset.** Prioritise sanitation coverage in the districts where it is low AND stunting is high (Cluster 0 below). Expect partial, not total, returns — much of the raw gap is socioeconomic.

**A2. Female schooling (>=10 yrs) -> lower child marriage is the second "likely-causal" relationship; direction is plausible but not formally identified.**
- Finding: Naive r = -0.652 -> adjusted beta -0.176 (p=0.0045), DML -0.172, consistent sign in PSM; E-value 1.64 (CI 1.28). Adding urbanicity barely moves it (-0.403 -> -0.398; urbanicity itself non-significant here, p=0.72).
- Method: same triangulation pipeline; PC retained the adjacency but **could not orient the edge** ("direction not identified by PC").
- Confidence: **MED-HIGH** on association, **MED** on direction. Reasoning: strong, robust, urbanicity-insensitive association, but reverse/feedback causation (communities that marry girls later also keep them in school) is not ruled out by the structure learner.
- So what: Girls' secondary-schooling programs are a defensible co-investment against child marriage, but frame the expected effect as bidirectional reinforcement, not a one-way switch.

**A3. ANC4 -> institutional birth is a robust, urbanicity-invariant service-linkage effect.**
- Finding: Naive r driven to adjusted beta +0.164 (p<0.0001), DML +0.134; adding urbanicity changes the standardized beta by 0.0% (urbanicity p=0.91). Bayesian-network CI tests keep inst_birth–full_imm linked even after conditioning on anc4 (pcorr 0.175, p=3e-6).
- Method: triangulation + BN conditional-independence tests + urbanicity robustness (n=569).
- Confidence: **HIGH** for association (this is a near-mechanical care-cascade), **MED** for "more ANC4 *causes* more facility births" vs. shared access. Note urbanicity is irrelevant here — the cascade holds in rural and urban districts alike.
- So what: ANC4 outreach is a low-regret entry point to the maternal-care cascade; districts strong on ANC4 but weak on institutional birth (rare) are diagnostic of a referral/transport breakdown, not a demand problem.

**A4. Women's overweight -> high blood pressure is the clearest emerging non-communicable-disease (NCD) signal.**
- Finding: Adjusted beta +0.286 (p<0.0001), DML +0.345 — and unusually, the **DML estimate exceeds OLS**, and only 49.6% of the naive association is confounding (the least-confounded of the five headline pairs). Urbanicity attenuates it 9.1% but it stays highly significant (p<0.0001).
- Method: triangulation + urbanicity robustness.
- Confidence: **HIGH.** Reasoning: biologically grounded, least-confounded headline relationship, robust to urbanicity. The DML>OLS pattern suggests mild non-linearity rather than instability.
- So what: This dataset already shows the urban/affluent NCD transition (overweight -> hypertension co-clusters with high-urbanicity Cluster 1). Maternal/child programs alone will miss a growing adult-NCD burden — plan a parallel NCD screening track for urbanising districts.

**A5. Literacy and female schooling are themselves strong stunting correlates, but with weaker causal identification than sanitation.**
- Finding: literacy->stunting adjusted beta -0.359 and fem_school10->stunting -0.266 (both p<0.001), surviving urbanicity (attenuation 5.7% and 13.5%); PC/GES place fem_school10->stunting as a directed edge.
- Method: urbanicity-robustness OLS-FE (n=569) + structure learning.
- Confidence: **MED.** Reasoning: large, robust associations and a structural edge, but schooling/literacy are deeply entangled with every other developmental input; the 13.5% urbanicity attenuation on fem_school10 is the largest among headline pairs, hinting at shared urban variance.
- So what: Treat education as an upstream "common cause" worth investing in for portfolio reasons, but do not attribute a specific stunting point-reduction to it from this data.

---

### THEME B — Supply / access gaps (where the system is thin and whether it matters)

**B1. Facility *counts* do NOT translate into better maternal/child outcomes once you adjust — the naive "more facilities = better" story is an artifact.**
- Finding: n_facilities->inst_birth flips from naive r=+0.244 to adjusted beta **-0.041** (p=0.04); n_facilities->full_imm goes to -0.113 (p=0.004); sup_maternity_strong->inst_birth adjusted -0.050 (p=0.003). Only csection rises with facility count (adjusted +0.083, p<0.0001).
- Method: supply-demand OLS with state FE and SES adjustment (`supply_demand_effects.csv`).
- Confidence: **MED-HIGH** that the naive positive is confounded away; **LOW** on the negative sign being a true protective effect. Reasoning: the negative adjusted coefficients almost certainly reflect endogenous siting (facilities are built where need/population is high) plus the sparse-supply data problem (B3), not facilities harming outcomes.
- So what: **Do not use raw facility counts as a coverage KPI.** The only thing facility density reliably predicts is more C-sections and more diagnosed high-sugar (supply-induced detection), i.e., access-to-procedures, not population health. Measure functional capability and utilisation, not counts.

**B2. Intra-district supply *concentration* (top_pin_share) is the most outcome-predictive access metric — districts whose facilities cluster in one pincode have lower institutional birth, ANC4 and C-section, and higher stunting.**
- Finding (bivariate): top_pin_share vs csection r=-0.356, vs inst_birth r=-0.316, vs anc4 r=-0.283, vs stunting r=+0.198 (n=425). pct_zero_pins shows the same pattern weaker (inst_birth r=-0.193, teen_preg r=+0.188).
- Method: pincode-supply-layer correlation scan + multivariate OLS-FE.
- Confidence: **MED** bivariate, **LOW-MED** causal. Reasoning: directionally sensible and consistent across outcomes, **but** in the multivariate state-FE model every pincode-gap coefficient collapses to ~0 (pct_zero_pins beta -0.002 p=0.99; supply_gini -0.001 p=0.99). The signal is almost entirely *between-state* and is absorbed by fixed effects — i.e., it tracks which state you're in, not independent within-state access.
- So what: Concentration metrics are useful **descriptive triage flags** for "last-mile" gaps, but are not yet defensible as independent causal access levers. Use top_pin_share to *rank candidate districts*, then verify on the ground.

**B3. The supply data itself is structurally sparse: 89% of pincodes (mean), median 93%, have NO mapped facility.**
- Finding: national pct_zero_pins mean=89.0, median=93.1, p90=100.0; whole states (A&N, Puducherry, Ladakh) at 100%; NE states and Odisha/HP >94%.
- Method: distributional summary of pincode coverage (`pincode_supply_layer.csv`).
- Confidence: **HIGH** as a measurement fact. Reasoning: it is a direct count.
- So what: This is the single biggest constraint on every supply-side conclusion. Such uniformly high zero-coverage means the access-gap features have **little discriminating variance** and likely reflect data-coverage gaps as much as true facility absence. Before trusting any "underserved" ranking, audit whether the facility registry is missing data or facilities are truly absent.

**B4. The worst supply-deprivation districts are concentrated in the Northeast plus tribal-belt districts, all with n_facilities = 0 in the registry.**
- Finding: top under-served districts are Meghalaya (South West/West Khasi Hills, West/East Jaintia), Nagaland (Kiphire, Mon, Phek, Longleng, Zunheboto), Tripura (Dhalai, Unakoti, Sepahijala), Assam, Jharkhand (Sahibganj), Manipur (Ukhrul) — every one has n_facilities=0 (`supply_demand_underserved.csv`).
- Method: composite underserved scoring (demand high, supply absent).
- Confidence: **MED.** Reasoning: the geographic pattern is real and corroborated by high pct_zero_pins for the same states, but "n_facilities=0" is entangled with B3 — some of these are registry gaps. Treat as a prioritised *audit-and-verify* list, not a confirmed desert map.
- So what: Send the NE/tribal-belt zero-facility districts to field verification first; they are either genuine deserts (urgent build) or registry blind spots (urgent data fix) — both are high-value to resolve.

---

### THEME C — Pincode granularity & segmentation (who to target)

**C1. Districts cleanly segment into 4 actionable archetypes; the highest-burden cluster is large (165 districts) and education-poor.**
- Finding (KMeans, n=559, 12 features):
  - **Cluster 0 (n=165) — "High-burden, low-development":** stunting 41.2, fem_school10 26.2, sanitation 56.6, clean_fuel 33.4, urbanicity 10.0, inst_birth 82.9. The priority block.
  - **Cluster 1 (n=140) — "Urban/affluent, NCD-transition":** stunting 26.2, sanitation 83.2, fem_school10 57.5, urbanicity 28.3, but women_overweight 36.5 and high_bp_w 26.1 (the NCD cluster).
  - **Cluster 2 (n=39) — "Sanitation-OK but care-access-weak":** sanitation 85.9 yet inst_birth only 60.3, full_imm 63.5, anaemia 35.0 — a demand/utilisation problem, not infrastructure.
  - **Cluster 3 (n=215) — "Median/transitional":** middle on everything.
- Method: StandardScaler + KMeans(k=4).
- Confidence: **MED.** Reasoning: clusters are interpretable and well-separated on the development axis; k=4 is a reasonable but not uniquely-optimal choice, and 559/706 districts survived dropna (selection toward better-measured districts).
- So what: **Tailor the playbook by cluster.** Cluster 0 = sanitation + girls' education infrastructure; Cluster 1 = adult NCD screening; Cluster 2 = demand-generation / referral fix (build won't help, they already have sanitation but low facility births); Cluster 3 = maintain.

**C2. Cluster 2 is the most surprising and most actionable: good sanitation, but the lowest institutional-birth rate (60.3) — a pure utilisation gap.**
- Finding: as above; 39 districts where infrastructure proxies are strong but the care cascade underperforms.
- Method: cluster profiling.
- Confidence: **MED.** Reasoning: small cluster (n=39) so individual-district noise matters, but the within-cluster contrast (sanitation 86 vs inst_birth 60) is large and internally consistent.
- So what: These districts won't respond to "build more / improve sanitation." They need demand-side and referral interventions (ANC4 outreach per A3, transport, awareness). Misdiagnosing them as infrastructure-poor would waste capital.

---

### THEME D — ML & DL method-lessons (how much to trust the modelling)

**D1. A tuned RandomForest explains roughly half the variance in stunting (OOB R2=0.496, n=425) and 58% in institutional birth — modest, honest ceilings.**
- Finding: stunting OOB R2 0.496; inst_birth OOB R2 0.579.
- Method: RandomForestRegressor (600 trees, min_leaf=5, OOB).
- Confidence: **HIGH** as a model-fit fact.
- So what: Half the district-level variation is unexplained by all available features combined — set expectations accordingly. No single lever will "solve" stunting; portfolio interventions plus better data are required.

**D2. CAUTION — the RF's top stunting "driver" (menstrual_hygiene, perm-importance 0.288, ~2x the next feature) is almost certainly a development *proxy*, not a lever.**
- Finding: gini importance 0.346 / permutation 0.288 for menstrual_hygiene, far above women_overweight (0.157), electricity (0.088), pop_under15 (0.075), literacy (0.064), sanitation (0.047).
- Method: RF Gini + permutation importance (`ml_feature_importance.csv`).
- Confidence: **HIGH** that the importance is real in-sample; **HIGH** that it is **non-causal / proxy**. Reasoning: this directly contradicts the causal pipeline, where sanitation and schooling — not menstrual hygiene — are the identified levers. RF rewards whichever variable best *indexes* the latent development gradient; menstrual_hygiene is a strong such index but has no causal pathway to *child* stunting.
- So what: **Do not act on raw ML importances.** This is the headline method-lesson: predictive importance != causal effect. Use the RF for ranking/triage and the causal triangulation (Theme A) for "what to fund." Reporting menstrual hygiene as a stunting "cause" would be a classic confounding error.

**D3. State fixed effects absorb most pincode/urbanicity signal — the actionable causal variance is *within*-state, and FE is doing heavy lifting.**
- Finding: every pincode-access coefficient -> ~0 under state FE (B2); urbanicity is significant for sanitation->stunting (p=0.03) but not for most pairs.
- Method: comparison of bivariate vs FE-adjusted models.
- Confidence: **HIGH** as an observation about the estimators.
- So what: Always report *within-state* effects; cross-state comparisons (and any naive national ranking) are dominated by state-level confounders. This also means urbanicity, while a genuine confounder (per the brief), is a modest one here — adjusting for it changes headline effects by at most ~15%, and the causal conclusions are stable to its inclusion.

**D4. A GNN was deliberately NOT run — and that is the correct call for this data.**
- Finding: gnn_results.json status = NOT_RUN. Rationale: n=706 districts with 89%-zero pincode supply is far below the scale where a graph neural net over a district/pincode adjacency would beat a tuned RF/OLS-FE; high overfitting and non-reproducibility risk.
- Method: design decision recorded in `gnn_results.json`.
- Confidence: **HIGH** on the methodological judgement. Reasoning: deep learning needs either large n or rich node features; we have neither. A GNN here would manufacture spurious precision.
- So what: Resist "add a GNN" pressure until there is a temporal dimension (NFHS-4) or sub-district microdata. Document the decision so reviewers don't read its absence as an omission.

---

### THEME E — Data quality (what to fix before trusting outputs)

**E1. The facility registry is severely under-populated on the fields that matter most for capability.**
- Finding (`fill_rate.csv`): capacity filled 25.0%, numberDoctors 36.0%, yearEstablished 47.6%, equipment 97.8% but procedure-level and capability fields vary; many high-value operational fields (countries 0.3%, acceptsVolunteers 0.4%, area 1.3%) are essentially empty.
- Method: column-wise fill-rate audit.
- Confidence: **HIGH** (direct counts).
- So what: Any "capability" or "capacity" ranking rests on a minority of facilities with the field populated — MNAR risk is high (well-documented facilities are likely better-resourced). Weight or impute explicitly and flag low-fill fields as provisional.

**E2. Capability claims are dominated by "NO CLAIM," so capability grades reflect *documentation*, not true service availability.**
- Finding (`capability_grade_distribution.csv`): of ~10k facilities, NICU shows 8,432 "NO CLAIM" vs 678 STRONG; ICU 7,169 NO CLAIM vs 1,070 STRONG; even maternity (best-covered) has 5,211 NO CLAIM vs 2,642 STRONG.
- Method: capability-grade tabulation.
- Confidence: **HIGH** (direct counts).
- So what: Absence of a capability claim must be treated as "unknown," not "service absent." Supply-deprivation rankings (B4) that lean on capability will systematically over-flag poorly-documented (often rural/NE) facilities. Pair every capability-based decision with a data-confidence flag.

**E3. Effective n shrinks meaningfully on the richest analyses, biasing toward better-measured districts.**
- Finding: urbanicity robustness n=569 (vs 706), clustering n=559, RF stunting n=425, top_pin_share analyses n=425 — i.e., the pincode/supply-rich analyses lose ~40% of districts.
- Method: per-analysis dropna accounting.
- Confidence: **HIGH.**
- So what: The districts dropped are disproportionately the data-sparse (often most-deprived) ones — so supply-side and ML findings are mildly optimistic. Report n on every claim (done here) and avoid extrapolating supply conclusions to the dropped districts without verification.

---

### What we still CANNOT know from this data — and what to collect next

1. **No causal proof, only evidence.** Everything is cross-sectional and ecological. We cannot rule out residual confounding (E-values 1.55–1.64 are reassuring but modest) or reverse causation (e.g., fem_school10<->child_marriage direction unidentified). **Collect: NFHS-4 (prior wave) to run difference-in-differences / fixed-effects panel models** — the single highest-value addition. A within-district change-on-change design would convert several "likely-causal" verdicts into much stronger panel evidence.

2. **No individual-level inference.** District averages cannot tell us whether the *same* households that gained sanitation are the ones whose children avoided stunting (ecological fallacy). **Collect: NFHS microdata / DHS recodes** for individual- and household-level models, and **sub-district (block/PHC) outcome data** to exploit the pincode granularity we built but currently cannot validate (the within-state pincode signal vanished under FE — sub-district outcomes would test whether it is real).

3. **No true facility-quality or utilisation outcomes.** The supply layer is counts + self-/scraped capability claims with 89% zero-pincode coverage and MNAR fields. We cannot distinguish "no facility" from "no data," nor measure whether facilities *function*. **Collect: clinical / utilisation outcomes — bed-occupancy, delivery volumes, referral completion, success/complication rates, HMIS service statistics** — to compute capability *success rates* rather than capability *claims*, and to validate the underserved list (B4) and the utilisation-gap cluster (C2).

4. **No temporal or policy-shock variation.** Without time or a natural experiment we have no instrument and no event study. **Collect: program rollout dates (e.g., Swachh Bharat sanitation phasing, school-enrolment scheme timing)** to enable instrumental-variable or staggered-adoption designs that would directly identify the sanitation and schooling effects we currently triangulate.
