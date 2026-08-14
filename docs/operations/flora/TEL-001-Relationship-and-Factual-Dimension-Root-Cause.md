# TEL-001 Relationship and Factual Dimension Root Cause

## Scope and governing owners

This report preserves the **before** trace and records the correction at the first reusable runtime boundaries. The governed fixture remained byte-for-byte unchanged (`bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`).

| Concern | Existing canonical owner reused |
|---|---|
| Business-object identity | `semantic_twin.business_object_id` over staging's `original_source_id` |
| Relationship objects and query | standalone `SemanticObject(kind="relationship")`, `relationship_endpoints`, `resolve_relationships`, and `enterprise_associations` |
| Canonical factual read model | `CanonicalFactualProjection` |
| Enterprise executive projection | `executive_workspace._dossier` |
| Completeness vocabulary | existing `fact_state` and owner assessment/readiness services |

The Researcher contract expects a combination: standalone Relationships own typed graph assertions; Programme `owning_enterprise` is a governed ownership field; Opportunity-to-Enterprise association is supplied by standalone Relationship objects; Memberships govern industry collection inclusion and do not replace these associations. No relationship was inferred from prose.

## BEFORE forensic trace: BT/Verizon Programme

Exact source Programme: `PROG-BT-VERIZON-JV`. Exact BT identity: `ENT-BT`.

| Boundary | Programme ID | BT ID | Relationship ID | Type | Resolution | Result |
|---|---|---|---|---|---|---|
| ZIP Programme | PROG-BT-VERIZON-JV | ENT-BT | — | `owning_enterprise` | YES | Source Programme explicitly says `owning_enterprise=ENT-BT`; it has no embedded Relationship ID. |
| ZIP Relationship collection | PROG-BT-VERIZON-JV | ENT-BT | — | — | ABSENT | None of the 308 standalone records has this Programme as an endpoint. Narrative relevance is therefore not Relationship evidence. |
| ZIP Membership | PROG-BT-VERIZON-JV | ENT-BT | membership register | Industry membership | NOT APPLICABLE | Membership does not own Enterprise/Programme association. |
| Validator/staging | PROG-BT-VERIZON-JV | ENT-BT | — | governed owner field | YES | Candidate retains immutable source ID and lossless payload. |
| Semantic object | PROG-BT-VERIZON-JV | ENT-BT | — | owner | YES | `owner=ENT-BT`; semantic subject also becomes `ENT-BT`. |
| Canonical factual projection | PROG-BT-VERIZON-JV | ENT-BT | — | owner | YES | Programme facts survive; CFP is not the graph owner. |
| **Before Enterprise query** | PROG-BT-VERIZON-JV | ENT-BT | — | owner | **NO** | **FIRST DIVERGENCE:** the dossier-associated record path depended on records attached by display-name context/embedded references. `ENT-BT` did not equal display name `BT Group`, so the governed owner field was not resolved through identity. |
| Before BT view/page | PROG-BT-VERIZON-JV | ENT-BT | — | owner | NO | “No programme can be shown without an explicit relationship.” |
| Corrected canonical query | PROG-BT-VERIZON-JV | ENT-BT | — | canonical ownership | YES | `enterprise_associations` compares owner endpoints to identity key, name and governed aliases. |
| Corrected BT page | PROG-BT-VERIZON-JV | ENT-BT | — | Owned programme | YES | Rendered once with summary, stage, Evidence, Unknowns and Contradictions. |

The required regression test proves that the standalone Relationship does **not** exist and that the governed Programme ownership field does. Inventing a Relationship would be incorrect.

## BEFORE forensic trace: BT Opportunity

Representative Opportunity: `OPP-BT-VERIZON-JV-INTEGRATION`; Relationship: `REL-W4-183`.

