#!/usr/bin/env python
"""Build the DAS_HACK deliverable: unique-values catalog, figures, MASTER.md and report.html."""
import pandas as pd, numpy as np, json, re, os, html as _html
from collections import Counter
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import markdown as mdlib

BASE='/Users/koushik/Downloads/DAS_HACK'; SEC='/tmp/report_sections'
FIG=f'{BASE}/figures'; DL='/Users/koushik/Downloads'; ART='/Users/koushik/Desktop/health_analysis_outputs'
os.makedirs(FIG,exist_ok=True)
plt.rcParams.update({'figure.dpi':110,'font.size':9,'axes.grid':True,'grid.alpha':.3})

def cleancell(x):
    s=str(x).strip()
    if s in ('*','','NA','nan','None','null'): return np.nan
    s=s.strip('()').replace(',','')
    try: return float(s)
    except: return np.nan

nf=pd.read_csv(f'{DL}/nfhs5.csv',dtype=str)
pc=pd.read_csv(f'{DL}/india_post.csv',dtype=str)
fc=pd.read_csv(f'{DL}/facilities_hack.csv',dtype=str)
nfc=nf.map(cleancell)
def C(sub):
    m=[c for c in nf.columns if sub in c]; return nfc[m[0]] if m else None

# ---------------- (A) UNIQUE-VALUES CATALOG ----------------
JSONCOLS={'source_types','source_ids','phone_numbers','websites','specialties','procedure',
          'equipment','capability','source_urls','countries','affiliationTypeIds'}
def is_jsonish(s):
    s=s.dropna().astype(str); return (s.str.startswith('[')).mean()>0.5 if len(s) else False
def catalog(df,name):
    L=[f"### {name} — {df.shape[0]} rows × {df.shape[1]} columns\n",
       "| # | Column | Kind | Fill | #unique | Values / range |","|---|---|---|---|---|---|"]
    for i,c in enumerate(df.columns):
        col=df[c].replace({'null':np.nan,'NA':np.nan,'*':np.nan,'':np.nan})
        fill=f"{100*col.notna().mean():.0f}%"; nu=int(col.nunique(dropna=True))
        if c in JSONCOLS or is_jsonish(df[c]):
            ct=Counter()
            for v in df[c].dropna():
                try: ct.update([str(t) for t in json.loads(v) if t not in (None,'null')])
                except: pass
            top=', '.join(f"{k}×{n}" for k,n in ct.most_common(6))
            kind,val='json[]',(f"{len(ct)} tokens; top: {top}" if ct else "—")
        else:
            asnum=pd.to_numeric(col.astype(str).str.strip().str.strip('()').str.replace(',',''),errors='coerce')
            if c=='pincode': kind,val='id',f"e.g. {', '.join(col.dropna().unique()[:3])} …"
            elif col.notna().any() and asnum.notna().mean()>.8 and nu>20:
                kind,val='numeric',f"min {asnum.min():.4g} · median {asnum.median():.4g} · max {asnum.max():.4g}"
            elif nu<=30:
                kind='categorical'; vc=col.value_counts().head(30)
                val='; '.join(f"{str(k)[:26]} ({v})" for k,v in vc.items())
            else:
                kind='id/high-card'; val="e.g. "+'; '.join(str(x)[:18] for x in col.dropna().unique()[:3])+" …"
        L.append(f"| {i} | `{c}` | {kind} | {fill} | {nu} | {val} |")
    return '\n'.join(L)+'\n'
cat=("## Complete Unique-Values Catalog (every column, every table)\n\n"
     "*Categorical (≤30 unique): full value list with counts. Numeric: cardinality + range (continuous, not enumerable). "
     "JSON-array: distinct token count + top tokens. ID/high-card: cardinality + examples.*\n\n"
     +catalog(pc,'india_pincode.csv')+"\n"+catalog(fc,'facilities.csv')+"\n"+catalog(nf,'nfhs.csv'))
open(f'{SEC}/90_unique_values_catalog.md','w').write(cat)

# ---------------- (A2) CONSOLIDATED DATA DICTIONARY (meanings) ----------------
ABBR={'fp':'family planning','cm':'currently married','anc':'antenatal care','pnc':'postnatal care',
 'ifa':'iron & folic acid','mcp':'mother & child protection card','steril':'sterilisation','bcg':'BCG',
 'mcv':'measles-containing vaccine','dpt':'DPT','penta':'pentavalent','ari':'acute respiratory infection',
 'whr':'waist-to-hip ratio','bp':'blood pressure','csection':'caesarean (C-section)','fac':'facility',
 'hp':'health personnel','reg':'registration','ors':'oral rehydration salts','neo':'neonatal','hh':'household'}
def denom(c):
    rules=[('fp_cm_w15_49','currently married women 15–49'),('non_pregnant_w15_49','non-pregnant women 15–49'),
     ('pregnant_w15_49','pregnant women 15–49'),('women_age_15_49','women 15–49'),('w1549','women 15–49'),('w15_49','women 15–49'),
     ('w20_24','women 20–24'),('all_w15_19','women/girls 15–19'),('w15_19','women/girls 15–19'),('w15_24','young women 15–24'),
     ('women_age_30_49','women 30–49'),('w15_plus','women 15+'),('women_age_15_years_and_above','women 15+'),
     ('m15_plus','men 15+'),('men_age_15','men 15+'),('men_15_54','men 15–54'),('child_12_23m','children 12–23 months'),
     ('child_24_35m','children 24–35 months'),('child_9_35m','children 9–35 months'),('child_6_59m','children 6–59 months'),
     ('child_6_23m','children 6–23 months'),('6_23m','children 6–23 months'),('child_6_8m','children 6–8 months'),
     ('child_u6m','children under 6 months'),('children_under_age_3','children under 3'),('child_u5','children under 5'),
     ('mothers','mothers (last birth in 5y)'),('lb5y','mothers (last birth in 5y)'),('registered_pregnancies','registered pregnancies'),
     ('households','households')]
    for k,v in rules:
        if k in c: return v
    if c.startswith('births'): return 'births in last 5 years'
    if c.startswith('hh'): return 'households'
    return '—'
