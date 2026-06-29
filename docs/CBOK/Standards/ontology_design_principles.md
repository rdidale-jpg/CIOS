# Ontology Design Principles

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-000-ODP |
| Title | Ontology Design Principles |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Purpose

These principles govern how CBOK ontology concepts are defined, reviewed, represented and mapped into engineering artefacts.

| Identifier | Statement | Rationale | Implication | Example |
|---|---|---|---|---|
| ODP-001 | One canonical definition per concept. | Duplicate meanings create conflicting SDK and graph interpretations. | Synonyms may be recorded, but only one definition shall govern. | `Capability` has one CBOK definition even if teams use local synonyms. |
| ODP-002 | Stable identifiers. | Traceability fails when identifiers change with wording or file names. | Published identifiers shall not be reused or repurposed. | `cios.ontology.enterprise.capability` remains stable through wording clarifications. |
| ODP-003 | One primary parent unless explicitly justified. | Multiple inheritance obscures taxonomy meaning. | Secondary semantics should be modelled with relationships. | `Business Unit` has one primary parent and may also `reports_to` another entity. |
| ODP-004 | Relationships are first-class objects. | Relationship meaning affects reasoning and validation. | Relationships shall have identifiers, definitions, allowed endpoints and evidence. | `owns` is governed, not an ad hoc graph label. |
| ODP-005 | Definitions are implementation independent. | Commercial meaning should survive technology changes. | Definitions must not depend on SDK classes, tables, APIs or graph vendors. | `Market Segment` is defined commercially, not as a database row. |
| ODP-006 | Concepts are stable; implementations evolve. | Software changes faster than governed meaning. | SDK migrations shall preserve concept identity unless CBOK changes meaning. | A field rename does not create a new concept. |
| ODP-007 | Behaviour belongs to concepts; logic belongs to engineering. | Ontologies describe what behaviours mean; engineering decides how logic runs. | Behaviour entries shall not contain executable algorithms. | `approves` is conceptual; approval workflow code is engineering. |
| ODP-008 | Machine-readable and human-readable versions must remain aligned. | Divergence creates unreviewable semantics. | YAML changes shall be reviewed against Markdown standards. | A YAML definition update requires a matching standard update. |
| ODP-009 | New commercial concepts require CBOK approval before engineering implementation. | Engineering-first concepts create semantic debt. | SDK and graph implementations must wait for governed concept approval or explicit exception. | A new `Value Stream` model is added to CBOK before SDK implementation. |
| ODP-010 | Every concept shall be traceable to evidence, standards and implementation. | Traceability supports review, trust and change control. | Concepts shall identify upstream evidence and downstream mappings. | A graph node can be traced to its CBOK standard and evidence record. |
