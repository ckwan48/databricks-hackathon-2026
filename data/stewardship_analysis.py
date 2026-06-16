#!/usr/bin/env python
"""Data-quality stewardship & human-review queue for facilities_hack.csv.
Surfaces contradictions, sparse fields, taxonomy issues, and a ranked review queue.
"""
import json
import re
import math
import pandas as pd
import numpy as np

CSV = '/Users/koushik/Downloads/facilities_hack.csv'
TRUST = '/Users/koushik/Desktop/health_analysis_outputs/facility_capability_trust.csv'
OUT_QUEUE = '/Users/koushik/Desktop/health_analysis_outputs/review_queue.csv'

df = pd.read_csv(CSV, low_memory=False)
N = len(df)

# ---------- helpers ----------
VALID_FT = {'hospital', 'clinic', 'dentist', 'doctor', 'farmacy', 'pharmacy', 'nursing_home'}
VALID_CC = {'IN'}


def is_missing(v):
    if pd.isna(v):
        return True
    s = str(v).strip().lower()
    return s in ('', 'null', 'nan', 'none')


def parse_json_array(v):
    """Parse a JSON-array string; return list of strings. Robust to malformed."""
    if is_missing(v):
        return []
    s = str(v)
    try:
        out = json.loads(s)
        if isinstance(out, list):
            return [str(x) for x in out if x is not None and str(x).strip().lower() != 'null']
        return [str(out)]
    except Exception:
        # fallback: strip brackets/quotes split on comma
        s2 = s.strip().strip('[]')
        parts = [p.strip().strip('"').strip("'") for p in s2.split(',')]
        return [p for p in parts if p and p.lower() != 'null']


def num(series):
    return pd.to_numeric(series, errors='coerce')


# ---------- 0. column-shift / parse corruption ----------
ft_str = df['facilityTypeId'].astype(str)
# A row is "structurally corrupt" if facilityTypeId is not a valid token AND not missing
ft_valid = ft_str.isin(VALID_FT)
ft_missing = df['facilityTypeId'].apply(is_missing)
corrupt_mask = ~ft_valid & ~ft_missing
n_corrupt = int(corrupt_mask.sum())

# ---------- 1. FILL-RATE TABLE ----------
fill_rows = []
for col in df.columns:
    nonmiss = (~df[col].apply(is_missing)).sum()
    fill_rows.append((col, nonmiss, round(100.0 * nonmiss / N, 1)))
fill_df = pd.DataFrame(fill_rows, columns=['column', 'filled', 'fill_pct']).sort_values('fill_pct')
fill_df.to_csv('/Users/koushik/Desktop/health_analysis_outputs/fill_rate.csv', index=False)

# core identity / location / contact fields
core_fields = {
    'name': 'identity', 'unique_id': 'identity',
    'address_city': 'location', 'address_stateOrRegion': 'location',
    'address_zipOrPostcode': 'location', 'latitude': 'location', 'longitude': 'location',
    'phone_numbers': 'contact', 'officialPhone': 'contact', 'email': 'contact',
    'websites': 'contact', 'officialWebsite': 'contact',
    'facilityTypeId': 'classification', 'operatorTypeId': 'classification',
}

# ---------- 2. COORDINATE / GEO contradictions ----------
lat = num(df['latitude'])
lon = num(df['longitude'])
# India bbox
in_bbox = (lat.between(6, 37)) & (lon.between(68, 98))
has_coord = lat.notna() & lon.notna()
out_of_india = has_coord & ~in_bbox
n_out_of_india = int(out_of_india.sum())

# lat/lon swap heuristic: swapping puts it inside India but original is outside
swap_in = (lon.between(6, 37)) & (lat.between(68, 98))
n_swap = int((has_coord & swap_in).sum())

# ---------- 3. country mismatch ----------
cc = df['address_countryCode'].astype(str)
country = df['address_country'].astype(str)
cc_bad = (~df['address_countryCode'].apply(is_missing)) & (~cc.str.upper().isin({'IN'}))
# only count plausible (not corrupt rows already counted)
cc_mismatch = cc_bad & ~corrupt_mask
n_cc_mismatch = int(cc_mismatch.sum())

