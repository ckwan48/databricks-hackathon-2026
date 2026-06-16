# How facilitiesHelp.io uses Databricks

Built **end-to-end on Databricks Free Edition** — every layer is a Databricks primitive, nothing is bolted on from outside.

| Databricks capability | Exactly how we used it | Point to it in the demo |
|---|---|---|
| **Unity Catalog** | Governs the **3 read-only Marketplace datasets** (facilities, India-Post, NFHS-5); our own `workspace.virtue_gold` schema holds **every decision table**. Read raw, write only gold. | "Every number you see is a governed Unity Catalog table read." |
| **Serverless SQL Warehouse** | Runs the whole **bronze → silver → gold** medallion (`build_gold.py`) **and** every cached read the app makes at request time. | Tracks load instantly because they read gold over the warehouse. |
| **Delta Lake (medallion)** | **Silver** dedups facilities by `cluster_id` and assembles the evidence text; **gold** = the trust grades, district gaps, referral index, specialty co-occurrence, condition correlations, readiness queue, and the persistence log. | The gold tables behind each track. |
| **Databricks Apps** | The entire UI is a **Streamlit Databricks App** ("virtue-desk") deployed on the Apps platform with **service-principal auth** — reliability-first (instant render from cached gold, AI is always on-demand). | The app itself is a Databricks App. |
| **Model Serving — Llama 4 Maverick** | Powers **3 on-demand agents** (insights · reasoning · simulation), a **grounded copilot** that refuses to fabricate numbers, and a **translator** for multilingual answers. | The "Explain" buttons, Ask-the-Data answers, and the Translate action. |
| **AI/BI Genie** | A Genie space over the gold tables turns **natural language → SQL**, executed live. | "Also run this as SQL via Genie" in Ask the Data. |
| **Databricks agent skills** (`databricks aitools`) | Installed **10 official Databricks skills** project-scoped (apps, app-design, model-serving, lakebase, vector-search, jobs, pipelines, dabs, core, serverless-migration). They taught the coding agent **how** to build on the platform. | `.claude/skills/` + `AGENTS.md` in the repo. |
| **Lakebase** | The persistence path: user overrides / shortlists / scenarios / chats are **Lakebase-ready** (Delta `app_user_actions` today); roadmap is Postgres + **pgvector** for sub-10ms reads and exact-quote citations. | Saved overrides and shortlists persist. |
| **Databricks CLI** | Ships the app: `databricks workspace import-dir` + `databricks apps deploy`, and builds the gold tables on the warehouse. | How every update reached the live app. |

## What to say to the judges (30-second version)

> "It's **100% Databricks, Free Edition**. The three datasets are governed in **Unity Catalog**; we transform them through a **Delta medallion on a serverless SQL Warehouse** into gold decision tables. The app is a **Streamlit Databricks App**. The AI is **Model Serving with Llama 4 Maverick** — three agents plus a grounded copilot that won't invent numbers — and **AI/BI Genie** writes and runs the SQL when you ask in plain English. We even built it **using the official Databricks agent skills** (`databricks aitools`), and persistence is **Lakebase-ready**. Read raw, write gold, cite everything."

## The one-line differentiators
- **Genie** isn't a gimmick tab — it's wired to the *same* gold tables the rest of the app trusts, so NL→SQL stays consistent with our grades.
- The copilot is **grounded**: it answers only from gold-table facts and **refuses** when it has no data — no hallucinated statistics.
- We used Databricks **agent skills** to build the app itself — Databricks tooling building a Databricks app.