def gloss(c):
    s=' '+c.replace('_pct','').replace('_',' ')+' '
    repl={' fp cm ':' family planning — ',' fp unmet ':' unmet need for family planning — ',
          ' f steril ':' female sterilisation ',' m steril ':' male sterilisation ',' anc ':' ANC ',' pnc ':' PNC ',
          ' ifa ':' iron-folic-acid ',' mcp ':' MCP card ',' bcg ':' BCG ',' mcv ':' measles vaccine ',' dpt ':' DPT ',
          ' ari ':' ARI ',' bp ':' blood pressure ',' csection ':' C-section ',' lt ':' < ',' gt ':' > ',
          ' g dl ':' g/dl ',' mg dl ':' mg/dl ',' ors ':' ORS ',' neo ':' neonatal ',' vit a ':' vitamin A '}
    for a,b in repl.items(): s=s.replace(a,b)
    for pop in ['fp cm w15 49','non pregnant w15 49','pregnant w15 49','women age 15 49','w15 49','w1549',
                'w15 plus','m15 plus','women age 15 years and above','men age 15 years and above','men age 15',
                'child 12 23m','child 24 35m','child 9 35m','child 6 59m','child 6 23m','child 6 8m','child u6m',
                'child u5','children under age 3','w20 24','w15 19','w15 24','women age 30 49']:
        s=s.replace(' '+pop+' ',' ')
    s=re.sub(r'\s+\d+\s*$',' ',s)            # strip trailing footnote number only
    s=re.sub(r'\s+',' ',s).strip(' —')
    return (s[:1].upper()+s[1:]) if s else c
def nf_unit(c):
    if 'sex_ratio' in c: return 'F per 1000 M'
    if c in ('households_surveyed','women_15_49_interviewed','men_15_54_interviewed'): return 'count'
    if 'average_out_of_pocket' in c: return 'INR'
    return '%'
PINMEAN={'circlename':'India Post Circle — top admin unit (≈ state level)','regionname':'Postal Region — a group of divisions',
 'divisionname':'Postal Division — a group of post offices','officename':'Name of the post office',
 'pincode':'6-digit PIN: d1=region, d1–2=circle, d1–3=sorting district, last 3=delivery office','officetype':'Office type HO/SO/BO (here all BO = Branch Office)',
 'delivery':'Whether the office performs delivery','district':'Revenue district','statename':'State / UT',
 'latitude':'Office latitude (some NA)','longitude':'Office longitude (some NA)'}
FACMEAN={'unique_id':'Surrogate primary key (UUID) of the scraped record','source_types':'Provenance tag per evidence item (overture/dynamic/constant/mongo_facility)',
 'source_ids':'Source-record IDs, parallel to source_types','source_content_id':'FK to upstream source-content record (==content_table_id)',
 'name':'Facility name','organization_type':"Record class (always 'facility')",'content_table_id':'FK to content table (==source_content_id)',
 'phone_numbers':'All discovered phone numbers','officialPhone':'Primary/official phone','email':'Contact email',
 'websites':'All discovered URLs (site + social)','officialWebsite':'Primary official website','yearEstablished':'Year founded',
 'acceptsVolunteers':'Flag — accepts volunteers','facebookLink':'Facebook URL','address_line1':'Street address line 1',
 'address_line2':'Street address line 2','address_line3':'Street address line 3','address_city':'City (often a town/district)',
 'address_stateOrRegion':'State (sometimes a district mis-filed)','address_zipOrPostcode':'6-digit PIN (FK → pincode)',
 'address_country':'Country','address_countryCode':'ISO country code','countries':'Country list','facilityTypeId':'Facility class (hospital/clinic/dentist/doctor/farmacy)',
 'operatorTypeId':'Ownership (private/public)','affiliationTypeIds':'Affiliation/accreditation IDs','description':'Free-text summary',
 'area':'Locality / area name','numberDoctors':'Reported number of doctors','capacity':'Reported bed capacity',
 'specialties':'Clinical specialty codes (164-term taxonomy)','procedure':'Procedure/service statements','equipment':'Equipment statements',
 'capability':'Capability/claim statements','recency_of_page_update':'Recency signal of the source page','distinct_social_media_presence_count':'# distinct social platforms',
 'affiliated_staff_presence':'Flag — named staff present','custom_logo_presence':'Flag — has a custom logo','number_of_facts_about_the_organization':'# structured facts extracted',
 'post_metrics_most_recent_social_media_post_date':'Date of latest social post','post_metrics_post_count':'# social posts',
 'engagement_metrics_n_followers':'Social followers','engagement_metrics_n_likes':'Social likes','engagement_metrics_n_engagements':'Social engagements',
 'source':"Pipeline source (always 'kie')",'coordinates':'GeoJSON point {coordinates:[lon,lat]}','latitude':'Latitude (some corrupt/out-of-India)',
 'longitude':'Longitude (some corrupt/out-of-India)','cluster_id':'Entity-resolution key (dedupe across sources)','source_urls':'Source page URLs'}
