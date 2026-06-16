## Child Immunization (NFHS-5, district factsheets) — columns 53-64

Theme coverage across all 706 NFHS-5 (2019-21) district rows (698 distinct districts, 36 states/UTs). Every figure below is computed **nationally** after applying the standard NFHS value-cleaning rules: `*` = suppressed (<25 unweighted cases, treated as missing), `(value)` = small-sample (25-49 unweighted cases, used with caution), with whitespace and thousands-separators stripped. All 12 indicators in this range are **percentages (0-100)** read at the **district level**.

### The two "fully vaccinated" bases (read this first)

NFHS-5 reports the share of children **12-23 months who are FULLY vaccinated** twice, on two different evidence bases, and they are NOT interchangeable:

- **Index 53 — "based on information from EITHER source" (card + recall).** A child counts as fully vaccinated if each dose is documented on the vaccination card **OR** reported by the mother from recall. This is the headline, internationally comparable figure and the one most people mean by "fully immunized." National district mean = **77.68%** (median 78.0).
- **Index 54 — "based on information from the VACCINATION CARD only."** Restricts evidence to doses actually written on a card that was seen; recall is excluded. Because it conditions on children who *have* a card and ignores undocumented-but-real doses, it sits on a smaller, self-selected denominator and reads systematically **higher** (mean 84.02, median 84.95) than the either-source figure. It measures documentation quality as much as true coverage and should never be compared head-to-head with other surveys' "fully vaccinated" rates.

"Fully vaccinated" in NFHS-5 = BCG + 3 doses polio + 3 doses penta/DPT + 1 dose measles (MCV1). It does NOT require MCV2, rotavirus, or hep-B as a separate shot, which is why those individual antigens (below) can sit far above or below the headline number.

### Data dictionary table

| Column name | What it measures (NFHS-5 definition) | Population / denominator | Unit & direction | n_valid (/706) | %suppressed | %small-sample | mean | median | min (district) | max (district) |
|---|---|---|---|---|---|---|---|---|---|---|
| child_12_23m_fully_vaccinated_based_on_information_from_eit_pct (53) | Fully vaccinated (BCG+3 polio+3 penta/DPT+MCV1) per **card OR mother's recall** | Children 12-23 months | % higher=better | 693 | 1.8% | 32.9% | 77.68 | 78.00 | 38.3 Udalguri (Assam) | 100.0 Dadra & Nagar Haveli (DNH&DD) |
| child_12_23m_fully_vaccinated_based_on_information_from_vax_pct (54) | Fully vaccinated documented on the **vaccination card only** (recall excluded) | Children 12-23 months (card-holders) | % higher=better (conditioned on card) | 684 | 3.1% | 45.8% | 84.02 | 84.95 | 45.0 Ukhrul (Manipur) | 100.0 Srikakulam (Andhra Pradesh) |
| child_12_23m_who_have_received_bcg_pct (55) | Received **BCG** (TB) vaccine, single dose at/near birth | Children 12-23 months | % higher=better | 693 | 1.8% | 32.9% | 95.01 | 96.00 | 65.9 North Garo Hills (Meghalaya) | 100.0 South Andaman (A&N Islands) |
| child_12_23m_who_have_received_3_doses_of_polio_vaccine_pct (56) | Received **3 doses of polio** vaccine (OPV/IPV series) | Children 12-23 months | % higher=better | 693 | 1.8% | 32.9% | 81.50 | 82.20 | 47.6 Tuensang (Nagaland) | 100.0 Dadra & Nagar Haveli (DNH&DD) |
| child_12_23m_who_have_received_3_doses_of_penta_or_dpt_vacc_pct (57) | Received **3 doses of pentavalent OR DPT** (diphtheria-pertussis-tetanus core) | Children 12-23 months | % higher=better | 693 | 1.8% | 32.9% | 87.34 | 88.80 | 53.3 Ukhrul (Manipur) | 100.0 Diu (DNH&DD) |
| child_12_23m_who_have_received_the_first_dose_of_mcv_mcv_pct (58) | Received **first dose of measles-containing vaccine (MCV1)** | Children 12-23 months | % higher=better | 693 | 1.8% | 32.9% | 88.46 | 89.60 | 53.2 Ukhrul (Manipur) | 100.0 Diu (DNH&DD) |
| child_24_35m_who_have_received_a_second_dose_of_mcv_mcv_pct (59) | Received **second dose of measles-containing vaccine (MCV2)** | Children **24-35 months** (older cohort) | % higher=better | 693 | 1.8% | 32.9% | 31.87 | 31.40 | 2.8 North Garo Hills (Meghalaya) | 63.8 Diu (DNH&DD) |
| child_12_23m_who_have_received_3_doses_of_rotavirus_vaccine_pct (60) | Received **3 doses of rotavirus** vaccine (diarrhoeal) | Children 12-23 months | % higher=better | 693 | 1.8% | 32.9% | 39.13 | 39.90 | 0.0 South Andaman (A&N Islands) | 100.0 Chamba (Himachal Pradesh) |
| child_12_23m_who_have_received_3_doses_of_penta_or_hepatiti_pct (61) | Received **3 doses of pentavalent OR hepatitis-B** (hep-B component) | Children 12-23 months | % higher=better | 693 | 1.8% | 32.9% | 84.66 | 86.30 | 39.5 North Garo Hills (Meghalaya) | 100.0 Diu (DNH&DD) |
| child_9_35m_who_received_a_vit_a_in_the_last_6_months_pct (62) | Received a **vitamin-A dose in the last 6 months** (supplementation, not a vaccine) | Children **9-35 months** | % higher=better | 705 | 0.1% | 0.7% | 72.27 | 73.00 | 27.5 Tuensang (Nagaland) | 98.1 Mysore (Karnataka) |
| child_12_23m_who_received_most_of_their_vaccinations_in_a_p_pct (63) | Received **most vaccinations in a PUBLIC** health facility | Children 12-23 months who were vaccinated | % (sourcing, not coverage) | 690 | 2.3% | 35.7% | 95.70 | 97.30 | 67.1 Bangalore (Karnataka) | 100.0 Nicobars (A&N Islands) |
| child_12_23m_who_received_most_of_their_vaccinations_in_a_2_pct (64) | Received **most vaccinations in a PRIVATE/other** facility | Children 12-23 months who were vaccinated | % (sourcing, not coverage) | 690 | 2.3% | 35.7% | 3.21 | 1.60 | 0.0 Nicobars (A&N Islands) | 32.9 Bangalore (Karnataka) |

