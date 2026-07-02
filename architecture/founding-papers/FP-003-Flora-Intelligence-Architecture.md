# FP-003 — Flora Intelligence Architecture

**Purpose:** Establish the durable intelligence architecture for Flora as a CIOS application.  
**Status:** draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-02

## Source note

This Markdown version is intended to preserve the content and intent of `CIOS_Research_Paper_001_Flora_Intelligence_Architecture_Draft_v0_1.docx` as a clean architecture founding paper for the repository. The uploaded DOCX was not present in the working tree, so this document consolidates the Flora intelligence architecture already represented by the repository's Flora documentation and implementation direction.

## Abstract

Flora is the CIOS intelligence application for identifying organisations where AI-enabled reinvention may be timely, valuable and commercially actionable. Flora should not behave as a generic news summariser or opaque recommendation tool. Its purpose is to convert governed evidence into explainable commercial judgement: what appears to be changing, why it may matter, what is still unknown, and what action is justified.

## 1. Architecture thesis

Flora exists to reduce commercial uncertainty. It observes public and governed signals, relates them to transformation pressure, evaluates commercial fit, and produces recommendations that remain traceable to evidence and constraints.

The architecture is founded on five commitments:

1. **Evidence before opinion** — Flora should distinguish observed facts from hypotheses and recommendations.
2. **Explainability by design** — every score, priority and recommendation should expose its reasoning trail.
3. **Human accountability** — Flora supports executive judgement; it does not replace it.
4. **Governed intelligence** — Flora should prefer legitimate, source-specific and auditable evidence collection.
5. **Institutional learning** — user feedback and case history should improve future recommendations without erasing provenance.

## 2. Intelligence object model

Flora should reason across a small number of durable intelligence objects:

- **Organisation** — the enterprise, public body or target account being assessed.
- **Signal** — an observed event, statement or artefact that may indicate change.
- **Evidence receipt** — the traceable record of where a signal came from and how it was interpreted.
- **Pressure profile** — the set of internal and external forces that may create transformation urgency.
- **Capability gap** — a plausible gap between current state and required future capability.
- **Commercial hypothesis** — a testable belief about why engagement may be valuable.
- **Recommendation** — an action Flora suggests, with rationale, confidence and caveats.
- **Case file** — the living memory object that accumulates evidence, timeline, insights and actions for an organisation.

## 3. Signal architecture

Flora should treat signals as structured intelligence assets rather than free text. A signal should have at least:

- source identity;
- organisation;
- signal type;
- evidence tier;
- summary;
- observed date or publication date where available;
- interpretation;
- confidence;
- limitations;
- relationship to scoring or recommendation logic.

Signals should not automatically become recommendations. They become useful only when combined with sector context, capability logic, executive ownership, commercial fit and known evidence gaps.

## 4. Reasoning flow

Flora's default reasoning flow should be:

1. Collect or load governed evidence.
2. Classify evidence into signals.
3. Assess transformation pressure and commercial relevance.
4. Identify capability themes and possible executive owners.
5. Compare evidence strength against unknowns.
6. Generate ranked opportunities or attention items.
7. Explain why Flora believes each item matters.
8. State what Flora cannot yet know.
9. Recommend next actions that a human can validate.
10. Capture feedback in the living case file.

## 5. Explainability requirements

Flora outputs should expose:

- the evidence used;
- the signal types contributing to a view;
- score or ranking rationale;
- confidence and uncertainty;
- assumptions;
- missing evidence;
- recommended validation steps.

Where evidence is seeded, simulated or limited to a pilot source set, Flora must label it visibly.

## 6. Governance and constraints

Flora must avoid unsupported claims about private intent, budget, procurement, sponsorship or competitor engagement. Public evidence may justify hypotheses, but it does not prove internal decision-making.

Flora should avoid broad crawling and should respect source-specific access policies. Where live evidence is unavailable, deterministic seeded evidence may be used for local validation if clearly labelled.

## 7. Product surfaces

Flora may express the same intelligence architecture through multiple product surfaces:

- daily or weekly intelligence briefs;
- executive brief publications;
- portfolio radar views;
- living commercial case files;
- observatory views;
- teach-Flora feedback loops.

These surfaces should remain consistent with the same evidence, reasoning and governance model.

## 8. Relationship to CIOS

Flora is not a standalone application in architectural terms. It is an applied expression of CIOS principles:

- commercial ontology;
- commercial knowledge graph concepts;
- commercial reasoning language;
- commercial decision engine;
- agent-supported analysis;
- learning and memory.

Flora should therefore create reusable knowledge assets rather than isolated outputs.

## 9. Future expansion

Future versions should expand:

- live governed evidence coverage;
- sector and capability playbooks;
- executive ownership models;
- recommendation validation workflows;
- learning from user feedback;
- architecture-level traceability from founding papers to runtime behaviour.

## 10. Open questions

- Which signal categories should be promoted to formal CIOS standards?
- What minimum evidence threshold is required before Flora recommends action?
- How should human feedback alter confidence without compromising provenance?
- Which recommendations require ADR-level governance before implementation?
