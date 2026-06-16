## 9A. The Solution: Unified Answer Engine + Complete Insight Register

**Scope.** This capstone ties every prior method (descriptive stats, correlation, causal inference, statistical/penalized ML, tree ensembles, geometric DL, multilevel shrinkage, pincode-granularity supply, and the facility-evidence trust layer) into ONE answering system. It is built on the v2 causal analytic table (706 districts; 569 with recovered geo-centroids), the 10,077-facility capability corpus (70,616 facility-capability rows), and the pincode supply layer. It supersedes the earlier interim register (Part B).

**Standing guardrails.** All district-level findings are **ecological and cross-sectional** (single NFHS-5 wave). Effects are associational unless explicitly triangulated; "causal" verdicts are design-based, not experimental. Geo-DL is exploratory at n=569. Facility "capability" = evidence of a *claim*, not a verified clinical success rate.

---

### PART A — THE ANSWER ENGINE (router: question type -> method -> artifact -> confidence-rated, evidence-attached answer)

The engine is a router. Each incoming question is classified into one of six TYPES; each TYPE binds to a method, a backing artifact, and a confidence rule. Every answer returns five fields: **answer / evidence / confidence / method / caveat.**

| # | Question type | Method | Backing artifact(s) | Confidence is driven by |
|---|---|---|---|---|
| R1 | "Can facility X do Y?" | Capability trust grade + evidence-tier confidence score | `facility_capability_confidence.csv` | trust_score (0-3), # evidence types, # distinct sources, contradiction_flag |
| R2 | "Is the care gap in Z real?" | Trust-weighted gap (real vs data-poor) + pincode deserts | `region_capability_gaps.csv`, `pincode_supply_layer.csv` | fill_rate (data completeness) separates APPARENT CARE GAP from DATA-POOR |
| R3 | "Where should a patient go for need N near L?" | Evidence + haversine-distance ranking | `facility_search.py` (+ confidence file) | grade of returned facilities + distance + candidate density |
| R4 | "Why is O high/low? / What if we change T?" | Causal triangulation (OLS+DML+PSM+PC/BN+E-value) over a DAG | `causal_effect_estimates.csv`, `causal_robustness_urbanicity.csv`, `triangulation_verdicts.csv`, `sensitivity_evalues.csv` | survives adjustment? E-value vs plausible confounding; PC direction identified? |
| R5 | "Estimate O for a data-poor district" | Ensemble prediction + hierarchical (state) shrinkage fallback | `ensemble_leaderboard.csv`, `multilevel_shrinkage.csv` | CV R², λ (state-borrowing weight), within-state SD as the band |
| R6 | "Spatial / neighbourhood trend?" | Geometric DL (GNN) + Moran's I + pincode granularity | `gnn_geometric_results.json`, `spatial_regions.csv`, `pincode_supply_layer.csv` | does spatial graph beat non-spatial baseline? Moran's I significance |

**Confidence rubric (applies to every answer):**
- **HIGH** — triangulated/replicated across ≥2 independent methods, survives confounder adjustment or carries strong evidence tier (trust=3, multi-source), large n.
- **MED** — single robust method, or weakened-but-holds after adjustment, or moderate evidence tier.
- **LOW** — exploratory, model-does-not-beat-baseline, data-poor region, single source, or direction not identified.

#### Five worked examples (EASY -> HARD)

**Q1 (EASY, R1): "Can Government Medical College, Thiruvananthapuram do maternity / obstetrics?"**
- **Answer:** Yes — graded **STRONG**, confidence **85/100 (VERY HIGH)**.
- **Evidence:** trust_score 3/3; 3 evidence types across 3 distinct source types; snippet "specialty=gynecologyandobstetrics, reproductiveendocrinologyandinfertility || procedure~assisted reproductive technology / IVF…"; no contradiction flag.
- **Confidence:** HIGH. **Method:** capability trust grade + evidence-tier scorer (`facility_capability_confidence.csv`).
- **Caveat:** Confirms a *documented claim* of capability, not a measured delivery success rate or current bed availability.

