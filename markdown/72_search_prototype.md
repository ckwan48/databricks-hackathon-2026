## 7.2 Location + Care-Need Search Prototype

A working, self-contained triage search over the full national dataset
(10,088 facilities; 9,959 distinct `cluster_id` entities after dedupe). Given a
free-text **location** and **care need**, it returns an evidence-attached,
trust-ranked shortlist of facilities. Runnable artifact:
`/Users/koushik/Desktop/health_analysis_outputs/facility_search.py`
(reads `facilities_hack.csv`; demo output captured in
`facility_search_demo_output.txt`).

### Function design — `search(location, need, k=10)`

1. **Need -> capability mapping.** Free text is normalized and matched
   (longest-phrase-wins) against a `NEED_MAP` lexicon covering all 9 required
   needs: dialysis/renal, emergency / emergency surgery, maternity/delivery,
   NICU/neonatal, ICU/critical care, oncology/cancer, trauma/orthopedic,
   pediatrics, cardiology. Seven of these map to the pre-built trust capability
   labels; **pediatrics and cardiology have no dedicated trust capability**, so
   they fall back to raw-column keyword matching (graded PARTIAL) over
   `specialties / capability / procedure / equipment / description`.

2. **Candidate selection (at-least-PARTIAL evidence).** Candidates are pulled
   from `facility_capability_trust.csv` (70,616 rows = 10,088 facilities x 7
   capabilities), keeping only rows graded **STRONG or PARTIAL** for the target
   capability. `WEAK/SUSPICIOUS` and `NO CLAIM` are excluded.

3. **Ranking — trust first, then proximity.** Sort key is
   `(grade_rank, distance_km)` with STRONG (0) before PARTIAL (1). Proximity is
   the haversine distance from the query-city centroid to each facility's
   `(latitude, longitude)`. Coordinates outside the India bbox (lat 6-37,
   lon 68-98) or null are treated as unknown distance and sink to the bottom of
   their grade band (not dropped — they may still be valid facilities with bad
   geocodes).

4. **Geocoder.** A built-in dict of 42 city keys (incl. **Jaipur, Patna** and
   every high-volume city in the data) uses **data-derived median centroids**,
   so query points line up with the points being ranked. Aliases handled
   (Bengaluru->Bangalore, Vizag->Visakhapatnam, Gurugram->Gurgaon, etc.).

5. **Output.** Each hit carries: name, city/state, grade, evidence snippets
   (the actual trust-table evidence string), distance_km, phone
   (`officialPhone` then first of `phone_numbers`), and website
   (`officialWebsite` then first of `websites`).

### Capability coverage at full scale (at-least-PARTIAL evidence, deduped)

| Need / capability | Candidates nationwide | Within 50 km of demo city |
|---|---|---|
| dialysis / renal | 2,086 | 36 (Jaipur), 46 (Patna) |
| emergency | 3,019 | 52 (Patna) |
| oncology / cancer | 2,215 | 148 (Mumbai) |
| NICU / neonatal | 1,375 | 53 (Hyderabad) |
| maternity / obstetrics | 4,210 | 146 (Chennai) |
| trauma / orthopedic | 3,718 | — |
| cardiology (raw fallback) | 3,647 | 128 (Pune) |

### Demo query results (top hits, k=5)

**`dialysis near Jaipur`** — 2,086 candidates, 36 within 50 km; top 5 all STRONG,
all in Jaipur within 5 km:

| # | Grade | Facility | City | Dist | Evidence (excerpt) |
|---|---|---|---|---|---|
| 1 | STRONG | KKS Urology And General Hospital | Jaipur | 2.8 km | specialty=nephrology; "Offers Nephrology & Dialysis" |
| 2 | STRONG | Indus Jaipur Hospital | Jaipur | 3.3 km | specialty=nephrology; procedure~Dialysis |
| 3 | STRONG | Soni Hospital | Jaipur | 3.4 km | CRRT equipment; "hemodialysis and CRRT in the dialysis center" |
| 4 | STRONG | Vaishali Hospital & Surgical Research Center | Jaipur | 4.7 km | On-site dialysis facility; Nephrology and Dialysis |
| 5 | STRONG | NAV Imperial Hospital & Research Centre | Jaipur | 5.0 km | "Dialysis machines ... for renal failure treatment" |

