#!/usr/bin/env python
"""Build the data-quality review queue for the facilities sample (first 100 rows)."""
import pandas as pd, json
from collections import Counter

SRC='/Users/koushik/Downloads/facilities.csv'
TRUST='/Users/koushik/Desktop/health_analysis_outputs/facility_capability_trust.csv'
OUT='/Users/koushik/Desktop/health_analysis_outputs/review_queue.csv'

df = pd.read_csv(SRC, dtype=str).fillna('null')
trust = pd.read_csv(TRUST, dtype=str).fillna('')

def raw_list(v):
    s=str(v).strip()
    if s=='' or s.lower()=='null': return []
    try:
        arr=json.loads(s)
        return [str(x) for x in arr if x is not None and str(x).lower()!='null'] if isinstance(arr,list) else [str(arr)]
    except: return []
def S(v): return '' if (v is None or str(v).lower()=='null') else str(v)
def miss(v): return v is None or str(v).strip()=='' or str(v).strip().lower() in ('null','nan')
def fnum(v):
    try: return float(v) if not miss(v) else None
    except: return None

# trust contradiction flags per facility
trust_contra = trust[trust['contradiction_flag'].str.lower()=='true'].groupby('unique_id').size().to_dict()

small_types={'clinic','dentist','doctor','farmacy','pharmacy'}
high_acuity=['icu','intensive care','nicu','neonatal','critical care','oncology','cancer','trauma','dialysis','transplant','cath lab','open heart','ventilator']
acuity_specs_set={'intensivecaremedicine','neonatologyperinatalmedicine','surgicaloncology','medicaloncology','radiationoncology','cardiothoracicsurgery','neurosurgery'}
dental_ok={'dentistry','dental','generaldentistry','aestheticdentistry','cosmeticdentistry','dentoalveolarsurgery','oralandmaxillofacialsurgery','orthodontics','endodontics','periodontics','prosthodontics','pedodontics','pediatricdentistry','sportsdentistry'}
syn_pairs=[('ent','otolaryngology'),('generalmedicine','internalmedicine'),('dental','dentistry'),('generaldentistry','dentistry'),('cosmeticdentistry','aestheticdentistry')]
core_contact=['phone_numbers','officialPhone','email','officialWebsite']

