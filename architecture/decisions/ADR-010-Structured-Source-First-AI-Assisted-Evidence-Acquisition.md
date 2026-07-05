# ADR-010 — Structured-Source-First, AI-Assisted Evidence Acquisition

**Status:** Accepted  
**Owner:** Rob / CIOS  
**Date:** 2026-07-05

## Context

Financial Intelligence needs accurate, explainable and cost-governed acquisition of source facts. Recent Flora runtime work showed that whole-document multimodal AI, provider DTOs and ad hoc extraction states can be mistaken for canonical CIOS intelligence if the acquisition boundary is not explicit.

CIOS already holds that Evidence proves change, Observations remember change and the Enterprise Model / Commercial Digital Twin accumulates durable state. This ADR clarifies how source facts enter that chain.

## Decision

CIOS uses the following acquisition hierarchy and SHOULD use the least ambiguous and least expensive adequate method:

1. Authoritative structured source, API, filing data or XBRL.
2. Source-specific deterministic adapter.
3. Local document structure, text and table extraction.
4. Bounded multimodal AI interpretation.
5. Governed human exception review.

AI is not the default when an authoritative structured source already contains the required fact. AI remains appropriate for narrative interpretation, ambiguous tables, complex documents, poor document structure and bounded cases where deterministic methods cannot safely extract the fact.

Provider output is untrusted candidate data until deterministic validation and canonical mapping complete. Provider DTOs are boundary contracts, not canonical CIOS models. Commercial Digital Twin state may only update through the canonical path from accepted Evidence to Observation to Enterprise Model projection.

## Rules

- Preserve source, transformation, prompt/schema/model where applicable, validation and canonical-mapping lineage.
- Do not repeatedly process unchanged sources that have already completed successfully.
- Prevent duplicate paid model calls through source hashes, packet hashes, prompt/schema versions and response reuse.
- Focus human review on ambiguity, contradiction and material exceptions.
- Failures must not silently update the Commercial Digital Twin.
- Partial success may preserve valid facts while quarantining invalid candidates.
- Candidate facts must satisfy the owning data contract before Observation creation.
- Provider-specific DTOs must be mapped into canonical CIOS objects before reasoning or model update.

## Alternatives considered

### Whole-document AI as universal collection mechanism

Rejected as the default because it is costly, harder to audit, may miss or hallucinate page-grounded facts and bypasses better structured sources when they exist. It remains available as a bounded adapter for complex source fragments.

### Deterministic extraction only

Rejected because many enterprise documents contain narrative, irregular tables, visual layout and ambiguity that deterministic extraction cannot reliably interpret without unacceptable loss of useful evidence.

### Human-only collection

Rejected because it does not scale and prevents CIOS from learning source yield, extraction patterns and repeatable validation paths. Human judgement remains essential for exceptions and calibration.

### Commercial-data-provider-first collection

Rejected as the default because provider output is secondary unless its authority and lineage satisfy the source requirement. Providers can supply useful candidate facts, but they do not replace governed source lineage or canonical mapping.

### Hybrid structured-source-first approach

Accepted because it prefers authoritative structured data where available, uses deterministic adapters when reliable, applies AI only where it adds interpretive value, and reserves human attention for high-value exceptions.

## Consequences

### Positive

- Improves accuracy, cost control and explainability.
- Reduces unnecessary paid model calls.
- Preserves provenance and transformation lineage.
- Prevents provider schemas from becoming canonical CIOS models.
- Supports partial success without corrupting Commercial Digital Twin state.

### Negative

- Requires source registry, hashing, validation and canonical mapping infrastructure.
- Requires more explicit adapter contracts before new providers are trusted.
- May slow early prototypes where whole-document AI would appear faster.
- Requires careful UX language for partial success and exception review.

## Migration implications

Existing Flora Financial Intelligence runtime work should be reconciled to this ADR before further implementation. Runtime code should distinguish source acquisition, provider candidate facts, canonical financial facts, Observations and Enterprise Model projection. Existing provider responses should be treated as candidate data until accepted against EI-001 and EI-012.

## Validation and review conditions

A compliant runtime path must show:

- governed source identity and retrieval lineage;
- source or packet hash used for idempotency;
- candidate fact validation against the owning data contract;
- canonical mapping before Observation creation;
- Evidence → Observation → Enterprise Model lineage;
- no Commercial Digital Twin update from failed or unvalidated candidates;
- human-review queue for material ambiguity, contradiction or unsupported candidates.

## Related documents

- [CIOS Reference Architecture v1.0](../reference-architecture/CIOS-Reference-Architecture-v1.0.md)
- [EI-001 — Enterprise Model Specification](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md)
- [EI-012 — Enterprise Observation Model](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md)
- [FP-003 — Flora Intelligence Architecture](../founding-papers/FP-003-Flora-Intelligence-Architecture.md)
