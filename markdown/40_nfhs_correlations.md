## NFHS-5 District-Level Correlation & Relationship Analysis

**Scope.** All 107 numeric NFHS-5 indicators were cleaned (`*` -> suppressed; parenthesised values -> small-sample, parens stripped; whitespace trimmed) and run through a **pairwise Pearson correlation matrix** over the 706 national district rows (698 distinct districts, 36 states/UTs). Every pair required **>= 50 overlapping valid districts**. This yielded **5,663 testable pairs**. Spearman rank correlation was computed alongside Pearson for all reported pairs to flag nonlinearity/outliers.

**Multiple-testing control (Benjamini-Hochberg FDR, q = 0.05).** Of the 5,663 pairs, **3,852 (68%) survive BH-FDR** at q = 0.05; the BH p-value threshold is **p <= 3.37e-02**. So roughly two-thirds of all indicator pairs are "statistically significant" associations — a direct consequence of strong common geographic gradients across Indian districts (the North/Central vs South/coastal development divide loads onto almost everything). Significance is therefore cheap here; **effect size (|r|) and plausibility matter far more than the p-value.**

**Tiering of the 5,614 non-redundant pairs (BH-significant subset, n = 3,803):**

| Tier | Definition | Count |
|---|---|---|
| HIGH | \|r\| >= 0.6 | 109 |
| MEDIUM | 0.4 <= \|r\| < 0.6 | 439 |
| LOW | 0.2 <= \|r\| < 0.4 | 1,532 |
| negligible | \|r\| < 0.2 (but still BH-sig) | 1,723 |

**Redundant / tautological pairs (49 excluded from the tables below, but they exist and are real).** These measure essentially the same construct and would otherwise dominate the top of the list:
- `fp_any_method` vs `fp_modern_method` (modern is a subset of any).
- The two "fully vaccinated" bases — *eit* (any source) vs *vax* card-only (r = +0.82).
- Anaemia measures among themselves: `all_w15_49_anaemic` vs `non_pregnant_w15_49_anaemic` (**r = +0.999**), vs `teen_women_anaemic` (r ~ +0.91).
- Blood-sugar composites vs their components (`high_or_very_high` contains `very_high`, r up to +0.95); BP composites vs `mildly/moderately high` components (r up to +0.94).
- IFA-100-days vs IFA-180-days (r = +0.91); total-adequate-diet vs its breastfed/non-breastfed sub-bases (r = +0.96); total C-section vs public-facility C-section (r = +0.95); female ever-schooled vs women literate (r = +0.93).

---

### Strongest associations

#### TOP 20 POSITIVE (non-redundant)

| # | Indicator A | Indicator B | Pearson r | Spearman | n |
|---|---|---|---|---|---|
| 1 | institutional birth (5y) | births attended by skilled provider | +0.946 | +0.904 | 706 |
| 2 | women high/v-high blood sugar | men high/v-high blood sugar | +0.906 | +0.897 | 706 |
| 3 | women very-high blood sugar (>160) | men very-high blood sugar (>160) | +0.891 | +0.881 | 706 |
| 4 | women high/v-high blood sugar | men very-high blood sugar | +0.877 | +0.867 | 706 |
| 5 | women high BP (>=140/90) | men high BP (>=140/90) | +0.863 | +0.856 | 706 |
| 6 | FP unmet need (total) | FP unmet need (spacing) | +0.849 | +0.865 | 706 |
| 7 | women mildly-high BP | men mildly-high BP | +0.847 | +0.831 | 706 |
| 8 | child wasted (WfH) | child severely wasted (WfH) | +0.844 | +0.827 | 706 |
| 9 | women very-high blood sugar | men high/v-high blood sugar | +0.840 | +0.820 | 706 |
| 10 | women ever had cervical screen | women ever had breast exam | +0.839 | **+0.657** | 706 |
| 11 | child received PNC | institutional birth (5y) | +0.823 | +0.829 | 706 |
| 12 | fully vaccinated (eit base) | fully vaccinated (vax-card base) | +0.822 | +0.805 | 684 |
| 13 | mother received PNC | institutional birth (5y) | +0.812 | +0.805 | 706 |
| 14 | women moderately/severely high BP | men moderately/severely high BP | +0.801 | +0.796 | 706 |
| 15 | women mildly-high BP | men high BP (composite) | +0.799 | +0.787 | 706 |
| 16 | women high blood sugar (141-160) | men high blood sugar (141-160) | +0.796 | +0.798 | 706 |
| 17 | mother received PNC | skilled birth attendant | +0.793 | +0.764 | 706 |
| 18 | child received PNC | skilled birth attendant | +0.792 | +0.772 | 706 |
| 19 | men mildly-high BP | men moderately/severely high BP | +0.788 | +0.778 | 706 |
| 20 | women high BP (composite) | men mildly-high BP | +0.784 | +0.780 | 706 |

