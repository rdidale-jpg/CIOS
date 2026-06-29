# Ontology Relationship Taxonomy

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-000-REL |
| Title | Ontology Relationship Taxonomy |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Modelling Rules

Relationships shall be first-class objects with identifiers, definitions, categories, direction, allowed source types, allowed target types, multiplicity, evidence and lifecycle status.

| Category | Definition | Example Relationships | Allowed Source / Target Guidance | Modelling Notes |
|---|---|---|---|---|
| Structural | Links that describe composition, hierarchy or arrangement. | `part_of`, `contains`, `reports_to` | Source and target should be structural entities or roles. | Use when the relationship changes object structure, not ownership. |
| Ownership | Links that describe possession, accountability or stewardship. | `owns`, `owned_by`, `accountable_for` | Source is usually an entity or role; target is an entity, asset, measure or artefact. | Ownership may imply governance but should not replace approval relationships. |
| Dependency | Links that describe reliance, prerequisite or enabling conditions. | `depends_on`, `enables`, `requires` | Source may be any concept; target should be the required or enabling concept. | Capture direction from dependent to dependency unless catalogue states otherwise. |
| Governance | Links that describe authority, policy, approval or control. | `governs`, `approves`, `controls` | Source should be an authority, role or governance entity; target is governed artefact. | Record evidence and review decision where governance affects conformance. |
| Behavioural | Links that describe conceptual action or participation. | `performs`, `triggers`, `responds_to` | Source is actor or behaviour-bearing concept; target is behaviour, event or object. | Do not encode runtime workflow logic. |
| Commercial | Links that describe value, exchange, customer, market or economic meaning. | `serves`, `sells_to`, `creates_value_for` | Source and target should be commercial actors, offerings, markets or value objects. | Keep commercially meaningful and independent of sales system implementation. |
| Knowledge | Links that describe evidence, definition, derivation or traceability. | `evidenced_by`, `derived_from`, `supports` | Source is concept, claim or standard; target is evidence or knowledge artefact. | Preserve confidence and limitation metadata. |
| Temporal | Links that describe sequence, validity, replacement or time dependency. | `precedes`, `supersedes`, `effective_during` | Source and target may be events, states, versions or concepts. | Use explicit dates or validity intervals where known. |
| Measurement | Links that describe quantification, indicators or evaluation. | `measured_by`, `scores`, `indicates` | Source is measured object; target is measure, metric or evidence. | Define scale, unit and interpretation when quantitative. |
