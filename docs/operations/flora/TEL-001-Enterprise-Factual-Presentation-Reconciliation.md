# TEL-001 Enterprise Factual Presentation Reconciliation

**Audit date:** 2026-08-15  
**Fixture:** `TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip`  
**SHA-256:** `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`

## Architecture and method

This audit preceded production edits. It reuses EIF-001, the semantic Twin constructor, the Canonical Factual Projection (CFP), the executive workspace, and the completed identity/association corrections. It does not create a factual model. Candidate fact display is a read only operation; assessment, review, promotion and recommendation remain separate.

Each cell below records `Source → Candidate → Semantic → CFP → Executive → Rendered`. `P` means the qualifying value is present at the stage, `A` absent, and `—` unsupported. Evidence/Unknown/Contradiction counts are retained on each Enterprise projection and exposed in Advanced Inspection. Concise summaries are bounded to the source field named; aliases are not combined and unrelated fields are never substituted.

## Governed runtime dimension inventory

| Dimension | Canonical source vocabulary | Runtime support |
|---|---|---|
| Organisation / Enterprise Profile | `description` aliases | Supported |
| Industry / Domain | explicit semantic `domains` | Supported; source absent in all six |
| Strategic Position | `strategy` / `corporate_strategy` aliases | Supported |
| Operating Model | `operating_model` / `operating_structure` aliases | Supported |
| Financial Position / Performance | `financial_context` / `financial_intelligence` aliases | Supported |
| Enterprise Economics | independent economics projection | **Architectural intent — not implemented** |
| Material Pressures | `pressures` | Supported |
| Leadership / Governance | independent leadership/governance projection | **Architectural intent — not implemented** |
| Technology / Platform | `technology` aliases | Supported |
| Supplier / Ecosystem | `ecosystem`, then supplier aliases | Supported |
| Major Programmes | explicit Enterprise relationship truth | Supported; protected association owner |
| Known Procurements | `procurement_intelligence` | Supported |
| Reinvention / Transformation | `transformation_posture` aliases | Supported |
| Commercial Opportunities | explicit Enterprise relationship truth | Supported; protected association owner |

## Complete six-Enterprise truth matrix

The identity-owned dimensions below all have the same candidate ID lineage as their Enterprise (`ENT-*` source ID → staged candidate ID → semantic Enterprise identity). Evidence references are those carried by that Enterprise candidate. The actual structured value is rendered as labelled list items, not a Python dictionary.

