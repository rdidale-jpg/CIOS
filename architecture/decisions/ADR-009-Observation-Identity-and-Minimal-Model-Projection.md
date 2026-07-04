# ADR-009: Observation Identity and Minimal Model Projection

Status: Proposed
Date: 2026-07-04

## Context

ADR-001 defines Observations as atomic intelligence units and ADR-002 defines the Enterprise Model as durable memory. Flora needed a first implementation choice for Observation identity, duplicate handling and current-state projection before the full Enterprise Model exists.

## Decision

Propose deterministic Observation identity based on a normalised tuple of enterprise ID, Observation type, atomic statement and affected Enterprise Model attribute. Reprocessing the same claim returns the same Observation and appends new supporting Evidence IDs as corroboration.

Propose a minimal current-state Enterprise Model projection derived from the Observation ledger. The projection is not canonical memory; the Observation ledger and Evidence lineage remain inspectable. Current attributes retain prior values and contradiction metadata.

## Alternatives considered

- Evidence ID as Observation ID: rejected because multiple Evidence records can corroborate one Observation.
- Report section as memory: rejected because reports must remain views.
- Semantic similarity deduplication: deferred because it requires governance thresholds not yet approved.
- Full append-only model events only: deferred because current Flora views need a simple projection.

## Consequences

- Safe retry and repeated collection are supported.
- Corroborating Evidence strengthens lineage without destroying provenance.
- Similar but differently worded claims can still create separate Observations until governed similarity matching is approved.
- Human architecture approval is required before treating this as the permanent identity strategy.
