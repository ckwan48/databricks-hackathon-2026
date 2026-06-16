## Data-Quality Stewardship & Human-Review Queue

Scope: all 10,088 facility records (10,077 distinct `unique_id`, 9,959 distinct `cluster_id`, i.e. ~129 rows are near-duplicates collapsible by entity-resolution key). `'null'`/empty treated as missing throughout. The review queue (`review_queue.csv`) holds **9,983 of 10,088 records (99.0%) with at least one issue**; the dominant issue is taxonomy noise (see below), but **3,908 records (38.7%) carry a true contradiction** beyond simple sparsity. An independent cross-check against the capability trust table agrees in spirit: it flags **1,445 capability claims across 1,030 facilities** with `contradiction_flag=True`.

### 1. Contradictions (with real rows)

| Contradiction class | # records | Notes |
|---|---:|---|
| `numberDoctors` present but `capacity` null/0 | 2,301 | bed count missing for staffed facilities |
| `capacity` present but `numberDoctors` null/0 | 1,188 | beds without staffing |
| Clinic claims high-acuity (ICU/NICU/oncology/cardiac/neuro/transplant) | 620 | capability text vs `facilityTypeId=clinic` |
| Within-row duplicate specialty entries (see Taxonomy) | 9,849 | structural taxonomy noise |
| Dentist with internalMedicine-heavy specialties (>=3) | 24 | mislabeled type or polyclinic |
| Low-acuity type (clinic/dentist) claiming >=30 distinct specialties | 20 | implausible breadth for a clinic/dentist |
| `yearEstablished` implausible (<1800 or >2026) | 13 | e.g. value `15` |
| `address_countryCode` != IN (non-corrupt rows) | 10 | India-addressed but foreign code |
| Coordinates outside India bbox (lat 6-37, lon 68-98) | 6 | wrong/garbage geocodes |
| Structural CSV column-shift corruption | 19 | embedded delimiters broke row parsing |

**Example contradiction rows (top of queue):**

- **Hande Medical Centre**, Chennai (TN) — `facilityTypeId=clinic` but lists **31 specialties**, claims **ICU + oncology + cardiac surgery + neurosurgery**, 8 doctors with **no bed capacity**, and 19 duplicate specialty entries. Priority 100.0.
- **Attingal (Medical Centre)**, Trivandrum (Kerala) — `clinic` with **580 beds but zero doctors**, **35 specialties**, claims ICU/NICU/oncology/cardiac surgery. Priority 99.3.
- **Sparkle Dental Care**, Ranchi (Jharkhand) — name says dental, typed `clinic`, claims **NICU + oncology + neurosurgery** across 31 specialties. Priority 93.4.
- **OrthoSquare**, Navi Mumbai — `facilityTypeId=dentist` yet has **9 internalMedicine specialty tags** and claims **oncology**; 28 duplicate entries. Priority 86.5.
- **Dr Alis Denta Care**, Bangalore — `dentist` claiming **neurosurgery** with internalMedicine-heavy tags. Priority 73.1.

**Coordinate / geo errors (all 6):**

| Name | City / State | lat | lon | Issue |
|---|---|---:|---:|---|
| Sanjivani Multi Speciality Hospital | Chengannur / Alappuzha | 59.95 | -38.26 | North Atlantic — confirms the known Kerala-at-lat-60 case |
| Krishna Hospital Multispeciality | Lucknow / Uttar Pradesh | -81.71 | 26.95 | lat below valid range (sub-antarctic) |
| Cardia Health Care | Noida / Uttar Pradesh | 7.71 | 109.69 | lon past India's eastern edge |
| The Family Tree Hospital | Tirupati / Andhra Pradesh | 32.96 | 7.48 | lon in N. Africa |
| Hzb Arogyam Multispeciality | Hazaribagh / Jharkhand | 46.07 | 106.17 | Mongolia |
| Cura Imaging & Gastro Clinic | Nagpur / Maharashtra | 2.95 | 41.39 | Horn of Africa |

No clean lat/lon-swap cases were found (swapping any of the six does not land it inside India), so these need re-geocoding from address rather than a coordinate transpose.

### 2. Sparse Fields — fill-rate table

Full table in `fill_rate.csv`. Sparsest and core fields:

| Column | Filled | Fill % |
|---|---:|---:|
| countries | 28 | 0.3 |
| acceptsVolunteers | 42 | 0.4 |
| area | 129 | 1.3 |
| affiliationTypeIds | 1,249 | 12.4 |
| **capacity** | 2,520 | 25.0 |
| number_of_facts_about_the_organization | 2,757 | 27.3 |
| recency_of_page_update | 3,546 | 35.2 |
| **numberDoctors** | 3,633 | 36.0 |
| post_metrics_post_count | 3,785 | 37.5 |
| **yearEstablished** | 4,804 | 47.6 |
| officialWebsite | 8,421 | 83.5 |
| email | 8,570 | 85.0 |
| operatorTypeId | 9,327 | 92.5 |
| phone_numbers | 9,748 | 96.6 |
| latitude / longitude | 9,970 | 98.8 |
| facilityTypeId | 9,962 | 98.8 |
| name / address_city / state / PIN | ~10,023 | ~99.4 |

Core identity/location/contact fields are well-filled (>96%); the operational fields used for trust scoring — `capacity` (25%), `numberDoctors` (36%), `yearEstablished` (48%) — are the weak points. 118 records are missing one or more core identity/location/contact fields and are flagged in the queue with a `missing:` tag.

### 3. Taxonomy Issues & Recommended Normalization

