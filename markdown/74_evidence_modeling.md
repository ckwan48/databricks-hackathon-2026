## Evidence-Confidence Modeling

A data scientist consuming this scrape needs to know *how much to trust each row*. This section adds that layer: a defensible source-reliability weighting, a 0-100 evidence-completeness score with its full formula and distribution, recency/decay handling, the cluster-based dedup mechanism, and the social-corroboration signal. All numbers are computed over the full **10,088-row** national file (`facilities_hack.csv`, pipeline `source='kie'`); the per-facility scores are saved to `/Users/koushik/Desktop/health_analysis_outputs/facility_completeness_scores.csv` and the reproducible scorer to `/Users/koushik/Desktop/health_analysis_outputs/evidence_scoring.py`.

### 1. Source-reliability weighting

`source_types` is a multiset (162,020 `overture` tokens, 82,952 `dynamic`, 20,669 `constant`, 5,955 `mongo_facility`, and **1,121 `mongo_ngo`** — a 5th type not listed in the brief). What matters for confidence is not raw token count but the **set of distinct provenances** independently attesting to a facility. Proposed weights and rationale:

| source_type | Present in | % of rows | Likely meaning | Reliability weight | Rationale |
|---|---:|---:|---|---:|---|
| `mongo_facility` | 1,124 | 11.1% | Curated internal facility master DB record | **1.00** | Human/operationally curated; rarest and most authoritative. |
| `constant` | 3,393 | 33.6% | Stable, slow-changing scraped attributes (name/address/geo) | **0.85** | Structurally stable fields; low churn = high trust. |
| `mongo_ngo` | 228 | 2.3% | NGO-registry-sourced record | **0.75** | Registry-backed, but NGO scope may not equal a clinical facility. |
| `overture` | 9,165 | 90.9% | Overture Maps open basemap POI / geo backbone | **0.70** | Broad coverage and geo, variable clinical depth; main geo-noise source. |
| `dynamic` | 6,942 | 68.8% | Dynamically scraped web/page/social content | **0.60** | Rich but volatile and parse-prone; best as corroboration, not standalone. |

A facility's **provenance factor** anchors on its single most trusted source and adds a corroboration bonus for independent sources: `W_prov = max(weights present) + 0.05 * (n_distinct_source_types - 1)`, capped at 1.0. Importantly, `officialWebsite` fill is ~83-87% no matter which source is present (overture 84%, dynamic 84%, constant 85%, mongo_facility 83%, mongo_ngo 87%), so no source is "contact-poor" — confidence differentiation comes from **clinical depth and provenance diversity**, not contact fields.

**Provenance diversity strongly predicts richer evidence.** Distinct source_types per facility: 116 rows have 0, 3,051 have 1, 3,603 have 2, 2,698 have 3, 599 have 4, and 21 have 5. Mean evidence counts rise monotonically with diversity:

| n distinct source_types | rows | mean specialties | mean procedures | mean equipment | mean source_urls |
|---:|---:|---:|---:|---:|---:|
| 1 | 3,051 | 7.1 | 11.3 | 2.8 | 6.0 |
| 2 | 3,603 | 11.6 | 16.5 | 5.4 | 14.0 |
| 3 | 2,698 | 16.2 | 21.7 | 9.4 | 27.0 |
| 4 | 599 | 18.0 | 23.4 | 11.0 | 32.5 |
| 5 | 21 | 19.6 | 26.0 | 11.9 | 37.4 |

Spearman correlations confirm it: diversity vs distinct `source_urls` **+0.70**, vs distinct specialties **+0.47**, vs equipment **+0.35**, vs procedures **+0.27**. **Caveat:** `number_of_facts_about_the_organization` is statistically *independent* of source diversity (Spearman ~0.005) and of every evidence-count field — it is a separate descriptive-richness signal (populated for only 27.3% of rows; median 5, mean 6.7, max 442), not a proxy for provenance breadth. The two are therefore scored as distinct components below.

### 2. Evidence-completeness score (0-100)

A composite of five weighted components. Array fields are JSON-parsed (`'null'`/`[]`/`{}` treated as empty; dict-valued specialty entries de-duplicated by canonical JSON). `cap(x, pts, c) = min(x, c)/c * pts` is a saturating contribution.

```
COMPLETENESS = IDENTITY(30) + CLINICAL(25) + PROVENANCE(20) + FACTS(10) + SOCIAL(15)

IDENTITY (max 30, contact verifiability):
   name 5 + has_phone 6 + has_website 6 + email 5 + (city & state) 4 + PIN 4
CLINICAL (max 25, depth):
   cap(n_specialties,8,15) + cap(n_procedures,7,20)
   + cap(n_equipment,5,10) + cap(n_capability,5,10)
PROVENANCE (max 20):
   (n_distinct_source_types/5)*14 + cap(n_distinct_source_ids,6,8)
FACTS (max 10):
   cap(number_of_facts,10,15)
SOCIAL (max 15):
   cap(presence_count,5,6) + min(log10(followers+1)/log10(1e6),1)*6
   + 4 if a social post within the last 730 days
score = clip(sum, 0, 100)
```

