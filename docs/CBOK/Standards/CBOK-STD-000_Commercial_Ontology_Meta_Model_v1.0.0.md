# CBOK-STD-000 Commercial Ontology Meta-Model

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-000 |
| Title | Commercial Ontology Meta-Model |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |
| Scope | Primitive ontology grammar, taxonomy rules and machine-readable representation requirements for all CBOK ontology domains |

## Executive Summary

CBOK-STD-000 defines the grammar for all CBOK ontology standards. It establishes the primitive building blocks, design principles, taxonomy rules, relationship categories, attribute categories, state categories, behaviour rules, constraints, evidence requirements and conformance obligations used by future Commercial Body of Knowledge ontology domains.

Domain ontologies must conform to this meta-model before they are represented in YAML, SDK models, knowledge graph structures or application artefacts. Enterprise, Human, Market, Capability, Decision, Knowledge and Change domain concepts must be built from the primitive types defined here.

Concepts before a meta-model create semantic debt: inconsistent identifiers, duplicated meanings, hidden implementation assumptions and graph structures that cannot be governed. This standard prevents that debt by separating commercial meaning from implementation while preserving traceability into engineering.

## Purpose

The purpose of this standard is to provide a stable, technology-independent ontology meta-model for CBOK commercial concepts. It shall be used to author, review, approve and map all CBOK ontology standards and supporting machine-readable ontology artefacts.

## Scope

This standard applies to:

- CBOK domain ontology standards and concept catalogues.
- Machine-readable ontology files maintained under CBOK governance.
- Relationship, attribute, state, behaviour and constraint taxonomies.
- SDK and knowledge graph mappings that consume governed ontology meaning.
- Traceability from evidence through ontology definitions to implementation artefacts.

This standard does not define domain-specific concepts in detail, add runtime behaviour, mandate a programming language or prescribe a storage technology.

## Normative References

- [CBOK Authoring System](../README.md)
- [CBOK Authoring Guide](../AUTHORING_GUIDE.md)
- [CBOK Identifier Standard](../IDENTIFIER_STANDARD.md)
- [CBOK-SCI-001 Scientific Knowledge Framework](../Science/CBOK-SCI-001_Scientific_Knowledge_Framework_v1.0.0.md)
- [CIOS-ENG-005 Ontology Engineering Standard](../../Engineering/CIOS-ENG-005_Ontology_Engineering_Standard_v1.0.0.md)
- [CIOS Master Document Index](../../MASTER_INDEX.md)
- [CIOS Document Standards](../../DOCUMENT_STANDARDS.md)
- [CIOS Traceability Model](../../TRACEABILITY.md)

## Relationship to CBOK-SCI-001

CBOK-SCI-001 governs how CBOK knowledge is classified, evidenced, promoted and consumed by engineering. CBOK-STD-000 applies those rules to ontology work by treating concepts, relationships, attributes, states, behaviours and constraints as governed knowledge artefacts. Ontology definitions shall carry evidence, confidence, lifecycle status and review history proportionate to downstream risk.

## Relationship to CIOS-ENG-005

CIOS-ENG-005 governs engineering representation of ontology artefacts. CBOK-STD-000 governs commercial meaning before engineering representation. The meta-model is technology-independent, while the SDK and knowledge graph are reference implementations. SDK classes, graph nodes and graph edges shall preserve CBOK identifiers and must not redefine commercial meaning.

## Why the Meta-Model Exists

The meta-model exists to:

1. Define common ontology grammar before domain expansion.
2. Prevent semantic debt caused by ad hoc concept creation.
3. Keep human-readable and machine-readable ontology artefacts aligned.
4. Ensure all domains use consistent primitives, identifiers and evidence expectations.
5. Support traceable mappings into SDK, knowledge graph and application artefacts.
6. Allow future domains to evolve without fragmenting commercial meaning.

## Ontology Primitive Types

| Primitive | Definition | Required Use |
|---|---|---|
| Entity | A commercially meaningful object, actor, structure or thing that can be identified. | Used for domain concepts such as Enterprise, Capability, Person or Market Segment. |
| Relationship | A governed connection between ontology primitives. | Used for graph edges and semantic links. |
| Attribute | A governed property of a primitive. | Used for intrinsic data that is not better modelled as a relationship. |
| Behaviour | A conceptual action, capability or response associated with a primitive. | Used to describe domain behaviour without implementing runtime logic. |
| State | A governed condition, lifecycle stage or status of a primitive or relationship. | Used for lifecycle, maturity, confidence, governance and operational states. |
| Constraint | A rule limiting valid ontology structures, values or transitions. | Used for invariants, multiplicity and validation gates. |
| Event | A significant occurrence that changes state, evidence or relationships. | Used for changes, decisions, approvals, incidents or observations. |
| Evidence | A traceable support, source, observation or review record. | Used to justify definitions, states and mappings. |
| Measure | A quantified observation, score or indicator. | Used for performance, confidence, value, risk and maturity measurement. |
| Role | A responsibility or participation pattern held by an entity in a context. | Used for actors, owners, reviewers, decision makers and participants. |

## Ontology Design Principles

Ontology authors shall apply [Ontology Design Principles](ontology_design_principles.md). In particular, each concept shall have one canonical definition, stable identifiers, implementation-independent meaning and traceability to evidence, standards and implementation.

## Taxonomy Rules

