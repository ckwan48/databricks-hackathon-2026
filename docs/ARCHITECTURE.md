# Architecture — facilitiesHelp.io

A reliability-first Databricks App: the page renders **instantly from cached gold-table queries**, and every LLM / Genie call is **on-demand** (button or chat) so AI never blocks the render. Everything runs on **Databricks Free Edition**.

---

## 1. System diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  SOURCE — Unity Catalog (read-only Marketplace dataset)                        │
│  databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset      │
│   • facilities (10,088 × 51)   • india_post (165,627 offices)   • nfhs_5 (706) │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                 │  bronze → silver → gold   (build_gold.py)
                                 ▼  serverless SQL Warehouse  (id c5e7e7089978bd43)
┌──────────────────────────────────────────────────────────────────────────────┐
│  GOLD — workspace.virtue_gold   (Delta, the decision layer)                    │
│   silver_facility            dedup by cluster_id, evidence text, PIN→district  │
│   gold_facility_capability_trust  22 acute capabilities + contradiction check  │
│   gold_facility_specialty         every specialty graded (2,580 · 118k rows)   │
│   gold_facility_contact           address · phone · web · beds · doctors · equip│
│   gold_all_gaps / *_district_gaps district care-gap classification (2,518 caps)│
│   gold_referral                   distance-rankable referral index            │
│   gold_nfhs · gold_pin_state · gold_specialty_counts   analysis aggregates     │
│   app_user_actions                persisted overrides/shortlists/scenarios/chat│
└───────────────────────────────┬──────────────────────────────────────────────┘
            cached reads (@st.cache_data, 600s)  │   writes (overrides, etc.)
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  APP — Streamlit Databricks App  "virtue-desk"  (service principal auth)       │
│   ① Facility Trust  ② Medical Desert  ③ Referral  ④ Data Readiness             │
│   ⑤ Ask the Data    ⑥ Data Science Lab                                         │
│        │ on-demand                         │ on-demand                          │
│        ▼                                   ▼                                    │
│   Model Serving — databricks-llama-4-maverick     AI/BI Genie space            │
│   (3 agents: insights · reasoning · simulation     (NL → SQL over gold tables) │
│    + grounded Copilot, never fabricates numbers)                               │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                 ▼
                       Non-technical user (planner / NGO / analyst)
```

## 2. Layers

**Data / medallion** — `build_gold.py` (+ `01_medallion_pipeline.py`) runs all transforms on the serverless SQL Warehouse: read the read-only Marketplace catalog → **silver** (dedup by `cluster_id`, assemble `evidence_text`/`spec_text`, count `source_types`, join `facilities → PIN → district`) → **gold** decision tables. The offline statistical analysis (`build_*.py`) produces the causal/ML results surfaced in the app.

**Gold (the contract between data and app).** The app *only* reads gold (never the raw catalog at request time), so reads are fast and stable. Key tables in §1.

**App.** A single `app.py` Streamlit app, six tracks, brand-styled CSS (IBM Plex Sans + Plex Mono). Auth via `databricks.sdk.core.Config()` → SQL via `databricks-sql-connector`, foundation model via `WorkspaceClient().serving_endpoints`, Genie via `WorkspaceClient().genie`.

**AI (all on-demand, never on page load).**
- **3 modular agents** + a grounded **Copilot** on **Model Serving (Llama 4 Maverick)**. The Copilot grounds on gold-table facts and **refuses to invent numbers**.
- **AI/BI Genie** space over the gold tables for natural-language → SQL.

**Persistence.** Overrides, shortlists, scenarios, and chats append to `app_user_actions` (Delta; Lakebase-ready).

## 3. Request lifecycle

1. Page load → cached gold queries (`@st.cache_data ttl=600`) → renders in well under a second after the warehouse is warm.
2. User clicks **"Explain"** / asks the Copilot → a single Model-Serving call, grounded in the relevant gold rows.
3. User clicks **"Run as SQL via Genie"** → Genie writes/executes SQL and returns rows.
4. User saves an override/shortlist → one INSERT into `app_user_actions`.

## 4. Track → data map

| Track | Reads |
|---|---|
| ① Facility Trust | `gold_facility_capability_trust`, `gold_facility_specialty`, `gold_facility_contact` |
| ② Medical Desert | `gold_all_gaps`, `gold_*_district_gaps`, facility tables, `gold_nfhs` (causal) |
| ③ Referral | `gold_facility_specialty` + `gold_facility_contact` + India-Post geocode |
| ④ Data Readiness | `gold_data_readiness` |
| ⑤ Ask the Data | grounded over all gold tables + Genie space |
| ⑥ Data Science Lab | `gold_nfhs`, `gold_pin_state`, `gold_specialty_counts`, facility tables |

## 5. Tech stack

Databricks **Free Edition** · **Unity Catalog** · serverless **SQL Warehouse** · **Delta** medallion · **Databricks Apps** (Streamlit) · **Model Serving** (Llama 4 Maverick) · **AI/BI Genie** · **Databricks agent skills** (`databricks aitools`) · Lakebase-ready. Python · Plotly · pandas · scikit-learn · statsmodels · causal-learn.

## 6. Design principles

- **Reliability-first:** instant render from cached gold; AI is always lazy.
- **Evidence-first:** every claim cites the facility's own text; confidence is always shown.
- **No fabrication:** the Copilot answers only from grounded data or says it has none.
- **Read raw, write gold:** the app never mutates the source catalog; only `workspace.virtue_gold`.

See [`METHODOLOGY.md`](METHODOLOGY.md), [`CAUSAL_INFERENCE.md`](CAUSAL_INFERENCE.md), and [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).
