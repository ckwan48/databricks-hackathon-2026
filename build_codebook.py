#!/usr/bin/env python
"""Value-level codebook: what each value of each coded column means, from the full data."""
import pandas as pd, numpy as np, json, warnings; warnings.filterwarnings('ignore')
from collections import Counter
DL='/Users/koushik/Downloads'; SEC='/tmp/report_sections'
pc=pd.read_csv(f'{DL}/india_post.csv',dtype=str); fc=pd.read_csv(f'{DL}/facilities_hack.csv',dtype=str); nf=pd.read_csv(f'{DL}/nfhs5.csv',dtype=str)
def vc(s): return s.value_counts(dropna=False)
def arr(x):
    try: return [str(i) for i in json.loads(x) if i not in (None,'null')]
    except: return []

OFFICE={'BO':'Branch Office — smallest rural/local post office; reports to a Sub Office','SO':'Sub Office — mid-level office under a Head Office','HO':'Head Office — top office of a postal division (e.g. a city GPO)'}
DELIV={'Delivery':'Delivers mail to addresses in its beat','Non Delivery':'Only books/processes mail; delivery done by another office'}
SRC={'overture':'Overture Maps Foundation open POI/places record (base map identity)','dynamic':'Dynamically scraped/derived content (live web pages, changeable facts)','constant':'Constant/static reference content (stable attributes)','mongo_facility':"Record from the platform's internal MongoDB facility store (curated/prior)",'mongo_ngo':"Record from the internal MongoDB NGO store"}
FT={'hospital':'Hospital (inpatient, multi-service)','clinic':'Clinic / OPD / single-service centre (many standalone dialysis/diagnostic centres are mis-typed here)','dentist':'Dental practice','doctor':'Solo doctor / individual practitioner','farmacy':'Pharmacy / drug store (MISSPELLED — should be "pharmacy")','pharmacy':'Pharmacy / drug store (correct spelling; coexists with "farmacy")'}
OP={'private':'Privately owned / operated','public':'Government / public-sector operated','government':'Government-operated (variant of "public" — normalize)'}
SPEC={'internalMedicine':'general adult internal medicine','familyMedicine':'family / general practice','gynecologyAndObstetrics':'OB-GYN (maternity)','pediatrics':'child health','dentistry':'dental','ophthalmology':'eye care','orthopedicSurgery':'bone & joint surgery','cardiology':'heart','dermatology':'skin','otolaryngology':'ENT (ear-nose-throat)','radiology':'imaging','generalSurgery':'general surgery','neurology':'nervous system','nephrology':'kidney / dialysis','criticalCareMedicine':'ICU / critical care','emergencyMedicine':'emergency','neonatologyPerinatalMedicine':'newborn / NICU'}

out=["## Value-Level Codebook (what each value MEANS, from the complete data)\n",
"*Beyond column meaning: for every CODED column, each distinct value, its count in the full data, and its meaning. Free-text and pure-numeric columns are summarized by their value SYSTEM.*\n"]

out.append("### NFHS — special value codes (apply to all 101 % / ratio / count cells)")
raw=nf[[c for c in nf.columns if c not in ('district_name','state_ut')]].astype(str).map(str.strip)
star=(raw=='*').values.sum(); paren=raw.map(lambda s:s.startswith('(') and s.endswith(')')).values.sum(); tot=raw.size
out+=["| Value pattern | Count | Meaning |","|---|---|---|",
 f"| `*` | {star:,} ({100*star/tot:.1f}%) | **Suppressed** — based on <25 unweighted cases; too few to report. Treat as missing. |",
 f"| `(value)` e.g. `(64.2)` | {paren:,} ({100*paren/tot:.1f}%) | Estimate from **25–49 unweighted cases** — usable but low precision; flag it. |",
 "| trailing spaces e.g. `927 ` | many | formatting noise — strip before use |",
 "| plain number | rest | interpret by unit: `*_pct`=% 0–100, `sex_ratio_*`=F per 1000 M, `*_interviewed`=count, OOP=₹ |\n"]

def block(title,counts,meanings,note=''):
    global out
    out.append(f"### {title}"); out+=["| Value | Count | Meaning |","|---|---|---|"]
    for v,c in counts.items():
        k=str(v).strip(); m=meanings.get(k,'missing' if k in ('nan','None') else '(other)')
        out.append(f"| `{k[:40]}` | {int(c):,} | {m} |")
    if note: out.append(f"\n{note}")
    out.append("")

block("Pincode · officetype",vc(pc['officetype']),OFFICE)
block("Pincode · delivery",vc(pc['delivery']),DELIV)
st=Counter()
for v in fc['source_types']: st.update(arr(v))
block("Facilities · source_types (provenance tag per evidence item)",dict(st.most_common()),SRC,
 "*Meanings inferred from naming + pipeline behaviour. The COUNT of DISTINCT source_types per facility is the trust signal — VERIFIED-STRONG grades require ≥2 distinct sources.*")
block("Facilities · facilityTypeId",vc(fc['facilityTypeId']).head(7),FT,
 "*The stray coordinates-JSON value is a column-shifted row (see misalignment note below).*")
# operatorType: clean values + misalignment count
opv=vc(fc['operatorTypeId']); clean_keys={'private','public','government','nan','None'}
mis=int(sum(c for v,c in opv.items() if str(v).strip() not in clean_keys))
block("Facilities · operatorTypeId",opv.head(4),OP,
 f"*⚠ Data-quality: **{mis} rows** carry malformed operatorTypeId values (coordinate fragments, URL-arrays, UUIDs, specialty codes) — these are **column-misaligned rows** where commas/JSON in earlier fields shifted the columns. They must be re-parsed or quarantined.*")
block("Facilities · organization_type",vc(fc['organization_type']).head(3),{'facility':'record class — the only valid value'})
for b in ['acceptsVolunteers','affiliated_staff_presence','custom_logo_presence']:
    block(f"Facilities · {b} (boolean)",vc(fc[b]).head(3),{'true':'yes','false':'no'})
block("Facilities · address_countryCode",vc(fc['address_countryCode']).head(5),{'IN':'India'})

sp=Counter()
for v in fc['specialties']: sp.update(arr(v))
out.append("### Facilities · specialties — the value SYSTEM (164 distinct codes)")
out.append(f"camelCase clinical specialty codes (HL7/FHIR-style); {len(sp)} distinct. Top values:\n")
out+=["| Code | Count | Meaning |","|---|---|---|"]
for k,c in sp.most_common(17): out.append(f"| `{k}` | {c:,} | {SPEC.get(k,'(clinical specialty)')} |")
out.append("\n*Overlapping pairs (`ent`↔`otolaryngology`, `generalMedicine`↔`internalMedicine`, `dental`↔`dentistry`) and within-row duplicates — normalize before modeling.*\n")
out.append("### Free-text / non-coded columns")
out.append("`capability`, `procedure`, `equipment`, `description`, `name`, address lines = free natural language (no fixed vocabulary). `pincode`=6-digit ID. `latitude`/`longitude`/`coordinates`=geo floats. `yearEstablished`=year; engagement/post metrics=counts. No enumerable value-meaning — see the unit audit (section 06).")
open(f'{SEC}/07_value_codebook.md','w').write('\n'.join(out)+'\n')
print(f"wrote 07_value_codebook.md | misaligned operatorTypeId rows: {mis} | source_types: {dict(st)}")