Ontology authors shall apply [Ontology Taxonomy Rules](ontology_taxonomy_rules.md). Concepts shall normally have one primary parent. Secondary semantics shall be modelled with governed relationships rather than multiple inheritance unless explicitly justified.

## Relationship Taxonomy

Relationships shall use the governed categories in [Ontology Relationship Taxonomy](ontology_relationship_taxonomy.md): Structural, Ownership, Dependency, Governance, Behavioural, Commercial, Knowledge, Temporal and Measurement. Relationship definitions shall specify direction, allowed sources, allowed targets, multiplicity and evidence expectations.

## Attribute Taxonomy

Attributes shall use the categories in [Ontology Attribute Taxonomy](ontology_attribute_taxonomy.md): Identity, Descriptive, Classification, Quantitative, Temporal, Evidence, Confidence, Governance and Implementation attributes. Attributes must not encode relationships that should be graph edges.

## State Taxonomy

States shall use the modelling rules in [Ontology State Taxonomy](ontology_state_taxonomy.md). State sets shall define allowed values, transition rules, transition evidence and review expectations.

## Behaviour Taxonomy

Behaviours shall use the modelling rules in [Ontology Behaviour Taxonomy](ontology_behaviour_taxonomy.md). Behaviour belongs to concepts; runtime logic belongs to engineering. Behaviour entries may be mapped to SDK methods or workflows only through engineering standards.

## Constraint Taxonomy

Constraints shall be classified as:

| Type | Definition | Example |
|---|---|---|
| Identity constraint | Rules for stable identifiers and uniqueness. | A concept identifier shall not be reused after retirement. |
| Cardinality constraint | Minimum or maximum occurrence rules. | A concept shall have exactly one canonical name. |
| Type constraint | Allowed primitive, source, target or value class. | `owns` shall connect an owning entity to an owned entity or asset. |
| Value constraint | Controlled vocabulary, range or data type. | Confidence shall use governed confidence values. |
| Transition constraint | Allowed state changes and gates. | Candidate concepts may become approved only after review. |
| Evidence constraint | Evidence required before approval or mapping. | Approved concepts shall cite supporting evidence or review decisions. |
| Governance constraint | Review, ownership or approval requirements. | New commercial concepts require CBOK approval before engineering implementation. |
| Mapping constraint | Rules for SDK and graph representation. | Graph edges shall use governed relationship identifiers. |

## Evidence Requirements

Every governed ontology artefact shall identify evidence appropriate to its maturity and impact. Evidence may include CBOK standards, reviewed operational examples, analysis, validation records, governance decisions or implementation traceability. Evidence records should identify source, date, owner, confidence and limitations.

## Machine-Readable Representation Rules

Machine-readable ontology files shall:

- Preserve CBOK identifiers, canonical names and versions.
- Represent primitives using the structure defined in [commercial_ontology_meta_model.yaml](commercial_ontology_meta_model.yaml).
- Keep definitions aligned with the human-readable standard.
- Distinguish attributes from relationships.
- Include evidence, status, owner and review metadata.
- Avoid implementation-only fields unless clearly marked as implementation mapping metadata.

## SDK Mapping Implications

SDK models shall consume CBOK ontology meaning rather than define it. SDK packages may implement validation, serialization and helper functions, but they must not introduce new commercial concepts, relationship labels, state values or behavioural meaning without CBOK approval.

## Knowledge Graph Mapping Implications

Knowledge graph nodes shall map to governed entities or other approved primitives. Knowledge graph edges shall map to governed relationships. Graph records should carry source evidence, transformation provenance, confidence metadata and CBOK identifiers sufficient to reconstruct ontology meaning.

## Conformance Requirements

An ontology artefact conforms to CBOK-STD-000 when it:

1. Uses the primitive types defined in this standard.
2. Applies the design principles and taxonomy rules referenced by this standard.
3. Maintains stable identifiers and one canonical definition per concept.
4. Separates commercial meaning from SDK, graph and application implementation.
5. Provides evidence, status, owner, version and review history.
6. Maps machine-readable records to human-readable definitions.
7. Uses governed relationships, attributes, states, behaviours and constraints.
8. Preserves traceability from evidence to application artefacts.

## Governance and Review Process

CIOS Knowledge Governance owns this standard. Material changes shall be reviewed for semantic impact, domain compatibility, evidence sufficiency and downstream engineering impact. Engineering Governance should review changes affecting SDK mapping, graph mapping or validation rules. Approved changes shall update the Master Index and traceability records.

## Future Extensions

Future extensions may define formal schemas, validation profiles, domain-specific primitive specialisations, migration playbooks, graph query patterns, ontology quality metrics and automated conformance checks.

## Version History

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0.0 | 2026-06-29 | Initial Commercial Ontology Meta-Model baseline. | CIOS Knowledge Governance |

## Review History

| Date | Reviewer | Role | Decision | Notes |
|---|---|---|---|---|
| 2026-06-29 | CIOS Knowledge Governance | Governance Reviewer | Approved | Establishes Newton Sprint 2A ontology grammar. |

## Appendices

### Appendix A: Domain Application

Enterprise, Human, Market, Capability, Decision, Knowledge and Change domains shall build concepts from these primitives. Domain standards may specialise primitives but must not replace or contradict them.

### Appendix B: Traceability Chain

```text
CBOK ontology meta-model
→ Domain ontology standard
→ Machine-readable ontology
→ SDK model
→ Knowledge graph node / edge
→ Application artefact
→ Evidence / reasoning output
```
