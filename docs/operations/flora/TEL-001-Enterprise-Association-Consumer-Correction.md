# TEL-001 Enterprise Association Consumer Correction

## Decision

**SAFE TO MERGE.** The shared Enterprise association consumer now presents the exact import-scoped, candidate-resolved Programme and Opportunity relationships supplied by the unchanged TEL-001 package. This is a read-only consumer correction; no candidate is reviewed, assessed, recommended, approved, or promoted.

## Root cause

`resolve_relationships()` already resolved `REL-W2-001` (`ENT-BT` → `PROG-BT-TRANSFORMATION`) and `REL-W2-014` (`OPP-BT-AI-ENGINEERING` → `ENT-BT`) in the candidate import scope. The first divergence was `enterprise_associations()`: it mixed resolver output with Programme/Opportunity object `subject`, `affected_organisations`, `owner`, and `owning_enterprise` fields. That was a second association rule, could manufacture an association without a Relationship row, and did not make the standalone candidate Relationship owner the exclusive input to the dossier.

The dossier then consumed that mixed set through `_associated_records()`. Earlier rendered audit artefacts showed zero because the presentation path had not consistently consumed the standalone resolved candidate rows. The candidate resolver required no change: endpoint IDs, relationship types, resolution status, and import-scoped endpoint objects were already present.

### Implementation traces

| Relationship | Endpoints | Resolver output | Consumer input | Consumer filtering | Resulting set |
|---|---|---|---|---|---|
| `REL-W2-001` | `ENT-BT` → `PROG-BT-TRANSFORMATION` | candidate relationship resolved; candidate endpoints resolved in import scope | shared `ResolvedRelationship` row | governed `Enterprise owns Programme`; Enterprise must be source and Programme must be target | `PROG-BT-TRANSFORMATION` exactly once |
| `REL-W2-014` | `OPP-BT-AI-ENGINEERING` → `ENT-BT` | candidate relationship resolved; candidate endpoints resolved in import scope | shared `ResolvedRelationship` row | governed `Opportunity targets Enterprise`; Opportunity must be source and Enterprise must be target | `OPP-BT-AI-ENGINEERING` exactly once |

## Architecture

- **Candidate business-object identity:** `business_object_id()` (immutable original/candidate identity).
- **Candidate relationship resolution/read owner:** `resolve_relationships()` and `ResolvedRelationship`.
- **Enterprise executive view model:** `_dossier()` consuming `_associated_records()`.
- **Programme/Opportunity executive view models:** `executive_record_view_model()` and the existing programme/opportunity cards.
- **Canonical Factual Projection:** `factual_projection_for_enterprise()` / `factual_projection_for_object()` remain unchanged.
- **Import/Twin scope:** one `SemanticTwin` assembled from one staging summary/import run; resolver endpoint lookup remains local to that Twin.
- **Direction semantics:** `Enterprise owns Programme` is consumed only as Enterprise → Programme; `Opportunity targets Enterprise` only as Opportunity → Enterprise.
- **Deduplication:** canonical/candidate business-object identity. Duplicate Relationship rows collapse to one object card while a stable Relationship ID/type remains available for explainability.

No new resolver, graph, semantic model, business-object model, factual projection, or governance workflow was introduced.

## Before / after

| Enterprise | Programmes before | Programmes expected | Programmes after | Opportunities before | Opportunities expected | Opportunities after |
|---|---:|---|---|---:|---|---|
| BT Group | 0 | `PROG-BT-TRANSFORMATION` | `PROG-BT-TRANSFORMATION` | 0 | `OPP-BT-AI-ENGINEERING`, `OPP-BT-AIOPS`, `OPP-BT-VERIZON-JV-INTEGRATION` | exact expected set |
| Openreach | 0 | `PROG-OPENREACH-FTTP` | exact expected set | 0 | `OPP-OPENREACH-FIBRE-AUTOMATION`, `OPP-OPENREACH-CP-ENABLEMENT`, `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` | exact expected set |
| Virgin Media O2 | 0 | `PROG-VMO2-LUMI-AI`, `PROG-VMO2-MOBILE-TRANSFORMATION` | exact expected set | 0 | `OPP-VMO2-AI-CX`, `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE`, `OPP-VMO2-NEXFIBRE-MIGRATION` | exact expected set |
| VodafoneThree | 0 | `PROG-VT-5G-SA`, `PROG-VT-INTEGRATION` | exact expected set | 0 | `OPP-VT-NETWORK-AI-OPS`, `OPP-VT-ENTERPRISE-5G`, `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` | exact expected set |
| CityFibre | 0 | `PROG-CITYFIBRE-WHOLESALE` | exact expected set | 0 | `OPP-CITYFIBRE-PROJECT-GIGABIT`, `OPP-CITYFIBRE-WHOLESALE` | exact expected set |
| TalkTalk | 0 | `PROG-TALKTALK-PXC-DEMERGER` | exact expected set | 0 | `OPP-TALKTALK-COST`, `OPP-PXC-PLATFORM-EFFICIENCY` | exact expected set |

## Advanced Inspection

Enterprise Association Reconciliation is calculated from the same `enterprise_associations()` owner used by the dossier. It displays resolved candidate IDs, rendered IDs, missing and unexpected associations, duplicate Relationship rows collapsed, and exact-set PASS/FAIL. The association anomaly total is based on the same resolved-versus-rendered equality, not promotion state.

## Source gap preserved

`PROG-BT-VERIZON-JV` lacks a source Relationship to `ENT-BT`. Flora therefore correctly does not associate it, even though its narrative and owner-shaped fields mention BT. This remains a Researcher/package gap.

`OPP-BT-VERIZON-JV-INTEGRATION` has explicit Relationship `REL-W4-183` to `ENT-BT`, so Flora associates it.

## Protected behaviour

- Opportunities remain 17 source, runtime, executive, and rendered business identities.
- Programmes remain 13 source, executive, and rendered business identities.
- Operating Model facts do not populate Financial Position, Material Pressures, Known Procurements, or Reinvention Timing.
- Enterprise, Programme, Opportunity, and Relationship objects remain candidates. Rendering performs no review, promotion, assessment, or recommendation.
- Fixture checksum remains `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.

## Fresh import

**Required: NO.** The correction changes only how already-resolved candidate relationships are consumed and presented. No persisted association or candidate read state is rebuilt.
