# ADR-001 — Observations as Atomic Intelligence Unit

**Identifier:** ADR-001
**Version:** 1.0
**Document Type:** Architecture Decision Record
**Authority Classification:** Accepted canonical ADR
**Status:** Accepted
**Date:** 2026-07-03
**Owner:** Rob / CIOS

## Context

CIOS collects evidence about enterprises, but the project objective is not evidence accumulation. CIOS must detect meaningful change, remember it, connect it to enterprise state and support commercial reasoning.

Raw Evidence is necessary for proof and traceability, but it is usually too transient, duplicated, uneven and source-shaped to be the reusable intelligence unit.

## Decision

CIOS treats Observations, not raw Evidence, as the atomic reusable unit of Enterprise Intelligence.

An Observation is an evidence-backed statement that something meaningful has been noticed about an enterprise, actor, relationship, behaviour, pressure, event or change. Observations sit between Evidence and higher-order reasoning.

## Why Evidence alone is insufficient

Evidence alone is insufficient because it can be:

- transient, stale or removed from its original source;
- duplicated across multiple pages or collection runs;
- too granular to support durable reasoning;
- too source-specific to compare across enterprises;
- factual but not commercially meaningful;
- contradictory without a structured way to preserve the contradiction;
- difficult to reuse after a report has been generated.

Evidence proves that something was seen. It does not by itself decide what should be remembered.

## Why Observations create durable memory

Observations convert evidence-backed facts into structured, reusable intelligence atoms. They can be stored, linked, compared, refreshed, challenged and retired.

Repeated Observations form memory. Observation Networks reveal patterns. Patterns support Signals. Signals support Hypotheses and commercial theses. This gives CIOS a durable intelligence substrate instead of a pile of collected fragments.

## Consequences for Flora runtime

Flora runtime should increasingly:

- create Observations from accepted Evidence;
- attach evidence lineage to every Observation;
- update Enterprise Models from Observations;
- reason from Observations where possible rather than directly from scrape fragments;
- preserve unknowns, contradictions and confidence limits at Observation level;
- expose Observation lineage in downstream Signals, Hypotheses and recommendations.

This does not require every runtime change to implement the full Observation Engine immediately, but new design should align with this direction.

## Architecture documents affected

- [EI-012 — Enterprise Observation Model](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md)
- [CIOS Reference Architecture v1.0](../reference-architecture/CIOS-Reference-Architecture-v1.0.md)
- [CIOS Design Doctrine](../reference-architecture/CIOS-Design-Doctrine.md)

## Runtime implications

The Observation Engine becomes a foundational runtime capability for Flora. Report generation should become a view over Observation-backed Enterprise Model state, not the primary destination of collected evidence.

## Compliance test

- Does the change create or preserve Observations as reusable objects?
- Does it avoid direct reasoning from raw evidence where Observations should exist?
- Does it update Enterprise Model state rather than only reports?
- Does it preserve evidence lineage from Observation back to Source?
- Does it keep unknowns, contradictions and confidence limits visible at Observation level?

## Review date

2026-10-03
