#!/usr/bin/env python
"""Recover district centroids (for geometric deep learning) and test spatial autocorrelation."""
import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
DL='/Users/koushik/Downloads'; ART='/Users/koushik/Desktop/health_analysis_outputs'
pc=pd.read_csv(f'{DL}/india_post.csv',dtype=str); fc=pd.read_csv(f'{DL}/facilities_hack.csv',dtype=str)
v2=pd.read_csv(f'{ART}/causal_analytic_table_v2.csv')
def normst(s):
    s=str(s).strip().upper().replace(' AND ',' & '); return s.replace('NCT OF DELHI','DELHI').replace('ISLANDS','').strip()
def normd(s): return str(s).strip().upper()

def fix_coord(v, lo, hi):
    try: x=float(v)
    except: return np.nan
    if lo<=x<=hi: return x
    ax=abs(x)
    for k in range(1,10):                       # rescale misplaced decimals (e.g. 233643145 -> 23.36)
        y=ax/(10**k)
        if lo<=y<=hi: return y
    return np.nan

# --- facility-based centroid (coords are mostly valid) ---
flat=fc['latitude'].map(lambda v: fix_coord(v,6,37)); flon=fc['longitude'].map(lambda v: fix_coord(v,68,98))
fz=fc['address_zipOrPostcode'].astype(str).str.extract(r'(\d{6})')[0]
pin2sd=pc.drop_duplicates('pincode').assign(P=pc.drop_duplicates('pincode')['pincode'].astype(str).str.strip())
pin2s=pin2sd.set_index('P')['statename'].map(normst); pin2d=pin2sd.set_index('P')['district'].map(normd)
fdf=pd.DataFrame({'lat':flat,'lon':flon,'_s':fz.map(pin2s),'_d':fz.map(pin2d)}).dropna()
fac_cent=fdf.groupby(['_s','_d']).agg(lat=('lat','median'),lon=('lon','median'),nfac=('lat','size')).reset_index()
fac_cent['src']='facility'

# --- pincode-based centroid (clean then median) as fallback ---
pc['_lat']=pc['latitude'].map(lambda v: fix_coord(v,6,37)); pc['_lon']=pc['longitude'].map(lambda v: fix_coord(v,68,98))
pc['_s']=pc['statename'].map(normst); pc['_d']=pc['district'].map(normd)
pin_cent=pc.dropna(subset=['_lat','_lon']).groupby(['_s','_d']).agg(lat=('_lat','median'),lon=('_lon','median')).reset_index()
pin_cent['src']='pincode'

# combine: prefer facility centroid (>=3 facilities), else pincode
geo=fac_cent[fac_cent['nfac']>=3][['_s','_d','lat','lon','src']]
have=set(zip(geo['_s'],geo['_d']))
add=pin_cent[~pin_cent.set_index(['_s','_d']).index.isin(have)]
geo=pd.concat([geo,add[['_s','_d','lat','lon','src']]],ignore_index=True)
print(f"district centroids: {len(geo)} (facility-based {(geo.src=='facility').sum()}, pincode-based {(geo.src=='pincode').sum()})")
print(f"  pincode coords recovered: {pc['_lat'].notna().sum()}/{len(pc)} ({100*pc['_lat'].notna().mean():.0f}%) after rescaling")

# merge centroid into v2 keys
v2['_s']=v2['state'].map(normst); v2['_d']=v2['district'].map(normd)
g=v2.merge(geo,on=['_s','_d'],how='left')
covered=g['lat'].notna().sum()
print(f"  districts in analytic table with a centroid: {covered}/{len(v2)}")
geo_out=g[['state','district','lat','lon','src','stunting','sanitation','fem_school10','urbanicity','inst_birth']]
geo_out.to_csv(f'{ART}/district_geo.csv',index=False)

# --- Moran's I: is there spatial autocorrelation? (justifies geometric DL) ---
from sklearn.neighbors import NearestNeighbors
sub=g.dropna(subset=['lat','lon','stunting']).reset_index(drop=True)
XY=sub[['lat','lon']].values
nn=NearestNeighbors(n_neighbors=9).fit(XY); _,idx=nn.kneighbors(XY)
n=len(sub); W=np.zeros((n,n))
for i in range(n):
    for j in idx[i,1:]: W[i,j]=1
W=W/W.sum(1,keepdims=True)
def moran(x):
    z=(x-x.mean()); return float((z@(W@z))/(z@z))
def moran_p(x,B=199):
    obs=moran(x); cnt=1
    for b in range(B):
        cnt+=moran(np.random.permutation(x))>=obs
    return obs,cnt/(B+1)
np.random.seed(0)
for v in ['stunting','sanitation','fem_school10','inst_birth','urbanicity']:
    if v in sub:
        I,p=moran_p(sub[v].values); print(f"  Moran's I [{v:13s}] = {I:+.2f} (perm p={p:.3f}) -> {'SPATIALLY CLUSTERED' if I>0.1 and p<0.05 else 'weak'}")
print("-> positive Moran's I means neighbouring districts resemble each other => geometric/spatial DL is justified.")
PY