# CIOS-ENG-005 Ontology Engineering Standard

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-ENG-005 |
| Title | Ontology Engineering Standard |
| Version | 1.0.0 |
| Status | Engineering Baseline |
| Owner | CIOS Engineering Governance |
| Last Reviewed | 2026-06-29 |
| Scope | Engineering representation, implementation, validation and traceability rules for CIOS ontology concepts |

## Executive Summary

This standard defines how CIOS ontology concepts shall be represented, implemented, validated and governed across CBOK, machine-readable ontology files, SDK models, knowledge graph artefacts and applications. CBOK is the authoritative source of ontology meaning. The SDK is the reference implementation of approved ontology primitives and mappings. Engineering must not introduce new commercial concepts without a corresponding CBOK ontology definition.

## Purpose

The purpose of CIOS-ENG-005 is to establish a durable engineering foundation for ontology work. It ensures that ontology concepts are scientifically governed, consistently named, traceable across implementations and safe for downstream application use.

## Scope

This standard applies to:

- human-readable CBOK ontology standards and concept specifications;
- machine-readable ontology files, including YAML representations;
- SDK ontology models and adapters;
- knowledge graph node and edge mappings;
- application artefacts that consume ontology concepts.

This standard does not define runtime behaviour, product workflows or complete domain ontologies. Domain meaning is defined in CBOK ontology standards.

## Normative References

- [CBOK Authoring System](../CBOK/README.md)
- [CBOK Authoring Guide](../CBOK/AUTHORING_GUIDE.md)
- [CBOK Identifier Standard](../CBOK/IDENTIFIER_STANDARD.md)
- [CBOK-SCI-001 Scientific Knowledge Framework](../CBOK/Science/CBOK-SCI-001_Scientific_Knowledge_Framework_v1.0.0.md)
- [Science Governance](../Science/SCIENCE_GOVERNANCE.md)
- [CIOS-ENG-001 SDK Specification](../CIOS_ENG_001_SDK_Specification_v1.0.0.md)
- [CIOS-ENG-002 Platform Architecture and Dependency Model](../CIOS_ENG_002_Platform_Architecture_and_Dependency_Model_v1.0.0.md)
- [CIOS-ENG-004 Application Composition Standard](CIOS_ENG_004_Application_Composition_Standard_v0.1.0.md)
- [CIOS Document Standards](../DOCUMENT_STANDARDS.md)
- [CIOS Traceability Model](../TRACEABILITY.md)

## Relationship to CBOK

CBOK is the authoritative source of ontology meaning. Engineering artefacts shall preserve CBOK definitions, constraints, confidence ratings and review status. Engineering may create implementation structures only when they map to governed CBOK concepts or explicitly marked technical primitives.

Engineering must not introduce new commercial concepts without a corresponding CBOK ontology definition. If a required concept is missing, engineering shall request or draft a CBOK concept definition before implementing the concept as a domain primitive.

## Ontology Engineering Principles

1. Meaning precedes implementation.
2. Human-readable CBOK standards and machine-readable ontology files shall remain aligned.
3. Identifiers shall be stable, governed and traceable.
4. Relationships shall use governed relationship identifiers.
5. SDK models shall implement approved concepts rather than redefining them.
6. Knowledge graph mappings shall preserve concept and relationship identifiers.
7. Applications shall consume ontology primitives compositionally and must not redefine platform ontology meaning.
8. Scientific confidence and operational confidence shall be visible where ontology meaning affects reasoning or decisions.

## Concept Identifier Conventions

Concept identifiers shall use stable, lowercase, dot-separated identifiers scoped by ontology domain:

```text
cios.ontology.<domain>.<concept_name>
```

Example: `cios.ontology.enterprise.business_unit`.

Concept identifiers shall be unique, permanent once published and recorded in the relevant CBOK concept catalogue. Retired identifiers must not be reused. Candidate identifiers may be used in draft catalogues when clearly marked as candidate.

## Concept Naming Conventions

Canonical concept names shall use singular title case, such as `Business Unit`. Names should be precise, commercially meaningful and consistent with CBOK definitions. Synonyms may be recorded, but SDK and graph mappings shall use the canonical name and governed identifier.

## Common Concept Template

Every governed concept specification shall include:

| Section | Requirement |
|---|---|
| Metadata | Identifier, canonical name, version, status, owner and review date. |
| Definition | Concise meaning controlled by CBOK. |
| Classification | Domain, object family, parent class and child classes. |
| Attributes | Governed descriptive fields and value expectations. |
| Relationships | Governed relationship identifiers and allowed target concepts. |
| States | Permitted lifecycle or condition states, where applicable. |
| Behaviours | Permitted domain behaviours, not runtime implementation logic. |
| Constraints | Invariants, multiplicities and validation expectations. |
| Evidence | Evidence types and confidence ratings supporting the definition. |
| Mapping | SDK, YAML and knowledge graph mapping details. |
| History | Version history and review history. |

