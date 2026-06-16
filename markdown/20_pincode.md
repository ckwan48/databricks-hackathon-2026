## India Post Pincode Directory — Column-by-Column Profile

**Source:** India Post All-India Pincode Directory (data.gov.in). **Scope:** complete national directory — every postal delivery point in India.

**Shape:** 165,627 rows × 11 columns. Each row is one **post office** (HO/SO/BO), not one pincode. The file covers 19,586 distinct pincodes, 749 distinct districts and 36 states/UTs, organized under 24 postal Circles, 52 Regions and 482 Divisions.

### The India Post hierarchy (how to read these columns)

India Post is organized as a strict administrative tree, and four columns encode it:

- **Circle** (`circlename`, 24 values) — top tier, roughly one per major state (e.g. *Uttar Pradesh Circle*), plus *APS Circle* (Army Postal Service). A Circle ≠ a state exactly: e.g. *North Eastern Circle* covers several NE states.
- **Region** (`regionname`, 52 values) — sub-division of a Circle, headed by a Postmaster General. Smaller Circles report directly without a named Region — coded as the placeholder **`DivReportingCircle`** (30,777 rows = 18.6% of the file; the single largest "region" value) or are simply missing (315 rows).
- **Division** (`divisionname`, 482 values) — the operational unit a Circle/Region is split into (e.g. *Adilabad Division*).
- **Office** (`officename` + `officetype`) — the leaf node. Three types:
  - **HO = Head Office** (811 rows) — the apex office of a Division/town; sorting and accounting hub.
  - **PO = "Post Office"** (24,546 rows) — in practice almost entirely **Sub Offices (S.O)**: 22,261 of 24,546 PO names end in "S.O". These are departmental offices under an HO.
  - **BO = Branch Office** (140,270 rows = 84.7%) — the smallest rural/last-mile outlets, run by a part-time *Gramin Dak Sevak*. **BOs do not own their own pincode** — they are mapped to the pincode of the SO/HO they hang off, which is why pincodes are massively shared (see below).

**Delivery vs Non-Delivery** (`delivery`): a **Delivery** office actually delivers mail to addresses in its beat (157,901 rows = 95.3%); a **Non-Delivery** office (7,726 = 4.7%) only handles counter/transit functions and routes delivery to another office. Non-delivery is concentrated in PO/Sub Offices (5,821 of 7,726).

### Data Dictionary

| Column | Meaning | Example | # Unique | # Missing | Notes |
|---|---|---|---|---|---|
| `circlename` | Postal Circle (top admin tier) | `Telangana Circle` | 24 | 0 | UP largest (17,997); *APS Circle* only 2 rows |
| `regionname` | Region within a Circle | `Hyderabad Region` | 52 | 315 | `DivReportingCircle` placeholder = 30,777 rows; 2 odd values (`EASTERN/WESTERN COMMAND`) |
| `divisionname` | Operational Division | `Adilabad Division` | 482 | 0 | Fully populated |
| `officename` | Post office name | `Kothimir B.O` | 145,086 | 0 | Names not unique — 10,911 names reused (e.g. *Rampur BO* ×57); suffix style inconsistent (`B.O` vs `BO`) |
| `pincode` | 6-digit postal index number | `504273` | 19,586 | 0 | int; all valid 6-digit (110001–900099); heavily shared across offices |
| `officetype` | HO / PO / BO | `BO` | 3 | 0 | BO 140,270 (84.7%), PO 24,546, HO 811 |
| `delivery` | Delivery / Non Delivery | `Delivery` | 2 | 0 | 95.3% Delivery |
| `district` | District (admin) | `KUMURAM BHEEM ASIFABAD` | 749 | 715 | UPPERCASE; 715 rows blank (with statename) |
| `statename` | State / UT | `TELANGANA` | 36 | 715 | UPPERCASE; same 715 rows missing as district |
| `latitude` | Latitude (°N) | `19.3638689` | 99,918 | 12,007 | Stored as **text**; 6 unparseable; range/swap errors present |
| `longitude` | Longitude (°E) | `79.5376658` | 94,867 | 12,002 | Stored as **text**; 6 unparseable; range/swap errors present |

### Distributions (full categorical value counts)

**Office type** — BO 140,270 · PO 24,546 · HO 811.
**Delivery** — Delivery 157,901 · Non Delivery 7,726.

**Office type × Delivery:**

| | Delivery | Non Delivery | Total |
|---|---|---|---|
| BO | 138,373 | 1,897 | 140,270 |
| PO | 18,725 | 5,821 | 24,546 |
| HO | 803 | 8 | 811 |
| **Total** | 157,901 | 7,726 | 165,627 |

**Circles (all 24, by office count):** Uttar Pradesh 17,997 · Maharashtra 14,073 · Tamilnadu 11,839 · Rajasthan 11,053 · Andhra Pradesh 10,686 · Madhya Pradesh 10,292 · Karnataka 9,670 · Bihar 9,369 · West Bengal 9,109 · Odisha 8,920 · Gujarat 8,905 · Telangana 6,304 · Kerala 5,080 · Chattisgarh 4,770 · Jharkhand 4,599 · North Eastern 4,477 · Assam 4,070 · Punjab 3,852 · Himachal Pradesh 2,811 · Uttarakhand 2,741 · Haryana 2,717 · Jammu Kashmir 1,740 · Delhi 551 · APS 2.

