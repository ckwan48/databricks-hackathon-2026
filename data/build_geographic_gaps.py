#!/usr/bin/env python3
"""
Geographic, trust-weighted capability gap analysis at NATIONAL scale.

Pipeline:
  1. Derive (district, state) for each facility:
       address_zipOrPostcode (6-digit) -> india_post pincode -> (district, statename)
       fall back to address_stateOrRegion when zip missing/unmatched.
  2. Join facility->region onto the trust-graded long table
     (one row per facility x capability, grade in
      STRONG / PARTIAL / WEAK-SUSPICIOUS / NO CLAIM).
  3. Dedupe on cluster_id so co-clustered duplicate rows are not double-counted.
  4. Aggregate trust-weighted capability availability by STATE and by DISTRICT.
  5. Classify each region x capability and each region overall:
        DATA-POOR        : n_facilities < 5  OR  mean evidence fill-rate < 0.5
        APPARENT CARE GAP: n_facilities >= 5 AND strong+partial share < 0.20
        EVIDENCED SUPPLY : otherwise
"""
import pandas as pd, numpy as np, re

FAC = '/Users/koushik/Downloads/facilities_hack.csv'
TRUST = '/Users/koushik/Desktop/health_analysis_outputs/facility_capability_trust.csv'
INDIA_POST = '/Users/koushik/Downloads/india_post.csv'
OUT_CSV = '/Users/koushik/Desktop/health_analysis_outputs/region_capability_gaps.csv'

EV_COLS = ['source_types','source_ids','specialties','procedure','equipment','capability','source_urls']

# ---- thresholds (explicit, scaled to full data) ----
MIN_FAC = 5            # data-poor if fewer than this many distinct facilities
MIN_FILL = 0.50        # data-poor if mean evidence fill-rate below this
GAP_SHARE = 0.20       # care gap if strong+partial share below this (>=MIN_FAC)
# trust weights for a weighted-availability score
W = {'STRONG':1.0, 'PARTIAL':0.5, 'WEAK/SUSPICIOUS':0.1, 'NO CLAIM':0.0}

def norm_state(s):
    if not isinstance(s,str): return ''
    s = s.strip().upper()
    s = re.sub(r'\s+',' ',s)
    s = s.replace(' AND ',' & ')
    aliases = {
        'ORISSA':'ODISHA','PONDICHERRY':'PUDUCHERRY','UTTARANCHAL':'UTTARAKHAND',
        'NCT OF DELHI':'DELHI','DELHI (NCT)':'DELHI',
        'JAMMU & KASHMIR':'JAMMU AND KASHMIR','J & K':'JAMMU AND KASHMIR',
        'DADRA & NAGAR HAVELI':'DADRA AND NAGAR HAVELI',
    }
    return aliases.get(s,s)

# ---------- 1. india_post pincode -> district,state ----------
ip = pd.read_csv(INDIA_POST, dtype=str)
ip['pincode'] = ip['pincode'].str.strip()
# one district/state per pincode (mode); pincodes can span >1 office but rarely >1 district
ip_map = (ip.dropna(subset=['pincode','district','statename'])
            .groupby('pincode')
            .agg(district=('district', lambda x: x.value_counts().index[0]),
                 statename=('statename', lambda x: x.value_counts().index[0]))
            .reset_index())
ip_map['district'] = ip_map['district'].str.strip().str.title()
ip_map['pin_state'] = ip_map['statename'].map(norm_state)
print(f"india_post: {len(ip_map)} distinct pincodes mapped")

# ---------- 2. facilities + region derivation ----------
f = pd.read_csv(FAC, dtype=str)
f['zip6'] = f['address_zipOrPostcode'].fillna('').str.strip()
f.loc[~f['zip6'].str.match(r'^\d{6}$'), 'zip6'] = ''

f = f.merge(ip_map[['pincode','district','pin_state']],
            left_on='zip6', right_on='pincode', how='left')

# state: prefer PIN-derived, else cleaned address_stateOrRegion
f['state_fallback'] = f['address_stateOrRegion'].fillna('').str.strip()
# drop garbage (>40 chars) fallback values
f.loc[f['state_fallback'].str.len()>40, 'state_fallback'] = ''
f['state_fallback_n'] = f['state_fallback'].map(norm_state)
f['state'] = f['pin_state'].where(f['pin_state'].notna() & (f['pin_state']!=''),
                                  f['state_fallback_n'])
f['state'] = f['state'].replace('', np.nan)

