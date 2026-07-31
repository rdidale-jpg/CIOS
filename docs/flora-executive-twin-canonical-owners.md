# Flora executive Twin canonical owners

This revision evolves the existing semantic Twin projection and executive workspace. It does not add a reasoning engine or a parallel translation layer.

| Capability | Canonical owner | Current input | Current output | Current gap | Required evolution |
|---|---|---|---|---|---|
| Executive insight qualification | `semantic_twin.executive_insight_eligible` | Immutable `SemanticObject` | Eligibility decision used by Insights | Previously accepted weak base eligibility | Require subject, observation, consequence, association, evidence, confidence and timing/freshness |
| Opportunity projection | `semantic_twin.business_collections` | Opportunity hypothesis/ranked opportunity objects | Canonical Opportunities collection | Only a composition count | Render the existing collection as first-class executive cards |
| Enterprise opportunity association | `semantic_twin.assemble_semantic_twin` | Explicit subject, affected organisation and references | Records attached to `SemanticEnterprise` | Affected-organisation links were not attached | Reconcile explicit affected organisations without inferring fit |
| Transformation programme projection | `semantic_twin.business_collections` and the executive workspace | Transformation programme objects | Collection and dossier records | No business dossier section | Present supported programmes in business order |
| Reinvention/pressure classification | Executive workspace projection over canonical semantic objects | Typed programmes, regulation, technology, financial and change records | Business theme/pressure cards | Not presented | Deterministic classification constrained by canonical type and evidence |
| Timing and urgency | Executive workspace pressure projection | Explicit deadline, timetable, programme/transition timing and dated qualifying change | Timing or explicit timing gap | Urgency absent | Never infer urgency from a record date alone |
| Enterprise dossier composition | `executive_workspace._dossier` | `SemanticEnterprise` and its canonical records | Enterprise business dossier | Technical/generic ordering | Business-complete ordered, empty-section-hiding dossier |
| Enterprise overview | `executive_workspace._dossier` | Identity description and supported associated change | Plain-language overview | Identity boilerplate | Description, role, domains, position, change and completeness |
| Financial data projection | Enterprise dossier over financial semantic objects | Structured metric/value/currency/period/source | Key financial item | Context-free values could surface | Render only context-complete measures; report gaps otherwise |
| Procurement records | Existing canonical procurement, procurement-route and buying-centre object types | Explicit associated procurement evidence | Known Procurements | Absent from dossier | Render only explicit records; no programme-to-procurement prediction |
| Source/evidence presentation | Enterprise dossier over `evidence` objects | Evidence title, origin/date/link/support fields and lineage | Key Sources plus advanced metadata | Source titles could resemble conclusions | Separate sources from qualified insights |
| Twin completeness/coverage diagnostics | Executive workspace deterministic completeness functions and Twin Health | Read-only semantic enterprise records | Aspect states and missing fields | Only record-count validation | Apply explicit presentation-quality rules without aggregate truth score |
| Researcher feedback | `executive_workspace._researcher_feedback` | Completeness and semantic exclusions | Non-blocking Twin Health/import diagnostics | Flat generic gap groups | Report Twin → domain → enterprise → aspect → missing information |

Commercial Mission is supplied separately and changes prominence/relevance only. Completeness output is advisory, does not mutate canonical records, does not resolve evidence gaps, and does not authorise promotion.

## Mission-aligned readiness owner assessment

