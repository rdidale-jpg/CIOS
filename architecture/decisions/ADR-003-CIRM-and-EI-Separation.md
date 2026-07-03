# ADR-003 — CIRM and EI Separation

**Status:** Accepted
**Date:** 2026-07-03
**Owner:** Rob / CIOS

## Context

CIOS contains two closely related but distinct architecture domains. The CIOS Intelligence Reference Model (CIRM) defines the reasoning process that converts observable enterprise reality into commercial judgement. Enterprise Intelligence defines the enterprise knowledge model CIOS builds and maintains.

Without separation, process concepts, knowledge-model concepts and runtime implementation details can blur into one vocabulary.

## Decision

CIOS separates CIRM from Enterprise Intelligence.

CIRM defines how CIOS reasons. Enterprise Intelligence defines what CIOS knows. Flora operationalises both.

## Alternatives considered

- **Single unified architecture vocabulary:** simpler at first, but risks mixing reasoning process, knowledge model and product runtime responsibilities.
- **Runtime-first terminology:** useful for implementation speed, but risks allowing Flora implementation details to become architecture doctrine.
- **Evidence-only architecture:** simpler for collection, but insufficient for durable memory, Commercial Digital Twins and inspectable commercial reasoning.

## Consequences

- Architecture documents should state whether they primarily define reasoning process, enterprise knowledge model or runtime implementation.
- Flora should not collapse CIRM stages and Enterprise Intelligence objects into generic report sections.
- Terminology should remain compliant with the Reference Architecture and Glossary.
- New runtime components should explain how they operationalise CIRM, Enterprise Intelligence or both.

## Architecture documents affected

- [CIOS Reference Architecture v1.0](../reference-architecture/CIOS-Reference-Architecture-v1.0.md)
- [Glossary](../reference-architecture/Glossary.md)
- [Document Map](../reference-architecture/Document-Map.md)

## Runtime implications

Flora runtime designs should distinguish between reasoning workflow components and persistent Enterprise Model components. A component may bridge both, but its responsibility should be explicit.

## Compliance test

- Does the change distinguish reasoning process concepts from enterprise knowledge-model concepts?
- Does it state whether the component belongs to CIRM, Enterprise Intelligence or both?
- Does it avoid allowing Flora implementation labels to become architecture doctrine?
- Does it use Reference Architecture and Glossary terminology consistently?

## Review date

2026-10-03
