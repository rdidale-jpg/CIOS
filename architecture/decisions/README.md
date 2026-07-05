# CIOS Architecture Decision Records

**Status:** Living index
**Owner:** Rob / CIOS
**Last updated:** 2026-07-03

## Purpose

Architecture Decision Records (ADRs) capture why major CIOS architecture decisions were made. They preserve context, trade-offs, consequences, runtime implications and governance expectations so important choices remain inspectable after implementation moves on.

The ADR set is part of the portable memory of CIOS. Future AI assistants and human contributors must treat Accepted ADRs, alongside the Reference Architecture, as source of truth for architecture direction.

## When to create an ADR

Create or update an ADR when a decision materially affects:

- CIOS architecture doctrine or terminology;
- Flora, Newton, Observatory or Publisher runtime behaviour;
- Evidence, Observation, Signal, Hypothesis, Recommendation or Source lineage;
- Enterprise Model / Commercial Digital Twin structure or persistence;
- human-supplied knowledge, trust, ethics or governance;
- recommendation thresholds or commercial conviction;
- a trade-off that future contributors should not have to rediscover.

Do not create ADRs for small implementation details unless the detail changes architecture direction or creates precedent.

## ADR status values

- **Proposed** — a draft decision or migrated placeholder that is useful to retain but not yet authoritative.
- **Accepted** — the decision is authoritative architecture guidance and must be followed by future work.
- **Superseded** — the decision has been replaced by a newer ADR; retain it for history but do not treat it as current guidance.
- **Deprecated** — the decision is intentionally retired and should not guide new work unless explicitly revived.

## Accepted ADRs

- [ADR-001 — Observations as Atomic Intelligence Unit](ADR-001-Observations-as-Atomic-Intelligence-Unit.md)
- [ADR-002 — Enterprise Model as Durable Memory](ADR-002-Enterprise-Model-as-Durable-Memory.md)
- [ADR-003 — CIRM and EI Separation](ADR-003-CIRM-and-EI-Separation.md)
- [ADR-004 — Human-Supplied Knowledge Must Be Labelled](ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md)
- [ADR-005 — No Recommendation Without Inspectable Lineage](ADR-005-No-Recommendation-Without-Inspectable-Lineage.md)
- [ADR-010 — Structured-Source-First, AI-Assisted Evidence Acquisition](ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md)

## Proposed ADRs

These are migrated placeholders retained for future review. They are not accepted architecture doctrine until reviewed and explicitly marked Accepted.

- [ADR-006 — Signal Architecture](ADR-006-Signal-Architecture.md)
- [ADR-007 — Transformation Thesis](ADR-007-Transformation-Thesis.md)
- [ADR-008 — Recommendation Engine](ADR-008-Recommendation-Engine.md)

## Superseded / archived ADRs

No superseded or archived ADRs currently exist. If an ADR is superseded, keep the file available, update its status, link the replacing ADR and list it here.

## ADR naming convention

Use:

```text
ADR-XXX-Short-Kebab-Case-Title.md
```

Rules:

- ADR numbers must be unique.
- Accepted ADRs ADR-001 to ADR-005 are reserved for their current meanings.
- Proposed ADRs may be renumbered before acceptance if needed to preserve a clean sequence.
- File names, H1 titles and README entries must agree.

## Relationship to Reference Architecture

The Reference Architecture explains the whole CIOS system. ADRs record specific decisions that constrain or clarify it.

When an ADR and a reference architecture document both apply, future contributors should:

1. treat Accepted ADRs as binding decision history;
2. use the Reference Architecture and Design Doctrine for system-level coherence;
3. update both the affected architecture document and ADR index if a new accepted decision changes direction.

## Requirement for future runtime PRs

Runtime PRs must review relevant Accepted ADRs before implementation. If a runtime change contradicts an Accepted ADR, Codex must stop and explain the conflict before implementation.

A runtime PR that changes CIOS reasoning, collection, model state, evidence lineage, recommendation behaviour or human-knowledge handling should state which Accepted ADRs it complies with and how.

## Template

Use [ADR-Template.md](ADR-Template.md) for new decisions.
