## Health Facilities — Identity, Location & Classification Profile

Source: `facilities_hack.csv` — an enriched/scraped health-facility dataset (web + Overture + 'kie' sources). **10,088 facility rows × 51 columns** (this section profiles the 28 identity/location/classification columns). All fill-rates are computed after treating the literal string `null`, empty strings, and blanks as missing. These are the complete national figures, not a sample.

### Headline findings

- The dataset is overwhelmingly **Indian health facilities**: `address_countryCode = IN` on **10,000 rows (99.1%)** and `address_country = India` on the same 10,000. `organization_type = facility` on 10,000 rows. **9,943 rows** carry an in-vocabulary `facilityTypeId`, and **99.1% of rows are structurally intact** (IN + UUID + organization_type=facility).
- **Facility type mix (n=9,943 clean):** `hospital` **5,637 (56.7%)**, `clinic` **3,782 (38.0%)**, `dentist` **490 (4.9%)**, `doctor` 21, `farmacy` 10, `pharmacy` 2, `nursing_home` 1. (`farmacy` is a misspelling sibling of `pharmacy` — 12 pharmacies total.)
- **Operator type (n=9,313 clean):** `private` **8,842 (94.9%)**, `public` **469 (5.0%)**, `government` 2. The dataset is dominated by private-sector facilities. `operatorTypeId` is missing on 761 rows (7.5%).
- **Contact-channel coverage is high:** phone_numbers 96.6%, officialPhone 94.4%, facebookLink 98.1%, websites 99.4%, email 85.0%, officialWebsite 83.5%.
- **A small but real data-quality problem: ~88 rows (0.9%) are corrupted by column-shift**, where JSON arrays of websites, GPS `{"coordinates":[...]}` objects, bare lat/long floats, UUIDs, the token `kie`, and free-text description fragments have bled into the wrong columns (visible as junk in `organization_type`, `facilityTypeId`, `operatorTypeId`, `address_country`, `address_countryCode`, `countries`, `acceptsVolunteers`). 29 rows have a non-`IN`, non-null `countryCode`; 88 `unique_id`s are not UUID-format.

### Data dictionary

| Column | Meaning | Type | Fill-rate | #unique | Notes |
|---|---|---|---|---|---|
| `unique_id` | Row primary key | UUID string | 100.0% | 10,077 | 10,000 valid UUIDs; 88 non-UUID (column-shift junk); **11 duplicate UUIDs** (appear twice) |
| `source_types` | Provenance source labels | JSON array (string) | 99.2% | 6,312 | Median 23 items/row (max 50). Only **5 distinct labels**: overture (162k mentions), dynamic (83k), constant (21k), mongo_facility (6k), mongo_ngo (1.1k). 38 rows unparseable |
| `source_ids` | Source record IDs | JSON array (string) | 99.1% | 9,261 | Median 17 items/row; 29,358 distinct IDs total; 27 unparseable |
| `source_content_id` | Content/document ID | UUID string | 99.3% | 9,086 | **Equals `content_table_id` on 10,000/10,008 rows** — effectively the same key. 933 dup values |
| `name` | Facility name | Free text | 99.4% | 9,530 | e.g. "Aravind Eye Hospital", "Fortis Hospital, Gurugram". A few rows hold free-text fragments (column-shift) |
| `organization_type` | Top-level entity type | Categorical | 99.4% | 28 | `facility` on 10,000 rows; remaining 27 "values" are description/specialty/free-text contamination |
| `content_table_id` | Content table key | UUID string | 99.4% | 9,092 | Mirror of `source_content_id` (see above) |
| `phone_numbers` | All scraped phone numbers | JSON array (string) | 96.6% | 9,729 | Median 7 numbers/row (max 50); 37,457 distinct numbers; 340 missing, 5 unparseable |
| `officialPhone` | Primary phone | Phone string | 94.4% | 9,176 | 9,506/9,524 are clean digit/`+`/`-` strings (mostly `+91…`) |
| `email` | Contact email | Email string | 85.0% | 8,065 | 8,115 regex-valid; ~455 invalid incl. `[email protected]` placeholders and missing-`@` strings |
| `websites` | All scraped site URLs | JSON array (string) | 99.4% | 10,008 | Median 12 URLs/row (max 50); 121,039 distinct URLs total |
| `officialWebsite` | Primary website (domain) | Domain string | 83.5% | 8,015 | Stored as **bare domains** (e.g. `fortishealthcare.com`), NOT full URLs — only 518 start with `http`; 8,395 contain a dot |
| `yearEstablished` | Year facility founded | Year (numeric) | 47.6% | 157 | Range **1836–2025**, median **2005**, mean 2000; lowest fill-rate among ID/location fields |
| `acceptsVolunteers` | NGO volunteer flag | Boolean | 0.4% | 16 | Only **28 real true/false values** (21 true, 7 false); remaining "values" are dates/junk. Essentially unusable |
| `facebookLink` | Facebook page URL | URL string | 98.1% | 9,880 | 9,878/9,896 contain "facebook" |
| `address_line1` | Street/area line 1 | Free text | 99.3% | 9,671 | e.g. "Santosh Nagar Colony", "Sector 44" |
| `address_line2` | Street/area line 2 | Free text | 97.2% | 8,900 | |
| `address_line3` | Street/area line 3 | Free text | 69.8% | 6,058 | Most sparsely filled address line |
| `address_city` | City | Categorical text | 99.4% | 1,642 | Mumbai (365), Hyderabad (358), Ahmedabad (326), Chennai (326). Has Bangalore/Bengaluru and Delhi/New Delhi duplicates |
| `address_stateOrRegion` | State/UT | Categorical text | 99.4% | 253 | **9,618 rows (96%) match a recognized state/UT**; ~407 hold cities (Thane, Mumbai, Pune) or typos (Tamilnadu 22, Orissa 7, "Up"/"U.p.") |
| `address_zipOrPostcode` | PIN code | 6-digit string | 99.3% | 3,216 | 9,772 valid 6-digit PINs; 250 non-conforming (often spaced like `560 034`) |
| `address_country` | Country name | Categorical | 99.4% | 28 | `India` on 10,000 rows; 29 contamination values (coords/floats/text) |
| `address_countryCode` | ISO country code | Categorical | 99.4% | 29 | `IN` on 10,000 rows; 29 contamination values (`kie`, coords, UUIDs, floats) |
| `countries` | (intended) country list | — | 0.3% | 28 | **Effectively dead column** — all 28 non-null values are column-shift junk (URLs, coords, UUIDs), not country lists |
| `facilityTypeId` | Facility category | Categorical | 98.8% | 26 | See type mix above; 9,943 in-vocab, 19 contaminated |
| `operatorTypeId` | Ownership type | Categorical | 92.5% | 17 | private 8,842 / public 469 / government 2; 14 contaminated |
| `affiliationTypeIds` | Affiliation tags | JSON array (string) | 12.4% | 307 | Where present: `["government"]` 258, `["academic"]` 121, `["philanthropy-legacy"]` 79, `["community"]` 42, `["faith-tradition"]` 36. High #unique = repeated tokens (e.g. `["government","government",…]`) |
| `description` | Free-text blurb | Free text | 99.2% | 9,577 | Length 5–6,557 chars, median 115, mean 179 |

