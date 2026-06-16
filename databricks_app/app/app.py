"""
Virtue Foundation — Trust, Desert & Causation Desk
Databricks App (Streamlit) · Apps & Agents for Good 2026 · Free Edition.

Reliability-first: the page renders instantly from cached gold-table queries.
Every AI agent (insights / reasoning / simulation / copilot) runs ON-DEMAND via a
button or chat, so the LLM never blocks the render. Llama 4 Maverick via Model Serving.
"""
import os, json, re
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

st.set_page_config(page_title="facilitiesHelp.io — Trust, Desert & Causation", layout="wide", page_icon="🏥")
GOLD="workspace.virtue_gold"; WID=os.getenv("DATABRICKS_WAREHOUSE_ID","c5e7e7089978bd43")
LLM="databricks-llama-4-maverick"; FIGS=os.path.join(os.path.dirname(__file__),"figures"); cfg=Config()
GC={"STRONG":"#119A6B","PARTIAL":"#E0A02A","WEAK/SUSPICIOUS":"#E0594C"}
T1,T2,T3,T4,T5,T6="Facility Trust","Medical Desert","Referral Copilot","Data Readiness","Ask the Data · Genie","Data Science Lab"
GRADE_HELP=("How we grade: STRONG = at least 2 independent evidence types (a clinical specialty code AND equipment/procedure text) "
 "plus a 2nd independent source. PARTIAL = one evidence type. WEAK/SUSPICIOUS = the claim contradicts the facility type "
 "(e.g. a small clinic claiming ICU). Confidence 0-100 = how many evidence types and sources agree — a probability the claim is genuine, not a guarantee.")
GLEG=("<div class='gradeleg'><span class='t'>How a grade is assigned — only from the facility's own record</span>"
 "<div class='row'>"
 "<span class='g'><span class='gdot' style='background:#119A6B'></span><b>STRONG</b>&nbsp;= specialty code <b>+</b> equipment / procedure text <b>+</b> a 2nd independent source</span>"
 "<span class='g'><span class='gdot' style='background:#E0A02A'></span><b>PARTIAL</b>&nbsp;= one evidence type only</span>"
 "<span class='g'><span class='gdot' style='background:#E0594C'></span><b>WEAK / SUSPICIOUS</b>&nbsp;= the claim contradicts the facility type (e.g. a clinic claiming ICU)</span>"
 "</div></div>")
NFHS_LABELS={"sanitation":"Improved sanitation %","clean_fuel":"Clean cooking fuel %","wealth_electricity":"Electricity (wealth proxy) %",
 "schooling":"Women 10+ yrs schooling %","literacy":"Women literate %","child_marriage":"Married before 18 %","inst_birth":"Institutional birth %",
 "anc4":"4+ ANC visits %","stunting":"Child stunting %","wasting":"Child wasting %","child_anaemia":"Child anaemia %",
 "overweight":"Women overweight %","high_blood_sugar":"High blood sugar %"}

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root{--lava:#FF3621;--lava2:#FF6F52;--tint:#FFF4F0;--ink:#0E2A30;--deep:#08191D;--oat:#F4F1EA;
 --line:#E7E2D6;--line2:#EFEBE0;--muted:#5C6B6F;--faint:#8FA0A4;
 --disp:'IBM Plex Sans',system-ui,sans-serif;--body:'IBM Plex Sans',system-ui,sans-serif;--mono:'IBM Plex Mono',ui-monospace,monospace;}
