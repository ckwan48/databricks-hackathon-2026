#!/usr/bin/env python3
"""
bridge_overlap.py
Reproduces the supply-vs-demand bridge diagnostics for the 100-row national sample.
Inputs : /Users/koushik/Downloads/{facilities,nfhs,india_pincode}.csv
Outputs: prints overlap stats; writes ap_bihar_supply_vs_nfhs_demand.csv
Run    : /tmp/dataenv/bin/python bridge_overlap.py
"""
import pandas as pd, ast

F = '/Users/koushik/Downloads/facilities.csv'
N = '/Users/koushik/Downloads/nfhs.csv'
P = '/Users/koushik/Downloads/india_pincode.csv'
OUT = '/Users/koushik/Desktop/health_analysis_outputs/ap_bihar_supply_vs_nfhs_demand.csv'

f = pd.read_csv(F); n = pd.read_csv(N); p = pd.read_csv(P)
norm = lambda s: str(s).strip().lower()

# ---- 1. State-level overlap across the three alphabetical 100-row slices ----
fac_s  = set(f['address_stateOrRegion'].dropna().map(norm))
nfhs_s = set(n['state_ut'].dropna().map(norm))
pin_s  = set(p['statename'].dropna().map(norm))
print('FAC states           :', len(fac_s))
print('NFHS states          :', sorted(nfhs_s))
print('PINCODE states        :', sorted(pin_s))
print('FAC ∩ NFHS           :', sorted(fac_s & nfhs_s))
print('FAC ∩ PINCODE        :', sorted(fac_s & pin_s))
print('NFHS ∩ PINCODE       :', sorted(nfhs_s & pin_s))
print('FAC ∩ NFHS ∩ PINCODE :', sorted(fac_s & nfhs_s & pin_s))

# ---- 2. Pincode bridge can't fire: zero shared pincodes ----
fz = set(f['address_zipOrPostcode'].dropna().astype(str).str.replace(r'\.0$','',regex=True).str.strip())
pz = set(p['pincode'].dropna().astype(str).str.replace(r'\.0$','',regex=True).str.strip())
print('\nfacility zips:', len(fz), 'pincode-file pincodes:', len(pz),
      'shared:', len(fz & pz))

# ---- 3. The ONE possible within-sample illustration: AP & Bihar ----
# Map facility city -> NFHS district (manual crosswalk for the 7 rows that overlap)
city2dist = {'patna':'Patna ', 'guntur':'Guntur '}   # Vijayawada=Krishna dist; not directly named by city
sub = f[f['address_stateOrRegion'].map(norm).isin(['andhra pradesh','bihar'])].copy()
sub['nfhs_district'] = sub['address_city'].map(norm).map(city2dist)

nfhs_cols = ['district_name','state_ut','institutional_birth_5y_pct',
             'births_delivered_by_csection_5y_pct',
             'births_in_a_private_fac_that_were_delivered_by_csection_5y_pct',
             'mothers_who_had_at_least_4_anc_visits_lb5y_pct',
             'all_w15_49_who_are_anaemic_pct',
             'w15_plus_with_high_or_very_high_gt_140_mg_dl_blood_sugar_or_pct',
             'hh_member_covered_health_insurance_pct']
joined = sub.merge(n[nfhs_cols], left_on='nfhs_district', right_on='district_name', how='left')
keep = ['name','address_city','address_stateOrRegion','facilityTypeId','operatorTypeId',
        'nfhs_district'] + nfhs_cols[2:]
joined[keep].to_csv(OUT, index=False)
print('\nWrote', OUT, 'rows:', len(joined))
print(joined[keep].to_string())
