## Cross-Dataset Linkage: Feasibility & Conceptual Data Model

This section establishes, with computed evidence, **how the three complete national datasets join** — NFHS-5 district indicators (706 rows, 698 distinct districts, 36 states/UTs), the India Post All-India pincode directory (165,627 post offices, 19,586 distinct pincodes, 749 districts, 36 states), and the enriched health-facility dataset (10,088 facilities nationwide). The verdict: **the join works**, with the pincode directory acting as the geographic backbone that links facility *supply* points to NFHS district *demand/outcome* indicators.

### 1. Geographic key overlap (full national data)

All keys were normalized: lower-cased, `&`→`and`, punctuation stripped, whitespace collapsed; a short state-alias map and a district suffix-strip (`district/dist/rural/urban`) were applied.

**State / UT level — exact match after normalization (36/36).**
Raw spellings differ across sources (NFHS `Maharastra` vs Post `MAHARASHTRA`; NFHS `NCT of Delhi` vs Post `DELHI`; NFHS `Andaman & Nicobar Islands` vs Post `ANDAMAN AND NICOBAR ISLANDS`; NFHS `Lakshadweep` has stray surrounding spaces; Post carries both `ODISHA` and the legacy `ORISSA`). After canonicalization:

| Comparison | Result |
|---|---|
| NFHS canonical states | 36 |
| India Post canonical states | 36 |
| **Intersection** | **36 / 36 (100%)** |
| NFHS states absent from Post | 0 |
| Post states absent from NFHS | 0 |

**District level — strong but imperfect; renames/splits drive the gap.**

| Comparison | Count | % of NFHS |
|---|---|---|
| NFHS distinct district names (normalized) | 692 | — |
| India Post distinct district names (normalized) | 744 | — |
| District **name-only** overlap | 603 | **87.1%** |
| District **(state, name)** overlap | 612 / 704 pairs | **86.9%** |
| NFHS (state,district) pairs with **no** Post match | 92 | 13.1% |

The 92 unmatched pairs are **not** data-quality failures — they are almost entirely (a) **post-2011 renames** (Bangalore→Bengaluru, Mysore→Mysuru, Gurgaon→Gurugram, Allahabad→Prayagraj, Belgaum→Belagavi, Gulbarga→Kalaburagi, Bijapur→Vijayapura, Shimoga→Shivamogga) and (b) **old vernacular NFHS spellings** (Visakhapatnam, Punch/Poonch, Badgam/Budgam, Baramula/Baramulla, Pashchimi/Purbi Singhbhum). A small ~18-entry rename crosswalk recovers most of them (see §3).

### 2. The operational join: facility → pincode → district → NFHS

The pincode is the reliable linking key. Build a `pincode → (district, state)` lookup from India Post (mode district per pincode), then chain to NFHS.

**Join funnel (N = 10,088 facilities):**

| Stage | Facilities | % of all |
|---|---|---|
| Has a valid 6-digit pincode (`address_zipOrPostcode`) | 9,929 | **98.4%** |
| Pincode found in India Post directory | 9,713 | **96.3%** (97.9% of those with a pincode) |
| Resolved pincode → NFHS district (strict (state,district) match) | 8,242 | **81.7%** |
| **+ apply ~18-row rename/split crosswalk** | **8,968** | **88.9%** |

So **~82% of all facilities link end-to-end with zero crosswalk**, and **~89% once a tiny rename table is applied**. Facility coverage is national: top facility states are Maharashtra (1,575), Gujarat (981), Uttar Pradesh (919), Tamil Nadu (780), Karnataka (529), Kerala (483), West Bengal (477).

**Residual mismatch is concentrated and explainable.** Of the 1,471 facilities whose pincode resolves to a district but fails the strict NFHS match, the top drivers are renamed metros and new splits, not noise:

| District (Post spelling) | Facilities lost | Cause |
|---|---|---|
| Bengaluru (Karnataka) | 305 | rename of Bangalore |
| Gurugram (Haryana) | 141 | rename of Gurgaon |
| 24 Paraganas North (WB) | 73 | spelling / "North Twenty Four Parganas" |
| NTR (Andhra Pradesh) | 63 | **new** post-2019 district (no NFHS row) |
| Raigad (Maharashtra) | 56 | Raigad/Raigarh ambiguity |
| Prayagraj (UP) | 56 | rename of Allahabad |
| Visakhapatanam (AP) | 53 | spelling of Visakhapatnam |
| Kamrup Metro (Assam) | 49 | "Kamrup Metropolitan" |

