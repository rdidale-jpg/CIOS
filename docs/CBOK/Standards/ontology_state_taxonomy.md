# Ontology State Taxonomy

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-000-STATE |
| Title | Ontology State Taxonomy |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Purpose

This taxonomy defines how ontology states shall be modelled for concepts, relationships and supporting artefacts.

## Lifecycle States

Lifecycle states describe progression from proposal to retirement. Recommended values are `candidate`, `review`, `approved`, `deprecated` and `retired`.

## Maturity States

Maturity states describe development depth or readiness. Domain standards may define values such as `emerging`, `defined`, `validated` and `baseline` when evidence supports the distinction.

## Confidence States

Confidence states express scientific or operational confidence. They shall align with CBOK confidence standards when used for knowledge claims or implementation readiness.

## Governance States

Governance states describe approval and control status, such as `draft`, `under_review`, `approved_by_governance`, `exception_granted` or `change_requested`.

## Operational States

Operational states describe condition in use, such as `active`, `inactive`, `suspended` or `observed`. Operational states shall not conflict with lifecycle states.

## Relationship States

Relationship states describe whether a governed relationship instance or relationship type is proposed, active, deprecated, invalidated or superseded.

## Transition Rules

Each state set shall define allowed transitions, required approver, evidence requirement and downstream impact. State transitions that affect SDK, graph or application artefacts shall identify migration or compatibility notes.

## State Evidence Requirements

State changes shall cite evidence or governance decisions. Approval requires sufficient evidence for intended use. Deprecation and retirement shall cite replacement guidance or rationale where available.