| Enterprise | Dimension | Source value / concise structured summary | Pipeline | Classification before | Corrected result / reason |
|---|---|---|---|---|---|
| BT Group | Organisation / Enterprise Profile | evidenced description | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| BT Group | Industry / Domain | no explicit semantic domain | A→A→A→A→A→A | A. source absent | EXPECTED ABSENCE — A. SOURCE ABSENT; Twin membership is not industry proof |
| BT Group | Strategic Position | structured strategy/priorities/challenges | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| BT Group | Operating Model | structured business/delivery model and constraints | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| BT Group | Financial Position / Performance | structured revenue/profitability/capex/debt/outlook context | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| BT Group | Enterprise Economics | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| BT Group | Material Pressures | source pressure list | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| BT Group | Leadership / Governance | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| BT Group | Technology / Platform Context | structured technology landscape | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| BT Group | Supplier / Ecosystem Context | structured ecosystem/supplier facts | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| BT Group | Major Programmes | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| BT Group | Known Procurements | structured procurement intelligence; not relabelled as open tenders | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| BT Group | Reinvention / Transformation Context | structured transformation posture and timing | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| BT Group | Commercial Opportunities | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| CityFibre | Organisation / Enterprise Profile | evidenced description | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| CityFibre | Industry / Domain | no explicit semantic domain | A→A→A→A→A→A | A. source absent | EXPECTED ABSENCE — A. SOURCE ABSENT; Twin membership is not industry proof |
| CityFibre | Strategic Position | structured strategy/priorities/challenges | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| CityFibre | Operating Model | structured business/delivery model and constraints | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| CityFibre | Financial Position / Performance | structured revenue/profitability/capex/debt/outlook context | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| CityFibre | Enterprise Economics | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| CityFibre | Material Pressures | source pressure list | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| CityFibre | Leadership / Governance | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| CityFibre | Technology / Platform Context | structured technology landscape | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| CityFibre | Supplier / Ecosystem Context | structured ecosystem/supplier facts | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| CityFibre | Major Programmes | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| CityFibre | Known Procurements | structured procurement intelligence; not relabelled as open tenders | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| CityFibre | Reinvention / Transformation Context | structured transformation posture and timing | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| CityFibre | Commercial Opportunities | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| Openreach | Organisation / Enterprise Profile | evidenced description | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| Openreach | Industry / Domain | no explicit semantic domain | A→A→A→A→A→A | A. source absent | EXPECTED ABSENCE — A. SOURCE ABSENT; Twin membership is not industry proof |
| Openreach | Strategic Position | structured strategy/priorities/challenges | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| Openreach | Operating Model | structured business/delivery model and constraints | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| Openreach | Financial Position / Performance | structured revenue/profitability/capex/debt/outlook context | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Openreach | Enterprise Economics | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| Openreach | Material Pressures | source pressure list | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Openreach | Leadership / Governance | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| Openreach | Technology / Platform Context | structured technology landscape | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| Openreach | Supplier / Ecosystem Context | structured ecosystem/supplier facts | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Openreach | Major Programmes | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| Openreach | Known Procurements | structured procurement intelligence; not relabelled as open tenders | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Openreach | Reinvention / Transformation Context | structured transformation posture and timing | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Openreach | Commercial Opportunities | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| TalkTalk | Organisation / Enterprise Profile | evidenced description | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| TalkTalk | Industry / Domain | no explicit semantic domain | A→A→A→A→A→A | A. source absent | EXPECTED ABSENCE — A. SOURCE ABSENT; Twin membership is not industry proof |
| TalkTalk | Strategic Position | structured strategy/priorities/challenges | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| TalkTalk | Operating Model | structured business/delivery model and constraints | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| TalkTalk | Financial Position / Performance | structured revenue/profitability/capex/debt/outlook context | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| TalkTalk | Enterprise Economics | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| TalkTalk | Material Pressures | source pressure list | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| TalkTalk | Leadership / Governance | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| TalkTalk | Technology / Platform Context | structured technology landscape | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| TalkTalk | Supplier / Ecosystem Context | structured ecosystem/supplier facts | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| TalkTalk | Major Programmes | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| TalkTalk | Known Procurements | structured procurement intelligence; not relabelled as open tenders | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| TalkTalk | Reinvention / Transformation Context | structured transformation posture and timing | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| TalkTalk | Commercial Opportunities | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| Virgin Media O2 | Organisation / Enterprise Profile | evidenced description | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| Virgin Media O2 | Industry / Domain | no explicit semantic domain | A→A→A→A→A→A | A. source absent | EXPECTED ABSENCE — A. SOURCE ABSENT; Twin membership is not industry proof |
| Virgin Media O2 | Strategic Position | structured strategy/priorities/challenges | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| Virgin Media O2 | Operating Model | structured business/delivery model and constraints | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| Virgin Media O2 | Financial Position / Performance | structured revenue/profitability/capex/debt/outlook context | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Virgin Media O2 | Enterprise Economics | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| Virgin Media O2 | Material Pressures | source pressure list | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Virgin Media O2 | Leadership / Governance | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| Virgin Media O2 | Technology / Platform Context | structured technology landscape | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| Virgin Media O2 | Supplier / Ecosystem Context | structured ecosystem/supplier facts | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Virgin Media O2 | Major Programmes | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| Virgin Media O2 | Known Procurements | structured procurement intelligence; not relabelled as open tenders | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Virgin Media O2 | Reinvention / Transformation Context | structured transformation posture and timing | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| Virgin Media O2 | Commercial Opportunities | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| VodafoneThree | Organisation / Enterprise Profile | evidenced description | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| VodafoneThree | Industry / Domain | no explicit semantic domain | A→A→A→A→A→A | A. source absent | EXPECTED ABSENCE — A. SOURCE ABSENT; Twin membership is not industry proof |
| VodafoneThree | Strategic Position | structured strategy/priorities/challenges | P→P→P→P→P→P | G. fact wrongly gated by assessment | PASS |
| VodafoneThree | Operating Model | structured business/delivery model and constraints | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| VodafoneThree | Financial Position / Performance | structured revenue/profitability/capex/debt/outlook context | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| VodafoneThree | Enterprise Economics | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| VodafoneThree | Material Pressures | source pressure list | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| VodafoneThree | Leadership / Governance | independent runtime field not implemented | P→P→P→—→—→— | I. unsupported architectural domain | UNSUPPORTED — I. UNSUPPORTED ARCHITECTURAL DOMAIN |
| VodafoneThree | Technology / Platform Context | structured technology landscape | P→P→P→P→P→P | F. executive value rendered as raw container | PASS |
| VodafoneThree | Supplier / Ecosystem Context | structured ecosystem/supplier facts | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| VodafoneThree | Major Programmes | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |
| VodafoneThree | Known Procurements | structured procurement intelligence; not relabelled as open tenders | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| VodafoneThree | Reinvention / Transformation Context | structured transformation posture and timing | P→P→P→P→P→P | E. CFP present / executive view lost | PASS |
| VodafoneThree | Commercial Opportunities | explicit relationship-owned exact set | P→P→P→P→P→P | No failure; protected association truth | PASS — one factual read contract |

