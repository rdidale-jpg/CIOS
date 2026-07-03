# CIOS AI Session Handoff

**Status:** Living briefing
**Owner:** Rob / CIOS
**Last updated:** 2026-07-03

## Purpose

This document provides a short copy/paste briefing for starting new ChatGPT or Codex sessions. It should help future assistants understand CIOS without relying on prior chat history.

## 1. Project summary

CIOS is an Enterprise Intelligence platform that detects meaningful enterprise change, builds Commercial Digital Twins, reasons over Observations and recommends commercially valuable action.

CIOS is designed to help users understand what changed in an enterprise, why it changed, why it matters, what may happen next and what action should be taken.

## 2. Current architecture summary

The CIOS Reference Architecture is the main entry point. It connects:

- Founding Papers, which define CIRM and the intelligence process;
- Enterprise Intelligence papers, which define what CIOS knows about enterprises;
- Flora runtime documents, which describe the first operational implementation;
- ADRs, which record important architecture decisions and trade-offs.

CIRM defines how CIOS reasons. Enterprise Intelligence defines what CIOS knows. Flora operationalises both.

## 3. Core doctrine

- CIOS detects change.
- Evidence proves change.
- Observations remember change.
- Enterprise Models accumulate change.
- Signals explain change.
- Hypotheses challenge change.
- Commercial reasoning evaluates change.
- Recommendations propose action.
- Learning improves future reasoning.

## 4. Current runtime state

Flora is the first CIOS runtime. It currently has strong report, briefing, live evidence and pilot workspace foundations. The architecture direction is to evolve Flora beyond report generation toward a runtime that maintains living Commercial Digital Twins.

Future runtime work should avoid treating reports as memory. Reports should become views over Observation-backed Enterprise Model state.

## 5. Near-term roadmap

The near-term strategic runtime direction is:

1. establish an Observation Engine;
2. persist Observations as reusable intelligence atoms;
3. update Enterprise Models / Commercial Digital Twins from Observations;
4. preserve evidence lineage from Source to Recommendation;
5. generate reports, briefings and recommendations as views over maintained model state;
6. introduce curiosity loops that turn unknowns, contradictions and weak evidence into evidence demand.

## 6. How to ask the AI to behave

Use this ready-to-copy prompt when starting a new AI session:

```text
You are helping develop CIOS, an Enterprise Intelligence platform. Before responding, follow CIOS-AI.md and the Reference Architecture. Treat Observations as the intelligence atom, Enterprise Models as durable memory, and reports as views. Challenge unsupported claims, preserve uncertainty and produce Codex-ready prompts in fenced code blocks.
```