| Boundary | Opportunity ID | BT ID | Relationship ID | Type | Resolution | Result |
|---|---|---|---|---|---|---|
| ZIP Opportunity | OPP-BT-VERIZON-JV-INTEGRATION | ENT-BT | — | Opportunity | YES | Substantive source identity exists once. |
| ZIP Relationship | OPP-BT-VERIZON-JV-INTEGRATION | ENT-BT | REL-W4-183 | Opportunity targets Enterprise | YES | Direction is Opportunity → Enterprise (`source_to_target`). |
| Validator/staging | OPP-BT-VERIZON-JV-INTEGRATION | ENT-BT | REL-W4-183 | Opportunity targets Enterprise | YES | Both lossless records and endpoints survive. |
| Semantic objects | OPP-BT-VERIZON-JV-INTEGRATION | ENT-BT | REL-W4-183 | Opportunity targets Enterprise | YES | Candidate IDs remain immutable source identities. |
| **Before Enterprise query** | OPP-BT-VERIZON-JV-INTEGRATION | ENT-BT | REL-W4-183 | Opportunity targets Enterprise | **NO** | **FIRST DIVERGENCE:** page-local association consumed attached/embedded dossier records, not the standalone Relationship population; reverse lookup from Enterprise to an Opportunity-origin edge was not performed. |
| Before BT page | OPP-BT-VERIZON-JV-INTEGRATION | ENT-BT | REL-W4-183 | — | NO | Commercial Opportunities reported no explicit relationship. |
| Corrected resolver/query | OPP-BT-VERIZON-JV-INTEGRATION | ENT-BT | REL-W4-183 | Opportunity targets Enterprise | YES | Both exact endpoints resolve and inverse lookup is permitted for this query without changing edge direction/type. |
| Corrected BT page | OPP-BT-VERIZON-JV-INTEGRATION | ENT-BT | REL-W4-183 | Opportunity targets Enterprise | YES | Rendered once. |

Identity formatting was not corrupted in staging. The failure was failure to query canonical identity plus standalone relationships. Directionality mattered to the Enterprise-side lookup; the edge itself remains directed. Relationship type survives unchanged.

## Relationship population audit

The source relationship population is exactly 308. After correction **252 resolve fully and 56 remain unresolved**; 21 source endpoints and 52 target endpoints do not resolve (some unresolved rows lack both). Runtime reconciliation reports these figures from `resolve_relationships`; unresolved relationships remain visible rather than being discarded. The unresolved endpoints are pipeline buckets, business units, industry sections, technology identifiers, namespaced Wave-5 estimates/unknowns, or one unresolved owner/programme source. They are not aliased by prose.

| Source family | Relationship type | Target family | Count | Resolved | Unresolved |
|---|---|---|---:|---:|---:|
| Enterprise/Participant | Enterprise owns Programme | Programme | 12 | 12 | 0 |
| Unresolved | Enterprise owns Programme | Programme | 1 | 0 | 1 |
| Opportunity | Opportunity targets Enterprise | Enterprise/Participant | 17 | 17 | 0 |
| Opportunity | Opportunity targets Business Unit | Unresolved | 16 | 0 | 16 |
| Opportunity | Opportunity classified into pipeline bucket | Unresolved | 17 | 0 | 17 |
| Programme | Programme creates Opportunity | Opportunity | 17 | 16 | 1 |
| Programme | Programme creates or enables Opportunity | Opportunity | 5 | 5 | 0 |
| Evidence | Evidence supports Opportunity | Opportunity | 48 | 48 | 0 |
| Evidence | Evidence supports Industry (two governed types) | Unresolved | 2 | 0 | 2 |
| Analyst estimate | Estimate addresses Unknown | Unknown | 76 | 76 | 0 |
| Unresolved namespaced estimate | Estimate addresses Unknown | Unresolved namespaced Unknown | 17 | 0 | 17 |
| Refresh trigger | Monitoring Trigger watches Opportunity | Opportunity | 51 | 51 | 0 |
| Market Participant | Participant supplies/partners Enterprise (typed variants retained) | Enterprise | 14 | 14 | 0 |
| Market Participant | Participant partners Enterprise | Enterprise | 2 | 2 | 0 |
| Market Participant | Participant partners Participant | Market Participant | 1 | 1 | 0 |
| Market Participant | Participant enables Opportunity | Opportunity | 1 | 1 | 0 |
| Market Participant | Regulation impacts Enterprise/Programme | Enterprise/Programme | 9 | 9 | 0 |
| Unresolved Technology | Technology enables Programme | Programme | 2 | 0 | 2 |
| **Total** |  |  | **308** | **252** | **56** |

