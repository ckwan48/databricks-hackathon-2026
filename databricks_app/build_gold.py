#!/usr/bin/env python
"""Build the gold tables for the 4 hackathon tracks directly on the Databricks SQL Warehouse.
Reads the Marketplace catalog (read-only), writes to workspace.virtue_gold."""
from databricks.sdk.core import Config
from databricks import sql

WID = "c5e7e7089978bd43"
SRC = "databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset"
GOLD = "workspace.virtue_gold"

cfg = Config(profile="DEFAULT")
conn = sql.connect(server_hostname=cfg.host.replace("https://","").rstrip("/"),
                   http_path=f"/sql/1.0/warehouses/{WID}", access_token=cfg.token)
cur = conn.cursor()
def run(label, q):
    cur.execute(q); print("✓", label)

# ---- SILVER: clean facility (parse JSON, dedup cluster_id, district via PIN, keep raw text) ----
run("silver_facility", f"""
CREATE OR REPLACE TABLE {GOLD}.silver_facility AS
WITH pin AS (
  SELECT cast(pincode AS string) AS pincode, max(upper(trim(district))) AS district_n, max(upper(trim(statename))) AS state_n
  FROM {SRC}.india_post_pincode_directory GROUP BY cast(pincode AS string)),
base AS (
  SELECT *,
    nullif(regexp_extract(address_zipOrPostcode,'([0-9]{{6}})',1),'') AS zip6,
    lower(replace(coalesce(facilityTypeId,''),'farmacy','pharmacy')) AS ftype,
    lower(concat_ws(' ', coalesce(description,''),
       coalesce(array_join(from_json(capability,'array<string>'),' '),''),
       coalesce(array_join(from_json(procedure,'array<string>'),' '),''),
       coalesce(array_join(from_json(equipment,'array<string>'),' '),''))) AS evidence_text,
    lower(coalesce(array_join(from_json(specialties,'array<string>'),' '),'')) AS spec_text,
    size(coalesce(array_distinct(from_json(source_types,'array<string>')),array())) AS n_sources,
    coalesce(array_join(slice(from_json(source_urls,'array<string>'),1,8),' | '),'') AS source_urls_str,
    coalesce(array_join(array_distinct(from_json(source_types,'array<string>')),', '),'') AS source_types_str,
    row_number() OVER (PARTITION BY cluster_id ORDER BY unique_id) AS rk
  FROM {SRC}.facilities)
SELECT b.*, p.district_n, p.state_n
FROM base b LEFT JOIN pin p ON b.zip6 = p.pincode
WHERE b.rk = 1
""")

