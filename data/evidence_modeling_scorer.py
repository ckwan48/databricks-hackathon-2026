"""
Evidence-Confidence Modeling for facilities_hack.csv (10,088 rows, national).
Computes a 0-100 evidence-completeness score per facility plus a source-reliability
provenance factor, and writes facility_completeness_scores.csv.

Run:  /tmp/dataenv/bin/python evidence_modeling_scorer.py
"""
import pandas as pd, json, numpy as np

SRC = "/Users/koushik/Downloads/facilities_hack.csv"
OUT = "/Users/koushik/Desktop/health_analysis_outputs/facility_completeness_scores.csv"
TODAY = pd.Timestamp("2026-06-15")

# Source-reliability weights (see report section 1 for rationale)
SRC_WEIGHTS = {
    "mongo_facility": 1.00,
    "constant":       0.85,
    "mongo_ngo":      0.75,
    "overture":       0.70,
    "dynamic":        0.60,
}


def parse_arr(s):
    """Parse a JSON-array string field; 'null'/''/NaN -> []; unparseable -> []."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return []
    ss = str(s).strip()
    if ss in ("", "null", "None", "nan"):
        return []
    try:
        v = json.loads(ss)
        return v if isinstance(v, list) else [v]
    except Exception:
        return []


def ndistinct(lst):
    """Count distinct items, hashing dict/list elements by canonical JSON."""
    out = set()
    for x in lst:
        out.add(json.dumps(x, sort_keys=True) if isinstance(x, (dict, list)) else x)
    return len(out)


def filled(series):
    """Boolean Series: True where the scalar field is meaningfully populated."""
    return ~series.apply(
        lambda v: v is None
        or (isinstance(v, float) and np.isnan(v))
        or str(v).strip() in ("", "null", "None", "nan")
    )


def cap(x, pts, c):
    """Saturating contribution: min(x, c)/c * pts."""
    return np.minimum(x, c) / c * pts


def main():
    df = pd.read_csv(SRC, low_memory=False)

    # ---- parsed evidence counts ----
    st_sets = df["source_types"].apply(parse_arr)
    div = st_sets.apply(ndistinct)                              # distinct source_types
    n_sid = df["source_ids"].apply(parse_arr).apply(ndistinct)
    n_spec = df["specialties"].apply(parse_arr).apply(ndistinct)
    n_proc = df["procedure"].apply(parse_arr).apply(len)
    n_equip = df["equipment"].apply(parse_arr).apply(len)
    n_cap = df["capability"].apply(parse_arr).apply(len)
    nfacts = pd.to_numeric(df["number_of_facts_about_the_organization"],
                           errors="coerce").fillna(0)

    # ---- A. IDENTITY / contact verifiability (max 30) ----
    ident = (
        filled(df["name"]).astype(int) * 5
        + (filled(df["officialPhone"]) | filled(df["phone_numbers"])).astype(int) * 6
        + (filled(df["officialWebsite"]) | filled(df["websites"])).astype(int) * 6
        + filled(df["email"]).astype(int) * 5
        + (filled(df["address_city"]) & filled(df["address_stateOrRegion"])).astype(int) * 4
        + filled(df["address_zipOrPostcode"]).astype(int) * 4
    )

    # ---- B. CLINICAL depth (max 25) ----
    clin = (cap(n_spec, 8, 15) + cap(n_proc, 7, 20)
            + cap(n_equip, 5, 10) + cap(n_cap, 5, 10))

    # ---- C. PROVENANCE / source diversity (max 20) ----
    prov = (div / 5 * 14) + cap(n_sid, 6, 8)

    # ---- D. descriptive FACTS richness (max 10) ----
    facts = cap(nfacts, 10, 15)

    # ---- E. SOCIAL corroboration (max 15) ----
    smc = pd.to_numeric(df["distinct_social_media_presence_count"], errors="coerce").fillna(0)
    foll = pd.to_numeric(df["engagement_metrics_n_followers"], errors="coerce").fillna(0)
    postd = pd.to_datetime(df["post_metrics_most_recent_social_media_post_date"], errors="coerce")
    recent_post = ((TODAY - postd).dt.days <= 730).fillna(False).astype(int)
    social = (cap(smc, 5, 6)
              + np.minimum(np.log10(foll + 1) / np.log10(1e6), 1) * 6
              + recent_post * 4)

    df["completeness"] = (ident + clin + prov + facts + social).clip(0, 100)

    # ---- provenance reliability factor (anchor on best source + diversity bonus) ----
    def prov_factor(types):
        s = set(types)
        if not s:
            return 0.0
        ws = [SRC_WEIGHTS.get(t, 0.4) for t in s]
        return min(max(ws) + 0.05 * (len(s) - 1), 1.0)

    df["provenance_factor"] = st_sets.apply(prov_factor)

    out = df[["unique_id", "name", "address_city", "address_stateOrRegion",
              "cluster_id", "source", "completeness", "provenance_factor"]].copy()
    out["source_diversity"] = div
    out["n_specialties"] = n_spec
    out["n_procedures"] = n_proc
    out["n_facts"] = nfacts
    out.to_csv(OUT, index=False)

    print(f"rows={len(out)}  mean_completeness={df['completeness'].mean():.1f}  "
          f"distinct_clusters={df['cluster_id'].nunique()}  -> {OUT}")


if __name__ == "__main__":
    main()