dd=["## Consolidated Data Dictionary — every column & its meaning\n",
    "*Plain-English meaning of all 171 columns across the three tables. NFHS meanings are derived from the indicator names + NFHS-5 conventions (denominator = the population the % is computed over); see the thematic NFHS sections for fuller definitions.*\n"]
dd.append("\n### india_pincode.csv (11)\n| # | Column | Meaning | Type |\n|---|---|---|---|")
for i,c in enumerate(pc.columns): dd.append(f"| {i} | `{c}` | {PINMEAN.get(c,'—')} | {'geo' if c in ('latitude','longitude') else 'text'} |")
dd.append("\n### facilities.csv (51)\n| # | Column | Meaning | Type |\n|---|---|---|---|")
for i,c in enumerate(fc.columns):
    typ='json[]' if c in JSONCOLS else ('geo' if c in ('latitude','longitude','coordinates') else 'field')
    dd.append(f"| {i} | `{c}` | {FACMEAN.get(c,'—')} | {typ} |")
dd.append("\n### nfhs.csv (109)\n| # | Column | Meaning | Denominator | Unit |\n|---|---|---|---|---|")
for i,c in enumerate(nf.columns):
    if c=='district_name': mean,de,u='District name (identifier)','—','id'
    elif c=='state_ut': mean,de,u='State / UT (identifier)','—','id'
    elif c=='households_surveyed': mean,de,u='Households surveyed (sample size)','households','count'
    elif c=='women_15_49_interviewed': mean,de,u='Women 15–49 interviewed (sample size)','women 15–49','count'
    elif c=='men_15_54_interviewed': mean,de,u='Men 15–54 interviewed (sample size)','men 15–54','count'
    else: mean,de,u=gloss(c),denom(c),nf_unit(c)
    dd.append(f"| {i} | `{c}` | {mean} | {de} | {u} |")
open(f'{SEC}/05_data_dictionary.md','w').write('\n'.join(dd)+'\n')

# ---------------- (B) FIGURES ----------------
def save(fn): plt.tight_layout(); plt.savefig(f'{FIG}/{fn}',bbox_inches='tight'); plt.close()

# F1 correlation tiers
ind=nfc[[c for i,c in enumerate(nf.columns) if i>=5]]
cm=ind.corr().abs(); iu=np.triu(np.ones(cm.shape,bool),1); vals=cm.values[iu]; vals=vals[~np.isnan(vals)]
tiers=[('HIGH≥.6',(vals>=.6).sum()),('MED .4-.6',((vals>=.4)&(vals<.6)).sum()),
       ('LOW .2-.4',((vals>=.2)&(vals<.4)).sum()),('neg <.2',(vals<.2).sum())]
plt.figure(figsize=(5.2,3)); plt.bar([t[0] for t in tiers],[t[1] for t in tiers],
    color=['#c0392b','#e67e22','#f1c40f','#bdc3c7']); plt.ylabel('# variable pairs')
plt.title('NFHS correlation strength tiers'); [plt.text(i,t[1],str(t[1]),ha='center',va='bottom') for i,t in enumerate(tiers)]; save('corr_tiers.png')

# F2 heatmap of curated indicators
subs=[('Stunting','stunted'),('Wasting','are_wasted'),('Underweight ch','underweight_weight_for_age'),
 ('Sanitation','improved_sanitation'),('Clean fuel','clean_fuel'),('Electricity','hh_electricity'),
 ('Fem 10+ sch','10_or_more_years'),('Literacy','who_are_literate'),('Married<18','married_before_age_18'),
 ('Inst birth','institutional_birth_5y'),('C-section','births_delivered_by_csection'),('ANC4+','at_least_4_anc'),
 ('Full imm','fully_vaccinated_based_on_information_from_eit'),('Anaemia W','all_w15_49_who_are_anaemic'),
 ('Overweight W','who_are_overweight_obese'),('High BP W','w15_plus_with_high_bp_sys_gte_140'),
 ('High sugar W','w15_plus_with_high_or_very_high'),('Diarrhoea','prev_diarrhoea'),('Tobacco M','m15_plus_who_use_any_kind_of_tobacco'),
 ('Insurance','health_insurance')]
cols=[(lbl,[c for c in nf.columns if s in c][0]) for lbl,s in subs if [c for c in nf.columns if s in c]]
M=nfc[[c for _,c in cols]].corr()
plt.figure(figsize=(8.2,7)); im=plt.imshow(M.values,cmap='RdBu_r',vmin=-1,vmax=1)
plt.xticks(range(len(cols)),[l for l,_ in cols],rotation=90); plt.yticks(range(len(cols)),[l for l,_ in cols])
plt.colorbar(im,fraction=.046,pad=.04,label='Pearson r'); plt.title('Correlation heatmap — key NFHS indicators'); save('corr_heatmap.png')

# F3 causal scatters
pairs=[('improved_sanitation','stunted','Sanitation %','Stunting %'),
       ('10_or_more_years','married_before_age_18','Female 10+yr schooling %','Married <18 %'),
       ('at_least_4_anc','institutional_birth_5y','ANC 4+ visits %','Institutional birth %'),
       ('who_are_overweight_obese','w15_plus_with_high_bp_sys_gte_140','Women overweight %','Women high BP %')]
