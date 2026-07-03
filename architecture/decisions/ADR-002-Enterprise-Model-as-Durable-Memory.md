# ADR-002 — Enterprise Model as Durable Memory

**Status:** Accepted
**Date:** 2026-07-03
**Owner:** Rob / CIOS

## Context

Flora has historically produced useful briefing and report outputs from collected evidence. That is valuable, but report-centric design risks losing project memory between runs and repeating the same evidence-to-summary cycle.

CIOS needs a durable model of each enterprise so evidence, Observations, Signals, Hypotheses and commercial reasoning can accumulate over time.

## Decision

CIOS treats the Enterprise Model / Commercial Digital Twin as durable memory. Reports are views over model state.

The Enterprise Model should represent what CIOS knows, believes, questions and is tracking about an enterprise. Reports, briefings and dashboards should project from that memory for a specific audience or task.

## Why report-centric design is insufficient

Report-centric design is insufficient because it tends to:

- optimise for output text rather than maintained intelligence;
- bury useful findings inside one-time documents;
- make change detection harder across collection runs;
- duplicate information across UI sections;
- weaken lineage from recommendation back to source;
- obscure uncertainty and unresolved questions;
- make learning from outcomes difficult.

Reports should communicate intelligence. They should not be the only place intelligence exists.

## Consequences for Flora

Flora should evolve from a report generator into a runtime that maintains living Commercial Digital Twins. This means future runtime work should favour:

- persistent Enterprise Model updates;
- Observation-led state changes;
- inspectable lineage from model state to Evidence;
- change history and temporal state;
- model-backed reports, briefings and recommendations;
- feedback and learning loops that improve future reasoning.

## Architecture documents affected

- [EI-001 — Enterprise Model Specification](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md)
- [CIOS Reference Architecture v1.0](../reference-architecture/CIOS-Reference-Architecture-v1.0.md)
- [CIOS Design Doctrine](../reference-architecture/CIOS-Design-Doctrine.md)

## Runtime implications

Future Flora architecture should introduce or strengthen persistent Enterprise Model storage, model update logic, Observation-to-model mapping and views generated from model state.

## Compliance test

- Does the change update or preserve durable Enterprise Model state?
- Does it treat reports, briefings and dashboards as views over model state?
- Does it support comparison across collection runs instead of one-off summaries?
- Does it preserve lineage from model state back to Observations and Evidence?
- Does it avoid duplicating report text as the primary memory mechanism?

## Review date

2026-10-03
