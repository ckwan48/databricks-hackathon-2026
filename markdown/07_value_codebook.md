## Value-Level Codebook (what each value MEANS, from the complete data)

*Beyond column meaning: for every CODED column, each distinct value, its count in the full data, and its meaning. Free-text and pure-numeric columns are summarized by their value SYSTEM.*

### NFHS — special value codes (apply to all 101 % / ratio / count cells)
| Value pattern | Count | Meaning |
|---|---|---|
| `*` | 4,125 (5.5%) | **Suppressed** — based on <25 unweighted cases; too few to report. Treat as missing. |
| `(value)` e.g. `(64.2)` | 5,068 (6.7%) | Estimate from **25–49 unweighted cases** — usable but low precision; flag it. |
| trailing spaces e.g. `927 ` | many | formatting noise — strip before use |
| plain number | rest | interpret by unit: `*_pct`=% 0–100, `sex_ratio_*`=F per 1000 M, `*_interviewed`=count, OOP=₹ |

### Pincode · officetype
| Value | Count | Meaning |
|---|---|---|
| `BO` | 140,270 | Branch Office — smallest rural/local post office; reports to a Sub Office |
| `PO` | 24,546 | (other) |
| `HO` | 811 | Head Office — top office of a postal division (e.g. a city GPO) |

### Pincode · delivery
| Value | Count | Meaning |
|---|---|---|
| `Delivery` | 157,901 | Delivers mail to addresses in its beat |
| `Non Delivery` | 7,726 | Only books/processes mail; delivery done by another office |

### Facilities · source_types (provenance tag per evidence item)
| Value | Count | Meaning |
|---|---|---|
| `overture` | 162,020 | Overture Maps Foundation open POI/places record (base map identity) |
| `dynamic` | 82,952 | Dynamically scraped/derived content (live web pages, changeable facts) |
| `constant` | 20,669 | Constant/static reference content (stable attributes) |
| `mongo_facility` | 5,955 | Record from the platform's internal MongoDB facility store (curated/prior) |
| `mongo_ngo` | 1,121 | Record from the internal MongoDB NGO store |

*Meanings inferred from naming + pipeline behaviour. The COUNT of DISTINCT source_types per facility is the trust signal — VERIFIED-STRONG grades require ≥2 distinct sources.*

### Facilities · facilityTypeId
| Value | Count | Meaning |
|---|---|---|
| `hospital` | 5,637 | Hospital (inpatient, multi-service) |
| `clinic` | 3,782 | Clinic / OPD / single-service centre (many standalone dialysis/diagnostic centres are mis-typed here) |
| `dentist` | 490 | Dental practice |
| `nan` | 126 | missing |
| `doctor` | 21 | Solo doctor / individual practitioner |
| `farmacy` | 10 | Pharmacy / drug store (MISSPELLED — should be "pharmacy") |
| `pharmacy` | 2 | Pharmacy / drug store (correct spelling; coexists with "farmacy") |

*The stray coordinates-JSON value is a column-shifted row (see misalignment note below).*

### Facilities · operatorTypeId
| Value | Count | Meaning |
|---|---|---|
| `private` | 8,842 | Privately owned / operated |
| `nan` | 761 | missing |
| `public` | 469 | Government / public-sector operated |
| `government` | 2 | Government-operated (variant of "public" — normalize) |

*⚠ Data-quality: **14 rows** carry malformed operatorTypeId values (coordinate fragments, URL-arrays, UUIDs, specialty codes) — these are **column-misaligned rows** where commas/JSON in earlier fields shifted the columns. They must be re-parsed or quarantined.*

### Facilities · organization_type
| Value | Count | Meaning |
|---|---|---|
| `facility` | 10,000 | record class — the only valid value |
| `nan` | 61 | missing |
| `Doctor couple's unblemished efforts help` | 1 | (other) |

### Facilities · acceptsVolunteers (boolean)
| Value | Count | Meaning |
|---|---|---|
| `nan` | 10,046 | missing |
| `true` | 21 | yes |
| `false` | 7 | no |

### Facilities · affiliated_staff_presence (boolean)
| Value | Count | Meaning |
|---|---|---|
| `true` | 9,260 | yes |
| `false` | 697 | no |
| `nan` | 129 | missing |

### Facilities · custom_logo_presence (boolean)
| Value | Count | Meaning |
|---|---|---|
| `true` | 8,611 | yes |
| `false` | 998 | no |
| `nan` | 477 | missing |

### Facilities · address_countryCode
| Value | Count | Meaning |
|---|---|---|
| `IN` | 10,000 | India |
| `nan` | 59 | missing |
| `kie` | 2 | (other) |
| `1` | 1 | (other) |
| `0029c85a-fa3b-45a7-b892-3f367b547466` | 1 | (other) |

### Facilities · specialties — the value SYSTEM (164 distinct codes)
camelCase clinical specialty codes (HL7/FHIR-style); 2935 distinct. Top values:

| Code | Count | Meaning |
|---|---|---|
| `internalMedicine` | 68,026 | general adult internal medicine |
| `familyMedicine` | 23,732 | family / general practice |
| `dentistry` | 13,111 | dental |
| `gynecologyAndObstetrics` | 11,020 | OB-GYN (maternity) |
| `ophthalmology` | 7,645 | eye care |
| `orthopedicSurgery` | 7,278 | bone & joint surgery |
| `pediatrics` | 6,763 | child health |
| `cardiology` | 6,103 | heart |
| `generalSurgery` | 5,744 | general surgery |
| `radiology` | 5,455 | imaging |
| `otolaryngology` | 4,912 | ENT (ear-nose-throat) |
| `pathology` | 4,912 | (clinical specialty) |
| `urology` | 4,488 | (clinical specialty) |
| `reproductiveEndocrinologyAndInfertility` | 4,323 | (clinical specialty) |
| `dermatology` | 4,094 | skin |
| `gastroenterology` | 3,966 | (clinical specialty) |
| `endodontics` | 3,855 | (clinical specialty) |

*Overlapping pairs (`ent`↔`otolaryngology`, `generalMedicine`↔`internalMedicine`, `dental`↔`dentistry`) and within-row duplicates — normalize before modeling.*

### Free-text / non-coded columns
`capability`, `procedure`, `equipment`, `description`, `name`, address lines = free natural language (no fixed vocabulary). `pincode`=6-digit ID. `latitude`/`longitude`/`coordinates`=geo floats. `yearEstablished`=year; engagement/post metrics=counts. No enumerable value-meaning — see the unit audit (section 06).