rows=[]
for _,r in df.iterrows():
    uid=S(r['unique_id']); name=S(r['name']); city=S(r['address_city']); st=S(r['address_stateOrRegion'])
    ft=S(r['facilityTypeId']).lower()
    caps=raw_list(r['capability']); specs=raw_list(r['specialties'])
    specs_l=[s.lower() for s in specs]; uspecs=set(specs_l)
    blob=(' '.join(caps)+' '+' '.join(specs_l)).lower()
    issues=[]; sev=0  # severity weight accumulates risk

    # --- CONTRADICTIONS ---
    # A. small type with high-acuity capability/specialty
    if ft in small_types:
        hits=sorted({k for k in high_acuity if k in blob})
        asp=sorted({s for s in specs if s.lower() in acuity_specs_set})
        if hits or asp:
            issues.append(f"{ft} claims high-acuity ({', '.join(hits+asp)})"); sev+=3
    # B. small type with too many specialties
    if ft in small_types and len(uspecs)>=12:
        issues.append(f"{ft} lists {len(uspecs)} distinct specialties"); sev+=2
    # C. dentist with non-dental specialties
    if ft=='dentist':
        nondental=sorted(uspecs - dental_ok)
        if nondental:
            issues.append(f"dentist with non-dental specialties ({', '.join(nondental)})"); sev+=2
    # Geo: out-of-India / swap
    lat=fnum(r['latitude']); lon=fnum(r['longitude'])
    if lat is not None and lon is not None:
        in_india=(6<=lat<=37) and (68<=lon<=98)
        swap_in=(6<=lon<=37) and (68<=lat<=98)
        if not in_india:
            issues.append(f"coordinates outside India (lat={lat:.2f},lon={lon:.2f}; cc={S(r['address_countryCode'])})" + (" [lat/lon swap likely]" if swap_in else "")); sev+=3
    # capacity vs doctors
    cap=fnum(r['capacity']); doc=fnum(r['numberDoctors'])
    if cap is not None and cap>0 and (doc is None or doc==0):
        issues.append(f"capacity={int(cap)} but numberDoctors missing/0"); sev+=1
    # year plausibility
    yr=fnum(r['yearEstablished'])
    if yr is not None and (yr<1800 or yr>2026):
        issues.append(f"implausible yearEstablished={int(yr)}"); sev+=2

    # --- TAXONOMY ---
    c=Counter(specs_l)
    dups={k:v for k,v in c.items() if v>1}
    if dups:
        issues.append(f"within-row duplicate specialty codes ({len(dups)} codes, {sum(v-1 for v in dups.values())} redundant)"); sev+=1
    syn_here=[f"{a}+{b}" for a,b in syn_pairs if a in uspecs and b in uspecs]
    if syn_here:
        issues.append(f"overlapping synonym codes ({', '.join(syn_here)})"); sev+=1

    # --- SPARSITY ---
    if miss(r['facilityTypeId']):
        issues.append("missing facilityTypeId (core identity)"); sev+=2
    if not any(not miss(r[cc]) for cc in core_contact):
        issues.append("no phone/email/website (no contact channel)"); sev+=2
    elif miss(r['phone_numbers']) and miss(r['officialPhone']):
        issues.append("no phone number"); sev+=1
    # count sparse core fields
    sparse_core=[f for f in ['facilityTypeId','operatorTypeId','yearEstablished','numberDoctors'] if miss(r[f])]
    if len(sparse_core)>=3:
        issues.append(f"sparse core attributes ({', '.join(sparse_core)})"); sev+=1

    # trust-table contradiction corroboration
    tc=trust_contra.get(uid,0)
    if tc:
        issues.append(f"trust-table flagged {tc} capability contradiction(s)"); sev+=2

    # --- POPULARITY / LEVERAGE ---
    foll=fnum(r['engagement_metrics_n_followers']) or 0
    posts=fnum(r['post_metrics_post_count']) or 0
    facts=fnum(r['number_of_facts_about_the_organization']) or 0
    likes=fnum(r['engagement_metrics_n_likes']) or 0
    smc=fnum(r['distinct_social_media_presence_count']) or 0
    import math
    pop = math.log1p(foll) + math.log1p(likes) + 0.5*math.log1p(posts) + 0.3*facts + 0.2*smc
    # priority = leverage(popularity) amplified by risk(severity)
    priority = round(pop*(1+sev) + 2.0*sev, 2)

    if issues:
        # suggested action
        if any('outside India' in i for i in issues):
            action="Re-geocode from address; verify lat/lon order"
        elif any('high-acuity' in i for i in issues):
            action="Manual review: verify facilityTypeId vs claimed acuity capabilities"
        elif any('non-dental' in i for i in issues):
            action="Reclassify type or prune non-dental specialties"
        elif any('missing facilityTypeId' in i for i in issues):
            action="Classify facilityTypeId from description/specialties"
        elif any('no phone/email/website' in i for i in issues):
            action="Enrich contact fields before publish"
        elif any('duplicate' in i or 'synonym' in i for i in issues):
            action="Normalize/dedup specialty taxonomy"
        else:
            action="Standard QA review"
        rows.append({'unique_id':uid,'name':name,'city':city,'state':st,
                     'priority_score':priority,'issues':'; '.join(issues),
                     'suggested_action':action,'_sev':sev,'_pop':round(pop,2)})

out=pd.DataFrame(rows).sort_values('priority_score',ascending=False).reset_index(drop=True)
out_public=out[['unique_id','name','city','state','priority_score','issues','suggested_action']]
out_public.to_csv(OUT,index=False)
print("Review queue rows:",len(out),"of 100 facilities")
print("Facilities clean (no issues):",100-len(out))
print("\n--- TOP 15 ---")
for i,r in out.head(15).iterrows():
    print(f"{i+1:2d}. [{r['priority_score']:8.2f}] sev={r['_sev']} pop={r['_pop']} {r['name'][:34]:36} {r['city']}/{r['state']}")
    print(f"     {r['issues'][:160]}")