fig,ax=plt.subplots(2,2,figsize=(9,7))
for a,(xs,ys,xl,yl) in zip(ax.ravel(),pairs):
    x=C(xs); y=C(ys); m=x.notna()&y.notna(); x,y=x[m],y[m]
    a.scatter(x,y,s=14,alpha=.6,color='#2c3e50')
    b,a0=np.polyfit(x,y,1); xx=np.linspace(x.min(),x.max(),50); a.plot(xx,a0+b*xx,'r-')
    r=np.corrcoef(x,y)[0,1]; a.set_xlabel(xl); a.set_ylabel(yl); a.set_title(f'r = {r:+.2f}')
fig.suptitle('Curated relationships (district level)'); save('causal_scatters.png')

# F4 techniques
techs=[('Pearson',.507),('Spearman',.500),('Kendall',.350),('Distance',.485),('Partial\n(SES ctrl)',.250)]
plt.figure(figsize=(5.5,3)); plt.bar([t[0] for t in techs],[t[1] for t in techs],color='#16a085')
plt.ylabel('|coefficient|'); plt.title('sanitation ~ stunting: five techniques (national, n=706)'); plt.ylim(0,.7)
[plt.text(i,t[1],f"{t[1]:.2f}",ha='center',va='bottom') for i,t in enumerate(techs)]; save('corr_techniques.png')

# F5 distributions
di=[('Stunting','stunted'),('Wasting','are_wasted'),('Sanitation','improved_sanitation'),
    ('Inst birth','institutional_birth_5y'),('Full imm','fully_vaccinated_based_on_information_from_eit'),
    ('Anaemia W','all_w15_49_who_are_anaemic'),('Fem 10+ sch','10_or_more_years')]
data=[C(s).dropna() for _,s in di]
plt.figure(figsize=(8,3.6)); plt.boxplot(data,tick_labels=[l for l,_ in di],showmeans=True)
plt.xticks(rotation=30,ha='right'); plt.ylabel('% (district)'); plt.title('Distributions of key NFHS indicators'); save('nfhs_distributions.png')

# F6 suppression by theme
groups=[('Demographics',0,10),('Household',11,19),('Marriage/FP',20,35),('Maternal',36,52),
        ('Immunization',53,64),('Nutrition',65,84),('NCD/Anaemia',85,108)]
sup=[];sml=[]
for _,lo,hi in groups:
    cells=nf.iloc[:,lo:hi+1].astype(str).map(lambda s:s.strip())
    tot=cells.size
    sup.append(100*(cells=='*').values.sum()/tot)
    sml.append(100*cells.map(lambda s:s.startswith('(') and s.endswith(')')).values.sum()/tot)
x=np.arange(len(groups)); plt.figure(figsize=(7.5,3.3))
plt.bar(x-.2,sup,.4,label="suppressed '*'",color='#c0392b'); plt.bar(x+.2,sml,.4,label="small-sample '(x)'",color='#e67e22')
plt.xticks(x,[g[0] for g in groups],rotation=30,ha='right'); plt.ylabel('% of cells'); plt.legend(); plt.title('Missingness by theme (MNAR)'); save('suppression_by_theme.png')

# F7 capability grades
try:
    t=pd.read_csv(f'{ART}/facility_capability_trust.csv'); piv=t.pivot_table(index='capability',columns='grade',aggfunc='size',fill_value=0)
    order=['STRONG','PARTIAL','WEAK/SUSPICIOUS']; piv=piv[[c for c in order if c in piv.columns]]
    piv.plot(kind='barh',stacked=True,figsize=(8,3.6),color=['#27ae60','#f1c40f','#e74c3c'])
    plt.xlabel('# facility cells (excl. NO CLAIM)'); plt.title('Capability claims by trust grade'); plt.legend(fontsize=7); save('capability_grades.png')
except Exception as e: print('F7',e)

# F8 confidence distribution
try:
    cf=pd.read_csv(f'{ART}/facility_capability_confidence.csv'); cc=cf[cf['confidence']>0]['confidence']
    plt.figure(figsize=(6,3.2)); plt.hist(cc,bins=np.arange(0,101,10),color='#2980b9',edgecolor='white')
    for x0,c0 in [(30,'#e74c3c'),(50,'#e67e22'),(70,'#f1c40f'),(85,'#27ae60')]: plt.axvline(x0,ls='--',color=c0,lw=1)
    plt.xlabel('confidence score (0-100)'); plt.ylabel('# capability claims'); plt.title('Evidence-confidence distribution'); save('confidence_hist.png')
except Exception as e: print('F8',e)

# F9 facilities per state
vs=fc['address_stateOrRegion'].value_counts().head(14)
plt.figure(figsize=(7,3.6)); vs[::-1].plot(kind='barh',color='#8e44ad'); plt.xlabel('# sampled facilities'); plt.title('Sampled facilities per state'); save('facilities_per_state.png')

# F10 facilities fill-rate
fill=(fc.replace({'null':np.nan}).notna().mean()*100).sort_values()
plt.figure(figsize=(7,7)); fill.plot(kind='barh',color='#34495e'); plt.xlabel('% non-null'); plt.title('Facilities — field fill-rate (all 51 columns)'); save('facilities_fill.png')

print('figures:',len(os.listdir(FIG)))

