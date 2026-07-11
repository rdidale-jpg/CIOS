# FP-010 — Knowledge Pack Architecture

**Status:** Proposed Foundation  
**Date:** 2026-07-11  
**Owner:** Rob / CIOS  
**Owning ADR:** ADR-016 — Knowledge Packs as the Standard Exchange Mechanism  
**Normative specification:** [Knowledge Pack Specification v1.0](../specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md)

## Purpose

FP-010 owns the conceptual architecture for Knowledge Packs in CIOS Architecture v2.0. A Knowledge Pack is a governed exchange container for Knowledge Assets, presentation payloads, provenance, validation results, Unknowns, Contradictions and recommendations.

## Principles

- A Knowledge Pack is an exchange mechanism, not automatic canonical fact.
- A Knowledge Asset remains inspectable, typed, versioned and traceable to source, author, model or human contribution.
- Human-supplied knowledge remains labelled.
- Unknowns and Contradictions remain first-class objects.
- Recommendations require inspectable lineage.
- Accepted packages may be stored in a Knowledge Repository for future retrieval and rendering.

## Conceptual model

Knowledge Pack architecture separates package validity from canonical knowledge acceptance. Package validation checks structure, lineage, required metadata and safety constraints. Canonical acceptance remains governed by the owning Enterprise Twin, Industry Twin, Market Participant Twin, Opportunity Twin or Relational Twin process.

## Runtime boundary

This paper creates no Flora runtime obligation in Phase 1. Runtime contracts will be derived from the normative specification in later phases.
