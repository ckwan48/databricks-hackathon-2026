#!/usr/bin/env python3
"""
LOCATION + CARE-NEED SEARCH PROTOTYPE
=====================================
A self-contained triage search over the enriched health-facility dataset
(facilities_hack.csv, 10,088 facilities nationwide).

search(location, need, k=10):
  1. Maps free-text `need` -> a target capability + keyword lexicon.
  2. Selects facilities with at least PARTIAL trust-graded evidence for that
     capability (grades: STRONG > PARTIAL ; excludes WEAK/SUSPICIOUS and NO CLAIM).
  3. Ranks by trust grade first (STRONG before PARTIAL), then geographic
     proximity (haversine km from the query city centroid).
  4. Returns an EVIDENCE-ATTACHED shortlist:
     name, city/state, grade, evidence snippets, distance_km, phone, website.

Trust grades come from the capability-trust table built earlier:
  facility_capability_trust.csv  (one row per facility x capability).
If that file is absent, the prototype falls back to scoring evidence directly
from the raw columns (specialties / procedure / equipment / capability / text).

Run:
  /tmp/dataenv/bin/python facility_search.py
"""

import os
import json
import math
import re
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
FACILITIES_CSV = "/Users/koushik/Downloads/facilities_hack.csv"
TRUST_CSV = "/Users/koushik/Desktop/health_analysis_outputs/facility_capability_trust.csv"

# ---------------------------------------------------------------------------
# India bounding box (lat 6-37, lon 68-98). Coords outside this are dropped
# for proximity ranking (some rows have lat/lon swaps or N. Atlantic points).
# ---------------------------------------------------------------------------
IN_LAT = (6.0, 37.0)
IN_LON = (68.0, 98.0)

# ---------------------------------------------------------------------------
# City geocoder. Centroids are the MEDIAN (lat,lon) of facilities in each city
# in this dataset (data-derived, so they line up with the points we rank).
# Jaipur and Patna are explicitly included per the task; the rest are the
# cities that actually carry data.
# ---------------------------------------------------------------------------
CITY_COORDS = {
    "jaipur": (26.8955, 75.7805),
    "patna": (25.6049, 85.1430),
    "agra": (27.1964, 78.0036),
    "ahmedabad": (23.0290, 72.5597),
    "amritsar": (31.6381, 74.8765),
    "bangalore": (12.9701, 77.5899),
    "bengaluru": (12.9675, 77.5951),
    "bhopal": (23.2260, 77.4291),
    "chennai": (13.0477, 80.2206),
    "coimbatore": (11.0221, 76.9731),
    "dehradun": (30.3172, 78.0464),
    "delhi": (28.6382, 77.1919),
    "new delhi": (28.5915, 77.1954),
    "ghaziabad": (28.6493, 77.4299),
    "gurgaon": (28.4573, 77.0427),
    "gurugram": (28.4295, 77.0484),
    "hyderabad": (17.4224, 78.4501),
    "indore": (22.7233, 75.8830),
    "jalandhar": (31.3191, 75.5737),
    "kanpur": (26.4798, 80.3104),
    "kolkata": (22.5378, 88.3674),
    "lucknow": (26.8672, 80.9521),
    "ludhiana": (30.8935, 75.8339),
    "madurai": (9.9235, 78.1276),
    "mumbai": (19.0819, 72.8467),
    "nagpur": (21.1345, 79.0783),
    "nashik": (19.9885, 73.7792),
    "navi mumbai": (19.0432, 73.0177),
    "noida": (28.5705, 77.3689),
    "pune": (18.5523, 73.8477),
    "raipur": (21.2494, 81.6536),
    "rajkot": (22.2887, 70.7914),
    "ranchi": (23.3791, 85.3282),
    "surat": (21.1930, 72.8141),
    "thane": (19.2088, 72.9725),
    "thiruvananthapuram": (8.5106, 76.9405),
    "trivandrum": (8.5106, 76.9405),
    "vadodara": (22.3074, 73.1701),
    "baroda": (22.3074, 73.1701),
    "varanasi": (25.3083, 82.9770),
    "vijayawada": (16.5114, 80.6379),
    "visakhapatnam": (17.7192, 83.3058),
    "vizag": (17.7192, 83.3058),
}
# city-name aliases -> canonical key
CITY_ALIASES = {
    "bengaluru": "bangalore",
    "trivandrum": "thiruvananthapuram",
    "baroda": "vadodara",
    "vizag": "visakhapatnam",
    "gurugram": "gurgaon",
}

