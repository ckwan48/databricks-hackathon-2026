# How facilitiesHelp.io reasons — the technique stack

One picture for judges and users. Read it **top to bottom**: the three datasets flow into **five method families** — probability, correlation, causation, ML / deep learning, and geospatial — and they all converge on a single **honest decision** that always carries its evidence and its uncertainty.

```mermaid
flowchart TD
    classDef data fill:#0E2A30,stroke:#0E2A30,color:#ffffff
    classDef prob fill:#E8F1FB,stroke:#2272B4,color:#0E2A30
    classDef corr fill:#FBF0E6,stroke:#E0A02A,color:#0E2A30
    classDef cause fill:#E7F6EF,stroke:#119A6B,color:#0E2A30
    classDef ml fill:#F1ECFB,stroke:#7A5AF8,color:#0E2A30
    classDef geo fill:#FDECEA,stroke:#E0594C,color:#0E2A30
    classDef out fill:#119A6B,stroke:#0E7A52,color:#ffffff

    D[("10,000 facility records<br/>+ 706 NFHS districts<br/>+ 165k post offices")]:::data

    subgraph P ["1 . Probability and Trust — how sure are we?"]
        direction TB
        P1["Evidence grading<br/>STRONG · PARTIAL ·<br/>WEAK · CLAIMED"]:::prob
        P2["Confidence 0-100<br/>more sources = higher"]:::prob
        P3["Validation<br/>logistic regression, ROC-AUC"]:::prob
        P4["Attribution<br/>SHAP-style"]:::prob
    end

    subgraph C ["2 . Correlation — what moves together?"]
        direction TB
        C1["Pearson r<br/>-1 to +1"]:::corr
        C2["Correlation heatmap"]:::corr
    end

    subgraph K ["3 . Causation — cause or coincidence?"]
        direction TB
        K1["PC structure learning<br/>build the DAG"]:::cause
        K2["OLS + state fixed effects"]:::cause
        K3["Double Machine Learning"]:::cause
        K4["Propensity-score matching"]:::cause
        K5["E-value robustness"]:::cause
        K1 --> K2 --> K3 --> K4 --> K5
    end

    subgraph M ["4 . ML and Deep Learning — non-linear and spatial"]
        direction TB
        M1["GAM + quantile regression"]:::ml
        M2["Multilevel / hierarchical"]:::ml
        M3["Stability selection"]:::ml
        M4["Spatial Graph Neural Net<br/>geometric deep learning"]:::ml
    end

    subgraph G ["5 . Geospatial and Referral — where, how far, what else?"]
        direction TB
        G1["Geocode any district"]:::geo
        G2["Haversine distance"]:::geo
        G3["Co-occurrence P(B given A)<br/>+ care pathways"]:::geo
    end

    D --> P
    D --> C
    D --> K
    D --> M
    D --> G
    C --> K

    P --> O
    K --> O
    M --> O
    G --> O

    O{{"HONEST DECISION<br/>Trust, Gap, Cause, Referral<br/>evidence + uncertainty, never fabricated"}}:::out
```

### In plain language

| Pillar | The question it answers | What we actually run |
|---|---|---|
| **1 · Probability & Trust** | *How sure are we a claim is real?* | A deterministic grading rubric turns the facility's own text into STRONG / PARTIAL / WEAK-SUSPICIOUS / CLAIMED with a 0–100 confidence; a logistic model proves the grade is reproducible, and a metadata-only model (AUC ≈ 0.57) proves it isn't just hospital fame. |
| **2 · Correlation** | *What moves together across districts?* | Pearson **r** (−1 to +1) over 706 districts, shown as an interactive heatmap. A strong correlation is a hint, **not** a cause. |
| **3 · Causation** | *Is it a real lever or a coincidence?* | The causal ladder: **PC** structure-learning builds the DAG → **OLS + state fixed-effects** → **Double Machine Learning** → **propensity-score matching** → **E-value** robustness. Effects that collapse under adjustment (sanitation→stunting) were confounded; ones that survive (schooling→child-marriage) are likely causal. |
| **4 · ML & Deep Learning** | *Non-linear, small-sample, and spatial patterns* | GAM + quantile regression (dose–response & tails), multilevel/hierarchical shrinkage, stability selection, and a **spatial Graph Neural Network** (geometric deep learning) benchmarked against baselines. |
| **5 · Geospatial & Referral** | *Where, how far, and what else might they need?* | Geocode any Indian district, rank by **haversine** distance, and suggest related care with specialty **co-occurrence P(B \| A)** and NFHS-correlation **care pathways**. |

**The golden rule across all five:** show the evidence, state the uncertainty, and never fabricate a number.