# ---------------- (C) OVERVIEW + ASSEMBLE ----------------
overview="""## Overview & How to Read This Report

**What this is:** a complete, from-scratch understanding of three India health datasets — built before any RAG/ontology/causal modeling — covering every column, every unique value, full statistics, correlations with reasoning & confidence, a facility capability-trust engine, geographic gap analysis, and a causal-readiness blueprint.

> ✅ **Complete national data.** `nfhs5.csv` = 706 NFHS-5 district rows (36 states/UTs); `india_post.csv` = 165,627 post offices (full HO/PO/BO hierarchy, 749 districts); `facilities_hack.csv` = 10,088 facilities nationwide. The cross-dataset **join works**: ~86% of NFHS district names match the pincode directory, ~95% of facilities have a pincode in the directory, and ~80% map facility→pincode→district→NFHS. An integrated district table (`data/district_supply_demand.csv`, 706 districts: outcomes + supply) is included.

### The three datasets
| File | Rows×Cols | Grain | Role |
|---|---|---|---|
| `nfhs5.csv` | 706 × 109 | district | health **outcomes & behaviours** (demand) |
| `facilities_hack.csv` | 10,088 × 51 | facility | health **supply / infrastructure** |
| `india_post.csv` | 165,627 × 11 | post office | **geographic backbone** (pincode→district) |

### Keys
- **nfhs**: PK `(state_ut, district_name)` — ⚠️ no district code exists.
- **pincode**: PK `(officename, pincode)` — pincode alone is NOT unique (up to 5 offices share one).
- **facilities**: PK `unique_id`; `cluster_id` = entity-resolution key.
- **Join path**: `facilities.address_zipOrPostcode → pincode → (district,state) → nfhs`.

### The four planning questions this answers
1. **Can a facility do what it claims?** → capability trust grades + confidence badges.
2. **Are the care gaps real?** → trust-weighted gap analysis (real gap vs data-poor).
3. **Where should a patient/coordinator go?** → location+need search prototype.
4. **What must be fixed before planning?** → stewardship review queue + causal-readiness fixes.

### How to navigate
Use the sidebar. Start with the **Unique-Values Catalog** for the complete column inventory, then the NFHS dictionary sections, then Correlations (matrix → reasoning/confidence → better techniques), then the facility product layer, then the causal-readiness blueprint. Data artifacts (CSVs, the search engine `.py`) are in `data/`; figures in `figures/`.
"""
open(f'{SEC}/00_overview.md','w').write(overview)

