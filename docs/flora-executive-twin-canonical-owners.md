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
