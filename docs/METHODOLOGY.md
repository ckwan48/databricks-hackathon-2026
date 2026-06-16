# Methodology — the inner mechanics of facilitiesHelp.io

How a pile of 10,000 scraped, uneven facility records becomes a trust grade, a confidence number, and a care-gap classification you can defend.

---

## 1. Medallion pipeline (bronze → silver → gold)

All transforms run on a serverless **SQL Warehouse**, reading the read-only Marketplace catalog and writing to `workspace.virtue_gold`.

- **Bronze** = the raw Marketplace tables (`facilities`, `india_post_pincode_directory`, `nfhs_5_district_health_indicators`).
- **Silver** (`silver_facility`): one row per facility. Steps:
  - **Entity resolution / dedup** — `row_number() OVER (PARTITION BY cluster_id ORDER BY unique_id)` keeps one canonical record per `cluster_id` (the dataset's pre-computed match key), collapsing duplicates scraped from many sources.
  - **Evidence text assembly** — lowercased concatenation of `description + capability + procedure + equipment` → `evidence_text`; `specialties` → `spec_text`.
  - **Source counting** — `n_sources` = number of *distinct* `source_types`; up to 8 `source_urls` retained.
  - **Geo join** — `address_zipOrPostcode` → 6-digit PIN → joined to the India-Post directory for `district_n` / `state_n`.
- **Gold** = the decision tables (trust, specialty grades, district gaps, referral index, readiness, contact, NFHS, PIN coverage) the app reads directly.

## 2. The trust-grading rubric (deterministic + auditable)

For each (facility × capability), two evidence signals are tested against the facility's own text:

| Signal | Test |
|---|---|
| **specialty-code match** (`spec_hit`) | `spec_text RLIKE <specialty regex>` |
| **equipment/procedure-text match** (`text_hit`) | `evidence_text RLIKE <keyword regex>` |
| **independent sources** (`n_sources`) | distinct `source_types` |

**Grade:**
```
WEAK/SUSPICIOUS  if the facility type contradicts the claim
                 (clinic / dentist / doctor / pharmacy claims an ACUTE capability
                  via free-text but has NO matching specialty code)
STRONG           if spec_hit AND text_hit
PARTIAL          if spec_hit OR text_hit
NO CLAIM         otherwise   (dropped — never shown)
```

**Confidence (0–100)** — a probability the claim is genuine, not a guarantee:
```
STRONG          = least(95, 70 + 5 × n_sources)
PARTIAL         = 50
WEAK/SUSPICIOUS = 20
```

We grade **22 high-stakes capabilities** with this enhanced rubric (it includes the contradiction check), and **every one of the 2,580 specialties** a facility lists with a generalized version (`gold_facility_specialty`): STRONG if corroborated in free-text + ≥2 sources, PARTIAL for one signal, CLAIMED if only listed in the structured field.

## 3. Why the grade is trustworthy — model validation (not a guess)

The attribution and confidence are validated on the raw data (`/tmp` analysis, scikit-learn):

- **Reproducibility of the grade.** A logistic regression `STRONG ~ spec_hit + text_hit + n_sources` reproduces the grade with **5-fold ROC-AUC = 1.00** — confirming the grade is a transparent, deterministic function of its evidence signals (≈49% specialty code, ≈51% procedure/equipment text).
- **The grade is NOT a popularity proxy.** A gradient-boosting model predicting STRONG from facility **metadata alone** (capacity, doctors, web presence, #specialties, facility type) — *excluding* the rule inputs — scores only **4-fold ROC-AUC = 0.57 (near chance)**. This is the important result: a facility's size/fame barely predicts its grade, so the grade reflects **cited evidence, not prestige.**
- Per-card **SHAP-style attribution** decomposes each confidence score into its contributing signals.

## 4. District care-gap classification (Track 2)

For each (capability × district), aggregated over distinct facilities:
```
DATA-POOR          if  count(distinct cluster_id) < 3       → too few records to judge (NOT "no care")
APPARENT CARE GAP  if  n_strong < 2                         → facilities exist but little trustworthy evidence
EVIDENCED SUPPLY   otherwise
```
This is the honesty hinge: it separates a **real gap** from a region we simply **under-measured**. Pre-computed for all 2,518 capabilities in `gold_all_gaps`.

## 5. Referral ranking (Track 3)

Geocoding resolves *any* city/district/place to a centroid from the 165,627-office India-Post directory (lat/long bounded to India: 6–38°N, 67–98°E to reject corrupt coordinates). Facilities are ranked **evidence-first (STRONG → PARTIAL → CLAIMED), then by great-circle (haversine) distance**:
```
d = 6371 · acos( sin φ₁ sin φ₂ + cos φ₁ cos φ₂ cos(λ₂−λ₁) )   [km]
```

## 6. Honesty guarantees

- Every claim **cites the facility's own text** + ranked source links (credible domains first).
- **Confidence is always shown**; weak evidence is never presented as fact.
- The Copilot **refuses to invent numbers** — it answers only from grounded gold-table data or says it has none.
- User actions (overrides, shortlists, scenarios, chats) persist to `app_user_actions` (Delta; Lakebase-ready).

See [`CAUSAL_INFERENCE.md`](CAUSAL_INFERENCE.md) for the correlation-vs-causation layer and [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for the tables.
