# Architecture Compliance Statement — Flora Sprint 1 Package

**Decision requested:** Accept  
**Date:** 2026-07-09  
**Owner:** Rob / CIOS

## Mission

Enable Flora to receive an accepted Commercial Digital Twin Blueprint as governed candidate intelligence, promote eligible objects into durable memory and make the enterprise understandable through an evidence-linked Enterprise Canvas.

## Scope

This documentation package governs:

- Blueprint package receipt and import;
- package-to-canonical acceptance boundary;
- runtime import objects and states;
- package exchange profile;
- analytical projections;
- Enterprise Canvas and drill-down;
- experience, accessibility and lineage;
- Sprint 1 Codex delivery.

It does not change EI-001, EI-002 or EI-012 canonical semantics.

## Architecture references

- CIOS-AI.md
- CIOS Reference Architecture v1.0
- CIOS Design Doctrine
- Architecture Principles
- CIOS Chief Architect Handbook
- FP-003 Flora Intelligence Architecture
- EI-001 Enterprise Model Specification
- EI-002 Enterprise Knowledge Graph
- EI-012 Enterprise Observation Model
- ADR-001, ADR-002, ADR-004, ADR-005 and ADR-010

## Accepted decisions added

- ADR-012 — Governed Blueprint Package Import and Canonical Acceptance Boundary
- ADR-013 — Enterprise Canvas as Primary Living Twin Navigation

## Principles implemented

- Evidence proves change.
- Observations remember change.
- Enterprise Models accumulate change.
- Reports and product surfaces are views.
- Package acceptance does not bypass object governance.
- Human knowledge remains labelled.
- Unknowns and Contradictions remain visible.
- Strong judgements retain inspectable lineage.
- Model before view.
- Simple surface, strong model, progressive disclosure.
- Learning actions create governed candidate updates.
- Architecture before implementation.

## Principles deferred

- universal package exchange;
- canonical Pain Point object;
- automated promotion;
- all Canvas lenses;
- nested CSM Twin;
- Provider Fit and pursuit logic;
- automated outcome learning.

## Objects affected

### New runtime objects

- Package Registry entry;
- Import Run;
- Candidate Import Record;
- Import Mapping;
- validation result;
- Import Ledger entry;
- Analytical Projection registration.

These are runtime and view-layer objects owned by the new runtime specification. They do not alter EI object meaning.

### Existing objects inspected or updated

- Source;
- Evidence;
- Observation;
- Enterprise Model;
- entity;
- relationship;
- Unknown;
- Contradiction;
- human-supplied knowledge;
- publication reference.

Updates must use owning services and contracts.

## Terminology compliance

New terms are added to the Glossary with named owners. Intelligence Tile, Enterprise Canvas and Analytical Projection are explicitly views, not canonical EI objects.

## Evidence and lineage

The package preserves:

- original archive and checksums;
- original external IDs;
- source file and location;
- candidate-to-canonical mapping;
- canonical mutation ledger;
- view-to-Observation-to-Evidence-to-Source navigation.

## Unknowns and Contradictions

Unmapped fields, unsupported classes, conflicting IDs, incomplete lineage and package disagreements remain visible through validation, quarantine or Contradiction state.

## Human-supplied knowledge

Human knowledge must retain contributor, date, scope, effect and validation need. User feedback creates candidate knowledge rather than Evidence or automatic canonical state.

## Durable memory

Eligible imported objects may update the Enterprise Model only after explicit object-level acceptance. Analytical pain and publication content remain versioned views.

## Commercial value

The user can understand a complex enterprise without reading the entire Blueprint, navigate to its principal pains and current responses and use the intelligence to improve executive validation and later bid work. Commercial need remains separate from Provider Fit and Pursue.

## Validation

Documentation validation:

- required documents created;
- internal links checked;
- ADR, Glossary, Document Map and Reference Architecture reconciled;
- terminology reviewed;
- Sprint plan includes acceptance, validation, commit, PR and completion-report requirements.

Runtime validation is specified but not yet executed.

## Architecture debt

- package profile is proven only against the MOD package;
- Pain Point remains a projection;
- tile mapping rules need code-binding validation;
- access-control detail for procurement-controlled nested Twins remains future work;
- full export and round-trip exchange remain future work.

## Decision

Accept the package as the architecture baseline for the read-only code-binding audit and subsequent bounded Flora Sprint 1 Codex PRs.
