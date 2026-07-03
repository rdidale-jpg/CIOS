# ADR-005 — No Recommendation Without Inspectable Lineage

**Status:** Accepted
**Date:** 2026-07-03
**Owner:** Rob / CIOS

## Context

CIOS recommendations may influence commercial action. Strong recommendations without inspectable lineage can create false confidence, hide weak evidence and make it difficult for humans to challenge or improve the reasoning.

CIOS must favour trust, explainability and commercial judgement over persuasive but unsupported recommendation language.

## Decision

CIOS must not present strong recommendations unless the reasoning chain can be inspected.

The expected lineage is:

```text
Recommendation
→ Commercial Thesis / Hypothesis
→ Signal
→ Observation
→ Evidence
→ Source
```

If the lineage is incomplete, the output should be framed as a question, weak hypothesis, learning action or evidence demand rather than a strong recommendation.

## Trust rationale

Inspectable lineage allows humans and AI agents to:

- verify what the recommendation depends on;
- distinguish evidence-backed claims from inference;
- identify unsupported leaps;
- challenge stale, weak or contradictory evidence;
- calibrate commercial conviction;
- learn from accepted, rejected or delayed recommendations.

## Runtime implications

Flora should:

- preserve links from recommendations back to Sources wherever possible;
- expose reasoning lineage in generated outputs and product surfaces;
- avoid strong recommendation language when lineage is weak;
- label assumptions, unknowns and contradictions;
- support review of the Hypotheses and Signals behind each recommendation.

## Architecture documents affected

- [CIOS Reference Architecture v1.0](../reference-architecture/CIOS-Reference-Architecture-v1.0.md)
- [FP-009 — Hypothesis Validation Standard](../founding-papers/FP-009-Hypothesis-Validation-Standard.md)
- [CIOS Design Doctrine](../reference-architecture/CIOS-Design-Doctrine.md)

## Review date

2026-10-03