**States/UTs (all 36, by office count):** UTTAR PRADESH 17,968 · MAHARASHTRA 13,762 · TAMIL NADU 11,733 · RAJASTHAN 11,032 · ANDHRA PRADESH 10,681 · MADHYA PRADESH 10,272 · KARNATAKA 9,658 · BIHAR 9,309 · ODISHA 8,915 · GUJARAT 8,841 · WEST BENGAL 8,787 · TELANGANA 6,253 · KERALA 5,057 · JHARKHAND 4,584 · CHHATTISGARH 4,411 · ASSAM 4,063 · PUNJAB 3,796 · HIMACHAL PRADESH 2,807 · UTTARAKHAND 2,742 · HARYANA 2,706 · JAMMU AND KASHMIR 1,617 · ARUNACHAL PRADESH 1,171 · MEGHALAYA 929 · MANIPUR 784 · TRIPURA 723 · DELHI 550 · MIZORAM 456 · NAGALAND 403 · GOA 261 · SIKKIM 212 · LADAKH 119 · ANDAMAN AND NICOBAR 100 · PUDUCHERRY 95 · CHANDIGARH 53 · DADRA & NAGAR HAVELI AND DAMAN & DIU 52 · LAKSHADWEEP 10. (715 rows have no state.)

**Regions (52 total) — top values:** `DivReportingCircle` 30,777 · Hyderabad 5,182 · Jabalpur 4,893 · Jodhpur 4,703 · South Karnataka 4,616 · North Karnataka 4,456 · Vijayawada 4,167 · South Bengal 3,984 · Nagpur 3,892 · Vadodara 3,641 · Bhubaneswar HQ 3,596 · Muzaffarpur 3,592 · Ajmer 3,550 · Bareilly 3,525 · Central Region Trichirapalli 3,510 … down to *Mumbai Region* 242 and singleton anomalies *Eastern Command* / *Western Command* (1 each). `DivReportingCircle` is the catch-all for smaller circles (Jharkhand 4,598, Chattisgarh 4,475, Himachal 2,811, etc.).

**Top 20 districts (of 749) by office count:** Y.S.R. 819 · PUNE 801 · 24 PARAGANAS SOUTH 774 · PRAKASAM 757 · MAYURBHANJ 728 · BELAGAVI 721 · GANJAM 707 · 24 PARAGANAS NORTH 694 · NASHIK 684 · SATARA 673 · RAIPUR 672 · AHMEDNAGAR 666 · RATNAGIRI 663 · AURANGABAD 651 · KANGRA 651 · BARMER 638 · MEDINIPUR EAST 630 · SPSR NELLORE 618 · MEDINIPUR WEST 604 (+ 1 more). (Plus 715 rows with blank district.)

### Pincode sharing

- **19,586 distinct pincodes** across **165,627 offices** → on average **8.46 offices per pincode** (median 7).
- **17,443 pincodes (89%) are shared by >1 office;** only 2,143 pincodes map to a single office.
- This is by design: **Branch Offices inherit the pincode of their parent Sub/Head Office.** In the most-shared pincodes the offices are almost entirely BOs.
- **Most-shared pincodes:** 791122 (Arunachal Pradesh) = **153 offices** (152 BO + 1 PO); 791118 = 149; 345001 (Rajasthan) = 119; 494450 (Chhattisgarh) = 102; 790102 (Arunachal) = 98; 792110 = 89; 494661 = 75; 793119 (Meghalaya) = 75; 822125 (Jharkhand) = 73; 794102 (Meghalaya) = 71. High sharing clusters in sparsely-settled NE/tribal districts where one pincode blankets a huge rural area.
- All pincodes are well-formed 6-digit codes (range 110001–900099); 0 malformed.

### Geo-coverage & data-quality

Latitude/longitude arrive as **text strings** and must be coerced to numeric. They are the dirtiest columns in the file.

- **Missing coordinates:** 12,007 rows missing latitude, 12,002 missing longitude; **12,015 rows (7.3%) lack at least one coordinate**. A further **6 values each** are present-but-unparseable (junk text). **153,612 rows (92.7%) have both coordinates present.**
- **India bounding-box check (lat 6–37, lon 68–98):**
  - 1,804 present latitudes fall outside [6,37]; 2,327 present longitudes fall outside [68,98].
  - **2,613 rows fail the bbox test in total.** Only **151,005 rows (91.2% of all rows)** have both coordinates present *and* inside the India box.
- **Impossible magnitudes:** 194 rows have latitude > 90 and 55 rows have longitude > 180 (impossible on Earth). Observed maxima are absurd: lat up to ~2.34×10⁸, lon up to ~9.33×10⁹ — clearly decimal-point / digit-concatenation corruption.
- **Swapped lat/lon:** **791 rows** have latitude in 68–98 and longitude in 6–37 — i.e. the two columns are transposed (e.g. *Kasimpalli B.O*, Telangana, recorded as lat 79.0 / lon 17.0, which is the reverse of its true location).
- **Suspected placeholder duplicates:** **730 rows** have latitude exactly equal to longitude (e.g. *Yellareddypalli B.O* = 18.169028/18.169028); 13 rows have lat=0 and 13 have lon=0 (null-island placeholders).
- **Recommendation for downstream geo use:** restrict to the **151,005 in-bbox rows** only; treat coordinates as best-effort enrichment, not authoritative, and never key spatial joins on the swapped/zero/oversized rows.

### Other quality notes

- `district` and `statename` share the **same 715 missing rows** — those records have full hierarchy/pincode but no resolved state/district.
- `officename` is **not unique** (145,086 distinct names for 165,627 rows): 10,911 names recur (e.g. *Rampur BO* appears 57 times in different states). Names are also **inconsistently formatted** — both `Rampur BO` and `Rampur B.O` exist — so suffix-based parsing must normalize punctuation/case before use; trust the `officetype` column instead.
- `regionname` contains two stray military values (*EASTERN COMMAND*, *WESTERN COMMAND*, 1 row each), likely tied to the *APS Circle* records.
