#!/usr/bin/env python
"""Enrich the analytic table with pincode-derived features: urbanization proxy + intra-district supply inequality."""
import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
DL='/Users/koushik/Downloads'; ART='/Users/koushik/Desktop/health_analysis_outputs'
v1=pd.read_csv(f'{ART}/causal_analytic_table.csv')
pc=pd.read_csv(f'{DL}/india_post.csv',dtype=str); fc=pd.read_csv(f'{DL}/facilities_hack.csv',dtype=str)
def normst(s):
    s=str(s).strip().upper().replace(' AND ',' & '); return s.replace('NCT OF DELHI','DELHI').replace('ISLANDS','').strip()
def normd(s): return str(s).strip().upper()
def gini(x):
    x=np.sort(np.asarray(x,float)); n=len(x)
    if n==0 or x.sum()==0: return np.nan
    return (2*np.sum((np.arange(1,n+1))*x)/(n*x.sum()))-(n+1)/n

pc['_s']=pc['statename'].map(normst); pc['_d']=pc['district'].map(normd)
# urbanization proxy + office structure per (state,district)
urb=pc.groupby(['_s','_d']).agg(n_pincodes=('pincode','nunique'),n_offices=('officename','size'),
     n_HO=('officetype',lambda s:(s=='HO').sum()),n_BO=('officetype',lambda s:(s=='BO').sum())).reset_index()
urb['bo_share']=100*urb['n_BO']/urb['n_offices']          # high = rural
urb['urbanicity']=100-urb['bo_share']                      # high = urban (the confounder)

# facilities -> pincode -> district; intra-district supply inequality
fz=fc['address_zipOrPostcode'].astype(str).str.extract(r'(\d{6})')[0]
pin2sd=pc.drop_duplicates('pincode').set_index(pc.drop_duplicates('pincode')['pincode'].astype(str).str.strip())[['_s','_d']]
fac_pin=pd.DataFrame({'pin':fz}).dropna()
fac_pin=fac_pin.join(pin2sd,on='pin')
fac_per_pin=fac_pin.groupby(['_s','_d','pin']).size().rename('nf').reset_index()
# for each district: distribution of facilities across ITS pincodes (incl zero-facility pincodes)
allpins=pc[['_s','_d','pincode']].drop_duplicates()
m=allpins.merge(fac_per_pin,left_on=['_s','_d','pincode'],right_on=['_s','_d','pin'],how='left')
m['nf']=m['nf'].fillna(0)
def dstats(g):
    nf=g['nf'].values
    return pd.Series({'n_pincodes_d':len(nf),'pins_with_fac':int((nf>0).sum()),
        'pct_zero_pins':100*float((nf==0).mean()),'supply_gini':gini(nf) if nf.sum()>0 else np.nan,
        'top_pin_share':100*nf.max()/nf.sum() if nf.sum()>0 else np.nan})
ineq=m.groupby(['_s','_d']).apply(dstats).reset_index()

# merge onto v1
v1['_s']=v1['state'].map(normst); v1['_d']=v1['district'].map(normd)
v2=v1.merge(urb[['_s','_d','n_pincodes','n_offices','bo_share','urbanicity']],on=['_s','_d'],how='left')
v2=v2.merge(ineq[['_s','_d','pins_with_fac','pct_zero_pins','supply_gini','top_pin_share']],on=['_s','_d'],how='left')
v2=v2.drop(columns=['_s','_d'])
v2.to_csv(f'{ART}/causal_analytic_table_v2.csv',index=False)
print('v2:',v2.shape,'| new cols: urbanicity,bo_share,n_pincodes,n_offices,pins_with_fac,pct_zero_pins,supply_gini,top_pin_share')
print('urbanicity coverage:',int(v2['urbanicity'].notna().sum()),'/',len(v2))
# quick check: does urbanicity correlate with sanitation & stunting (i.e. is it a real confounder?)
from scipy import stats
for t in ['sanitation','stunting','fem_school10']:
    d=v2[['urbanicity',t]].dropna(); r,p=stats.pearsonr(d['urbanicity'],d[t])
    print(f'  urbanicity ~ {t}: r={r:+.2f} (p={p:.1e})  -> {"confounder candidate" if abs(r)>0.2 else "weak"}')
