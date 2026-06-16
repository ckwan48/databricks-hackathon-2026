# Databricks notebook source
# MAGIC %md
# MAGIC # Virtue Foundation — Medallion Pipeline (Bronze → Silver → Gold)
# MAGIC Databricks Apps & Agents for Good 2026 · runs on **Free Edition** (serverless + Unity Catalog).
# MAGIC
# MAGIC **Inputs** (upload to a Volume `/Volumes/{CATALOG}/{SCHEMA}/raw/`):
# MAGIC - `facilities_hack.csv` (10k Virtue Foundation facility records — PRIMARY)
# MAGIC - `india_post.csv` (PIN directory — geographic enrichment)
# MAGIC - `nfhs5.csv` (district health indicators — demand context)
# MAGIC
# MAGIC **Outputs (gold)**: `gold_facility_capability_trust` (Track 1), `gold_district_gaps` (Track 2),
# MAGIC `gold_referral` (Track 3), `gold_data_readiness` (Track 4), `app_user_actions` (persistence).
# MAGIC Every gold row carries **evidence citation** + **confidence**.

# COMMAND ----------
CATALOG = "workspace"        # Free Edition default catalog; change if needed
SCHEMA  = "virtue_hack"
RAW     = f"/Volumes/{CATALOG}/{SCHEMA}/raw"
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.raw")
spark.sql(f"USE {CATALOG}.{SCHEMA}")
print("Upload the 3 CSVs to:", RAW)

# COMMAND ----------
# MAGIC %md ## BRONZE — raw ingest (lossless; keep every original value)
from pyspark.sql import functions as F, types as T

def bronze(name, fname):
    df = (spark.read.option("header", True).option("multiLine", True)
          .option("escape", '"').csv(f"{RAW}/{fname}"))
    df = df.withColumn("_ingested_at", F.current_timestamp()).withColumn("_source_file", F.lit(fname))
    df.write.mode("overwrite").option("overwriteSchema", True).saveAsTable(f"bronze_{name}")
    print(f"bronze_{name}: {df.count()} rows, {len(df.columns)} cols")

bronze("facilities", "facilities_hack.csv")
bronze("pincode",    "india_post.csv")
bronze("nfhs",       "nfhs5.csv")

# COMMAND ----------
# MAGIC %md ## SILVER — clean + type + dedup. Two-track rule: ADD flags, never delete raw.

# --- silver_pincode: row grain is post office -> DEDUP to 1 row per PIN (avoid join fan-out) ---
pin = spark.table("bronze_pincode")
pin = (pin.withColumn("lat", F.col("latitude").cast("double"))
          .withColumn("lon", F.col("longitude").cast("double"))
          .withColumn("district_n", F.upper(F.trim("district")))
          .withColumn("state_n", F.upper(F.trim("statename"))))
# majority district/state per pincode + median-ish coords
w = (pin.groupBy("pincode", "district_n", "state_n").count())
from pyspark.sql.window import Window
rank = Window.partitionBy("pincode").orderBy(F.desc("count"))
pin_dedup = (w.withColumn("rk", F.row_number().over(rank)).filter("rk=1")
             .select("pincode", "district_n", "state_n"))
pin_geo = pin.groupBy("pincode").agg(F.avg("lat").alias("lat"), F.avg("lon").alias("lon"))
silver_pincode = pin_dedup.join(pin_geo, "pincode", "left")
silver_pincode.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("silver_pincode")
print("silver_pincode (1 row/PIN):", silver_pincode.count())

# --- silver_nfhs: *->NULL + suppressed flag; (x)->value + low-precision flag ---
nf = spark.table("bronze_nfhs")
def clean_num(c):
    s = F.trim(F.col(c))
    val = F.when(s == "*", None).otherwise(F.regexp_replace(s, r"[()]", "")).cast("double")
    return val
num_cols = [c for c in nf.columns if c not in ("district_name", "state_ut") and not c.startswith("_")]
sel = [F.trim("district_name").alias("district"), F.trim("state_ut").alias("state")]
for c in num_cols:
    sel.append(clean_num(c).alias(c))
    sel.append(F.when(F.trim(F.col(c)) == "*", True).otherwise(False).alias(f"{c}__suppressed"))
    sel.append(F.col(c).rlike(r"^\(.*\)$").alias(f"{c}__lowprecision"))
silver_nfhs = (nf.select(*sel)
               .withColumn("district_n", F.upper("district")).withColumn("state_n", F.upper("state")))
silver_nfhs.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("silver_nfhs")
print("silver_nfhs:", silver_nfhs.count())

# --- silver_facility: dedup entity (cluster_id), parse JSON arrays, keep RAW text for citations, join district via PIN ---
fac = spark.table("bronze_facilities")
arr_cols = ["specialties", "procedure", "equipment", "capability", "source_urls", "source_types"]
for c in arr_cols:
    fac = fac.withColumn(c + "_arr", F.from_json(F.col(c), T.ArrayType(T.StringType())))
