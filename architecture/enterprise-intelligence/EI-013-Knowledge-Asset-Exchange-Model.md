# EI-013 — Knowledge Asset Exchange Model

**Status:** Proposed Foundation  
**Date:** 2026-07-11  
**Owner:** Rob / CIOS  
**Owning ADR:** ADR-016 — Knowledge Packs as the Standard Exchange Mechanism  
**Normative specification:** [Knowledge Pack Specification v1.0](../specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md)

## Purpose

EI-013 owns the semantics of exchanged Knowledge Assets. A Knowledge Asset is an inspectable unit of portable intelligence carried by a Knowledge Pack.

## Semantic rules

Knowledge Assets must declare type, subject, provenance, authoring mode, confidence where applicable, lineage, temporal scope, human-supplied labels where applicable, and whether the asset is fact, interpretation, recommendation, Unknown or Contradiction.

## Canonical boundary

Exchange does not equal canonical acceptance. Accepted Knowledge Assets may inform Enterprise Twin, Industry Twin, Market Participant Twin, Opportunity Twin or Relational Twin updates, but promotion requires the target model's own acceptance process.
