# AGENTS.md — Databricks defaults for coding agents

This repo is **Virtue Desk**, a Databricks App for *Apps & Agents for Good 2026*.
Coding agents (Claude Code / Cursor / Codex) should read this before touching code.

## Workspace
- **Host:** `https://dbc-fc1bd7fb-a374.cloud.databricks.com`
- **CLI profile:** `DEFAULT` (token auth). Verify with `databricks auth profiles` and `databricks current-user me`.
- **SQL Warehouse:** *Serverless Starter Warehouse* — id `c5e7e7089978bd43`.

## Catalogs & schemas
- **Source (read-only Marketplace dataset):** `databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset`
  - tables: `facilities` (10,088), `india_post_pincode_directory`, `nfhs_5_district_health_indicators` (706 districts)
- **Gold (ours — write here only):** `workspace.virtue_gold`
  - `gold_facility_capability_trust`, `gold_district_gaps`, `gold_referral`, `gold_data_readiness`, `app_user_actions`

## App
- **Name:** `virtue-desk` — **URL:** `https://virtue-desk-7474648370355072.aws.databricksapps.com`
- **Source path:** `/Workspace/Users/<you>/apps/virtue-desk`
- **Deploy:** `databricks apps deploy virtue-desk --source-code-path <path>` (see README).

## Model Serving (LLM)
- Use **`databricks-llama-4-maverick`** via `WorkspaceClient().serving_endpoints.query(...)`.
- ⚠️ `databricks-claude-opus-4-8` and `databricks-gemini-3-5-flash` are **rate-limited to 0 on Free Edition** — do not use.

## Databricks agent skills
Installed **project-scoped** under `.claude/skills/` (and mirrored at `.databricks/aitools/skills/`) via
`databricks aitools install --scope project --agents claude-code`. These are the official **Databricks** skills —
the `.claude/` path is just where the installer puts them for the Claude Code agent. See [`docs/SKILLS.md`](docs/SKILLS.md).
The 10 installed: `databricks-core`, `databricks-apps`, `databricks-app-design`, `databricks-lakebase`,
`databricks-model-serving`, `databricks-vector-search`, `databricks-jobs`, `databricks-pipelines`, `databricks-dabs`, `databricks-serverless-migration`.

## Conventions (do not break)
1. **Read** from the Marketplace catalog (read-only); **write** only to `workspace.virtue_gold`.
2. **Cite facility text** for every claim; **never present weak evidence as fact.**
3. **LLM calls are on-demand** (button/chat) — never on page load (it blocks the render).
4. Streamlit on Databricks Apps runs **Python 3.11 / Streamlit 1.38** → use `use_column_width` (not `use_container_width`) for `st.image`.
5. Grants: the app service principal needs `USE/SELECT/MODIFY` on `workspace.virtue_gold` + `CAN_USE` on the warehouse + `CAN_QUERY` on the LLM endpoint.