#### TOP 20 NEGATIVE (non-redundant)

| # | Indicator A | Indicator B | Pearson r | Spearman | n |
|---|---|---|---|---|---|
| 1 | FP any method (current use) | FP unmet need (total) | -0.860 | -0.845 | 706 |
| 2 | institutional birth (5y) | home birth by skilled provider | -0.800 | **-0.861** | 706 |
| 3 | FP any method | FP unmet need (spacing) | -0.778 | -0.752 | 706 |
| 4 | FP modern method | FP unmet need (total) | -0.722 | -0.696 | 706 |
| 5 | population below age 15 | deaths last 3y civil-registered | -0.671 | -0.678 | 705 |
| 6 | child received PNC | home birth by skilled provider | -0.666 | **-0.728** | 706 |
| 7 | women overweight/obese (BMI>=25) | men tobacco use | -0.665 | -0.652 | 706 |
| 8 | home birth by skilled provider | skilled birth attendant | -0.655 | **-0.720** | 706 |
| 9 | women 10+ yrs schooling | women married before 18 | -0.652 | -0.668 | 706 |
| 10 | households using clean cooking fuel | men tobacco use | -0.652 | -0.666 | 706 |
| 11 | births delivered by C-section | men tobacco use | -0.643 | -0.647 | 706 |
| 12 | population below age 15 | C-section delivery | -0.640 | **-0.735** | 706 |
| 13 | population below age 15 | child birth registered | -0.635 | -0.619 | 706 |
| 14 | mother received PNC | home birth by skilled provider | -0.629 | **-0.694** | 706 |
| 15 | population below age 15 | women 10+ yrs schooling | -0.624 | -0.639 | 706 |
| 16 | population below age 15 | C-section in public facility | -0.624 | **-0.743** | 706 |
| 17 | population below age 15 | institutional birth (5y) | -0.622 | **-0.716** | 706 |
| 18 | improved sanitation | women underweight BMI (<18.5) | -0.618 | -0.617 | 706 |
| 19 | population below age 15 | mothers with 4+ ANC visits | -0.616 | -0.627 | 706 |
| 20 | women 10+ yrs schooling | men tobacco use | -0.615 | -0.613 | 706 |

**Pearson vs Spearman divergences (nonlinearity / outliers).** Most pairs agree closely. The biggest gaps:
- **Cervical screen ~ breast exam: Pearson +0.839 but Spearman only +0.657.** Both indicators are near-zero in most districts with a long right tail (a handful of southern districts with active screening programmes), so Pearson is inflated by a few high-leverage points; the rank correlation is the more honest figure.
- The **`population below age 15`** cluster (rows 12, 16, 17 negative) and **home-birth-by-skilled-provider** pairs are all *stronger* in Spearman (e.g. pop<15 vs C-section -0.64 Pearson -> -0.74 Spearman; institutional birth vs skilled home-birth -0.80 -> -0.86), indicating a **monotonic but curved** relationship — high-fertility (young-population) districts have systematically lower facility-delivery/screening uptake, but not linearly.

---

### Interpretation (causally-plausible relationships)

1. **Female schooling vs child marriage — r = -0.65 (HIGH; Spearman -0.67).** Districts where more women have 10+ years of schooling have markedly less marriage before 18. Headline: schooling ranges from 13.6% (Pakur, Jharkhand) to 88.2% (Mahe, Puducherry); child marriage from 0.0% (Pathanamthitta, Kerala) to 57.6% (Purba Medinipur, West Bengal). One of the cleanest education-empowerment signals in the dataset.

2. **Female schooling vs teen motherhood — r = -0.44 (MEDIUM).** Same direction as #1: more-educated districts have fewer 15-19-year-olds already mothers/pregnant. Schooling delays both marriage and first birth.

3. **Family-planning use vs unmet need — r = -0.86 (HIGH).** The single strongest non-redundant negative association: districts that have converted demand into actual contraceptive use have little unmet need. Modern-method use vs unmet need is -0.72. This is close to definitional (use and unmet-need partition the demand pool) but quantifies how completely services close the gap.

4. **Institutional birth vs C-section rate — r = +0.54 (MEDIUM; Spearman +0.69).** As facility delivery rises, so does the C-section share — the curvature (Spearman > Pearson) suggests C-section climbs faster once facility delivery is near-universal, the classic over-medicalisation tail. Institutional birth also tracks skilled-attendant (+0.95), mother-PNC (+0.81) and child-PNC (+0.82): facility delivery is the hub of the entire maternal continuum-of-care.

5. **Sanitation vs child stunting — r = -0.51 (MEDIUM); clean cooking fuel vs stunting — r = -0.42 (MEDIUM).** Districts with better improved-sanitation coverage and clean-fuel access have lower under-5 stunting, consistent with the WASH-enteropathy and indoor-air-pollution pathways. Stunting itself ranges 13.2% (Jagatsinghapur, Odisha) to 60.6% (Pashchimi Singhbhum, Jharkhand).