**Q2 (EASY-MED, R3): "Where should a patient go for dialysis near Jaipur?"**
- **Answer:** Top STRONG-grade option **KKS Urology & General Hospital, Jaipur (2.8 km)**; 4 more STRONG facilities within 5 km (Indus, Soni, Vaishali, NAV Imperial).
- **Evidence:** 36 candidates within 50 km, 2,086 nationwide with ≥PARTIAL evidence; each return ships phone, website and the matched evidence snippet (e.g. Soni: "CRRT equipment for renal replacement therapy; hemodialysis…").
- **Confidence:** HIGH for the ranked shortlist (all STRONG, geocoded, near). **Method:** `facility_search.py` evidence+distance ranking.
- **Caveat:** Distance uses recovered centroids; call ahead — capability is claim-based, not a live-capacity feed.

**Q3 (MED, R2): "Is the dialysis care gap in Jamnagar real?"**
- **Answer:** **Likely a REAL gap, not a data artifact.** Jamnagar has 20 facilities catalogued (fill_rate 0.97 — well-documented) yet **0 STRONG/PARTIAL dialysis claims** -> weighted_score 0.0 -> classified **APPARENT CARE GAP**. (Same pattern: Deoghar oncology, 13 facilities; Faridkot dialysis, 10 facilities.)
- **Evidence:** `region_capability_gaps.csv`. The classifier separates **APPARENT CARE GAP (718 region-capability cells: documented but no strong supply)** from **DATA-POOR (2,345 cells: thin documentation)** using fill_rate, so this is not just missing data.
- **Confidence:** MED. **Method:** trust-weighted region gap classifier.
- **Caveat:** Absence-of-evidence ≠ evidence-of-absence; a dialysis unit may exist but never surfaced a web/registry claim. Verify before acting.

**Q4 (HARD, R4): "Why is stunting high, and what if we improve sanitation?"**
- **Answer:** Sanitation is a **likely-causal** lever. Naive bivariate slope −0.507 collapses **70.9%** to −0.147 after adjustment (DML −0.114; PSM ATT std −0.004). Adding urbanicity barely moves it (−0.112 -> −0.120, "Survives"). BN do-operator: P(high stunting) falls **0.57 -> 0.20** moving low->high sanitation tercile (vs 0.43 crude diff shrinking to 0.185 adjusted). Verdict: **LIKELY-CAUSAL** (E-value 1.55, CI-bound 1.31).
- **Evidence:** `causal_effect_estimates.csv`, `causal_robustness_urbanicity.csv`, `triangulation_verdicts.csv`, `sensitivity_evalues.csv`, `bn_results.json` (PC retained directed edge sanitation->stunting; sanitation->diarrhoea->stunting mediation visible).
- **Confidence:** MED-HIGH (4 methods agree on sign + significance; survives urbanicity; modest E-value means a confounder of RR≈1.55 could explain it away). **Method:** causal triangulation over the learned DAG.
- **Caveat:** Ecological + cross-sectional; the strongest stunting predictor in ML is actually **menstrual_hygiene/women_overweight (perm imp 0.29/0.16)**, not sanitation — sanitation is robust but not the largest mover. PSM ATT near zero warns the effect is sensitive to matching.

**Q5 (HARDEST, R5+R6): "Estimate stunting for a data-poor district and is there a neighbourhood trend?"**
- **Answer (estimate):** For a thin district the engine returns the **stacked ensemble** prediction (CV R² **0.50**, RMSE 6.13 — best of 5 models, beating DecisionTree 0.36) and falls back to the **multilevel state-shrunk** estimate with a calibrated band. Example: Muzaffarnagar (UP) raw 29.8 vs state mean 39.5 -> fitted_mlm **37.4** at λ=0.97 (state-dominated). **437 of 569 districts have λ>0.9**, i.e. they borrow mostly from the state mean. Report the estimate **±≈6 pp** (median within-state stunting SD 6.15; MLM residual SD 5.64).
- **Answer (spatial):** Neighbourhood structure is **real but not predictively useful here.** Moran's I is **+0.47 stunting, +0.59 sanitation, +0.68 schooling (all p<0.01)** — strong clustering. But the **best spatial GNN (GraphSAGE-geo R² 0.35) does NOT beat the non-spatial Ridge (0.39)**; over 5 seeds GraphSAGE 0.468±0.066 vs Ridge 0.422±0.084 — statistically indistinguishable at n_test≈115. GAT attention is diffuse (0.108) and only spikes within tiny Sikkim. Six contiguous health-regions (R1-R6) emerge.
- **Evidence:** `ensemble_leaderboard.csv`, `multilevel_shrinkage.csv`, `gnn_geometric_results.json`, `spatial_regions.csv`, GEO Moran's I.
- **Confidence:** MED for the ensemble/MLM estimate (good CV, honest band); LOW for any *spatial-DL* claim (does not beat baseline). **Method:** stacked ensemble + hierarchical shrinkage; geometric DL + Moran's I.
- **Caveat:** Spatial autocorrelation justifies geometric DL but n=569 + k-NN-on-centroids (no true shapefile adjacency) is too small to win; trust the simpler model and report the wider band.