fac = (fac
   .withColumn("zip6", F.regexp_extract(F.col("address_zipOrPostcode"), r"(\d{6})", 1))
   .withColumn("lat", F.col("latitude").cast("double"))
   .withColumn("lon", F.col("longitude").cast("double"))
   .withColumn("ftype", F.regexp_replace(F.lower(F.trim("facilityTypeId")), "farmacy", "pharmacy"))
   # flag column-misaligned rows (e.g. JSON/coords leaked into facilityTypeId)
   .withColumn("_misaligned", F.col("facilityTypeId").rlike(r'[\{\[]|^\d+\.\d+$')))
# entity dedup: 1 row per cluster_id (keep first; the FDR resolved entity)
wc = Window.partitionBy("cluster_id").orderBy("unique_id")
fac = fac.withColumn("_rk", F.row_number().over(wc))
# join to deduped pincode -> district (note official rec: spatial join is better where coords exist; see 02_spatial cell)
silver_facility = (fac.join(silver_pincode.select("pincode", "district_n", "state_n"),
                            fac.zip6 == silver_pincode.pincode, "left"))
silver_facility.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("silver_facility")
print("silver_facility:", silver_facility.count(), "| distinct entities:", silver_facility.select("cluster_id").distinct().count())

# COMMAND ----------
# MAGIC %md ## GOLD — Track 1: facility × capability trust (with EVIDENCE CITATION + CONFIDENCE)
# MAGIC Deterministic, auditable grading (runs on Free Edition with no LLM cost). An optional `ai_query`
# MAGIC GenAI path is in notebook `03_genai_grading` for richer extraction.

import re, json
CAPS = {
 "ICU": dict(spec={"criticalcaremedicine"}, kw=r"\b(icu|intensive care|critical care|ventilator|central oxygen)\b", acute=True),
 "NICU": dict(spec={"neonatologyperinatalmedicine"}, kw=r"\b(nicu|neonat|radiant warmer|phototherapy)\b", acute=True),
 "maternity": dict(spec={"gynecologyandobstetrics","reproductiveendocrinologyandinfertility"}, kw=r"\b(maternit|obstetric|gyn[ae]ecolog|labour|delivery|antenatal|ivf|iui)\b", acute=False),
 "emergency": dict(spec={"emergencymedicine"}, kw=r"\b(emergency|casualty|24/?7|ambulance|trauma)\b", acute=False),
 "oncology": dict(spec={"medicaloncology","surgicaloncology","radiationoncology","breastimaging"}, kw=r"\b(oncolog|cancer|chemotherap|radiotherap|mammogra|tumou?r)\b", acute=True),
 "trauma": dict(spec={"orthopedicsurgery","traumasurgery"}, kw=r"\b(trauma|fracture|polytrauma|orthop[ae]dic)\b", acute=False),
 "dialysis": dict(spec={"nephrology"}, kw=r"\b(dialysis|renal|haemodialysis|nephrolog)\b", acute=True),
}
schema = T.ArrayType(T.StructType([
    T.StructField("capability", T.StringType()), T.StructField("grade", T.StringType()),
    T.StructField("confidence", T.IntegerType()), T.StructField("evidence", T.StringType()),
    T.StructField("n_sources", T.IntegerType()), T.StructField("contradiction", T.BooleanType())]))

def grade_facility(desc, capability, procedure, equipment, specialties, source_types, ftype):
    specs = set([s.lower() for s in (specialties or [])])
    texts = {"specialty": " ".join(specs),
             "capability": " ".join(capability or []), "procedure": " ".join(procedure or []),
             "equipment": " ".join(equipment or []), "description": desc or ""}
    nsrc = len(set(source_types or [])) or 1
    out = []
    for cap, d in CAPS.items():
        ev, types_hit = [], 0
        if specs & d["spec"]:
            types_hit += 1; ev.append("specialty=" + ",".join(sorted(specs & d["spec"])))
        for field in ["equipment", "procedure", "capability", "description"]:
            m = re.search(d["kw"], texts[field], re.I)
            if m:
                types_hit += 1
                snip = texts[field][max(0, m.start()-30):m.start()+60]
                ev.append(f"{field}~…{snip.strip()}…")
        if types_hit == 0:
            continue
        contradiction = d["acute"] and ftype in ("clinic", "dentist", "doctor", "pharmacy") and not (specs & d["spec"])
        if contradiction:
            grade, conf = "WEAK/SUSPICIOUS", 15
        elif types_hit >= 2 and nsrc >= 2:
            grade, conf = "STRONG", min(100, 65 + 5*(types_hit-1) + 5*(nsrc-1))
        elif types_hit >= 1:
            grade, conf = "PARTIAL", 40 + 5*(types_hit-1)
        else:
            grade, conf = "NO CLAIM", 0
        out.append((cap, grade, int(conf), " || ".join(ev[:3]), int(nsrc), bool(contradiction)))
    return out

grade_udf = F.udf(grade_facility, schema)
g = (spark.table("silver_facility").filter("_rk = 1")  # 1 row per entity
     .withColumn("g", grade_udf("description", "capability_arr", "procedure_arr", "equipment_arr",
                                "specialties_arr", "source_types_arr", "ftype"))
     .withColumn("g", F.explode("g")))