# ---- GOLD Track 1: facility x capability trust (evidence + confidence) ----
CAPS = {
 # ---- 7 high-stakes acute capabilities ----
 'ICU':       ('criticalcaremedicine', r'icu|intensive care|critical care|ventilator|central oxygen', True),
 'NICU':      ('neonatologyperinatalmedicine', r'nicu|neonat|radiant warmer|phototherapy', True),
 'maternity': ('gynecologyandobstetrics|reproductiveendocrinologyandinfertility', r'maternit|obstetric|gyn[ae]ecolog|labour|delivery|antenatal|ivf|iui', False),
 'emergency': ('emergencymedicine', r'emergency|casualty|24/?7|ambulance|trauma', False),
 'oncology':  ('medicaloncology|surgicaloncology|radiationoncology|breastimaging', r'oncolog|cancer|chemotherap|radiotherap|mammogra|tumou?r', True),
 'trauma':    ('orthopedicsurgery|traumasurgery', r'trauma|fracture|polytrauma', True),
 'dialysis':  ('nephrology', r'dialysis|renal|haemodialysis|nephrolog', True),
 # ---- broader clinical capabilities across the complete specialty vocabulary ----
 'cardiology':('cardiology|cardiacsurgery|cardiothoracicsurgery|cardiacelectrophysiology', r'cardiac|cardiolog|\bheart\b|angiograph|angioplast|cath ?lab|echocardiograph|bypass|\bstent', True),
 'neurology': ('neurology|neurosurgery|neuroradiology', r'neurolog|neurosurg|stroke|epilep|\bbrain\b|spine surgery', True),
 'pediatrics':('pediatrics|paediatrics|pediatricsurgery|pediatriccardiology', r'p[ae]diatric|child health|well baby', False),
 'ophthalmology':('ophthalmology', r'ophthalmolog|\beye\b|cataract|retina|lasik|glaucoma', False),
 'dentistry': ('dentistry|endodontics|orthodontics|periodontics|prosthodontics|oralandmaxillofacialsurgery', r'dental|dentist|\btooth\b|teeth|orthodont|root canal', False),
 'orthopedics':('orthopedicsurgery', r'joint replacement|arthroscop|arthroplast|knee replacement|hip replacement|orthop[ae]dic', False),
 'gastroenterology':('gastroenterology|hepatology', r'gastroenterolog|endoscop|colonoscop|\bliver\b|hepatolog', False),
 'urology':   ('urology', r'urolog|kidney stone|prostate|cystoscop|lithotrips', False),
 'dermatology':('dermatology', r'dermatolog|\bskin\b|cosmetolog', False),
 'ent':       ('otolaryngology', r'otolaryngolog|ear.?nose.?throat|\bent\b|sinus|tonsil|audiolog', False),
 'radiology': ('radiology|breastimaging|nuclearmedicine', r'radiolog|\bmri\b|ct scan|ultrasound|x-?ray|sonograph', False),
 'general surgery':('generalsurgery', r'general surgery|laparoscop|hernia|appendic|cholecystect', False),
 'pulmonology':('pulmonarymedicine|pulmonology|respiratorymedicine', r'pulmonolog|respiratory medicine|asthma|\bcopd\b', True),
 'psychiatry':('psychiatry', r'psychiatr|mental health|de-?addiction', False),
 'endocrinology':('endocrinologyanddiabetesandmetabolism|endocrinology', r'endocrinolog|diabetolog|thyroid', False),
}
selects = []
for cap,(spec,kw,acute) in CAPS.items():
    contradiction = (f"(ftype IN ('clinic','dentist','doctor','pharmacy') AND NOT (spec_text rlike '{spec}') AND (evidence_text rlike '{kw}'))"
                     if acute else "false")
    selects.append(f"""
SELECT unique_id, cluster_id, name, ftype, address_city, address_stateOrRegion, district_n,
  latitude, longitude, source_urls_str AS source_urls, source_types_str AS source_types, '{cap}' AS capability,
  (spec_text rlike '{spec}') AS spec_hit, (evidence_text rlike '{kw}') AS text_hit, n_sources,
  CASE WHEN {contradiction} THEN 'WEAK/SUSPICIOUS'
       WHEN (spec_text rlike '{spec}') AND (evidence_text rlike '{kw}') THEN 'STRONG'
       WHEN (spec_text rlike '{spec}') OR (evidence_text rlike '{kw}') THEN 'PARTIAL'
       ELSE 'NO CLAIM' END AS grade,
  trim(concat_ws(' | ',
     CASE WHEN spec_text rlike '{spec}' THEN 'specialty code present' END,
     nullif(regexp_extract(evidence_text, '(.{{0,30}}({kw}).{{0,45}})', 1),''))) AS evidence_citation
FROM {GOLD}.silver_facility
WHERE (spec_text rlike '{spec}') OR (evidence_text rlike '{kw}')""")
trust_sql = f"""
CREATE OR REPLACE TABLE {GOLD}.gold_facility_capability_trust AS
SELECT *, CASE grade WHEN 'STRONG' THEN least(95, 70 + 5*n_sources)
                     WHEN 'PARTIAL' THEN 50 WHEN 'WEAK/SUSPICIOUS' THEN 20 ELSE 0 END AS confidence
FROM ( {' UNION ALL '.join(selects)} ) t
WHERE grade <> 'NO CLAIM'
"""
run("gold_facility_capability_trust", trust_sql)

