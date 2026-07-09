# CIOS Architecture Decision Records

**Status:** Living index  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-09

## Purpose

Architecture Decision Records capture why major CIOS architecture decisions were made. They preserve context, trade-offs, consequences and runtime implications so important choices remain inspectable after implementation moves on.

Use ADRs when a decision materially affects CIOS architecture, terminology, runtime behaviour, Evidence lineage, Enterprise Intelligence, Commercial Digital Twins, recommendations, governance or cross-cutting user experience.

## Accepted ADRs

- [ADR-001 — Observations as Atomic Intelligence Unit](ADR-001-Observations-as-Atomic-Intelligence-Unit.md)
- [ADR-002 — Enterprise Model as Durable Memory](ADR-002-Enterprise-Model-as-Durable-Memory.md)
- [ADR-003 — CIRM and EI Separation](ADR-003-CIRM-and-EI-Separation.md)
- [ADR-004 — Human-Supplied Knowledge Must Be Labelled](ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md)
- [ADR-005 — No Recommendation Without Inspectable Lineage](ADR-005-No-Recommendation-Without-Inspectable-Lineage.md)
- [ADR-010 — Structured-Source-First, AI-Assisted Evidence Acquisition](ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md)
- [ADR-012 — Governed Blueprint Package Import and Canonical Acceptance Boundary](ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md)
- [ADR-013 — Enterprise Canvas as Primary Living Twin Navigation](ADR-013-Enterprise-Canvas-as-Primary-Living-Twin-Navigation.md)

## Proposed ADRs

- [ADR-006 — Signal Architecture](ADR-006-Signal-Architecture.md)
- [ADR-007 — Transformation Thesis](ADR-007-Transformation-Thesis.md)
- [ADR-008 — Recommendation Engine](ADR-008-Recommendation-Engine.md)

Proposed ADRs are not authoritative until accepted.

## Numbering

ADR numbers preserve project history and may not be contiguous. Do not renumber existing decisions to close gaps.

## Required ADR content

A good ADR includes:

- status;
- context;
- decision;
- alternatives;
- consequences;
- affected documents;
- runtime implications;
- validation;
- architecture debt;
- review and supersession conditions.

## Authority

Accepted ADRs override derived guidance where a conflict exists. They do not silently replace the owning Founding Paper or Enterprise Intelligence specification. Where a decision changes an owned concept, update or reconcile the owning document.

## Template

Use `ADR-Template.md` for new decisions.
