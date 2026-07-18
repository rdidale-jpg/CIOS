# ADR-024: Hybrid Enterprise Intelligence Runtime

## Status
Proposed

## Date
2026-07-18

## Owner
Rob / CIOS

## Context
CIOS differentiates through Enterprise Reinvention Intelligence, Living Commercial Digital Twins and evidence-governed commercial judgement. Existing accepted decisions already establish that Observations are atomic intelligence units, Enterprise Models are durable memory, human-supplied knowledge must be labelled, strong recommendations require inspectable lineage, and Flora may perform evidence-governed runtime interpretation without silently changing canonical memory.

The next Flora architecture decision is whether runtime intelligence should be led by GPT answers, encoded deterministically, or orchestrated through a governed hybrid model.

## Decision
CIOS will adopt a hybrid governed Enterprise Intelligence runtime for Flora:

```text
Enterprise Knowledge
→ Flora Runtime
→ Governed Reasoning Orchestration
→ Specialist GPT Workers
→ Candidate Intelligence Objects
→ Flora Validation
→ Enterprise Intelligence
→ Strategic Sales Experience
```

1. Flora is the Enterprise Intelligence runtime.
2. The repository remains the authoritative source for governed Enterprise Knowledge and architecture.
3. GPTs operate as bounded reasoning workers, not sovereign agents or systems of record.
4. GPT outputs are candidate intelligence unless accepted through governed lifecycle controls.
5. Flora owns orchestration, provenance, runtime state, validation and presentation.
6. Deterministic controls govern lineage, authority, lifecycle, confidence, contradiction preservation and recommendation eligibility.
7. Human approval remains required for defined high-consequence commercial judgements.
8. Reports, summaries and user views remain transient unless deliberately promoted into governed knowledge objects.
9. Durable learning must be written back through governed knowledge processes, not silently inserted by runtime agents.
10. Strong Recommendations require inspectable lineage.

The owning architecture paper is `FEIR-001 — Flora Enterprise Intelligence Runtime Architecture v1.0`.

## Options considered

### Option A — GPT-led reasoning with passive Flora

```text
Knowledge → GPT → Answer
```

**Advantages**

- Fast to prototype.
- Provides fluent narrative and synthesis.
- Requires limited bespoke runtime policy logic.

**Disadvantages**

- Collapses evidence, observation, hypothesis and recommendation boundaries into prose.
- Risks treating retrieved text or model priors as authoritative knowledge.
- Does not reliably preserve Unknowns, Contradictions or competing hypotheses.
- Makes durable learning and audit dependent on generated answers.

**Risks**

- Unsupported executive specificity or commercial recommendations may be presented as fact.
- Knowledge lineage may be too weak for Chief Architect review or commercial accountability.
- The runtime may become a conventional RAG chatbot rather than Enterprise Intelligence infrastructure.

**Consequences**

- Rejected as the primary architecture because it conflicts with accepted CIOS evidence, lineage, human-knowledge labelling and recommendation controls.

### Option B — Deterministic Flora reasoning with GPT presentation

```text
Knowledge → Flora reasoning engine → GPT explanation → View
```

**Advantages**

- Strong repeatability, explainability and policy enforcement.
- Clear control over lifecycle state, evidence lineage and recommendation thresholds.
- GPT is kept away from authority and used only to explain validated results.

**Disadvantages**

- Attempts to encode too much commercial judgement, ambiguity and mechanism interpretation in software.
- Weak at interpreting new patterns, competing explanations and executive nuance.
- May create brittle rules that overfit early Banking examples.

**Risks**

- Strategic judgement may be reduced to deterministic scoring without adequate methodology.
- Implementation cost and complexity may delay useful Flora learning.
- Commercial users may receive correct but unhelpful mechanical outputs.

**Consequences**

- Rejected as the primary architecture because CIOS requires human-amplified commercial judgement, not a fully deterministic reasoning engine.

### Option C — Hybrid governed runtime

```text
Knowledge → Flora orchestration → bounded GPT workers → candidate intelligence → deterministic validation → governed view
```

**Advantages**

- Uses GPTs where they are valuable: interpretation, challenge, narrative and hypothesis generation.
- Preserves deterministic authority for identity, lineage, lifecycle, confidence bounds, contradiction handling and recommendation eligibility.
- Keeps durable knowledge in governed repositories and accepted Enterprise Intelligence objects.
- Supports Strategic Sales users without exposing repository internals.

**Disadvantages**

- Requires structured worker contracts, validation services and runtime state management.
- Requires careful governance of write-back and human approval boundaries.
- Produces more candidate objects and audit records than a simple chatbot.

**Risks**

- If validation is underbuilt, GPT prose could still leak into authoritative knowledge.
- If policy is overbuilt, the runtime could drift toward Option B brittleness.
- Worker/model versioning and audit retention require explicit design.

**Consequences**

- Selected as the proposed direction. It preserves ADR-014 while expanding from evidence-governed account-level briefs to a broader governed Enterprise Intelligence runtime architecture.

## Preserved decisions

This ADR preserves accepted decisions in ADR-001, ADR-002, ADR-003, ADR-004, ADR-005, ADR-009, ADR-010, ADR-011, ADR-012, ADR-013, ADR-014 and ADR-016. It does not replace EI-001, EI-002, EI-003, EI-012, FP-003 or FP-009 ownership of durable knowledge, graph, behaviour, observation and hypothesis semantics.

## Conflicts

No conflict with accepted architecture was identified during this commission. This ADR remains Proposed pending established Chief Architect governance.

## Consequences

- Flora implementation must include runtime orchestration, candidate-intelligence state, deterministic validation and audit before strong recommendations are enabled.
- GPT workers must return structured candidate or transient outputs; unclassified prose is never authoritative intelligence.
- Reports and briefs remain views unless promoted through governed knowledge processes.
- Subsequent ADRs are recommended for runtime graph persistence, recommendation eligibility policy promotion, audit-retention boundaries and external-output approval.
