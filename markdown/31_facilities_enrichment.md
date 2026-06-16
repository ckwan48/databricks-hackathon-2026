## Health Facilities — Enrichment, Clinical, Social & Geospatial Profile

Scope: `facilities_hack.csv` — **10,088 health facilities** nationwide (complete national dataset, not a sample), produced by an enriched/scraped pipeline (web + Overture + `kie` sources). This section profiles the enrichment, clinical, social-media and geospatial columns. All figures are computed over the full 10,088 rows and are national in scope.

### Headline findings

- **Clinical content is well-populated but capped.** Clinical-detail array columns are filled for ~98–99% of facilities, but every array is truncated at exactly **50 items**, so high-end counts are pipeline caps rather than true totals.
- **Operational numerics are sparse.** `numberDoctors` is present for only 36.0% of rows and `capacity` for 25.0%; `area` is essentially anecdotal at **1.3%** fill (126 usable numeric rows).
- **Social/engagement footprint is broad but shallow.** 88.1% of facilities carry a follower count, but the median is only **244 followers** and the median `post_metrics_post_count` is **0** — most facilities have a discoverable handle with little activity. 1,174 facilities (11.6%) have no social engagement metric at all.
- **Geocoding is 99.94% sound but has 6 hard errors**, including a Kerala (Alappuzha) hospital plotted in the **North Atlantic at lat 59.95 / lon -38.26** and a row at **lat -81.7** (Antarctic latitude). The `coordinates` JSON matches the lat/lon columns exactly (0 mismatches), so these are source-data errors, not parsing artifacts.
- **A handful of rows are structurally misaligned** (CSV field shift): hash IDs and JSON arrays leaked into `source`, `numberDoctors`, `capacity`, `area`, `affiliated_staff_presence`, and `custom_logo_presence`; a longitude value (79.53) even landed in `distinct_social_media_presence_count`.

### Data dictionary (assigned columns)

| Column | Meaning | Type | Fill-rate | Notes |
|---|---|---|---|---|
| description | Free-text facility blurb | str | 99.2% | 9,577 distinct; median 115 chars, max 6,557 |
| area | Built/site area (sq ft) | str→num | 1.3% | Only 126 numeric rows; 3 rows hold leaked JSON/hash |
| numberDoctors | Doctor headcount | str→num | 36.0% | Median 2, p90 40, max 15,000 (implausible) |
| capacity | Bed capacity | str→num | 25.0% | Median 100, max 200,000 (implausible) |
| specialties | JSON array of specialty codes | json[] | 98.9% | Median 24 items/row, **capped at 50**; 2,932 distinct labels |
| procedure | JSON array of procedure descriptions | json[] | 98.6% | Median 10 items; 1,093 rows have 0 items |
| equipment | JSON array of equipment items | json[] | 97.8% | Median 2 items; 2,744 rows have 0 items (sparsest array) |
| capability | JSON array of capability statements | json[] | 98.8% | Median 19 items; 34 rows have 0 items |
| recency_of_page_update | Last-update date of source page | date | 35.2% | Range 2003→2027; 2,241 rows in 2025; 1 future date (2027-07-20) |
| distinct_social_media_presence_count | # of distinct social platforms | float | 98.8% | Mode 5 (2,737 rows); 434 rows = 0; 1 corrupt value 79.53 |
| affiliated_staff_presence | Whether affiliated staff are listed | bool(str) | 98.7% | true 9,260 / false 697; 2 corrupt ('24', a hash) |
| custom_logo_presence | Whether facility has a custom logo | bool(str) | 95.3% | true 8,611 / false 998; 2 corrupt ('3', a JSON URL array) |
| number_of_facts_about_the_organization | Count of extracted org facts | float | 27.3% | Median 5, p99 31, max 442 |
| post_metrics_most_recent_social_media_post_date | Date of latest social post | date | 48.9% | Range 2009→2026-01; no future dates; peak 2024 (1,514) |
| post_metrics_post_count | Count of social posts | str→num | 37.5% | Median 0, p99 271, max 59,000 |
| engagement_metrics_n_followers | Follower count | str→num | 88.1% | Median 244, p99 35,324, max 15,000,000 (suspect) |
| engagement_metrics_n_likes | Like count | float | 77.3% | Median 69, p99 18,000, max 384,000 |
| engagement_metrics_n_engagements | Engagement count | float | 48.5% | Median 0, p99 2,776, max 121,855 |
| source | Provenance tag | str | 98.8% | 'kie' = 9,970; 1 corrupt (hash); 117 null |
| coordinates | GeoJSON `{coordinates:[lon,lat],type:Point}` | json | 98.8% | Matches lat/lon cols exactly (0 mismatches) |
| latitude | Latitude (decimal deg) | float | 98.8% | 9,964 in India bbox; 6 outside |
| longitude | Longitude (decimal deg) | float | 98.8% | See coordinate-anomaly subsection |
| cluster_id | Dedup cluster key (UUID) | str | 98.8% | 9,959 distinct; 11 clusters have 2 rows (intra-file dups) |
| source_urls | JSON array of evidence URLs | json[] | 98.8% | Median 8 URLs/row, capped at 50; 0 parse failures |

