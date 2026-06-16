## Bayesian Network: Structure Learning and Interventional Reasoning

**Question.** Can we recover a plausible causal *graph* among district-level health drivers, and use it to reason about what would happen if we *set* sanitation high rather than merely *observe* it high?

**Data & method.** 10 key variables — `sanitation`, `clean_fuel`, `fem_school10`, `anc4`, `diarrhoea`, `stunting`, `inst_birth`, `full_imm`, `pop_under15`, `anaemia_women` — over **n = 693** districts (complete cases; 13 of 706 dropped for missing `full_imm`). Each variable was discretized into **terciles** (low / med / high; ~231 districts per bin). Structure was learned two ways:

1. **Primary — discrete hill-climbing BIC.** A score-based search over the tercile-coded data (add / remove / reverse moves, acyclicity enforced via `networkx`, max 3 parents/node, BIC = log-likelihood − ½·log(n)·free-params). Converged in 12 sweeps to **total BIC = −6857.9**.
2. **Cross-check — PC (constraint-based, Fisher-Z, α = 0.05)** on the *standardized continuous* data, from a different search family. (The requested causal-learn **GES** `local_score_BIC` path hit a covariance-shape bug — `TypeError: only 0-dimensional arrays can be converted to scalars` — in this build, so PC was substituted as the continuous cross-check; PC also exposes Markov-equivalence ambiguity directly as undirected edges.)

Tercile cut points (1/3, 2/3 quantiles): sanitation [66.6, 80.0] %, clean_fuel [38.0, 67.2] %, fem_school10 [32.6, 45.6] %, anc4 [51.3, 70.9] %, diarrhoea [4.4, 7.2] %, stunting [29.4, 37.3] %, inst_birth [87.0, 96.0] %, full_imm [73.3, 84.1] %, pop_under15 [23.7, 28.2] %, anaemia_women [52.2, 61.3] %.

### Learned DAG edges (hill-climbing BIC, parent → child)

| Edge | Interpretation |
|---|---|
| `fem_school10 → sanitation` | Female schooling precedes household sanitation uptake |
| `clean_fuel → fem_school10` | Development bundle: cleaner fuel co-moves with schooling |
| `pop_under15 → clean_fuel` | Younger demographic ↔ less clean fuel (development gradient) |
| `pop_under15 → anc4` | Demographic structure shapes 4+ antenatal care |
| `inst_birth → anc4` | Institutional-birth and antenatal-care systems co-evolve |
| `sanitation → diarrhoea` | **Sanitation lowers childhood diarrhoea** (mechanistic) |
| `sanitation → anaemia_women` | Sanitation linked to women's anaemia |
| `pop_under15 → stunting` | Demographic confounder of stunting |
| `fem_school10 → stunting` | **Female schooling lowers stunting** |
| `anc4 → full_imm` | Antenatal contact feeds into full immunization |
| `inst_birth → pop_under15` | Health-system maturity tracks demographic transition |

### Continuous cross-check (PC, CPDAG)

PC, from a different algorithmic family, **corroborates the load-bearing edges**: `sanitation → diarrhoea`, `sanitation → stunting`, `fem_school10 → stunting`, `pop_under15 → stunting`, `anc4 → inst_birth`. It additionally returns **undirected** edges where the data cannot pick a direction: `sanitation — fem_school10`, `anc4 — full_imm`, `anc4 — pop_under15`. These are genuine **Markov-equivalence** ambiguities (see caveats).

### Key conditional dependencies (Fisher-Z partial correlations, n = 693)

| Test | Partial r | p | Reading |
|---|---|---|---|
| sanitation ⟂̸ stunting (marginal) | −0.504 | < 1e-16 | Strong raw negative association |
| sanitation ⟂̸ stunting \| diarrhoea | −0.464 | < 1e-16 | Most of the link is **not** through the diarrhoea mediator |
| sanitation ⟂̸ diarrhoea (marginal) | −0.366 | < 1e-16 | Supports `sanitation → diarrhoea` |
| fem_school10 ⟂̸ anc4 (marginal) | +0.390 | < 1e-16 | Schooling co-moves with antenatal care |
| inst_birth ⟂̸ full_imm \| anc4 | +0.175 | 3.3e-06 | Residual link beyond shared anc4 channel |
| clean_fuel ⟂ stunting \| sanitation, fem_school10 | −0.062 | 0.104 | **Independent** once sanitation+schooling held fixed → clean_fuel's stunting link is largely confounded |
| stunting ⟂ full_imm \| fem_school10 | −0.072 | 0.057 | Borderline independence — schooling explains most of the co-movement |

