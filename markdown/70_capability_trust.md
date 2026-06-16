## Capability Trust-Grading Engine

A deterministic engine grades **every facility x every target capability** (10,088 facilities x 7 capabilities = **70,616 graded cells**) by triangulating evidence across five fields: the structured `specialties` taxonomy, the `equipment` and `procedure` arrays, the `capability` statements, and free-text `description`. Each cell gets one auditable grade plus a numeric `trust_score`, and every grade carries the exact strings that triggered it. This is the FULL national enriched dataset (pipeline `source='kie'`), not a sample.

Artifact: `/Users/koushik/Desktop/health_analysis_outputs/facility_capability_trust.csv` (70,616 rows; columns: `unique_id, name, address_city, address_stateOrRegion, facilityTypeId, capability, grade, trust_score, n_evidence_types, n_distinct_source_types, evidence_snippets, contradiction_flag`). Engine: `build_capability_trust.py`; per-capability distribution: `capability_grade_distribution.csv`.

### What the engine does

For every facility x every target capability it scans five evidence channels and assigns one deterministic trust grade, capturing the exact triggering strings so each cell is auditable:

| Channel | Field | Counts as |
|---|---|---|
| Structured | `specialties` (164-code taxonomy, exact code match) | structured evidence type |
| Structured | `equipment` (lexicon regex on array) | structured evidence type |
| Structured | `procedure` (lexicon regex on array) | structured evidence type |
| Free text | `capability` (lexicon regex) | corroborating text |
| Free text | `description` (lexicon regex) | corroborating text |

A separate set of **related/soft specialties** (e.g. `pediatrics` for NICU, `urology` for renal) corroborates a free-text mention into PARTIAL but is never itself a structured match.

### Rubric (deterministic)

- **STRONG** (score 3): >=2 *independent* structured evidence types agree (e.g. specialty code AND matching equipment/procedure), OR a specialty code + a clear capability statement; AND the claim is consistent with `facilityTypeId`; AND backed by >=2 distinct `source_types` where provenance exists. A would-be-STRONG claim resting on a single low-diversity source is demoted to WEAK.
- **PARTIAL** (score 2): exactly one structured evidence type (specialty-only, equipment-only, or procedure-only), OR a capability/description mention corroborated by a related specialty.
- **WEAK/SUSPICIOUS** (score 1, minus 2 for contradiction -> floored at 0): only a single vague text mention with no structure or related specialty; OR an internal contradiction (capability inconsistent with `facilityTypeId`); OR an otherwise-strong claim on a single source.
- **NO CLAIM** (score 0): no evidence found.

**Contradiction logic.** A `dentist` or `farmacy` claiming any of the seven capabilities, an individual `doctor` claiming any institutional capability, or a `clinic` claiming a heavy-infrastructure capability (ICU, NICU, oncology, dialysis) is flagged. A `clinic` claiming maternity or emergency is *not* a contradiction — those are within a clinic's plausible scope.

**Pattern hygiene.** Bare `delivery` was removed from the maternity lexicon (false-positives on "instrument delivery system" on dental rows and "report/medicine delivery"); maternity requires obstetric context (`cesarean`, `labour ward`, `antenatal`, IVF/IUI/ICSI, etc.). `source_types` is parsed against a whitelist (`overture, dynamic, constant, mongo_facility, mongo_ngo`) because the raw array is occasionally polluted with free-text fragments.

### Grade distribution per capability

| Capability | STRONG | PARTIAL | WEAK/SUSP | NO CLAIM | Any claim |
|---|---:|---:|---:|---:|---:|
| maternity / obstetrics | 2,642 | 1,568 | 667 | 5,211 | 4,877 |
| trauma / orthopedic | 2,388 | 1,330 | 581 | 5,789 | 4,299 |
| emergency | 1,293 | 1,726 | 354 | 6,715 | 3,373 |
| oncology / cancer | 1,138 | 1,077 | 816 | 7,057 | 3,031 |
| ICU / critical care | 1,070 | 1,498 | 351 | 7,169 | 2,919 |
| dialysis / renal | 839 | 1,247 | 404 | 7,598 | 2,490 |
| NICU / neonatal | 678 | 697 | 281 | 8,432 | 1,656 |
| **All capabilities** | **10,048** | **9,143** | **3,454** | **47,971** | **22,645** |

**3,892 distinct facilities (38.6%)** earn >=1 STRONG capability; **3,247 (32.2%)** make no claim on any of the seven. Of the 10,048 STRONG cells, 5,967 are earned by >=2 independent structured types and 4,081 by the specialty-code + capability-statement path. Maternity is the best-evidenced capability (2,642 STRONG, from `gynecologyAndObstetrics`/REI codes plus IVF equipment/procedure); NICU is the rarest (678 STRONG), consistent with neonatal ICU being a scarce, high-infrastructure service. **Oncology carries the most suspicion** — its 816 WEAK cells (and 652 contradictions, below) are the worst of any capability.