# district: PIN-derived; fallback to "<statefallback> (unmapped)" when no PIN match
f['district_src'] = np.where(f['district'].notna(), 'pin', 'fallback')
f['district'] = f['district'].where(f['district'].notna(),
        np.where(f['state_fallback']!='', f['state_fallback'].str.title()+' (district unknown)', np.nan))

matched = (f['district_src']=='pin').sum()
print(f"facilities: {len(f)}  PIN->district matched: {matched} ({matched/len(f):.1%})")
print(f"state assigned: {f['state'].notna().sum()}  district assigned: {f['district'].notna().sum()}")

# ---------- 3. evidence fill-rate per facility (0..1) ----------
def filled(col):
    s = f[col].fillna('null').str.strip()
    return (~s.isin(['null','[]','','NaN','None'])).astype(int)
fill = pd.DataFrame({c: filled(c) for c in EV_COLS})
f['fill_rate'] = fill.mean(axis=1)

# dedupe key: cluster_id (fallback to unique_id)
f['cluster_key'] = f['cluster_id'].fillna(f['unique_id'])

fac_region = f[['unique_id','cluster_key','state','district','fill_rate']].copy()

# ---------- 4. join trust long table ----------
t = pd.read_csv(TRUST, dtype=str)
t = t[['unique_id','capability','grade']].copy()
t['grade'] = t['grade'].str.strip().str.upper()
t['w'] = t['grade'].map(W).fillna(0.0)
t['is_strong'] = (t['grade']=='STRONG').astype(int)
t['is_partial'] = (t['grade']=='PARTIAL').astype(int)

m = t.merge(fac_region, on='unique_id', how='left')
print(f"trust rows: {len(t)}  joined with region (state present): {m['state'].notna().sum()}")

# dedupe within (region-level, region, capability, cluster_key): keep best grade per cluster
GRADE_RANK = {'STRONG':3,'PARTIAL':2,'WEAK/SUSPICIOUS':1,'NO CLAIM':0}
m['grank'] = m['grade'].map(GRADE_RANK).fillna(0)

def aggregate(df, level, region_col):
    d = df.dropna(subset=[region_col]).copy()
    # collapse co-clustered duplicate facilities -> one row per (region,capability,cluster_key)
    d = (d.sort_values('grank', ascending=False)
           .drop_duplicates(subset=[region_col,'capability','cluster_key'], keep='first'))
    g = d.groupby([region_col,'capability'])
    out = g.agg(
        n_facilities=('cluster_key','nunique'),
        n_strong=('is_strong','sum'),
        n_partial=('is_partial','sum'),
        sum_w=('w','sum'),
        fill_rate=('fill_rate','mean'),
    ).reset_index()
    out['weighted_score'] = out['sum_w'] / out['n_facilities']   # mean trust weight, 0..1
    out = out.rename(columns={region_col:'region'})
    out['level'] = level
    return out[['region','level','capability','n_facilities','n_strong','n_partial',
                'weighted_score','fill_rate']]

state_agg = aggregate(m, 'state', 'state')
dist_agg  = aggregate(m, 'district', 'district')

# ---------- 5. classify ----------
def classify(row):
    n = row['n_facilities']; fr = row['fill_rate']
    sp_share = (row['n_strong'] + row['n_partial']) / n if n else 0
    if n < MIN_FAC or fr < MIN_FILL:
        return 'DATA-POOR'
    if sp_share < GAP_SHARE:
        return 'APPARENT CARE GAP'
    return 'EVIDENCED SUPPLY'

allreg = pd.concat([state_agg, dist_agg], ignore_index=True)
allreg['sp_share'] = (allreg['n_strong']+allreg['n_partial'])/allreg['n_facilities']
allreg['classification'] = allreg.apply(classify, axis=1)

# round
for c in ['weighted_score','fill_rate','sp_share']:
    allreg[c] = allreg[c].round(4)

allreg = allreg.sort_values(['level','region','capability'])
cols = ['region','level','capability','n_facilities','n_strong','n_partial',
        'weighted_score','fill_rate','classification']
allreg[cols].to_csv(OUT_CSV, index=False)
print(f"\nWROTE {OUT_CSV}  rows={len(allreg)}")
print("\nclassification counts (region x capability):")
print(allreg.groupby(['level','classification']).size())

# save full for section building
allreg.to_pickle('/tmp/allreg.pkl')
fac_region.to_pickle('/tmp/fac_region.pkl')
PY=None
