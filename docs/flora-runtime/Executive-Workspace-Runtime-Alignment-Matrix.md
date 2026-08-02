# Executive Workspace Runtime Alignment Matrix (WP3)

**Status:** canonical implementation reference for WP3. This is an implementation binding, not an architectural owner. It changes no accepted architecture and creates no FP-015.

## Runtime owner map

`ExecutiveAssessmentProjection` is a read-only, non-persistent presentation adapter. It owns no information, completeness rules, reasoning, evidence, eligibility policy, scoring, or lifecycle decision. It copies an owner-supplied result or returns `legacy_unassessed`; record volume and field presence can never manufacture readiness.

| Executive Workspace component | Runtime object | Canonical owner | Evidence source | Completeness authority | Eligibility authority | Research-gap authority | Current implementation | Required change / WP3 reference |
|---|---|---|---|---|---|---|---|---|
| Twin Map readiness tiles/bars | `ExecutiveAssessmentProjection` via compatibility facade `twin_readiness` | FP-013/FP-014 presentation; subject owner per row below | Owner result reference, or explicit “not supplied” | IT-001 controlled High-Fidelity dimensions | EIRP-001 S09–S12 | IT-001 §10 plus the subject owner | Activated: no bar score is generated; missing output is `legacy_unassessed` | Consume owner-emitted High-Fidelity result without translating it into a new score |
| Research Gaps page and Markdown brief | Same projection instance | IT-001 composition; EI-001/EIF-001 information semantics | Deficiencies/evidence/exhaustion/review references carried by owner result | Named dimension in each row | EIRP-001 | IT-001 §10; EI-001/EIF-001 requirements | Activated: gap includes owner, missing information, impact, required evidence, acceptance criteria | Add no local field checklist; render richer owner deficiencies when packages emit them |
| Advanced readiness inspection | Same projection instance | FP-013 inspection / FP-014 composition | Owner result ID/source | IT-001 | EIRP-001 | Same owner result | Activated: exposes distinct owner, completeness and eligibility authority | Preserve traceability and never upgrade owner state |
| Industry Overview | projection key `industry-overview` | IT-001 | Industry facts/observations and owner assessment references | Industry Fidelity, Temporal Fidelity, Evidence Maturity, Source Diversity | EIRP-001 S09–S12 | IT-001 §10 | Replaced “one insight = Usable” heuristic with owner projection | Ingest the exact IT-001 dimension names and deficiencies |
| Enterprises / enterprise dossiers | projection key `enterprises` | EI-001 and EIF-001; EI-003/EI-002 for delegated behaviour/graph semantics | Enterprise objects and owner-linked evidence | Enterprise Intelligence Density, Financial Intelligence, Temporal Fidelity, Graph Integrity | EIRP-001 S09–S12 | IT-001 §10 plus EI-001/EIF-001 requirements | Top-level assessment activated; legacy dossier section-availability checks remain presentation-only | Project subject-level EI-001/EIF-001 results when supplied; do not infer dossier completeness |
| Market Participants | projection key `market-participants` | IT-001 delegation; participant owner remains architecturally unresolved | Participant/capability/relationship evidence | Market Participant Density, Capability and Offer Intelligence, Graph Integrity | EIRP-001 S09–S12 | IT-001 §10 | Replaced role/domain/evidence/consequence “sufficiently classified” assessment | Preserve `owner unresolved`; consume an accepted participant-owner result when available |
| Major Programmes | projection key `major-programmes` | EI-001 Transformation Portfolio; EIF-001 Change Landscape; EI-002 relationships | Programme and linked evidence objects | Enterprise Density, Temporal Fidelity, Graph Integrity, Evidence Maturity | EIRP-001 S09–S12 | IT-001 §10 plus enterprise owners | Replaced local executive-ready predicate at top-level/readiness gap | Section rendering prerequisites may hide malformed cards but must not claim completeness |
| Opportunities | projection key `opportunities` | EI-004 reasoning and FP-009 hypothesis validation (specialised EI-006/OT-001 delegation retained by IT-001) | Opportunity/reasoning/evidence lineage | Opportunity Completeness, Commercial Reasoning Lineage, Evidence Maturity, Decision Maturity | EIRP-001 S09–S12 | IT-001 §10 | Readiness no longer uses `_opportunity_contract` or mission relevance; “sales-ready” is not an assessment state | Consume owner completeness and recommendation-eligibility outputs separately; mission only orders context |
| Reinvention Timing | projection key `reinvention-timing` | EI-001/EIF-001, EI-003 and FP-012; FP-014 presentation | Transformation observations, history and evidence | Temporal Fidelity, Observation and Explanation Maturity, Evidence Maturity, Decision Maturity | EIRP-001 S09–S12 / FP-014 presentation | IT-001 §10 | Replaced AI-label/field-presence readiness pass with owner projection | Render an FP-014 stage only when its inspectable owner basis is supplied |
| Promotion summary completeness/maturity percentages | no assessment object | IT-001 promotion; ADR-009 decision maturity | Owner governance decision | IT-001 promotion gates | Protected governance authorisation | Owner decision deficiencies | Removed local weighted percentage/cap/penalty calculation; explicitly “Not assessed” | Consume separately recorded owner decisions only; never infer promotion from package validity |