# ---- GOLD Track 2: district care gaps ----
run("gold_district_gaps", f"""
CREATE OR REPLACE TABLE {GOLD}.gold_district_gaps AS
SELECT district_n, capability, count(distinct cluster_id) AS n_facilities,
  sum(CASE WHEN grade='STRONG' THEN 1 ELSE 0 END) AS n_strong,
  sum(CASE WHEN grade='PARTIAL' THEN 1 ELSE 0 END) AS n_partial,
  round(sum(CASE WHEN grade IN ('STRONG','PARTIAL') THEN 1 ELSE 0 END)/count(distinct cluster_id),3) AS strong_partial_share,
  CASE WHEN count(distinct cluster_id) < 3 THEN 'DATA-POOR'
       WHEN sum(CASE WHEN grade='STRONG' THEN 1 ELSE 0 END) < 2 THEN 'APPARENT CARE GAP'
       ELSE 'EVIDENCED SUPPLY' END AS classification
FROM {GOLD}.gold_facility_capability_trust WHERE district_n IS NOT NULL
GROUP BY district_n, capability
""")

# ---- GOLD Track 3: referral index ----
run("gold_referral", f"""
CREATE OR REPLACE TABLE {GOLD}.gold_referral AS
SELECT cluster_id, name, capability, grade, confidence, evidence_citation,
       address_city, district_n, latitude, longitude, source_urls, source_types
FROM {GOLD}.gold_facility_capability_trust
WHERE grade IN ('STRONG','PARTIAL') AND latitude IS NOT NULL
""")

# ---- GOLD Track 4: data readiness ----
run("gold_data_readiness", f"""
CREATE OR REPLACE TABLE {GOLD}.gold_data_readiness AS
WITH f AS (
  SELECT cluster_id, name, address_city, district_n, ftype, facilityTypeId,
    (facilityTypeId rlike '[\\\\{{\\\\[]') AS issue_misaligned,
    (ftype='clinic' AND size(coalesce(from_json(specialties,'array<string>'),array()))>=25) AS issue_clinic_overclaim,
    (try_cast(capacity AS double)>0 AND try_cast(numberDoctors AS double) IS NULL) AS issue_capacity_no_doctors,
    (try_cast(numberDoctors AS double)>2000 OR try_cast(capacity AS double)>5000) AS issue_impossible,
    coalesce(try_cast(engagement_metrics_n_followers AS double),0) AS followers
  FROM {GOLD}.silver_facility)
SELECT *, (cast(issue_misaligned as int)+cast(issue_clinic_overclaim as int)
          +cast(issue_capacity_no_doctors as int)+cast(issue_impossible as int)) AS n_issues,
   round((cast(issue_misaligned as int)+cast(issue_clinic_overclaim as int)
         +cast(issue_capacity_no_doctors as int)+cast(issue_impossible as int))*100 + ln(1+followers),1) AS review_priority
FROM f
WHERE (cast(issue_misaligned as int)+cast(issue_clinic_overclaim as int)
      +cast(issue_capacity_no_doctors as int)+cast(issue_impossible as int)) > 0
""")

# ---- PERSISTENCE table ----
run("app_user_actions", f"""
CREATE TABLE IF NOT EXISTS {GOLD}.app_user_actions (
  action_id STRING, user_id STRING, action_type STRING, track STRING,
  entity_id STRING, payload STRING, created_at TIMESTAMP) USING DELTA
""")

# ---- validate ----
cur.execute(f"SELECT capability, grade, count(*) FROM {GOLD}.gold_facility_capability_trust GROUP BY 1,2 ORDER BY 1,2")
print("\n=== grade distribution ==="); [print("  ",r[0],r[1],r[2]) for r in cur.fetchall()]
cur.execute(f"SELECT count(*) FROM {GOLD}.gold_facility_capability_trust"); print("trust rows:", cur.fetchone()[0])
cur.execute(f"SELECT count(*) FROM {GOLD}.gold_data_readiness"); print("readiness flagged:", cur.fetchone()[0])
cur.close(); conn.close(); print("\nGOLD LAYER BUILT in workspace.virtue_gold ✓")