### Clinical content (specialties / procedure / equipment / capability)

All four clinical arrays parse cleanly (2–3 parse failures each, traced to the misaligned rows below). Item counts per row:

| Array | Median items | Mean | Max | Rows with 0 items |
|---|---|---|---|---|
| specialties | 24 | 28.0 | 50 | 0 |
| capability | 19 | 23.3 | 50 | 34 |
| procedure | 10 | 16.5 | 50 | 1,093 |
| equipment | 2 | 5.7 | 50 | 2,744 |
| source_urls | 8 | 15.9 | 50 | 0 |

The hard **50-item ceiling** on every array means richer facilities are under-counted; treat 50 as "≥50." `equipment` is the weakest clinical field — 2,744 facilities (27%) list no equipment at all.

**Top 15 specialties** (facilities listing the specialty at least once; 2,932 distinct labels total, median 10 distinct specialties/facility):

| # | Specialty | Facilities |
|---|---|---|
| 1 | internalMedicine | 6,847 |
| 2 | familyMedicine | 5,178 |
| 3 | gynecologyAndObstetrics | 4,497 |
| 4 | dentistry | 4,192 |
| 5 | orthopedicSurgery | 3,526 |
| 6 | pediatrics | 3,438 |
| 7 | generalSurgery | 3,198 |
| 8 | cardiology | 3,011 |
| 9 | radiology | 2,999 |
| 10 | ophthalmology | 2,828 |
| 11 | otolaryngology | 2,702 |
| 12 | urology | 2,628 |
| 13 | gastroenterology | 2,422 |
| 14 | dermatology | 2,330 |
| 15 | pathology | 2,251 |

### Operational numerics (numberDoctors / capacity / area)

| Metric | n (numeric) | Min | Median | Mean | p90 | p99 | Max |
|---|---|---|---|---|---|---|---|
| numberDoctors | 3,630 | 0 | 2 | 31.7 | 40 | 409 | 15,000 |
| capacity (beds) | 2,517 | 0 | 100 | 270.4 | 500 | 1,668 | 200,000 |
| area (sq ft) | 126 | 0 | 5,525 | 63,812 | 170,000 | 1,046,093 | 1,125,000 |

Outliers (almost certainly data errors):
- **numberDoctors:** Nithya Hospital = 15,000; Kims Hospital = 6,000; Scientific Pathology = 5,000; Vijaya / Megavision Diagnostic Centres = 3,000 each. These dwarf the median of 2 and are implausible.
- **capacity:** Harsh Hospital = **200,000 beds** (impossible) vs the next value King George's Medical University = 4,000. Anything above ~3,000 is suspect.
- **area:** Kasturba Hospital (Manipal) = 1,125,000; AIIMS Bibinagar = 809,372 — likely full-campus sq ft, not facility footprints.

### Social media & engagement

| Metric | n | Median | Mean | p90 | p99 | Max |
|---|---|---|---|---|---|---|
| distinct_social_media_presence_count | 9,966 | 4 (mode 5) | — | 6 | 9 | 11 (valid) |
| post_metrics_post_count | 3,784 | 0 | 44.1 | 3 | 271 | 59,000 |
| n_followers | 8,884 | 244 | 8,057 | 2,600 | 35,324 | 15,000,000 |
| n_likes | 7,801 | 69 | 1,194 | 1,800 | 18,000 | 384,000 |
| n_engagements | 4,888 | 0 | 156 | 93 | 2,776 | 121,855 |

