#!/usr/bin/env python
"""Build the cleaned district-level analytic table for causal inference (Track-3 EDA-clean)."""
import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
DL='/Users/koushik/Downloads'; ART='/Users/koushik/Desktop/health_analysis_outputs'
nf=pd.read_csv(f'{DL}/nfhs5.csv',dtype=str); hdr=list(nf.columns)
def clean(x):
    s=str(x).strip()
    if s in ('*','','NA','nan','None'): return np.nan
    s=s.strip('()').replace(',','')
    try: return float(s)
    except: return np.nan
def col(sub):
    m=[c for c in hdr if sub in c]; return m[0] if m else None
# clean named variables: (clean_name, substring, role)
VARS=[
 ('stunting','child_u5_who_are_stunted','outcome'),('wasting','child_u5_who_are_wasted_weight_for_height_18','outcome'),
 ('underweight','child_u5_who_are_underweight','outcome'),('inst_birth','institutional_birth_5y','outcome'),
 ('full_imm','fully_vaccinated_based_on_information_from_eit','outcome'),('anaemia_women','all_w15_49_who_are_anaemic','outcome'),
 ('teen_preg','w15_19_who_were_already_mothers','outcome'),('csection','births_delivered_by_csection_5y','outcome'),
 ('sanitation','hh_use_improved_sanitation','treatment'),('clean_fuel','households_using_clean_fuel','treatment'),
 ('fem_school10','women_age_15_49_with_10_or_more_years','treatment'),('literacy','women_age_15_49_who_are_literate','treatment'),
 ('insurance','hh_member_covered_health_insurance','treatment'),('anc4','at_least_4_anc','treatment'),
 ('electricity','hh_electricity','treatment'),('improved_water','hh_improved_water','treatment'),
 ('child_marriage','married_before_age_18','outcome'),('menstrual_hygiene','w15_24_who_use_menstrual','treatment'),
 ('diarrhoea','prev_diarrhoea','mediator'),('ari','symptoms_of_acute_respiratory','mediator'),
 ('pop_under15','population_below_age_15','confounder'),('sex_ratio','sex_ratio_total_f_per_1000_m','confounder'),
 ('women_overweight','who_are_overweight_obese','treatment'),('high_bp_w','w15_plus_with_high_bp_sys_gte_140','outcome'),
 ('high_sugar_w','w15_plus_with_high_or_very_high_gt_140_mg_dl_blood_sugar_or','outcome'),
 ('clean_water','hh_improved_water','treatment'),
]
df=pd.DataFrame({'state':nf['state_ut'].str.strip(),'district':nf['district_name'].str.strip()})
for nm,sub,role in VARS:
    c=col(sub)
    if c is not None and nm not in df: df[nm]=nf[c].map(clean)
# reliability weights
df['w_women']=pd.to_numeric(nf['women_15_49_interviewed'],errors='coerce')
df['w_men']=pd.to_numeric(nf['men_15_54_interviewed'],errors='coerce')
df['w_households']=pd.to_numeric(nf['households_surveyed'],errors='coerce')

# merge supply counts from the integrated table
def normst(s):
    s=str(s).strip().upper().replace(' AND ',' & ');
    return s.replace('NCT OF DELHI','DELHI').replace('ISLANDS','').strip()
def normd(s): return str(s).strip().upper()
df['_s']=df['state'].map(normst); df['_d']=df['district'].map(normd)
try:
    sd=pd.read_csv(f'{ART}/district_supply_demand.csv')
    sup=sd[['_s','_d','n_facilities','n_hospital','n_clinic']].drop_duplicates(['_s','_d'])
    df=df.merge(sup,on=['_s','_d'],how='left')
    for c in ['n_facilities','n_hospital','n_clinic']: df[c]=df[c].fillna(0)
except Exception as e:
    print('supply merge skipped:',e)

# capability-STRONG density per district from hardened trust + facility->district
try:
    fc=pd.read_csv(f'{DL}/facilities_hack.csv',dtype=str)
    pc=pd.read_csv(f'{DL}/india_post.csv',dtype=str)
    pcu=pc.assign(P=pc['pincode'].astype(str).str.strip()).drop_duplicates('P')
    pin2d=pcu.set_index('P')['district'].map(normd)
    fz=fc['address_zipOrPostcode'].astype(str).str.extract(r'(\d{6})')[0]
    fc=fc.assign(_d=fz.map(pin2d))
    tr=pd.read_csv(f'{ART}/facility_capability_trust_hardened.csv')
    strong=tr[tr['evidence_tier'].astype(str).str.startswith(('VERIFIED-STRONG','STRONG'))]
    strong=strong.merge(fc[['unique_id','_d']].drop_duplicates('unique_id'),on='unique_id',how='left')
    for cap,nm in [('maternity / obstetrics','sup_maternity_strong'),('NICU / neonatal','sup_nicu_strong'),('emergency','sup_emergency_strong')]:
        cnt=strong[strong['capability']==cap].groupby('_d').size()
        df[nm]=df['_d'].map(cnt).fillna(0)
except Exception as e:
    print('capability density skipped:',e)

df=df.drop(columns=['_s','_d'])
df.to_csv(f'{ART}/causal_analytic_table.csv',index=False)
print('causal_analytic_table.csv:',df.shape)
print('columns:',list(df.columns))
print('supply coverage: districts with >=1 facility:',int((df['n_facilities']>0).sum()),'/',len(df))
print(df[['stunting','sanitation','fem_school10','inst_birth','n_facilities','sup_maternity_strong']].describe().round(1).to_string())
