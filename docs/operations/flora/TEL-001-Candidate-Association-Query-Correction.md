# TEL-001 Candidate Association Query Correction

## Finding and first divergence

1. **Did a reusable subject association query already exist?** No. `resolve_relationships()` was the canonical, import-scoped endpoint resolver, while `enterprise_associations()` was an Enterprise presentation consumer returning deduplicated object tuples. It was not a generic subject query and discarded duplicate Relationship evidence.
2. **What did 252 candidate-resolved relationships mean?** For 252 candidate Relationship rows, both exact endpoint identities existed uniquely in the same assembled candidate `SemanticTwin`, the relationship type was present, and no involved object was promoted. It did not mean that a subject lookup/index could return those rows.
3. **Why did Enterprise association lookup previously return None?** Before the preceding consumer correction, presentation did not consistently consume standalone resolved Relationship rows. After that correction it could render TEL-001, but the underlying interface was still an Enterprise-specific, deduplicating consumer rather than the required reusable subject association read boundary.
4. **What was the exact first divergence?** Immediately after `resolve_relationships()`: no API accepted an import-scoped Twin plus a business-object subject ID and returned faithful typed Relationship evidence. Endpoint resolution passed; reusable subject lookup did not exist.
5. **Which canonical owner was evolved?** `semantic_twin.py`, adjacent to `ResolvedRelationship` and `resolve_relationships()`, now owns `SubjectAssociation` and `query_subject_associations()`.
6. **How is either endpoint handled?** A relationship-type rule identifies the valid subject endpoint. `Enterprise owns Programme` locates the Enterprise at the source and reports an outgoing association. `Opportunity targets Enterprise` locates it at the target and reports an incoming association.
7. **How is type respected?** Only registered relationship types with their governed endpoint/family semantics qualify. This does not make relationships generally bidirectional.
8. **How is scope enforced?** The caller supplies one `SemanticTwin`, assembled from one candidate import run. Resolution and lookup see only objects in that Twin. A collision regression proves an endpoint in a second Twin cannot satisfy a relationship in the first.
9. **How are duplicates handled?** The query faithfully returns every Relationship row. `enterprise_associations()` remains the executive projection and deduplicates related objects by immutable business-object identity, never by title.
10. **Why is governance unchanged?** The capability is an immutable read projection. It does not invoke review, assessment, recommendation, approval, lifecycle, or promotion services.
11. **Why was None/None an invalid PASS?** The earlier diagnostic compared only query-resolved and rendered sets. Two empty derived sets could agree while non-empty source Relationship truth disappeared. TEL-001 diagnostics now independently derive source endpoint sets and require source expected = query resolved = rendered. A controlled empty-truth regression retains a valid zero/zero/zero PASS.

## Direct traces

| Relationship | Candidate resolver | Subject query | Result |
|---|---|---|---|
| `REL-W2-001` | `ENT-BT` and `PROG-BT-TRANSFORMATION`; `candidate relationship resolved`; `candidate endpoints resolved in import scope` | subject `ENT-BT`; type `Enterprise owns Programme`; outgoing | Programme returned |
| `REL-W2-014` | `OPP-BT-AI-ENGINEERING` and `ENT-BT`; `candidate relationship resolved`; `candidate endpoints resolved in import scope` | subject `ENT-BT`; type `Opportunity targets Enterprise`; incoming | Opportunity returned |

## Exact TEL-001 acceptance truth

| Enterprise | Programmes | Opportunities |
|---|---|---|
| BT Group (`ENT-BT`) | `PROG-BT-TRANSFORMATION` | `OPP-BT-AI-ENGINEERING`, `OPP-BT-AIOPS`, `OPP-BT-VERIZON-JV-INTEGRATION` |
| Openreach (`ENT-OPENREACH`) | `PROG-OPENREACH-FTTP` | `OPP-OPENREACH-FIBRE-AUTOMATION`, `OPP-OPENREACH-CP-ENABLEMENT`, `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE` |
| Virgin Media O2 (`ENT-VMO2`) | `PROG-VMO2-LUMI-AI`, `PROG-VMO2-MOBILE-TRANSFORMATION` | `OPP-VMO2-AI-CX`, `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE`, `OPP-VMO2-NEXFIBRE-MIGRATION` |
| VodafoneThree (`ENT-VODAFONETHREE`) | `PROG-VT-5G-SA`, `PROG-VT-INTEGRATION` | `OPP-VT-NETWORK-AI-OPS`, `OPP-VT-ENTERPRISE-5G`, `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` |
| CityFibre (`ENT-CITYFIBRE`) | `PROG-CITYFIBRE-WHOLESALE` | `OPP-CITYFIBRE-PROJECT-GIGABIT`, `OPP-CITYFIBRE-WHOLESALE` |
| TalkTalk (`ENT-TALKTALK`) | `PROG-TALKTALK-PXC-DEMERGER` | `OPP-TALKTALK-COST`, `OPP-PXC-PLATFORM-EFFICIENCY` |

`PROG-BT-VERIZON-JV` remains excluded because no explicit Relationship links it to BT. `OPP-BT-VERIZON-JV-INTEGRATION` remains included through `REL-W4-183`. No narrative or title inference is used.

## Protected outcome

The unchanged fixture checksum is `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`. Populations remain 17 Opportunities and 13 Programmes. Candidate lifecycle states and factual projection are unchanged. A fresh import is not required because the correction is read behaviour over the existing candidate scope.
