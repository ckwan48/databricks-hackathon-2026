## Geographic, Trust-Weighted Capability Gap Analysis (National)

**Question this answers for planners:** where are the *real* clinical-capability gaps, versus regions that merely *look* empty because we have too little data? We separate the two explicitly.

### Method

1. **District derivation.** Each facility's 6-digit `address_zipOrPostcode` was joined to `india_post.pincode` -> `(district, state)`. **9,564 of 10,088 facilities (94.8%)** matched a PIN to a district. The remaining 524 fell back to a cleaned `address_stateOrRegion` for state (only 12 values were garbage >40 chars, 63 empty), and to a `"... (district unknown)"` bucket for district.
2. **Trust-graded evidence.** We used the long capability-trust table (`facility_capability_trust.csv`, 70,616 rows = 10,077 facilities x 7 capabilities) where every facility x capability carries a grade: STRONG / PARTIAL / WEAK-SUSPICIOUS / NO CLAIM (national grade mix: 10,048 STRONG, 9,143 PARTIAL, 3,454 WEAK, 47,971 NO CLAIM).
3. **Dedup.** Aggregation collapses co-clustered duplicates on `cluster_id` (keeping the strongest grade per cluster), so multi-source duplicate rows are not double-counted.
4. **Trust-weighted score** per region x capability = mean of grade weights (STRONG=1.0, PARTIAL=0.5, WEAK=0.1, NO CLAIM=0.0), range 0-1. We also track strong/partial share and the mean evidence fill-rate over 7 evidence columns (`source_types, source_ids, specialties, procedure, equipment, capability, source_urls`).

### Classification rule (explicit, scaled to full data)

For each region x capability:

| Class | Rule |
|---|---|
| **DATA-POOR** | `n_facilities < 5` **OR** mean evidence fill-rate `< 0.50` — too thin to conclude |
| **APPARENT CARE GAP** | `n_facilities >= 5` **AND** (strong+partial) share `< 0.20` — supply present, but little trust-worthy capability evidence |
| **EVIDENCED SUPPLY** | otherwise |

Across all region x capability cells: **2,345 DATA-POOR, 718 APPARENT CARE GAP, 1,557 EVIDENCED SUPPLY**.

### National capability picture (which services are weakest)

Strong/partial evidence is scarce for high-acuity neonatal and renal care everywhere:

| Capability | STRONG share | STRONG+PARTIAL share |
|---|---|---|
| NICU / neonatal | 6.7% | **13.6%** |
| dialysis / renal | 8.3% | 20.7% |
| oncology / cancer | 11.3% | 22.0% |
| ICU / critical care | 10.6% | 25.5% |
| emergency | 12.8% | 29.9% |
| trauma / orthopedic | 23.7% | 36.9% |
| maternity / obstetrics | 26.2% | 41.7% |

Among the **298 districts with >=5 facilities**, NICU is an APPARENT CARE GAP in **71.8%** of them, dialysis in 47.3%, oncology in 47.0% — while maternity (5.4% gap) and trauma (10.4%) are mostly evidenced. NICU/dialysis/oncology account for **495 of 673 (74%)** district-level capability gaps.

### Ranked state-level table (sorted by facility count)

`cap_*` = how many of the 7 capabilities fall in each class for that state; `mean_wt` = mean trust-weighted score; `fill` = mean evidence fill-rate.

| State | n_fac | EVIDENCED | GAP | DATA-POOR | mean_wt | fill |
|---|--:|--:|--:|--:|--:|--:|
| Maharashtra | 1,647 | 5 | 2 | 0 | 0.208 | 0.94 |
| Gujarat | 997 | 5 | 2 | 0 | 0.171 | 0.94 |
| Uttar Pradesh | 956 | 6 | 1 | 0 | 0.230 | 0.95 |
| Tamil Nadu | 828 | 6 | 1 | 0 | 0.234 | 0.94 |
| Karnataka | 533 | 6 | 1 | 0 | 0.228 | 0.94 |
| Kerala | 520 | 6 | 1 | 0 | 0.219 | 0.95 |
| West Bengal | 493 | 5 | 2 | 0 | 0.192 | 0.95 |
| Punjab | 487 | 6 | 1 | 0 | 0.231 | 0.95 |
| Haryana | 470 | 6 | 1 | 0 | 0.235 | 0.95 |
| Telangana | 461 | 6 | 1 | 0 | 0.209 | 0.94 |
| Rajasthan | 410 | 6 | 1 | 0 | 0.241 | 0.95 |
| **Delhi** | 350 | **2** | **5** | 0 | **0.150** | 0.95 |
| Andhra Pradesh | 317 | 6 | 1 | 0 | 0.228 | 0.94 |
| Madhya Pradesh | 315 | 6 | 1 | 0 | 0.223 | 0.94 |
| Bihar | 262 | 6 | 1 | 0 | 0.225 | 0.94 |
| Jharkhand | 157 | 6 | 1 | 0 | 0.216 | 0.93 |
| Chhattisgarh | 143 | 6 | 1 | 0 | 0.221 | 0.93 |
| Uttarakhand | 130 | 5 | 2 | 0 | 0.236 | 0.95 |
| Odisha | 120 | 4 | 3 | 0 | 0.216 | 0.95 |
| Assam | 119 | 6 | 1 | 0 | 0.237 | 0.95 |
| Jammu & Kashmir | 70 | 5 | 2 | 0 | 0.232 | 0.93 |
| **Chandigarh** | 45 | **1** | **6** | 0 | **0.092** | 0.93 |
| Himachal Pradesh | 38 | 6 | 1 | 0 | 0.231 | 0.92 |
| Goa | 35 | 5 | 2 | 0 | 0.201 | 0.94 |