---

### PART B — THE COMPLETE INSIGHT REGISTER (definitive, ranked; supersedes interim)

26 decision-relevant insights, grouped by theme. Each: **finding (with number) · method · confidence (+why) · so-what.**

#### Theme 1 — Causal inference (the action levers)

1. **Sanitation -> stunting is likely-causal: −0.507 naive collapses 70.9% to −0.147 adjusted (DML −0.114), survives urbanicity, E-value 1.55.** Method: OLS+DML+PSM+PC/BN+E-value triangulation. **Confidence: MED-HIGH** — 4 methods agree, survives adjustment, but E-value is modest and PSM-ATT≈0. **So-what:** sanitation is a defensible WASH investment lever for stunting, but pair it with the larger nutrition drivers below.

2. **BN do-operator: forcing low->high sanitation tercile drops P(high stunting) 0.57 -> 0.20 (do-adjusted), with full positivity coverage.** Method: discrete hill-climbing BN + back-door adjustment {fem_school10, pop_under15}. **Confidence: MED** — model-implied interventional contrast, positivity holds, but BN structure is sample-dependent. **So-what:** quantifies the *interventional* (not just observational) payoff of sanitation upgrades.

3. **Female schooling -> child marriage is likely-causal (naive −0.652 -> adj −0.176, 73% shrink; DML −0.172; E-value 1.64).** Method: triangulation; PC retained the edge but **could not orient direction.** **Confidence: MED** — strong magnitude/significance, but direction not identified (reverse causation / shared cause plausible). **So-what:** girls' secondary education is the single largest associational lever on child marriage — prioritize, while acknowledging bidirectionality.

4. **anc4 -> institutional birth is robust and positive (+0.599 naive -> +0.164 adj, DML +0.134, p<0.001), strengthens further under DML-with-urbanicity.** Method: triangulation. **Confidence: HIGH** — survives every adjustment, large n, consistent sign. **So-what:** antenatal-care outreach is a high-confidence pathway to institutional delivery; fund ANC4 programs.

5. **women_overweight -> high BP is the most adjustment-stable effect (+0.566 -> +0.286 adj, only 49.6% shrink, DML +0.345).** Method: triangulation. **Confidence: HIGH** — lowest shrinkage of all five pairs, biologically expected, survives urbanicity. **So-what:** the nutrition transition is already driving hypertension; NCD screening should follow rising overweight prevalence.

6. **clean_fuel -> stunting weakens after adjustment and loses significance under DML-with-urbanicity (p=0.095).** Method: triangulation; verdict "Weakened but holds." **Confidence: LOW-MED** — sign stable but fragile to urbanicity. **So-what:** treat clean-fuel as a *correlate of development*, not a standalone stunting lever — do not over-invest expecting stunting gains.

7. **Sanitation acts partly THROUGH diarrhoea: partial corr sanitation–stunting falls −0.504 -> −0.464 controlling diarrhoea, and sanitation->diarrhoea edge is retained.** Method: BN CI tests / mediation. **Confidence: MED.** **So-what:** part of sanitation's benefit routes through reduced diarrhoeal disease — WASH + diarrhoea management are complementary.

#### Theme 2 — Statistical ML & penalized regression (which features actually matter)

8. **For stunting, the dominant predictors are menstrual_hygiene (perm imp 0.288) and women_overweight (0.157) — NOT sanitation (0.047).** Method: RandomForest gini + permutation importance. **Confidence: MED** — consistent gini/perm ranking, but ecological. **So-what:** the highest-leverage stunting correlates are women's health/nutrition factors; broaden beyond WASH-only framing.

9. **Stacked ensemble is the best stunting model (CV R² 0.50, RMSE 6.13) and inst_birth (R² 0.55); a depth-4 tree alone manages only 0.36/0.39.** Method: 5-model leaderboard, CV. **Confidence: HIGH** — proper cross-validation, n=425. **So-what:** use the stack for data-poor imputation (Q5); the ~0.50 ceiling shows ~half the variance is unexplained by available features.

