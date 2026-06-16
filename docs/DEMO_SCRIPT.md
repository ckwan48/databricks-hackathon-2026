# facilitiesHelp.io — 3-minute live demo script

**Goal:** prove all four tracks + the honesty differentiator, fast. One browser tab, app already open and warm.

> One-liner to open with: *"A planner is handed 10,000 messy healthcare records. Half the claims are unverified. facilitiesHelp.io turns that into decisions you can trust — every claim cited, scored for confidence, and tested for cause, not coincidence."*

---

### 0:00 – 0:20 · The hook
- Land on the home hero. Say the one-liner above.
- "We didn't pick one track — we did **all four, plus two bonus tracks**, on Databricks Free Edition."

### 0:20 – 1:00 · Track 1 — Facility Trust *(Can it do what it claims?)*
- Search a known hospital. Point to a **STRONG** badge and a **WEAK/SUSPICIOUS** one.
- Open **"Why this verdict"** → show the **cited source text**, the **confidence score**, and the **evidence→verdict** breakdown.
- Key line: *"Every grade comes from the facility's own evidence — and we **validated** it isn't just hospital fame: a model using only size/popularity scores barely above chance (AUC ≈ 0.57)."*

### 1:00 – 1:40 · Track 2 — Medical Desert *(Where are the real gaps?)*
- Pick a capability (e.g., NICU). Show the three classes: **real care gap** vs **data-poor** vs **evidenced supply**.
- Key line: *"The honest move — we separate a **real gap** from a place we simply **under-measured**, and we say 'we don't know' instead of guessing."*
- Scroll to the causal note: *"And we checked — building more facilities is only weakly linked to outcomes. So 'build more' isn't always the answer."*

### 1:40 – 2:20 · Track 3 — Referral + Care pathway *(Where should a patient go?)*
- Type **"dialysis near Guntur"** → evidence-attached, distance-ranked shortlist.
- Show the **🗺️ Maps / 💬 WhatsApp / 📧 Email this shortlist** buttons → *"from insight to action in one tap."*
- Scroll to **Care pathway**: pick **Child stunting** → it routes to a paediatrician/nutritionist **and** flags *"you may also need"* anaemia + wasting care — *"because these conditions travel together (r = 0.33), a maybe, not a diagnosis."*
- Switch the answer language to **Hindi** and hit **🔊 Listen** → *"multilingual, and it speaks."*

### 2:20 – 2:45 · The differentiator — interactive causal studio
- Data Science Lab → **Causal & ML experiments** → the **d3 studio**.
- **Drag a node.** Show **sanitation→stunting in red (confounded)** vs **schooling→child-marriage in green (survives)**.
- Key line: *"This is the part most teams skip — telling a correlation from a cause. Sanitation looks like it fixes stunting, but it collapses once we account for wealth."*

### 2:45 – 3:00 · Close
- *"All four tracks plus two bonus, fully on Databricks — Unity Catalog, SQL Warehouse, Model Serving with Llama 4 Maverick, and AI/BI Genie. 117,993 claims graded, 706 districts tested for cause. The hardest part of 'for good' data work isn't prediction — it's honesty. That's what we built."*

---

### If asked tough questions (have these ready)
- **"Did you A/B test?"** → "You can't randomize sanitation across districts, so we used propensity-score matching — the observational analog of an A/B test — plus Double-ML and E-values."
- **"How do you stop the LLM hallucinating?"** → "Every answer is grounded in the gold tables; it refuses to invent numbers and says when it has no data."
- **"Is the grade just popularity?"** → "No — a metadata-only model scores AUC ≈ 0.57, near chance. The grade reflects cited evidence."
- **"Scale?"** → "Complete dataset, no sampling: 2,580 specialties, 2,518 capabilities, 706 districts, 165k post offices."

**Backup if the app is slow:** the GitHub repo (README + technique mermaid + paper) is the fallback slide deck.