**`emergency surgery near Patna`** — 3,019 candidates, 52 within 50 km; top 5 all
STRONG, all in Patna within 1.6 km:

| # | Grade | Facility | City | Dist | Evidence (excerpt) |
|---|---|---|---|---|---|
| 1 | STRONG | Medizone Hospitals | Patna | 0.6 km | "24x7 Emergency & Trauma Centre" |
| 2 | STRONG | Shrinivas Hospital | Patna | 0.8 km | "Emergency Room provides first aid and emergency treatment" |
| 3 | STRONG | Satyavrat Hospital | Patna | 1.0 km | specialty=emergencymedicine; "Fully equipped ambulance" |
| 4 | STRONG | MGM Hospital and Research Centre | Patna | 1.2 km | "Provides 24x7 emergency care" |
| 5 | STRONG | Jagdish Memorial Hospital | Patna | 1.6 km | specialty=emergencymedicine; Emergency care |

**`oncology / cancer near Mumbai`** — 2,215 candidates, 148 within 50 km; top hit
Bhatia Hospitals (2.7 km, STRONG, GI oncology + tumour surgery). Lilavati
Hospital (3.9 km, STRONG) shows PET-CT imaging + Hematology-Oncology dept.

**`NICU near Hyderabad`** — 1,375 candidates, 53 within 50 km; top hits Aster
Prime (1.7 km), Cloudnine (1.8 km, "Offers NICU and neonatal care"), Rainbow
Hospital (1.9 km, advanced neonatal ambulances + NICU). *Data caveat: Cloudnine's
`address_stateOrRegion` reads "Chhattisgarh" though it geocodes to Hyderabad — an
address-field inconsistency in the source row, not a ranking error.*

**`maternity / delivery near Chennai`** — 4,210 candidates, 146 within 50 km; top
hits Aakash Fertility Centre (1.0 km, IVF/IUI), SIMS Hospital (1.1 km), all
STRONG with gynecologyAndObstetrics specialty evidence.

**`cardiology near Pune`** (raw fallback) — 3,647 keyword candidates, 128 within
50 km; top hits Oyster & Pearl Prime, Hardikar Hospital, Deccan Hardikar — all
list `cardiology` in their specialties array. Shown as PARTIAL because no trust
grade is computed for cardiology.

### Honesty / limitations

- **This is the full national dataset, not a 100-row sample.** Jaipur (190
  facilities) and Patna (138) both have dense coverage, so the headline queries
  return many nearby STRONG hits. Where a query returns few/no nearby results, the
  function emits an explicit note distinguishing a **dataset coverage gap** from
  "no such care exists."
- **Ungeocodable city** (e.g. `trauma near Shillong`): Shillong is not in the
  geocoder, so the function returns the top STRONG trauma facilities **without
  proximity ranking** and warns the location could not be geocoded. Fix = add the
  city to `CITY_COORDS`; it is a geocoder-coverage limit, not a data gap.
- **Unmappable need** (e.g. `time travel near Jaipur`): returns empty with the
  list of supported needs — no hallucinated matches.
- **Coordinate hygiene:** out-of-India / swapped coords (lat 6-37, lon 68-98
  bbox) are excluded from distance math but facilities are still retained at the
  bottom of their grade band, so a bad geocode never silently drops a real
  hospital.
- **Pediatrics & cardiology** rely on raw keyword evidence (no trust grade), so
  their hits are conservatively labeled PARTIAL and should be treated as
  lower-confidence than the seven trust-graded capabilities.