## Repository locations

| Concern | Location |
|---|---|
| Runtime composition contract | `cios/applications/flora/blueprint_import/intelligence_projection.py` |
| Executive Workspace projection/rendering | `cios/applications/flora/blueprint_import/executive_workspace.py` |
| Promotion governance presentation | `cios/applications/flora/blueprint_import/views.py` |
| Canonical authorities | `architecture/enterprise-intelligence/`, `architecture/reference-architecture/standards/EIF-001-Enterprise-Intelligence-Foundation-Model.md`, `architecture/specifications/industry-twins/`, `architecture/specifications/flora/`, `architecture/founding-papers/`, `architecture/decisions/` |

## Removed heuristic list

1. `executive-readiness-v3` six-aspect state machine and its `Absent / Insufficient / Partial / Usable / Executive-ready` bars.
2. Insight-count proxy for Industry Overview readiness.
3. Field-presence predicates claiming Enterprise, Market Participant and Major Programme readiness.
4. Mission-sensitive `_opportunity_contract` as the owner of Opportunity completeness in the readiness projection.
5. AI-specific field-presence pass for Reinvention Timing readiness.
6. Weighted `maturity.py` percentages, caps and penalties from the promotion view. The module is removed rather than retained as an alternative completeness owner.
7. Generic research-gap commissioning from the preceding local readiness predicates.

## Architecture activation summary

### Activated and reused

- IT-001 and its controlled High-Fidelity dimension names now own information-completeness projection and research-completion gaps.
- EI-001/EIF-001, EI-002, EI-003, EI-004, FP-009 and FP-012 are delegated subject owners rather than duplicated by UI rules.
- FP-013/FP-014 remain presentation/composition authorities only.
- EIRP-001 remains the distinct eligibility authority; FEIR-001 remains the runtime/addressability boundary; ADR-014 and ADR-024 remain evidence/runtime boundaries.

### Not yet activated

- Repository packages currently expose legacy weighted `maturity_assessment` records rather than an IT-001 22-dimension `high_fidelity_completeness_assessment`. They are honestly shown as `legacy_unassessed`.
- Owner-produced EIRP recommendation-eligibility and IT-001 promotion results are not yet present in the imported semantic model.
- Subject-level Enterprise/Participant/Programme assessment envelopes are not yet emitted by packages.

### Remaining runtime heuristics and architectural gaps

- `_enterprise_completeness` and card-level field checks still decide whether content is displayable in dossiers/collection pages. They are presentation safeguards, not readiness or promotion claims, but should be replaced by subject-level owner results when available.
- `_opportunity_contract` still gates the legacy opportunity table and dossier card. It no longer controls readiness or Research Gaps; WP3 must replace it when an EIRP eligibility result is supplied.
- The accepted canonical Market Participant owner remains unresolved in IT-001. Runtime preserves that gap and does not invent an owner.
- IT-001, EIRP-001, FP-013 and FP-014 retain their repository statuses; runtime activation does not silently promote them.

## Before / after evidence

| Before | After |
|---|---|
| A package with one insight could display `Usable`; field counts generated bars and `executive-readiness-v3` gaps. | The same package displays `legacy_unassessed`, its inventory, exact owner/dimensions, missing owner output, evidence required and acceptance criteria; no bars are calculated. |
| Promotion UI displayed locally weighted Candidate Twin maturity and Decision completeness percentages. | Promotion UI states that IT-001 completeness, ADR-009 decision maturity and promotion readiness are not assessed or inferred without their owner outputs. |

The Twin Map layout, routes, tile labels and responsive styling are unchanged. Only the assessment content and traceability have changed.
