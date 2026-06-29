# Ontology Behaviour Taxonomy

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-000-BEH |
| Title | Ontology Behaviour Taxonomy |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Purpose

This taxonomy defines how CBOK ontologies describe conceptual behaviour while avoiding runtime implementation logic.

## Behaviour Definition

A behaviour is a conceptual action, capability or response associated with a primitive. Behaviour definitions shall explain commercial meaning, not executable steps.

## Trigger

A trigger identifies the condition, event or relationship that initiates the behaviour conceptually. Triggers should be named and evidenced when they affect state transitions.

## Actor

An actor is the entity or role that performs, initiates or is accountable for the behaviour. Actors shall map to governed entities or roles.

## Input

Inputs are concepts, evidence, measures, events or states required by the behaviour. Inputs should be expressed as ontology primitives, not implementation parameters.

## Output

Outputs are conceptual results such as a changed state, created evidence, new relationship or decision outcome. Outputs shall identify affected primitives where possible.

## Side Effect

Side effects are secondary conceptual consequences. They should be documented when they affect governance, traceability, risk or downstream artefacts.

## Evidence

Behaviour definitions shall cite evidence or standards supporting why the behaviour belongs to the concept. Evidence is especially important when behaviour informs automation or recommendations.

## Related Relationships

Behaviours should identify relationships they create, require, modify or explain, such as `approves`, `depends_on`, `measured_by` or `governs`.

## Engineering Mapping

Engineering mappings may link behaviours to SDK methods, services, workflows or application actions. Such mappings shall be governed by CIOS-ENG-005 and must not change CBOK behaviour meaning.

## Distinction Between Behaviour and Runtime Logic

Behaviour belongs to concepts; runtime logic belongs to engineering. Ontology behaviour shall describe what a commercial action means. It must not define executable algorithms, orchestration, error handling, API calls or product-specific workflow steps.