**Within-row duplication is the single largest data-quality defect: 9,849 of 9,972 records with specialties (98.8%) repeat a code, totaling 160,768 duplicate entries.** This badly inflates the apparent breadth of every facility and corrupts any specialty-count signal (e.g. the "30+ specialties" contradiction). **Recommendation: dedupe specialty arrays per row before any downstream use.**

**Synonym / overlapping codes** (codeA count, codeB count, rows containing both) — these should be merged to a canonical code:

| Pair (recommend keep <- drop) | A count | B count | Rows with both |
|---|---:|---:|---:|
| internalMedicine <- generalMedicine | 251 | 6,847 | 248 |
| gynecologyAndObstetrics <- gynecology | 365 | 4,497 | 281 |
| anesthesiology <- anesthesia | 1,323 | 163 | 72 |
| orthopedicSurgery <- orthopedics | 44 | 3,526 | 30 |
| otolaryngology <- ent | 38 | 2,702 | 22 |
| pediatrics <- paediatrics | 24 | 3,438 | 17 |
| dentistry <- dental | 15 | 4,195 | 10 |
| gynecologyAndObstetrics <- obstetrics | 4 | 4,497 | 4 |
| cardiology <- cardiac | 1 | 3,015 | 1 |

Where both members of a pair co-occur on a row (e.g. 248 rows with both generalMedicine and internalMedicine), the duplication is double-counted. Recommended normalization: (a) deduplicate within-row, (b) apply a synonym-collapse map (above), (c) re-validate specialty-count-based contradiction flags afterward.

### 4. Top-15 Human-Review Queue

Priority = risk-severity (weighted by contradiction type) amplified by log-scaled popularity (followers/posts/likes/facts/social presence), normalized 0-100. Full ranked list in `review_queue.csv` (9,983 rows).

| # | Priority | Name | City / State | Key issues | Suggested action |
|---:|---:|---|---|---|---|
| 1 | 100.0 | Hande Medical Centre | Chennai / TN | clinic, 31 specialties, ICU+oncology+cardiac+neuro, 8 docs/0 beds | Reclassify type or downgrade claims; verify |
| 2 | 99.3 | Attingal (Medical Centre) | Trivandrum / Kerala | clinic, 580 beds/0 docs, 35 specialties, ICU/NICU/oncology | Reclassify type or downgrade claims; verify |
| 3 | 93.4 | Sparkle Dental Care | Ranchi / Jharkhand | clinic, NICU+oncology+neurosurgery, 31 specialties | Reclassify type or downgrade claims; verify |
| 4 | 93.4 | Sarthak Nursing Home | Agra / UP | clinic, 32 beds/0 docs, 35 specialties, NICU/oncology | Reclassify type or downgrade claims; verify |
| 5 | 90.7 | N.G. Nursing Home, Kalighat | Kolkata / WB | clinic, 38 specialties, ICU, 1 doc/0 beds | Reclassify type or downgrade claims; verify |
| 6 | 89.5 | Rathna Medical Centre | Coimbatore (RS Puram) / TN | clinic, 33 specialties, NICU+oncology | Reclassify type or downgrade claims; verify |
| 7 | 86.5 | OrthoSquare | Navi Mumbai | dentist, internalMedicine x9, claims oncology | Reclassify type or downgrade claims; verify |
| 8 | 85.7 | Aarogya Super Speciality Homoeopathic Clinic | Indore / MP | clinic, 32 specialties, neurosurgery+transplant | Reclassify type or downgrade claims; verify |
| 9 | 85.2 | Dispur Polyclinic & Nursing Home | Guwahati / Assam | clinic, 33 specialties, ICU+oncology | Reclassify type or downgrade claims; verify |
| 10 | 82.9 | Medini Cosmetic Surgery Centre, KPHB | Hyderabad / Telangana | yearEstablished=15, clinic claims ICU | Reclassify type or downgrade claims; verify |
| 11 | 81.2 | Gleneagles Clinic, Adyar | Chennai / TN | clinic, 37 specialties, NICU+oncology, 15 docs/0 beds | Reclassify type or downgrade claims; verify |
| 12 | 81.0 | Olivia Nursing Home & Diagnostic Centre | Kolkata / WB | clinic, 31 specialties, ICU+oncology, 20 docs/0 beds | Reclassify type or downgrade claims; verify |
| 13 | 79.3 | SH Medical Centre | Kottayam / Kerala | clinic, 250 beds/0 docs, 33 specialties, ICU/NICU | Reclassify type or downgrade claims; verify |
| 14 | 77.7 | Balaji Healthcare | Siliguri / WB | clinic, 35 specialties, oncology+neurosurgery | Reclassify type or downgrade claims; verify |
| 15 | 73.1 | Dr Alis Denta Care | Bangalore / Karnataka | dentist claiming neurosurgery, internalMedicine-heavy | Reclassify type or downgrade claims; verify |

**Pattern:** the top of the queue is dominated by *nursing homes / medical centres / polyclinics mis-typed as `clinic`* that legitimately offer broad services but are over-claiming the most serious capabilities — these are the highest-leverage records because they are both popular and risky. The cleanest single fix (reclassifying these from `clinic` to `hospital`/`nursing_home` and deduplicating specialties) would resolve a large share of both the contradiction and taxonomy issues at once.

### Artifacts
- `review_queue.csv` — full 9,983-row ranked queue (unique_id, name, city, state, priority_score, issues, suggested_action).
- `fill_rate.csv` — per-column fill rate (all 51 columns).
- `stewardship_analysis.py` — reproducible analysis script.
