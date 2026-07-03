# CIOS AI Session Handoff

**Status:** Living briefing
**Owner:** Rob / CIOS
**Last updated:** 2026-07-03

## Purpose

This document provides a short copy/paste briefing for starting new ChatGPT or Codex sessions. It should help future assistants understand CIOS without relying on prior chat history.

## Paste this into a new chat

```text
You are helping develop CIOS, an Enterprise Intelligence platform. Read CIOS-AI.md and the Reference Architecture first. CIOS detects meaningful enterprise change, builds Commercial Digital Twins, reasons over Observations and recommends commercially valuable action. Evidence is proof, Observation is memory, Signal is meaning, Hypothesis is interpretation, Recommendation is action. Challenge unsupported claims, preserve unknowns, label human-supplied knowledge and produce Codex-ready prompts in fenced code blocks.
```

## Current project state

Flora is the first CIOS runtime. It has useful report, briefing, live evidence and pilot workspace foundations, but the architecture direction is to move beyond report generation toward living Commercial Digital Twins.

Reports should become views over Observation-backed Enterprise Model state. Future work should strengthen Observations, durable memory, lineage, model-backed recommendations and learning from unknowns.

## Latest strategic decision

The latest strategic decision is that the portable project memory now lives in CIOS-AI.md, the Reference Architecture and Accepted ADRs. Accepted ADRs ADR-001 to ADR-005 define the current architecture constraints for Observations, Enterprise Model memory, CIRM/EI separation, human-supplied knowledge and recommendation lineage.

## Next likely sprint

The next likely runtime sprint is to begin aligning Flora with the Observation Engine and Enterprise Model runtime direction: create reusable Observations, persist durable enterprise state, link model updates to evidence and expose reports as views over maintained memory.

## Where to find architecture documents

Start here:

1. [CIOS AI Context](../../CIOS-AI.md)
2. [Reference Architecture README](README.md)
3. [CIOS Reference Architecture v1.0](CIOS-Reference-Architecture-v1.0.md)
4. [CIOS Design Doctrine](CIOS-Design-Doctrine.md)
5. [Document Map](Document-Map.md)
6. [ADR README](../decisions/README.md)

Use Founding Papers for CIRM process standards and Enterprise Intelligence papers for the Commercial Digital Twin model.

## How to review uploaded output documents

When Rob uploads generated reports, case files, briefings or workspace exports, review them against CIOS doctrine:

- identify whether claims are evidence-backed or inferred;
- look for missing Observation, Signal, Hypothesis and Recommendation lineage;
- preserve unknowns and contradictions instead of smoothing them away;
- flag repetition and generic executive language;
- check whether human-supplied knowledge is labelled;
- recommend architecture-aligned improvements rather than only copy edits.

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
