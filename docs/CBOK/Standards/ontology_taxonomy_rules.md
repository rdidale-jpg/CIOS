# Ontology Taxonomy Rules

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-000-TAX |
| Title | Ontology Taxonomy Rules |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Purpose

These rules define how CBOK ontology taxonomies shall be constructed across all commercial domains.

## Parent-Child Modelling

Parent-child links shall represent `is a kind of` meaning. A child concept shall inherit the essential meaning of its parent and add narrower commercial meaning.

## Inheritance

Inherited attributes, relationships, constraints and states should be explicit in concept catalogues when they affect validation, SDK mapping or graph mapping. Inheritance must not be used to hide domain assumptions.

## Primary Parent Rule

Each concept shall have one primary parent unless a documented governance decision approves an exception. The primary parent controls taxonomy placement, identifier path and inherited meaning.

## Secondary Relationship Rule

Additional semantic links shall be modelled as governed relationships rather than secondary parents. Examples include `depends_on`, `owned_by`, `governed_by`, `measured_by` and `part_of`.

## Concept Granularity

Concepts shall be granular enough to carry distinct meaning, relationships, states or evidence. Authors should not create separate concepts for mere labels, UI categories, implementation fields or local process variants.

## Domain Boundary Rules

A concept belongs in the domain that owns its canonical definition. Cross-domain use shall link to the owning domain concept instead of duplicating it. Boundary disputes shall be resolved by CIOS Knowledge Governance.

## Naming Conventions

Canonical concept names shall use singular title case. Identifiers should use lowercase dot-delimited namespaces or approved catalogue conventions. Names shall be commercially meaningful, implementation independent and stable.

## Deprecation Rules

Deprecated concepts shall retain identifiers, status, replacement guidance and migration notes. Retired identifiers must not be reused. Deprecation shall identify affected YAML, SDK, graph and application mappings.

## Cross-Domain Linking

Cross-domain links shall use governed relationships and preserve both source and target identifiers. A domain standard may reference another domain concept but must not redefine that concept.

## Concept Maturity

Concept maturity shall be recorded as candidate, review, approved, deprecated or retired. Candidate concepts may guide exploration but shall not become production SDK or graph semantics without approval.
