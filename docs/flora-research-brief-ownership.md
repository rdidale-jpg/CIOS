# Research brief context ownership

| Capability | Canonical owner | Persistence owner | Current UI | Runtime use | Gap |
|---|---|---|---|---|---|
| Commercial role, objectives, industries, accounts, geography, horizon and interests | `CommercialMission` | Authenticated-user JSON profile adapter | Commercial Settings | Mission relevance and brief purpose | Governance adapter may replace human-supplied values |
| Employer organisation, offers, propositions, partners, competitors and constraints | `EmployerContext` projection | Separate employer fields in the authenticated-user profile | Employer Context section of Commercial Settings | Employer-alignment disclosure only | Governed capabilities and credentials remain unresolved when not supplied |
| Industry and enterprise intelligence | `SemanticTwin` | Blueprint import staging/canonical governance stores | Twin Map, executive aspects and Advanced Inspection | Readiness, completeness, evidence and lineage | Enrichment is commissioned by the Research Gap brief |
| Six-aspect Twin readiness | `twin_readiness` / `ReadinessAspect` | Derived; not persisted | Twin Map and Research Gaps | Executive projection and export acceptance criteria | None; the exporter reuses this owner |
| Enterprise completeness | `_enterprise_completeness` / `CompletenessAspect` | Derived; not persisted | Enterprise dossier and diagnostics | Enterprise research work and acceptance tests | Some imported shapes cannot yet populate every business field |
| Import diagnostics and candidate governance | Blueprint validator, registry and review plan | Blueprint package registry/staging store | Import review and Advanced Inspection | Authorisation, traceability and non-mutating export | Comparison after a later import is prepared but non-blocking |
| Evidence and lineage | `SemanticObject.evidence_refs` and imported evidence records | Imported Twin stores | Key Sources and Advanced Inspection | Evidence/source gaps and appendix IDs | Source metadata may be incomplete |
| Markdown document export | `research_gap_brief` | Download response; no new document store | Export Research Brief in Research Gaps | Research commissioning derivative | PDF/DOCX is not added because Markdown is the existing canonical text format |

## Authority boundary

Commercial Mission describes **what the user is trying to achieve**. Employer Context describes **the supplier organisation from which the user operates**. The imported Industry Twin describes **external market, enterprise, programme, opportunity and evidence intelligence**. The exporter presents these authorities separately and never infers supplier capabilities from the employer name.
