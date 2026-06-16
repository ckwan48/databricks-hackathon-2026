#!/usr/bin/env python
"""
Capability Trust-Grading Engine
================================
For EVERY facility x EVERY target clinical capability, gather evidence across:
  - specialties (structured 164-code taxonomy)
  - equipment   (free-text array)
  - procedure   (free-text array)
  - capability  (free-text array)
  - description (free text)
...then assign ONE deterministic trust grade per (facility, capability).

Grades:
  STRONG  = >=2 INDEPENDENT structured evidence types agree (e.g. specialty code AND
            equipment/procedure), OR a specialty code + a clear capability statement;
            AND consistent with facilityTypeId;
            AND backed by >=2 distinct source_types where available.
  PARTIAL = exactly one structured evidence type (specialty-only OR equipment-only OR
            procedure-only), OR a capability/description mention corroborated by a
            related specialty.
  WEAK/SUSPICIOUS = only a single vague text mention, OR an internal contradiction
            (capability inconsistent with facilityTypeId, e.g. dentist/clinic claiming
            ICU/oncology/NICU), OR a would-be-strong claim backed by a single
            low-diversity source.
  NO CLAIM= no evidence found.

Numeric trust_score: strong=3, partial=2, weak=1, none=0; contradiction subtracts 2 (floored at 0).
Evidence snippets captured so every grade is auditable.

Input: FULL national enriched dataset facilities_hack.csv (10,088 facilities; pipeline source='kie').
"""
import pandas as pd
import json
import ast
import re
from collections import Counter

INFILE = "/Users/koushik/Downloads/facilities_hack.csv"
OUTCSV = "/Users/koushik/Desktop/health_analysis_outputs/facility_capability_trust.csv"
DISTCSV = "/Users/koushik/Desktop/health_analysis_outputs/capability_grade_distribution.csv"

# Only these source_types are legitimate evidence-provenance tokens; the source_types
# array is sometimes polluted with free-text fragments, which we ignore for diversity.
LEGIT_SOURCE_TYPES = {"overture", "dynamic", "constant", "mongo_facility", "mongo_ngo"}

# ----------------------------------------------------------------------------
# Capability lexicon. Each capability has:
#   specialties     : structured specialty codes (case-insensitive exact) = STRUCTURED match
#   text            : regex patterns for free-text fields (equipment/procedure/capability/description)
#   related         : "soft" specialty codes that corroborate a text mention (-> PARTIAL)
#   incompatible_ft : facilityTypeId values for which this claim is an internal contradiction
# ----------------------------------------------------------------------------
CAPABILITIES = {
    "ICU / critical care": {
        "specialties": {"criticalcaremedicine"},
        "text": [r"\bicu\b", r"intensive care", r"critical care", r"ventilator",
                 r"multi[- ]?para monitor", r"central oxygen", r"mechanical ventilation",
                 r"cardiac monitor"],
        "related": {"anesthesiology", "pulmonology", "internalmedicine", "cardiology",
                    "cardiothoracicsurgery"},
        "incompatible_ft": {"dentist", "farmacy", "clinic", "doctor"},
    },
    "NICU / neonatal": {
        "specialties": {"neonatologyperinatalmedicine"},
        "text": [r"\bnicu\b", r"neonat", r"radiant warmer", r"neonatal phototherapy",
                 r"level\s*iii", r"sick newborn", r"newborn intensive"],
        "related": {"pediatrics", "pediatricsurgery", "gynecologyandobstetrics"},
        "incompatible_ft": {"dentist", "farmacy", "doctor"},
    },
    "maternity / obstetrics": {
        "specialties": {"gynecologyandobstetrics", "reproductiveendocrinologyandinfertility"},
        # bare "delivery" excluded -> false-positives on "instrument delivery system"
        # (dental) and "report/medicine delivery"; require obstetric context.
        "text": [r"maternit", r"obstetric", r"gyn[ae]?ecolog", r"labour ward", r"labor ward",
                 r"painless delivery", r"normal delivery", r"delivery and cesarean",
                 r"delivery are provided", r"cesarean", r"caesarean", r"c-section",
                 r"antenatal", r"high risk pregnancy", r"birthing",
                 r"\bivf\b", r"\biui\b", r"\bicsi\b"],
        "related": {"pediatrics", "neonatologyperinatalmedicine"},
        "incompatible_ft": {"dentist", "farmacy", "doctor"},
    },
    "emergency": {
        "specialties": {"emergencymedicine"},
        "text": [r"emergency department", r"casualty", r"24/7 emergency", r"24x7 emergency",
                 r"24 hour emergency", r"\bambulance\b", r"emergency care",
                 r"accident and emergency", r"emergency room", r"\ba&e\b"],
        "related": {"criticalcaremedicine", "traumasurgery", "internalmedicine"},
        "incompatible_ft": {"dentist", "farmacy", "doctor"},
    },
    "oncology / cancer": {
        "specialties": {"medicaloncology", "surgicaloncology", "radiationoncology", "breastimaging"},
        "text": [r"oncolog", r"\bcancer\b", r"chemotherap", r"radiotherap", r"mammogra",
                 r"tumour", r"tumor", r"pet[- ]?ct", r"linear accelerator", r"\blinac\b",
                 r"brachytherapy", r"cyberknife"],
        "related": {"hematology", "radiology", "generalsurgery", "nuclearmedicine", "pathology"},
        "incompatible_ft": {"dentist", "farmacy", "doctor"},
    },
    "trauma / orthopedic": {
        "specialties": {"orthopedicsurgery", "traumasurgery", "spineneurosurgery",
                        "shoulderandelboworthopedicsurgery", "pediatricorthopedicsurgery",
                        "handorupperextremityandperipheralnervesurgery"},
        "text": [r"\btrauma\b", r"fracture", r"polytrauma", r"orthop[ae]?edic", r"\baccident\b",
                 r"joint replacement", r"knee replacement", r"hip replacement", r"spine surgery",
                 r"arthroscopy", r"fixation"],
        "related": {"physicalmedicineandrehabilitation", "neurosurgery", "sportsmedicine",
                    "emergencymedicine"},
        "incompatible_ft": {"dentist", "farmacy", "doctor"},
    },
    "dialysis / renal": {
        "specialties": {"nephrology"},
        "text": [r"dialysis", r"\brenal\b", r"ha?emodialysis", r"kidney failure",
                 r"renal replacement", r"peritoneal dialysis", r"renal transplant"],
        "related": {"urology", "internalmedicine", "transplantsurgery"},
        "incompatible_ft": {"dentist", "farmacy", "doctor"},
    },
}