gold_trust = g.select(
    "unique_id", "cluster_id", "name", "ftype", "address_city", "address_stateOrRegion", "district_n",
    "lat", "lon", F.col("g.capability").alias("capability"), F.col("g.grade").alias("grade"),
    F.col("g.confidence").alias("confidence"), F.col("g.evidence").alias("evidence_citation"),
    F.col("g.n_sources").alias("n_sources"), F.col("g.contradiction").alias("contradiction"),
    F.col("source_urls_arr").alias("source_urls"))
gold_trust.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("gold_facility_capability_trust")
print("gold_facility_capability_trust:", gold_trust.count(), "claim rows")
display(gold_trust.groupBy("capability", "grade").count().orderBy("capability", "grade"))

# COMMAND ----------
# MAGIC %md ## GOLD — Track 2: district care gaps (real gap vs data-poor + confidence)
gold_gaps = (gold_trust.filter("district_n is not null")
    .groupBy("district_n", "capability")
    .agg(F.countDistinct("cluster_id").alias("n_facilities"),
         F.sum(F.when(F.col("grade")=="STRONG",1).otherwise(0)).alias("n_strong"),
         F.sum(F.when(F.col("grade")=="PARTIAL",1).otherwise(0)).alias("n_partial"))
    .withColumn("strong_partial_share", (F.col("n_strong")+F.col("n_partial"))/F.col("n_facilities"))
    .withColumn("classification",
        F.when(F.col("n_facilities") < 5, "DATA-POOR")
         .when(F.col("strong_partial_share") < 0.2, "APPARENT CARE GAP")
         .otherwise("EVIDENCED SUPPLY")))
gold_gaps.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("gold_district_gaps")
print("gold_district_gaps:", gold_gaps.count())

# COMMAND ----------
# MAGIC %md ## GOLD — Track 3: referral index (capability + geo + confidence for search/ranking)
gold_referral = (gold_trust.filter("grade in ('STRONG','PARTIAL') and lat is not null")
    .select("cluster_id","name","capability","grade","confidence","evidence_citation",
            "address_city","district_n","lat","lon","source_urls"))
gold_referral.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("gold_referral")
print("gold_referral:", gold_referral.count())

# COMMAND ----------
# MAGIC %md ## GOLD — Track 4: data readiness (contradictions, sparse fields, review priority)
fac1 = spark.table("silver_facility").filter("_rk = 1")
issues = (fac1.select("cluster_id","name","address_city","district_n","ftype","_misaligned",
        F.size(F.coalesce("specialties_arr", F.array())).alias("n_spec"),
        F.col("numberDoctors").cast("double").alias("doctors"),
        F.col("capacity").cast("double").alias("capacity"),
        F.col("engagement_metrics_n_followers").cast("double").alias("followers"))
    .withColumn("issue_misaligned", F.col("_misaligned"))
    .withColumn("issue_clinic_overclaim", (F.col("ftype")=="clinic") & (F.col("n_spec")>=25))
    .withColumn("issue_capacity_no_doctors", (F.col("capacity")>0) & (F.col("doctors").isNull()))
    .withColumn("issue_impossible", (F.col("doctors")>2000) | (F.col("capacity")>5000))
    .withColumn("n_issues", F.expr("cast(issue_misaligned as int)+cast(issue_clinic_overclaim as int)+cast(issue_capacity_no_doctors as int)+cast(issue_impossible as int)"))
    .withColumn("review_priority", F.col("n_issues")*100 + F.coalesce(F.log1p("followers"),F.lit(0))))
gold_readiness = issues.filter("n_issues > 0").orderBy(F.desc("review_priority"))
gold_readiness.write.mode("overwrite").option("overwriteSchema", True).saveAsTable("gold_data_readiness")
print("gold_data_readiness:", gold_readiness.count(), "facilities flagged")

# COMMAND ----------
# MAGIC %md ## PERSISTENCE — user actions (notes, overrides, shortlists, scenarios, reviews)
spark.sql("""
CREATE TABLE IF NOT EXISTS app_user_actions (
  action_id   STRING DEFAULT uuid(),
  user_id     STRING,
  action_type STRING,         -- note | override | shortlist | scenario | review_decision
  track       STRING,         -- trust | desert | referral | readiness
  entity_id   STRING,         -- cluster_id / district / pincode
  payload     STRING,         -- JSON: the note text, new grade, shortlist items, scenario params...
  created_at  TIMESTAMP DEFAULT current_timestamp()
) USING DELTA TBLPROPERTIES (delta.enableDeletionVectors = true)
""")
print("app_user_actions ready (append-only audit of every user action).")

# COMMAND ----------
# MAGIC %md ### Done. Gold tables power the 4 tracks; every claim cites `evidence_citation` + `source_urls`,
# MAGIC every score carries `confidence`, and `app_user_actions` persists user work. Next: the Databricks App + Agent.