6. **Women overweight/obese vs high blood sugar — r = +0.62 (HIGH); vs high BP — r = +0.57 (MEDIUM).** The metabolic-syndrome cluster: districts with more overweight/obese women have more diabetes and hypertension. Women's and men's blood sugar (+0.91), very-high sugar (+0.89) and high BP (+0.86) are tightly coupled across districts — NCD burden is an environmental/dietary district trait shared by both sexes, not just an individual one.

7. **The double burden of malnutrition — child stunting vs women underweight BMI — r = +0.55 (MEDIUM); women overweight/obese vs child stunting — r = -0.56 (MEDIUM).** Two faces of the same gradient: poorer districts carry *both* thin women and stunted children, while more affluent districts shift toward maternal over-nutrition and lower child stunting. Stunting and child underweight co-move at r = +0.70.

8. **Tobacco/clean-fuel/development axis — clean fuel vs men's tobacco r = -0.65; women overweight vs men's tobacco r = -0.67; C-section vs men's tobacco r = -0.64; women schooling vs men's tobacco r = -0.62 (all HIGH).** Male tobacco use is a strong *negative* marker of district affluence: it falls where clean fuel, education, facility delivery and maternal over-nutrition rise. This is an ecological signal of the development gradient, not a causal effect of any one variable.

9. **High-fertility (young-population) districts lag on services — pop<15 vs institutional birth r = -0.62, vs 4+ ANC visits -0.62, vs women schooling -0.62, vs C-section -0.64 (all HIGH, Spearman stronger).** A district's share of population under 15 (a proxy for high fertility / earlier demographic stage) is the most pervasive negative correlate of maternal-health and education indicators — it is essentially a composite "underdevelopment" axis.

10. **Co-occurring behaviours — men's vs women's alcohol r = +0.73; men's vs women's tobacco r = +0.67 (HIGH).** Substance-use norms cluster by district and cut across sex — likely cultural/regional (high in some North-East and tribal-belt districts).

11. **Sanitation vs women's education — r = +0.58 (MEDIUM).** Infrastructure and human-capital development rise together; a useful confounding warning for #5/#6 (see below).

12. **Maternal-care continuum coherence — mother-PNC vs child-PNC r = +0.95; PNC vs skilled attendance ~ +0.79.** Where one element of the postnatal/delivery package is delivered, the others are too: the system tends to work (or fail) as a bundle at district level.

---

### Confounding & ecological-fallacy caveats

- **These are DISTRICT-level (ecological) correlations, not individual-level causation.** A district correlation of, say, sanitation vs stunting (-0.51) does **not** mean an individual child with a latrine is 51% less likely to be stunted. Aggregation can both inflate correlations (shared geographic gradients) and reverse signs (Simpson's paradox / ecological fallacy). Inferring individual risk from these numbers is invalid.
- **A dominant common confounder — district development / wealth / region** — drives most of the headline associations. Education, sanitation, clean fuel, facility delivery, maternal over-nutrition and (inverse) male tobacco all load onto a single North-Central-vs-South/coastal axis. Many bivariate r's would shrink substantially after adjusting for state/wealth; treat them as *associational fingerprints of the development gradient*, not isolated causal levers.
- **Reverse/definitional links** sit in some "interesting" pairs (FP use vs unmet need; institutional birth vs home-birth-by-skilled-provider, r = -0.80, which is near-complementary).
- **Suppression is non-random and concentrated.** 29 columns carry suppressed (`*`) values; mean ~39 suppressed districts/column. Worst: non-breastfeeding adequate-diet (91.1% suppressed, n = 63 — its r's, e.g. with total adequate diet, rest on tiny overlap), child 6-8m solid food (90.9%), the three diarrhoea-treatment indicators (69.7% each, n = 214), home-birth-to-facility (59.8%), exclusive breastfeeding (37.0%). Correlations involving these rest on a self-selected subset of larger/surveyed districts and should be read with caution; the n column in the tables above flags the few pairs (e.g. fully-vaccinated bases, n = 684) that fall below the full 706.
- **Small-sample (parenthesised) values were retained but flagged**; several maternal/child columns (e.g. exclusive breastfeeding: 347 small-sample districts, pregnant-women anaemia: 421) lean heavily on 25-49-case estimates, adding noise that attenuates true associations.
- **Multiplicity:** with 5,663 tests, ~283 false positives would be expected at an uncorrected alpha = 0.05; BH-FDR (q = 0.05, threshold p <= 3.37e-02) bounds the expected false-discovery proportion among the 3,852 "significant" pairs to ~5%. Even so, focus interpretation on the HIGH/MEDIUM tiers — the 1,723 BH-significant but |r| < 0.2 pairs are statistically real yet substantively trivial.