# ---------- 4. yearEstablished implausible ----------
yr = num(df['yearEstablished'])
CURRENT_YEAR = 2026
yr_bad = yr.notna() & ((yr < 1800) | (yr > CURRENT_YEAR))
n_yr_bad = int(yr_bad.sum())

# ---------- 5. capacity vs numberDoctors ----------
cap = num(df['capacity'])
ndoc = num(df['numberDoctors'])
cap_no_doc = (cap > 0) & (ndoc.isna() | (ndoc == 0))
doc_no_cap = (ndoc > 0) & (cap.isna() | (cap == 0))
n_cap_no_doc = int(cap_no_doc.sum())
n_doc_no_cap = int(doc_no_cap.sum())

# ---------- 6. SPECIALTY parsing + TAXONOMY ----------
spec_lists = df['specialties'].apply(parse_json_array)
# normalize for dup/overlap detection: lowercase
spec_norm = spec_lists.apply(lambda L: [x.lower() for x in L])
n_spec_unique = spec_norm.apply(lambda L: len(set(L)))
n_spec_raw = spec_norm.apply(len)
# within-row duplicates
within_dup = (n_spec_raw - n_spec_unique)
n_rows_within_dup = int((within_dup > 0).sum())
total_within_dup = int(within_dup.sum())

# overlapping/duplicate code pairs across the taxonomy (synonyms)
SYNONYM_PAIRS = [
    ('ent', 'otolaryngology'),
    ('generalmedicine', 'internalmedicine'),
    ('dental', 'dentistry'),
    ('obstetrics', 'gynecologyandobstetrics'),
    ('gynecology', 'gynecologyandobstetrics'),
    ('paediatrics', 'pediatrics'),
    ('orthopedics', 'orthopedicsurgery'),
    ('anesthesia', 'anesthesiology'),
    ('cardiac', 'cardiology'),
    ('neuro', 'neurology'),
]
# tally how many rows contain each side of a synonym pair (co-occurrence)
syn_cooccur = {}
all_codes = []
for L in spec_norm:
    all_codes.extend(set(L))
code_counts = pd.Series(all_codes).value_counts()
for a, b in SYNONYM_PAIRS:
    co = spec_norm.apply(lambda L: (a in L) and (b in L)).sum()
    syn_cooccur[f'{a} & {b}'] = (int(code_counts.get(a, 0)), int(code_counts.get(b, 0)), int(co))

# ---------- 7. CAPABILITY/SPECIALTY vs facilityTypeId contradictions ----------
# Build text blob of capability + procedure + equipment + specialties per row
cap_lists = df['capability'].apply(parse_json_array)
proc_lists = df['procedure'].apply(parse_json_array)
equip_lists = df['equipment'].apply(parse_json_array)


def blob(i):
    return ' || '.join(cap_lists[i] + proc_lists[i] + equip_lists[i] + spec_lists[i]).lower()


# high-acuity signals that should NOT appear at a dentist / pharmacy / (mostly) clinic
HIGH_ACUITY = {
    'icu': r'\bicu\b|intensive care|critical care',
    'nicu': r'\bnicu\b|neonatal intensive|neonatology',
    'oncology': r'oncolog|chemotherap|radiotherap|cancer institute|bone marrow transplant|car-t',
    'cardiac_surgery': r'cardiac surger|cardiothoracic|cath lab|bypass|angioplasty|open heart',
    'neurosurgery': r'neurosurg|craniotomy|aneurysm clip',
    'transplant': r'organ transplant|kidney transplant|liver transplant|stem cell transplant',
    'maternity': r'maternity|obstetric|labour room|delivery',
}

contradiction_records = []  # for example surfacing
geo_examples = []