10. **LASSO/ElasticNet zero out clean_fuel, anc4, urbanicity, n_facilities for stunting; women_overweight (−2.54) and pop_under15 (+1.76) carry the largest standardized coefficients.** Method: penalized regression, standardized. **Confidence: MED.** **So-what:** parsimonious stunting model needs only ~6 features; supply/facility counts add nothing predictively.

11. **Stability selection (200 bootstraps): sanitation, electricity, women_overweight, pop_under15 select at 100% for stunting; clean_fuel (26.5%), anc4 (14.5%) are unstable.** Method: bootstrap selection frequency. **Confidence: HIGH for the robust set.** **So-what:** trust the always-selected features for policy; flag the unstable ones as wave-specific noise.

12. **Quantile regression: schooling and sanitation effects on stunting are LARGEST in the worst-off districts (τ=0.9: fem_school10 −3.62, sanitation −2.70 per SD) and persist at the median.** Method: quantile regression, standardized. **Confidence: MED.** **So-what:** these levers help the highest-stunting districts most — target them where the burden is worst (pro-equity).

13. **Urbanicity is NOT a significant stunting predictor at any quantile (τ=0.1/0.5/0.9 all p>0.35; OLS p=0.88).** Method: quantile + OLS. **Confidence: MED-HIGH.** **So-what:** rural-urban status per se does not explain stunting once schooling/sanitation are in — avoid urban-bias in targeting.

#### Theme 3 — Geometric DL & spatial structure

