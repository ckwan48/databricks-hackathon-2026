## Outlier & Anomaly Hunt — NFHS-5, India Post, and Health Facilities

National-scale scan of all three complete datasets (NFHS-5: 706 district rows / 698 distinct districts / 36 states; India Post: 165,627 post offices / 19,586 pincodes / 749 districts; facilities_hack: 10,088 facilities). These are the full national files, not samples. Every figure below is a real value from the data. NFHS percentages were cleaned per the value rules (`*` = suppressed, parentheses = small-sample 25–49 cases, whitespace stripped).

---

### 1. NFHS-5 — statistical & logical outliers

**Method.** For every percentage indicator we flagged district values with |z| > 3 or outside [Q1−1.5·IQR, Q3+1.5·IQR]. This produced **1,849 outlier flags** across the 706 rows.

#### 15 most extreme values (by |z|)

| Indicator | District (State) | Value | z | Why |
|---|---|---|---|---|
| male sterilization % | Chamba (Himachal Pradesh) | 18.4% | +11.0 | National mean 0.5%, median 0.1% — extreme male-sterilization concentration |
| oral-cancer-exam % (W 30–49) | North & Middle Andaman (A&N) | 15.8% | +10.3 | Screening near-zero nationally |
| MCP-card received % | Imphal West (Manipur) | 50.0% | −10.1 | National Q1=95.1%; suspiciously round 50.0 |
| oral-cancer-exam % | Guntur (Andhra Pradesh) | 14.6% | +9.5 | AP/Telangana cluster on cancer screening |
| MCP-card received % | Imphal East (Manipur) | 53.8% | −9.2 | Manipur cluster of very low MCP coverage |
| breast-exam % (W 30–49) | Salem (Tamil Nadu) | 14.6% | +8.9 | Screening near-zero nationally |
| iodized-salt % | Koppal (Karnataka) | 47.9% | −8.6 | National mean 95.1% — lowest in India by far |
| male sterilization % | Kinnaur (Himachal Pradesh) | 14.4% | +8.6 | HP male-steril cluster |
| IUD use % | Longleng (Nagaland) | 32.2% | +8.5 | Nagaland IUD cluster |
| oral-cancer-exam % | West Godavari (Andhra Pradesh) | 13.1% | +8.4 | AP cluster |
| IUD use % | Mon (Nagaland) | 31.8% | +8.4 | Nagaland IUD cluster |
| injectables use % | Badgam (Jammu & Kashmir) | 9.8% | +8.4 | J&K injectables cluster |
| diarrhoea prevalence (U5, 2wk) % | Supaul (Bihar) | 39.3% | +8.0 | Implausibly high 2-week prevalence |
| breast-exam % | Nicobars (A&N) | 13.2% | +8.0 | A&N screening cluster |
| injectables use % | Punch (Jammu & Kashmir) | 9.3% | +7.9 | J&K injectables cluster |

#### Logically suspicious values