ORDER=[('00_overview','Overview & How to Read This'),
('05_data_dictionary','Consolidated Data Dictionary — every column & meaning'),
('06_column_semantics_audit','Column Semantics & Unit Audit (validated vs data)'),
('07_value_codebook','Value-Level Codebook (what each value means)'),
('90_unique_values_catalog','Complete Unique-Values Catalog'),
('10_nfhs_g1_demographics','NFHS · Survey Design & Demographics'),
('11_nfhs_g2_household','NFHS · Household & Socioeconomic'),
('12_nfhs_g3_fp','NFHS · Marriage, Fertility & Family Planning'),
('13_nfhs_g4_maternal','NFHS · Maternal Health & Delivery'),
('14_nfhs_g5_immunization','NFHS · Child Immunization'),
('15_nfhs_g6_nutrition','NFHS · Child Illness, IYCF & Nutrition'),
('16_nfhs_g7_ncd','NFHS · Anaemia, NCDs & Substance Use'),
('20_pincode','Pincode Directory'),
('30_facilities_core','Facilities · Identity/Location/Classification'),
('31_facilities_enrichment','Facilities · Clinical/Social/Geo'),
('40_nfhs_correlations','Correlations · Matrix & Associations'),
('41_correlation_reasoning_confidence','Correlations · Reasoning, Causation & Confidence'),
('42_correlation_methods','Correlations · Better Techniques'),
('50_outliers','Outliers & Anomaly Register'),
('60_linkage','Cross-Dataset Linkage'),
('70_capability_trust','Capability Trust-Grading Engine'),
('71_geographic_gaps','Geographic Care-Gap Analysis'),
('72_search_prototype','Location + Need Search Prototype'),
('73_stewardship','Data-Quality Stewardship & Review Queue'),
('74_evidence_modeling','Evidence-Confidence Modeling'),
('75_bridge_roadmap','Supply↔Demand Bridge & Roadmap'),
('76_confidence_and_evidence','Confidence & Evidence Hardening'),
('80_data_prep_causal_readiness','Data-Prep & Causal-Readiness Blueprint'),
('81_retrieval_vs_eda','Retrieval vs EDA — Two Data Tracks'),
('82_causal_structure','Causal Structure Discovery (PC + GLASSO)'),
('83_bayesian_network','Bayesian Network & Interventional Reasoning'),
('84_effect_estimation','Causal Effect Estimation — What Survives Adjustment'),
('85_supply_demand_causal','Supply→Demand Causal Analysis'),
('86_sensitivity_did_triangulation','Sensitivity, Difference-in-Differences & Triangulation'),
('87_inference_fallback','Inference Under Missing Data — Trends, Probability & Fallback'),
('88_causal_robustness','Causal Robustness to the Urbanization Confounder'),
('89_pincode_supply','Pincode-Granular Supply & Access (neighbourhood deserts)'),
('91_ml_insights','Machine-Learning Insights — Prediction, Typology, Anomalies'),
('92_deep_learning','Deep Learning — Feature-Graph GNN'),
('94_penalized_regression','Statistical ML — Penalized Regression & Stability Selection'),
('95_hierarchical_models','Statistical ML — Hierarchical / Multilevel (Partial Pooling)'),
('96_gam_quantile_conformal','Statistical ML — GAM, Quantile Regression & Conformal Intervals'),
('97_geometric_gnn','Geometric Deep Learning — Spatial GAT / GraphSAGE'),
('98_spectral_spatial','Geometric DL — Spectral Embeddings & Spatial Spillover'),
('99_ensemble_solver','Unified Ensemble Solver — Best Predictor + Interpretable Rules'),
('93_insight_register','Insight Register (interim, ML)'),
('9A_solution_and_insights','★ The Solution — Answer Engine & Complete Insight Register')]
FIGMAP={'40':[('corr_tiers.png','Correlation strength tiers'),('corr_heatmap.png','Key-indicator correlation heatmap')],
'41':[('causal_scatters.png','Curated relationships with fit lines')],'42':[('corr_techniques.png','Five techniques, same pair')],
'15':[('nfhs_distributions.png','Distributions of key indicators')],'16':[('suppression_by_theme.png','Missingness by theme (MNAR)')],
'70':[('capability_grades.png','Capability claims by trust grade')],'76':[('confidence_hist.png','Confidence-score distribution')],
'71':[('facilities_per_state.png','Facilities per state (full data)')],'30':[('facilities_fill.png','Facilities field fill-rate')],
'82':[('causal_dag.png','Discovered causal structure (PC algorithm + GLASSO)')],'83':[('83_bayesian_network.png','Learned Bayesian network')],
'84':[('causal_effects.png','Effect size: naive vs confounder-adjusted')],'85':[('supply_demand_causal.png','Supply vs demand')],
'88':[('causal_robustness_urbanicity.png','Effects before vs after adding urbanicity')],'89':[('pincode_deserts.png','Intra-district supply deserts')],
'91':[('ml_feature_importance.png','What predicts each outcome (permutation importance)')],'92':[('gnn_vs_baseline.png','GNN vs baselines (test R²)')],
'94':[('stability_selection.png','Bootstrap selection frequency (robust drivers)')],'95':[('multilevel_shrinkage.png','Partial pooling: raw vs shrunk')],
'96':[('gam_quantile.png','Nonlinear dose-response & quantile slopes')],'97':[('gnn_geometric.png','Spatial GNN vs baselines (test R²)')],
'98':[('spectral_embedding.png','Spectral embedding — geography from connectivity')],'99':[('ensemble_leaderboard.png','Model leaderboard')]}
REASON={
'corr_tiers.png':"Of 5,356 indicator pairs, only 149 are strongly correlated and most of those are definitional (the same thing measured twice). <b>Why it matters:</b> don't chase every correlation — real signal lives in the medium band, and a small/biased sample inflates this count (the 100-row sample showed 341). <b>Takeaway:</b> be skeptical of 'strong' correlations.",
'corr_heatmap.png':"Red = two indicators rise together; blue = one rises as the other falls. <b>Reasoning:</b> development indicators (sanitation, schooling, institutional birth) cluster red — districts that do well on one tend to do well on all (shared wealth). Sanitation↔stunting is blue: better toilets, less stunting. <b>Caveat:</b> this is association — wealth drives many of these together, so it is NOT proof of cause.",
'causal_scatters.png':"Each dot is one district; a downward line means 'as X goes up, Y goes down'. <b>Cause-effect story:</b> more female schooling → less child marriage; more sanitation → less stunting; more ANC visits → more hospital births. <b>Caveat:</b> these are real patterns but confounded by wealth — the next chart shows how much shrinks once we adjust.",
'corr_techniques.png':"The same sanitation→stunting relationship measured five ways. <b>The point:</b> the bar SHRINKS from −0.51 (raw) to −0.25 (after removing wealth/schooling) — meaning <b>about half the apparent 'effect' was really just confounding</b>. This single picture is why correlation ≠ causation, and why we control for confounders.",
'nfhs_distributions.png':"Each box = the middle 50% of districts; the line inside = the median. <b>Reasoning:</b> indicators like stunting span ~13% to ~60% across districts — national averages hide local crises. <b>Why it matters:</b> health planning must target districts, not the country average.",
'suppression_by_theme.png':"Bars show how much data is hidden ('*' = too few people surveyed) by topic. <b>Reasoning:</b> NCD/nutrition/male topics have more gaps, and those gaps cluster in small, remote, poorer districts — so the missing data is NOT random. <b>Consequence:</b> naive analysis would silently drop the neediest districts and bias every result.",
'capability_grades.png':"For each capability, green = well-evidenced claims, yellow = partial, red = weak/suspicious. <b>Reasoning:</b> maternity is the best-evidenced service; oncology and dialysis carry the most suspicious claims (e.g. small clinics claiming cancer care). <b>Takeaway:</b> trust a maternity claim far more than an oncology claim from the same source.",
'confidence_hist.png':"How confident we are in each facility's capability claim (0–100). <b>Reasoning:</b> ~10,000 claims are High/Very-High confidence (safe to route patients there); the large low-confidence tail rests on a single weak mention and needs human verification before use. <b>Why:</b> a number you can't trust is worse than no number.",
'facilities_per_state.png':"Where the scraped facility data is concentrated. <b>Reasoning:</b> Maharashtra/Gujarat/etc. dominate the dataset — but this reflects WEB VISIBILITY, not where care actually exists. <b>Caveat:</b> a state with few facilities here may be under-scraped, not under-served — never read absence as a real care gap.",
'facilities_fill.png':"How complete each facility field is. <b>Reasoning:</b> identity/contact/location fields are nearly full, but clinical fields (capacity, number of doctors) are mostly empty. <b>Takeaway:</b> trust a facility's location and name; treat its bed-count or doctor-count as missing, not zero.",
'causal_dag.png':"Arrows show where the DATA says causation COULD flow — discovered by algorithm, not assumed. <b>Key reasoning:</b> the skeleton (which variables connect) is stable across 100 resamples, but the arrow DIRECTIONS are unreliable because this is a single-time-point snapshot with no 'before/after'. <b>Takeaway:</b> trust 'these are connected' far more than 'this causes that' — and supply (facilities) sits almost disconnected from health outcomes once you account for development.",
'83_bayesian_network.png':"A probabilistic map of how indicators depend on each other. <b>Why it matters:</b> it lets us ask <i>do(X)</i> — 'if we SET sanitation high, what happens to stunting?' — not just observe a correlation. After adjusting for schooling & age-structure, ~57% of the crude sanitation–stunting gap survives, so part is real and part was confounding.",
'causal_effects.png':"The single clearest correlation-vs-causation picture. Each pair shows the raw effect vs the effect after removing confounders. <b>Bars that COLLAPSE</b> (sanitation→stunting, −71%) were mostly confounding — the wealth gradient, not sanitation itself. <b>Bars that SURVIVE</b> (female-schooling→child-marriage, overweight→blood-pressure) are likely-causal across all four methods. <b>Takeaway:</b> a strong correlation is not a strong cause — only adjustment tells you which is which.",
'supply_demand_causal.png':"Does having more facilities in a district actually improve outcomes? <b>Reasoning:</b> after adjusting for wealth/schooling, facility counts are weakly linked to outcomes — partly because supply is web-scraped (visibility bias) and facilities LOCATE where demand already is (reverse causation). <b>Takeaway:</b> 'more facilities' on paper ≠ 'better outcomes'; read this as suggestive, not causal.",
'causal_robustness_urbanicity.png':"We added 'urbanicity' (built from pincodes) as a new confounder and re-checked each effect. <b>Surprise:</b> it barely moved them — state fixed-effects had already captured the urban/rural difference — and the likely-causal effects (schooling→child-marriage, overweight→BP) still survive. <b>Takeaway:</b> the causal conclusions are robust to this extra control.",
'pincode_deserts.png':"How a district's facilities spread across its pincodes. <b>Reasoning:</b> most districts leave >80% of pincodes facility-free and cram most facilities into one pincode — so a 'served' district can still strand whole neighbourhoods. <b>Takeaway:</b> 'where do I go?' must be answered at pincode resolution, not district.",
'ml_feature_importance.png':"What best PREDICTS each outcome (not what causes it). <b>Reasoning:</b> stunting tracks women-overweight & age-structure; institutional birth tracks age-structure & ANC visits. <b>Takeaway:</b> useful for targeting/prediction — but importance ≠ cause (that's what the causal sections are for).",
'gnn_vs_baseline.png':"Does a graph neural network beat simple models at predicting outcomes? <b>Reasoning:</b> here it roughly ties them, because the inputs are already smooth across similar districts so a plain model captures the signal. <b>Takeaway:</b> fancier ≠ better on this data — prefer the simple, explainable model.",
'stability_selection.png':"How often each driver is selected across 200 bootstrap resamples. <b>Reasoning:</b> drivers chosen >80% of the time are robust; unstable ones are usually interchangeable with a correlated twin (e.g. schooling vs literacy). <b>Takeaway:</b> trust the consistently-selected drivers, not a single fit.",
'multilevel_shrinkage.png':"Small states with few districts get pulled toward their region's average; big states stay put. <b>Reasoning:</b> a 1-district estimate is noisy, so we blend it with context (borrowing strength) — the principled way to answer for data-poor areas. <b>Takeaway:</b> this is the statistically-optimal version of the 'fall back to state' rule.",
'gam_quantile.png':"Top: sanitation's effect on stunting is a straight line — no plateau, so investment keeps paying off. Bottom: female-schooling protects MORE in the worst-off districts. <b>Takeaway:</b> drivers act differently across the distribution — target the high-burden tail.",
'gnn_geometric.png':"A spatial graph neural network (using real geography) vs simple models for predicting stunting. <b>Reasoning:</b> it ties Ridge — because sanitation/schooling are already spatially clustered, so the geographic signal is mostly already in the features. <b>Honest takeaway:</b> the spatial net doesn't beat the simple model here, but the spatial structure is real (see spillover).",
'spectral_embedding.png':"The district graph alone reconstructs India's map, and reveals a high-stunting central corridor. <b>Reasoning:</b> neighbouring districts strongly resemble each other (spillover β=+0.59), so health clusters geographically. <b>Takeaway:</b> plan by contiguous region (central plateau & eastern plains are the worst), not isolated districts.",
'ensemble_leaderboard.png':"Models compared head-to-head on the same cross-validation. <b>Reasoning:</b> the stacked ensemble barely edges a single RandomForest. <b>Takeaway:</b> a simple, interpretable model is the practical choice — complexity didn't pay, which is itself a useful finding.",
}