GRADE_SCORE = {"STRONG": 3, "PARTIAL": 2, "WEAK/SUSPICIOUS": 1, "NO CLAIM": 0}


def parse_list(v):
    """Robustly parse a JSON-array-string into a list of stripped strings."""
    if v is None or (isinstance(v, float)):
        return []
    s = str(v).strip()
    if s == "" or s.lower() == "null":
        return []
    out = None
    try:
        x = json.loads(s)
        out = x if isinstance(x, list) else [x]
    except Exception:
        try:
            x = ast.literal_eval(s)
            out = x if isinstance(x, list) else [s]
        except Exception:
            out = [s]
    return [str(i).strip() for i in out if str(i).strip() != ""]


def norm_spec(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def text_hits(patterns, items):
    """Return list of source_strings that match any pattern (one record per string)."""
    hits = []
    for it in items:
        low = str(it).lower()
        for p in patterns:
            if re.search(p, low):
                hits.append(str(it))
                break
    return hits


def main():
    df = pd.read_csv(INFILE, dtype=str, low_memory=False)
    n = len(df)
    rows = []

    for _, r in df.iterrows():
        specs = {norm_spec(x) for x in parse_list(r["specialties"])}
        equip = parse_list(r["equipment"])
        proc = parse_list(r["procedure"])
        capab = parse_list(r["capability"])
        d = r["description"]
        desc = [str(d)] if (d is not None and not (isinstance(d, float)) and str(d).strip().lower() not in ("", "null")) else []
        ftype = str(r["facilityTypeId"]).lower().strip() if (r["facilityTypeId"] is not None and str(r["facilityTypeId"]).lower() != "null") else None
        src_types = {t.lower() for t in parse_list(r["source_types"]) if t.lower() in LEGIT_SOURCE_TYPES}
        n_src = len(src_types)

        for cap, lex in CAPABILITIES.items():
            ev_types = []
            snippets = []

            # 1) STRUCTURED: specialty code
            spec_match = specs & lex["specialties"]
            if spec_match:
                ev_types.append("specialty")
                snippets.append("specialty=" + ",".join(sorted(spec_match)))

            # 2) STRUCTURED: equipment text
            eq_hits = text_hits(lex["text"], equip)
            if eq_hits:
                ev_types.append("equipment")
                snippets.append("equipment~" + " | ".join(h[:80] for h in eq_hits[:2]))

            # 3) STRUCTURED-ish: procedure text
            pr_hits = text_hits(lex["text"], proc)
            if pr_hits:
                ev_types.append("procedure")
                snippets.append("procedure~" + " | ".join(h[:80] for h in pr_hits[:2]))

            # 4) FREE-TEXT: capability statements
            cap_hits = text_hits(lex["text"], capab)
            if cap_hits:
                ev_types.append("capability")
                snippets.append("capability~" + " | ".join(h[:80] for h in cap_hits[:2]))

            # 5) FREE-TEXT: description
            de_hits = text_hits(lex["text"], desc)
            if de_hits:
                ev_types.append("description")
                snippets.append("description~" + de_hits[0][:120])

            # related/corroborating specialty (soft signal)
            related_match = specs & lex["related"]

            n_ev = len(ev_types)
            has_spec = "specialty" in ev_types
            has_capability = "capability" in ev_types
            has_freetext = has_capability or ("description" in ev_types)
            structured_types = sum(1 for t in ev_types if t in ("specialty", "equipment", "procedure"))

            # contradiction: claim inconsistent with facilityTypeId
            contradiction = False
            if n_ev > 0 and ftype:
                heavy = cap in ("ICU / critical care", "NICU / neonatal",
                                "oncology / cancer", "dialysis / renal")
                if ftype in ("dentist", "farmacy"):
                    contradiction = True   # dental/pharmacy can't legitimately offer any of these
                elif ftype == "clinic":
                    contradiction = heavy  # a "clinic" claiming ICU/NICU/oncology/dialysis is suspect
                elif ftype == "doctor":
                    contradiction = True   # an individual practitioner claiming institutional capability

            # ----------------------------------------------------------------
            # GRADE assignment
            # ----------------------------------------------------------------
            if n_ev == 0:
                grade = "NO CLAIM"
            elif contradiction:
                grade = "WEAK/SUSPICIOUS"
            else:
                two_independent_structured = structured_types >= 2
                spec_plus_capability = has_spec and has_capability
                if two_independent_structured or spec_plus_capability:
                    if n_src >= 2 or n_src == 0:   # n_src==0 = unknown -> don't penalize
                        grade = "STRONG"
                    else:
                        grade = "WEAK/SUSPICIOUS"   # would-be strong but single low-diversity source
                elif structured_types == 1:
                    grade = "PARTIAL"               # exactly one structured type (with or w/o free text)
                elif structured_types == 0 and has_freetext and related_match:
                    grade = "PARTIAL"               # free-text corroborated by a related specialty
                else:
                    grade = "WEAK/SUSPICIOUS"        # only single vague text mention, no structure/relation

            score = GRADE_SCORE[grade]
            if contradiction:
                score = max(0, score - 2)

            if related_match and grade in ("PARTIAL", "WEAK/SUSPICIOUS"):
                snippets.append("related_specialty=" + ",".join(sorted(related_match)))
            if contradiction:
                snippets.append(f"CONTRADICTION: facilityTypeId={ftype} claims {cap}")

            rows.append({
                "unique_id": r["unique_id"],
                "name": r["name"],
                "address_city": r["address_city"],
                "address_stateOrRegion": r["address_stateOrRegion"],
                "facilityTypeId": ftype,
                "capability": cap,
                "grade": grade,
                "trust_score": score,
                "n_evidence_types": n_ev,
                "n_distinct_source_types": n_src,
                "evidence_snippets": " || ".join(snippets) if snippets else "",
                "contradiction_flag": bool(contradiction),
            })

    out = pd.DataFrame(rows)
    out.to_csv(OUTCSV, index=False)
    print("WROTE", OUTCSV, out.shape, "| facilities:", n)

    # ---- distributions ----
    print("\n=== GRADE DISTRIBUTION PER CAPABILITY ===")
    piv = out.pivot_table(index="capability", columns="grade", values="unique_id",
                          aggfunc="count", fill_value=0)
    for g in ["STRONG", "PARTIAL", "WEAK/SUSPICIOUS", "NO CLAIM"]:
        if g not in piv.columns:
            piv[g] = 0
    piv = piv[["STRONG", "PARTIAL", "WEAK/SUSPICIOUS", "NO CLAIM"]]
    piv["with_claim"] = piv["STRONG"] + piv["PARTIAL"] + piv["WEAK/SUSPICIOUS"]
    print(piv.to_string())
    piv.to_csv(DISTCSV)

    print("\n=== OVERALL GRADE COUNTS ===")
    print(out["grade"].value_counts().to_dict())

    print("\n=== CONTRADICTIONS ===")
    contra = out[out["contradiction_flag"]]
    print("total contradiction cells:", len(contra))
    print(contra.groupby("capability").size().to_string())
    print("\nby facilityTypeId:")
    print(contra.groupby("facilityTypeId").size().sort_values(ascending=False).to_string())

    print("\n=== SOURCE DIVERSITY by grade (claims only) ===")
    print(out[out["grade"] != "NO CLAIM"].groupby("grade")["n_distinct_source_types"]
          .agg(["mean", "median", "count"]).to_string())

    print("\n=== EXEMPLAR STRONG (top by evidence breadth then source diversity) ===")
    strong = out[out["grade"] == "STRONG"]
    for cap in CAPABILITIES:
        sub = strong[strong["capability"] == cap].sort_values(
            ["n_evidence_types", "n_distinct_source_types"], ascending=False).head(2)
        for _, rr in sub.iterrows():
            print(f"[{cap}] {rr['name']} ({rr['address_city']}, {rr['address_stateOrRegion']}) "
                  f"ev={rr['n_evidence_types']} src={rr['n_distinct_source_types']} :: {rr['evidence_snippets'][:200]}")

    print("\n=== EXEMPLAR SUSPICIOUS (contradictions, most evidence) ===")
    for _, rr in contra.sort_values("n_evidence_types", ascending=False).head(12).iterrows():
        print(f"[{rr['capability']}] {rr['name']} type={rr['facilityTypeId']} "
              f"({rr['address_city']}, {rr['address_stateOrRegion']}) :: {rr['evidence_snippets'][:180]}")


if __name__ == "__main__":
    main()