- **C-section epidemic in Telangana.** Total C-section rate spans 1.4%–82.4% (national mean 22.8%, median 18.6%; WHO "expected" ceiling ~10–15%). **54 districts exceed 50%; 23 exceed 60%.** The 19 highest-C-section districts in India are **all in Telangana** — Karimnagar **82.4%**, Jangoan 79.1%, Nirmal 77.3%, Rajanna Sircilla 77.2%, Suryapet 77.0%. **25 of 31 Telangana districts** are above 50% (state mean 61.6%). Private-facility C-section rates reach **94.2% (West Tripura)**, with 40 districts above 80% — clinically implausible, indicative of supply-driven surgical delivery.
- **Sex-ratio-at-birth extremes.** Range 658–1,485 females/1,000 males (biological norm ~952; national mean 944.8). Lows: **Satna & Datia (MP) = 658**, West District (Sikkim) & Muzaffarpur (Bihar) = 685, Kinnaur (HP) = 691 — flag for possible sex-selective practices. Highs (likely small-sample noise): **Alappuzha (Kerala) = 1,485**, Almora (Uttarakhand) = 1,444, East Garo Hills (Meghalaya) = 1,427.
- **Total sex ratio extremes.** Low: **Daman = 755**, Dadra & Nagar Haveli = 817, Sonipat (Haryana) = 844 (migrant-labour male skew). High: **Diu = 1,332**, Almora = 1,331, Rudraprayag = 1,242 (male out-migration).
- **OOP delivery expenditure in PUBLIC facilities (₹).** Should be near-free under JSY; range ₹193–₹20,101 (mean ₹3,529, median ₹2,830). Top outliers all in the Northeast: **Kra Daadi (Arunachal) ₹20,101**, Imphal East (Manipur) ₹18,578, Papum Pare (Arunachal) ₹17,185, Bishnupur (Manipur) ₹16,362. Lowest: Dindori (MP) ₹193, Betul (MP) ₹454.
- **Round-number / boundary values.** Manipur's MCP-card value of exactly **50.0% (Imphal West)** stands out (z = −10.1). Exact **0.0%** appears 329× for male sterilization, 264× for "vaccinations in private facility," 220× for breast exams, 179× for oral-cancer exams. Exact **100.0%** appears 189× for "most vaccinations in public facility," 119× for BCG, **45× for institutional birth** (e.g. South Goa, Porbandar, Mysore, Kasaragod, Wayanad) and **26× for household electricity** (Diu, North/South Goa, several Haryana & HP districts). The 100% ceilings are plausible for small wealthy/urban districts but are statistical edge cases warranting a denominator check.

#### Serial outliers (extreme on many indicators)

Northeast hill districts dominate. **Ukhrul (Manipur) — extreme on 19 indicators**, Tuensang (Nagaland) and East Khasi Hills (Meghalaya) — 17 each, North Garo Hills (Meghalaya) — 16, West Jaintia Hills (Meghalaya) & **Thiruvananthapuram (Kerala) — 15 each**, Kiphire (Nagaland) & West Khasi Hills (Meghalaya) — 14 each. Meghalaya and Nagaland districts recur because of small populations and distinct fertility/health profiles.

#### Most-suppressed districts

Suppression is severe on some indicators: **non-breastfeeding child adequate-diet (91.1% suppressed), child 6–8m solid food (90.9%), the three diarrhoea-management indicators (69.7% each), children born at home taken to facility (59.8%).** Districts with the most suppressed cells in a single row: **Jabalpur (MP) — 26 suppressed cells**, Raisen (MP) 22, Bhopal (MP) 22, North & Middle Andaman (A&N) 21, Tiruppur (TN)/Sirsa (Haryana)/Mumbai Suburban/South Goa — 20 each.

---

### 2. India Post — pincode & coordinate anomalies

165,627 offices (140,270 BO / 24,546 PO / 811 HO); 19,586 distinct pincodes; 749 districts; 36 states. All pincodes are exactly 6 digits (no length anomalies). 157,901 delivery / 7,726 non-delivery.