# ---------------------------------------------------------------------------
# NEED -> capability mapping. Each need maps to:
#   - "capability": the trust-table capability label (the ranking key)
#   - "keywords": evidence lexicon for snippet highlighting / fallback scoring
# The capability labels match those in facility_capability_trust.csv exactly.
# ---------------------------------------------------------------------------
NEED_MAP = {
    "dialysis": {
        "capability": "dialysis / renal",
        "keywords": ["dialysis", "renal", "haemodialysis", "hemodialysis",
                     "nephrolog", "kidney"],
    },
    "renal": {
        "capability": "dialysis / renal",
        "keywords": ["dialysis", "renal", "haemodialysis", "nephrolog", "kidney"],
    },
    "emergency surgery": {
        "capability": "emergency",
        "keywords": ["emergency surgery", "emergency department", "casualty",
                     "24/7 emergency", "trauma surgery", "emergency",
                     "operation theatre", "surgical emergency"],
    },
    "emergency": {
        "capability": "emergency",
        "keywords": ["emergency department", "casualty", "24/7 emergency",
                     "ambulance", "emergency", "emergencymedicine"],
    },
    "maternity": {
        "capability": "maternity / obstetrics",
        "keywords": ["maternit", "obstetric", "gynaecolog", "gynecolog",
                     "labour ward", "delivery", "antenatal", "ivf", "iui",
                     "icsi"],
    },
    "delivery": {
        "capability": "maternity / obstetrics",
        "keywords": ["delivery", "labour ward", "maternit", "obstetric",
                     "antenatal", "gynaecolog"],
    },
    "obstetrics": {
        "capability": "maternity / obstetrics",
        "keywords": ["obstetric", "maternit", "gynaecolog", "delivery",
                     "labour ward"],
    },
    "nicu": {
        "capability": "NICU / neonatal",
        "keywords": ["nicu", "neonat", "radiant warmer", "neonatal phototherapy",
                     "level iii", "neonatology"],
    },
    "neonatal": {
        "capability": "NICU / neonatal",
        "keywords": ["nicu", "neonat", "radiant warmer", "neonatology"],
    },
    "icu": {
        "capability": "ICU / critical care",
        "keywords": ["icu", "intensive care", "critical care", "ventilator",
                     "multi-para monitor", "central oxygen", "criticalcaremedicine"],
    },
    "critical care": {
        "capability": "ICU / critical care",
        "keywords": ["icu", "intensive care", "critical care", "ventilator"],
    },
    "oncology": {
        "capability": "oncology / cancer",
        "keywords": ["oncolog", "cancer", "chemotherap", "radiotherap",
                     "mammogra", "tumour", "tumor"],
    },
    "cancer": {
        "capability": "oncology / cancer",
        "keywords": ["cancer", "oncolog", "chemotherap", "radiotherap",
                     "tumour", "tumor"],
    },
    "trauma": {
        "capability": "trauma / orthopedic",
        "keywords": ["trauma", "fracture", "polytrauma", "orthopedic surgery",
                     "orthopaedic", "accident", "orthopedicsurgery"],
    },
    "orthopedic": {
        "capability": "trauma / orthopedic",
        "keywords": ["orthopedic", "orthopaedic", "fracture", "trauma",
                     "joint replacement", "spine"],
    },
    # pediatrics & cardiology are not separate trust capabilities, so they
    # use raw-column fallback scoring (handled in search()).
    "pediatrics": {
        "capability": None,
        "keywords": ["pediatric", "paediatric", "child health", "picu",
                     "neonat", "pediatrics"],
    },
    "paediatrics": {
        "capability": None,
        "keywords": ["paediatric", "pediatric", "child health", "picu"],
    },
    "cardiology": {
        "capability": None,
        "keywords": ["cardiolog", "cardiac", "heart", "angioplast",
                     "angiograph", "cath lab", "echocardiograph",
                     "bypass", "cabg"],
    },
}