master=[]; bodies=[]; toc=[]
for key,title in ORDER:
    p=f'{SEC}/{key}.md'
    if not os.path.exists(p): continue
    text=open(p).read(); master.append(f"\n\n---\n\n# {title}\n\n"+text)
    figs=''.join(f'<figure><img src="figures/{f}" alt="{cap}"><figcaption>{cap}</figcaption><div class="reason"><b>📊 How to read this &amp; why it matters</b><br>{REASON.get(f,"")}</div></figure>' for f,cap in FIGMAP.get(key.split('_')[0],[]))
    body=mdlib.markdown(text,extensions=['tables','fenced_code','sane_lists'])
    # mermaid: convert fenced code to div + unescape
    def merm(m):
        c=m.group(1).replace('&gt;','>').replace('&lt;','<').replace('&amp;','&').replace('&quot;','"')
        return f'<div class="mermaid">{c}</div>'
    body=re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>',merm,body,flags=re.S)
    bodies.append(f'<section id="{key}"><h2>{_html.escape(title)}</h2>{figs}{body}</section>')
    toc.append(f'<li><a href="#{key}">{_html.escape(title)}</a></li>')

open(f'{BASE}/MASTER.md','w').write("# DAS_HACK — India Health Data: Complete Analysis\n"+''.join(master))

