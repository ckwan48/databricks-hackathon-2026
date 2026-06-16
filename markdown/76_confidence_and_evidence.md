## Confidence & Evidence Hardening (so people can trust each answer)

*Every facility capability claim across the FULL national dataset (10,077 facilities × 7 capabilities = 70,616 cells) is graded, hardened against false-positives, and given a transparent 0–100 confidence score with the evidence that earned it.*

### The evidence pyramid (22,645 cells carry a claim; 47,971 are NO CLAIM)
| Tier | Count | Meaning |
|---|---|---|
| **VERIFIED-STRONG** (multi-source) | **10,039** | ≥2 independent evidence types *and* ≥2 distinct sources agree, consistent with facility type |
| **PARTIAL** | **9,143** | one solid structured evidence type |
| **WEAK/SUSPICIOUS** (hospital, weak evidence) | **1,577** | a single vague mention at a hospital; no contradiction |
| **PLAUSIBLE-SPECIALTY-CLINIC** | **1,294** | flagged by the naive rule but legitimate (women's clinic w/ obstetric HDU; paediatric clinic w/ paed-critical-care) |
| **HARD-CONTRADICTION** | **583** | genuine red flags that survived scrutiny |
| STRONG (single-source) | 9 | strong evidence but only one source — down-rated |

### Hardening result (adversarial check)
Of the cells the naive contradiction rule flagged, hardening split them into **1,294 PLAUSIBLE** (rescued — focused specialty clinics legitimately offering sub-specialty care) and **583 HARD-CONTRADICTION** (kept — e.g. dentists/pharmacies/generic clinics claiming oncology, ICU, NICU, dialysis). Source diversity is the deciding lever: only multi-source STRONG cells reach VERIFIED-STRONG (just 9 single-source strong cells exist).

### The confidence score (0–100, auditable)
```
confidence = base(evidence_tier)
           + 5 × (n_independent_evidence_types − 1)   [cap +20]
           + 5 × (n_distinct_sources − 1)             [cap +10]
           − contradiction penalty (caps score at 30)
```
| Level | Score | Badge | Count | Action |
|---|---|---|---|---|
| VERY HIGH | ≥85 | ▰▰▰▰▰ | **4,019** | route here with confidence |
| HIGH | 70–84 | ▰▰▰▰▱ | **6,020** | trust, light verification |
| MODERATE | 50–69 | ▰▰▰▱▱ | 693 | verify before relying |
| LOW | 30–49 | ▰▰▱▱▱ | 9,903 | single/weak evidence; confirm |
| VERY LOW / REJECT | <30 | ▰▱▱▱▱ | 2,010 | do not route; human review |

**≈10,000 capability claims nationwide are High or Very-High confidence** — the trustworthy backbone for routing and planning.

### Showcase (real full-data examples)
```
 ▰▰▰▰▰ 90 VERY HIGH  Fortis Hospital, Gurugram   — oncology   (Gurgaon)
 ▰▰▰▰▰ 85 VERY HIGH  Aravind Eye Hospital        — ICU        (Hyderabad)
 ▰▰▰▰▰ 85 VERY HIGH  Wockhardt Hospital          — emergency  (Nagpur)
 ▰▰▱▱▱ 13 REJECT     S.S. Dental Hospital        — claims oncology (is a clinic/dental)
 ▰▰▱▱▱ 23 REJECT     Park Clinic                 — claims oncology (is a clinic)
```

### How this answers the four planning questions
- **Can this facility do what it claims?** → per-claim confidence badge + evidence snippets.
- **Are the care gaps real?** → region confidence = facility-count + field-fill-rate (real gap vs data-poor).
- **Where should a patient/coordinator go?** → search ranks by confidence first, then distance.
- **What must be fixed first?** → the 583 hard contradictions + sparse fields + the causal "fix-before-modeling" list.

> Artifacts: `facility_capability_trust.csv` (raw grades), `facility_capability_trust_hardened.csv` (+ tier reclassification), `facility_capability_confidence.csv` (+ 0–100 score, level). Reliability note: male-derived NCD indicators in NFHS rest on a small men subsample (median 145/district, min 17) — they carry a lower effective-sample reliability weight.