# precompute swap detail per row for issues
for i in range(N):
    issues = []
    ft = ft_str.iloc[i]
    ft_clean = ft if ft in VALID_FT else None

    # structural corruption
    if corrupt_mask.iloc[i]:
        issues.append('structural_csv_corruption(column_shift)')

    # geo
    if out_of_india.iloc[i]:
        if swap_in.iloc[i]:
            issues.append(f'coords_outside_india_likely_latlon_swap(lat={lat.iloc[i]:.2f},lon={lon.iloc[i]:.2f})')
        else:
            issues.append(f'coords_outside_india(lat={lat.iloc[i]:.2f},lon={lon.iloc[i]:.2f})')
    if has_coord.iloc[i] and is_missing(df['latitude'].iloc[i]):
        pass

    # country
    if cc_mismatch.iloc[i]:
        issues.append(f'country_code_not_IN({cc.iloc[i]})')

    # year
    if yr_bad.iloc[i]:
        issues.append(f'yearEstablished_implausible({yr.iloc[i]:.0f})')

    # capacity/doctors
    if cap_no_doc.iloc[i]:
        issues.append(f'capacity_present_but_no_doctors(cap={cap.iloc[i]:.0f})')
    if doc_no_cap.iloc[i]:
        issues.append(f'doctors_present_but_no_capacity(doc={ndoc.iloc[i]:.0f})')

    # specialty count contradiction for clinic/dentist/doctor/pharmacy
    nsu = int(n_spec_unique.iloc[i])
    if ft_clean in ('clinic', 'dentist', 'doctor', 'farmacy', 'pharmacy') and nsu >= 30:
        issues.append(f'{ft_clean}_claims_{nsu}_specialties')

    # within-row dup specialties
    if within_dup.iloc[i] > 0:
        issues.append(f'duplicate_specialty_entries(x{int(within_dup.iloc[i])})')

    # high-acuity capability vs low-acuity type
    if ft_clean in ('dentist', 'farmacy', 'pharmacy', 'clinic', 'doctor'):
        b = blob(i)
        hits = [k for k, pat in HIGH_ACUITY.items() if re.search(pat, b)]
        # dentist with internalMedicine-heavy
        if ft_clean == 'dentist':
            im = sum(1 for c in spec_norm.iloc[i] if c in ('internalmedicine', 'generalmedicine'))
            if im >= 3:
                issues.append(f'dentist_with_internalMedicine_heavy(x{im})')
        # for dentist/pharmacy any high-acuity is a contradiction; for clinic only the most severe
        if ft_clean in ('dentist', 'farmacy', 'pharmacy'):
            sev = [h for h in hits if h in ('icu', 'nicu', 'oncology', 'cardiac_surgery', 'neurosurgery', 'transplant')]
            if sev:
                issues.append(f'{ft_clean}_claims_high_acuity({",".join(sev)})')
        elif ft_clean in ('clinic', 'doctor'):
            sev = [h for h in hits if h in ('icu', 'nicu', 'oncology', 'cardiac_surgery', 'neurosurgery', 'transplant')]
            if sev:
                issues.append(f'{ft_clean}_claims_high_acuity({",".join(sev)})')

    # missing core identity/location
    missing_core = []
    if is_missing(df['name'].iloc[i]):
        missing_core.append('name')
    if is_missing(df['address_city'].iloc[i]):
        missing_core.append('city')
    if is_missing(df['latitude'].iloc[i]) or is_missing(df['longitude'].iloc[i]):
        missing_core.append('coords')
    if (is_missing(df['phone_numbers'].iloc[i]) and is_missing(df['officialPhone'].iloc[i])
            and is_missing(df['email'].iloc[i])
            and is_missing(df['websites'].iloc[i]) and is_missing(df['officialWebsite'].iloc[i])):
        missing_core.append('all_contact')
    if missing_core:
        issues.append('missing:' + '+'.join(missing_core))

    contradiction_records.append(issues)

issues_series = pd.Series(contradiction_records, index=df.index)
n_issues = issues_series.apply(len)
has_contradiction = issues_series.apply(lambda L: any(not x.startswith('missing:') and not x.startswith('duplicate_specialty') for x in L))

