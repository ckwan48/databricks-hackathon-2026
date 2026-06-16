#!/usr/bin/env python
"""
GEOGRAPHIC, TRUST-WEIGHTED CAPABILITY GAP ANALYSIS
==================================================
Aggregates the trust-graded long table (facility x capability) up to
  - address_stateOrRegion  (level='state')
  - address_city           (level='city')
and classifies each REGION (across all capabilities, plus per region x capability)
into one of:
  EVIDENCED SUPPLY  - enough facilities AND a real share carry trust-worthy capability evidence
  APPARENT CARE GAP - enough facilities present, fields reasonably filled, but little/no STRONG evidence
  DATA-POOR         - too few facilities OR sparse evidence fields -> cannot conclude

NOTE: input is the FIRST 100 rows of facilities.csv (a national sample), pipeline source='kie'.
There is NO district / pincode-derived column here; with full data we would derive district
from address_zipOrPostcode (pincode) and/or coordinates (reverse-geocode) for sub-state planning.
"""
import pandas as pd
import json

TRUST = "/Users/koushik/Desktop/health_analysis_outputs/facility_capability_trust.csv"
FAC   = "/Users/koushik/Downloads/facilities.csv"
OUT   = "/Users/koushik/Desktop/health_analysis_outputs/region_capability_gaps.csv"

# ---- classification thresholds (explicit & tunable) ----
MIN_FACILITIES   = 3      # need >=3 facilities in a region to even attempt a call
MIN_FILL_RATE    = 0.50   # mean evidence-field fill-rate must be >=50% to trust "absence of evidence"
STRONG_SHARE_GAP = 0.20   # if <20% of facilities carry STRONG/PARTIAL evidence for a capability -> gap

EV_COLS = ["specialties", "procedure", "equipment", "capability", "description"]


def filled(v):
    if pd.isna(v):
        return False
    s = str(v).strip().lower()
    return s not in ("null", "", "[]", "nan")


def fill_rate_for(sub_df):
    """mean fill-rate across the evidence columns for a set of facility rows."""
    if len(sub_df) == 0:
        return 0.0
    rates = [sub_df[c].apply(filled).mean() for c in EV_COLS]
    return float(sum(rates) / len(rates))


def main():
    t = pd.read_csv(TRUST)
    df = pd.read_csv(FAC)

    # fill-rate per facility (so we can aggregate to region)
    df["_fill"] = df.apply(lambda r: fill_rate_for(df.loc[[r.name]]), axis=1)
    fill_by_uid = dict(zip(df["unique_id"], df["_fill"]))
    t["fill_rate_fac"] = t["unique_id"].map(fill_by_uid).fillna(0.0)

    t["is_strong"] = t["grade"] == "STRONG"
    t["is_partial"] = t["grade"] == "PARTIAL"
    t["is_weak"] = t["grade"] == "WEAK/SUSPICIOUS"
    t["is_anyclaim"] = t["grade"].isin(["STRONG", "PARTIAL", "WEAK/SUSPICIOUS"])

    rows = []
    for level, col in [("state", "address_stateOrRegion"), ("city", "address_city")]:
        for region, g in t.groupby(col):
            # facilities present in this region (unique)
            region_uids = g["unique_id"].unique()
            n_fac = len(region_uids)
            region_fill = float(pd.Series([fill_by_uid.get(u, 0.0) for u in region_uids]).mean())

            for cap, gc in g.groupby("capability"):
                n_strong = int(gc["is_strong"].sum())
                n_partial = int(gc["is_partial"].sum())
                n_weak = int(gc["is_weak"].sum())
                # trust-weighted availability: mean trust_score across facilities, normalized to [0,1]
                weighted_score = float(gc["trust_score"].mean() / 3.0)

                # share of facilities with STRONG-or-PARTIAL evidence for this capability
                strong_partial_share = (n_strong + n_partial) / n_fac if n_fac else 0.0

                # ---- classification rule (per region x capability) ----
                if n_fac < MIN_FACILITIES or region_fill < MIN_FILL_RATE:
                    classification = "DATA-POOR"
                elif strong_partial_share < STRONG_SHARE_GAP:
                    classification = "APPARENT CARE GAP"
                else:
                    classification = "EVIDENCED SUPPLY"

                rows.append({
                    "region": region,
                    "level": level,
                    "capability": cap,
                    "n_facilities": n_fac,
                    "n_strong": n_strong,
                    "n_partial": n_partial,
                    "n_weak": n_weak,
                    "strong_partial_share": round(strong_partial_share, 3),
                    "weighted_score": round(weighted_score, 3),
                    "fill_rate": round(region_fill, 3),
                    "classification": classification,
                })

    out = pd.DataFrame(rows)
    # order columns to match deliverable spec (+ extras at end)
    out = out[["region", "level", "capability", "n_facilities", "n_strong", "n_partial",
               "weighted_score", "fill_rate", "classification",
               "n_weak", "strong_partial_share"]]
    out.to_csv(OUT, index=False)
    print("WROTE", OUT, out.shape)

    # ===================== REGION-LEVEL ROLLUP (state) =====================
    st = out[out["level"] == "state"].copy()
    agg = st.groupby("region").agg(
        n_facilities=("n_facilities", "first"),
        fill_rate=("fill_rate", "first"),
        total_strong=("n_strong", "sum"),
        total_partial=("n_partial", "sum"),
        total_weak=("n_weak", "sum"),
        mean_weighted=("weighted_score", "mean"),
    ).reset_index()
    # caps with ANY strong-or-partial in the region (out of 7)
    caps_covered = st[st[["n_strong", "n_partial"]].sum(axis=1) > 0].groupby("region")["capability"].nunique()
    agg["caps_covered_7"] = agg["region"].map(caps_covered).fillna(0).astype(int)
    # region-level classification: data-poor if too few fac or low fill; else gap if 0 caps strong-covered
    caps_strong = st[st["n_strong"] > 0].groupby("region")["capability"].nunique()
    agg["caps_strong_7"] = agg["region"].map(caps_strong).fillna(0).astype(int)

    def region_class(r):
        if r["n_facilities"] < MIN_FACILITIES or r["fill_rate"] < MIN_FILL_RATE:
            return "DATA-POOR"
        if r["caps_covered_7"] == 0:
            return "APPARENT CARE GAP"
        return "EVIDENCED SUPPLY"
    agg["region_classification"] = agg.apply(region_class, axis=1)
    agg = agg.sort_values(["n_facilities", "total_strong"], ascending=False)

    print("\n=== STATE ROLLUP (ranked by n_facilities) ===")
    print(agg.to_string(index=False))

    print("\n=== STATE-LEVEL classification counts ===")
    print(agg["region_classification"].value_counts().to_dict())

    print("\n=== per region x capability classification counts (state level) ===")
    print(st["classification"].value_counts().to_dict())

    # save the rollup too for the report
    agg.to_csv("/Users/koushik/Desktop/health_analysis_outputs/region_state_rollup.csv", index=False)
    print("\nWROTE state rollup")

    # capability-level national gap view (state-level cells only)
    print("\n=== national: per-capability, n states EVIDENCED vs GAP vs DATA-POOR (state cells) ===")
    capnat = st.groupby(["capability", "classification"]).size().unstack(fill_value=0)
    print(capnat.to_string())


if __name__ == "__main__":
    main()
