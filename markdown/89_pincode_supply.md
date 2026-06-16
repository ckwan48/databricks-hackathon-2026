## Pincode-Granular Supply & Access: From "Which District" to "Which Neighbourhood"

A district-level facility count answers the question *"does this district have care?"* It cannot answer the
question a family actually asks: *"is there care **near me**?"* The pincode layer (`n_pincodes`, `pins_with_fac`,
`pct_zero_pins`, `supply_gini`, `top_pin_share`) decomposes each district's headline supply into its constituent
pincodes and exposes how concentrated — and therefore how locally inaccessible — that supply really is.

**Universe.** Of 706 districts, 569 have pincode data. Among these, **144 are total facility deserts**
(`n_facilities == 0`, every pincode empty — `supply_gini` undefined). The remaining **425 districts have real
facility presence** and are the focus here: these are the places a headline count would mark "served," yet whose
internal distribution can still leave most residents stranded. (`top_pin_share` is on a 0–100 scale = % of a
district's facilities sitting in its single busiest pincode.)

### (1) Worst hidden supply deserts — metros that look served but aren't
We rank within the real-presence universe using a composite **desert score = z(`pct_zero_pins`) + z(`supply_gini`)**,
restricting to districts with **above-median facility counts** (≥4 facilities) so we surface places whose headline
number would *not* trigger concern. These are the analogue of the Pune pattern (a high-count district where most
pincodes are nonetheless empty). The worst hidden deserts:

| Rank | District (State) | Facilities | Pincodes | Pincodes w/ facility | % zero-pincodes | Supply Gini | Top-pin share % |
|---|---|---|---|---|---|---|---|
| 1 | Anantapur (Andhra Pradesh) | 10 | 56 | 2 | 96.4 | 0.98 | 90 |
| 2 | Hoshiarpur (Punjab) | 8 | 52 | 2 | 96.2 | 0.98 | 88 |
| 3 | Mandi (Himachal Pradesh) | 4 | 57 | 2 | 96.5 | 0.97 | 75 |
| 4 | Gaya (Bihar) | 8 | 32 | 1 | 96.9 | 0.97 | 100 |
| 5 | Prakasam (Andhra Pradesh) | 6 | 83 | 3 | 96.4 | 0.97 | 50 |
| 6 | Ganjam (Odisha) | 5 | 80 | 3 | 96.2 | 0.97 | 60 |
| 7 | Sultanpur (Uttar Pradesh) | 4 | 31 | 1 | 96.8 | 0.97 | 100 |
| 8 | Chittoor (Andhra Pradesh) | 21 | 60 | 4 | 93.3 | 0.97 | 86 |

The pattern is stark: districts reporting 8–21 facilities concentrate them into **1–4 pincodes out of 30–84**.
Gaya (8 facilities) and Sultanpur (4 facilities) place **100% of their supply in a single pincode** — every other
neighbourhood is a desert. The headline count is real; the access it implies is fictional.

### (2) The district-average-vs-pincode-reality gap
Across the 425 real-presence districts:
- **Mean 85.2% / median 90.3% of pincodes have zero facilities.** A "served" district is, in the median case, ~90%
  empty by neighbourhood.
- **Mean supply Gini = 0.89** (near-maximal inequality) and **mean top-pin share = 67.4%** — on average two-thirds
  of a district's entire facility stock sits in one pincode.
- **337 of 425 (79%)** real-presence districts have **≥80% of pincodes facility-free** yet are counted as served by a
  district-level metric.
- **All 425** districts have their single busiest pincode holding ≥50% of facilities.

This is the central message: the district average is a near-meaningless summary because supply is not spread, it is
**stacked**. Reading the headline count as "coverage" overstates access for roughly four in five districts.

### (3) Does supply inequality track worse demand (institutional births, full immunisation)?
Unadjusted correlations (n=425 / 415):

| Supply metric | inst_birth (Pearson / Spearman) | full_imm (Pearson / Spearman) |
|---|---|---|
| supply_gini | −0.016 (ns) / −0.039 (ns) | +0.050 (ns) / +0.047 (ns) |
| pct_zero_pins | −0.096 (p=.05) / −0.125 (p=.01) | +0.029 (ns) / +0.023 (ns) |
| **top_pin_share** | **−0.316 (p=2.6e-11)** / −0.355 (p=4.6e-14) | −0.118 (p=.02) / −0.113 (p=.02) |

The one robust raw signal: **the more a district concentrates supply into a single pincode (`top_pin_share`), the
lower its institutional-birth rate** (r=−0.32). Supply *spread* matters more for demand than supply *volume*. Gini
alone is too saturated (almost every district ≈0.89) to discriminate.

**Adjusted (OLS, state fixed effects + urbanicity + log facility count):** the `top_pin_share`→`inst_birth`
association **attenuates to non-significance** (β=−0.015, p=0.33, n=424); none of the supply-inequality terms survive
adjustment for either outcome (all p>0.15). The raw concentration–demand link is therefore **largely confounded by
urbanicity and overall supply scale** — concentration co-travels with rural, low-facility settings rather than
exerting an independent effect detectable at this resolution. This is suggestive *evidence* of an access channel, not
proof of a causal one.

### Why pincode resolution changes the policy question
At the district level, "where should the next facility go?" has only ~706 possible answers and most "served" districts
look fine. The pincode layer reframes it as a **neighbourhood-siting problem**: within a single served district, the
table identifies exactly how many pincodes (e.g. Anantapur's 54 of 56) are empty and how lopsided the existing stock
is. A district like Chittoor (21 facilities) does not need *more* facilities so much as **redistribution away from its
4 hot pincodes**, whereas a true desert (one of the 144 zero-facility districts) needs net new build. Pincode
resolution turns a binary "covered / not covered" district verdict into an actionable map of which neighbourhoods to
fill first.

### Outputs
- Figure: `/Users/koushik/Downloads/DAS_HACK/figures/pincode_deserts.png` (left: facility count vs % empty pincodes,
  sized by pincodes, coloured by Gini; right: worst hidden deserts).
- Table: `/Users/koushik/Desktop/health_analysis_outputs/pincode_supply_layer.csv` (425 ranked real-presence
  districts with desert_score, z-components, and a `hidden_metro_desert` flag).

### Guardrails
**Ecological** (district/pincode aggregates, not individuals — concentration ≠ individual travel time);
**cross-sectional** (no temporal/causal direction); **residual unobserved confounding** (urbanicity adjusts only
partially; terrain, roads, private supply unmodelled); **MNAR** (137 districts lack pincode data, 144 are total
deserts dropped from inequality analysis — likely the most underserved, biasing estimates toward optimism);
**supply_gini is saturated** (≈0.89 everywhere) and discriminates poorly; report as **causal evidence, not proof**.