# ---------- 8. REVIEW PRIORITY SCORE ----------
# popularity / engagement
foll = num(df['engagement_metrics_n_followers']).fillna(0).clip(lower=0)
posts = num(df['post_metrics_post_count']).fillna(0).clip(lower=0)
likes = num(df['engagement_metrics_n_likes']).fillna(0).clip(lower=0)
facts = num(df['number_of_facts_about_the_organization']).fillna(0).clip(lower=0)
smp = num(df['distinct_social_media_presence_count']).fillna(0).clip(lower=0)

# log-scale popularity components -> 0..1
def lognorm(s):
    x = np.log1p(s)
    if x.max() == 0:
        return x
    return x / x.max()

pop = (lognorm(foll) * 0.4 + lognorm(posts) * 0.2 + lognorm(likes) * 0.2
       + lognorm(facts) * 0.1 + lognorm(smp) * 0.1)

# severity weights per issue keyword
def severity(issues):
    w = 0.0
    for it in issues:
        if 'structural_csv_corruption' in it:
            w += 5
        elif 'coords_outside_india' in it:
            w += 4
        elif 'claims_high_acuity' in it:
            w += 4
        elif 'claims_' in it and 'specialties' in it:
            w += 3
        elif 'internalMedicine_heavy' in it:
            w += 3
        elif 'country_code_not_IN' in it:
            w += 2
        elif 'yearEstablished_implausible' in it:
            w += 2
        elif 'capacity_present_but_no_doctors' in it or 'doctors_present_but_no_capacity' in it:
            w += 1.5
        elif it.startswith('missing:'):
            w += 1 + 0.5 * it.count('+')
        elif 'duplicate_specialty' in it:
            w += 0.5
    return w


sev = issues_series.apply(severity)
sev_norm = sev / max(sev.max(), 1)

# priority: weight risk heavily, amplified by popularity (popular AND broken = top)
priority = (0.6 * sev_norm + 0.4 * pop) * (1 + sev_norm)  # multiplicative amplification of risk
priority = (priority / priority.max() * 100).round(2)

df['_priority'] = priority
df['_issues'] = issues_series
df['_n_issues'] = n_issues
df['_sev'] = sev


def suggest(issues):
    j = ' '.join(issues)
    if 'structural_csv_corruption' in j:
        return 'Re-ingest source row; CSV column-shift corrupted record'
    if 'coords_outside_india' in j and 'swap' in j:
        return 'Swap lat/lon; verify against city/state'
    if 'coords_outside_india' in j:
        return 'Re-geocode from address; coordinates invalid'
    if 'claims_high_acuity' in j or ('claims_' in j and 'specialties' in j):
        return 'Reclassify facilityTypeId or downgrade capability claims; verify'
    if 'internalMedicine_heavy' in j:
        return 'Verify facility type; specialty taxonomy mismatch'
    if 'country_code_not_IN' in j:
        return 'Correct country/countryCode'
    if 'yearEstablished_implausible' in j:
        return 'Correct yearEstablished'
    if 'capacity_present_but_no_doctors' in j or 'doctors_present_but_no_capacity' in j:
        return 'Backfill missing capacity/numberDoctors'
    if 'duplicate_specialty' in j:
        return 'Dedupe & normalize specialty codes'
    if j.startswith('missing') or 'missing:' in j:
        return 'Enrich missing identity/location/contact fields'
    return 'Review'


# ---------- WRITE REVIEW QUEUE (only rows with issues) ----------
qmask = n_issues > 0
q = df[qmask].copy()
q = q.sort_values('_priority', ascending=False)
queue = pd.DataFrame({
    'unique_id': q['unique_id'].astype(str).str.slice(0, 80),
    'name': q['name'].astype(str).str.slice(0, 120),
    'city': q['address_city'].astype(str).str.slice(0, 60),
    'state': q['address_stateOrRegion'].astype(str).str.slice(0, 60),
    'priority_score': q['_priority'],
    'issues': q['_issues'].apply(lambda L: '; '.join(L)),
    'suggested_action': q['_issues'].apply(suggest),
})
queue.to_csv(OUT_QUEUE, index=False)

