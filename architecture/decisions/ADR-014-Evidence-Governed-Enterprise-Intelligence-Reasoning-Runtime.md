# ADR-014: Evidence-Governed Enterprise Intelligence Reasoning Runtime

## Status
Accepted

## Context
The governed Commercial Digital Twin is authoritative memory, but deterministic Executive Commercial Canvas templates expose record structure, source labels and placeholder language rather than enterprise understanding. Strategic sales users need an interpretation that explains what is happening, what changed, why it matters, who matters, what is uncertain and what to do next, while preserving evidence boundaries.

## Decision
Flora will implement an Evidence-Governed Enterprise Intelligence Reasoning Runtime:

1. Governed Twin memory remains authoritative.
2. A bounded retrieval service selects only enterprise-scoped, decision-relevant records.
3. A structured evidence package is built with truth status, confidence, freshness and lineage.
4. A versioned strategic-sales reasoning profile guides AI interpretation.
5. Structured output is required as `ExecutiveCommercialBriefV1`.
6. A claim validator checks citations, tenancy, truth status, unknowns, contradictions, human knowledge, projections, confidence and dates before rendering.
7. Briefs are transient by default; persistence of interpretations requires human approval and preserves originating brief, profile, model, prompt, evidence package and lineage.
8. The model provider is abstracted behind a provider interface configured by environment settings.
9. Failure renders a safe unavailable state or deterministic evidence-bounded fallback, never fabricated generic executive content.

## Why deterministic templates are insufficient
Templates can reorganise accepted records but cannot reliably synthesise materiality, change significance, commercial relevance, decision ownership, access constraints or contradictions. They also risk repeating worksheet labels and placeholders as if they were insight.

## Why AI reasoning is required
AI reasoning is used as a bounded interpreter over a curated evidence package. It is not allowed to discover facts from public model knowledge or write canonical memory. Its role is to turn governed evidence into executive-specific hypotheses, pressure assessments, stakeholder questions and next learning moves.

## Bounded retrieval
Retrieval is scoped by authenticated user, active workspace, enterprise access, Twin version, evidence cut-off and evidence volume. It ranks by materiality, recency, evidence strength, change significance, decision relevance, commercial relevance, uncertainty and contradiction, not by record count.

## Evidence-package construction
Every selected item carries stable ID, class, statement, truth status, confidence, freshness, lineage, linked objects and source location where available. Unknowns, contradictions, human-supplied knowledge and accepted projections remain labelled.

## Structured output
The runtime requires `ExecutiveCommercialBriefV1` with executive summary, situation, changes, pressures, operating model, portfolio, stakeholders, commercial relevance, unknowns, contradictions, next moves, limitations, lineage, metadata and validation status.

## Claim validation
Material claims must cite package IDs. Invalid, cross-enterprise or unsupported claims are rejected or weakened. Unknowns are not promoted to facts, contradictions are disclosed, human knowledge and projections remain labelled, and recommendations require lineage.

## Separation of fact and interpretation
Canonical facts remain in governed memory. Generated briefs are interpretations and recommendations. Approved interpretations are stored separately from canonical facts with explicit status.

## Human approval
Users may inspect lineage, mark a brief useful, request regeneration and approve selected interpretation objects for governed persistence. Approval records include user, timestamp, model, prompt version, evidence package and claim lineage.

## Provider abstraction
The domain layer depends on a provider interface, not a hard-coded vendor. Environment configuration selects provider/model, timeout, token budget and retry posture. Telemetry records provider, model, token use and duration without logging secrets or unrestricted source text.

## Tenancy and security
Retrieval and brief storage are tenant-isolated. The runtime enforces authenticated user, active workspace, enterprise and Twin access. It prevents cross-enterprise context mixing and does not opt application data into provider training.

## Failure behavior
When the provider is unavailable or structured output fails, Flora does not present placeholder templates as intelligence. It shows an unavailable state or a deterministic evidence-bounded fallback that clearly identifies limitations and links to Model Explorer.

## Consequences
Flora gains executive-grade interpretation while preserving inspectable lineage, uncertainty and governance boundaries. The Model Explorer remains the data-oriented read model; Executive Intelligence Brief becomes the default MOD Twin view.

## 2026-07-11 Architecture v2.0 reconciliation amendment

This amendment narrows interpretation of ADR-014 without contradicting the accepted decision.

- Account-level runtime reasoning remains permitted.
- Account-level runtime reasoning is not required when an accepted Twin Presentation Model is supplied through the Knowledge Exchange Architecture.
- Specialist GPTs may create account-level interpretation, provided human-supplied knowledge, Unknowns, Contradictions and recommendations remain labelled with inspectable lineage.
- Flora may validate, version, store and render accepted Twin Presentation Models when later runtime implementation is approved.
- Flora-native AI should preferentially focus on Cross-Twin Intelligence across Industry Twin, Market Participant Twin, Opportunity Twin, Relational Twin and portfolio contexts.
- Runtime reasoning must never silently upgrade interpretation into canonical fact.

ADR-016 and the Architecture v2.0 specifications govern Knowledge Pack and Twin Presentation Model exchange boundaries. ADR-014 remains the accepted decision for evidence-governed account-level runtime reasoning where Flora performs interpretation directly.