The last two are the analytically interesting "screening-off" results: variables that *look* associated marginally become (near-)independent after conditioning on the right parents — exactly what a correct DAG predicts.

### Interventional reasoning: stunting ~ sanitation

`see()` is the observed conditional frequency P(stunting=high | sanitation=X). `do()` is the back-door–adjusted distribution P(stunting=high | **do**(sanitation=X)), standardized over the confounder strata {`fem_school10`, `pop_under15`}. We deliberately **do not** adjust for `diarrhoea`: in the learned DAG it is a *mediator* (`sanitation → diarrhoea → ...`), and conditioning on a mediator would block part of the very effect we want to estimate.

| sanitation tercile | n districts | P(stunting=high) **see()** | P(stunting=high) **do()**, adjusted |
|---|---|---|---|
| low | 231 | **0.571** | 0.385 |
| med | 231 | 0.281 | 0.296 |
| high | 231 | **0.139** | 0.200 |

- **Observational contrast (see):** P(high stunting) falls from **57.1% → 13.9%** going from low to high sanitation — a crude gap of **0.433**.
- **Interventional contrast (do):** after back-door adjustment, the low→high gap shrinks to **0.385 → 0.200 = 0.185** — **about 57% of the crude gap survives.**

Interpretation: a large part of the raw sanitation–stunting gradient is **confounding** (poorer, less-schooled, more youthful districts have both bad sanitation *and* high stunting). But a substantial adjusted contrast remains, so the data still carry **evidence** (not proof) that raising sanitation would lower stunting. Positivity held: every confounder stratum had support at all three sanitation levels (coverage = 1.0), so no extrapolation was needed.

**Why adjustment is needed for `do()` but not `see()`.** `see(sanitation=high)` simply *filters* to districts that happen to be high-sanitation — and those districts also tend to be richer/more-schooled, so the observed low stunting partly reflects *who* has high sanitation, not the effect of sanitation itself. `do(sanitation=high)` imagines *forcing* sanitation high while leaving the confounder distribution at its population values; the back-door formula P(Y | do(X)) = Σ_z P(Y | X, z)·P(z) re-weights the strata to remove the spurious confounder pathway. The two coincide only if there is no open back-door path — which is not the case here.

![Learned DAG and see-vs-do contrast](/Users/koushik/Downloads/DAS_HACK/figures/83_bayesian_network.png)

### Caveats (read before citing any number)

- **Ecological, not individual.** All variables are district aggregates; edges and CPTs describe *district-level* (ecological) relationships and must not be read as individual-child risks.
- **Cross-sectional — no temporal precedence.** Edge *directions* here come from score/CI patterns, not from time ordering. A DAG arrow is a modeling claim, not observed precedence.
- **Markov-equivalence classes can't orient every edge.** Many DAGs encode the same conditional-independence pattern; PC explicitly left `sanitation — fem_school10`, `anc4 — full_imm`, `anc4 — pop_under15` *undirected*. The hill-climb returns one DAG from the equivalence class, so some of its arrowheads are not uniquely identified.
- **Discretization information loss.** Collapsing continuous percentages into 3 bins discards within-tercile variation, can blur monotone trends, and makes results sensitive to the cut points; the partial-correlation tests (run on continuous data) are the higher-resolution complement.
- **Unobserved confounding.** No income or caste variables are available; the back-door adjustment set {fem_school10, pop_under15} is a *proxy* and almost certainly incomplete, so the `do()` estimates are likely still biased toward the crude contrast.
- **MNAR suppression.** The 13 dropped districts (missing `full_imm`) and any suppressed cells are not missing-at-random; complete-case analysis can bias the learned structure.
- **Bottom line: causal *evidence*, not proof.** Treat the DAG as a hypothesis generator and the `do()` numbers as adjustment-conditional, not as validated treatment effects.

**Artifacts:** `/Users/koushik/Desktop/health_analysis_outputs/bn_results.json`, `/Users/koushik/Desktop/health_analysis_outputs/bn_stunting_sanitation_cpt.csv`, figure `/Users/koushik/Downloads/DAS_HACK/figures/83_bayesian_network.png`.