# ---------- SUMMARY PRINT ----------
print('=== SUMMARY ===')
print('N facilities:', N)
print('distinct unique_id:', df['unique_id'].nunique(), 'distinct cluster_id:', df['cluster_id'].nunique())
print('structural CSV corruption rows:', n_corrupt)
print('coords outside India:', n_out_of_india, '(of which likely lat/lon swap:', n_swap, ')')
print('country_code != IN (non-corrupt):', n_cc_mismatch)
print('yearEstablished implausible:', n_yr_bad)
print('capacity>0 but no doctors:', n_cap_no_doc)
print('doctors>0 but no capacity:', n_doc_no_cap)
print('rows w/ within-row duplicate specialties:', n_rows_within_dup, 'total dup entries:', total_within_dup)
print('rows with >=1 issue (in queue):', int(qmask.sum()))
print('rows with a contradiction (not just sparsity):', int(has_contradiction.sum()))
print()
print('=== Synonym co-occurrence (codeA count, codeB count, rows with both) ===')
for k, v in syn_cooccur.items():
    print(f'  {k}: A={v[0]} B={v[1]} both={v[2]}')
print()
print('=== Top 20 specialty codes by row-frequency ===')
print(code_counts.head(20).to_string())
print()
print('=== Sparsest 15 columns ===')
print(fill_df.head(15).to_string(index=False))

# Save artifacts for the markdown writer
fill_df.to_csv('/Users/koushik/Desktop/health_analysis_outputs/fill_rate.csv', index=False)

# Specialty count by facility type for contradiction section
ft_for_rows = ft_str.where(ft_valid, other=np.nan)
spec_by_ft = pd.DataFrame({'ft': ft_for_rows, 'nspec': n_spec_unique})
print()
print('=== max distinct specialties by facility type ===')
print(spec_by_ft.groupby('ft')['nspec'].agg(['count', 'mean', 'max']).round(1).to_string())

# Example contradiction rows for clinic/dentist with high acuity
print()
print('=== EXAMPLE: dentist/clinic claiming high-acuity (top 8 by priority) ===')
ex = q[q['_issues'].apply(lambda L: any('claims_high_acuity' in x or ('claims_' in x and 'specialties' in x) or 'internalMedicine_heavy' in x for x in L))]
for _, r in ex.head(8).iterrows():
    print(f"  [{r['_priority']:.1f}] {str(r['name'])[:50]:50s} ft={ft_str.loc[r.name][:10]:10s} {str(r['address_city'])[:18]:18s} :: {'; '.join(r['_issues'])[:160]}")

print()
print('=== EXAMPLE: coords outside India (top 8) ===')
ex2 = q[q['_issues'].apply(lambda L: any('coords_outside_india' in x for x in L))]
for _, r in ex2.head(8).iterrows():
    print(f"  [{r['_priority']:.1f}] {str(r['name'])[:45]:45s} {str(r['address_city'])[:16]:16s}/{str(r['address_stateOrRegion'])[:14]:14s} :: {'; '.join([x for x in r['_issues'] if 'coords' in x])}")

print()
print('=== TOP 15 REVIEW QUEUE ===')
for _, r in queue.head(15).iterrows():
    print(f"  [{r['priority_score']:.1f}] {r['name'][:45]:45s} {r['city'][:16]:16s} :: {r['issues'][:140]}")

# emit some numbers needed for markdown to a json
summary = dict(
    N=N, distinct_uid=int(df['unique_id'].nunique()), distinct_cluster=int(df['cluster_id'].nunique()),
    n_corrupt=n_corrupt, n_out_of_india=n_out_of_india, n_swap=n_swap, n_cc_mismatch=n_cc_mismatch,
    n_yr_bad=n_yr_bad, n_cap_no_doc=n_cap_no_doc, n_doc_no_cap=n_doc_no_cap,
    n_rows_within_dup=n_rows_within_dup, total_within_dup=total_within_dup,
    n_queue=int(qmask.sum()), n_contradiction=int(has_contradiction.sum()),
)
with open('/Users/koushik/Desktop/health_analysis_outputs/_steward_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print()
print('SUMMARY_JSON', json.dumps(summary))