- **Missing coordinates: 12,013 rows (7.25%) have NaN latitude; 12,008 NaN longitude.**
- **Garbage / extreme-magnitude coordinates: 224 rows** with |lat|>90 or |lon|>180. Worst is **Udari BO (Surguja, Chhattisgarh): lat 23,724.29 / lon 832,015.52** — unscaled/concatenated junk. Latitude max reaches **233,643,145**, longitude max **9,334,975,723**. A cluster of J&K offices (Anantnag/Pulwama/Kulgam) show lat values like 129.6, 256.2, 325.0 (decimal point dropped, e.g. 33.25 → 325.0).
- **2,611 offices fall outside the India bounding box** (lat 6–37.6, lon 68–97.5) once both coords are present.
- **Likely lat/lon SWAP: 794 rows** have lat in 60–98 and lon in 5–38. The pattern is unmistakable in coastal Andhra Pradesh — e.g. Vizianagaram and Parvathipuram Manyam BOs stored as lat ≈ 83, lon ≈ 18 (true values are lon ≈ 83 E, lat ≈ 18 N). Kasimpalli B.O (Telangana) = 79/17.
- **lat == lon (identical nonzero) in 717 rows** — e.g. Yellareddypalli B.O (Nizamabad) 18.169/18.169, Adawal B.O (Raipur) 19.36/19.36; placeholder/copy error.
- **(0,0) coordinates: 13 offices.** No negative coordinates (none expected for India).
- **Duplicate office names (expected but high):** "Rampur BO" appears 57×, "Rampur B.O" 42× (note the spelling/punctuation split storing the same name two ways), Khanpur BO 42×, Narayanpur BO 39×, Gopalpur BO 39×. 145,086 distinct names of 165,627 rows. **48 rows share an identical (officename, pincode) pair; 2 rows are full duplicates.**
- **Pincodes with unusually many offices:** **791122 (Arunachal) = 153 offices**, 791118 = 149, 345001 (Rajasthan) = 119, 494450 (Chhattisgarh) = 102, 790102 = 98. Sparse Northeast/tribal pincodes legitimately bundle many BOs, but 153 offices on one pincode is worth verifying.

---

### 3. Health facilities — coordinate, value & integrity anomalies

10,088 facilities; 9,970 sourced `kie`; 9,530 distinct names. 118 rows missing lat/lon.

- **Geographic impossibilities (6 facilities all claim "India" but plot elsewhere):**
  - **Sanjivani Multi Speciality Hospital — Chengannur, Kerala → lat 59.95 N, lon −38.26 W** = mid–North Atlantic Ocean (the "North-Atlantic hospital"; only negative-longitude row).
  - **Krishna Hospital Multispeciality — Lucknow, UP → lat −81.71** = near the South Pole / Southern Ocean.
  - **The Family Tree Hospital — Tirupati, AP → lat 32.96, lon 7.48** = off West Africa (Gulf of Guinea).
  - Cura Imaging & Gastro Clinic — Nagpur → 2.95 / 41.39 (Somalia/Indian Ocean); Hzb Arogyam — Hazaribagh → 46.07 / 106.17 (Mongolia); Cardia Health Care — Noida → 7.71 / 109.69 (South China Sea).
- **State/coordinate mismatch (within plausible-globe range):** Attukal Devi Hospital — claims Thiruvananthapuram, Kerala, but coords (11.87 N, 78.05 E) fall in inland Tamil Nadu (Salem region).
- **CSV column-shift corruption: 29 rows have address_country ≠ "India"** and 29 have countryCode ≠ "IN"; 24 rows have a garbage countryCode (coordinate-JSON or hex IDs). Specialties-JSON arrays and "kie" tokens leak into the `name`, `yearEstablished`, `organization_type` and `source` columns. ~5,300 `yearEstablished` cells are non-numeric (mostly NaN, but includes JSON spillover).
- **Impossible / extreme values:**
  - **capacity (beds): max 200,000 at Harsh Hospital, Motihari** (no hospital on earth; median capacity = 100, only 2,517 rows populated). Next-largest 4,000 (KGMU Lucknow) is plausible.
  - **numberDoctors: max 15,000 at Nithya Hospital, Dharmapuri** (median = 2, 3,630 rows populated); 6,000 (KIMS Hyderabad), 5,000 (Scientific Pathology, Agra) also implausible for a single facility.
  - **yearEstablished out of range:** values of **0** (3 rows), and 1–100 (8 rows, e.g. Sri Krishna Hospital Proddutur = "7", Medini Cosmetic = "15"); also corrupt entries like 1756 and 1723 from column shift. 4,775 rows hold a plausible 1800–2026 year.
  - Social-media post dates span 2009-06-29 to 2026-01-22 — **no future dates** beyond today (2026-06-15).
