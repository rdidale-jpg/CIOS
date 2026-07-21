# ADR-011 — Dual-Speed Financial Intelligence

**Identifier:** ADR-011
**Version:** 1.0
**Document Type:** Architecture Decision Record
**Authority Classification:** Accepted canonical ADR
**Status:** Accepted
**Owner:** Rob / CIOS
**Date:** 2026-07-05

## Context

Flora Financial Intelligence has been treating structured filing completion as the practical prerequisite for useful financial intelligence. That protects canonical quality, but it can leave Rob with no commercial answer when an ESEF, NSM or hosted filing route is temporarily inaccessible.

ADR-010 remains correct: provider output is candidate data, structured sources are preferred for canonical acquisition and the Commercial Digital Twin may only update through governed Evidence, Observations and Enterprise Model projection.

## Decision

CIOS adopts a dual-speed Financial Intelligence model:

1. **Rapid Financial Intelligence** may produce evidence-backed candidate facts, analysis, Hypotheses and Recommendations from official annual reports, XHTML/PDF reports, results announcements, investor presentations, earnings materials and regulatory announcements before structured verification completes.
2. **Financial Verification** validates important candidate facts using the strongest available route: official structured filing; deterministic table extraction from the official report; corroborating official publication; controlled human review; or retention as unverified candidate.
3. **Canonical Twin Update** remains restricted to accepted facts moving through the existing governed path: Source → Evidence → Observation → Enterprise Model.

Structured-source-first remains the preferred route for accepted canonical financial facts. Rapid intelligence does not weaken source governance; it changes the user outcome from an all-or-nothing parser result to a useful, explicitly labelled intelligence result.

## Rules

- Official PDF, XHTML, results announcements and investor materials may provide Evidence and candidate facts.
- Provider or AI output is candidate data, not canonical intelligence.
- Rapid outputs must distinguish Fact, Inference, Hypothesis and Recommendation.
- Every material reported fact must carry inspectable source lineage: source document, authority, document date, reporting period, page/section/table/location where available, supporting span where permissible, unit, scale, scope, basis, extraction method, confidence and ambiguity.
- Candidate facts must not silently update the Enterprise Model.
- Accepted facts create or update Evidence, Observations and Enterprise Model state only through existing governed boundaries.
- Structured verification may operate asynchronously.
- Failure of structured verification must not erase useful, properly labelled rapid intelligence.
- Unknowns and Contradictions remain visible user-facing intelligence objects.
- Partial evidence-backed results are preferable to an empty result when limitations are explicit.
- Observations remain atomic and non-speculative; financial facts must not be combined with commercial interpretation.
- Commercial interpretation belongs in Signals, Hypotheses and Recommendations.

## Stopped work

Further hosted attempts to reverse-engineer `ixbrl-viewer.htm`, guess FCA NSM download URLs or deploy unproven hosted filing-source changes are paused. The existing `StructuredFinancialAdapter` remains preserved as a verification-lane component.

## Consequences

### Positive

- Rob can receive timely, cited financial-pressure and transformation intelligence from official documents.
- Structured ingestion continues to improve canonical quality without blocking all value.
- Candidate-versus-canonical separation is explicit and auditable.
- Unknowns, contradictions and verification queues become part of the intelligence product.
- Repeated unchanged verification failures can be cached and reported without repeated provider calls.

### Negative

- Rapid intelligence requires careful UX labelling so users do not confuse candidates with accepted twin state.
- Some outputs remain partial until deterministic extraction, structured filing or human review completes.
- Source-location quality varies by official document format and extraction method.

## Validation and review conditions

A compliant implementation must demonstrate:

- official source identity retained for every material fact;
- candidate facts persisted separately from accepted canonical facts;
- zero Enterprise Model updates from unverified candidates;
- visible Unknowns, Contradictions and verification exceptions;
- cost, runtime, candidate count, accepted count and AI call instrumentation;
- reusable source/profile configuration rather than company-specific parser code;
- BT FY26 rapid Financial Pressure and Transformation Outlook produced without ESEF/NSM success;
- at least two additional enterprises producing useful partial cited output through the same generic path.

## Related documents

- [ADR-010 — Structured-Source-First, AI-Assisted Evidence Acquisition](ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md)
- [ADR-005 — No Recommendation Without Inspectable Lineage](ADR-005-No-Recommendation-Without-Inspectable-Lineage.md)
- [ADR-001 — Observations as Atomic Intelligence Unit](ADR-001-Observations-as-Atomic-Intelligence-Unit.md)
- [CIOS Reference Architecture v1.0](../reference-architecture/CIOS-Reference-Architecture-v1.0.md)