### Exemplar STRONG facilities (with earning evidence)

- **Anand Children Hospital** (Surat, Gujarat) — NICU: `neonatologyPerinatalMedicine` + "Ventilated ambulance for neonatal and pediatric transport" (equipment) + neonatal-surgery procedures + capability text; ev=5, 4 distinct sources.
- **Vatsalya Hospital** (Ahmedabad, Gujarat) — maternity: `gynecologyAndObstetrics` + `reproductiveEndocrinologyAndInfertility` + "ICSI machine / Well-equipped IVF laboratory" + IVF procedure; ev=5, **5 distinct sources**.
- **Ganga Hospital** (Coimbatore, Tamil Nadu) — trauma/orthopedic: `orthopedicSurgery` + `pediatricOrthopedicSurgery` + "36 operating theatres dedicated to orthopaedics... and trauma"; ev=5, 4 sources.
- **B P Poddar Hospital** (Kolkata, West Bengal) — oncology: `medicalOncology` + `surgicalOncology` + "Full Field Digital Mammography machine" + "Linear Accelerator and Brachytherapy"; ev=5, 4 sources.
- **Anant Hospital** (Varanasi, UP) — ICU: `criticalCareMedicine` + "Invasive cardiac monitoring equipment for PCWP, CVP" + invasive-monitoring procedures + "ICU Services"; ev=5, 3 sources.
- **Guru Nanak Hospital** (Ranchi, Jharkhand) — dialysis: `nephrology` + "Dialysis unit with 8 beds" + "8-bed artificial kidney dialysis unit" procedure; ev=5, 4 sources.

### Exemplar SUSPICIOUS facilities (with the contradiction)

**1,445 cells are contradiction-flagged.** By type: **clinic 1,278, dentist 144, doctor 14, farmacy 9**; by capability they cluster in oncology (652), dialysis (322), ICU (206), NICU (149) — exactly the heavy-infrastructure services a `clinic` should not own.

- **Neuroxon Healthcare Solutions** (Bengaluru) — **clinic** flagged for ICU: holds a `criticalCareMedicine` code but its "ICU" evidence is "Hectaplex PCR technology for ICU infections diagnostics" — a lab assay, not an intensive-care unit. Clear text-driven mis-tag.
- **Neo Clinic** (Jaipur) — **clinic** flagged for NICU: `neonatologyPerinatalMedicine` + "Fully equipped NICU and PICU facilities". Genuine-sounding but inconsistent with the `clinic` type — a true review case (the type is wrong or the claim inflated).
- **Hb Dialysis Centre**, **St George Charitable Dialysis Centre**, **DKM Diagnostic Centre** (PET-CT) — standalone dialysis and diagnostic-imaging centres typed as `clinic`. **313 of 1,445 contradictions (22%)** are such named dialysis/diagnostic/imaging/PET/scan/lab centres: likely **mis-typed legitimate single-service providers**, not fraud — the flag correctly surfaces a `facilityTypeId` data-quality problem. The other ~78% (e.g. a plain dentist/pharmacy claiming oncology) are higher-suspicion.

### How source diversity & fact-count factor in

- **Source diversity is the deciding lever for STRONG.** Mean distinct `source_types` per claim rises with grade: WEAK/SUSPICIOUS **1.60** (median 1), PARTIAL **2.47** (median 3), STRONG **2.71** (median 3). The rubric enforces this — every STRONG cell has >=2 source types (or unknown provenance); otherwise-strong evidence on a single source is held down to WEAK, so STRONG is never a single-source artifact.
- **Evidence breadth.** `n_evidence_types` runs up to 5 (specialty + equipment + procedure + capability + description all firing); every exemplar above is ev=5. Average `trust_score` across all claims (excluding NO CLAIM) is 2.23.
- **Net effect:** the engine rewards facilities whose claims survive both cross-channel agreement (specialty + equipment/procedure) and cross-source corroboration, and pushes single-source or facility-type-mismatched claims down to PARTIAL/WEAK even when the raw text reads impressively.

### Caveats

- 11 `unique_id`s appear twice in the raw source (22 rows), so those 11 facilities have 14 grading cells; the long-format artifact is faithful to source rows, not deduped on `unique_id`. Group on `cluster_id` (9,959 distinct) for a one-row-per-entity view.
- Contradiction flags on `clinic` are conservative by design; ~22% are mis-typed standalone dialysis/diagnostic centres and should be read as data-quality flags, not fraud signals.
- Grades reflect evidence present in the dataset, not on-the-ground verification; NO CLAIM (68% of cells) is absence of evidence, not absence of capability.
