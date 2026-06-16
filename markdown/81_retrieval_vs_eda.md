## Retrieval vs EDA — Two Data Tracks (don't clean like traditional ML)

*Core principle: the end goal is **retrieval** (vector RAG / GraphRAG / hybrid), not prediction. So we must keep **whatever is in the data** — we never delete rows, drop "messy" values, or impute things away. Destructive ML-style cleaning is reserved for a separate, transient analytics pipeline.*

### The architecture: enrich, never prune
| Layer | Mutability | Purpose | What lives here |
|---|---|---|---|
| **1. Raw layer** | immutable | source of truth for retrieval | every original cell verbatim — including `*`, `(x)`, `"null"`, bad coords, duplicates, free text |
| **2. Annotation layer** | **additive only** | trust + structure for retrieval | parsed numeric value, flags (`suppressed`, `small_sample`, `out_of_india_coord`, `contradiction`), **confidence score**, normalized geo (district/LGD code), `cluster_id` entity link, specialty/capability multi-hot |
| **3. Analytic view** | derived / disposable | correlation, EDA, causal models | the cleaned + winsorized + standardized table — **regenerated on demand, never written back** |

**Rule:** Layer 2 only *adds* columns next to the raw value; it never overwrites it. A suppressed `*` stays `*` and *also* gets `value=NaN, flag=suppressed`. A North-Atlantic coordinate is retained *and* flagged + given a corrected geo — both are retrievable.

### Why this matters for each track
- **Correlation / EDA / causal (this report's stats):** here we *do* clean — parse tokens, reliability-weight, transform proportions, standardize — because statistics need numeric, comparable inputs. This is Track 3 and it is **transient**: it answered "what correlates, how strongly, how confidently," and is then discarded.
- **The final application (retrieval):** "make everything better" = **enrich, not prune**. Every retrievable record keeps its raw text plus an evidence/confidence wrapper, so a user sees *what exists* and *how much to trust it* — even a half-empty or contradictory record is still retrievable, just flagged.

### How the two tracks feed the RAG/GraphRAG app
- **Raw text** (descriptions, capability/equipment strings, names) → **embeddings** for vector retrieval.
- **Annotation layer** (geo codes, facility type, specialties, flags) → **metadata filters** + **graph edges** for GraphRAG.
- **Confidence score** → **re-ranking** signal, so trustworthy evidence surfaces first without hiding the rest.

> Bottom line: clean *for the correlation/EDA pass only*; for the application, retain everything and wrap it in confidence. The earlier "data-prep blueprint" (cleaning, MNAR handling, standardization) applies to **Track 3**, not to the retrieval store.
