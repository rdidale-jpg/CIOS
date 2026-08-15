# TEL-001 Enterprise Identity Propagation Root Cause

## Decision

**SAFE TO MERGE**, subject to the validation recorded below. This correction is read-only. It does not change Relationship semantics, the immutable package, candidate state, promotion, assessment, recommendations, or canonical memory.

## Architectural identity ownership

| Layer | Canonical identifier for this read | Owner | Required lineage |
|---|---|---|---|
| Source object | Source-declared `id` (`ENT-BT`) | governed TEL-001 record set | immutable ZIP member and record location |
| Candidate | `candidate_record_id`; source identity in `original_source_id` | validator/staging Candidate Import Record | package/import-run scope + original external stable ID |
| Semantic object | `SemanticObject.record_id`; source identity in `original_id` | `semantic_twin._object` | staged candidate ID + original ID |
| Canonical Factual Projection | imported object identity exposed as `object_id`; source lineage includes original ID | `factual_projection_for_enterprise` | semantic Enterprise and its source lineage |
| Executive Enterprise | presentation key plus explicit source, candidate and Relationship-subject identities | `assemble_semantic_twin` / `SemanticEnterprise` | candidate record → original stable ID; no label inference |
| Route | display slug (`bt-group`) | executive workspace navigation | route resolves to the import-scoped `SemanticEnterprise` |

This follows accepted ADR-012 §4: every candidate preserves its original external stable ID and import-run lineage, and §8: identity uses owned canonical rules, external stable IDs, and package lineage. It also follows the read-interface rule that runtime projection identity must not replace canonical identity and that display names are not identifiers.

## BT forensic trace (actual values)

| Boundary | Runtime owner | Kind | Primary ID | Source/candidate lineage | Scope/name/slug |
|---|---|---|---|---|---|
| TEL-001 | `record_sets/enterprise_dossiers_wave5.ndjson` | `Enterprise Dossier` | `ENT-BT` | source `id=ENT-BT` | `TEL-001`; BT Group |
| Archive/manifest | package registry / manifest reader | immutable package member | package `TEL-001_UK-Telecoms-Twin_Wave5-Corrected` | member path retained | import-run/package scope |
| Validator/staging | Candidate Import Record | `enterprise_twin` | generated `candidate_record_id` | `original_source_id=ENT-BT`, `source_file=record_sets/enterprise_dossiers_wave5.ndjson`, source payload retains `id=ENT-BT` | same import run; BT Group |
| Semantic object | `_object` | `SemanticObject` | candidate record ID | `original_id=ENT-BT`; attributes retain mapped source payload | candidate; BT Group |
| Factual projection | `factual_projection_for_enterprise` | `CanonicalFactualProjection` | `ENT-BT` | `source_lineage` includes record member/location and `ENT-BT` | candidate; Enterprise Dossier |
| Executive | `assemble_semantic_twin` | `SemanticEnterprise` | source/Relationship identity `ENT-BT` | source `ENT-BT`; staged candidate record ID explicitly exposed | presentation `bt-group` |
| Route/render | `executive_workspace_page` | Enterprise dossier | `bt-group` route key | route resolves the above executive object, whose Relationship subject is `ENT-BT` | BT Group |

### First divergence

`ENT-BT` was last present on the staged candidate as `original_source_id` and on `SemanticObject.original_id`. It became unavailable at semantic Enterprise assembly: the constructor considered only payload `enterprise_id`/`canonical_id`, then reconstructed `bt-group` from the name when those redundant fields were absent. The source `id` was already correctly retained; it was simply omitted from the governed executive read interface.

The transformation to a display slug was intentional; loss of the original-ID lineage was not. The semantic Enterprise constructor is the earliest canonical owner of the combined executive identity projection and therefore the correct owner to fix. No relationship resolver or page-specific association rule was changed.

## Correction

`assemble_semantic_twin` now uses the staged semantic object's `original_id` after an explicit source `enterprise_id`/`canonical_id` and before any display fallback. `SemanticEnterprise` exposes distinct `source_identity`, `candidate_identity`, `presentation_key`, and `relationship_subject_identity` values. The shared association consumer queries the governed Relationship-subject value. All values originate in the staged candidate; there is no alias table, name match, title match, or slug reconstruction for Relationship identity.

No fresh import is required because every existing staged Candidate Import Record already persists `original_source_id`. Reconstructing the read model is sufficient.

## Required questions

