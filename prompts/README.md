# DevHub Prompt Templates — copy any into a coding agent (Claude Code / Cursor / Codex)

From **developers.databricks.com/templates** — "Copy any template as a prompt for your coding agent to build for you."
Fetch the full prompt from each URL (the page has a **Copy** button), paste it into your agent, then point it at this repo (it will read `AGENTS.md`).

## UI templates (use these to iterate on the app's look & features)
| Template | What it gives | URL |
|---|---|---|
| **Genie Analytics App** ⭐ | Embed **AI/BI Genie** conversational analytics in the app (NL → SQL + charts). Big "uses Databricks well" win. | https://developers.databricks.com/templates/genie-analytics-app |
| **Genie Conversational Analytics** | Embedded Genie chat panel; server+client plugin wiring. | https://developers.databricks.com/templates/genie-conversational-analytics |
| **AI Chat App** | Streaming chat (Model Serving / AI Gateway) + Lakebase-persisted history — upgrade our Copilot. | https://developers.databricks.com/templates/ai-chat-app |
| **Spin Up a Databricks App** | Scaffold a fresh AppKit (React/TS) app with `databricks apps init`. | https://developers.databricks.com/templates/spin-up-a-databricks-app |

## Persistence / data templates
| Template | What it gives | URL |
|---|---|---|
| **App with Lakebase** ⭐ | Wire a Databricks App to **Lakebase Postgres** for persistence + full CRUD (see `../notebooks/lakebase_setup.py`). | https://developers.databricks.com/templates/app-with-lakebase |
| **Hackathon App with Synced Dataset** | The official hackathon starter: App + Lakebase + UC→Lakebase **synced tables** (sub-10ms). | https://developers.databricks.com/templates/hackathon-app-with-synced-dataset |
| **Lakebase pgvector** | Vector similarity search in Lakebase — RAG over facility text. | https://developers.databricks.com/templates/lakebase-pgvector |
| **Operational Data Analytics** | UC + Lakebase + CDC + medallion (silver/gold). | https://developers.databricks.com/templates/operational-data-analytics |
| **Sync Tables: UC → Lakebase** | Sync our gold tables into Lakebase for low-latency app reads. | https://developers.databricks.com/templates/sync-tables-autoscaling |

## AI / model templates
| Template | URL |
|---|---|
| **Query AI Gateway Endpoints** | https://developers.databricks.com/templates/foundation-models-api |
| **Streaming AI Chat with Model Serving** | https://developers.databricks.com/templates/ai-chat-model-serving |
| **Create a Model Serving endpoint** | https://developers.databricks.com/templates/model-serving-endpoint-creation |

## Setup
| Template | URL |
|---|---|
| **Set Up Your Local Dev Environment** | https://developers.databricks.com/templates/set-up-your-local-dev-environment |
| **Onboard Your Coding Agent** (`databricks aitools install`) | https://developers.databricks.com/templates/onboard-your-coding-agent |

> Full index of every DevHub doc/template: https://developers.databricks.com/llms.txt
