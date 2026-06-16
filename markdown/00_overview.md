## Overview & How to Read This Report

**What this is:** a complete, from-scratch understanding of three India health datasets — built before any RAG/ontology/causal modeling — covering every column, every unique value, full statistics, correlations with reasoning & confidence, a facility capability-trust engine, geographic gap analysis, and a causal-readiness blueprint.

> ✅ **Complete national data.** `nfhs5.csv` = 706 NFHS-5 district rows (36 states/UTs); `india_post.csv` = 165,627 post offices (full HO/PO/BO hierarchy, 749 districts); `facilities_hack.csv` = 10,088 facilities nationwide. The cross-dataset **join works**: ~86% of NFHS district names match the pincode directory, ~95% of facilities have a pincode in the directory, and ~80% map facility→pincode→district→NFHS. An integrated district table (`data/district_supply_demand.csv`, 706 districts: outcomes + supply) is included.

### The three datasets
| File | Rows×Cols | Grain | Role |
|---|---|---|---|
| `nfhs5.csv` | 706 × 109 | district | health **outcomes & behaviours** (demand) |
| `facilities_hack.csv` | 10,088 × 51 | facility | health **supply / infrastructure** |
| `india_post.csv` | 165,627 × 11 | post office | **geographic backbone** (pincode→district) |

### Keys
- **nfhs**: PK `(state_ut, district_name)` — ⚠️ no district code exists.
- **pincode**: PK `(officename, pincode)` — pincode alone is NOT unique (up to 5 offices share one).
- **facilities**: PK `unique_id`; `cluster_id` = entity-resolution key.
- **Join path**: `facilities.address_zipOrPostcode → pincode → (district,state) → nfhs`.

### The four planning questions this answers
1. **Can a facility do what it claims?** → capability trust grades + confidence badges.
2. **Are the care gaps real?** → trust-weighted gap analysis (real gap vs data-poor).
3. **Where should a patient/coordinator go?** → location+need search prototype.
4. **What must be fixed before planning?** → stewardship review queue + causal-readiness fixes.

### How to navigate
Use the sidebar. Start with the **Unique-Values Catalog** for the complete column inventory, then the NFHS dictionary sections, then Correlations (matrix → reasoning/confidence → better techniques), then the facility product layer, then the causal-readiness blueprint. Data artifacts (CSVs, the search engine `.py`) are in `data/`; figures in `figures/`.
