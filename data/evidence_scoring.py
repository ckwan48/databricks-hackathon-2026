"""Evidence-confidence scoring for facilities.csv (national sample, first 100 rows).
Run: /tmp/dataenv/bin/python evidence_scoring.py
Reads /Users/koushik/Downloads/facilities.csv, writes facility_evidence_scores.csv.
"""
import pandas as pd, json, numpy as np

SRC = '/Users/koushik/Downloads/facilities.csv'
OUT = '/Users/koushik/Desktop/health_analysis_outputs/facility_evidence_scores.csv'
REF = pd.Timestamp('2026-06-15')          # "today" per run context
HALF_LIFE_DAYS = 540                       # 18-month confidence half-life

# Source-reliability weights. mongo_facility = curated facility master (most trusted);
# constant = stable scraped attributes; overture = open map basemap (broad, noisy);
# dynamic = volatile scraped/social signals (lowest standalone reliability).
WEIGHTS = {'mongo_facility': 1.00, 'constant': 0.85, 'overture': 0.70, 'dynamic': 0.50}

def parse_arr(x):
    if pd.isna(x) or str(x).strip().lower() == 'null':
        return []
    try:
        v = json.loads(x)
        if isinstance(v, list):
            return [e for e in v if e is not None and str(e).lower() != 'null']
        return [] if v is None else [v]
    except Exception:
        return []

def filled(x):
    return not (pd.isna(x) or str(x).strip().lower() == 'null')

def main():
    df = pd.read_csv(SRC)

    df['n_src_types'] = df['source_types'].map(lambda x: len(set(parse_arr(x))))
    df['src_quality'] = df['source_types'].map(
        lambda x: float(np.mean([WEIGHTS.get(t, 0.4) for t in set(parse_arr(x))])) if parse_arr(x) else 0.0)

    # A. key-field fill (35 pts)
    fill_fields = ['officialPhone','officialWebsite','email','address_line1','address_city',
                   'address_zipOrPostcode','facilityTypeId','operatorTypeId','description','yearEstablished']
    df['c_fill'] = df.apply(lambda r: sum(filled(r[f]) for f in fill_fields)/len(fill_fields), axis=1) * 35

    # B. clinical evidence depth (25 pts), distinct items across 4 arrays, capped at 60
    df['n_evidence'] = df[['specialties','procedure','equipment','capability']].apply(
        lambda r: sum(len(set(parse_arr(v))) for v in r), axis=1)
    df['c_evid'] = (df['n_evidence'].clip(upper=60)/60) * 25

    # C. source diversity (20 pts)
    df['c_div'] = (df['n_src_types']/4) * 20

    # D. contact verifiability + geo validity (10 pts)
    lat = pd.to_numeric(df['latitude'], errors='coerce'); lon = pd.to_numeric(df['longitude'], errors='coerce')
    df['geo_ok'] = (lat.between(6,37)) & (lon.between(68,98))
    def contact(r):
        s = 0.0
        if filled(r['officialPhone']) or filled(r['phone_numbers']): s += 0.4
        if filled(r['officialWebsite']) or filled(r['websites']): s += 0.3
        if filled(r['email']): s += 0.3
        return s
    df['c_contact'] = (df.apply(contact, axis=1)*0.7 + df['geo_ok'].astype(float)*0.3) * 10

    # E. social corroboration (10 pts)
    smp = pd.to_numeric(df['distinct_social_media_presence_count'], errors='coerce').fillna(0)
    fol = pd.to_numeric(df['engagement_metrics_n_followers'], errors='coerce').fillna(0)
    df['c_social'] = ((smp.clip(upper=6)/6)*0.5 + (np.log1p(fol)/np.log1p(15000)).clip(upper=1)*0.5) * 10

    df['completeness'] = (df['c_fill']+df['c_evid']+df['c_div']+df['c_contact']+df['c_social']).round(1)

    # Recency decay -> confidence
    page_age = (REF - pd.to_datetime(df['recency_of_page_update'], errors='coerce')).dt.days
    df['page_age_days'] = page_age
    df['post_age_days'] = (REF - pd.to_datetime(df['post_metrics_most_recent_social_media_post_date'], errors='coerce')).dt.days
    df['recency_factor'] = np.where(page_age.notna(), 0.5**(page_age/HALF_LIFE_DAYS), np.nan)
    # confidence = completeness scaled by source reliability (recency applied where parseable)
    norm_q = df['src_quality']/df['src_quality'].replace(0, np.nan).max()
    df['confidence'] = (df['completeness'] * norm_q).round(1)

    cols = ['unique_id','name','address_city','address_stateOrRegion','facilityTypeId','operatorTypeId',
            'n_src_types','src_quality','n_evidence','distinct_social_media_presence_count',
            'engagement_metrics_n_followers','geo_ok','page_age_days','post_age_days',
            'c_fill','c_evid','c_div','c_contact','c_social','completeness','recency_factor','confidence']
    out = df[cols].copy()
    out['src_quality'] = out['src_quality'].round(3); out['recency_factor'] = out['recency_factor'].round(3)
    for c in ['c_fill','c_evid','c_div','c_contact','c_social']:
        out[c] = out[c].round(1)
    out.sort_values('completeness', ascending=False).to_csv(OUT, index=False)
    print('wrote', OUT, len(out), 'rows')

if __name__ == '__main__':
    main()
