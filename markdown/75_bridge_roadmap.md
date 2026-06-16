## Supply-vs-Demand Bridge and Product Roadmap

This section connects the **supply** side of the data (the full 10,088-facility `facilities_hack.csv` — where care physically exists and what it can do) to the **demand/outcomes** side (NFHS-5 district health indicators — what populations actually need and how they fare), stitched together by the geographic backbone `pincode -> district`. The join is no longer hypothetical: the integrated table `district_supply_demand.csv` (**706 NFHS districts x 114 columns**) is built and live, and every relationship below is computed on it at national scale.

### 1. The conceptual bridge: SUPPLY -> geography -> DEMAND/OUTCOMES

Three tables, three layers of one model:

- **SUPPLY (`facilities_hack.csv`)** — *where care exists and what it can do.* 10,088 facilities nationwide with sub-district resolution (a named, geocoded point per facility), capability evidence (`specialties` over a 164-code taxonomy, plus `procedure`/`equipment`/`capability`), and structural fields (`facilityTypeId`, `operatorTypeId`, `numberDoctors`, `capacity`).
- **GEOGRAPHY (`india_post.csv`)** — *the backbone* translating each facility's `address_zipOrPostcode` (6-digit PIN) into a `district`, the unit NFHS reports at, via `pincode -> district -> statename`.
- **DEMAND / OUTCOMES (`nfhs5.csv`)** — *who needs care and how well it reaches them.* 700+ districts x 109 indicators: institutional-birth %, public-vs-private C-section %, ANC, immunization, anaemia, blood sugar / blood pressure (NCD burden), teen pregnancy, health-insurance coverage, out-of-pocket delivery cost.

The join chain **facility.PIN -> post.district -> nfhs.district_name** fires nationally and produces district-level supply counts (`n_facilities`, `n_hospital`, `n_clinic`) sitting in the same row as NFHS demand indicators.

- **Coverage achieved.** Of 10,088 raw facility rows, **6,533 matched to a valid Indian district** and aggregate into the supply counts; **425 of 706 districts have >=1 matched facility**, **281 districts have zero matched facilities**. District facility counts range **0–330** (mean 9.3, median 1) — a highly skewed, metro-concentrated supply distribution. Of matched facilities, 3,765 are hospitals and 2,376 clinics.

### 2. Real supply <-> outcome correlations (computed on all 706 districts)

Pearson r across districts (full 27-pair matrix in `supply_demand_correlations.csv`):

| Supply metric | Demand / outcome indicator | n | Pearson r | p | Spearman rho |
|---|---|---|---|---|---|
| n_hospital | Women high blood sugar % | 706 | **+0.271** | <0.0001 | +0.283 |
| n_facilities | Women high blood sugar % | 706 | +0.267 | <0.0001 | +0.268 |
| n_clinic | Women high blood sugar % | 706 | +0.244 | <0.0001 | +0.249 |
| n_hospital | Institutional birth in **public** facility % | 706 | **-0.231** | <0.0001 | -0.266 |
| n_facilities | Institutional birth in public facility % | 706 | -0.214 | <0.0001 | -0.259 |
| n_hospital | C-section % | 706 | **+0.199** | <0.0001 | +0.262 |
| n_hospital | Institutional birth % (overall) | 706 | +0.164 | <0.0001 | +0.250 |
| n_hospital | Women high BP % | 706 | +0.122 | 0.0012 | +0.148 |
| n_facilities | >=4 ANC visits % | 706 | +0.123 | 0.0011 | +0.108 |
| n_facilities | Teen pregnancy % | 706 | **-0.116** | 0.0020 | -0.149 |