html,body,[class*="css"],.stApp{font-family:var(--body);}
.stApp{background:radial-gradient(900px 440px at 90% -10%,#FBE7E0 0%,rgba(251,231,224,0) 58%),var(--oat);color:var(--ink);}
header[data-testid="stHeader"]{height:0;background:transparent;}
.block-container{padding:1rem 3rem 5rem;max-width:1380px;}
h1,h2,h3,h4{font-family:var(--disp);color:var(--ink);font-weight:600;letter-spacing:-.015em;}
h3{font-size:20px;margin:.4em 0 .15em;} h4{font-size:15.5px;letter-spacing:0;margin:.5em 0 .2em;}
.stApp p,.stApp li{line-height:1.55;}
/* ---- sidebar ---- */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#FBFAF6,#F0EDE3);border-right:1px solid var(--line);min-width:362px;width:362px;}
section[data-testid="stSidebar"] *{color:var(--ink);}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding:1.2rem 1.15rem 2rem;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.55rem;}
section[data-testid="stSidebar"] label{color:var(--faint);font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;font-weight:500;margin-bottom:2px;}
section[data-testid="stSidebar"] .stRadio div[role=radiogroup]{gap:3px;}
section[data-testid="stSidebar"] .stRadio div[role=radiogroup] label{font-family:'IBM Plex Sans';text-transform:none;letter-spacing:0;color:var(--ink);font-size:14px;font-weight:500;padding:3px 0;}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{font-family:'IBM Plex Sans';color:var(--muted);font-size:12px;line-height:1.5;letter-spacing:0;text-transform:none;}
section[data-testid="stSidebar"] [data-baseweb="select"]>div{border-radius:9px;border-color:var(--line);}
section[data-testid="stSidebar"] .stTextInput input{border-radius:9px;}
/* ---- cards / metrics ---- */
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid var(--line) !important;border-radius:16px;box-shadow:0 1px 2px rgba(16,42,48,.04),0 10px 26px -18px rgba(16,42,48,.20);transition:box-shadow .18s ease,transform .18s ease;}
div[data-testid="stVerticalBlockBorderWrapper"]:hover{box-shadow:0 2px 4px rgba(16,42,48,.05),0 20px 44px -22px rgba(16,42,48,.30);transform:translateY(-1px);}
div[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-radius:14px;padding:15px 18px;}
div[data-testid="stMetricValue"]{font-family:var(--disp);color:var(--lava);font-weight:600;}
div[data-testid="stMetricLabel"] p{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);}
.stButton button{background:var(--lava);color:#fff;border:0;border-radius:10px;font-weight:600;font-size:13.5px;padding:.5rem 1rem;box-shadow:0 6px 16px -10px rgba(255,54,33,.85);transition:.16s ease;}
.stButton button:hover{background:var(--ink);box-shadow:0 9px 22px -11px rgba(14,42,48,.7);transform:translateY(-1px);}
.stButton button:active{transform:translateY(0);}
header[data-testid="stHeader"]{background:transparent;}
/* ---- hero ---- */
.hero{position:relative;overflow:hidden;border:1px solid #11343c;border-radius:20px;padding:32px 36px 28px;margin:2px 0 18px;color:#EAF0F0;
 background:radial-gradient(680px 300px at 92% -30%,rgba(255,111,82,.30),rgba(255,111,82,0) 70%),linear-gradient(160deg,#0E2A30 0%,#08191D 100%);}
.hero::after{content:"";position:absolute;inset:0;opacity:.5;pointer-events:none;
 background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:34px 34px;
 -webkit-mask-image:linear-gradient(160deg,#000,transparent 72%);mask-image:linear-gradient(160deg,#000,transparent 72%);}
.hero>*{position:relative;z-index:1;}
.hero .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--lava2);font-weight:500;display:flex;align-items:center;gap:10px;}
.hero .eyebrow .dot{width:7px;height:7px;border-radius:50%;background:#27d796;box-shadow:0 0 0 4px rgba(39,215,150,.18);}
.herowrap{display:flex;gap:46px;align-items:stretch;}
.heroL{flex:1.55;min-width:0;}
.heroR{flex:.95;border-left:1px solid rgba(255,255,255,.10);padding-left:38px;display:flex;flex-direction:column;justify-content:center;gap:22px;}
.hero h1{font-family:var(--disp);color:#fff !important;font-size:34px;line-height:1.12;margin:.34em 0 .3em;font-weight:600;letter-spacing:-.02em;max-width:18ch;}
.hero p{color:#AEBBBD;margin:0;font-size:14.5px;line-height:1.55;max-width:52ch;}
.kpi b{font-family:var(--disp);display:block;font-size:36px;color:#fff;font-weight:600;letter-spacing:-.01em;line-height:1;}
.kpi span{font-family:var(--mono);font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:#8FA0A4;display:block;margin-top:7px;}
@media(max-width:900px){.herowrap{flex-direction:column;gap:24px;}.heroR{border-left:0;border-top:1px solid rgba(255,255,255,.10);padding-left:0;padding-top:20px;flex-direction:row;gap:30px;}}
.ctx{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);margin:6px 2px 16px;font-weight:500;display:flex;gap:10px;align-items:center;}
.ctx .sep{color:var(--line);}
.kick{font-family:var(--mono);font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--lava);font-weight:600;margin:6px 0 -2px;}
.claimrow{font-size:15px;margin:2px 0;}
.chip{display:inline-flex;align-items:center;gap:6px;font-family:var(--mono);font-size:10.5px;font-weight:600;letter-spacing:.04em;padding:3px 10px 3px 8px;border-radius:999px;vertical-align:middle;}
.chip .gdot{width:7px;height:7px;border-radius:50%;}
.meter{display:inline-block;width:120px;height:8px;border-radius:99px;background:#ECEAE2;vertical-align:middle;margin:0 10px;overflow:hidden;box-shadow:inset 0 0 0 1px rgba(0,0,0,.03);}
.meter-fill{display:block;height:100%;border-radius:99px;}
.score{font-family:var(--disp);font-weight:600;color:var(--ink);vertical-align:middle;font-size:14px;}
.score-sm{font-family:var(--mono);color:var(--faint);font-size:10px;font-weight:500;}
.evid{background:var(--tint);border:1px solid #FAD9CE;border-left:3px solid var(--lava);padding:9px 12px;border-radius:10px;font-size:12.5px;color:#6A4A40;line-height:1.45;}
.pillrow{display:flex;flex-wrap:wrap;gap:7px;margin:3px 0 7px;}
.pill{display:inline-flex;align-items:center;gap:5px;background:#F3F1EA;border:1px solid var(--line);color:var(--ink);font-size:12px;padding:3px 10px;border-radius:999px;}
.pill a{color:var(--lava);text-decoration:none;}
.pill2{background:#fff;color:var(--muted);font-family:var(--mono);font-size:11px;letter-spacing:.02em;}
.specs{font-size:12.5px;color:var(--muted);margin:4px 0 2px;line-height:1.5;}
.ico{display:inline-block;width:17px;height:17px;line-height:17px;text-align:center;border-radius:50%;background:#EBE8E0;color:#6A7B7F;font-size:11px;font-weight:700;cursor:help;margin-left:9px;vertical-align:middle;font-family:var(--body);}
.gradeleg{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 18px;margin:4px 0 16px;font-size:13px;box-shadow:0 1px 2px rgba(16,42,48,.04);}
.gradeleg .t{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);}
.gradeleg .row{display:flex;flex-wrap:wrap;gap:10px 24px;margin-top:9px;}
.gradeleg .g{display:flex;align-items:center;gap:8px;line-height:1.45;}
.gradeleg .gdot{width:9px;height:9px;border-radius:50%;flex:none;}
[data-testid="stChatInput"]{background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:0 10px 30px -20px rgba(16,42,48,.45);}
div[data-testid="stExpander"]{border:1px solid var(--line);border-radius:12px;background:#fff;}
.stDataFrame{border-radius:12px;overflow:hidden;border:1px solid var(--line);}
.stAlert{border-radius:12px;}
hr{border-color:var(--line2);margin:1.1rem 0;}
</style>""", unsafe_allow_html=True)

# ---------------- data + agent helpers ----------------
@st.cache_resource
def _conn(): return sql.connect(server_hostname=cfg.host.replace("https://","").rstrip("/"),
    http_path=f"/sql/1.0/warehouses/{WID}", credentials_provider=lambda: cfg.authenticate)
@st.cache_data(ttl=600, show_spinner=False)
def q(query):
    with _conn().cursor() as c:
        c.execute(query); return pd.DataFrame([dict(zip([d[0] for d in c.description], r)) for r in c.fetchall()])
@st.cache_resource
def _wc(): return WorkspaceClient()

CAUSAL_CTX=("Our causal analysis of 706 NFHS districts (PC structure-learning, OLS+state fixed-effects, Double-ML, "
 "propensity matching, E-value sensitivity): sanitation~stunting correlation r=-0.51 COLLAPSES to ~0 after adjusting for "
 "household wealth (CONFOUNDED, not a true cause); female schooling -> less child marriage (r=-0.65, SURVIVES adjustment = "
 "likely causal); ANC4 visits -> institutional birth (r=+0.60, SURVIVES = likely causal); women overweight -> high blood "
 "pressure (r=+0.57, grows under adjustment = causal); facility COUNT is only weakly linked to outcomes after adjustment. "
 "Trust grades are probabilistic: confidence reflects how many independent evidence types (specialty code, equipment/procedure "
 "text, capability text) and how many independent sources agree.")
AGENTS={
 "insights":("You are the INSIGHTS agent for a NON-TECHNICAL health planner who does not know statistics. Reply in markdown. "
  "Start with a bold one-line headline. Then 3 short bullets: each states a plain-English finding FIRST, then weaves the number in and IMMEDIATELY explains what it means in everyday words "
  "(e.g. 'confidence 95/100 — meaning almost every evidence type and source agrees, so we can rely on it'; or 'r=-0.51 vanishes to about 0 once we account for wealth — so it was never a real cause, just a coincidence'). "
  "NEVER begin a bullet with a bare number. Ground each point in the evidence/data given. End with a bold **Action:** line. Be concrete and self-explanatory."),
 "reasoning":("You are the REASONING agent (causal · evidence · probability · correlation) for a non-technical reader. Reply in formatted markdown with short paragraphs. "
  "Whenever you mention a number, explain in plain words what it means right after it. Always (1) distinguish CORRELATION from CAUSATION explicitly, (2) state the probability/confidence honestly and what it implies, "
  "(3) name confounders, (4) quote the ground-truth evidence you were given. Never overstate weak evidence. End with a bold one-line bottom verdict."),
 "simulation":("You are the SIMULATION what-if agent for a non-technical reader. In markdown, reason about the scenario outcome and its UNCERTAINTY, grounded in the evidence rubric and our causal findings "
  "(flag causal vs correlational). Explain every number in plain words and say what evidence would change the result. End with a clear bold bottom line."),
 "copilot":("You are the facilitiesHelp.io Copilot (Llama 4 Maverick on Databricks) for a NON-TECHNICAL planner. Answer in clean markdown about facility trust, district care gaps, referrals, data quality, and NFHS causal findings. "
  "CRITICAL: never fabricate statistics, percentages, rates or example numbers — use ONLY numbers you are explicitly given; if you weren't given data, say so. Whenever you cite a number, explain in plain words what it means. State confidence and distinguish correlation from causation in everyday language. Keep it concise; don't pad with invented illustrations.")}
def run_agent(name, ctx, mx=420):
    try:
        from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
        r=_wc().serving_endpoints.query(name=LLM, max_tokens=mx, temperature=0.2,
            messages=[ChatMessage(role=ChatMessageRole.SYSTEM, content=AGENTS[name]),
                      ChatMessage(role=ChatMessageRole.USER, content=ctx)])
        c=r.choices[0].message.content
        return c if isinstance(c,str) else " ".join(str(x) for x in c)
    except Exception as e: return f"⚠️ Agent unavailable ({type(e).__name__})."
def ai_button(key, agent, ctx, label="Explain with the AI agent", kind="info"):
    if st.button(f"🧠 {label}", key="b_"+key):
        with st.spinner("Agent reasoning…"): st.session_state["ai_"+key]=run_agent(agent, ctx)
    if st.session_state.get("ai_"+key):
        (st.success if kind=="success" else st.warning if kind=="warn" else st.info)(st.session_state["ai_"+key])
def save_action(user, at, track, ent, payload, silent=False):
    p=json.dumps(payload).replace("'","''"); e=str(ent)[:60].replace("'","")
    with _conn().cursor() as c:
        c.execute(f"INSERT INTO {GOLD}.app_user_actions (action_id,user_id,action_type,track,entity_id,payload,created_at) VALUES (uuid(),'{user}','{at}','{track}','{e}','{p}',current_timestamp())")
    if not silent: st.toast("Saved ✓", icon="✅")
GENIE_SID=os.getenv("GENIE_SPACE_ID","01f16941592d11d898fe40ebe4cee777")
def genie_ask(question):
    g=_wc().genie
    msg=g.start_conversation_and_wait(GENIE_SID, question)
    out={"text":None,"sql":None,"cols":None,"rows":None}
    for a in (msg.attachments or []):
        if getattr(a,"text",None) and getattr(a.text,"content",None) and not out["text"]:
            out["text"]=a.text.content
        if getattr(a,"query",None) and getattr(a.query,"query",None) and not out["sql"]:
            out["sql"]=a.query.query
            try:
                sr=g.get_message_attachment_query_result(GENIE_SID,msg.conversation_id,msg.id,a.attachment_id).statement_response
                out["cols"]=[c.name for c in sr.manifest.schema.columns]; out["rows"]=sr.result.data_array or []
            except Exception: pass
    return out
def _v(x):
    if x is None: return None
    if isinstance(x,float) and pd.isna(x): return None
    s=str(x).strip()
    return None if s in ("","None","nan","null","NaN") else x
def _int(x):
    try: return int(float(x))
    except Exception: return None
def badge(g,c):
    col=GC.get(g,"#9aa3af")
    return (f"<span class='chip' style='background:{col}1A;color:{col};border:1px solid {col}55'>"
            f"<span class='gdot' style='background:{col}'></span>{g}</span>"
            f"<span class='meter'><span class='meter-fill' style='width:{int(c)}%;background:linear-gradient(90deg,{col}bb,{col})'></span></span>"
            f"<span class='score'>{int(c)}<span class='score-sm'>/100</span></span>")
def clean_ev(s):
    parts=[p.strip() for p in str(s or "").split(" | ") if p.strip()]
    out=[]
    for p in parts:
        if p=="specialty code present": out.append("a matching clinical **specialty code**")
        else:
            t=p.split()
            if len(t)>2: t=t[1:-1]
            if t: out.append("the phrase “…"+" ".join(t)+"…”")
    return " and ".join(out) if out else "no machine-readable evidence"
_CRED=("gov.in","nic.in",".gov","nabh","jci","ncbi.nlm","pubmed","nih.gov","who.int","health","hospital","medical","clinic","care")
def rank_sources(raw,k=3):
    urls=[u.strip() for u in str(raw or "").split(" | ") if u.strip() and u.strip()!="null"]
    urls.sort(key=lambda u: 0 if any(c in u.lower() for c in _CRED) else 1)
    return urls[:k]
def facacts(h):
    bits=[]
    addr=_v(h.get("full_address")); ph=_v(h.get("phone")); web=_v(h.get("website")); em=_v(h.get("email"))
    if addr: bits.append(f"<span class='pill'>📍 {str(addr)[:90]}</span>")
    if ph:   bits.append(f"<span class='pill'>📞 {str(ph)[:48]}</span>")
    if web:
        wb=str(web) if str(web).startswith("http") else "https://"+str(web)
        bits.append(f"<span class='pill'>🌐 <a href='{wb}' target='_blank'>{str(web)[:42]}</a></span>")
    if em:   bits.append(f"<span class='pill'>✉️ {str(em)[:40]}</span>")
    facts=[]
    cap=_int(h.get("capacity")); doc=_int(h.get("n_doctors")); yr=_v(h.get("year_est")); fol=_int(h.get("followers"))
    if cap: facts.append(f"🛏️ {cap:,} beds")
    if doc: facts.append(f"🩺 {doc:,} doctors")
    if yr:  facts.append(f"📅 est. {str(yr)[:4]}")
    if fol: facts.append(f"👥 {fol:,} followers")
    html=""
    if bits:  html+="<div class='pillrow'>"+"".join(bits)+"</div>"
    if facts: html+="<div class='pillrow'>"+"".join(f"<span class='pill pill2'>{f}</span>" for f in facts)+"</div>"
    return html
def facmap(df,h=420):
    df=df.dropna(subset=["latitude","longitude"]).copy()
    if df.empty: return None
    df["confidence"]=df["confidence"].clip(lower=8)
    f=px.scatter_mapbox(df,lat="latitude",lon="longitude",color="grade",color_discrete_map=GC,size="confidence",
        size_max=12,zoom=3.3,hover_name="name",center={"lat":22.5,"lon":80},opacity=.8)
    f.update_layout(mapbox_style="carto-positron",margin=dict(l=0,r=0,t=2,b=0),height=h,legend=dict(orientation="h",y=1.0,x=0,title=""))
    return f

# ---- causal model (correlation vs causation, 706 NFHS districts) ----
_NODES={"Wealth/SES":(0.04,0.95,"confounder"),"Urbanicity":(0.04,0.52,"confounder"),"Sanitation":(0.27,0.96,"treatment"),
 "Clean fuel":(0.27,0.73,"treatment"),"Schooling":(0.27,0.30,"treatment"),"ANC4":(0.27,0.07,"treatment"),
 "Overweight":(0.52,0.96,"treatment"),"Diarrhoea":(0.55,0.60,"mediator"),"Stunting":(0.90,0.80,"outcome"),
 "Child marriage":(0.63,0.22,"outcome"),"Inst. birth":(0.63,0.04,"outcome"),"High BP":(0.92,0.42,"outcome"),"Facilities":(0.50,0.03,"supply")}
_EDGES=[("Wealth/SES","Sanitation","confounder","Wealth raises sanitation (common cause of both)"),
 ("Wealth/SES","Stunting","confounder","Wealth lowers stunting (common cause)"),("Wealth/SES","Schooling","confounder","Wealth raises schooling"),
 ("Urbanicity","Sanitation","confounder","Urbanicity raises sanitation"),("Sanitation","Diarrhoea","causal","Sanitation → less diarrhoea (r=-0.13, holds up)"),
 ("Diarrhoea","Stunting","mediator","Diarrhoea → stunting (r=+0.23, a mediator)"),
 ("Sanitation","Stunting","confounded","Sanitation→stunting r=-0.51 COLLAPSES to ~0 after wealth adjustment — CONFOUNDED, not a real cause"),
 ("Clean fuel","Stunting","confounded","Clean fuel→stunting -0.42 → weak after adjustment"),
 ("Schooling","Child marriage","causal","Female schooling → less child marriage (-0.65, SURVIVES adjustment) — LIKELY CAUSAL"),
 ("ANC4","Inst. birth","causal","ANC4 visits → institutional birth (+0.60, SURVIVES) — LIKELY CAUSAL"),
 ("Overweight","High BP","causal","Women overweight → high blood pressure (+0.57, grows under adjustment) — CAUSAL"),
 ("Facilities","Inst. birth","weak","More facilities → only weakly linked to outcomes after adjustment")]
_RC={"outcome":"#0E2A30","treatment":"#2272B4","confounder":"#9aa6a8","mediator":"#E0A93B","supply":"#119A6B"}
_VC={"causal":"#119A6B","confounded":"#FF3621","mediator":"#E0A93B","confounder":"#9aa6a8","weak":"#c0c7c9"}
_FOCUS={"maternity":["Inst. birth","Child marriage"],"NICU":["Inst. birth","Stunting"],"emergency":["High BP"],
 "ICU":["High BP"],"oncology":["High BP"],"trauma":["High BP"],"dialysis":["High BP"]}
def _subgraph(cap):
    focus=set(_FOCUS.get(cap,[])); rel=set(focus); changed=True
    while changed:
        changed=False
        for s,d,v,l in _EDGES:
            if d in rel and s not in rel: rel.add(s); changed=True
    if not rel: rel=set(_NODES)
    sub=[(s,d,v,l) for s,d,v,l in _EDGES if s in rel and d in rel]
    return focus, rel, sub
def causal_d3(cap):
    """Interactive d3.js causal sub-graph — only the nodes relevant to the selected capability."""
    focus,rel,sub=_subgraph(cap)
    xs=[_NODES[n][0] for n in rel]; ys=[_NODES[n][1] for n in rel]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    NX=lambda x:round((x-minx)/(maxx-minx),3) if maxx>minx else 0.5
    NY=lambda y:round((y-miny)/(maxy-miny),3) if maxy>miny else 0.5
    nodes=[{"id":n,"role":_NODES[n][2],"x":NX(_NODES[n][0]),"y":NY(_NODES[n][1]),
            "r":19 if n in focus else 13,"color":_RC[_NODES[n][2]],"focus":n in focus} for n in rel]
    links=[{"sx":NX(_NODES[s][0]),"sy":NY(_NODES[s][1]),"tx":NX(_NODES[d][0]),"ty":NY(_NODES[d][1]),
            "color":_VC[v],"verd":v,"lbl":l,"dash":v in ("confounded","confounder","weak"),
            "w":5 if v=="causal" else 2.5} for s,d,v,l in sub]
    tpl="""<!DOCTYPE html><html><head><meta charset="utf-8"><script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<style>
 body{margin:0;font-family:IBM Plex Sans,system-ui,sans-serif;}
 #wrap{position:relative;height:470px;background:#fff;border:1px solid #E7E2D6;border-radius:14px;overflow:hidden;}
 .lnk{fill:none;stroke-linecap:round;cursor:pointer;}
 .nodec{stroke:#fff;stroke-width:2.5px;cursor:pointer;}
 .nlab{font:600 12px IBM Plex Sans,sans-serif;fill:#0E2A30;pointer-events:none;}
 .vrole{font:500 8.5px 'IBM Plex Mono',monospace;fill:#8FA0A4;pointer-events:none;letter-spacing:.06em;text-transform:uppercase;}
 #tip{position:absolute;pointer-events:none;background:#0E2A30;color:#fff;border-radius:9px;padding:8px 11px;font:12px/1.45 IBM Plex Sans,sans-serif;max-width:270px;opacity:0;transition:opacity .12s;box-shadow:0 12px 30px -12px rgba(0,0,0,.5);z-index:9;}
 .vb{display:inline-block;font:600 9px 'IBM Plex Mono',monospace;letter-spacing:.06em;text-transform:uppercase;padding:1px 6px;border-radius:6px;margin-bottom:4px;}
</style></head><body><div id="wrap"><div id="tip"></div></div>
<script>
const NODES=__NODES__, LINKS=__LINKS__;
const wrap=document.getElementById('wrap'), W=wrap.clientWidth||760, H=470, P=58;
const svg=d3.select('#wrap').append('svg').attr('width',W).attr('height',H);
const tip=d3.select('#tip');
const cols=[...new Set(LINKS.map(l=>l.color))]; const ci={}; cols.forEach((c,i)=>ci[c]=i);
const defs=svg.append('defs');
cols.forEach((c,i)=>defs.append('marker').attr('id','ar'+i).attr('viewBox','0 -5 10 10').attr('refX',20).attr('refY',0)
  .attr('markerWidth',6).attr('markerHeight',6).attr('orient','auto').append('path').attr('d','M0,-5L10,0L0,5').attr('fill',c));
const X=x=>P+x*(W-2*P), Y=y=>P+(1-y)*(H-2*P);
function move(ev,html){const [mx,my]=d3.pointer(ev,wrap);tip.html(html).style('left',(mx+15)+'px').style('top',(my+12)+'px').style('opacity',1);}
const link=svg.selectAll('.lnk').data(LINKS).enter().append('path').attr('class','lnk')
 .attr('d',d=>{const x1=X(d.sx),y1=Y(d.sy),x2=X(d.tx),y2=Y(d.ty),dx=x2-x1,dy=y2-y1,h=Math.hypot(dx,dy)||1,o=Math.min(48,h*0.13);
   return `M${x1},${y1} Q${(x1+x2)/2-dy/h*o},${(y1+y2)/2+dx/h*o} ${x2},${y2}`;})
 .attr('stroke',d=>d.color).attr('stroke-width',d=>d.w).attr('stroke-dasharray',d=>d.dash?'6 5':null)
 .attr('marker-end',d=>`url(#ar${ci[d.color]})`).attr('opacity',0.95)
 .on('mousemove',function(ev,d){d3.select(this).attr('stroke-width',d.w+2.5);move(ev,`<span class="vb" style="background:${d.color}22;color:${d.color}">${d.verd}</span><br>${d.lbl}`);})
 .on('mouseleave',function(ev,d){d3.select(this).attr('stroke-width',d.w);tip.style('opacity',0);});
const g=svg.selectAll('.nd').data(NODES).enter().append('g').attr('transform',d=>`translate(${X(d.x)},${Y(d.y)})`);
g.append('circle').attr('class','nodec').attr('r',d=>d.r).attr('fill',d=>d.color)
 .on('mousemove',(ev,d)=>move(ev,`<b>${d.id}</b><br><span style="opacity:.75">role: ${d.role}</span>`))
 .on('mouseleave',()=>tip.style('opacity',0));
g.append('text').attr('class','nlab').attr('y',d=>-d.r-8).attr('text-anchor','middle').text(d=>d.id);
g.append('text').attr('class','vrole').attr('y',d=>-d.r-21).attr('text-anchor','middle').text(d=>d.role);
link.attr('opacity',0).transition().duration(450).delay((d,i)=>i*70).attr('opacity',0.95);
g.attr('opacity',0).transition().duration(380).delay((d,i)=>i*55+140).attr('opacity',1);
</script></body></html>"""
    return tpl.replace("__NODES__",json.dumps(nodes)).replace("__LINKS__",json.dumps(links))
def causal_plot(cap):
    """Clean Plotly causal sub-graph (no external CDN) — only the levers relevant to `cap`."""
    focus,rel,sub=_subgraph(cap); rel=list(rel)
    xs=[_NODES[n][0] for n in rel]; ys=[_NODES[n][1] for n in rel]
    minx,maxx,miny,maxy=min(xs),max(xs),min(ys),max(ys)
    NX=lambda x:(x-minx)/(maxx-minx) if maxx>minx else 0.5
    NY=lambda y:(y-miny)/(maxy-miny) if maxy>miny else 0.5
    pos={n:(NX(_NODES[n][0]),NY(_NODES[n][1])) for n in rel}
    fig=go.Figure()
    for s,d,verd,lbl in sub:
        x0,y0=pos[s]; x1,y1=pos[d]; col=_VC[verd]
        fig.add_annotation(x=x1,y=y1,ax=x0,ay=y0,xref="x",yref="y",axref="x",ayref="y",showarrow=True,arrowhead=3,
            arrowsize=1.1,arrowwidth=5 if verd=="causal" else 2.5,arrowcolor=col)
        fig.add_trace(go.Scatter(x=[(x0+x1)/2],y=[(y0+y1)/2],mode="markers",marker=dict(size=28,color=col,opacity=0.001),
            hovertext=f"<b>{verd.upper()}</b><br>{lbl}",hoverinfo="text",showlegend=False))
    fig.add_trace(go.Scatter(x=[pos[n][0] for n in rel],y=[pos[n][1] for n in rel],mode="markers+text",
        marker=dict(size=[36 if n in focus else 24 for n in rel],color=[_RC[_NODES[n][2]] for n in rel],line=dict(color="#fff",width=2.5)),
        text=rel,textposition="top center",textfont=dict(size=11,color="#0E2A30",family="IBM Plex Sans"),
        hovertext=[f"{n} · {_NODES[n][2]}" for n in rel],hoverinfo="text",showlegend=False))
    fig.update_layout(height=430,margin=dict(l=8,r=8,t=12,b=8),plot_bgcolor="#fff",paper_bgcolor="#fff",
        xaxis=dict(visible=False,range=[-0.14,1.14]),yaxis=dict(visible=False,range=[-0.12,1.20]),font=dict(family="IBM Plex Sans"))
    return fig
# ---- interactive d3 causal-graph studio (d3 INLINED so it renders inside Databricks Apps; force layout ⇒ draggable) ----
@st.cache_resource
def _d3src():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"d3.v7.min.js"),encoding="utf-8") as f: return f.read()
KINDC={"causal":"#119A6B","confounded":"#E0594C","confounder":"#9AA6A8","mediator":"#E0A93B","weak":"#C0C7C9","evidence":"#2272B4","cooccur":"#7A5AF8","demand":"#E0732B","protective":"#119A6B"}
KIND_LBL={"causal":"likely causal (survives adjustment)","confounded":"confounded (vanishes after wealth adj.)","confounder":"common cause (confounder)","mediator":"mediator (on the pathway)","weak":"weak / negligible link","evidence":"evidence → verdict","cooccur":"co-occurs (population correlation)","demand":"demand-side driver","protective":"protective (shrinks the gap)"}
_RROLE={"outcome":18,"supply":16,"treatment":15,"confounder":14,"mediator":14,"evidence":15,"demand":15}
def _mod(nodes,links,desc=""):
    return {"desc":desc,
      "nodes":[{"id":n,"role":role,"color":_RC.get(role,"#2272B4"),"r":_RROLE.get(role,15)} for n,role in nodes],
      "links":[{"source":s,"target":t,"kind":k,"label":l,"w":5 if k in ("causal","evidence") else 3,"dash":k in ("confounded","confounder","weak","cooccur")} for s,t,k,l in links]}
def causal_modules():
    M={}
    M["① NFHS health — full correlation-vs-causation map"]=_mod([(n,_NODES[n][2]) for n in _NODES],[(s,d,v,l) for s,d,v,l in _EDGES],
      "Every NFHS link we tested. Green survives wealth adjustment (likely causal); red collapses (confounded); grey are common causes.")
    M["② Confounding — the wealth fork (sanitation ↔ stunting)"]=_mod(
      [("Household wealth","confounder"),("Sanitation","treatment"),("Child stunting","outcome")],
      [("Household wealth","Sanitation","confounder","Richer districts have better sanitation"),
       ("Household wealth","Child stunting","confounder","Richer districts have less stunting"),
       ("Sanitation","Child stunting","confounded","Raw r = -0.51 — collapses to ~0 after adjusting for wealth ⇒ NOT a cause")],
      "The textbook fork: wealth drives both, creating a strong but spurious sanitation↔stunting link.")
    M["③ Facility trust — evidence → verdict"]=_mod(
      [("Specialty code","evidence"),("Equipment / procedure text","evidence"),("2nd independent source","evidence"),
       ("Grade = STRONG","outcome"),("Confidence 0–100","outcome"),("Contradicts facility type","evidence"),("WEAK / SUSPICIOUS","outcome")],
      [("Specialty code","Grade = STRONG","evidence","A matching clinical specialty code (+35)"),
       ("Equipment / procedure text","Grade = STRONG","evidence","Procedure / equipment in the free text (+20)"),
       ("2nd independent source","Grade = STRONG","evidence","Each extra independent source (up to +40)"),
       ("Grade = STRONG","Confidence 0–100","causal","More agreeing evidence ⇒ higher confidence"),
       ("Contradicts facility type","WEAK / SUSPICIOUS","causal","e.g. a tiny clinic claiming ICU ⇒ downgraded")],
      "How a grade is built — purely from the facility's own record, fully auditable.")
    M["④ Care pathway — conditions that travel together"]=_mod(
      [("Child stunting","outcome"),("Child anaemia","outcome"),("Child wasting","outcome"),
       ("Paediatrics","supply"),("Child nutrition","supply"),("Pathology / labs","supply")],
      [("Child stunting","Child anaemia","cooccur","Travel together across districts (r = +0.33)"),
       ("Child stunting","Child wasting","cooccur","Travel together across districts (r = +0.25)"),
       ("Child stunting","Paediatrics","causal","See a paediatrician"),
       ("Child stunting","Child nutrition","causal","Nutrition / dietetics counselling"),
       ("Child anaemia","Pathology / labs","causal","Haemoglobin / blood work"),
       ("Child anaemia","Paediatrics","causal","Paediatric review")],
      "Why Referral's 'you may also need' exists: conditions co-occur, so related care is a sensible maybe.")
    M["⑤ Medical desert — supply vs demand vs outcome"]=_mod(
      [("Population / demand","demand"),("Facilities / supply","supply"),("Care gap","outcome"),
       ("Health outcome","outcome"),("Household wealth","confounder")],
      [("Population / demand","Care gap","demand","More unmet need ⇒ larger gap"),
       ("Facilities / supply","Care gap","protective","More trusted supply ⇒ smaller gap"),
       ("Facilities / supply","Health outcome","weak","Facility count only weakly linked to outcomes after adjustment"),
       ("Household wealth","Health outcome","confounder","Wealth drives outcomes directly"),
       ("Household wealth","Facilities / supply","confounder","Richer districts attract more facilities")],
      "The honest planning picture: 'build more' is only weakly linked to outcomes — demand-side levers often matter more.")
    M["⑥ Maternal & adolescent care chain"]=_mod(
      [("Female schooling","treatment"),("Child marriage","outcome"),("ANC4 visits","treatment"),
       ("Institutional birth","outcome"),("Newborn care","supply")],
      [("Female schooling","Child marriage","causal","Schooling ⇒ less child marriage (-0.65, survives)"),
       ("Female schooling","ANC4 visits","causal","Schooling ⇒ more antenatal care"),
       ("ANC4 visits","Institutional birth","causal","ANC4 ⇒ institutional birth (+0.60, survives)"),
       ("Institutional birth","Newborn care","causal","Facility delivery ⇒ newborn care access")],
      "Demand-side levers that DO survive adjustment — likely real causes a planner can act on.")
    return M
_TPL="""<!DOCTYPE html><html><head><meta charset="utf-8"><script>__D3__</script>
<style>
 html,body{margin:0;font-family:'IBM Plex Sans',system-ui,sans-serif;}
 #wrap{position:relative;height:__H__px;background:linear-gradient(180deg,#fff,#FBFAF6);border:1px solid #E7E2D6;border-radius:16px;overflow:hidden;}
 .nlab{font:600 12.5px 'IBM Plex Sans',sans-serif;fill:#0E2A30;pointer-events:none;}
 .vrole{font:600 8px 'IBM Plex Mono',monospace;fill:#90A0A4;pointer-events:none;letter-spacing:.07em;text-transform:uppercase;}
 #tip{position:absolute;pointer-events:none;background:#0E2A30;color:#fff;border-radius:10px;padding:9px 12px;font:12px/1.5 'IBM Plex Sans',sans-serif;max-width:290px;opacity:0;transition:opacity .12s;box-shadow:0 14px 34px -12px rgba(0,0,0,.55);z-index:9;}
 .vb{display:inline-block;font:700 9px 'IBM Plex Mono',monospace;letter-spacing:.06em;text-transform:uppercase;padding:1px 7px;border-radius:6px;margin-bottom:5px;}
 #hint{position:absolute;left:13px;bottom:11px;font:500 11px 'IBM Plex Sans',sans-serif;color:#9AA7AB;pointer-events:none;}
 #leg{padding:10px 4px 2px;}
</style></head><body>
<div id="wrap"><div id="tip"></div><div id="hint">drag any node · scroll to zoom · hover a link for the evidence</div></div>
<div id="leg">__LEGEND__</div>
<script>
const NODES=__NODES__, LINKS=__LINKS__, KCOL=__KCOL__;
const wrap=document.getElementById('wrap'), W=wrap.clientWidth||820, H=__H__;
const svg=d3.select('#wrap').append('svg').attr('width',W).attr('height',H);
const root=svg.append('g');
svg.call(d3.zoom().scaleExtent([0.45,2.6]).on('zoom',ev=>root.attr('transform',ev.transform)));
const tip=d3.select('#tip');
const kinds=[...new Set(LINKS.map(l=>l.kind))];
const defs=svg.append('defs');
kinds.forEach(k=>defs.append('marker').attr('id','m_'+k).attr('viewBox','0 -5 10 10').attr('refX',23).attr('refY',0).attr('markerWidth',6.5).attr('markerHeight',6.5).attr('orient','auto').append('path').attr('d','M0,-5L10,0L0,5').attr('fill',KCOL[k]));
function move(ev,html){const p=d3.pointer(ev,wrap);tip.html(html).style('left',(p[0]+15)+'px').style('top',(p[1]+12)+'px').style('opacity',1);}
const link=root.append('g').selectAll('path').data(LINKS).join('path').attr('fill','none')
 .attr('stroke',d=>KCOL[d.kind]).attr('stroke-width',d=>d.w).attr('stroke-linecap','round')
 .attr('stroke-dasharray',d=>d.dash?'7 6':null).attr('marker-end',d=>'url(#m_'+d.kind+')').attr('opacity',.92).style('cursor','pointer')
 .on('mousemove',function(ev,d){d3.select(this).attr('stroke-width',d.w+2.5);move(ev,'<span class="vb" style="background:'+KCOL[d.kind]+'22;color:'+KCOL[d.kind]+'">'+d.kind+'</span><br>'+d.label);})
 .on('mouseleave',function(ev,d){d3.select(this).attr('stroke-width',d.w);tip.style('opacity',0);});
const node=root.append('g').selectAll('g').data(NODES).join('g').style('cursor','grab')
 .call(d3.drag().on('start',ds).on('drag',dg).on('end',de));
node.append('circle').attr('r',d=>d.r).attr('fill',d=>d.color).attr('stroke','#fff').attr('stroke-width',2.6)
 .on('mousemove',(ev,d)=>move(ev,'<b>'+d.id+'</b><br><span style="opacity:.78">role: '+d.role+'</span>'))
 .on('mouseleave',()=>tip.style('opacity',0));
node.append('text').attr('class','nlab').attr('text-anchor','middle').attr('y',d=>-d.r-9).text(d=>d.id);
node.append('text').attr('class','vrole').attr('text-anchor','middle').attr('y',d=>-d.r-22).text(d=>d.role);
const sim=d3.forceSimulation(NODES)
 .force('link',d3.forceLink(LINKS).id(d=>d.id).distance(150).strength(.45))
 .force('charge',d3.forceManyBody().strength(-680))
 .force('center',d3.forceCenter(W/2,H/2-6))
 .force('collide',d3.forceCollide().radius(d=>d.r+30)).on('tick',tick);
function tick(){
 link.attr('d',d=>{const dx=d.target.x-d.source.x,dy=d.target.y-d.source.y,h=Math.hypot(dx,dy)||1,o=Math.min(38,h*0.13);
  return 'M'+d.source.x+','+d.source.y+' Q'+((d.source.x+d.target.x)/2-dy/h*o)+','+((d.source.y+d.target.y)/2+dx/h*o)+' '+d.target.x+','+d.target.y;});
 node.attr('transform',d=>'translate('+d.x+','+d.y+')');}
function ds(ev,d){if(!ev.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y;}
function dg(ev,d){d.fx=ev.x;d.fy=ev.y;}
function de(ev,d){if(!ev.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}
</script></body></html>"""
def d3_graph(mod,height=540):
    legend="".join(f"<span style='display:inline-flex;align-items:center;gap:6px;margin:0 12px 7px 0;font:500 11px IBM Plex Sans,sans-serif;color:#3C4A4E'><span style='width:18px;border-top:3px {'dashed' if k in ('confounded','confounder','weak','cooccur') else 'solid'} {KINDC[k]}'></span>{KIND_LBL[k]}</span>" for k in KINDC if any(l['kind']==k for l in mod['links']))
    return (_TPL.replace("__D3__",_d3src()).replace("__NODES__",json.dumps(mod["nodes"]))
        .replace("__LINKS__",json.dumps(mod["links"])).replace("__KCOL__",json.dumps(KINDC))
        .replace("__H__",str(height)).replace("__LEGEND__",legend))
def attribution_html(spec_hit,text_hit,n_sources):
    ns=int(n_sources or 0)
    rows=[("Matching specialty code",35 if spec_hit else 0,"#2272B4"),
          ("Procedure / equipment text",20 if text_hit else 0,"#E0A02A"),
          (f"Independent sources (×{ns})",min(40,7*ns),"#119A6B")]
    h="<div style='margin:4px 0 2px'>"
    for lbl,v,c in rows:
        h+=(f"<div style='display:flex;align-items:center;gap:10px;margin:5px 0;font-size:12.5px'>"
            f"<span style='width:200px;color:#5C6B6F'>{lbl}</span>"
            f"<span style='flex:1;background:#ECEAE2;border-radius:6px;height:10px;overflow:hidden'>"
            f"<span style='display:block;height:100%;width:{min(100,v*2.2):.0f}%;background:{c}'></span></span>"
            f"<span style='width:40px;text-align:right;font-family:IBM Plex Mono;font-size:11px;color:#0E2A30'>+{v}</span></div>")
    return h+"</div>"
def info_pop(text,label="ⓘ  what this shows"):
    with st.popover(label):
        st.markdown(text)
def explain_r(r,xl,yl):
    a=abs(r)
    strength=("almost no" if a<0.1 else "a weak" if a<0.3 else "a moderate" if a<0.5 else "a strong" if a<0.7 else "a very strong")
    direction=("they tend to rise together" if r>0 else "as one goes up, the other tends to go down")
    return (f"**r = {r:+.2f} — {strength} relationship.** On a scale from −1 (perfect opposite) to +1 (perfect lockstep), "
            f"this says **{xl}** and **{yl}** move together {'strongly' if a>=0.5 else 'somewhat' if a>=0.3 else 'barely'} — {direction}. "
            f"But **a correlation is not a cause:** a third factor (often household wealth) can drive both at once. "
            f"The *Causal & ML experiments* tab re-checks each link after statistically removing wealth — only the ones that survive are likely real causes.")
_EFF=[("sanitation→stunting",-0.51,-0.15,-0.11,-0.01),("schooling→child-marriage",-0.65,-0.18,-0.17,-0.40),
 ("clean-fuel→stunting",-0.42,-0.16,-0.14,-0.06),("ANC4→inst-birth",0.60,0.16,0.13,0.36),("overweight→high-BP",0.57,0.29,0.35,0.44)]
def causal_effects_chart():
    rows=[{"pair":n,"method":m,"effect":v} for n,nv,ols,dml,psm in _EFF for m,v in [("Naive",nv),("Adjusted (OLS+state FE)",ols),("Double-ML",dml),("Matching (PSM)",psm)]]
    fig=px.bar(pd.DataFrame(rows),x="pair",y="effect",color="method",barmode="group",
        color_discrete_map={"Naive":"#FF3621","Adjusted (OLS+state FE)":"#2272B4","Double-ML":"#119A6B","Matching (PSM)":"#E0A93B"})
    fig.add_hline(y=0,line_color="#9aa6a8")
    fig.update_layout(height=470,margin=dict(l=0,r=0,t=44,b=0),legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0,title=""),font=dict(family="IBM Plex Sans"),yaxis_title="standardized effect",xaxis_title="")
    return fig
def effect_bar(name):
    row=next((e for e in _EFF if e[0]==name),_EFF[0]); _,nv,ols,dml,psm=row
    df=pd.DataFrame({"method":["Naive (raw correlation)","Adjusted (OLS+state FE)","Double-ML","Matching (PSM)"],"effect":[nv,ols,dml,psm]})
    fig=px.bar(df,x="method",y="effect",color="method",text=[f"{v:+.2f}" for v in [nv,ols,dml,psm]],
        color_discrete_map={"Naive (raw correlation)":"#FF3621","Adjusted (OLS+state FE)":"#2272B4","Double-ML":"#119A6B","Matching (PSM)":"#E0A02A"})
    fig.add_hline(y=0,line_color="#9aa6a8")
    fig.update_layout(height=410,margin=dict(l=0,r=0,t=10,b=0),showlegend=False,font=dict(family="IBM Plex Sans"),yaxis_title="standardized effect (−1…+1)",xaxis_title="")
    return fig,(nv,ols,dml,psm)
def conf_gauge(val,title="Resulting confidence"):
    fig=go.Figure(go.Indicator(mode="gauge+number",value=val,number={"suffix":"/100","font":{"size":30,"color":"#0E2A30","family":"IBM Plex Sans"}},
        gauge={"axis":{"range":[0,100],"tickwidth":1,"tickcolor":"#9aa6a8"},"bar":{"color":"#0E2A30"},
               "bgcolor":"#fff","borderwidth":0,
               "steps":[{"range":[0,40],"color":"#F7D9D3"},{"range":[40,75],"color":"#F6E6C8"},{"range":[75,100],"color":"#CDEBDD"}],
               "threshold":{"line":{"color":"#FF3621","width":3},"thickness":0.85,"value":val}}))
    fig.update_layout(height=240,margin=dict(l=14,r=14,t=44,b=4),font=dict(family="IBM Plex Sans"),title=dict(text=title,font=dict(size=14)))
    return fig
def verdict_dag(rec):
    """A facility-specific decision DAG: which evidence signals drive THIS grade (not population health)."""
    sh=bool(rec.get('spec_hit')); th=bool(rec.get('text_hit')); ns=_int(rec.get('n_sources')) or 0
    g=rec.get('grade'); cf=int(rec.get('confidence') or 0)
    ev=[("Specialty code",sh,0.06,0.84,"#2272B4"),("Equipment / procedure text",th,0.06,0.5,"#E0A02A"),(f"{ns} independent source(s)",ns>=1,0.06,0.16,"#119A6B")]
    vx,vy=0.9,0.5; fig=go.Figure()
    for lbl,on,x,y,col in ev:
        c=col if on else "#D7DCDC"
        fig.add_annotation(x=vx,y=vy,ax=x,ay=y,xref="x",yref="y",axref="x",ayref="y",showarrow=True,arrowhead=3,arrowsize=1.1,arrowwidth=4.5 if on else 1.2,arrowcolor=c,opacity=1 if on else .45)
    fig.add_trace(go.Scatter(x=[e[2] for e in ev],y=[e[3] for e in ev],mode="markers+text",
        marker=dict(size=[24 if e[1] else 15 for e in ev],color=[e[4] if e[1] else "#D7DCDC" for e in ev],line=dict(color="#fff",width=2)),
        text=[("✓ " if e[1] else "✗ ")+e[0] for e in ev],textposition="middle right",textfont=dict(size=11,color="#0E2A30",family="IBM Plex Sans"),hoverinfo="text",showlegend=False))
    vcol=GC.get(g,"#9aa3af")
    fig.add_trace(go.Scatter(x=[vx],y=[vy],mode="markers+text",marker=dict(size=58,color=vcol,line=dict(color="#fff",width=3)),
        text=[f"<b>{g}</b><br>{cf}/100"],textposition="middle center",textfont=dict(size=11,color="#fff",family="IBM Plex Sans"),hoverinfo="text",showlegend=False))
    fig.update_layout(height=300,margin=dict(l=0,r=0,t=8,b=0),plot_bgcolor="#fff",paper_bgcolor="#fff",
        xaxis=dict(visible=False,range=[-0.02,1.22]),yaxis=dict(visible=False,range=[-0.02,1.02]),font=dict(family="IBM Plex Sans"))
    return fig
def why_verdict(rec, kk, ctx_extra=""):
    """Reusable 'why this grade' block: ground truth + SHAP-style attribution + verbatim evidence + sources,
    then on demand: reasoning text + probability gauge + causal DAG. Used on every facility card."""
    g=rec.get('grade'); cf=int(rec.get('confidence') or 0)
    sh=bool(rec.get('spec_hit')); th=bool(rec.get('text_hit')); ns=_int(rec.get('n_sources')) or 0
    st.markdown(f"**Verdict: _{g}_ · confidence {cf}/100.** Graded only from the facility's own record — confidence is the probability the claim is genuine, not a guarantee.")
    st.markdown("**Ground truth — the exact signals from the dataset:**")
    gt=pd.DataFrame({"Evidence signal":["Matching clinical specialty code","Equipment / procedure text match","Independent corroborating sources","Capability vs facility-type"],
        "From the data":["✅ present" if sh else "— absent","✅ present" if th else "— absent",f"{ns} source(s)","⚠️ contradiction" if g=='WEAK/SUSPICIOUS' else "✓ consistent"]})
    st.dataframe(gt,use_container_width=True,hide_index=True)
    st.markdown("**Evidence attribution — how the confidence score is built (SHAP-style contribution):**")
    st.markdown(attribution_html(sh,th,ns),unsafe_allow_html=True)
    raw=_v(rec.get('evidence_citation'))
    if raw:
        s=str(raw)
        if "specialty code present" in s or " | " in s:
            chips=[]
            for p in [x.strip() for x in s.split(" | ") if x.strip()]:
                if p=="specialty code present": chips.append("a matching clinical <b>specialty code</b> in the registry")
                else:
                    tk=p.split()
                    if len(tk)>2: tk=tk[1:-1]   # drop the regex-cut partial words at each edge
                    if tk: chips.append('the phrase “…'+" ".join(tk)+'…”')
            disp=" &nbsp;·&nbsp; ".join(chips) if chips else s
        else: disp=s
        st.markdown("<div class='evid'>📄 <b>In the facility's own record:</b> "+disp+"</div>",unsafe_allow_html=True)
    ns=int(rec.get('n_sources') or 0); stypes=_v(rec.get('source_types')); urls=rank_sources(rec.get('source_urls'),8)
    st.markdown(f"**Where the evidence comes from — {ns} independent source type(s).** A *source* is an independent place this facility's record was found — a public web directory, the facility's own website, or a medical / government registry. More independent sources agreeing → higher confidence.")
    if stypes: st.caption("Source types in the data: "+str(stypes))
    if urls:
        st.markdown("**The actual source pages:**")
        for u in urls: st.markdown(f"- [{u[:80]}]({u})")
    else:
        st.caption("No source URLs were captured for this particular record — the count reflects distinct source *types*.")
    if st.button("🧠 Explain step-by-step (evidence · probability · what would change it)",key="ex"+kk):
        with st.spinner("Reasoning agent…"):
            st.session_state["rx"+kk]=run_agent("reasoning",
                f"Facility '{rec.get('name')}' ({rec.get('ftype')}, {rec.get('address_city')}) is graded {g} (confidence {cf}/100) for '{rec.get('capability')}'. "
                f"GROUND TRUTH from the dataset: specialty-code match={sh}, equipment/procedure-text match={th}, independent sources={ns}. Verbatim evidence: {rec.get('evidence_citation')}. {ctx_extra} "
                f"In formatted markdown, explain for a non-technical reader: (1) read these ground-truth signals and give the PROBABILITY in plain words that the facility genuinely provides this; (2) the key caveat that a claim in scraped/listed text is NOT proof it is delivered (claimed ≠ delivered); (3) how trustworthy the {ns} cited source(s) are; (4) exactly what extra evidence would raise or lower the confidence. Bold a one-line bottom verdict. Do NOT discuss unrelated population-health statistics — stay on this facility.")
    if st.session_state.get("rx"+kk):
        st.info(st.session_state["rx"+kk])
        pg1,pg2=st.columns([1,1.15])
        with pg1:
            st.markdown("**Probability the claim is genuine**")
            st.plotly_chart(conf_gauge(cf,"confidence"),use_container_width=True,key="gg"+kk)
        with pg2:
            st.markdown("**How the evidence builds this verdict**")
            st.plotly_chart(verdict_dag(rec),use_container_width=True,key="cg"+kk)
@st.cache_data(ttl=600, show_spinner=False)
def kpis():
    try:
        a=q(f"SELECT count(*) n,sum(CASE WHEN grade='STRONG' THEN 1 ELSE 0 END) s FROM {GOLD}.gold_facility_capability_trust")
        g=q(f"SELECT sum(CASE WHEN classification='APPARENT CARE GAP' THEN 1 ELSE 0 END) gaps FROM {GOLD}.gold_district_gaps")
        return f"{int(a['n'][0]):,}",f"{int(a['s'][0]):,}",f"{int(g['gaps'][0]):,}"
    except Exception: return "—","—","—"
@st.cache_data(ttl=600, show_spinner=False)
def caplist():
    try: return q(f"SELECT capability,count(*) n FROM {GOLD}.gold_facility_capability_trust GROUP BY capability ORDER BY n DESC")['capability'].tolist()
    except Exception: return ["maternity","emergency","trauma","ICU","oncology","dialysis","NICU"]
SRC="databricks_virtue_foundation_dataset_dais_2026.virtue_foundation_dataset"
@st.cache_data(ttl=3600, show_spinner=False)
def geocode(loc):
    """Resolve any city / district / place to a lat-lon centroid from the India-Post directory (165k offices, every district)."""
    loc=re.sub(r"[^a-z0-9 ]","",(loc or "").strip().lower())
    if len(loc)<3: return None
    try:
        d=q(f"""SELECT avg(cast(latitude AS double)) la, avg(cast(longitude AS double)) lo, count(*) n
                FROM {SRC}.india_post_pincode_directory
                WHERE (lower(district)='{loc}' OR lower(district) LIKE '%{loc}%' OR lower(officename) LIKE '%{loc}%' OR lower(regionname) LIKE '%{loc}%')
                  AND cast(latitude AS double) BETWEEN 6 AND 38 AND cast(longitude AS double) BETWEEN 67 AND 98""")
        if not d.empty and d['n'][0] and d['la'][0] is not None: return float(d['la'][0]),float(d['lo'][0])
    except Exception: pass
    try:
        d=q(f"""SELECT avg(latitude) la, avg(longitude) lo, count(*) n FROM {GOLD}.gold_facility_capability_trust
                WHERE lower(address_city) LIKE '%{loc}%' AND latitude BETWEEN 6 AND 38""")
        if not d.empty and d['n'][0] and d['la'][0] is not None: return float(d['la'][0]),float(d['lo'][0])
    except Exception: pass
    return None
@st.cache_data(ttl=600, show_spinner=False)
def speclist():
    try: return q(f"SELECT specialty FROM {GOLD}.gold_facility_specialty GROUP BY specialty ORDER BY count(*) DESC")['specialty'].tolist()
    except Exception: return caplist()
@st.cache_data(ttl=600, show_spinner=False)
def allcaps():
    try: return sorted(q(f"SELECT capability FROM {GOLD}.gold_all_gaps GROUP BY capability")['capability'].tolist(), key=lambda s:s.lower())
    except Exception: return caplist()
def alpha_pick(options,key,label="Capability / specialty"):
    """A–Z letter filter, then a capability dropdown — makes all capabilities reachable."""
    letters=sorted({o[0].upper() for o in options if o and o[0].isalpha()})
    c1,c2=st.columns([1,5])
    L=c1.selectbox("A–Z",letters,index=(letters.index("M") if "M" in letters else 0),key=key+"L")
    opts=[o for o in options if o and o[0].upper()==L] or options
    return c2.selectbox(label,opts,key=key+"S")

# ---- grounded answer engine (example questions + copilot) ----
CAPS_KW={"dialysis":"dialysis","maternity":"maternity","emergency":"emergency","nicu":"NICU","oncology":"oncology","trauma":"trauma","icu":"ICU"}
def ground(ql):
    ctx=""; capn=next((CAPS_KW[k] for k in CAPS_KW if k in ql), None)
    try:
        if capn and any(w in ql for w in ["gap","desert","real","data-poor","district"]):
            d=q(f"SELECT classification,count(*) n FROM {GOLD}.gold_district_gaps WHERE capability='{capn}' GROUP BY classification")
            ctx+=f"District gap classification for {capn}: {d.to_dict('records')}. "
        if capn and any(w in ql for w in ["strong","partial","evidence","claim","suspicious","weak"]):
            d=q(f"SELECT grade,count(*) n FROM {GOLD}.gold_facility_capability_trust WHERE capability='{capn}' GROUP BY grade")
            ctx+=f"{capn} grade counts: {d.to_dict('records')}. "
        if any(w in ql for w in ["flag","review","quality","issue","contradiction","capacity","fix","readiness"]):
            d=q(f"SELECT count(*) n FROM {GOLD}.gold_data_readiness"); ctx+=f"{int(d['n'][0])} facilities flagged for data review. "
        m=re.search(r'(fortis|apollo|aiims|max|manipal|kims|narayana|medanta|sunshine|rainbow|care)', ql)
        if m:
            d=q(f"SELECT name,capability,grade,confidence,evidence_citation FROM {GOLD}.gold_facility_capability_trust WHERE lower(name) LIKE '%{m.group(1)}%' AND grade<>'NO CLAIM' LIMIT 8")
            ctx+="Facility evidence — "+"; ".join(f"{r['name']} {r['capability']}={r['grade']}({int(r['confidence'])})" for _,r in d.iterrows())+". "
        m2=re.search(r'\b(?:in|near|at|around|within|from)\s+([a-z][a-z]{2,20})', ql)
        place=m2.group(1) if m2 else None
        if place and place not in ("the","this","that","india","what","real","each","care","need","with","data"):
            pq=place.replace("'","")
            d=q(f"SELECT grade,count(*) n FROM {GOLD}.gold_facility_capability_trust WHERE lower(address_city) LIKE '%{pq}%' AND grade<>'NO CLAIM' GROUP BY grade")
            tot=int(d['n'].sum()) if not d.empty else 0
            if tot>0:
                top=q(f"SELECT capability,grade,count(*) n FROM {GOLD}.gold_facility_capability_trust WHERE lower(address_city) LIKE '%{pq}%' AND grade<>'NO CLAIM' GROUP BY capability,grade ORDER BY n DESC LIMIT 12")
                ctx+=f"REAL DATA — facilities in {place.title()}: {tot} graded capability claims; by grade {d.to_dict('records')}; top capabilities {top.to_dict('records')}. "
            else:
                ctx+=f"IMPORTANT: our data has NO facility records in '{place.title()}'. Say this plainly and do NOT invent any numbers for it. "
    except Exception: pass
    if any(w in ql for w in ["caus","stunting","why","anc","correlation","confound","probab"]):
        ctx+=CAUSAL_CTX+" "
    return ctx
_GREET=re.compile(r'^(hi+|hey+|hello+|yo|hola|namaste|good (morning|evening|afternoon)|sup|thanks|thank you|ty|ok|okay|test|hii)\b',re.I)
def answer(qtext):
    qt=(qtext or "").strip()
    if len(qt)<4 or _GREET.match(qt):
        return ("👋 **Hi — I'm the facilitiesHelp.io Copilot.** I answer from the facility data with cited evidence and honest confidence. Try:\n\n"
                "- *Does Fortis have oncology, and how strong is the evidence?*\n"
                "- *Is the NICU care gap real, or just data-poor?*\n"
                "- *Dialysis near Guntur*\n"
                "- *Which data-quality issues are most common?*\n"
                "- *Is sanitation a real cause of child stunting?*")
    ctx=ground(qt.lower())
    if not ctx:
        return run_agent("copilot", f"Question: {qtext}\n\nWe found NO matching record in our gold tables for this exact question. Do NOT invent any statistics, percentages, rates or examples. In 2–3 short sentences, say plainly that you don't have specific data for that, then suggest the user ask about a specific facility, a city + care need, a district care gap, a data-quality issue, or an NFHS causal finding. Friendly and brief.", 320)
    return run_agent("copilot", f"Question: {qtext}\n\nGrounding data from our Databricks gold tables:\n{ctx}\n\nAnswer using ONLY this grounding data; cite its numbers and explain them in plain words; state confidence; distinguish correlation from causation; never invent statistics or examples; flag weak evidence honestly.", 540)
def answer_chart(ql):
    """Render the chart(s) most relevant to a Copilot question — evidence, gaps, or causation."""
    ql=ql.lower(); capn=next((CAPS_KW[k] for k in CAPS_KW if k in ql),None)
    try:
        m2=re.search(r'\b(?:in|near|at|around|within|from)\s+([a-z][a-z]{2,20})', ql)
        place=m2.group(1) if m2 else None
        if place and place not in ("the","this","that","india","what","real","each","care","need","with","data") and not any(w in ql for w in ["caus","stunt","sanitation","confound","correlation"]):
            pq=place.replace("'","")
            d=q(f"SELECT capability,grade,count(*) n FROM {GOLD}.gold_facility_capability_trust WHERE lower(address_city) LIKE '%{pq}%' AND grade IN ('STRONG','PARTIAL','WEAK/SUSPICIOUS') GROUP BY capability,grade")
            if not d.empty:
                fig=px.bar(d,x="capability",y="n",color="grade",barmode="stack",color_discrete_map=GC,category_orders={"grade":["STRONG","PARTIAL","WEAK/SUSPICIOUS"]})
                fig.update_layout(height=320,margin=dict(l=0,r=0,t=10,b=0),legend=dict(orientation="h",y=1.05,title=""),font=dict(family="IBM Plex Sans"),xaxis_title="",yaxis_title="claims")
                st.caption(f"Evidence grades for facilities in **{place.title()}** — from the data (not all-India):")
                st.plotly_chart(fig,use_container_width=True); return True
            else:
                st.info(f"No facility records found in **{place.title()}** in the dataset."); return True
        if any(w in ql for w in ["caus","stunt","sanitation","confound","correlation","schooling","anc","overweight","probab"]):
            st.caption("Correlation → causation across 4 estimators (bars collapsing to 0 were confounded):")
            st.plotly_chart(causal_effects_chart(),use_container_width=True)
            cp=capn if capn in _FOCUS else "maternity"
            st.caption(f"Causal levers relevant to {cp} (🟢 causal · 🔴 confounded):")
            st.plotly_chart(causal_plot(cp),use_container_width=True,key="ans_causal")
            return True
        if capn and any(w in ql for w in ["gap","desert","district","real","data-poor","need","where"]):
            cls=q(f"SELECT classification,count(*) n FROM {GOLD}.gold_district_gaps WHERE capability='{capn}' GROUP BY classification")
            fig=px.pie(cls,values="n",names="classification",hole=.58,color="classification",color_discrete_map={"APPARENT CARE GAP":"#FF3621","DATA-POOR":"#B6C0C2","EVIDENCED SUPPLY":"#119A6B"})
            fig.update_traces(textinfo="value",textfont_size=14)
            fig.update_layout(height=300,margin=dict(l=0,r=0,t=10,b=0),legend=dict(orientation="h",y=-.1,title=""),font=dict(family="IBM Plex Sans"))
            st.caption(f"{capn} districts by classification:")
            st.plotly_chart(fig,use_container_width=True); return True
        if capn or any(w in ql for w in ["grade","evidence","strong","partial","trust","claim","suspicious"]):
            wc=f"WHERE capability='{capn}' AND grade IN ('STRONG','PARTIAL','WEAK/SUSPICIOUS')" if capn else "WHERE grade IN ('STRONG','PARTIAL','WEAK/SUSPICIOUS')"
            d=q(f"SELECT capability,grade,count(*) n FROM {GOLD}.gold_facility_capability_trust {wc} GROUP BY capability,grade")
            fig=px.bar(d,x="capability",y="n",color="grade",barmode="stack",color_discrete_map=GC,category_orders={"grade":["STRONG","PARTIAL","WEAK/SUSPICIOUS"]})
            fig.update_layout(height=300,margin=dict(l=0,r=0,t=10,b=0),legend=dict(orientation="h",y=1.05,title=""),font=dict(family="IBM Plex Sans"),xaxis_title="",yaxis_title="claims")
            st.caption("Evidence grades for this question:")
            st.plotly_chart(fig,use_container_width=True); return True
    except Exception: pass
    return False
QUESTIONS={
 T1:[("Easy","Does Fortis have oncology, and how strong is the evidence?"),("Medium","Which capabilities have the most STRONG-evidence facilities?"),("Hard","Show me clinics suspiciously claiming ICU and why they're flagged."),("Difficult","For maternity, how many facilities are strong vs partial, and what makes evidence 'strong'?")],
 T2:[("Easy","How many districts are real NICU care gaps?"),("Medium","Nationally, is the maternity shortfall a real gap or just data-poor?"),("Hard","Is sanitation a real cause of child stunting, or just correlation?"),("Difficult","If ANC4 rises 10 points in a district, what happens to institutional births — and how confident are we causally?")],
 T3:[("Easy","Dialysis near Jaipur"),("Medium","Emergency care near Patna with strong evidence"),("Hard","Best NICU within 100 km of Hyderabad and why"),("Difficult","Oncology near Mumbai but the top option has weak evidence — what should a coordinator do?")],
 T4:[("Easy","How many facilities are flagged for review?"),("Medium","What kinds of data-quality issues are most common?"),("Hard","Which contradictions should we fix first, and why?"),("Difficult","Which high-visibility facilities have the most issues, and what's the leverage of fixing them?")],
}
EMO={"Easy":"🟢","Medium":"🟡","Hard":"🟠","Difficult":"🔴"}
def example_questions(tk):
    with st.expander("💡 Example questions (Easy → Difficult) — click any to ask the Copilot", expanded=False):
        for lvl,qq in QUESTIONS.get(tk,[]):
            if st.button(f"{EMO[lvl]} {lvl} — {qq}", key=f"eq{tk}{lvl}", use_container_width=True):
                with st.spinner("Agent answering from the data…"): st.session_state["qa"+tk]=(qq, answer(qq))
        if st.session_state.get("qa"+tk):
            qq,aa=st.session_state["qa"+tk]; st.markdown(f"**Q — {qq}**"); st.success(aa)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("""<div style='display:flex;align-items:center;gap:11px;margin:0 0 6px'>
<div style='width:33px;height:33px;border-radius:9px;background:linear-gradient(150deg,#FF3621,#FF6F52);display:flex;align-items:center;justify-content:center;color:#fff;font-family:IBM Plex Sans;font-weight:700;font-size:18px;box-shadow:0 7px 16px -8px rgba(255,54,33,.9)'>F</div>
<div><div style='font-family:IBM Plex Sans;font-weight:600;font-size:15.5px;color:#0E2A30;letter-spacing:-.01em;line-height:1.15'>facilitiesHelp.io</div>
<div style='font-family:IBM Plex Mono;font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:#8FA0A4;margin-top:3px'>Trust · Desert · Cause</div></div></div>""", unsafe_allow_html=True)
st.sidebar.caption("Turn messy facility records into decisions you can trust.")
track=st.sidebar.radio("Track",[T1,T2,T3,T4,T5,T6])
mode=st.sidebar.radio("Mode",["Insights","Simulation"],horizontal=True)
user=st.sidebar.text_input("Your name (saved work)","planner")
st.sidebar.divider()
st.sidebar.caption("Databricks · Unity Catalog · SQL Warehouse · gold medallion · Model Serving (Llama 4 Maverick) · AI/BI Genie · 3 modular agents. Every claim cites facility text.")

_n,_s,_g=kpis()
st.markdown(f"""<div class="hero"><div class="herowrap">
<div class="heroL"><div class="eyebrow"><span class="dot"></span>Virtue Foundation · Apps &amp; Agents for Good 2026 · Live on Databricks Free Edition</div>
<h1>Decisions you can trust from 10,000 messy facility records</h1>
<p>Every capability claim is graded from the facility's own words, scored for confidence, and weighed against district need — so a planner acts on evidence, not hope.</p></div>
<div class="heroR"><div class="kpi"><b>{_n}</b><span>graded claims</span></div><div class="kpi"><b>{_s}</b><span>strong-evidence claims</span></div><div class="kpi"><b>{_g}</b><span>real care gaps</span></div></div>
</div></div>
<div class="ctx">{track}<span class="sep">/</span>{mode} mode<span class="sep">/</span>complete dataset · 2,580 specialties</div>""", unsafe_allow_html=True)

# ==================== TRACK 1 · FACILITY TRUST ====================
if track==T1:
    if mode=="Insights":
        st.markdown("#### Can this facility actually do what it claims?")
        st.caption("Search by **name, city, or specialty** (e.g. *Fortis*, *Hyderabad cardiology*, *AIIMS Delhi*). Each capability is graded from the facility's own text, with the evidence and confidence shown.")
        st.markdown(GLEG,unsafe_allow_html=True)
        name=st.text_input("Search a facility, city or specialty","Fortis",label_visibility="collapsed")
        rows=[]
        toks=[t for t in re.split(r"[^a-z0-9]+", (name or "").lower()) if len(t)>=3]
        if not toks:
            st.info("Type at least 3 letters — a facility name, a city, or a specialty.")
        else:
            where=" OR ".join(f"(c.search_text LIKE '%{t}%' OR lower(t.name) LIKE '%{t}%')" for t in toks)
            df=q(f"""SELECT t.name,t.capability,t.grade,t.confidence,t.evidence_citation,t.ftype,t.address_city,t.source_urls,t.source_types,t.cluster_id,
                     t.spec_hit,t.text_hit,t.n_sources,
                     c.full_address,c.phone,c.website,c.email,c.capacity,c.n_doctors,c.year_est,c.followers,c.specialties_str,c.search_text
                     FROM {GOLD}.gold_facility_capability_trust t LEFT JOIN {GOLD}.gold_facility_contact c ON t.cluster_id=c.cluster_id
                     WHERE {where} ORDER BY t.confidence DESC LIMIT 1500""")
            if df.empty:
                st.warning(f"No facility matched “{name}”. Try a broader term — a chain (*Fortis*, *Apollo*), a city (*Hyderabad*), or a specialty (*cardiology*).")
            else:
                df["_txt"]=(df["search_text"].fillna("")+" "+df["name"].fillna("")).str.lower()
                df["_city"]=df["address_city"].fillna("").str.lower(); df["_nm"]=df["name"].fillna("").str.lower()
                def _sc(rr):
                    s=0
                    for t in toks:
                        if t in rr["_city"]: s+=4      # a city/location match dominates
                        elif t in rr["_nm"]: s+=3      # then a facility-name match
                        elif t in rr["_txt"]: s+=1     # a stray mention in description counts least
                    return s
                df["_score"]=df.apply(_sc,axis=1)
                df=df[df["_score"]>0].copy(); df["gk"]=df["cluster_id"].fillna(df["name"])
                df=df.sort_values(["_score","confidence"],ascending=False)
                keep=df.drop_duplicates("gk")["gk"].head(12).tolist(); df=df[df["gk"].isin(keep)]
                rows=df.to_dict("records")
                _cids=[str(c) for c in df["cluster_id"].dropna().unique().tolist()][:12]; _spall={}
                if _cids:
                    _inl=",".join("'"+c.replace("'","")[:60]+"'" for c in _cids)
                    try:
                        for _c,_gg in q(f"SELECT cluster_id,specialty,grade,confidence FROM {GOLD}.gold_facility_specialty WHERE cluster_id IN ({_inl}) ORDER BY confidence DESC,specialty").groupby("cluster_id"): _spall[str(_c)]=_gg
                    except Exception: pass
                st.caption(f"Showing the top {df['gk'].nunique()} matching facilities (best match first) — searched across the complete dataset.")
                for gk,gdf in df.groupby("gk",sort=False):
                    head=gdf.iloc[0]
                    st.markdown(f"### {head['name']}")
                    st.caption(f"{head.get('ftype') or 'facility'} · {head.get('address_city') or '—'}")
                    fa=facacts(head)
                    if fa: st.markdown(fa,unsafe_allow_html=True)
                    spec=_v(head.get("specialties_str"))
                    if spec: st.markdown(f"<div class='specs'><b>Specialties on file:</b> {str(spec)[:220]}</div>",unsafe_allow_html=True)
                    for ri,r in gdf.iterrows():
                        with st.container(border=True):
                            st.markdown(f"<div class='claimrow' style='margin:4px 0 6px'><b>{r['capability'].upper()}</b>&nbsp;&nbsp;{badge(r['grade'],r['confidence'])}<span class='ico' title=\"{GRADE_HELP}\">i</span></div>",unsafe_allow_html=True)
                            kk=f"{gk}_{r['capability']}_{ri}".replace(" ","")
                            with st.expander("Why this verdict — ground truth, reasoning, sources & causal graph"):
                                why_verdict(r,kk,ctx_extra=f"Specialties on file: {spec}. Beds {_int(head.get('capacity'))}, doctors {_int(head.get('n_doctors'))}.")
                                st.divider(); st.caption("Human review (optional) — saved to the audit log; the model grade is never overwritten.")
                                cc1,cc2=st.columns([3,1])
                                ov=cc1.selectbox("Your verdict",["— agree with model","STRONG","PARTIAL","WEAK/SUSPICIOUS"],key="o"+kk,label_visibility="collapsed")
                                if cc2.button("Save",key="s"+kk): save_action(user,"review_decision","trust",head['name'],{"capability":r["capability"],"model":r["grade"],"human":None if ov.startswith("—") else ov})
                    cid=_v(head.get('cluster_id')); sp=_spall.get(str(cid)) if cid else None
                    if sp is not None and not sp.empty:
                        if True:
                            with st.expander(f"📋 Complete graded profile — all {len(sp)} clinical specialties this facility lists"):
                                spv=sp.sort_values("confidence")
                                figsp=px.bar(spv,x="confidence",y="specialty",orientation="h",color="grade",
                                    color_discrete_map={**GC,"CLAIMED":"#B6C0C2"},category_orders={"grade":["STRONG","PARTIAL","CLAIMED"]})
                                figsp.update_layout(height=max(240,24*len(sp)),margin=dict(l=0,r=12,t=8,b=0),font=dict(family="IBM Plex Sans"),legend=dict(orientation="h",y=1.02,title=""),xaxis_title="confidence /100",yaxis_title="")
                                st.plotly_chart(figsp,use_container_width=True,key="sp"+str(gk))
                                st.caption("Every specialty the facility lists, graded from its own evidence — STRONG = corroborated in free-text + ≥2 sources · PARTIAL = one signal · CLAIMED = listed only.")
        if rows:
            ai_button("t1ins","insights","Facility search '"+name+"'. Graded capabilities (facility · capability · grade · confidence): "+"; ".join(f"{r['name']} {r['capability']}={r['grade']}({int(r['confidence'])})" for r in rows[:10])+". Summarise which facilities are most trustworthy for which capabilities, and flag any that should be treated with caution and why. Stay strictly about these facilities — do NOT mention population-health statistics such as sanitation, stunting, ANC visits or child marriage.","Summarise trust for these facilities")
        st.divider(); st.markdown("#### Evidence quality across the dataset")
        d=q(f"SELECT capability,grade,count(*) n FROM {GOLD}.gold_facility_capability_trust WHERE grade IN ('STRONG','PARTIAL','WEAK/SUSPICIOUS') GROUP BY capability,grade")
        order=d.groupby("capability")["n"].sum().sort_values().index.tolist()
        fig=px.bar(d,x="n",y="capability",color="grade",orientation="h",barmode="stack",color_discrete_map=GC,category_orders={"grade":["STRONG","PARTIAL","WEAK/SUSPICIOUS"],"capability":order})
        fig.update_layout(margin=dict(l=0,r=12,t=44,b=0),height=560,legend=dict(orientation="h",yanchor="bottom",y=1.01,x=0,title=""),font=dict(family="IBM Plex Sans"),xaxis_title="graded claims",yaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
        st.caption("These **22 high-stakes capabilities** get an extra contradiction check — but we grade **every one of the 2,580 specialties** a facility lists (open any facility's full profile above). Most claims are PARTIAL; STRONG needs ≥2 independent evidence types + a 2nd source.")
        info_pop(GRADE_HELP,"ⓘ  what makes a facility STRONG / PARTIAL / WEAK")
        cda,cdb=st.columns([1,1.3])
        with cda:
            st.markdown("##### Overall grade mix")
            gd=q(f"SELECT grade,count(*) n FROM {GOLD}.gold_facility_capability_trust WHERE grade IN ('STRONG','PARTIAL','WEAK/SUSPICIOUS') GROUP BY grade")
            figd=px.pie(gd,values="n",names="grade",hole=.6,color="grade",color_discrete_map=GC)
            figd.update_traces(textinfo="percent",textfont_size=13)
            figd.update_layout(height=300,margin=dict(l=0,r=0,t=6,b=0),legend=dict(orientation="h",y=-.05,title=""),font=dict(family="IBM Plex Sans"))
            st.plotly_chart(figd,use_container_width=True)
            info_pop(GRADE_HELP,"ⓘ  what STRONG / PARTIAL / WEAK mean")
        with cdb:
            st.markdown("##### Every specialty in the data — all 2,580 graded")
            sb=q(f"SELECT specialty,n_facilities FROM {GOLD}.gold_specialty_counts ORDER BY n_facilities DESC LIMIT 14").sort_values("n_facilities")
            figs=px.bar(sb,x="n_facilities",y="specialty",orientation="h",text="n_facilities",color_discrete_sequence=["#2272B4"])
            figs.update_layout(height=300,margin=dict(l=0,r=12,t=6,b=0),font=dict(family="IBM Plex Sans"),xaxis_title="facility mentions",yaxis_title="")
            st.plotly_chart(figs,use_container_width=True)
        st.caption("We trust-grade **every one of the 2,580 specialties** a facility lists — open any facility above to see its complete graded profile. The 7 highest-stakes acute capabilities (maternity, NICU, emergency, ICU, oncology, trauma, dialysis) additionally get a contradiction check that flags a small clinic over-claiming acute care as WEAK/SUSPICIOUS.")
    else:
        st.markdown("#### What-if: how does a facility earn a higher trust grade?")
        st.caption("Trust isn't a black box. Toggle the evidence a facility could add — a matching clinical **specialty code**, **equipment/procedure** text, a **2nd independent source** — and watch the grade, the confidence probability, and the reasoning update. This is the same evidence logic applied to every claim in the data.")
        cap=alpha_pick(allcaps(),"t1simcap","Capability / specialty"); capq=cap.replace("'","''")
        add=st.multiselect("Evidence the facility adds",["matching specialty code","matching equipment/procedure text","a 2nd independent source"])
        hs="matching specialty code" in add; ht="matching equipment/procedure text" in add; src="a 2nd independent source" in add
        types=int(hs)+int(ht)
        if types>=2 and src: grade,conf="STRONG",90
        elif types>=1 and src: grade,conf="PARTIAL",66
        elif types>=1: grade,conf="PARTIAL",50
        else: grade,conf="NO CLAIM",6
        g1,g2=st.columns([1,1])
        with g1:
            st.markdown("##### Resulting verdict")
            st.markdown(f"<div style='margin:6px 0 10px'>{badge(grade if grade!='NO CLAIM' else 'WEAK/SUSPICIOUS',conf)}</div>",unsafe_allow_html=True)
            st.markdown(f"**{grade}** — {'two independent evidence types plus a corroborating source' if grade=='STRONG' else ('one evidence type'+(' plus a 2nd source' if src else '') if grade=='PARTIAL' else 'no machine-readable evidence yet')}.")
            if cap in set(caplist()):
                real=q(f"SELECT grade,count(*) n FROM {GOLD}.gold_facility_capability_trust WHERE capability='{capq}' AND grade IN ('STRONG','PARTIAL','WEAK/SUSPICIOUS') GROUP BY grade")
            else:
                real=q(f"SELECT grade,count(*) n FROM {GOLD}.gold_facility_specialty WHERE specialty='{capq}' AND grade IN ('STRONG','PARTIAL','CLAIMED') GROUP BY grade")
            if not real.empty:
                tot=int(real['n'].sum()); strong=int(real[real.grade=='STRONG']['n'].sum())
                st.caption(f"Across the dataset, **{strong:,} of {tot:,}** graded {cap} claims currently reach STRONG.")
        with g2:
            st.plotly_chart(conf_gauge(conf,f"{cap} · resulting confidence"),use_container_width=True)
        ai_button("t1sim","simulation",
            f"A facility claims the capability '{cap}'. Evidence types present in this scenario: {add or 'none'}. Under our deterministic rubric this yields grade {grade} at confidence ~{conf}/100. {CAUSAL_CTX} "
            f"In markdown: explain what this grade means PROBABILISTICALLY, exactly what evidence would push it to STRONG, and the correlation-vs-causation caveat in inferring a real clinical capability from claimed/scraped text. Bold the bottom line.",
            "Reasoning agent: explain this grade, its evidence & probability","info")

# ==================== TRACK 2 · MEDICAL DESERT ====================
elif track==T2:
    cap=alpha_pick(allcaps(),"t2cap","Capability / specialty — all 2,518"); capq=cap.replace("'","''")
    g=q(f"""SELECT district_n,n_facilities,n_strong,n_partial,strong_partial_share,classification FROM {GOLD}.gold_all_gaps
            WHERE capability='{capq}' ORDER BY CASE classification WHEN 'APPARENT CARE GAP' THEN 0 WHEN 'DATA-POOR' THEN 1 ELSE 2 END,n_facilities DESC""")
    if mode=="Insights":
        a,b,c=st.columns(3)
        a.metric("🔴 Real care gaps",int((g.classification=="APPARENT CARE GAP").sum()))
        b.metric("⚪ Data-poor (can't tell)",int((g.classification=="DATA-POOR").sum()))
        c.metric("🟢 Evidenced supply",int((g.classification=="EVIDENCED SUPPLY").sum()))
        st.caption("**Real gap** = enough facilities but little trustworthy evidence. **Data-poor** = too few records to judge — *not* 'no care'.")
        col1,col2=st.columns([1,1])
        with col1:
            cls=g.groupby("classification").size().reset_index(name="n")
            fig=px.pie(cls,values="n",names="classification",hole=.58,color="classification",
                color_discrete_map={"APPARENT CARE GAP":"#FF3621","DATA-POOR":"#B6C0C2","EVIDENCED SUPPLY":"#119A6B"})
            fig.update_traces(textinfo="value",textfont_size=14)
            fig.update_layout(margin=dict(l=0,r=0,t=46,b=0),height=300,legend=dict(orientation="h",yanchor="bottom",y=1.02,x=0,title=""),font=dict(family="IBM Plex Sans"))
            st.markdown(f"##### {cap} — districts by classification")
            st.plotly_chart(fig,use_container_width=True)
        with col2:
            st.markdown("##### Top capabilities by classification (of all 2,518)")
            def _gapbar(cls,color):
                dd=q(f"SELECT capability, sum(CASE WHEN classification='{cls}' THEN 1 ELSE 0 END) n FROM {GOLD}.gold_all_gaps GROUP BY capability ORDER BY n DESC LIMIT 15").sort_values("n")
                fg=px.bar(dd,x="n",y="capability",orientation="h",text="n",color_discrete_sequence=[color])
                fg.update_layout(height=300,margin=dict(l=0,r=10,t=6,b=0),font=dict(family="IBM Plex Sans"),xaxis_title="districts",yaxis_title="")
                return fg
            gt1,gt2,gt3=st.tabs(["🔴 Real care gaps","⚪ Data-poor","🟢 Evidenced supply"])
            with gt1: st.plotly_chart(_gapbar("APPARENT CARE GAP","#FF3621"),use_container_width=True,key="gb1")
            with gt2: st.plotly_chart(_gapbar("DATA-POOR","#B6C0C2"),use_container_width=True,key="gb2")
            with gt3: st.plotly_chart(_gapbar("EVIDENCED SUPPLY","#119A6B"),use_container_width=True,key="gb3")
        st.caption("Districts, classified. Below: the actual facilities offering this capability, with their capacity, doctors and equipment.")
        st.dataframe(g.head(40),use_container_width=True,hide_index=True,height=200)
        _ft,_col=("gold_facility_capability_trust","capability") if cap in set(caplist()) else ("gold_facility_specialty","specialty")
        st.markdown(f"##### Facilities offering {cap} — capacity · doctors · equipment")
        ftab=q(f"""SELECT t.name AS facility, t.address_city AS city, t.district_n AS district, t.grade, t.confidence,
                   c.capacity AS beds, c.n_doctors AS doctors, c.equipment_str AS equipment
                   FROM {GOLD}.{_ft} t LEFT JOIN {GOLD}.gold_facility_contact c ON t.cluster_id=c.cluster_id
                   WHERE t.{_col}='{capq}' ORDER BY CASE t.grade WHEN 'STRONG' THEN 0 WHEN 'PARTIAL' THEN 1 ELSE 2 END, c.n_doctors DESC NULLS LAST LIMIT 300""")
        st.dataframe(ftab,use_container_width=True,hide_index=True,height=340)
        st.caption(f"{len(ftab)} graded **{cap}** facilities (top 300, evidence-first then by doctor count). Beds / doctors / equipment come from each facility's own record — blank means the facility did not report it.")
        st.markdown("#### Where the evidence is — national view (zoom & hover)")
        _ft,_col=("gold_facility_capability_trust","capability") if cap in set(caplist()) else ("gold_facility_specialty","specialty")
        mp=q(f"SELECT name,grade,confidence,latitude,longitude FROM {GOLD}.{_ft} WHERE {_col}='{capq}' AND latitude IS NOT NULL LIMIT 8000")
        _m=facmap(mp,430)
        if _m is not None: st.plotly_chart(_m,use_container_width=True)
        st.caption("🟢 strong · 🟡 partial · 🔴 suspicious. Empty regions = possible deserts (cross-check 'data-poor').")
        ai_button("t2ins","insights",f"Capability {cap}: {(g.classification=='APPARENT CARE GAP').sum()} real gaps, {(g.classification=='DATA-POOR').sum()} data-poor, {(g.classification=='EVIDENCED SUPPLY').sum()} evidenced. Worst gaps: "+", ".join(g[g.classification=='APPARENT CARE GAP']['district_n'].head(5))+". "+CAUSAL_CTX,"Brief the planner on these gaps")
        st.divider(); st.markdown("#### Will building more facilities actually fix this gap?")
        st.caption("The honest part. Our analysis of **706 NFHS districts** shows **facility count is only weakly linked to health outcomes after adjustment** — so before recommending *“build more”*, a planner should see which levers truly move the outcome. Often it's demand-side (female schooling, antenatal care), not supply.  🟢 likely-causal · 🔴 confounded (vanishes after adjusting for wealth).")
        cc1,cc2=st.columns(2)
        with cc1:
            st.plotly_chart(causal_plot(cap),use_container_width=True,key="t2_causal")
        with cc2:
            st.plotly_chart(causal_effects_chart(),use_container_width=True)
            st.caption("Correlation vs CAUSATION across 4 methods. Bars that COLLAPSE toward 0 (sanitation→stunting) were confounded; bars that SURVIVE (schooling→child-marriage, overweight→BP) are likely-causal.")
        ai_button("t2reason","reasoning",CAUSAL_CTX+f" Explain which levers are real causes vs coincidences for reducing {cap} gaps, and how confident we should be.","Reasoning agent: real levers vs coincidences","success")
    else:
        st.markdown("#### What-if: add evidenced facilities to a district")
        st.caption("Watch a district's classification flip — and read the honest caveat about what facility supply does and does not cause.")
        dg=g[g.classification!="EVIDENCED SUPPLY"]; dist=st.selectbox("District",dg["district_n"].tolist() or g["district_n"].tolist())
        row=g[g.district_n==dist].iloc[0]; addn=st.slider(f"Add STRONG {cap} facilities to {dist}",0,20,3)
        nf=int(row.n_facilities)+addn; ns=int(row.n_strong)+addn; share=(ns+int(row.n_partial))/nf if nf else 0
        newcls="DATA-POOR" if nf<5 else ("APPARENT CARE GAP" if share<0.2 else "EVIDENCED SUPPLY")
        m1,m2,m3=st.columns(3); m1.metric("Facilities",nf,addn); m2.metric("Strong share",f"{share:.0%}"); m3.metric("Classification",newcls,"→ improved" if newcls=="EVIDENCED SUPPLY" else "")
        ai_button("t2sim","simulation",f"Add {addn} STRONG {cap} facilities to {dist}: classification {row.classification}→{newcls}. {CAUSAL_CTX} Caveat: facility COUNT is only weakly linked to outcomes after adjustment (supply follows demand; scraped data has visibility bias). Advise what this really implies.","Simulation agent: what this really means","warn")
        if st.button("Save scenario"): save_action(user,"scenario","desert",dist,{"cap":cap,"add":addn,"result":newcls})

# ==================== TRACK 3 · REFERRAL COPILOT ====================
elif track==T3:
    need=alpha_pick(speclist(),"t3need","Care need — any of 2,580 specialties")
    b,cc=st.columns([2,1]); loc=b.text_input("Near (city, district or place)","Jaipur").strip()
    radius=cc.number_input("Within how many km?",min_value=2,max_value=2000,value=50,step=10,help="Increase to reach facilities in nearby towns and cities.")
    ll=geocode(loc) if loc else None
    if ll:
        la,lo=ll; needq=need.replace("'","''")
        df=q(f"""SELECT t.name,t.specialty AS capability,t.grade,t.confidence,t.evidence_citation,t.address_city,t.latitude,t.longitude,t.source_urls,
             t.spec_hit,t.text_hit,t.n_sources,c.phone,c.full_address,
             (6371*acos(least(1,cos(radians({la}))*cos(radians(t.latitude))*cos(radians(t.longitude)-radians({lo}))+sin(radians({la}))*sin(radians(t.latitude))))) dist_km
             FROM {GOLD}.gold_facility_specialty t
             LEFT JOIN {GOLD}.gold_facility_contact c ON t.cluster_id=c.cluster_id
             WHERE t.specialty='{needq}' AND t.latitude IS NOT NULL ORDER BY dist_km LIMIT 4000""")
        within=df[df.dist_km<=radius].copy()
        df=within.sort_values(["grade","dist_km"],key=lambda s:s.map({"STRONG":0,"PARTIAL":1}).fillna(2) if s.name=="grade" else s).head(30).reset_index(drop=True)
        if df.empty: st.warning(f"No {need} facilities found within {radius:.0f} km of {loc.title()}. Increase the distance box to reach nearby towns.")
        else:
            st.caption(f"**{len(within)} {need} facilities within {radius:.0f} km of {loc.title()}** (showing the nearest {len(df)}, evidence-first). **Distance** = straight-line great-circle km from {loc.title()}'s centre to each facility's GPS coordinates — raise the km box to reach nearby cities.")
        for i,r in df.iterrows():
            with st.container(border=True):
                st.markdown(f"<div class='claimrow'><b>{i+1}. {r['name']}</b>&nbsp;&nbsp;{badge(r['grade'],r['confidence'])}<span class='ico' title=\"{GRADE_HELP}\">i</span> &nbsp;·&nbsp; {r['dist_km']:.0f} km · {r['address_city']}</div>",unsafe_allow_html=True)
                meta=[]
                if _v(r.get('phone')): meta.append(f"📞 {str(r['phone'])[:40]}")
                if _v(r.get('full_address')): meta.append(f"📍 {str(r['full_address'])[:70]}")
                if meta: st.markdown("<div class='pillrow'>"+"".join(f"<span class='pill'>{m}</span>" for m in meta)+"</div>",unsafe_allow_html=True)
                st.markdown(f"<div class='evid'>📄 {clean_ev(r['evidence_citation'])}</div>",unsafe_allow_html=True)
                with st.expander("Why this verdict — ground truth, evidence, probability & causal DAG"):
                    why_verdict(r, f"ref{need}{i}".replace(" ",""))
                if st.button("Add to shortlist",key=f"sl{i}"): save_action(user,"shortlist","referral",r["name"],{"need":need,"near":loc,"grade":r["grade"],"km":round(r["dist_km"],1)})
        _m=facmap(df,360)
        if _m is not None: st.plotly_chart(_m,use_container_width=True)
        try:
            rel=q(f"SELECT B,p_b_given_a FROM {GOLD}.gold_specialty_cooccur WHERE A='{needq}' ORDER BY p_b_given_a DESC LIMIT 5")
        except Exception: rel=pd.DataFrame()
        if not rel.empty:
            st.markdown("<div class='kick'>You may also need</div>",unsafe_allow_html=True)
            st.caption(f"Facilities offering **{need}** in the data very often also offer these — a soft, data-driven suggestion (specialty co-occurrence P(B|A) across facilities, **not medical advice**):")
            chips="".join(f"<span class='pill'>{r['B']} · {int(r['p_b_given_a']*100)}% also offer it</span>" for _,r in rel.iterrows())
            st.markdown(f"<div class='pillrow'>{chips}</div>",unsafe_allow_html=True)
        # ---- Care pathway: a health concern -> the right specialist + causally-related "maybe" needs ----
        st.divider()
        CARE_MAP={
          "Child stunting (chronic malnutrition)":("stunting",["Pediatrics","Nutrition And Dietetic"],"low height-for-age — a paediatrician + child nutritionist"),
          "Child wasting (acute malnutrition)":("wasting",["Pediatrics","Nutrition And Dietetic"],"low weight-for-height — paediatric + nutrition care"),
          "Child anaemia":("child_anaemia",["Pediatrics","Pathology"],"low haemoglobin — paediatric review + blood work"),
          "Overweight / obesity":("overweight",["Endocrinology And Diabetes And Metabolism","Cardiology"],"high BMI — endocrine + cardiac risk review"),
          "High blood sugar / diabetes":("high_blood_sugar",["Endocrinology And Diabetes And Metabolism","Internal Medicine"],"raised blood glucose — diabetes care"),
          "Antenatal / pregnancy care":("anc4",["Gynecology And Obstetrics","Maternal Fetal Medicine Or Perinatology"],"antenatal visits — obstetric care"),
          "Safe institutional delivery":("inst_birth",["Gynecology And Obstetrics","Neonatology Perinatal Medicine"],"facility delivery + newborn care"),
        }
        COND_INFO={"stunting":("child stunting",["Pediatrics","Nutrition And Dietetic"]),"wasting":("child wasting",["Pediatrics","Nutrition And Dietetic"]),"child_anaemia":("child anaemia",["Pediatrics","Pathology"]),"overweight":("overweight / obesity",["Endocrinology And Diabetes And Metabolism"]),"high_blood_sugar":("high blood sugar / diabetes",["Endocrinology And Diabetes And Metabolism"]),"anc4":("low antenatal care",["Gynecology And Obstetrics"]),"inst_birth":("low institutional delivery",["Gynecology And Obstetrics","Neonatology Perinatal Medicine"])}
        CLUSTERS=[["stunting","wasting","child_anaemia"],["overweight","high_blood_sugar"],["anc4","inst_birth"]]
        st.markdown("<div class='kick'>Care pathway — start from a health concern</div>",unsafe_allow_html=True)
        st.caption("Pick a population-health concern. We route it to the right specialist near you — and because these conditions **travel together**, we flag related care as a *maybe* (Pearson correlation across 705 NFHS districts, **not a diagnosis**).")
        concern=st.selectbox("Health concern",["—"]+list(CARE_MAP),key="t3cp",label_visibility="collapsed")
        if concern!="—":
            ckey,csee,cwhy=CARE_MAP[concern]
            def _near(specs,k=3):
                sp="','".join(s.replace("'","''") for s in specs)
                d=q(f"""SELECT name,specialty,grade,confidence,address_city,
                  (6371*acos(least(1,cos(radians({la}))*cos(radians(latitude))*cos(radians(longitude)-radians({lo}))+sin(radians({la}))*sin(radians(latitude))))) dist_km
                  FROM {GOLD}.gold_facility_specialty WHERE specialty IN ('{sp}') AND latitude IS NOT NULL AND grade IN ('STRONG','PARTIAL') ORDER BY (grade='STRONG') DESC, dist_km LIMIT 60""")
                d=d[d.dist_km<=radius]
                return d.sort_values(["grade","dist_km"],key=lambda s:s.map({"STRONG":0,"PARTIAL":1}).fillna(2) if s.name=="grade" else s).head(k)
            def _show(d):
                if d.empty: st.caption(f"· no STRONG/PARTIAL facility within {radius:.0f} km — widen the distance box."); return
                st.markdown("".join(f"<div class='claimrow' style='font-size:.9rem;margin:2px 0'>{badge(r2['grade'],r2['confidence'])} &nbsp;<b>{r2['name']}</b> · {r2['specialty']} · {r2['dist_km']:.0f} km · {r2['address_city']}</div>" for _,r2 in d.iterrows()),unsafe_allow_html=True)
            st.markdown(f"**See first — {cwhy}:** {', '.join(csee)}")
            _show(_near(csee))
            shown=False
            for s in [c for cl in CLUSTERS if ckey in cl for c in cl if c!=ckey]:
                rr=q(f"SELECT r,n FROM {GOLD}.gold_condition_corr WHERE cond_a='{ckey}' AND cond_b='{s}'")
                if rr.empty or float(rr['r'][0])<0.2: continue
                if not shown:
                    st.markdown("<div class='kick' style='margin-top:.7rem'>You may also need — a maybe</div>",unsafe_allow_html=True); shown=True
                lbl,specs=COND_INFO[s]; rv=float(rr['r'][0]); nv=int(rr['n'][0])
                st.markdown(f"Because **{concern.split(' (')[0].lower()}** and **{lbl}** travel together across districts (Pearson r = **{rv:.2f}**, n = {nv}), a patient may also benefit from **{', '.join(specs)}**.")
                _show(_near(specs,2))
            if shown: st.caption("Population correlation ≠ individual diagnosis — this surfaces conditions that *co-occur* in the data so a clinician can screen for them. Confounders (e.g. household wealth) are examined in Medical Desert ▸ causal layer.")
    elif loc:
        st.warning(f"Couldn't locate “{loc}”. Try a city or district name — any of India's 700+ districts works (e.g. Guntur, Jaipur, Hyderabad, Kozhikode, Siliguri).")

# ==================== TRACK 4 · DATA READINESS ====================
elif track==T4:
    r=q(f"""SELECT name,address_city,ftype,n_issues,issue_misaligned,issue_clinic_overclaim,issue_capacity_no_doctors,issue_impossible,review_priority
            FROM {GOLD}.gold_data_readiness ORDER BY review_priority DESC LIMIT 100""")
    if mode=="Insights":
        st.metric("Facilities flagged for review",len(r))
        st.caption("High-leverage records (most issues × popularity) float to the top; each flag cites the structural contradiction.")
        counts=pd.DataFrame({"issue":["misaligned row","clinic over-claim","capacity w/o doctors","impossible value"],"n":[int(r.issue_misaligned.sum()),int(r.issue_clinic_overclaim.sum()),int(r.issue_capacity_no_doctors.sum()),int(r.issue_impossible.sum())]})
        fig=px.bar(counts,x="issue",y="n",color="n",color_continuous_scale=["#F8C9BE","#FF3621"],text="n")
        fig.update_layout(margin=dict(l=0,r=0,t=10,b=0),height=300,coloraxis_showscale=False,font=dict(family="IBM Plex Sans"),xaxis_title="",yaxis_title="facilities")
        st.markdown("##### Data-quality issues found")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(r,use_container_width=True,hide_index=True,height=300)
    else:
        fixn=st.slider("Records reviewed & fixed",0,len(r),min(20,len(r))); st.metric("Remaining flagged",len(r)-fixn,-fixn); st.progress(min(1.0,fixn/max(len(r),1)))
    pick=st.selectbox("Mark a record reviewed",["—"]+r["name"].tolist()); dec=st.radio("Decision",["valid","needs-fix","drop"],horizontal=True)
    if pick!="—" and st.button("Save review decision"): save_action(user,"review_decision","readiness",pick,{"decision":dec})

# ==================== TRACK 5 · GENIE ====================
elif track==T5:
    st.markdown("<div class='kick'>Ask the Data · grounded evidence + AI/BI Genie</div>",unsafe_allow_html=True)
    st.markdown("#### 💬 Ask anything about the data")
    st.caption("One assistant for everything. It answers with **cited evidence and honest confidence**, shows the **relevant chart**, and — on demand — lets native Databricks **AI/BI Genie** write & run the SQL. It never invents numbers.")
    if "genie" not in st.session_state: st.session_state.genie=[]
    ex=["Does Fortis have oncology, and how strong is the evidence?","Is the maternity care gap real or just data-poor?","Dialysis near Guntur","Which data-quality issues are most common?","Is sanitation a real cause of child stunting?"]
    ec=st.columns(len(ex)); gpick=None
    for i,e in enumerate(ex):
        if ec[i].button(e,key=f"gx{i}",use_container_width=True): gpick=e
    qc,bc=st.columns([6,1])
    typed=qc.text_input("Ask",key="genieq",placeholder="e.g. Best NICU within 100 km of Hyderabad — and how confident are we?",label_visibility="collapsed")
    qq=gpick or (typed if bc.button("Ask",key="genieask",use_container_width=True) else None)
    if qq:
        with st.spinner("Answering from the evidence…"): _ans=answer(qq)
        st.session_state.genie.insert(0,(qq,_ans))
        try: save_action(user,"chat","ask",qq,{"q":qq,"a":_ans[:1500]},silent=True)
        except Exception: pass
    for idx,(qx,ans) in enumerate(st.session_state.genie[:5]):
        with st.container(border=True):
            st.markdown(f"**🧑 {qx}**")
            if ans: st.markdown(ans)
            if idx==0: answer_chart(qx)
            if st.button("🧮 Also run this as SQL via Genie",key="gbtn"+str(idx)):
                with st.spinner("Genie is writing SQL…"):
                    try: st.session_state["gres"+str(idx)]=genie_ask(qx)
                    except Exception as e: st.session_state["gres"+str(idx)]={"sql":None,"text":f"Genie unavailable ({type(e).__name__})."}
            gr=st.session_state.get("gres"+str(idx))
            if gr:
                if gr.get("sql"): st.code(gr["sql"],language="sql")
                if gr.get("cols") and gr.get("rows") is not None:
                    st.dataframe(pd.DataFrame(gr["rows"],columns=gr["cols"]),use_container_width=True,hide_index=True,height=min(300,70+28*max(1,len(gr["rows"]))))
                elif gr.get("text"): st.caption(gr["text"])

# ==================== TRACK 6 · DATA SCIENCE LAB ====================
elif track==T6:
    st.markdown("<div class='kick'>Data Science Lab · all three datasets + our experiments</div>",unsafe_allow_html=True)
    st.markdown("#### The evidence behind every claim — explore it yourself")
    st.caption("Facilities (10,088) · India-Post PIN directory (165,627 offices) · NFHS-5 (706 districts). Interactive EDA, correlation, confounding, and the causal / ML experiments that power the trust engine.")
    nf=q(f"SELECT * FROM {GOLD}.gold_nfhs")
    tb=st.tabs(["🔬 Correlation explorer","📈 Confounding (corr ≠ cause)","🏥 Facility evidence","🗺️ Geographic coverage","🧪 Causal & ML experiments"])
    with tb[0]:
        st.caption("Pick any NFHS-5 indicators — the correlation matrix recomputes live across 706 districts.")
        sel=st.multiselect("Indicators",list(NFHS_LABELS),
            default=["sanitation","wealth_electricity","schooling","child_marriage","anc4","inst_birth","stunting","overweight","high_blood_sugar"],
            format_func=lambda k:NFHS_LABELS[k])
        if len(sel)>=2:
            cm=nf[sel].corr().round(2)
            fig=px.imshow(cm,text_auto=True,color_continuous_scale="RdBu_r",zmin=-1,zmax=1,aspect="auto",
                x=[NFHS_LABELS[s] for s in sel],y=[NFHS_LABELS[s] for s in sel])
            fig.update_layout(height=540,margin=dict(l=0,r=0,t=10,b=0),font=dict(family="IBM Plex Sans"),coloraxis_colorbar=dict(title="r"))
            st.plotly_chart(fig,use_container_width=True)
            st.caption("Red = positive, blue = negative correlation. **A strong correlation is not a cause** — the next tab shows why.")
        else: st.info("Pick at least two indicators.")
    with tb[1]:
        st.caption("Plot any two indicators and colour by a possible confounder. A strong raw correlation can dissolve once you account for wealth — that is the heart of correlation-vs-causation.")
        c1,c2,c3=st.columns(3)
        xv=c1.selectbox("X axis",list(NFHS_LABELS),index=0,format_func=lambda k:NFHS_LABELS[k])
        yv=c2.selectbox("Y axis",list(NFHS_LABELS),index=list(NFHS_LABELS).index("stunting"),format_func=lambda k:NFHS_LABELS[k])
        cv=c3.selectbox("Colour by (possible confounder)",list(NFHS_LABELS),index=list(NFHS_LABELS).index("wealth_electricity"),format_func=lambda k:NFHS_LABELS[k])
        d=nf.dropna(subset=[xv,yv,cv])
        if not d.empty:
            fig=px.scatter(d,x=xv,y=yv,color=cv,hover_name="district",color_continuous_scale="Viridis",opacity=.82,
                labels={xv:NFHS_LABELS[xv],yv:NFHS_LABELS[yv],cv:NFHS_LABELS[cv]})
            fig.update_layout(height=460,margin=dict(l=0,r=0,t=10,b=0),font=dict(family="IBM Plex Sans"))
            st.plotly_chart(fig,use_container_width=True)
            rr=d[xv].corr(d[yv])
            st.markdown(explain_r(rr,NFHS_LABELS[xv],NFHS_LABELS[yv]))
            if {xv,yv}=={"sanitation","stunting"}:
                st.warning("Worked example: sanitation ↔ stunting looks strong (**r ≈ −0.51** — districts with better toilets have less child stunting), but it **collapses to ~0 once we account for wealth**: richer districts simply have both. So sanitation here is a *coincidence*, not the cause. Female schooling and ANC visits, by contrast, stay strong after adjustment — likely real causes.")
            info_pop("Each dot is one of 706 districts. Position = the two indicators you picked; colour = a possible confounder (default: household wealth). If same-coloured dots form their own slanted bands, the headline correlation is partly an illusion created by that confounder. **r** runs from −1 to +1 and measures how tightly the two move together.")
    with tb[2]:
        c1,c2=st.columns(2)
        with c1:
            st.markdown("##### Confidence distribution (graded claims)")
            h=q(f"SELECT confidence,grade FROM {GOLD}.gold_facility_capability_trust WHERE grade IN ('STRONG','PARTIAL','WEAK/SUSPICIOUS')")
            fig=px.histogram(h,x="confidence",color="grade",nbins=20,color_discrete_map=GC)
            fig.update_layout(height=330,margin=dict(l=0,r=0,t=10,b=0),bargap=.04,font=dict(family="IBM Plex Sans"),legend=dict(orientation="h",y=1.05,title=""),xaxis_title="confidence /100",yaxis_title="claims")
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown("##### Evidence grade by facility type")
            ft=q(f"SELECT ftype,grade,count(*) n FROM {GOLD}.gold_facility_capability_trust WHERE grade IN ('STRONG','PARTIAL','WEAK/SUSPICIOUS') AND ftype IS NOT NULL GROUP BY ftype,grade")
            top=ft.groupby('ftype')['n'].sum().sort_values(ascending=False).head(7).index.tolist(); ft=ft[ft.ftype.isin(top)]
            fig=px.bar(ft,x="ftype",y="n",color="grade",color_discrete_map=GC,category_orders={"grade":["STRONG","PARTIAL","WEAK/SUSPICIOUS"]})
            fig.update_layout(height=330,margin=dict(l=0,r=0,t=10,b=0),font=dict(family="IBM Plex Sans"),legend=dict(orientation="h",y=1.05,title=""),xaxis_title="",yaxis_title="claims")
            st.plotly_chart(fig,use_container_width=True)
        st.caption("Most claims sit at PARTIAL evidence; a high-confidence STRONG tail clears the ≥2-evidence-types + 2nd-source bar. Hospitals carry more STRONG grades than clinics.")
        st.divider(); st.markdown("##### Grade distribution for ANY specialty (2,580 in the data)")
        allspecs=q(f"SELECT specialty FROM {GOLD}.gold_facility_specialty GROUP BY specialty ORDER BY count(*) DESC")['specialty'].tolist()
        pk=st.selectbox("Specialty",allspecs,index=allspecs.index("Cardiology") if "Cardiology" in allspecs else 0,key="dlspec")
        sd=q(f"SELECT grade,count(*) n FROM {GOLD}.gold_facility_specialty WHERE specialty='{pk.replace(chr(39),chr(39)+chr(39))}' GROUP BY grade")
        cS1,cS2=st.columns([1.4,1])
        with cS1:
            figsd=px.bar(sd,x="grade",y="n",color="grade",color_discrete_map={**GC,"CLAIMED":"#B6C0C2"},text="n",category_orders={"grade":["STRONG","PARTIAL","CLAIMED"]})
            figsd.update_layout(height=320,margin=dict(l=0,r=0,t=10,b=0),showlegend=False,font=dict(family="IBM Plex Sans"),xaxis_title="",yaxis_title="facilities")
            st.plotly_chart(figsd,use_container_width=True,key="dl_specgrade")
        with cS2:
            tot=int(sd['n'].sum()) if not sd.empty else 0; strong=int(sd[sd.grade=='STRONG']['n'].sum()) if not sd.empty else 0
            st.metric(f"Facilities offering {pk}",f"{tot:,}")
            st.metric("With STRONG evidence",f"{strong:,}",f"{(strong/tot*100 if tot else 0):.0f}% of claims")
        st.caption("**Every one of the 2,580 specialties** in the data is graded — pick any to see how its claims split across STRONG / PARTIAL / CLAIMED evidence.")
        info_pop("Every specialty each facility lists, graded from its own free-text evidence and source count. STRONG = corroborated in free-text + ≥2 sources · PARTIAL = one signal · CLAIMED = listed in the structured field only.")
    with tb[3]:
        st.caption("The India-Post PIN directory (165,627 offices) geocodes facilities to districts so care gaps map to real geography.")
        c1,c2=st.columns(2)
        with c1:
            st.markdown("##### Post offices per state (India-Post)")
            pin=q(f"SELECT initcap(lower(state)) state,n_post_offices FROM {GOLD}.gold_pin_state ORDER BY n_post_offices DESC LIMIT 15").sort_values("n_post_offices")
            fig=px.bar(pin,x="n_post_offices",y="state",orientation="h",text="n_post_offices",color_discrete_sequence=["#119A6B"])
            fig.update_layout(height=430,margin=dict(l=0,r=12,t=6,b=0),font=dict(family="IBM Plex Sans"),xaxis_title="post offices",yaxis_title="")
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            st.markdown("##### Graded facilities per state")
            fc=q(f"SELECT initcap(lower(state)) state,count(*) n FROM {GOLD}.gold_facility_contact WHERE state IS NOT NULL GROUP BY initcap(lower(state)) ORDER BY n DESC LIMIT 15").sort_values("n")
            fig=px.bar(fc,x="n",y="state",orientation="h",text="n",color_discrete_sequence=["#2272B4"])
            fig.update_layout(height=430,margin=dict(l=0,r=12,t=6,b=0),font=dict(family="IBM Plex Sans"),xaxis_title="facilities",yaxis_title="")
            st.plotly_chart(fig,use_container_width=True)
    with tb[4]:
        st.markdown("##### Does a correlation survive once we remove confounders?")
        rel=st.selectbox("Pick a relationship to test",[e[0] for e in _EFF],key="dleff")
        fige,(nv,ols,dml,psm)=effect_bar(rel)
        cE1,cE2=st.columns([2,1])
        with cE1: st.plotly_chart(fige,use_container_width=True,key="dl_eff")
        with cE2:
            st.metric("Raw correlation",f"{nv:+.2f}")
            st.metric("After removing wealth & confounders",f"{ols:+.2f}",f"{ols-nv:+.2f}")
            if abs(ols)<abs(nv)*0.5:
                st.error(f"**Confounded.** The link shrinks from {nv:+.2f} to about {ols:+.2f} once we account for wealth — so it was mostly a **coincidence**, not a cause.")
            else:
                st.success(f"**Likely causal.** The link stays strong ({nv:+.2f} → {ols:+.2f}) even after removing confounders — a real effect.")
        info_pop("Each bar is the estimated effect under a different method. **Naive** is the raw correlation. **OLS+state fixed-effects**, **Double-ML** (a machine-learning estimator) and **Matching (PSM)** each remove the influence of confounders like household wealth. If the bars shrink toward 0 as you move right, the original correlation was an illusion; if they hold, the cause is likely real.")
        st.divider()
        st.markdown("##### 🕸️ Interactive causal-graph studio — drag the nodes, switch modules")
        _M=causal_modules()
        msel=st.selectbox("Causal graph module",list(_M),key="dlmod")
        st.caption(_M[msel]["desc"]+"  ·  **Drag** any node to rearrange · **scroll** to zoom · **hover** a link for the evidence.")
        try:
            components.html(d3_graph(_M[msel]),height=660,scrolling=False)
        except Exception as e:
            st.warning(f"Interactive view unavailable ({type(e).__name__}); showing the static causal map.")
            st.plotly_chart(causal_plot(""),use_container_width=True,key="dl_causal_fb")
        with st.expander("Prefer a static, print-friendly view of the levers?"):
            oc=st.selectbox("Show causal pathway for",["(all levers)","maternity","NICU","emergency","oncology","cardiology","dialysis"],key="dlcap")
            st.plotly_chart(causal_plot("" if oc.startswith("(all") else oc),use_container_width=True,key="dl_causal")
            st.caption("🟢 likely-causal · 🔴 confounded (collapses under wealth adjustment) · grey dashed = common cause. Hover any arrow for the relationship + effect size.")
        with st.expander("📊 Raw experiment plots — statistical ML & geometric deep learning (full size)"):
            for fn,cap2 in [("corr_heatmap.png","Full NFHS correlation heatmap (all indicators)"),("causal_scatters.png","Naive vs wealth-adjusted scatters"),("gam_quantile.png","GAM + quantile regression — non-linear dose-response & tail effects")]:
                p=os.path.join(FIGS,fn)
                if os.path.exists(p): st.image(p,caption=cap2,use_column_width=True)

# ---- one assistant only: pointer to the "Ask the Data" track (no duplicate chat per track) ----
if track in (T1,T2,T3,T4,T6):
    st.divider()
    st.caption("💬 Have a free-form question? Open the **“⑤ Ask the Data”** track — one assistant that answers anything with cited evidence, the relevant chart, and (on demand) the SQL via AI/BI Genie.")
