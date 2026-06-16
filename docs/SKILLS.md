# Databricks agent skills

This repo ships the **official Databricks agent skills**, installed project-scoped with:

```bash
databricks aitools install --scope project --agents claude-code
```

> **Why are they under `.claude/skills/`?** That's just the directory the `databricks aitools` installer uses for the Claude Code coding agent. The **content is 100% Databricks** — each is an official Databricks skill (note the `name: databricks-*` and `Requires databricks CLI` frontmatter). The same skills are mirrored at the Databricks-native path `.databricks/aitools/skills/`. The folder name is the *agent's* convention; the skills are Databricks'.

## The 10 skills installed (v0.2.4)

| Skill | What it teaches the coding agent |
|---|---|
| `databricks-core` | Parent skill — CLI auth, profiles, workspace conventions |
| `databricks-apps` | Build & deploy apps on the Databricks Apps platform |
| `databricks-app-design` | App UX/architecture: analytics vs Lakebase synced-table data access |
| `databricks-lakebase` | Lakebase Postgres: provisioning, CRUD, pgvector, synced tables |
| `databricks-model-serving` | Query/serve foundation & custom models (e.g. Llama 4 Maverick) |
| `databricks-vector-search` | Vector indexes for RAG over text |
| `databricks-jobs` | Author and run Databricks Jobs |
| `databricks-pipelines` | Lakeflow / Delta Live Tables pipelines |
| `databricks-dabs` | Databricks Asset Bundles (IaC for jobs/apps/pipelines) |
| `databricks-serverless-migration` | Migrate workloads to serverless compute |

## How facilitiesHelp.io used them

- **`databricks-apps` + `databricks-app-design`** — scaffolding and deploying the Streamlit app (`databricks apps create/deploy`), and the data-access decision (serverless SQL Warehouse analytics reads vs. Lakebase synced tables).
- **`databricks-model-serving`** — wiring the on-demand agents + Copilot to `databricks-llama-4-maverick`.
- **`databricks-lakebase`** — the persistence path for user actions (Lakebase-ready; currently Delta `app_user_actions`).
- **`databricks-core`** — auth/profile conventions captured in [`../AGENTS.md`](../AGENTS.md).

Any coding agent (Claude Code / Cursor / Codex) opening this repo reads [`../AGENTS.md`](../AGENTS.md) for workspace defaults, then these skills for *how* to build on Databricks.
