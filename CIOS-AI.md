# CIOS AI Context

**Status:** Living document
**Owner:** Rob / CIOS
**Last updated:** 2026-07-03

## Purpose

This document defines how any AI assistant, Codex session or human contributor should work on CIOS. It preserves project memory, architecture doctrine and AI operating rules outside chat history.

Treat this file, the Reference Architecture and Accepted ADRs as source of truth for CIOS project direction unless Rob explicitly changes the architecture. Treat the CIOS Chief Architect Handbook as the primary guide for judgement and working practice. Treat the Reference Architecture, Accepted ADRs and owning architecture papers as authoritative for detailed architecture and model decisions.

## One-page quick-start for AI agents

CIOS is an Enterprise Intelligence platform that detects meaningful enterprise change, builds Commercial Digital Twins, reasons over Observations and recommends commercially valuable action.

The current north-star is: **Move Flora from report generation to living Commercial Digital Twins.**

Before proposing work, ask whether the change improves durable enterprise memory, evidence-backed Observations, inspectable reasoning lineage and commercially useful action. If it only creates more output text, dashboards or summaries without improving memory or traceability, challenge the assumption.

## Mandatory reading order

Before major work, read in this order:

1. [`CIOS-AI.md`](CIOS-AI.md)
2. [`architecture/reference-architecture/README.md`](architecture/reference-architecture/README.md)
3. [`architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md`](architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md)
4. [`architecture/reference-architecture/CIOS-Design-Doctrine.md`](architecture/reference-architecture/CIOS-Design-Doctrine.md)
5. [`architecture/handbook/CIOS-Chief-Architect-Handbook.md`](architecture/handbook/CIOS-Chief-Architect-Handbook.md)
6. [`architecture/reference-architecture/Glossary.md`](architecture/reference-architecture/Glossary.md)
7. [`architecture/reference-architecture/Document-Map.md`](architecture/reference-architecture/Document-Map.md)
8. [`architecture/decisions/README.md`](architecture/decisions/README.md) and relevant Accepted ADRs
9. Relevant Founding Papers, Enterprise Intelligence papers and runtime documents

## What CIOS is

CIOS is not a generic scraping, dashboarding or report-generation system. It is designed to maintain durable enterprise memory, interpret change and support commercially useful decisions with inspectable evidence and reasoning lineage.

## Core doctrine

- CIOS detects change.
- Evidence proves change.
- Observations remember change.
- Enterprise Models accumulate change.
- Signals explain change.
- Hypotheses challenge change.
- Commercial reasoning evaluates change.
- Recommendations propose action.
- Learning improves future reasoning.

## Non-negotiable architecture rules

- Evidence is proof.
- Observation is memory.
- Enterprise Model is durable memory.
- Reports are views.
- No strong recommendation without lineage.
- Human knowledge must be labelled.

## AI operating rules

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

## Architecture compliance expectations

Every meaningful implementation proposal should state:

- which architecture documents apply;
- which Accepted ADRs apply;
- which principles are implemented;
- which are deferred;
- whether terminology is compliant;
- how evidence lineage is preserved;
- how unsupported inference is prevented.

If a requested change conflicts with the Reference Architecture, a Founding Paper, Enterprise Intelligence paper or Accepted ADR, stop and explain the conflict before proposing implementation.

## Codex prompt standards

Codex-ready prompts should be inspectable and bounded. Always include:

- mission;
- files in scope;
- constraints;
- acceptance criteria;
- validation;
- commit message;
- PR title;
- completion report.

Specify whether the task is documentation-only or runtime-changing. Put Codex prompts in fenced code blocks.

## Response style

AI assistants working on CIOS should:

- challenge weak assumptions;
- prefer architecture coherence over feature volume;
- reduce repetition;
- produce Codex prompts in fenced code blocks;
- use CIOS terminology consistently;
- keep uncertainty visible;
- avoid unsupported commercial claims.

## Current strategic direction

The next major runtime goal is to move Flora from report generation to maintaining living Commercial Digital Twins, beginning with Observation Engine and Enterprise Model runtime.