## Relationship Modelling Rules

Graph relationships shall use governed relationship identifiers. Each relationship shall define an identifier, name, definition, allowed source types, allowed target types, direction, multiplicity and example. Relationship identifiers should use lowercase snake case verbs or verb phrases, such as `belongs_to`.

Relationships must not be created ad hoc in application code. When a new relationship is needed, the relationship shall be added to the relevant CBOK relationship catalogue and mapped into machine-readable ontology files before SDK or graph use.

## Attribute Modelling Rules

Attributes shall describe intrinsic or governed properties of a concept. Attribute definitions should specify name, data type, cardinality, required status, allowed values when controlled, provenance expectations and sensitivity classification when relevant. Attributes must not encode relationships that should be represented as graph edges.

## State Modelling Rules

States shall represent governed lifecycle, condition or maturity positions for a concept. State sets shall define allowed values, transition rules and evidence required for transitions. Runtime process status may map to ontology states, but applications must not create domain states that conflict with CBOK definitions.

## Behaviour Modelling Rules

Behaviours shall describe domain-relevant actions or capabilities associated with a concept, such as an enterprise capability enabling a process. Behaviour definitions shall remain conceptual unless an engineering standard explicitly maps them to SDK methods or application workflows. Behaviour modelling must not introduce hidden automation.

## Constraint Modelling Rules

Constraints shall define invariants, multiplicity rules, compatibility rules, controlled vocabularies and validation gates. Constraint violations should fail validation before machine-readable ontology files are promoted for SDK or graph consumption.

## YAML Representation Rules

Machine-readable ontology files should use YAML when a readable interchange format is needed. YAML records shall include, at minimum:

```yaml
identifier: cios.ontology.enterprise.business_unit
canonical_name: Business Unit
version: 0.1.0
status: candidate
cbok_reference: CIOS-CBOK-STD-001A
object_family: Enterprise Structure
attributes: []
relationships: []
states: []
constraints: []
```

YAML files shall preserve CBOK identifiers and shall not contain concepts, relationships or constraints absent from the governing CBOK standard. YAML schema changes require engineering review.

## SDK Mapping Rules

The SDK is the reference implementation. SDK ontology models shall map to governed CBOK concepts and shall retain concept identifiers. SDK packages must not redefine commercial meaning in docstrings, constants or validation logic when that meaning belongs in CBOK. Technical helper types may exist when clearly documented as implementation primitives rather than commercial ontology concepts.

## Knowledge Graph Mapping Rules

Knowledge graph nodes shall carry governed concept identifiers. Knowledge graph edges shall carry governed relationship identifiers. Graph mappings should include source evidence identifiers, transformation provenance and confidence metadata where available. A graph edge must not use an ungoverned relationship label.

## Validation and Conformance Rules

An ontology artefact conforms to this standard when it:

1. references a governed CBOK ontology definition;
2. uses stable concept and relationship identifiers;
3. keeps human-readable and machine-readable definitions aligned;
4. maps SDK models to CBOK concepts without redefining meaning;
5. maps graph nodes and edges using governed identifiers;
6. preserves traceability to evidence and downstream artefacts;
7. records version, status, owner and review history.

## Versioning and Deprecation Rules

Ontology versions shall follow semantic versioning. Major versions change meaning or compatibility. Minor versions add concepts, relationships or constraints without breaking existing meaning. Patch versions clarify wording or correct non-material errors. Deprecated concepts shall retain identifiers and include replacement guidance when available.

## Governance and Review Process

Ontology changes shall be reviewed by CBOK Knowledge Governance for meaning and by Engineering Governance for implementation impact. Reviews should confirm evidence sufficiency, identifier stability, SDK mapping, graph mapping, application impact and migration requirements.

## Engineering Traceability Requirements

Ontology implementation shall preserve the following chain:

```text
CBOK ontology concept
→ Machine-readable ontology
→ SDK model
→ Knowledge graph node / edge
→ Application artefact
→ Evidence / reasoning output
```

Each downstream artefact should retain the upstream identifier needed to reconstruct meaning, provenance and review status.

## Appendices

### Appendix A: Minimum Concept Record

A minimum concept record contains identifier, canonical name, definition, domain, object family, status, CBOK reference, relationship references and mapping notes.

### Appendix B: Prohibited Practices

- Introducing commercial concepts only in SDK code.
- Creating graph edge labels without governed relationship identifiers.
- Allowing machine-readable ontology files to drift from CBOK standards.
- Treating application-specific labels as authoritative ontology definitions.