### Classification distributions (full counts)

**`facilityTypeId`** (clean vocabulary, n=9,943; 126 missing):
hospital 5,637 · clinic 3,782 · dentist 490 · doctor 21 · farmacy 10 · pharmacy 2 · nursing_home 1.

**`operatorTypeId`** (clean vocabulary, n=9,313; 761 missing):
private 8,842 · public 469 · government 2.

**`organization_type`**: facility 10,000; all other 27 distinct strings are contamination → operationally a single-value column.

**`affiliationTypeIds`** (only 1,249 rows / 12.4% populated): governance/affiliation tags drawn from {government, academic, philanthropy-legacy, community, faith-tradition, private}; arrays often repeat the same token N times reflecting per-source agreement. 10 rows hold an empty array `[]`.

**`yearEstablished`** (n=4,775 valid years): heavily modern-skewed — 2010s 1,476 · 2000s 1,176 · 1990s 761 · 2020s 414 · 1980s 418; a pre-1950 long tail down to a single facility founded in the 1830s. p25=1993, median=2005, p75=2014.

### State & city coverage

- **State/UT coverage:** 253 distinct `address_stateOrRegion` values, of which 9,618 rows (96.0%) map to a recognized Indian state/UT. Top states: **Maharashtra 1,575 · Gujarat 981 · Uttar Pradesh 919 · Tamil Nadu 780 · Karnataka 529 · Kerala 483 · West Bengal 477 · Punjab 469 · Haryana 462 · Telangana 421 · Rajasthan 407 · Delhi 337 · Andhra Pradesh 329 · Madhya Pradesh 302 · Bihar 258.** North-eastern states are thinly represented (Meghalaya 14, Manipur 13). Coverage is national but **west/south-skewed** (Maharashtra + Gujarat alone = ~25% of rows).
- **City coverage:** 1,642 distinct cities. Top metros: **Mumbai 365 · Hyderabad 358 · Ahmedabad 326 · Chennai 326 · Pune 274 · Kolkata 243 · Bangalore 204 · Jaipur 190 · Surat 164 · Lucknow 155.** Note duplicate-spelling fragmentation: Bangalore (204) + Bengaluru (110) are the same city; Delhi (133) + New Delhi (146) likewise — these should be merged before any city-level analysis.

### Caveats

- **~0.9% of rows (≈88) suffer column-shift corruption**: JSON website arrays, `{"coordinates":[...]}` objects, bare lat/long floats, UUIDs, the literal token `kie`, and description/specialty text appear in the wrong columns. This inflates `#unique` for the low-cardinality categoricals and is the only source of "extra" values beyond the clean vocabularies. Filter on `address_countryCode == 'IN'` AND a UUID `unique_id` to recover the clean 10,000-row core.
- `unique_id` has **11 duplicate UUIDs** — not a strict primary key.
- `source_content_id` and `content_table_id` are effectively the **same identifier** (equal on 10,000/10,008 rows) — treat as one key, not two.
- `officialWebsite` stores **bare domains, not URLs**; `email` includes `[email protected]` anti-scrape placeholders that count as non-valid.
- `acceptsVolunteers` (0.4% fill) and `countries` (0.3%, all junk) are **unusable** as-is.
- `yearEstablished` is only **47.6% populated** — establishment-year analysis covers under half the facilities and skews toward recently scraped/modern facilities.
