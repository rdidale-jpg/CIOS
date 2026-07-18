---
architecture_metadata:
  identity:
    id: EKPP-001
    title: Enterprise Knowledge Production Protocol v1.0
    canonical_path: architecture/specifications/enterprise-knowledge/Enterprise-Knowledge-Production-Protocol-v1.0.md
    version: "1.0"
    aliases:
      - Enterprise Knowledge Production Protocol v1.0
  type:
    document_class: Specification
    architecture_domain: enterprise knowledge
    canonical_document: true
  status: Accepted
  authority:
    classification: Accepted normative protocol governing Enterprise Knowledge production; documentation-only and non-runtime
    scope: Creation, review, governance, validation, release and maintenance of Enterprise Knowledge assets
    normative: true
    registry_entry_required: true
    conflict_rule: Authority Registry wins over conflicting document metadata; Accepted ADRs, Reference Architecture, Enterprise Knowledge Architecture and Knowledge Pack Specification retain precedence where applicable
  owner:
    name: Rob / CIOS
    role: Chief Architect
  dependencies:
    requires:
      - CIOS Design Doctrine
      - Chief Architect Handbook
      - CIOS Reference Architecture v1.0
      - Enterprise Knowledge Architecture
      - Knowledge Pack Specification v1.0
      - Accepted ADRs
    related:
      - FP-010 — Knowledge Pack Architecture
      - FP-011 — Knowledge Exchange Architecture
      - EI-013 — Knowledge Asset Exchange Model
      - EI-001 — Enterprise Model Specification
      - EI-012 — Enterprise Observation Model
    supersedes: []
    superseded_by: []
    validation_triggers:
      - Chief Architect review before changing production doctrine or authority precedence
      - Link, metadata and registry consistency checks before release
  profiles:
    membership:
      - architecture-authority
    exclusions:
      - researcher-pack
      - reviewer-pack
      - assurance-pack
  lifecycle:
    created: 2026-07-18
    last_updated: 2026-07-18
    review_due: null
    promotion_state: accepted
    change_control: Accepted governance change recorded in the Authority Registry
---

# Enterprise Knowledge Production Protocol v1.0

## 1. Mission

The Enterprise Knowledge Production Protocol defines the standard
operating model for creating, reviewing, governing and publishing
Enterprise Knowledge within CIOS.

Its purpose is to ensure every knowledge asset is:

-   evidence-backed
-   architecturally consistent
-   explainable
-   reusable
-   governed
-   traceable from source evidence through to enterprise reasoning

The protocol is independent of any specific industry.

------------------------------------------------------------------------

## 2. Scope

This protocol governs the production of:

-   Research assets
-   Industry Foundations
-   Enterprise Twins
-   Industry Twins
-   Infrastructure Twins
-   Mechanism Catalogues
-   Observation Registers
-   Reinvention Hypotheses
-   Enterprise Models
-   Reference Models
-   Architecture documents
-   Methodologies
-   Specifications

It governs **knowledge production**, not software development.

------------------------------------------------------------------------

## 3. Guiding Doctrine

> Evidence proves change.\
> Observations remember change.\
> Enterprise Models accumulate change.\
> Reports are views.

These principles are normative.

All production activities shall preserve them.

------------------------------------------------------------------------

## 4. Production Principles

Every knowledge asset shall be:

-   Evidence-backed
-   Explainable
-   Architecturally consistent
-   Independently understandable
-   Version controlled
-   Governed
-   Cross-referenced
-   Inspectable

Unknowns are preserved.

Contradictions are preserved.

Confidence is explicit.

Lineage is never removed.

------------------------------------------------------------------------

## 5. Production Lifecycle

``` text
Research
        â
Evidence Collection
        â
Knowledge Synthesis
        â
Architectural Review
        â
Knowledge Acceptance
        â
Repository Governance
        â
Validation
        â
Knowledge Pack Release
        â
Publication
        â
Continuous Maintenance
```

Each stage has a distinct owner and a defined completion criterion.

------------------------------------------------------------------------

## 6. Production Roles

### Researcher

Responsible for discovering and synthesising Enterprise Knowledge.

Produces:

-   Foundations
-   Twins
-   Mechanism Catalogues
-   Observation Registers
-   Reinvention Hypotheses

Does not govern repositories or define architecture.

### Chief Architect

Owns Enterprise Knowledge quality.

Responsibilities:

-   Architectural review
-   Methodological consistency
-   Challenge and critique
-   Acceptance
-   Preservation of doctrine
-   Approval for governance

Determines whether knowledge becomes authoritative.

### Codex

Owns repository governance.

Responsibilities:

-   Metadata
-   Manifests
-   Stable identifiers
-   Relationship integrity
-   Validation
-   Release packaging
-   Pull requests
-   Repository maintenance

Does not create Enterprise Knowledge.

### Repository

The authoritative system of record.

### Knowledge Packs

Generated releases for reasoning tasks.

Knowledge Packs are derived artefacts, not authoritative sources.

### Runtime Intelligence (Flora)

Consumes governed Enterprise Knowledge and reasons over observations,
mechanisms, enterprise models and reinvention hypotheses.

------------------------------------------------------------------------

## 7. Standard Knowledge Asset Lifecycle

``` text
Draft
      â
Reviewed
      â
Accepted
      â
Governed
      â
Validated
      â
Released
      â
Referenced
      â
Maintained
      â
Superseded
```

Only accepted assets may enter governance.

------------------------------------------------------------------------

## 8. Knowledge Production Sequence

1.  Industry Foundation
2.  Enterprise Twins
3.  Infrastructure Twins (where applicable)
4.  Industry Twin
5.  Mechanism Catalogue
6.  Observation Register
7.  Reinvention Hypotheses

------------------------------------------------------------------------

## 9. Quality Gates

Every asset shall pass:

-   Evidence Gate
-   Architectural Gate
-   Lineage Gate
-   Observation Gate
-   Mechanism Gate
-   Knowledge Gate
-   Governance Gate
-   Release Gate

------------------------------------------------------------------------

## 10. Definition of Done

A knowledge asset is complete only when it is:

-   Reviewed
-   Accepted
-   Governed
-   Validated
-   Cross-referenced
-   Versioned
-   Packaged
-   Published

Completion is determined by governance status, not document length.

------------------------------------------------------------------------

## 11. Governance Boundaries

This protocol complements, but does not replace:

-   CIOS Design Doctrine
-   Chief Architect Handbook
-   Reference Architecture
-   Enterprise Knowledge Architecture
-   Knowledge Pack Specification
-   Accepted ADRs

Precedence order:

1.  Accepted ADRs
2.  Reference Architecture
3.  Enterprise Knowledge Architecture
4.  Enterprise Knowledge Production Protocol

------------------------------------------------------------------------

## 12. Success Measures

The protocol is successful when it enables:

-   Repeatable knowledge production
-   Consistent quality across industries
-   Complete evidence lineage
-   Reusable Enterprise Knowledge
-   Rapid creation of Knowledge Packs
-   Effective reasoning by future runtimes

Success is measured by the quality and reusability of Enterprise
Knowledge, not by the number of documents produced.

------------------------------------------------------------------------

## Appendix A -- Production Anti-Patterns

Avoid:

-   Reports replacing models
-   Recommendations without evidence lineage
-   Mechanisms expressed as observations
-   Multi-fact observations
-   Governance before architectural acceptance
-   Knowledge Packs treated as authoritative
-   Duplicate concepts with different names
-   Silent removal of unknowns or contradictions
