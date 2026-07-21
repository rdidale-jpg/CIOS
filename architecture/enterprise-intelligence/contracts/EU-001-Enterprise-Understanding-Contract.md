# EU-001 — Enterprise Understanding Contract

**Identifier:** EU-001
**Document Type:** Enterprise Intelligence Contract
**Authority Classification:** Review canonical contract
**Document class:** Proposed operational contract / review material
**Short name:** Enterprise Understanding Contract
**Version:** 0.1 review draft
**Status:** Review
**Owner:** Rob / CIOS
**Canonical review path:** `architecture/enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md`
**Companion proposal:** [`ADR-023`](../../decisions/ADR-023-Enterprise-Understanding-as-the-Primary-Governed-Asset.md)
**Production release-profile membership:** None

**Last updated:** 2026-07-21
---

## 1. Purpose

EU-001 defines review material for treating **Enterprise Understanding** as the governed outcome CIOS is trying to improve, without creating a new canonical runtime object and without replacing the Commercial Digital Twin Blueprint Contract.

Enterprise Understanding is the inspectable, evidence-backed comprehension of an enterprise's structure, behaviour, pressures, constraints, decision logic and commercially relevant change. It is expressed through existing authoritative architecture objects: Evidence, Observations, Enterprise Models, Enterprise Knowledge Graphs, Commercial Digital Twins, Hypotheses, Commercial Theses, Recommendations, Presentation Models and Knowledge Packs.

EU-001 is proposed operational guidance only. It does not promote itself, ADR-023, the Reference Architecture, EI papers, FP papers or any runtime implementation to Accepted or Authoritative status.

## 2. Authority boundary

This Contract depends on, and must remain subordinate to:

- CIOS Reference Architecture;
- EI-001 — Enterprise Model Specification;
- EI-002 — Enterprise Knowledge Graph;
- EI-003 — Enterprise Behaviour Model;
- EI-012 — Enterprise Observation Model;
- FP-009 — Hypothesis Validation Standard;
- ADR-009 — Progressive Assurance for Commercial Digital Twins;
- Commercial Digital Twin Blueprint Contract.

Where EU-001 conflicts with an Accepted ADR, the Reference Architecture or an owning EI/FP paper, the existing authority wins and EU-001 must be revised or rejected.

## 3. Non-goals

EU-001 does not:

1. define a new canonical runtime object named Enterprise Understanding;
2. replace the Enterprise Model, Enterprise Knowledge Graph, Observation Model or Commercial Digital Twin;
3. replace or supersede the Commercial Digital Twin Blueprint Contract;
4. alter production Researcher or Reviewer packs;
5. change accepted architecture, accepted ADRs or release-profile membership;
6. require provider calls or consume provider credits;
7. permit unlabelled human knowledge, ungrounded inference or recommendation without inspectable lineage.

## 4. Working definition

**Enterprise Understanding** is the governed level of comprehension that exists when CIOS can explain:

- what the enterprise is;
- how it is structured and governed;
- how it behaves under pressure;
- what has materially changed;
- why the change matters;
- what remains Unknown or Contradictory;
- which hypotheses are being tested;
- what action or learning step is justified by the evidence.

Understanding is therefore a quality of the existing intelligence system, not an additional persisted authority layer.

## 5. Minimum review contract

A candidate Enterprise Understanding view should be considered reviewable only when it preserves the following distinctions:

| Concern | Required treatment |
| --- | --- |
| Evidence | Attributable proof remains separate from intelligence interpretation. |
| Observation | Durable atomic memory records what changed, exists, is absent or contradicts. |
| Enterprise Model | Accepted state is held by the owning model and remains the durable memory boundary. |
| Knowledge Graph | Relationships and inferred links are explainable, confidence-scored and temporal. |
| Behaviour | Behaviour patterns are evidence-derived and cannot override contradictory evidence. |
| Hypothesis | Propositions are testable, falsifiable and linked to evidence demand. |
| Recommendation | Recommendations are downgraded when lineage is incomplete. |
| Unknowns | Unknowns remain visible as first-class decision constraints. |
| Contradictions | Contradictions are preserved until resolved by governed review. |

## 6. Review validation trigger

EU-001 should not be considered for acceptance until it has been validated against:

1. MOD; and
2. one materially different enterprise with different sector, operating model, evidence availability or commercial motion.

The validation should test whether EU-001 improves comprehension without increasing document theatre, duplicating canonical objects or weakening progressive assurance.

## 7. Acceptance questions

Before promotion is considered, reviewers should answer:

1. Does EU-001 clarify the target outcome of CIOS without changing the canonical object model?
2. Does it preserve Evidence → Observation → Enterprise Model → Commercial Digital Twin authority?
3. Does it improve hypothesis validation and decision quality?
4. Does it keep Unknowns, Contradictions and evidence boundaries visible?
5. Does it remain compatible with ADR-009 progressive assurance?
6. Does it leave production packs and release profiles unchanged until separately approved?
