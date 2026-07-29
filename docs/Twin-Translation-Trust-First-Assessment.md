# Imported Twin translation capability assessment

## Investigation and decision

The investigation covered Blueprint Import staging and package contracts, `IndustryTwinDeltaAdapter`, semantic assembly, the Executive Intelligence Workspace, Twin Explorer, enterprise dossiers, Twin Inspection adapters, Enterprise Canvas/Digital Twins routes, architecture authorities, tests, implementation reports, and Git history.

The canonical imported-Twin translation owner is `blueprint_import.semantic_twin.assemble_semantic_twin`. Its input is the existing list of staged candidate dictionaries; its immutable output is `SemanticTwin`, containing `SemanticObject` and explicitly resolved `SemanticEnterprise` records. The function was introduced in programme increment commit `5a8ac86` (“Complete mission-aware imported Twin workspace”), then corrected for TMS semantics in `0171902`. The Executive Workspace, Explorer and dossier already consume this same assembly result through `executive_workspace_page`; no parallel translator is required.

This increment evolves that owner with `business_collections`, a read-only navigation projection over the same immutable objects. The vocabulary is Enterprises, Market Participants, Opportunities, Insights, Financial Intelligence, Transformation Programmes, Capabilities and Offers, Relationships, Evidence Sources, Unknowns, Contradictions, and the recoverable advanced collection Other Twin content. Object identity is retained and each object has one collection membership. Canonical objects and candidate/governed semantics are not mutated.

## Capability map

| Capability | Canonical owner | Implemented source | Previous behaviour | Reusable | Gap addressed |
|---|---|---|---|---|---|
| Package semantic type translation | Blueprint Import staging boundary | `industry_delta_adapter.py` | Contract records became typed candidates | Yes | Retained unchanged |
| Candidate object interpretation | Imported-Twin semantic projection | `semantic_twin.py:assemble_semantic_twin` | Normalised statement, subject, evidence, confidence, freshness, eligibility and immutable identity | Yes | Extended at its owner with business collections |
| Executive prominence | Executive Workspace derived runtime view | `executive_workspace.py:_themes` | Eligible interpretations grouped by deterministic themes | Yes | Evidence mechanics moved into intentional expansion |
| Twin composition | Semantic projection plus Explorer view | `semantic_twin.py`, `executive_workspace.py` | Raw aspect-coverage table was primary | Yes | Navigable non-empty business tiles are primary; raw coverage is advanced |
| Enterprise dossier association | Semantic assembly | `semantic_twin.py:assemble_semantic_twin` | Explicit identity seeds, exact subject identity and resolved references; never package scope alone | Yes | Twin-scope unknown/contradiction leakage removed |
| Evidence and lineage | ADR-014/import inspection | `SemanticObject`, `_conclusion`, existing inspect route | Repeated metadata beneath each statement | Yes | Preserved one deliberate disclosure away |
| Candidate governance | Blueprint review/promotion | existing review and inspect routes | Prominent throughout reading flow | Yes | Dedicated navigation/action; no promotion changes |
| Enterprise Canvas / Digital Twins | Existing application routes | `digital_twins.py`, web application entry point | Import Twin entry and governed Twin navigation | Yes | Retained; no second explorer application |

## Bypass and consolidation findings

Before this increment raw canonical/runtime type names bypassed business translation in Explorer aspect rows, validation summaries, and dossier record rendering. The workspace, Explorer, and dossier shared semantic assembly but did not share a business collection vocabulary. `business_collections` now supplies that vocabulary to overview tiles and Explorer filtering. Advanced aspect coverage, package inspection, canonical identifiers, excluded content, evidence, lineage, and governance remain recoverable.

Counts are computed from the current `SemanticTwin`; no deployed count is hard-coded. Non-empty tile counts reconcile to unique semantic objects represented by mapped types. Unmapped types appear in Other Twin content. The full aspect table remains within Advanced aspect coverage.

## Experience change

Primary reading now progresses from Twin overview to composition tiles, filtered business collection, enterprise dossier or insight, then explanation and evidence. Candidate state appears discreetly at Twin level. Repeated type, sufficiency, confidence, freshness, lineage, and governance labels were removed from collapsed insight cards; they remain in “Explain this insight”, advanced aspect coverage, package inspection, and Candidate governance.

No canonical model, promotion permission, candidate truth status, source evidence, contradiction, freshness, confidence, or lineage contract changed.