1. TEL-001 assigns BT `ENT-BT`.
2. Candidate runtime assigns a generated `candidate_record_id` and preserves `original_source_id=ENT-BT`.
3. Semantic runtime assigns the candidate record ID to `record_id` and preserves `original_id=ENT-BT`.
4. The factual projection exposes Enterprise object ID `ENT-BT` and includes `ENT-BT` in source lineage.
5. Executive runtime uses `bt-group` for presentation and exposes `ENT-BT` as source/Relationship-subject identity.
6. `bt-group` is a route/navigation slug, not Relationship identity.
7. `ENT-BT` became unavailable at the staged candidate/SemanticObject → `SemanticEnterprise` assembly boundary.
8. The separate route transformation was intended; dropping lineage was not.
9. Candidate record → original external ID → executive Relationship subject was supposed to survive.
10. The semantic Enterprise constructor failed to expose it.
11. That constructor and its shared executive contract were corrected.
12. An alias table is unnecessary because staging already owns `original_source_id`.
13. The actual BT executive object retrieves `REL-W2-001` and `PROG-BT-TRANSFORMATION`.
14. It retrieves incoming `REL-W2-014` and `OPP-BT-AI-ENGINEERING` under the existing typed direction rule.
15. All six source/query/render exact sets agree.

## Exact reconciliation

| Enterprise | Source / Relationship identity | Programme IDs (source = query = rendered) | Opportunity IDs (source = query = rendered) |
|---|---|---|---|
| BT Group | `ENT-BT` | `PROG-BT-TRANSFORMATION` | `OPP-BT-AI-ENGINEERING`, `OPP-BT-AIOPS`, `OPP-BT-VERIZON-JV-INTEGRATION` |
| CityFibre | `ENT-CITYFIBRE` | `PROG-CITYFIBRE-WHOLESALE` | `OPP-CITYFIBRE-PROJECT-GIGABIT`, `OPP-CITYFIBRE-WHOLESALE` |
| Openreach | `ENT-OPENREACH` | `PROG-OPENREACH-FTTP` | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE`, `OPP-OPENREACH-CP-ENABLEMENT`, `OPP-OPENREACH-FIBRE-AUTOMATION` |
| TalkTalk | `ENT-TALKTALK` | `PROG-TALKTALK-PXC-DEMERGER` | `OPP-PXC-PLATFORM-EFFICIENCY`, `OPP-TALKTALK-COST` |
| Virgin Media O2 | `ENT-VMO2` | `PROG-VMO2-LUMI-AI`, `PROG-VMO2-MOBILE-TRANSFORMATION` | `OPP-VMO2-AI-CX`, `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE`, `OPP-VMO2-NEXFIBRE-MIGRATION` |
| VodafoneThree | `ENT-VODAFONETHREE` | `PROG-VT-5G-SA`, `PROG-VT-INTEGRATION` | `OPP-VT-ENTERPRISE-5G`, `OPP-VT-NETWORK-AI-OPS`, `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` |

`PROG-BT-VERIZON-JV` remains absent because no explicit Relationship supplies it. `OPP-BT-VERIZON-JV-INTEGRATION` remains present through `REL-W4-183`. Relationship resolution remains 308 retained / 252 candidate-resolved. Programme population remains 13 and Opportunity population remains 17.

## Diagnostics and rendered acceptance

Advanced Inspection independently reads explicit source Relationship endpoints, queries via each executive object's Relationship-subject identity, and reads rendered business-object IDs. It displays all four identities and all three exact sets. A non-empty source/empty query is FAIL; query/render disagreement is FAIL. The import screen names this correction, says no fresh import is required, and makes functional acceptance primary.

Actual route acceptance covers Import Twin, Explore Twin/Advanced Inspection, Major Programmes, Opportunities, and all six presentation routes. The route regression starts with the presentation slug and resolves the real executive object; it does not invoke `ENT-BT` as a route shortcut. An import-scope regression demonstrates that an executive object carrying a different source identity cannot acquire BT associations merely because its display identity is `bt-group`.

## Protected and out of scope

Candidate governance, factual isolation, promotion, human decision state, assessment state, and recommendation eligibility are unchanged. Known out-of-scope defects remain: Operating Model raw-dictionary rendering; Financial Position diagnostic/presentation disagreement; general dossier wording; Research Gap presentation; unrelated executive presentation defects.

Fixture SHA-256: `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07` (unchanged).
