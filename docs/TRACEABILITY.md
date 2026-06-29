# CIOS Traceability Model

CIOS documentation must preserve a clear line of reasoning from foundational doctrine to shipped products. Traceability ensures that implementation choices can be explained, reviewed and revised when upstream knowledge changes.

```text
Constitution
    ↓
Science
    ↓
Engineering
    ↓
SDK
    ↓
Applications
    ↓
Products
```

## Constitution to Science

Constitutional documents define durable principles, boundaries and commitments. Science documents translate those principles into commercial theories, assumptions, hypotheses and laws that can be studied, challenged and refined.

A science document should identify which constitutional principles it supports or interprets.

## Science to Engineering

Engineering documents convert scientific concepts into buildable architecture, data structures, algorithms, interfaces and operating constraints. Engineering specifications should state which scientific assumptions they implement and which assumptions remain unimplemented or experimental.

## Engineering to SDK

The SDK is the reusable implementation layer for CIOS platform primitives. SDK modules should trace back to engineering specifications for package structure, dependency direction, model ownership and lifecycle behaviour.

Engineering documents should define enough detail for SDK implementation without forcing application-specific behaviour into the platform.

## SDK to Applications

Applications compose SDK primitives into domain workflows. Application documentation should identify the SDK modules, models and pipeline stages it uses. Applications must preserve upstream identifiers so recommendations, reports and memory records can be traced back to evidence, reasoning, scores and decisions.

## Applications to Products

Products package one or more applications for users, markets or operational contexts. Product documentation should identify which applications it exposes, which engineering standards govern them and which constitutional or scientific commitments constrain product behaviour.

## Bidirectional Change Control

Traceability is not only top-down. When implementation, application usage or product feedback reveals a gap, the relevant downstream artefact should create a review path back to the SDK, engineering specification, science document or constitutional principle that needs revision.

## Minimum Traceability Expectations

- Controlled documents appear in `MASTER_INDEX.md`.
- Engineering specifications reference upstream doctrine or science when applicable.
- SDK changes cite the engineering specification they implement.
- Application designs preserve identifiers across evidence, reasoning, scoring, decisions and recommendations.
- Product decisions identify the applications and standards they depend on.

## CBOK Traceability Extension

CBOK documents add a formal authoring layer for commercial knowledge claims, evidence, models, laws, patterns, validation records and architecture decisions. Each CBOK document should identify upstream doctrine or evidence, internal claims and downstream engineering or operational mappings.

CBOK traceability records should preserve both scientific confidence and operational confidence so that a claim can be scientifically promising without being ready for production use, or operationally useful while still requiring further scientific validation.

## Scientific Knowledge Traceability Chain

CBOK-SCI-001 extends traceability for scientific knowledge through the following chain:

```text
Evidence
    ↓
Claim
    ↓
Hypothesis
    ↓
Law / Model
    ↓
Standard
    ↓
Engineering Standard
    ↓
SDK
    ↓
Application
    ↓
Operational Evidence
```

This chain ensures that operational findings can be traced back to the scientific evidence and assumptions that informed engineering and application behaviour.

## Ontology Traceability Chain

Ontology work extends CIOS traceability through governed concept meaning and implementation artefacts:

```text
CBOK ontology concept
    ↓
Machine-readable ontology
    ↓
SDK model
    ↓
Knowledge graph node / edge
    ↓
Application artefact
    ↓
Evidence / reasoning output
```

This chain ensures that commercial concept meaning remains aligned from CBOK standards through ontology files, SDK implementation, graph representation, application use and reasoning evidence.
