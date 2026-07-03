# CIOS Architecture Maturity Model

**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-03

The maturity model describes how CIOS evolves from evidence collection into an autonomous business development partner while preserving traceability, evidence lineage and human-governed judgement.

## Level 0 — Evidence Collector

- **Description:** CIOS can collect and store attributable evidence from governed sources.
- **Capabilities:** source capture, evidence storage, basic provenance, manual review.
- **Limitations:** limited intelligence; no durable Enterprise Model; weak reasoning support.
- **Required architecture:** FP-004 Evidence Acquisition Standard, FP-005 Enterprise Intelligence Collection Framework, FP-006 Source Quality Standard.
- **Runtime indicators:** evidence libraries exist; source metadata is captured; quality gates are manual or basic.
- **Next step:** add evidence quality assessment and collection governance that support intelligence workflows.

## Level 1 — Evidence Intelligence Platform

- **Description:** CIOS can assess evidence quality, freshness, relevance and usefulness.
- **Capabilities:** source tiering, evidence acceptance, freshness scoring, collection handbrakes, evidence curation.
- **Limitations:** evidence is still not durable enterprise memory; repeated reasoning can be fragmented.
- **Required architecture:** FP-003 Flora Intelligence Architecture, FP-004, FP-005, FP-006.
- **Runtime indicators:** evidence quality scores are visible; rejected and downgraded evidence are tracked; source yield can be reviewed.
- **Next step:** create Observations and Enterprise Models so evidence becomes reusable memory.

## Level 2 — Enterprise Model Platform

- **Description:** CIOS maintains durable Enterprise Models for monitored organisations.
- **Capabilities:** enterprise identity, profile, leadership, financial, operating, technology and transformation fields; model freshness; attribute lineage.
- **Limitations:** graph reasoning, contradiction handling and opportunity prediction are still partial.
- **Required architecture:** EI-001 Enterprise Model Specification, EI-003 Enterprise Behaviour Model, EI-012 Enterprise Observation Model.
- **Runtime indicators:** stable enterprise records persist across reports; model fields link to evidence or Observations; stale attributes are visible.
- **Next step:** formalise the Commercial Digital Twin and connect entities through an Enterprise Knowledge Graph.

## Level 3 — Commercial Digital Twin Platform

- **Description:** CIOS maintains evidence-backed, time-aware, confidence-scored and contradiction-aware Commercial Digital Twins.
- **Capabilities:** Observation memory, contradiction preservation, relationship graph, behaviour and dynamics context, executive views.
- **Limitations:** prediction, opportunity shaping and learning remain assisted rather than mature.
- **Required architecture:** EI-001, EI-002 Enterprise Knowledge Graph, EI-007 Executive Intelligence Model, EI-008 to EI-012.
- **Runtime indicators:** graph queries answer relationship and timing questions; Observations update model state; contradictory claims are inspectable.
- **Next step:** add predictive reasoning over pressure, momentum, economics and commercial opportunity.

## Level 4 — Predictive Enterprise Intelligence Platform

- **Description:** CIOS predicts likely enterprise change and commercially relevant opportunities from model state and dynamics.
- **Capabilities:** transformation prediction, opportunity prediction, conviction scoring, next best learning action, executive recommendation support.
- **Limitations:** human validation and calibration remain central; conversation and learning loops are not fully autonomous.
- **Required architecture:** FP-007, FP-008, FP-009, EI-004 Commercial Reasoning Framework, EI-005, EI-006, EI-009, EI-010, EI-011.
- **Runtime indicators:** prediction outputs show evidence lineage, assumptions, confidence and blockers; opportunities distinguish need from accessibility.
- **Next step:** convert predictions into governed commercial conversations and feedback-driven learning.

## Level 5 — Autonomous Business Development Partner

- **Description:** CIOS recommends learning, engagement and action plans while improving from outcomes and human calibration.
- **Capabilities:** commercial conversation planning, account planning, curiosity-driven collection, outcome learning, adaptive source strategy.
- **Limitations:** autonomy remains bounded by ethics, privacy, permissible source rules and human-governed decision authority.
- **Required architecture:** future EI-013 Enterprise Learning Model, EI-014 Commercial Conversation Model, EI-015 Enterprise Question Model, EI-016 Enterprise Curiosity Engine.
- **Runtime indicators:** recommendations include inspectable reasoning lineage; feedback changes future collection and hypotheses; unknowns generate targeted questions.
- **Next step:** continuously govern, audit and improve model behaviour without weakening evidence standards.