**Distribution (all 10,088 rows):** mean **58.9**, std 12.4, min 0, max **93.9**. Percentiles: p10 44.2, p25 50.5, **p50 58.3**, p75 67.6, p90 75.4, p95 79.2, p99 84.6. Component means reveal where evidence is thin: IDENTITY **28.9/30** (contact data is excellent), CLINICAL 15.2/25, PROVENANCE 8.6/20, SOCIAL 5.2/15, and **FACTS just 1.0/10** (72.7% of rows have no fact count). The biggest confidence levers are therefore provenance breadth and clinical depth — not contact info, which is near-universal.

**Best-evidenced facilities:** Aravind Eye Hospital, Hyderabad (**93.9**); Sri Sathya Sai Institute of Higher Medical Sciences, Puttaparthi (92.4); Apollo Hospital CBD Belapur, Mumbai (91.0); SUM Hospital, Bhubaneswar (90.9); Sakra World Hospital, Bengaluru (90.7); Yashoda Cancer Hospital, Ghaziabad (90.4); Fortis Escorts Hospital, Faridabad (90.3).

**Worst-evidenced:** the rows that failed to populate at all — at least **8 rows score 0.0** with null `name`/`address`. These coincide with the ~38 rows whose array fields are unparseable (embedded CSV corruption) and the 117 rows with null pipeline `source`. Quarantine, do not delete.

### 3. Recency / confidence decay

Two staleness signals, both **partial and noisy**:
- `recency_of_page_update`: ISO dates, parseable for **3,532 / 10,088** rows (35%). Median page age vs the 2026-06-15 run date is **1.08 yr**, mean 1.98 yr, p90 5.2 yr. One row is corrupt/future-dated (`2027-07-20`) and must be clamped.
- `post_metrics_most_recent_social_media_post_date`: parseable for **4,914** rows (49%). Median post age **2.89 yr**, mean 3.63 yr, p90 7.2 yr. Freshness buckets: only **115** posted within 180 days, 193 within 6-12 months, 1,268 at 1-2 yr, and **3,338 (68% of dated rows) older than 2 years** — social activity is broadly stale.

**Confidence-decay idea:** multiply a row's confidence by an exponential freshness factor `decay = exp(-age_years / τ)`, with τ≈2 yr for social signals and τ≈4 yr for page updates (structural facts decay slower than social activity). Because ~half of rows have *no* parseable date, apply decay only where a date exists and assign missing-date rows a neutral prior (decay ≈ 0.7) rather than penalizing them as fully stale. The SOCIAL component already bakes in a coarse version of this via its "+4 if posted within 730 days" recency bonus.

### 4. Dedup — the cluster_id mechanism

`cluster_id` is the cross-source entity-resolution key: rows sharing it are the same real-world facility reconciled across sources, so the pipeline can collapse harvested copies into one entity. **Contrary to the brief's "all distinct in sample" assumption, this file is NOT dedup-clean** — 10,088 rows reduce to **9,959 distinct cluster_ids**, leaving **129 excess rows** to merge (11 clusters carry 2 rows each as true duplicate pairs, plus rows with degenerate/null keys). The mechanism is also visible *within* a single row: the lead record (Aravind Eye Hospital) carries 50+ phone entries and dozens of `source_ids`/`source_urls` from overture/dynamic/constant/mongo crawls stitched into one entity. **Strategy at full scale:** `groupby(cluster_id)`, keep the **max completeness** per cluster, union the array evidence fields, and resolve scalar conflicts by **source-reliability weight** (`mongo_facility` > `constant` > `mongo_ngo` > `overture` > `dynamic`).

### 5. Social corroboration as an "operating facility" signal

A live follower base plus recent posts is independent evidence a facility actually operates. **7,693 rows have >0 followers** (median among those: 449), **273 have ≥10,000 followers**, and median `distinct_social_media_presence_count` is 4. Useful corroboration — but with severe outliers that must be capped before use:
- **J J Eye Hospital (Mumbai)** and **Shiromany Dental Care (Agra)** both report exactly **15,000,000 followers**, and three facilities (Kidwai Oncology, two Bangalore "Fortis"/"Shankar" rows) report an identical **4,756,342** — repeated round/identical values are scraper artifacts, not real audiences. This is why SOCIAL uses a log-compressed, saturating `min(log10(followers+1)/6, 1)` transform on followers rather than raw counts.
- `distinct_social_media_presence_count` has a non-integer max of **79.5**, another parse artifact to clamp.

Treat social corroboration as a **bonus, never a gate**: a high-completeness hospital with zero social presence is still credible, while a sparse row with a verified, recently-active social presence gains confidence it would otherwise lack.

### Caveats (carry into downstream use)
- ~38 rows have unparseable array fields, 117 have null pipeline `source`, and 8+ rows are fully empty (score 0) — quarantine these.
- Only 35% of rows have a parseable page-update date and 49% a social-post date, so recency confidence is unavailable for roughly half the file.
- Follower/likes/presence fields contain capped or duplicated sentinel values (15M, 4.76M, 79.5) — always transform, never use raw.
- The component weights (30/25/20/10/15) are a defensible default, not calibrated against ground truth; tune them if a labeled "verified-facility" set becomes available.
- Coordinate corruption persists (e.g., a Kerala-addressed hospital plotted at lat ~60/lon ~-38 in the North Atlantic); gate geo-dependent confidence on the India bbox (lat 6-37, lon 68-98).
