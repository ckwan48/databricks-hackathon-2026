#!/usr/bin/env python
"""Harden capability trust grades and attach a 0-100 confidence score. Full national data."""
import pandas as pd, numpy as np, json, re
ART='/Users/koushik/Desktop/health_analysis_outputs'; DL='/Users/koushik/Downloads'
t=pd.read_csv(f'{ART}/facility_capability_trust.csv')
fc=pd.read_csv(f'{DL}/facilities_hack.csv',dtype=str)

def arr(x):
    try: return [str(i).lower() for i in json.loads(x) if i not in (None,'null')]
    except: return []
spec={r['unique_id']:set(arr(r['specialties'])) for _,r in fc.iterrows()}
name={r['unique_id']:str(r['name']).lower() for _,r in fc.iterrows()}
PLAUS={'ICU / critical care':{'criticalcaremedicine','pulmonology','cardiology','anesthesia'},
 'NICU / neonatal':{'neonatologyperinatalmedicine','pediatrics','gynecologyandobstetrics'},
 'maternity / obstetrics':{'gynecologyandobstetrics','reproductiveendocrinologyandinfertility'},
 'emergency':{'emergencymedicine'},
 'oncology / cancer':{'medicaloncology','surgicaloncology','radiationoncology','breastimaging','hematology'},
 'trauma / orthopedic':{'orthopedicsurgery','traumasurgery'},
 'dialysis / renal':{'nephrology','urology'}}
ACUTE={'ICU / critical care','NICU / neonatal','oncology / cancer','dialysis / renal'}

def reclass(r):
    if r['grade']!='WEAK/SUSPICIOUS': return r['grade']
    ft=str(r['facilityTypeId']).lower(); uid=r['unique_id']; cap=r['capability']; nm=name.get(uid,'')
    if ft in ('dentist','farmacy','pharmacy','doctor'): return 'HARD-CONTRADICTION'
    if ft=='clinic':
        related=bool(spec.get(uid,set()) & PLAUS.get(cap,set()))
        if cap in ('maternity / obstetrics','NICU / neonatal') and (related or any(k in nm for k in ('women','gyn','obstet','matern','kidz','child','pediatr','paediatr'))): return 'PLAUSIBLE-SPECIALTY-CLINIC'
        if cap=='ICU / critical care' and (related or any(k in nm for k in ('women','kidz','child','cardiac','critical'))): return 'PLAUSIBLE-SPECIALTY-CLINIC'
        if cap=='dialysis / renal' and (related or any(k in nm for k in ('kidney','nephro','dialysis'))): return 'PLAUSIBLE-SPECIALTY-CLINIC'
        if cap=='oncology / cancer': return 'PLAUSIBLE-SPECIALTY-CLINIC' if related else 'HARD-CONTRADICTION'
        return 'HARD-CONTRADICTION' if cap in ACUTE else 'PLAUSIBLE-SPECIALTY-CLINIC'
    return r['grade']

t['grade_hardened']=t.apply(reclass,axis=1)
def tier(r):
    if r['grade']=='STRONG': return 'VERIFIED-STRONG (multi-source)' if r['n_distinct_source_types']>=2 else 'STRONG (single-source)'
    return r['grade_hardened']
t['evidence_tier']=t.apply(tier,axis=1)
BASE={'VERIFIED-STRONG (multi-source)':65,'STRONG (single-source)':55,'PARTIAL':38,'PLAUSIBLE-SPECIALTY-CLINIC':28,'WEAK/SUSPICIOUS':18,'HARD-CONTRADICTION':8}
def score(r):
    if r['evidence_tier'] not in BASE: return 0
    s=BASE[r['evidence_tier']]+min(20,5*(int(r['n_evidence_types'])-1))+min(10,5*(int(r['n_distinct_source_types'])-1))
    if r['evidence_tier']=='HARD-CONTRADICTION' or str(r.get('contradiction_flag')).lower() in ('true','1','1.0'): s=min(s,30)
    return max(0,min(100,s))
t['confidence']=t.apply(score,axis=1)
def lvl(c): return 'VERY HIGH' if c>=85 else 'HIGH' if c>=70 else 'MODERATE' if c>=50 else 'LOW' if c>=30 else ('VERY LOW / REJECT' if c>0 else 'NO CLAIM')
t['confidence_level']=t['confidence'].map(lvl)
t.to_csv(f'{ART}/facility_capability_trust_hardened.csv',index=False)
t.to_csv(f'{ART}/facility_capability_confidence.csv',index=False)

claimed=t[t['evidence_tier'].isin(BASE)]
print("=== FULL-DATA evidence pyramid (claimed cells: %d) ==="%len(claimed))
print(t['evidence_tier'].value_counts().to_string())
print("\n=== WEAK/SUSPICIOUS reclassified ===")
print(t[t['grade']=='WEAK/SUSPICIOUS']['grade_hardened'].value_counts().to_string())
print("\n=== confidence level distribution (claimed) ===")
print(claimed['confidence_level'].value_counts().reindex(['VERY HIGH','HIGH','MODERATE','LOW','VERY LOW / REJECT']).to_string())
print("\nVERIFIED-STRONG facilities: %d | HARD-CONTRADICTION cells: %d"%(
    (t['evidence_tier']=='VERIFIED-STRONG (multi-source)').sum(),(t['evidence_tier']=='HARD-CONTRADICTION').sum()))
