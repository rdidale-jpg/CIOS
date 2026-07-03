# CIOS AI Context

**Status:** Living document
**Owner:** Rob / CIOS
**Last updated:** 2026-07-03

## Purpose

This document defines how any AI assistant, Codex session or human contributor should work on CIOS. It preserves project memory, architecture doctrine and AI operating rules outside chat history.

## 1. What CIOS is

CIOS is an Enterprise Intelligence platform that detects meaningful enterprise change, builds Commercial Digital Twins, reasons over Observations and recommends commercially valuable action.

CIOS is not a generic scraping, dashboarding or report-generation system. It is designed to maintain durable enterprise memory, interpret change and support commercially useful decisions with inspectable evidence and reasoning lineage.

## 2. Core doctrine

- CIOS detects change.
- Evidence proves change.
- Observations remember change.
- Enterprise Models accumulate change.
- Signals explain change.
- Hypotheses challenge change.
- Commercial reasoning evaluates change.
- Recommendations propose action.
- Learning improves future reasoning.

## 3. Required reading order for AI agents

Before major work, read:

1. [`architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md`](architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md)
2. [`architecture/reference-architecture/Glossary.md`](architecture/reference-architecture/Glossary.md)
3. [`architecture/reference-architecture/Architecture-Principles.md`](architecture/reference-architecture/Architecture-Principles.md)
4. [`architecture/reference-architecture/Document-Map.md`](architecture/reference-architecture/Document-Map.md)
5. Relevant FP / EI / runtime documents
6. Relevant ADRs in [`architecture/decisions/`](architecture/decisions/)

## 4. AI operating rules

- Do not treat evidence as intelligence.
- Do not reason directly from raw scrape fragments where an Observation can be created.
- Do not create recommendations without traceable reasoning lineage.
- Do not introduce new terminology if an existing CIOS term exists.
- Preserve unknowns and contradictions.
- Label human-supplied knowledge.
- Prefer durable Enterprise Model updates over report-only output.
- Favour explainability over cleverness.
- Favour commercial judgement over volume.
- Challenge unsupported claims.

## 5. Architecture compliance expectations

Every meaningful implementation proposal should state:

- Which architecture documents apply.
- Which principles are implemented.
- Which are deferred.
- Whether terminology is compliant.
- How evidence lineage is preserved.
- How unsupported inference is prevented.

If a requested change conflicts with the Reference Architecture, a Founding Paper, Enterprise Intelligence paper or accepted ADR, identify the conflict before proposing implementation.

## 6. Output standards for Codex prompts

Codex-ready prompts should make the work inspectable and bounded:

- Documentation-only or runtime-changing scope must be explicit.
- Acceptance criteria must be included.
- Validation commands must be included.
- Commit and PR names must be included.
- Completion report requirements must be included.

## 7. Current strategic direction

The next major runtime goal is to move Flora from report generation to maintaining living Commercial Digital Twins, beginning with Observation Engine and Enterprise Model runtime.
