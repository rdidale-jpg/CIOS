# CBOK-STD-001A Commercial Ontology Enterprise Domain Outline

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-001A |
| Title | Commercial Ontology Enterprise Domain Outline |
| Version | 0.1.0 |
| Status | Draft |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |
| Scope | Initial domain shape and authoring approach for the Enterprise Domain ontology |

## Executive Summary

This outline establishes the first scientific domain shape for the Enterprise Domain within the CIOS commercial ontology. It defines top-level object families, a meta-model and authoring expectations for future concept specifications. It does not fully define all concepts.

## Purpose

The purpose of this document is to guide consistent development of enterprise ontology concepts before they are implemented in machine-readable ontology files, SDK models, knowledge graphs or applications.

## Scope

This outline covers enterprise structure, governance, capability, resources, strategy, risk and performance. It establishes authoring approach, evidence expectations and engineering traceability. It excludes detailed concept definitions, runtime behaviours and SDK implementation.

## Relationship to CBOK-STD-000

The Enterprise Domain standard shall conform to [CBOK-STD-000 Commercial Ontology Meta-Model](CBOK-STD-000_Commercial_Ontology_Meta_Model_v1.0.0.md). Enterprise concepts, relationships, attributes, states, behaviours and constraints shall use the primitive types, taxonomy rules and machine-readable representation expectations defined by CBOK-STD-000.

## Relationship to CBOK-SCI-001

This outline applies [CBOK-SCI-001](../Science/CBOK-SCI-001_Scientific_Knowledge_Framework_v1.0.0.md) by treating ontology definitions as governed knowledge artefacts. Future concept specifications shall identify knowledge classification, evidence type, scientific confidence, operational confidence and lifecycle status.

## Relationship to CIOS-ENG-005

CIOS-ENG-005 governs engineering representation and implementation of ontology concepts. Enterprise Domain concepts shall be defined in CBOK before being represented in YAML, SDK models, knowledge graph nodes or application artefacts.

## Enterprise Domain Definition

The Enterprise Domain represents the structures, authorities, capabilities, resources, strategic intents, risks and performance measures through which an organisation coordinates commercial activity and creates value.

## Top-Level Object Families

| Object Family | Scope |
|---|---|
| Enterprise Structure | Organisational units, legal forms and structural groupings. |
| Enterprise Governance | Decision bodies, authority models, policies and control mechanisms. |
| Enterprise Capability | Capabilities, processes, services, products, platforms, technologies, data assets and suppliers. |
| Enterprise Resources | People, skills, budgets, assets, facilities, intellectual property and contracts. |
| Enterprise Strategy | Vision, mission, objectives, outcomes, initiatives, programmes, projects and portfolios. |
| Enterprise Risk | Risks, issues, dependencies, assumptions, constraints and opportunities. |
| Enterprise Performance | KPIs, benefits, costs, value, investments, returns and performance measures. |

## Enterprise Meta-Model

Enterprise concepts should be described as objects with governed attributes, relationships, states, behaviours and constraints. The domain shall support links between strategic intent, organisational ownership, capabilities, resources, risk and performance evidence.

## Concept Specification Approach

Each concept shall be specified using `enterprise_domain_concept_template.md`. Concept authors should begin with candidate catalogues, then promote concepts through CBOK review when definitions, relationships and evidence are sufficient.

## Relationship Catalogue Approach

Relationships shall be governed in `enterprise_domain_relationship_catalogue.md`. New relationships should be added only when their meaning, allowed source types, allowed target types and multiplicity are clear.

## Behaviour Catalogue Approach

Behaviour catalogues may be created in future versions to describe domain behaviours such as governs, delivers, funds, measures or transforms. Behaviour entries shall remain conceptual until mapped by an engineering standard.

## State Catalogue Approach

State catalogues may define lifecycle, maturity, risk or performance states. States shall include allowed values, transition evidence and review expectations.

## Constraint Approach

Constraints shall define invariants, multiplicities, compatibility rules and validation expectations. Constraints should be proportionate to evidence and operational impact.

## Evidence Requirements

Concept definitions should cite internal artefacts, reviewed operational examples, analysis or future validation records. Evidence shall be classified under CBOK-SCI-001. Early catalogue entries may remain candidate where evidence is incomplete.

## Engineering Traceability

Enterprise concepts shall trace through:

```text
CBOK enterprise concept
→ Machine-readable ontology
→ SDK model
→ Knowledge graph node / edge
→ Application artefact
→ Evidence / reasoning output
```

## Conformance Expectations

A future Enterprise Domain concept conforms when it uses a stable identifier, records canonical meaning, identifies object family, uses governed relationships, states confidence levels and maps to engineering artefacts according to CIOS-ENG-005.

## Future Work

- Promote candidate concepts into full concept specifications.
- Define state and behaviour catalogues.
- Create machine-readable YAML representations.
- Map approved concepts into SDK ontology models.
- Validate knowledge graph mappings and application usage.

## Review History

| Date | Reviewer | Role | Decision | Notes |
|---|---|---|---|---|
| 2026-06-29 | CIOS Knowledge Governance | Governance Reviewer | Drafted | Establishes Newton Sprint 2 Enterprise Domain outline. |