## Failure classification and first divergence

* **A — Source absent:** explicit Industry / Domain for all six Enterprises. Membership in a UK Telecoms Twin is context, not evidence that every member has that industry.
* **E — CFP present / executive view lost:** financial, pressure, supplier, procurement and transformation dictionaries survived staging/semantic construction but dossier-specific selectors independently declared absence.
* **F — Executive view present / render lost:** Operating Model and Technology container values were escaped/stringified on selected surfaces rather than rendered structurally.
* **G — Fact wrongly gated by assessment:** Enterprise cards described sourced profile facts as pending owner assessment.
* **I — Unsupported architectural domain:** independent Enterprise Economics and Leadership / Governance dimensions are architectural intent but not implemented by this runtime.
* No B, C or D loss was found: the immutable package, candidate staging, semantic object and CFP retained the qualifying identity facts.
* No H contamination is accepted. Financials do not fall back to operating model; pressures do not use arbitrary constraints; procurements do not use supplier lists; strategy does not use generic description.

## Evidence, confidence, unknowns and contradictions

Each source Enterprise dossier supplies its candidate identity, evidence list, confidence attribute, Unknown references and Contradiction references. CFP preserves evidence/Unknown/Contradiction references without treating confidence as approval. Advanced Inspection reports counts per Enterprise/dimension and the executive dossier exposes the references alongside factual values. Source lineage remains the source file, source location and original `ENT-*` ID.

## Assessment and governance phrases

“Assessment not yet performed” means no analytical owner assessment exists. It does not mean source facts are absent. “Imported candidate” describes unchanged candidate governance. No committee or additional ceremony is implied. Review, promotion, assessment and recommendation status are not mutated by projection.

## Research Gaps and true absence

A gap is justified only for absent or insufficient qualifying evidence. The shared dimension contract prevents a presentation failure, missing assessment, structured value, or vocabulary alias from becoming a false gap. Explicit Industry / Domain remains a true absence. Independent Enterprise Economics and Leadership / Governance remain unsupported rather than falsely “not supplied”.

## Fresh import

**Fresh import required: NO.** Candidate/source attributes already contain the profile, strategy, operating, financial, pressure, technology, ecosystem, procurement and transformation objects. The first divergences were read/projection and rendering defects after persistence.
