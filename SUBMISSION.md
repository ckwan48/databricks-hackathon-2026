# Virtue Desk — Trust, Desert & Causation Desk
**Databricks Apps & Agents for Good 2026 · Live app:** https://virtue-desk-7474648370355072.aws.databricksapps.com

## Inspiration
A planner or NGO coordinator is handed **10,000 messy, scraped healthcare-facility records**. Half the "capabilities" are unverified claims. Where do you safely send a patient? Where are the *real* care gaps — not just regions we under-measured? You can't act on hope. You need **evidence, confidence, and cause.** That is Virtue Desk.

## What it does
Four tracks for a non-technical planner — **every answer carries its evidence and its uncertainty**:

1. **Facility Trust Desk** — grades every facility × capability (ICU, maternity, oncology, NICU, emergency, trauma, dialysis) **from the facility's own text** as Strong / Partial / Weak-Suspicious, with a **0–100 confidence meter**, the **cited source text + links**, step-by-step AI reasoning on demand, and an optional **human override saved to an audit log** (the model grade is never overwritten).
2. **Medical Desert Planner** — aggregates trust-weighted evidence to district level and **distinguishes a real care gap (facilities exist but little trustworthy capability) from data-poor (too few records to judge)** — **247 real gaps** surfaced. Plus an **interactive causal graph** from a 706-district NFHS analysis showing which health levers are *real causes* vs *confounded coincidences*.
3. **Referral Copilot** — "dialysis near Jaipur" → an **evidence-attached, distance-ranked shortlist** on an interactive map.
4. **Data Readiness Desk** — surfaces contradictions, impossible values and sparse fields, ranked by **leverage** for human review.

Plus **example questions (Easy → Difficult) per track** and a grounded **Copilot chat** that answers any question with citations.

## How we built it (all Databricks, Free Edition)
- **Data:** the Virtue Foundation Marketplace dataset (Unity Catalog) + India Post PIN directory + NFHS-5 district indicators.
- **Medallion:** bronze → silver → gold in **Unity Catalog** on a serverless **SQL Warehouse**. Silver dedups the PIN directory, parses JSON evidence arrays, resolves facility entities via `cluster_id`, and joins facilities → PIN → district. Gold holds trust grades, district gaps, the referral index, the readiness queue, and a persistence table.
- **Trust engine:** deterministic, auditable grading across **specialty codes + equipment + procedure + capability text + source-diversity**, producing a confidence score and contradiction flags.
- **AI:** **3 modular agents** (insights · reasoning · simulation) + a copilot on **Databricks Model Serving (Llama 4 Maverick)**, called on-demand and grounded in the gold tables.
- **Causal layer (the differentiator):** structure learning (PC), Bayesian network, **multi-method effect estimation (OLS+state FE, Double-ML, propensity matching)**, sensitivity (E-values), statistical ML (penalized, multilevel, GAM, **conformal prediction**), and **geometric deep learning** (spatial GNN, spillover β=0.59) on 706 NFHS districts.
- **App:** a **Streamlit Databricks App**, Databricks-branded, fully interactive (Plotly), persisting every user action to Delta.

## Challenges we ran into
- The data is genuinely messy — column-misaligned rows, `pharmacy`/`farmacy`, impossible values (200k beds), corrupt PIN coordinates, MNAR suppression in NFHS. **We flag, never hide.**
- **Correlation ≠ causation:** sanitation↔stunting looks strong (r = −0.51) but **collapses to ~0 after adjusting for wealth** — confounded. We built the full causal ladder to separate real levers (female schooling → less child marriage; ANC visits → institutional birth) from confounds.
- Calibrating *real gap vs data-poor* so the desert story is honest, not alarmist.

## Accomplishments we're proud of
- **24,843** evidence-graded capability claims; **~10,000 high-confidence**.
- **247 real care gaps** rigorously distinguished from data-poor regions.
- An **interactive causal graph that changes per capability** — depth almost no team will have.
- A **fully Databricks-native, live app on Free Edition**, with every claim cited.

## What we learned
The hardest part of "for good" data work isn't prediction — it's **honesty**: showing the evidence, communicating uncertainty, and telling the difference between a correlation and a cause.

## What's next
- **NFHS-4 → difference-in-differences** for true causal effects (two waves).
- **2SFCA accessibility + GNN spatial spillover** for sharper desert detection.
- **Vector-search RAG** over facility text + **Lakebase synced tables** for sub-10ms reads.

## Built with
Databricks Free Edition · Unity Catalog · SQL Warehouse · Delta medallion · Model Serving (Llama 4 Maverick) · Databricks Apps · Streamlit · Plotly · causal-learn · scikit-learn · statsmodels · PyTorch.