For every large state, the single gap capability is **NICU** (25 of 45 state-level gaps are NICU). The standouts are **Delhi** (gap in 5 of 7 capabilities despite 350 facilities) and **Chandigarh** (gap in 6 of 7, lowest mean weighted score 0.092). All large states have fill-rate ~0.93-0.95, so these are *evidence-of-capability* gaps, not missing-data artifacts.

### Worst REAL-gap districts (APPARENT CARE GAP, ranked by facility density)

These are dense urban districts with hundreds of facilities yet a thin strong/partial share — the highest-priority "supply exists, capability unverified" cells:

| District | Capability | n_fac | strong | partial | s+p share | fill |
|---|---|--:|--:|--:|--:|--:|
| Pune | NICU / neonatal | 325 | 18 | 29 | 0.145 | 0.95 |
| Pune | dialysis / renal | 325 | 25 | 27 | 0.160 | 0.95 |
| Ahmadabad | NICU / neonatal | 319 | 18 | 15 | 0.103 | 0.95 |
| Ahmadabad | dialysis / renal | 319 | 18 | 24 | 0.132 | 0.95 |
| Bengaluru Urban | NICU / neonatal | 287 | 22 | 20 | 0.146 | 0.94 |
| Chennai | NICU / neonatal | 272 | 13 | 11 | 0.088 | 0.93 |
| Mumbai Suburban | NICU / neonatal | 272 | 8 | 21 | 0.107 | 0.94 |
| Mumbai Suburban | dialysis / renal | 272 | 19 | 23 | 0.154 | 0.94 |
| Chennai | dialysis / renal | 272 | 24 | 27 | 0.188 | 0.93 |
| Chennai | ICU / critical care | 272 | 20 | 34 | 0.199 | 0.93 |
| Kolkata | NICU / neonatal | 184 | 6 | 9 | 0.082 | 0.95 |
| Surat | NICU / neonatal | 161 | 9 | 6 | 0.093 | 0.93 |
| Lucknow | NICU / neonatal | 147 | 11 | 11 | 0.150 | 0.94 |
| Patna | NICU / neonatal | 144 | 10 | 11 | 0.146 | 0.94 |

**Systemic real-gap districts** (>=5 facilities AND >=4 of 7 capabilities classed APPARENT CARE GAP — i.e. a broad capability gap, not a data artifact): **71 districts**. Examples with the widest gaps: Junagadh (7/7 caps, 11 facilities), Purbi Champaran (7/7, 8), Sambalpur (7/7, 7), Vizianagaram (7/7, 7), Chandigarh (6/7, 38), Hanumakonda (6/7, 17), Spsr Nellore (6/7, 12). These are the districts where supply is genuinely on the map but high-acuity capability evidence is near-absent.

### The gap-vs-data-poor call-out (the core deliverable)

- **REAL gaps are concentrated in dense metros, not the rural periphery.** Every top real-gap district above is a Tier-1/Tier-2 urban district with hundreds of facilities and ~94-95% field fill. The gap is *unverified capability*, especially **NICU, dialysis, oncology** — services that need explicit equipment/procedure evidence that scraped pages rarely surface. Planners should read these as **"audit/verify"** targets, not greenfield build targets.
- **DATA-POOR is the rural-coverage problem.** **305 of 602 districts (51%)** are DATA-POOR across all 7 capabilities, but together they hold only **627 facilities (6.3%)** of the national footprint; **304 districts have fewer than 5 facilities**. For these, the binding constraint is *coverage of the dataset itself*, not a proven absence of care — they need more data collection before any gap claim can be made.
- **Bottom line:** the same NICU-shaped weakness appears as an *APPARENT CARE GAP* in metros (lots of facilities, low evidence) and as *DATA-POOR* in rural districts (too few facilities to judge). The two demand opposite interventions — verification/audit in cities, data acquisition in the countryside.

**Caveats.** "Care gap" measures *trust-worthy capability evidence*, not actual clinical capacity — a real ICU with a sparse website grades as a gap, so dense-metro gaps are best read as verification queues. 5.2% of facilities lacked a PIN match and were placed by state only; a handful of `address_stateOrRegion` values are mis-filed districts/garbage (correctly absorbed into low-n DATA-POOR rows). Single-PIN-per-district mode collapses the rare multi-district PINs.

*Artifact: `/Users/koushik/Desktop/health_analysis_outputs/region_capability_gaps.csv` (4,620 rows: 406 state x capability, 4,214 district x capability).*
