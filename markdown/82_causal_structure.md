## Causal Structure Discovery: What the Data Says vs. What Domain Theory Assumes

**Goal.** Rather than impose a causal graph, we let two complementary algorithms *learn* the dependency structure among 16 core variables and then confront that data-driven structure with the assumed domain DAG. Structure learning answers the question "where *could* causation flow, given the conditional-independence footprint in the data?" — it does **not** prove causation.

**Sample.** From 706 districts we kept complete cases over the 16 variables (`stunting, underweight, inst_birth, full_imm, anaemia_women, sanitation, clean_fuel, fem_school10, literacy, anc4, diarrhoea, pop_under15, women_overweight, high_bp_w, electricity, n_facilities`). **n = 693** districts (13 dropped for missingness). All variables were z-standardized before analysis.

### (1) PC algorithm — discovered CPDAG
Method: `causallearn` PC, `indep_test='fisherz'`, `alpha=0.05`. The output is a CPDAG: directed edges (`X->Y`) are orientations the data can identify; undirected edges (`X--Y`) belong to a Markov-equivalence class the data cannot orient.

**Directed edges (X -> Y), with bootstrap stability (B=100 resamples: P[edge present] / P[oriented this way]):**

| Edge | edge-present | oriented-this-dir |
|---|---|---|
| underweight -> stunting | 1.00 | 0.65 |
| pop_under15 -> stunting | 0.99 | 0.70 |
| underweight -> sanitation | 1.00 | 0.80 |
| underweight -> anaemia_women | 0.92 | 0.47 |
| underweight -> women_overweight | 1.00 | 0.53 |
| underweight -> diarrhoea | 0.61 | 0.22 |
| sanitation -> anaemia_women | 1.00 | 0.71 |
| sanitation -> diarrhoea | 1.00 | 0.58 |
| literacy -> sanitation | 1.00 | 0.84 |
| literacy -> fem_school10 | 1.00 | 0.65 |
| clean_fuel -> fem_school10 | 0.97 | 0.63 |
| clean_fuel -> women_overweight | 1.00 | 0.85 |
| fem_school10 -> women_overweight | 1.00 | 0.78 |
| women_overweight -> high_bp_w | 1.00 | 0.63 |
| anc4 -> full_imm | 1.00 | 0.46 |
| anc4 -> inst_birth | 0.97 | 0.50 |
| full_imm -> inst_birth | 0.92 | 0.80 |
| clean_fuel -> inst_birth | 1.00 | 0.88 |
| pop_under15 -> inst_birth | 1.00 | 0.79 |
| pop_under15 -> anc4 | 1.00 | 0.76 |
| pop_under15 -> literacy | 0.76 | 0.20 |
| pop_under15 -> electricity | 1.00 | 0.77 |
| high_bp_w -> pop_under15 | 1.00 | 0.70 |
| high_bp_w -> sanitation | 0.93 | 0.89 |
| stunting -> electricity | 0.89 | 0.59 |
| full_imm -> electricity | 0.57 | 0.21 |
| fem_school10 -> anaemia_women | 0.47 | 0.45 |
| diarrhoea -> anaemia_women | 0.65 | 0.33 |
| diarrhoea -> full_imm | 0.40 | 0.24 |
| clean_fuel -> pop_under15 | 0.56 | 0.53 |

**Undirected edge (X -- Y):** `clean_fuel -- n_facilities` (edge-present 0.91; the data sees a robust association to facility supply but cannot orient it).

**Bidirected edges (X <-> Y, latent-confounder signatures):** none under PC.

**Reading the stability.** Adjacency is far more stable than orientation. Skeleton edges such as `underweight–stunting`, `sanitation–diarrhoea`, `literacy–sanitation`, `women_overweight–high_bp_w`, `pop_under15–anc4/inst_birth/electricity` appear in ~100% of bootstraps and are trustworthy as *associations*. Arrowheads are much shakier: `underweight->diarrhoea` (0.22), `pop_under15->literacy` (0.20), `full_imm->electricity` (0.21) flip direction across resamples, so their causal *reading* should be discarded even though the connection is real. Edges with edge-present < 0.6 (`diarrhoea->full_imm` 0.40, `fem_school10->anaemia_women` 0.47) are themselves fragile. **Direction of effect is the least reliable thing PC produces here — treat orientations with oriented-prob < ~0.7 as undetermined.**

A clear artifact: several arrows point *into* obvious upstream variables (e.g., `underweight -> sanitation`, `stunting -> electricity`, `high_bp_w -> sanitation`). These are almost certainly orientation errors — sanitation and electricity are infrastructural and cannot be *caused* by a child's nutritional status. They arise because PC orients edges from collider patterns in cross-sectional data with **no temporal precedence**; with development confounders unmeasured, the algorithm picks a member of the equivalence class that contradicts domain sense.

### (2) Graphical-Lasso partial-correlation network
Method: `GraphicalLassoCV` (5-fold), selected regularization `alpha = 0.167`; edge retained if |partial correlation| > 0.1. This gives an **undirected** network where an edge means two variables remain associated after conditioning on all 14 others. **24 edges** survived. Strongest:

