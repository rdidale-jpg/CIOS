# TEL-001 Population and Relationship Root Cause

## Findings

1. **17 became 272 at the executive Opportunity collection/query boundary.** Ignored lineage/support rows were previously eligible to enter the executive semantic projection. The 272 were: 17 canonical Opportunities + 187 qualification scorecards + 17 qualified rows + 17 residual rows + 8 named-open rows + 7 overlap rows + 7 shaping rows + 12 corrected-ID rows.
2. The corrected boundary consumes validator-accepted candidates only. `business_object_id` then enforces one immutable source/canonical identity per executive collection; it does not use title, limits, CSS, or fixture-specific IDs.
3. **Enterprise association first diverged in the query.** The importer retained all 308 EI-002 relationships, but the dossier searched fields on Programme/Opportunity objects and never traversed relationship objects' `source` and `target`. Consequently reverse-form `OPP-X → ENT-X` relationships and their governed type were invisible.
4. The existing semantic Twin is still the identity owner; existing EI-002 relationship records are still the relationship owner. The reusable consumer now resolves either endpoint, normalises business-unit endpoints such as `ENT-BT:unit` to the owning Enterprise, preserves relationship direction and displayed type, and admits only canonical ownership or an explicit relationship.
5. No package, validator, canonical factual projection, Observation, Review, promotion, Unknown, Contradiction, or membership lifecycle was changed.

## Relationship forensics

There are **308** accepted Relationship records. The full rendered/test evidence is `rendered-population-reconciliation/acceptance.json`. Endpoint families are:

| Source → target family | Count |
|---|---:|
| Enterprise → Programme | 11 |
| Market Participant → Enterprise / Market Participant / Opportunity / Programme | 24 / 1 / 1 / 2 |
| Opportunity → Enterprise / Market Participant / unresolved business-unit or support endpoint | 27 / 1 / 22 |
| Programme → Opportunity | 21 |
| Evidence → Opportunity / unresolved | 48 / 2 |
| Refresh Trigger → Opportunity | 51 |
| Unresolved → Opportunity / Programme / Unknown / unresolved | 1 / 3 / 76 / 17 |

“Unresolved” in this source-family matrix means the endpoint is not itself one of the accepted executive business-object families; it does not silently make that supporting endpoint an executive object. Target-resolution failures remain diagnostic anomalies.

## BT truth table

| Object ID | Type | Relationship ID | Relationship type | Expected on BT | Actual | Result |
|---|---|---|---|---|---|---|
| PROG-BT-TRANSFORMATION | Programme | REL-W2-001 | Enterprise owns Programme | YES | YES | PASS |
| PROG-BT-VERIZON-JV | Programme | canonical ownership | Owned programme | YES | YES | PASS |
| OPP-BT-AI-ENGINEERING | Opportunity | REL-W2-014 | Opportunity targets Enterprise | YES | YES | PASS |
| OPP-BT-AIOPS | Opportunity | REL-W2-017 | Opportunity targets Enterprise | YES | YES | PASS |
| OPP-BT-VERIZON-JV-INTEGRATION | Opportunity | REL-W4-183 | Opportunity targets Enterprise | YES | YES | PASS |

Every other Programme and Opportunity has expected/actual **NO/NO** on BT. Market Participant links remain classified EI-002 relationships and are not mislabelled as owned Programmes or Opportunities.

## All-enterprise rendered reconciliation

| Enterprise | Expected/Rendered Programmes | Expected/Rendered Opportunities | Result |
|---|---:|---:|---|
| BT Group | 2 / 2 | 3 / 3 | PASS |
| CityFibre | 1 / 1 | 2 / 2 | PASS |
| Openreach | 1 / 1 | 3 / 3 | PASS |
| TalkTalk | 1 / 1 | 2 / 2 | PASS |
| Virgin Media O2 | 2 / 2 | 3 / 3 | PASS |
| VodafoneThree | 2 / 2 | 3 / 3 | PASS |

## Acceptance

Actual routes were rendered for Twin Map, Major Programmes, Opportunities, Explore Twin, Advanced Inspection, Research Gaps and all six Enterprise dossiers. HTML and the machine-readable exact sets are under `docs/operations/flora/rendered-population-reconciliation/`. Opportunities contain 17 `data-business-object-family='Opportunity'` containers; Programmes contain 13 `data-business-object-family='Programme'` containers. The diagnostic tables are computed with the same `business_object_id` and `enterprise_associations` functions as the pages.

Fresh import required: **NO**. Existing accepted/ignored staging dispositions are sufficient; the corrected request-time read projection consumes them correctly. Governance remains candidate, not reviewed, not promoted, not assessed, and not recommendation eligible.

## Merge gate

**SAFE TO MERGE** — all population and association exact-set invariants pass against the unchanged fixture and actual rendered routes.