- **1,174 facilities (11.6%)** have no follower, like, or engagement value at all; **434 (4.3%)** report `distinct_social_media_presence_count = 0`.
- Distribution is heavily right-skewed: mean followers (8,057) is ~33× the median (244), driven by a few viral/aggregated handles.
- **Follower outliers look erroneous:** J J Eye Hospital and Shiromany Dental Care both show **15,000,000 followers**, and three unrelated facilities (Kidwai Memorial, Fortis Hospital, Shankar Super Speciality) all share the identical **4,756,342** — a tell-tale sign of a single aggregator/page attributed to multiple facilities.
- **post_count outliers:** Rajagiri Hospital and "The Liver Unit … Kochi" both = 59,000; AIIA New Delhi = 8,710.
- Engagement timeliness: most-recent post dates peak in **2024 (1,514 rows)** then drop in 2025 (560) — the scrape captured most pages before 2025 activity accrued. Page-update recency is fresher: **2,241 of 3,532 (63%) updated in 2025**.

### Deduplication (cluster_id)

`cluster_id` is the dedup key: 9,970 non-null rows resolve to **9,959 distinct clusters**. **11 clusters contain 2 rows each** (max cluster size 2) — i.e. ~11 intra-file duplicate pairs survived clustering, e.g. "MOSC Medical College Hospital," "Trustwell Hospitals," and "Yadgire Super Specialty Hospital" each appear twice. `unique_id` likewise has only 10,077 distinct values across 10,088 rows (11 collisions). Net: the file is ~99.9% deduplicated but not perfectly.

### Data-quality & coordinate anomalies

**Coordinate validation (India bbox lat 6–37, lon 68–98):** Of 9,970 rows with coordinates, **9,964 (99.94%) fall inside India**; the `coordinates` GeoJSON matches the latitude/longitude columns on every row (0 mismatches). **6 rows are outside the bbox** — genuine source errors:

| Name | Claimed location | latitude | longitude | Problem |
|---|---|---|---|---|
| Sanjivani Multi Speciality Hospital | Alappuzha, Kerala | 59.95 | -38.26 | **North Atlantic** (off Greenland) |
| Krishna Hospital Multispeciality | Lucknow, UP | -81.71 | 26.95 | **Antarctic** latitude |
| Hzb Arogyam Multispeciality Hospital | Hazaribagh, Jharkhand | 46.07 | 106.17 | Mongolia |
| The Family Tree Hospital | Tirupati, Andhra Pradesh | 32.96 | 7.48 | Mediterranean / N. Africa |
| Cardia Health Care | Noida, UP | 7.71 | 109.69 | South China Sea |
| Cura Imaging & Gastro Clinic | Nagpur, Maharashtra | 2.95 | 41.39 | Off Somalia (Indian Ocean) |

- The Kerala→North Atlantic row is a **duplicate of a valid Indian record**: a second "Sanjivani Multi Speciality Hospital" exists at lat 20.91 / lon 70.36 (valid). One copy was geocoded correctly, the other catastrophically.
- **No clean lat/lon swap detected** (0 rows with lat in 68–98 and lon in 6–37), so these are not simple axis transpositions — they are bad geocodes, not column swaps.
- No `lat==0`/`lon==0` null-island rows.

**Structural field-misalignment (CSV field shift)** — a small number of rows carry non-conforming values leaking across columns, almost certainly from unescaped commas/quotes in scraped JSON:
- 1 row has `source` = a 32-char hex hash (`08f60a89…`) instead of `kie`; same row has `affiliated_staff_presence='24'`, `custom_logo_presence='3'`, name = `""cataractAndAnteriorSegmentSurgery""`, and all geo fields null.
- `affiliated_staff_presence` has 2 non-boolean values (`'24'`, a hash); `custom_logo_presence` has 2 (`'3'`, a JSON URL array).
- `distinct_social_media_presence_count` has one corrupt value **79.53** (a longitude that shifted into the count field).
- `numberDoctors`, `capacity`, and `area` each have 3 non-numeric values that are actually leaked JSON arrays (equipment/procedure lists, source-URL arrays) or hashes.
- `specialties` / `procedure` / `equipment` / `capability` each have 2–3 JSON parse failures attributable to these same shifted rows.

**Temporal sanity:** `recency_of_page_update` contains **1 future date (2027-07-20)** and a few implausibly old ones (2003); these should be flagged. `post_metrics_most_recent_social_media_post_date` has no future dates (max 2026-01-22).

**Recommended cleaning before downstream use:** (1) drop/repair the ~3 structurally shifted rows; (2) cap or null `numberDoctors > ~3,000`, `capacity > ~3,000`, and `n_followers ≥ 4.7M`; (3) flag the 6 out-of-bbox geocodes and de-duplicate the 11 surviving cluster pairs; (4) treat any array length of 50 as a right-censored "≥50."
