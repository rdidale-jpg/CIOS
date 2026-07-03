# ADR-004 — Human-Supplied Knowledge Must Be Labelled

**Status:** Accepted
**Date:** 2026-07-03
**Owner:** Rob / CIOS

## Context

CIOS may use human-supplied knowledge such as Rob score, relationship intelligence, account context, prior experience, stakeholder judgement or commercially sensitive insight. This knowledge can be valuable, but it has a different provenance from evidence-backed facts collected from sources.

If human-supplied knowledge is not labelled, CIOS may present it as externally evidenced fact or blend it into recommendations without clear governance.

## Decision

Human-supplied knowledge, including Rob score and relationship intelligence, must be labelled, dated and distinguishable from evidence-backed facts.

Human knowledge may inform reasoning, but its source, date, confidence and role in the reasoning chain must remain inspectable.

## Governance rationale

Labelling human-supplied knowledge protects:

- provenance clarity;
- trust in evidence-backed claims;
- separation between facts, judgement and relationship context;
- ethical use of sensitive commercial knowledge;
- auditability of recommendations;
- future correction when human context becomes stale or inaccurate.

## Runtime implications

Flora should:

- store human-supplied inputs with explicit provenance;
- distinguish human knowledge from source-backed Evidence in UI and generated outputs;
- date and, where possible, owner-label human inputs;
- prevent human-supplied knowledge from silently becoming a fact;
- show where human context affects conviction, hypotheses or recommendations.

## Architecture documents affected

- [FP-008 — Commercial Conviction Model](../founding-papers/FP-008-Commercial-Conviction-Model.md)
- [EI-001 — Enterprise Model Specification](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md)
- [EI-002 — Enterprise Knowledge Graph](../enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md)

## Review date

2026-10-03
