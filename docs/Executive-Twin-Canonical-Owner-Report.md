# Executive Twin canonical-owner report

This revision changes the existing semantic projection and Executive Workspace;
it does not add a reasoning engine or a parallel Twin translator.

| Capability | Canonical owner | Current input | Current output | Required change delivered |
|---|---|---|---|---|
| Twin composition mapping | `semantic_twin.BUSINESS_COLLECTIONS` and `business_collections` | Immutable `SemanticTwin.objects` | Business navigation collections | Canonical wrapper ownership makes counts represent distinct concepts while all semantic records remain inspectable. |
| Executive prominence and Material Insight classification | `semantic_twin.executive_insight_eligible` | Typed `SemanticObject` fields | Strictly qualified insight collection | Requires subject, observation, supplied consequence, supported domain, evidence, confidence and timing; labels, sources, capabilities and unsupported claims are excluded. |
| Subsector/domain representation | `SemanticObject.domains` populated by `_object` | Existing domain/subsector fields and canonical TMS associations | All Twin, Telecoms, Media, Sport and Cross-domain lenses | Filtering is deterministic; Cross-domain requires at least two explicit associations and never uses package co-location. |
| Insight explanation | `executive_workspace._conclusion` | Qualified `SemanticObject` | Clickable executive card and progressive explanation | “Why it matters” is supplied, Sources are collapsed, and lineage is under Advanced explanation. |
| Enterprise card composition | `executive_workspace._enterprise_card` | `SemanticEnterprise.records` | Clickable dossier card | Empty change placeholders and zero counts are suppressed; grammar and direct navigation are corrected. |
| Twin health and governance | `executive_workspace._health`, existing review/inspect routes | Semantic Twin, staging diagnostics and protected package routes | Secondary Twin Health destination | Validation, coverage, unknowns, contradictions, audit, candidate state and authorised governance are separated from the executive home. |
| Package-quality diagnostics | Existing validator/staging summary plus `_researcher_feedback` | Immutable imported candidates and coverage metadata | Non-blocking Researcher Feedback Report | Gaps are grouped for later package-contract research without mutating records or blocking import. |

## Count reconciliation

For the configured TMS-001 entry point, the business collection projection now
reports **14 Enterprises**, **10 Market Participants**, and **9 Opportunities**.
The paired `enterprise`, `market_participant`, and `ranked_opportunity` semantic
records remain available in advanced inspection but do not inflate those three
business counts. **81 Evidence Sources**, **34 Unknowns**, and **24
Contradictions** remain typed one-to-one records and are therefore unchanged.
Any future wrapper identity that cannot be reconciled must remain visible in
Twin Health rather than being merged by display label.