GRADE_RANK = {"STRONG": 0, "PARTIAL": 1, "WEAK/SUSPICIOUS": 2, "NO CLAIM": 3}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = (math.sin(dphi / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def resolve_need(need_text):
    """Map free-text need to (need_key, spec dict). Longest phrase wins."""
    n = _norm(need_text)
    for key in sorted(NEED_MAP, key=len, reverse=True):
        if key in n:
            return key, NEED_MAP[key]
    return None, None


def geocode(location):
    """Return (lat, lon, canonical_city) for a query location, else (None,None,None)."""
    n = _norm(location)
    n = re.sub(r"^(near|in|at)\s+", "", n)
    for city, coords in CITY_COORDS.items():
        if city in n:
            return coords[0], coords[1], CITY_ALIASES.get(city, city)
    return None, None, None


def _first_phone(row):
    p = row.get("officialPhone")
    if pd.notna(p) and _norm(p) not in ("null", "nan", ""):
        return str(p)
    raw = row.get("phone_numbers")
    if pd.notna(raw) and _norm(raw) not in ("null", "nan", ""):
        try:
            arr = json.loads(raw)
            if arr:
                return arr[0]
        except Exception:
            return str(raw).split(",")[0].strip("[]\" ")
    return ""


def _first_website(row):
    w = row.get("officialWebsite")
    if pd.notna(w) and _norm(w) not in ("null", "nan", ""):
        return str(w)
    raw = row.get("websites")
    if pd.notna(raw) and _norm(raw) not in ("null", "nan", ""):
        try:
            arr = json.loads(raw)
            if arr:
                return arr[0]
        except Exception:
            return str(raw).split(",")[0].strip("[]\" ")
    return ""


def _evidence_from_raw(row, keywords):
    """Build short evidence snippets from raw columns for fallback capabilities
    (pediatrics, cardiology) that have no trust-table row."""
    hits = []
    for col in ("specialties", "capability", "procedure", "equipment", "description"):
        val = row.get(col)
        if pd.isna(val):
            continue
        s = str(val)
        sl = s.lower()
        for kw in keywords:
            if kw in sl:
                snippet = s.replace("\n", " ")
                if len(snippet) > 160:
                    idx = sl.find(kw)
                    start = max(0, idx - 40)
                    snippet = ("..." if start > 0 else "") + snippet[start:start + 160] + "..."
                hits.append(f"{col}~{snippet}")
                break
    return " || ".join(hits[:3])


# ---------------------------------------------------------------------------
# Data loading (cached at module level)
# ---------------------------------------------------------------------------
_FAC = None
_TRUST = None


def _load():
    global _FAC, _TRUST
    if _FAC is None:
        df = pd.read_csv(FACILITIES_CSV, low_memory=False)
        df["lat"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["lon"] = pd.to_numeric(df["longitude"], errors="coerce")
        df["in_india"] = df["lat"].between(*IN_LAT) & df["lon"].between(*IN_LON)
        # dedupe on cluster_id: keep the row with the richest evidence
        ev_cols = ["specialties", "procedure", "equipment", "capability"]
        df["_evrich"] = df[ev_cols].notna().sum(axis=1)
        df = (df.sort_values("_evrich", ascending=False)
                .drop_duplicates(subset=["cluster_id"], keep="first"))
        _FAC = df.set_index("unique_id", drop=False)
    if _TRUST is None and os.path.exists(TRUST_CSV):
        _TRUST = pd.read_csv(TRUST_CSV, low_memory=False)
    return _FAC, _TRUST


# ---------------------------------------------------------------------------
# Main search
# ---------------------------------------------------------------------------
def search(location, need, k=10):
    """Return a dict with the query echo + an evidence-attached shortlist."""
    fac, trust = _load()
    need_key, spec = resolve_need(need)
    qlat, qlon, qcity = geocode(location)

    result = {
        "query": {"location": location, "need": need, "k": k},
        "resolved_need": need_key,
        "capability": (spec or {}).get("capability"),
        "geocoded_city": qcity,
        "geocoded_coords": (qlat, qlon),
        "n_candidates": None,
        "rows": [],
        "notes": [],
    }

    if spec is None:
        result["notes"].append(
            f"Could not map need '{need}' to a known capability. "
            f"Supported: dialysis, emergency/emergency surgery, maternity/delivery, "
            f"NICU, ICU, oncology/cancer, trauma, pediatrics, cardiology.")
        return result
    if qlat is None:
        result["notes"].append(
            f"Could not geocode location '{location}'. Add it to CITY_COORDS. "
            f"Results returned without proximity ranking.")

    keywords = spec["keywords"]
    cap = spec["capability"]

    # ---- Candidate selection -------------------------------------------------
    if cap is not None and trust is not None:
        sub = trust[(trust["capability"] == cap)
                    & (trust["grade"].isin(["STRONG", "PARTIAL"]))].copy()
        sub = sub[sub["unique_id"].isin(fac.index)]
        recs = []
        for _, tr in sub.iterrows():
            row = fac.loc[tr["unique_id"]]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            recs.append((row, tr["grade"], tr["evidence_snippets"]))
    else:
        recs = []
        for _, row in fac.iterrows():
            ev = _evidence_from_raw(row, keywords)
            if ev:
                recs.append((row, "PARTIAL", ev))
        result["notes"].append(
            f"'{need_key}' has no dedicated trust capability; using raw-evidence "
            f"keyword match (grade shown as PARTIAL).")

    if not recs:
        result["notes"].append(
            f"No facilities in the dataset carry at-least-PARTIAL evidence for "
            f"'{cap or need_key}'. This is a coverage limit of the dataset, "
            f"not a statement that no such care exists.")
        return result

    # ---- Ranking: grade first, then proximity --------------------------------
    ranked = []
    for row, grade, ev in recs:
        in_india = bool(row.get("in_india"))
        if qlat is not None and in_india:
            dist = haversine_km(qlat, qlon, float(row["lat"]), float(row["lon"]))
        else:
            dist = float("inf")
        ranked.append({
            "unique_id": row["unique_id"],
            "name": row.get("name"),
            "city": row.get("address_city"),
            "state": row.get("address_stateOrRegion"),
            "facilityType": row.get("facilityTypeId"),
            "grade": grade,
            "grade_rank": GRADE_RANK.get(grade, 9),
            "distance_km": (round(dist, 1) if math.isfinite(dist) else None),
            "phone": _first_phone(row),
            "website": _first_website(row),
            "evidence": ev if isinstance(ev, str) else "",
        })

    ranked.sort(key=lambda r: (r["grade_rank"],
                               r["distance_km"] if r["distance_km"] is not None
                               else float("inf")))

    result["rows"] = ranked[:k]
    result["n_candidates"] = len(ranked)

    if qlat is not None:
        near = [r for r in ranked if r["distance_km"] is not None
                and r["distance_km"] <= 50]
        result["notes"].append(
            f"{len(near)} candidate(s) within 50 km of {qcity}; "
            f"{len(ranked)} total with at-least-PARTIAL evidence nationwide.")
        if not near:
            result["notes"].append(
                f"No graded facility within 50 km of {qcity} for this need in the "
                f"dataset -> a coverage gap near {qcity}, not absence of care. "
                f"Nearest graded options (possibly far) are listed.")
    return result


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------
def print_result(res):
    q = res["query"]
    print("=" * 78)
    print(f"QUERY: {q['need']!r} near {q['location']!r}  (k={q['k']})")
    print(f"  resolved need     : {res['resolved_need']}  ->  capability="
          f"{res['capability']}")
    print(f"  geocoded location : {res['geocoded_city']}  {res['geocoded_coords']}")
    if res.get("n_candidates") is not None:
        print(f"  candidates (>=PARTIAL evidence): {res['n_candidates']}")
    for note in res["notes"]:
        print(f"  NOTE: {note}")
    print("-" * 78)
    if not res["rows"]:
        print("  (no results)")
        return
    for i, r in enumerate(res["rows"], 1):
        dist = f"{r['distance_km']} km" if r["distance_km"] is not None else "dist?"
        print(f"{i:>2}. [{r['grade']:<6}] {r['name']}  "
              f"({r['city']}, {r['state']}) | {dist}")
        if r["phone"]:
            print(f"      phone   : {r['phone']}")
        if r["website"]:
            print(f"      website : {r['website']}")
        if r["evidence"]:
            ev = r["evidence"]
            print(f"      evidence: {ev[:220]}{'...' if len(ev) > 220 else ''}")
    print()


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demos = [
        ("Jaipur", "dialysis", 5),
        ("Patna", "emergency surgery", 5),
        ("Mumbai", "oncology / cancer", 5),
        ("Hyderabad", "NICU", 5),
        ("Chennai", "maternity / delivery", 5),
        ("Pune", "cardiology", 5),
    ]
    for loc, need, k in demos:
        print_result(search(loc, need, k))