Selected quartiles: headline either-source (53) Q1=69.7 / Q3=87.1; card-only (54) Q1=77.4 / Q3=92.2; rotavirus (60) Q1=5.2 / Q3=69.5 (extremely wide); public-sector share (63) Q1=93.5 / Q3=100.0; private/other (64) Q1=0.0 / Q3=4.7.

### Nuances & caveats

- **Small-sample contamination is severe in this theme.** ~33% of valid district values (232/706) on most antigen columns — and **45.8% on the card-only measure (col 54)** — are flagged as based on only 25-49 unweighted cases. Many district point estimates, especially the 100.0% maxima (Diu, Dadra & Nagar Haveli, Srikakulam) and the lowest values from small Northeast-hill districts, are statistically fragile. Treat district extremes as indicative, not definitive; state-level rollups are far more stable. Suppression is light (~13 districts, 1.8%) except col 54 (22 districts, 3.1%).

- **MCV2 (col 59) is on a different, older cohort (24-35 months) and looks alarmingly low (mean 31.9%) by design, not by failure.** MCV2 was introduced into India's Universal Immunization Programme relatively recently, so at survey time much of the 24-35m cohort had aged past the recommended MCV2 window before the dose was widely available. A low MCV2 here does NOT carry the same meaning as a low BCG — it largely reflects programme roll-out timing. North Garo Hills (2.8%) is the extreme low; even the maximum (Diu) only reaches 63.8%.

- **Rotavirus (col 60) is a roll-out map, not a quality map (std = 32.2, the widest spread in the theme).** Rotavirus vaccine was phased into states in different years, so the 0.0% (South Andaman) vs 100.0% (Chamba) range reflects *whether the state had introduced rotavirus into routine immunization yet*, not differential parental uptake. The distribution is essentially bimodal: Q1 = 5.2 but Q3 = 69.5. Do not rank districts on this column without accounting for state introduction status.

- **BCG is the ceiling and full-schedule completion is the floor — that gap is the "dropout" signal.** BCG (mean 95.0, given at birth) is near-universal because mothers reach a facility for delivery; coverage then erodes dose-by-dose (penta3 87.3, MCV1 88.5) down to *fully* vaccinated at 77.7%. The ~17-point BCG-to-fully gap is the operational dropout indicator — children who start but never complete the schedule.

- **The two "penta-or-X" columns are NOT duplicates.** Col 57 (penta **or DPT**) measures the diphtheria/pertussis/tetanus core; col 61 (penta **or hepatitis-B**) measures the hep-B component. Both are satisfied by the same pentavalent shot where pentavalent is used, but they diverge where standalone DPT is given without hep-B, which is why col 61 (mean 84.7) trails col 57 (mean 87.3).

- **Vitamin-A (col 62) is supplementation, not vaccination, and uses yet another denominator (9-35 months).** It is a 6-month-recall question capturing recent campaign reach, so it should not be folded into "immunization coverage." It is also the cleanest column in the theme: 705/706 valid, only 1 suppressed and 5 small-sample.

- **Place-of-vaccination columns (63 & 64) are conditional and complementary, not coverage.** They are computed only among children who *were* vaccinated and describe *where* (public vs private/other); col 63 + col 64 ≈ 100 at the district level (national means 95.7 + 3.2). A low public-sector share is not inherently a bad outcome — it signals private-sector reliance. The sharpest contrast: **Bangalore is simultaneously the public-sector minimum (67.1%) and the private/other maximum (32.9%)** — roughly a third of Bangalore's vaccinated children used private providers, by far the highest privatization in the country. Conversely, Nicobars is essentially 100% public.

- **Never average or interchange the two "fully vaccinated" bases** (see header note): col 53 (card+recall, the comparable headline) vs col 54 (card-only, a documentation-quality proxy on a self-selected card-holding denominator). The ~6-point gap between their means is mostly a card-availability artefact, not a true coverage difference.