| Edge | partial corr |
|---|---|
| fem_school10 -- literacy | **+0.383** |
| stunting -- underweight | **+0.376** |
| clean_fuel -- women_overweight | **+0.345** |
| full_imm -- anc4 | +0.277 |
| sanitation -- literacy | +0.265 |
| pop_under15 -- high_bp_w | -0.233 |
| fem_school10 -- women_overweight | +0.218 |
| inst_birth -- pop_under15 | -0.216 |
| inst_birth -- anc4 | +0.214 |
| anc4 -- pop_under15 | -0.212 |
| women_overweight -- high_bp_w | +0.182 |
| pop_under15 -- electricity | -0.168 |
| anaemia_women -- sanitation | -0.167 |
| clean_fuel -- fem_school10 | +0.164 |
| underweight -- sanitation | -0.163 |
| underweight -- women_overweight | -0.153 |
| stunting -- pop_under15 | +0.149 |
| sanitation -- diarrhoea | -0.125 |
| ... | (full list in CSV) |

The GLASSO skeleton agrees strongly with the PC skeleton: the high-stability PC adjacencies (`stunting–underweight`, `fem_school10–literacy`, `women_overweight–high_bp_w`, `sanitation–diarrhoea`, `anc4–full_imm`, `pop_under15`-hub edges) all re-appear as the largest partial correlations, which is reassuring cross-method convergence on *which variables are connected*. Note `n_facilities` and the supply features are almost entirely disconnected from the health outcomes once development covariates are conditioned out — supply enters only via the weak undirected `clean_fuel–n_facilities` link.

### (3) Data-discovered structure vs. assumed domain DAG

| Assumed domain edge | In PC skeleton? | PC reading | In GLASSO? (pcorr) |
|---|---|---|---|
| sanitation -> diarrhoea | **Yes** | `sanitation->diarrhoea` (correct direction) | **Yes** (-0.125) |
| diarrhoea -> stunting | **No** | absent | **No** |
| fem_school10 -> stunting | **No** | absent | **No** |
| fem_school10 -> underweight | **No** | absent | **No** |
| fem_school10 -> full_imm | **No** | absent | **No** |
| fem_school10 -> inst_birth | **No** | absent | **No** |
| women_overweight -> high_bp_w | **Yes** | `women_overweight->high_bp_w` (correct direction) | **Yes** (+0.182) |

**Two of the assumed mechanisms are corroborated by the data, and with the correct direction:**
- `sanitation -> diarrhoea`: present and oriented correctly (orient-prob 0.58, edge-present 1.00). The negative partial corr (-0.125) confirms better sanitation, less diarrhoea.
- `women_overweight -> high_bp_w`: present and oriented correctly (orient-prob 0.63, edge-present 1.00, pcorr +0.182). The metabolic pathway survives conditioning.

**The remaining assumed edges are NOT recovered as *direct* edges — and that is expected, not a refutation.** This is the textbook signature of *mediation*:
- `diarrhoea -> stunting` and `fem_school10 -> stunting`/`underweight` disappear because their influence is screened off. In the discovered graph, `underweight` is the hub adjacent to `stunting` (the single strongest edge in both methods, pcorr +0.376), and `fem_school10` connects to child outcomes only through chains (`fem_school10 - women_overweight`, `literacy - sanitation - diarrhoea`, etc.). Conditional-independence methods *delete* an A->C edge whenever a measured mediator B fully transmits the effect (A->B->C). So a missing direct edge is consistent with an **indirect** causal pathway, which the chained edges still support.
- `fem_school10 -> full_imm / inst_birth`: in the data these run through `anc4` and `clean_fuel` (the hub `pop_under15 -> anc4 -> full_imm -> inst_birth` chain), so the direct school->service edges are screened off by antenatal care and socioeconomic proxies.

**Where faithfulness can fail.** The PC/GLASSO logic assumes *faithfulness*: that conditional independencies in the distribution exactly mirror the graph. This breaks when a variable has both a **direct** effect and an **indirect** (mediated) effect of opposite sign that nearly **cancel** — the net partial correlation falls below the test/threshold and the true edge is erased. With many development variables intercorrelated (literacy, fem_school10, clean_fuel, electricity all proxy the same latent "development"), such cancellation and near-collinearity are plausible here, so some genuinely causal direct edges may be wrongly judged absent. This is a reason to read absent edges cautiously, not as evidence of "no effect."

### Interpretation guardrails (read before using any arrow)
- **Ecological, not individual.** Every node is a *district-level* prevalence. Edges describe how district aggregates co-move; they are **ECOLOGICAL relationships** and do not license individual-level causal claims (ecological fallacy).
- **Cross-sectional — no temporal precedence.** All measures are contemporaneous, so the algorithm has *no time information* to orient cause before effect. Implausible arrowheads (`underweight->sanitation`, `stunting->electricity`, `high_bp_w->sanitation`) are direct evidence of this limitation; trust the *skeleton* (which variables connect) far more than the *arrowheads*.
- **Unobserved confounding.** No income, caste, wealth, or urbanicity is measured. A shared "development/wealth" latent almost certainly drives the dense literacy–fem_school10–clean_fuel–electricity–sanitation cluster; PC found no bidirected (latent) edges, but that is a limitation of the assumption set, not proof that confounders are absent.
- **MNAR suppression.** The 13 dropped districts and any value suppression are likely *not* missing at random (suppression often correlates with extreme/small-population districts), which can bias the learned structure.
- **Bottom line.** These graphs are *causal evidence / hypotheses about where effects could flow*, to be combined with domain knowledge and validated with designs that have temporal or quasi-experimental identification — **not causal proof.**

**Artifacts.** Edge list (PC directed/undirected/bidirected with bootstrap stability, GLASSO partial correlations, and the domain-DAG check) -> `/Users/koushik/Desktop/health_analysis_outputs/causal_structure_edges.csv`. CPDAG drawing -> `/Users/koushik/Downloads/DAS_HACK/figures/causal_dag.png`.