| Capability | Architectural owner | Runtime owner | Persistence owner | Current implementation / UI / tests | Gap addressed and required evolution |
|---|---|---|---|---|---|
| Commercial Mission and preferences | FP-014 executive relevance boundary (review architecture), constrained by FEIR-001/EIRP-001 | `commercial_mission.CommercialMission` and executive workspace | Authenticated-user profile JSON, separate from package and canonical Twin stores | Selectable compact indicator, business settings and user-scoped persistence; mission tests | Contract extended with account, objective, supplier and presentation policy without changing Twin truth |
| Target accounts, competitors and partners | Commercial Mission operational context | `commercial_mission` plus `_mission_relevance` | User mission profile | Explicit configuration; deterministic rationale inspected alongside eligible opportunity | No values inferred from package prose |
| Supplier capabilities and offers | EIRP-001 commercial assessment | Existing `offer_portfolio` mission field and canonical `capability_offer` Twin objects | User profile for declared supplier context; Twin store for imported facts | Mission readiness reports absence separately | Catalogue absence constrains mission readiness only |
| Opportunities and procurement | EIRP-001 Strategic Sales projection | `semantic_twin.business_collections`, `_opportunity_contract` | Existing staged/canonical object stores | Governed five-column projection and incomplete-record Browse route | Prominent rows now require explicit customer, problem, evidence, confidence, procurement timing and status |
| Transformation and reinvention | FP-012; existing semantic translation | `semantic_twin` and executive workspace | Existing staged/canonical object stores | Plain-language projection; timing precedes themes | Readiness exposes missing owner, phase, horizon, mechanism and evidence |
| Completeness, evidence demands and feedback | EIRP-001 completeness/evidence demands | `twin_readiness` projection over semantic validation and diagnostics | Read-only derivation; no new truth store | Versioned states, inspection and Researcher Feedback | Existing import diagnostics evolved into aspect readiness; no weighted aggregate |
| Executive presentation and translation | FEIR-001 | `executive_workspace` and `semantic_twin` | No duplicate persistence | Workspace, dossiers, explorer and health tests | Eligibility suppresses Absent/Insufficient content without hiding Browse access |

### Explicit findings

1. A canonical runtime Commercial Mission object exists in `commercial_mission.py`; it is operational composition context, not imported Twin truth.
2. It is persisted in the configured mission-profile JSON file, atomically and separately from imports.
3. It is scoped to the authenticated user. No workspace or organisation scope is silently asserted.
4. The authenticated headers resolve the mission and supply it directly to executive composition.
5. Mission account and industry criteria affect deterministic opportunity relevance and ordering, not merely display; they never mutate the objects.
6. No pilot mission is assumed or hard-coded. An authorised user configures one through the settings route.
7. No Sopra Steria catalogue is assumed. A user may declare an offer portfolio; imported `capability_offer` objects remain separate Twin content.
8. Competitors, partners and target accounts are only configured when explicitly present in the selected user mission.
9. Existing semantic completeness, validator diagnostics and evidence-demand surfaces existed and remain the canonical basis.
10. Those import diagnostics can, and now do, feed a single aspect-readiness projection and its researcher actions without becoming another reasoning or promotion engine.

## Executive Twin Map owner evolution

| Capability | Canonical owner | Current behaviour | Required evolution |
|---|---|---|---|
| Executive Intelligence Workspace | `blueprint_import.executive_workspace.executive_workspace_page` | Composed a long executive report | Compose the concise six-aspect Twin Map and preserve candidate context. |
| Twin Readiness and rules | `executive_workspace.twin_readiness` | Readiness dimensions over structured presence | Apply six explicit business-usefulness contracts and never advance from volume alone. |
| Twin Composition | `semantic_twin.business_collections` consumed by `executive_workspace` | Separate collection-count grid | Feed counts into the relevant Twin Map tiles; retain the full inventory only in Browse Full Twin. |
| Twin Health and Research Gaps | `executive_workspace._health`, validation and researcher-feedback helpers | Mixed executive gaps with technical diagnostics | Present six concise Research Gaps summaries and retain the same technical content under Advanced diagnostics. |
| Twin Explorer and collection routing | `executive_workspace._explorer` and `flora.web.app` | Primary tiles opened generic collections | Keep the explorer as Browse Full Twin and route primary tiles to contextual aspect pages. |
| Business display names | `SemanticEnterprise.name` and executive presentation helpers | Enterprise dossiers resolved names, while diagnostics exposed source IDs | Use supported names or explicit incomplete-record labels in business views; reserve canonical codes for advanced inspection. |
| Canonical identifier resolution | `semantic_twin.assemble_semantic_twin` | Reconciles canonical enterprise identity and attached records | Reuse resolved identity for direct dossiers and distinct affected-record counts. |
| Domain filtering | `_domain_lenses`, semantic object domains and `business_collections` | Filtered composition/explorer views | Carry the selected domain into every aspect route without changing canonical scope. |
| Governance | Existing inspect/review routes and access services | Sometimes appeared as peer navigation | Keep authorised governance in advanced inspection rather than business-primary navigation. |
