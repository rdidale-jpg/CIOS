# Twin Presentation Model Specification v1.0

**Status:** Draft Normative Specification  
**Date:** 2026-07-11  
**Owner:** Rob / CIOS  
**Owning paper:** [FP-011 — Knowledge Exchange Architecture](../../founding-papers/FP-011-Knowledge-Exchange-Architecture.md)  
**Owning ADR:** [ADR-016](../../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md)

## Purpose

This specification owns presentation payload semantics for Twin Presentation Models. A Twin Presentation Model is a versioned interpretation intended for rendering, review and navigation over governed knowledge.

## Rules

Specialist GPTs may author account-level Twin Presentation Models. Flora may later validate, version, store and render accepted models. A Twin Presentation Model is interpretation unless its claims are separately accepted by the canonical owner. Unknowns, Contradictions, human-supplied knowledge and recommendations must remain labelled with inspectable lineage.

## Knowledge Pack release carriage

Twin Presentation Models for Commercial Digital Twin releases MUST be carried under `payload/presentation-model/` in the Knowledge Pack release structure. A single Twin release MAY contain multiple Presentation Models for different audiences or purposes.

Each Presentation Model MUST declare its audience, purpose, source Twin release, source cut-off, producer, interpretation status, Evidence and Observation lineage references, Unknowns, Contradictions and human-supplied knowledge labels. Presentation Model acceptance is acceptance of a governed interpretation for rendering, review and navigation; it does not promote the interpretation or its claims to canonical fact. Reports generated from Presentation Models remain views.