14. **Strong spatial autocorrelation exists (Moran's I +0.47 stunting, +0.59 sanitation, +0.68 schooling, all p<0.01).** Method: Moran's I on recovered centroids. **Confidence: HIGH.** **So-what:** outcomes cluster geographically — neighbour-aware targeting and spillover planning are justified.

15. **Despite the clustering, the spatial GNN does NOT beat the non-spatial baseline (GraphSAGE-geo R² 0.35 < Ridge 0.39; 5-seed 0.468±0.066 vs 0.422±0.084, indistinguishable).** Method: PyG GNNs vs Ridge/HistGBR, 5 seeds. **Confidence: HIGH (honest negative).** **So-what:** at n=569 with centroid k-NN, prefer the simple model; geometric DL is premature until shapefile adjacency + more waves arrive.

16. **GAT attention is diffuse (mean concentration 0.108) and only concentrates within tiny Sikkim's 3 districts.** Method: GAT attention extraction. **Confidence: MED.** **So-what:** no informative long-range spatial dependency was learned — confirms the GNN's lack of edge over tabular.

17. **Six contiguous health-regions (R1-R6, 48-129 districts each) emerge from spatial clustering with neighbour-mean stunting fields.** Method: spatial regionalization (`spatial_regions.csv`). **Confidence: MED.** **So-what:** gives a ready geographic stratification for regional program rollout and benchmarking.

18. **Four feature-based district archetypes (clusters 0-3; sizes 165/140/39/215) cross-cut states.** Method: k-means/clustering (`district_clusters.csv`). **Confidence: MED.** **So-what:** lets a state with a few districts borrow a playbook from same-archetype districts elsewhere.

#### Theme 4 — Hierarchical / small-area estimation

19. **437 of 569 districts have shrinkage λ>0.9 — their stunting estimate is state-dominated; mean fitted shift from raw is 4.4 pp.** Method: multilevel (random-intercept) shrinkage. **Confidence: HIGH.** **So-what:** most district point estimates are unstable on their own; report state-shrunk values with bands for planning, not raw district numbers.

20. **Calibrated uncertainty band for a data-poor district stunting estimate ≈ ±6 pp (within-state SD 6.15, MLM residual SD 5.64).** Method: MLM residuals + within-state dispersion. **Confidence: MED.** **So-what:** never quote a single-district estimate without this ±6 pp band — it is wide enough to change rankings.

#### Theme 5 — Facility capability & evidence trust

21. **10,048 facility-capability claims are STRONG and 4,019 reach VERY HIGH confidence (≥85), but 47,971 cells are NO CLAIM and 3,454 are WEAK/SUSPICIOUS.** Method: evidence-tier trust scorer. **Confidence: HIGH (data-quality fact).** **So-what:** the engine can answer "can X do Y" with high confidence for ~14% of cells; the rest must be hedged.

22. **1,445 facility-capability rows carry an explicit contradiction flag (claim vs source mismatch).** Method: contradiction detector. **Confidence: HIGH.** **So-what:** route these to human review before they feed any patient-routing answer (R3) — they are the highest-risk records.

23. **Maternity (4,877 with-claim) and emergency (3,373) are the best-evidenced capabilities; NICU is the worst (only 678 STRONG of 1,656 claims).** Method: capability grade distribution. **Confidence: HIGH.** **So-what:** neonatal-intensive-care routing is the least trustworthy — prioritize NICU evidence collection and verification.

#### Theme 6 — Care gaps, supply-demand & pincode granularity

24. **718 region-capability cells are APPARENT CARE GAPs (well-documented yet zero strong supply) — distinct from 2,345 DATA-POOR cells.** Method: trust-weighted gap classifier using fill_rate. **Confidence: MED.** **So-what:** these 718 are the actionable shortlist (e.g. Jamnagar dialysis, Deoghar oncology) — real gaps worth field verification, separated from mere missing data.

25. **More facilities does NOT predict better outcomes: n_facilities -> inst_birth adj β −0.041 (negative!), -> full_imm −0.113, and supply-demand correlations are weak (|r|≤0.27).** Method: adjusted supply-demand regression + correlation. **Confidence: MED-HIGH.** **So-what:** facility *count* is not a quality/access proxy — counting hospitals will not fix immunization or institutional-birth gaps; invest in service quality, not raw numbers. (Positive supply–C-section link r≈0.25 hints at private-supply-driven over-intervention.)

26. **Pincode supply is extremely sparse and inversely tracks urbanicity: NE/hill/Odisha states have ≥93-100% zero-supply pincodes (Ladakh, A&N, Puducherry 100%; Odisha 95%) vs Delhi 38%, Chandigarh 43%.** Method: pincode supply layer (mean 87.8% zero-supply pins). **Confidence: HIGH.** **So-what:** rural/NE pincode "supply deserts" are where new capacity and verified-evidence collection should concentrate; current data is urban-biased.

---

### PART C — WHAT WE STILL CANNOT KNOW (and exactly what to collect next)

These three tables (district NFHS-5 outcomes/features, facility capability corpus, pincode supply) cannot answer four classes of question. For each, the precise next data:

1. **No causal identification over time — every "causal" verdict is design-based on a single 2019-21 wave.** We cannot run difference-in-differences, fixed-effects-over-time, or rule out time-invariant confounding. **Collect: NFHS-4 (2015-16) district outcomes/features** for the same indicators -> enables district fixed-effects DiD (e.g. did rising sanitation *change* track falling stunting *change*), turning MED causal verdicts into HIGH.

2. **No sub-district / within-district heterogeneity — all 706 estimates are district averages, and 437/569 districts are already state-shrunk.** We cannot see urban-slum vs rural pockets, caste/wealth gradients, or individual-level confounding (ecological fallacy). **Collect: NFHS individual/household microdata (PSU + wealth quintile + woman-level records)** -> enables multilevel woman-in-PSU-in-district models, true sub-district small-area estimation, and individual-level causal adjustment.

3. **Facility "capability" = a documented CLAIM, never a verified outcome — we cannot tell whether a STRONG dialysis claim means good dialysis.** No volumes, success/complication rates, or live capacity. So R1/R3 answer "claims to do" not "does well." **Collect: clinical registry / facility-reporting outcomes (HMIS, NABH accreditation, procedure volumes, mortality/complication rates, bed availability)** -> upgrades capability grade from claim-trust to verified-success and lets R3 rank by *quality*, not just evidence+distance.

4. **No TRUE spatial adjacency — geo work uses recovered centroids + haversine k-NN, which is why the GNN cannot beat the baseline and Moran's I rests on approximate locations.** We cannot compute real shared-border contiguity, road/travel-time access, or correct spatial-lag models. **Collect: district administrative shapefiles (and ideally road network / travel-time isochrones)** -> enables true queen/rook adjacency, proper spatial econometrics, and a fair re-test of geometric DL; with NFHS-4 added as temporal node features the GNN may finally earn its keep.

**Bottom line:** The engine answers all six question types today with explicit confidence, but its causal answers are capped at MED until NFHS-4 (DiD), its equity answers are capped until microdata (sub-district), its facility answers are claim-bound until registries, and its spatial answers stay LOW until shapefiles. Those four datasets are the highest-ROI next collection.
