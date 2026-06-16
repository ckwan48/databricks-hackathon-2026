# Data dictionary — sources & gold tables

## Source datasets (Unity Catalog, read-only Marketplace)

`databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset`

### 1. `facilities` — 10,088 records, 51 columns
The core dataset: scraped Indian healthcare facilities. Treat every field as a **claim to verify**, not ground truth.

| Field | Coverage | Notes |
|---|---|---|
| `name`, `address_*`, `latitude`, `longitude` | 100% | identity + geo (9,996 have a postcode) |
| `specialties` | controlled | JSON array of clinical specialty codes → `spec_hit` |
| `description` | 100% | free text |
| `capability` | 99.7% | claimed capabilities (free text) |
| `procedure` | 92.5% | claimed procedures |
| `equipment` | 77.0% | claimed equipment |
| `numberDoctors` | 36.4% | sparse |
| `capacity` (beds) | 25.2% | sparse |
| `yearEstablished` | 47.8% | sparse |
| `source_types`, `source_urls` | — | provenance: how many independent sources & their pages |
| `cluster_id` | — | pre-computed entity-match key (dedup) |

### 2. `india_post_pincode_directory` — 165,627 offices
`pincode, officename, district, statename, latitude, longitude, …`. Powers **geocoding** (any city/district → centroid) and the facility→district join.

### 3. `nfhs_5_district_health_indicators` — 706 districts, 109 indicators
District-level NFHS-5 health indicators (sanitation, clean fuel, electricity, women's schooling/literacy, child marriage, institutional birth, ANC4, child stunting/wasting/anaemia, women overweight, blood sugar, …). Powers the **causal layer**.

## Gold tables (`workspace.virtue_gold` — ours)

| Table | Grain | Purpose |
|---|---|---|
| `silver_facility` | 1 / facility (deduped) | cleaned, geo-joined, evidence text assembled |
| `gold_facility_capability_trust` | facility × 22 capabilities (≈75k) | the high-stakes trust grades (with contradiction check) |
| `gold_facility_specialty` | facility × every listed specialty (≈118k, 2,580 specialties) | complete-coverage grades |
| `gold_facility_contact` | 1 / facility (9,959) | address, phone, website, beds, doctors, equipment, specialties |
| `gold_district_gaps` | district × 22 capabilities | care-gap classification (acute) |
| `gold_specialty_district_gaps` | district × specialty | care-gap classification (all specialties) |
| `gold_all_gaps` | district × 2,518 capabilities | unified gaps powering Medical Desert |
| `gold_specialty_gap_summary` | specialty | gap counts for the comparison charts |
| `gold_referral` | facility × capability | distance-rankable referral index |
| `gold_specialty_counts` | specialty | dataset-wide specialty frequencies |
| `gold_nfhs` | 706 districts | cleaned numeric NFHS indicators for correlation/causation |
| `gold_pin_state` | state | post-office & pincode coverage |
| `app_user_actions` | append | persisted overrides, shortlists, scenarios, chats (audit log) |

## Grade vocabulary

`STRONG` · `PARTIAL` · `WEAK/SUSPICIOUS` (acute contradiction) · `CLAIMED` (specialty listed only) · `NO CLAIM` (dropped).
`classification`: `APPARENT CARE GAP` · `DATA-POOR` · `EVIDENCED SUPPLY`.

See [`METHODOLOGY.md`](METHODOLOGY.md) and [`CAUSAL_INFERENCE.md`](CAUSAL_INFERENCE.md).