- **Engagement-metric extremes (likely scrape placeholders):** two facilities at **exactly 15,000,000 followers** — J J Eye Hospital (Mumbai) and Shiromany Dental Care (Agra) — vs. median 244.5. Likes max 384,000 (Handa Health Care Centre); engagements max 121,855 (North Bengal Medical College); post_count max 59,000 (Rajagiri Hospital). Round/identical maxima suggest capped or default-injected values.
- **Duplicate coordinates: 219 rows** share an exact (lat, lon) pair; duplicate names include Apollo Clinic (10×), City Hospital (8×), Life Care Hospital (6×) — likely chains, but possible double-scrapes.

---

### 4. Prioritized Anomaly Register

| Dataset | Field | Row / District identifier | Value | Why anomalous | Likely cause |
|---|---|---|---|---|---|
| Facilities | latitude/longitude | Sanjivani Multi Speciality Hospital (Chengannur, Kerala) | 59.95, −38.26 | Plots in North Atlantic Ocean | Geocode/scrape failure |
| Facilities | latitude | Krishna Hospital (Lucknow, UP) | −81.71 | Near South Pole | Sign/geocode error |
| Facilities | longitude | The Family Tree Hospital (Tirupati, AP) | 7.48 | Off West Africa | Truncated/wrong geocode |
| Facilities | capacity | Harsh Hospital, Motihari | 200,000 beds | Physically impossible | Data-entry/scrape error |
| Facilities | numberDoctors | Nithya Hospital, Dharmapuri | 15,000 | Impossible for one facility | Scrape/parse error |
| Facilities | engagement_n_followers | J J Eye Hospital; Shiromany Dental Care | 15,000,000 (×2) | Identical implausible max | Capped/placeholder value |
| Facilities | column structure | ~29 rows (countryCode ≠ IN) | JSON/coords in wrong cols | Column-shift corruption | Malformed CSV rows |
| Facilities | state vs coords | Attukal Devi Hospital (claims Kerala) | 11.87, 78.05 (TN) | State/coordinate mismatch | Wrong geocode |
| Post | latitude/longitude | Udari BO, Surguja (Chhattisgarh) | 23,724.29 / 832,015.52 | Off-planet magnitude | Concatenated/unscaled junk |
| Post | latitude/longitude | 794 rows incl. Vizianagaram/Parvathipuram BOs | lat≈83, lon≈18 | Lat/lon swapped | Column order swapped at source |
| Post | latitude/longitude | 717 rows incl. Yellareddypalli B.O | lat == lon | Identical coords impossible | Copy/placeholder error |
| Post | latitude | 12,013 rows | NaN | 7.25% missing geocodes | Incomplete geocoding |
| Post | pincode | 791122 (Arunachal Pradesh) | 153 offices | Unusually many on one pincode | Sparse-region bundling (verify) |
| NFHS | births_delivered_by_csection_5y_pct | Karimnagar (Telangana) | 82.4% | >> WHO norm; 25/31 TG districts >50% | Real but extreme medical pattern |
| NFHS | births_in_a_private_fac_csection | West Tripura | 94.2% | Near-total surgical delivery | Supply-driven C-sections |
| NFHS | average_OOP_public_delivery | Kra Daadi (Arunachal Pradesh) | ₹20,101 | Public delivery should be ~free | NE high cost / data issue |
| NFHS | sex_ratio_at_birth | Satna & Datia (Madhya Pradesh) | 658 | Far below biological norm | Possible sex selection |
| NFHS | households_using_iodized_salt_pct | Koppal (Karnataka) | 47.9% | National mean 95.1% (z=−8.6) | True low coverage / verify |
| NFHS | MCP-card received % | Imphal West (Manipur) | 50.0% | z=−10.1; round value | Low coverage / rounding |
| NFHS | fp_cm_w15_49_m_steril_pct | Chamba (Himachal Pradesh) | 18.4% | z=+11.0; mean 0.5% | True local program / verify |
| NFHS | (suppression) | Jabalpur (Madhya Pradesh) | 26 suppressed cells | Highest missingness in a row | Small unweighted subgroups |
