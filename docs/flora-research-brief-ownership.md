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

## Commercial context runtime completion assessment (2026-08-02)

The accepted runtime boundaries in ADR-014 and ADR-024 remain controlling. FP-014 is the later, proposed composition authority and WP2-003 specifies the workspace; this increment implements their runtime intent without creating FP-015, another Founding Paper, an ADR, a narrative engine, or a Twin representation. FP-014's proposed status is a programme-state reconciliation item: implementation does not silently promote the paper to accepted architecture.

| Capability | Architectural owner | Runtime owner | Persistence owner | Current route | Assessed behaviour and gap | Required change delivered |
|---|---|---|---|---|---|---|
| Commercial Mission | FP-014 composition boundary; accepted identity/configuration constraints | `CommercialMission` and executive workspace | Authenticated-user mission profile JSON adapter | `GET/POST /blueprint-import/{run}/mission` | Model and route existed, but employer fields were co-persisted and required for mission save | Mission saves independently; business fields and explicit validation are rendered |
| Employer Context | FP-014 commercial landscape boundary | `EmployerContext` | Independent authenticated-user employer profile JSON adapter | Same settings screen, independently selectable save scope | A projection existed only inside `CommercialMission`; there was no independent resolver/store | Independent contract, statuses, atomic persistence and explicit human-supplied labels |
| Mission status projection | WP2-003 / FP-014 | `_mission_indicator` | Derived from both profiles | Twin Map | Missing mission prompt linked to an existing route; context states were conflated | Separate Mission and Employer Context state shown once |
| Executive composition | FP-014 constrained by FEIR-001, EIRP-001 and ADR-014 | `_mission_relevance`, `_opportunities`, Twin Map | Derived, never persisted | `/blueprint-import/{run}` | Account/industry ordering existed; focus/horizon rationale was incomplete | Deterministic account, industry, focus and horizon rationale; canonical objects remain read-only |
| Research Gap export | WP2-003 readiness contract | `research_gap_brief` | Response-only Markdown derivative | `/blueprint-import/{run}/research-brief` | Mission and a projected employer section existed but unresolved employer data could not be independently resolved | Active independent contexts, mission readiness, researcher actions and user configuration actions are separated |
| Industry Twin | FP-012, FEIR-001/EIRP-001, ADR-014/024 | `SemanticTwin` read projection and import runtime | Existing staging/governance stores | Twin Map and detail routes | Canonical candidate import was already separate | Unchanged; commercial saves never receive or write a Twin |
| Market participants/offers | Existing Market Participant and imported semantic object authorities | `market_participant_twin` / `capability_offer` projections | Imported Twin stores for evidence; employer profile for declared internal context | Advanced Inspection | Market Participant records may exist per package; no governed Sopra Steria or universal offer catalogue is guaranteed | No supplier data is inferred; only explicit employer profile values support alignment readiness |
| Advanced Inspection | FP-013 progressive inspection | `_explorer`, diagnostics and canonical collection projections | Derived | `/blueprint-import/{run}/explore` | Technical explorer was secondary in navigation but retained “Twin overview” return language | Primary identity is Advanced Inspection and return language is “Back to Twin Map” |

### Explicit inspection answers

1. A canonical runtime `CommercialMission` model already existed in `commercial_mission.py`.
2. It was persisted by the authenticated-user JSON profile adapter at `config/flora/commercial_missions.json` (environment-overridable).
3. It is user-scoped through the accepted authenticated Flora principal; the imported package remains workspace/Twin-scoped.
4. `EmployerContext` existed only as a projection of mission fields. It now resolves and persists independently at `config/flora/employer_contexts.json` (environment-overridable), at the same user scope pending an organisation-profile adapter.
5. The Configure link did point to an implemented GET route and POST handler. The operational defect was contract/persistence incompleteness: required employer data was coupled to mission validation and no independent employer owner existed.
6. `_mission_indicator` in the Executive Intelligence Workspace generates the not-configured message.
7. `_mission_relevance`, `_opportunities`, `twin_readiness`, and the executive workspace projection consume mission context.
8. `research_gap_brief`, reached through `export_research_gap_brief`, generates the Markdown brief.
9. Market Participant or Enterprise records are package-dependent; repository inspection does not establish a canonical Sopra Steria record available to every imported Twin.
10. Imported `capability_offer` objects can exist, but no universal governed offer, competitor, or partner catalogue is available. Employer values therefore require explicit human supply and are not external evidence.
11. `/blueprint-import/{run}/explore` renders the legacy technical explorer; `/diagnostics` renders deeper diagnostics.
12. The explorer is intentionally secondary as Advanced Inspection. Its heading, primary navigation, and return route no longer claim another Twin home; Twin Map remains primary.