The complete per-record truth is available in Advanced Inspection through the shared resolver. No type is collapsed to “related”; no global bidirectionality is introduced.

## Factual-dimension trace and root cause

| Dimension | Required governed facts | BT correct facts available | Before selected facts | Correct? |
|---|---|---|---|---|
| Organisation Overview | description, form, activities, role, position | executive overview/corporate identity partly supplied | overview | Partly |
| Operating Model | operating model/structure/business units | operating model and business units | operating-model facts | YES |
| Strategic Position and Ambition | strategy/ambition/position/evidence | corporate strategy supplied in CFP; dimension-specific detailed requirements partial | first CFP values | NO |
| Financial Position | measure, value/currency, period, source, interpretation | financial context exists but no complete qualifying semantic financial object in the dossier record set | first CFP values (including Business Model) | NO |
| Material Pressures | pressure, consequence, timing, evidence | constraints/pressures exist; qualification varies | first CFP values when no qualifying pressure item | NO |
| Major Programmes | canonical Programme association | two governed owner associations | first CFP values when page-local association returned zero | NO |
| Known Procurements | procurement facts/stage/timing/buyer/value/outcome | incomplete procurement intelligence | first CFP values | NO |
| Reinvention Timing | mechanism/exposure/indicators/horizon/response | no complete timing assessment | first CFP values | NO |
| Commercial Opportunities | canonical Opportunity association | three typed standalone Relationship associations | first CFP values when page-local association returned zero | NO |
| Technology and Ecosystem | technology/ecosystem semantic fields | supplied | CFP inventory | YES, presentation incomplete |
| Suppliers and Partners | suppliers/partners or typed relationships | Kyndryl, Dynatrace, ServiceNow, Nokia and Google secondary are supplied | CFP inventory | YES, presentation incomplete |

**FIRST DIVERGENCE:** `_dossier.gap` set presence from `factual.has_facts` and flattened the first three values from *all* CFP sections into every missing dimension's `Known` line. This was a generic any-fact/first-non-empty fallback at the executive projection boundary, not source loss and not a CFP field-mapping error.

The corrected executive projection never treats `factual.has_facts` as dimension presence. A correct field/related object produces dimension content; a qualifying but incomplete fact may be shown as incomplete; no qualifying fact produces the existing missing state and dimension-specific requirements. This is reusable because selection is based on canonical semantic fields and typed relationships, never TEL-001 IDs or text.

## Six-Enterprise reconciliation

| Enterprise | Programmes | Opportunities | Unresolved association endpoints | Incorrect dimension substitutions after correction |
|---|---:|---:|---:|---:|
| BT Group | 2 | 3 | 0 | 0 |
| Openreach | 1 | 3 | 0 | 0 |
| Virgin Media O2 | 2 | 3 | 0 | 0 |
| VodafoneThree | 2 | 3 | 0 | 0 |
| CityFibre | 1 | 2 | 0 | 0 |
| TalkTalk | 1 | 2 | 0 | 0 |

These sets are derived from governed owner fields and `Opportunity targets Enterprise` relationships. The remaining two of the 13 Programmes belong to non-dossier owners/industry scope and remain in the global Programme population.

## Operational result

Fresh import required: **NO**. The accepted candidate already persists the lossless Relationship and factual payloads; correction is at request-time canonical resolution/executive projection. Optional deployment telemetry is a limitation, not a functional-test blocker, when the current marker is visible and functional validation passed. Candidate review, promotion, assessment and recommendation semantics are unchanged.