**Strongest, most interpretable relationships:**
- **Hospital density tracks NCD burden** (r = +0.27 with women's high blood sugar; +0.12 with high BP). More health infrastructure sits in the urbanised, higher-NCD-prevalence districts — supply follows the chronic-disease transition. This validates a **dialysis/oncology-desert** lens: NCD demand and treatment-capability supply can be co-mapped.
- **More private supply -> less reliance on public delivery** (r = -0.23 between hospital count and institutional-birth-*in-public*-facility %). Where private facilities cluster, mothers shift out of public maternity wards — a clean supply-substitution signal.
- **Hospital density correlates with C-section rate** (r = +0.20) and overall institutional birth (r = +0.16): supply enables facility-based delivery (and, for C-sections, may over-induce it).
- **Facility density is *negatively* associated with teen pregnancy** (r = -0.12) and *positively* with >=4 ANC visits (r = +0.12): infrastructure tracks better reproductive-health demand-side outcomes.
- **Null results matter too.** Full immunization %, women's anaemia %, and HH health-insurance % show **no significant correlation** with facility counts (|r| < 0.03, p > 0.5). Anaemia and routine immunization are driven by community/outreach programs, not facility density — building hospitals will not move these needles. This is a key guardrail against a naive "more facilities = better health" narrative.

### 3. Under-served vs over-supplied districts (153 flagged)

Using percentile ranks — **under-served** = bottom-25% facility supply AND top-25% dependence on public maternity facilities (people forced into the public system with little private choice); **over-supplied** = top-15% supply AND bottom-35% public dependence (private-rich). Full list in `underserved_oversupplied_districts.csv`.

- **90 under-served districts.** Highest-need examples (zero matched facilities, >90% public-facility dependence for births): **Nicobars**, **Leh (Ladakh)**, **Kulgam / Shupiyan / Badgam (J&K)**, **Kandhamal & Balangir (Odisha)**, **Guna (MP)**, **Pratapgarh (Rajasthan)**, **West Kameng (Arunachal)**, **North District (Sikkim)**, **Serchhip (Mizoram)**. These are remote/hill/island/tribal districts where institutional birth is high *only because the public system carries it* — a fragile, single-point-of-failure supply posture.
- **63 over-supplied districts.** Top examples: **Ahmadabad (330 facilities, 189 hospitals)**, **Hyderabad (212)**, **Surat (161)**, **Lucknow (147)**, **Patna (144)**, **Vadodara (122)**, **Ernakulam (106)**, **Ludhiana (103)**. High private density, low public dependence, elevated C-section rates (Hyderabad 59.7%, Ranga Reddy 57.8%, Ernakulam 51.1%) — candidate markets for consolidation/competition analytics and C-section-appropriateness review rather than capacity-building.

### 4. Privacy / compliance

The raw facilities file carries **genuine PII at near-100% fill**: `phone_numbers`, `officialPhone`, and `email` each hold real (non-`null`) values in **10,087 of 10,088 rows (100.0%)**, plus `websites`/`officialWebsite`/`facebookLink`, alongside scraped social/engagement fields (`engagement_metrics_*`, `post_metrics_*`). Implications under India's **DPDP Act 2023** (which treats identifiable contact data as personal data): (a) segregate PII columns into a restricted, encrypted store, exposing only hashed/tokenized keys to analysts; (b) retain provenance (`source_types`, `source_ids`, `source_urls`) for every PII value to honor takedown/correction requests; (c) the analytics/desert layer needs **no PII at all** — derive district aggregates from a PII-stripped view (`district_supply_demand.csv` already contains none); (d) any external "facility lookup" product must gate PII behind authenticated, rate-limited, audited access, with documented lawful basis and retention.

### 5. Additional high-value ideas to pitch (product roadmap)

1. **Capability-desert mapping** — overlay capability/equipment evidence (dialysis, oncology, NICU, CT/MRI) on NFHS NCD and maternity demand to rank districts by *unmet* need, not just facility count. The headline product, now backed by the +0.27 hospital<->blood-sugar signal.
2. **Equity / access scoring** — composite district score combining supply density, public-dependence, remoteness, and demand intensity; the 90 under-served districts above are the seed list.
3. **Facility "trust score" API** — serve the existing `facility_capability_trust.csv` confidence/grade signals (accreditation, doctor count, capacity, year established, digital footprint) as a real-time scored endpoint.
4. **Dedupe-at-scale on `cluster_id`** — entity-resolution + blocking so one real facility = one record across overture/mongo/dynamic/constant sources before supply counts are trusted at full scale.
5. **Active-learning review loop** — route low-confidence capability/dedupe predictions (`review_queue.csv`) to human reviewers, feeding corrections back into the model.
6. **Geocoding-repair pipeline** — auto-detect lat/lon swaps and out-of-India points (e.g. the Kerala-addressed hospital at lat ~60 / lon ~-38 in the North Atlantic), validate against the India bbox (lat 6-37, lon 68-98), and re-geocode from PIN; this directly recovers part of the 3,555 unmatched facilities.
7. **NABH / accreditation extraction** from free-text `description`/`capability` to enrich trust scoring with a structured quality flag.
8. **Specialty-taxonomy normalization service** — canonicalise the 164-code clinical taxonomy in `specialties` across sources (hosted free-text -> code mapper) for clean cross-source capability rollups.

### Caveats

- **281 of 706 districts (40%) have zero matched facilities** — a mix of true supply gaps and PIN-match misses; the 3,555 unmatched raw rows (bad/missing PINs, out-of-India coordinates) bias coverage toward metros and understate rural supply. Treat zero-facility districts as "unknown," not confirmed empty.
- All correlations are **cross-sectional and ecological** (district-level): they show co-location, not causation, and are subject to confounding by urbanisation/income.
- NFHS values in parentheses and `*` denote small unweighted denominators / suppressed estimates; these were stripped to numeric before correlation but remain low-confidence at the district level.
- `cluster_id` should be used to dedupe before any per-facility supply count is taken to production scale.

*Artifacts: `/Users/koushik/Desktop/health_analysis_outputs/supply_demand_correlations.csv` (all 27 supply x demand Pearson/Spearman pairs with n and p), `/Users/koushik/Desktop/health_analysis_outputs/underserved_oversupplied_districts.csv` (153 flagged districts), built on `/Users/koushik/Desktop/health_analysis_outputs/district_supply_demand.csv` (706-district integrated table).*
