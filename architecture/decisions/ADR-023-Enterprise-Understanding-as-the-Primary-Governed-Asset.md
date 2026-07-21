# ADR-023 — Enterprise Understanding as the Primary Governed Asset

**Identifier:** ADR-023
**Version:** 0.1
**Document Type:** Architecture Decision Record
**Authority Classification:** Proposed canonical ADR
**Status:** Proposed
**Date:** 2026-07-11
**Owner:** Rob / CIOS
**Related review material:** [`EU-001`](../enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md)
**Production release-profile membership:** None

## Context

CIOS aims to help users understand enterprises more deeply than ordinary profiles, dashboards or reports. Existing accepted architecture already establishes the authoritative chain: Evidence proves change, Observations remember change, Enterprise Models accumulate change, Commercial Digital Twins expose governed enterprise state, and recommendations require inspectable lineage.

The phrase **Enterprise Understanding** is useful as an outcome statement, but adopting it carelessly could create duplicate runtime objects, weaken the Observation doctrine or imply that generated narrative is authoritative.

## Decision

Propose that CIOS may use **Enterprise Understanding** as the name for the governed outcome it seeks to improve, provided that:

1. Enterprise Understanding is not introduced as a new canonical runtime object;
2. existing authoritative objects remain the source of truth;
3. the Commercial Digital Twin Blueprint Contract remains the operational contract for Blueprint construction;
4. evidence, fact, inference, hypothesis, recommendation, Unknown and Contradiction remain distinguishable;
5. production Researcher and Reviewer packs are unchanged until a separate accepted decision approves inclusion.

## Consequences

If accepted in future, this ADR would allow architecture and product language to describe CIOS as governing Enterprise Understanding while preserving the current canonical model boundaries.

Until accepted, ADR-023 is review material only and must not be cited as an accepted architecture decision.

## Dependencies

- CIOS Reference Architecture;
- EI-001 — Enterprise Model Specification;
- EI-002 — Enterprise Knowledge Graph;
- EI-003 — Enterprise Behaviour Model;
- EI-012 — Enterprise Observation Model;
- FP-009 — Hypothesis Validation Standard;
- ADR-009 — Progressive Assurance for Commercial Digital Twins;
- Commercial Digital Twin Blueprint Contract;
- EU-001 — Enterprise Understanding Contract.

## Validation trigger

Promotion requires validation against MOD and one materially different enterprise. The validation must show that the proposal improves governed understanding without replacing the Blueprint Contract, changing release profiles, or adding a new canonical runtime object.