HTML=f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>DAS_HACK — India Health Data Analysis</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script><script>try{{mermaid.initialize({{startOnLoad:true}});}}catch(e){{}}</script>
<style>
:root{{--accent:#1a5276}}*{{box-sizing:border-box}}body{{margin:0;font:15px/1.6 -apple-system,Segoe UI,Roboto,Helvetica,Arial;color:#1d2733;background:#f4f6f8}}
#wrap{{display:flex}}nav{{position:sticky;top:0;height:100vh;width:300px;overflow:auto;background:#0e2233;color:#cdd9e5;padding:18px 14px;flex:none}}
nav h1{{font-size:16px;color:#fff;margin:0 0 4px}}nav .sub{{font-size:11px;color:#7f93a6;margin-bottom:14px}}
nav ol{{list-style:none;padding:0;margin:0;counter-reset:s}}nav li{{counter-increment:s;margin:1px 0}}
nav a{{color:#cdd9e5;text-decoration:none;font-size:12.5px;display:block;padding:5px 8px;border-radius:6px}}
nav a:before{{content:counter(s)". ";color:#5b7387}}nav a:hover{{background:#16344c;color:#fff}}
main{{flex:1;max-width:1000px;margin:0 auto;padding:30px 42px}}
section{{background:#fff;border:1px solid #e3e8ee;border-radius:12px;padding:24px 30px;margin:0 0 26px;box-shadow:0 1px 3px rgba(0,0,0,.04)}}
h2{{color:var(--accent);border-bottom:2px solid #eaeff4;padding-bottom:8px;margin-top:0}}h3{{color:#21618c}}
table{{border-collapse:collapse;width:100%;margin:14px 0;font-size:13px;display:block;overflow-x:auto}}
th,td{{border:1px solid #dfe6ee;padding:6px 9px;text-align:left;vertical-align:top}}th{{background:#eef3f8}}tr:nth-child(even) td{{background:#fafcfe}}
code{{background:#eef1f4;padding:1px 5px;border-radius:4px;font-size:12.5px}}pre{{background:#0e2233;color:#dbe7f0;padding:12px;border-radius:8px;overflow:auto;font-size:12.5px}}pre code{{background:none;color:inherit}}
blockquote{{border-left:4px solid #e67e22;background:#fff8f0;margin:12px 0;padding:8px 14px;color:#7a4a12}}
figure{{margin:16px 0;text-align:center}}figure img{{max-width:100%;border:1px solid #e3e8ee;border-radius:8px}}figcaption{{font-size:12px;color:#6b7a88;margin-top:4px;font-style:italic}}
.reason{{background:#eef6ff;border-left:4px solid #2e86c1;padding:10px 14px;margin:8px 0 4px;font-size:13.5px;text-align:left;color:#1d3a52;line-height:1.55}}
.banner{{background:linear-gradient(135deg,#1a5276,#2e86c1);color:#fff;padding:18px 22px;border-radius:12px;margin-bottom:22px}}
.banner h1{{margin:0 0 4px;font-size:22px}}.banner p{{margin:0;opacity:.92;font-size:13px}}
</style></head><body><div id=wrap>
<nav><h1>DAS_HACK</h1><div class=sub>India Health Data · complete analysis</div><ol>{''.join(toc)}</ol></nav>
<main><div class=banner><h1>India Health Data — Complete Analysis</h1>
<p>NFHS-5 · India Post Pincodes · Health Facilities &nbsp;|&nbsp; data dictionary · unique values · statistics · correlations · trust &amp; confidence · causal-readiness</p></div>
{''.join(bodies)}
<p style="color:#90a0ad;font-size:12px;text-align:center;margin:30px">Generated by build_report.py · figures in <code>figures/</code> · data artifacts in <code>data/</code> · full markdown in <code>MASTER.md</code></p>
</main></div></body></html>"""
open(f'{BASE}/report.html','w').write(HTML)

# README + refresh markdown copies
readme="""# DAS_HACK — India Health Data: Complete Analysis

Open **`report.html`** in a browser for the full browsable report (sidebar nav, tables, graphs).

## Contents
- `report.html` — complete styled HTML report (all sections + figures)
- `MASTER.md` — same content as a single Markdown file
- `markdown/` — each section as an individual `.md`
- `figures/` — all generated charts (PNG)
- `data/` — reusable artifacts: trust grades, hardened grades, confidence scores, region gaps, correlation pairs, the search engine (`facility_search.py`), and the build scripts
- `build_report.py` — regenerates catalog + figures + report

## ⚠️ Caveat
All three CSVs are the **first 100 rows** (samples) of larger datasets and barely share join keys. Statistics are sample figures; design for the full national downloads.
"""
open(f'{BASE}/README.md','w').write(readme)
os.system(f'cp {SEC}/*.md {BASE}/markdown/ 2>/dev/null')
print('report.html bytes:',os.path.getsize(f'{BASE}/report.html'))
print('MASTER.md bytes:',os.path.getsize(f'{BASE}/MASTER.md'))
print('sections in report:',len(bodies))