A genuinely unrecoverable sliver remains: brand-new post-2019 districts (e.g. AP's NTR, Anakapalli) that **did not exist** when NFHS-5 was fielded — these have no demand-side counterpart by construction, not by normalization failure.

**Pincode→district ambiguity is minor:** only **1,252 of 19,586 pincodes (6.4%)** span more than one district; a mode-district rule resolves these with negligible error.

**Lat/lon point-in-polygon fallback is well-supported.** 9,970 facilities (98.8%) carry coordinates, and **95.1% of the facilities that fail the pincode chain still have lat/lon** — so a spatial join against official district boundary polygons can rescue most residual cases and validate the pincode mapping. India Post itself provides centroids for 153,620 of 165,627 rows (92.8%), usable to QA the pincode→district assignment.

### 3. Conceptual data model

```
            DEMAND SIDE                  BACKBONE                 SUPPLY SIDE
   +--------------------------+   +------------------+   +--------------------------+
   |  NFHS-5 (706 rows)        |   | India Post 165k  |   | facilities_hack (10,088) |
   |  grain: district          |   | grain: post off. |   | grain: facility point    |
   |  health OUTCOMES &        |   | pincode <->      |   | health SUPPLY /          |
   |  BEHAVIOURS by district:  |<--| (district,state) |-->| INFRASTRUCTURE:          |
   |  institutional birth %,   |   | + lat/lon        |   | facilityTypeId,capability|
   |  C-section %, immunization|   | (centroids)      |   | specialties, capacity,   |
   |  anaemia, BP/sugar (NCD)  |   |                  |   | numberDoctors, equipment |
   +--------------------------+   +------------------+   +--------------------------+
        key: (state_ut,            join key: pincode          key: address_zipOrPostcode
              district_name)       6.4% multi-district         (98.4% valid) + lat/lon
```

- **NFHS-5 = demand / outcomes** (one row per district): institutional-birth %, public-facility-birth %, C-section %, full-immunization %, ANC visits, plus NCD burden (hypertension, high blood sugar, anaemia, obesity) and cancer-screening rates.
- **facilities_hack = supply / infrastructure** (one row per point): facility type (9,962 populated), capability (9,966), specialties (9,972), equipment (9,863); plus partial capacity (2,520) and doctor counts (3,633).
- **India Post = geographic backbone**: the only field that reliably bridges a facility *point* to an NFHS *district*.

### 4. Supply-vs-demand analyses unlocked

With the join in place, aggregate facilities to district counts/capability scores and align to NFHS rates:

- **Facility & capability density per district vs institutional-birth %** — does denser obstetric supply track higher institutional delivery (and lower home births)?
- **C-section supply vs C-section %** — districts with many private surgical-capable facilities vs NFHS `births_delivered_by_csection_5y_pct` and the public/private split, flagging over-medicalization or unmet need.
- **Immunization-capable facility density vs `child_12_23m_fully_vaccinated`** — supply gaps explaining low-coverage districts.
- **NCD burden (hypertension / high blood sugar / cancer-screening) vs specialty supply** — match high-NCD-prevalence districts against facilities reporting relevant capability/specialties to surface under-served high-burden districts.

### 5. Recommended join recipe & caveats

**Recipe**
1. **Normalize** all keys: lower-case, `&`→`and`, strip punctuation, collapse whitespace; apply a state-alias map (Maharastra→Maharashtra, NCT of Delhi→Delhi, Orissa→Odisha, Tamilnadu→Tamil Nadu) — gives **36/36 state match**.
2. **Primary key = pincode.** Parse `facilities.address_zipOrPostcode` to a clean 6-digit integer; build `pincode → (district, state)` from India Post using the **mode district** per pincode (handles the 6.4% multi-district pincodes).
3. **Resolve district → NFHS** on `(state, normalized district)`; strip `district/rural/urban` suffixes. This alone reaches **81.7%**.
4. **Apply a ~18-row rename/split crosswalk** (Bengaluru↔Bangalore, Gurugram↔Gurgaon, Prayagraj↔Allahabad, Kalaburagi↔Gulbarga, Kamrup Metro↔Kamrup Metropolitan, etc.) → **88.9%**.
5. **Geocode fallback:** for the residual, point-in-polygon the facility lat/lon (available for 98.8%; 95.1% of the misses) against district boundaries, and use it to QA the pincode mapping.

An integrated district table (`district_supply_demand.csv`) joining facility supply aggregates to NFHS demand indicators **has already been built** on this recipe.

**Caveats**
- **Temporal mismatch / new districts:** NFHS-5 reflects 2019–21 district boundaries. Post-2019 splits (AP's NTR, Anakapalli, etc.) have facilities but no NFHS row — an inherent gap, not a fix. Conversely, one 2019-era NFHS district may now map to several pincode districts.
- **Pincode→district is a many-to-one approximation:** 6.4% of pincodes straddle districts; the mode rule is good but not exact for boundary post offices (pincodes are point geographies, not polygons).
- **Facility self-report fields are sparse** (`capacity` 25%, `numberDoctors` 36%) — density/typology metrics are robust, but absolute capacity figures are partial.
- **`address_stateOrRegion` is dirty** (253 distinct values incl. cities like Thane/Mumbai/Pune and tokens like `kie`, `Up`) — do **not** join on it directly; always route through the pincode key.
