# CIOS Reference Architecture v1.0

**Purpose:** Define the single authoritative architecture entry point for CIOS.  
**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-11

## Executive Summary

CIOS is an Enterprise Intelligence platform that constructs Commercial Digital Twins of organisations, reasons over evidence-backed observations, and recommends commercially valuable actions.

CIOS is not a CRM.  
CIOS is not a BI dashboard.  
CIOS is not a scraper.  
CIOS is not a reporting tool.

CIOS exists to answer:

1. What changed?
2. Why did it change?
3. Why does it matter?
4. What will probably happen next?
5. What should we do?

The Reference Architecture is the top-level navigation, philosophy, taxonomy and governance document for CIOS. It explains how the Founding Papers, CIRM, Enterprise Intelligence papers and Flora runtime relate without replacing their detailed authority.

## The CIOS Philosophy

CIOS detects change.  
Evidence proves change.  
Observations remember change.  
Enterprise Models accumulate change.  
Signals explain change.  
Hypotheses challenge change.  
Commercial reasoning evaluates change.  
Recommendations propose action.  
Learning improves future reasoning.

## The First Principles of CIOS

1. CIOS detects meaningful enterprise change.
2. Evidence is proof, not intelligence.
3. Observations are the atomic unit of Enterprise Intelligence.
4. Enterprise Models are durable memory.
5. Every material claim must be traceable.
6. Unknowns and contradictions are first-class objects.
7. Commercial reasoning must distinguish fact, inference, hypothesis and recommendation.
8. Recommendations should maximise learning before selling.
9. Human expertise calibrates the model but must be labelled.
10. The platform should become more valuable as enterprise memory deepens.



## Architecture v2.0 pillars

Architecture v2.0 organises CIOS around four architectural pillars:

1. **Enterprise Intelligence** — the evidence-backed modelling discipline for Enterprise Models, Enterprise Knowledge Graphs, Observations, behaviour, commercial reasoning and hypothesis validation. EI-001 owns the Enterprise Model, EI-002 owns graph structure, EI-003 owns behaviour semantics and EI-012 owns Observation lifecycle.
2. **Commercial Digital Twins** — governed enterprise, industry, market-participant, opportunity and relational twins that hold durable state and make change inspectable. Twin state is canonical only when accepted through the owning model process.
3. **Presentation Intelligence** — Twin Presentation Models and related views that render governed knowledge for review, navigation and executive understanding. Presentation payloads are interpretation unless their claims are separately accepted by the canonical owner.
4. **Knowledge Exchange Architecture** — Knowledge Packs, Knowledge Assets, Knowledge Repository handling and the Knowledge Supply Chain governed by ADR-016, FP-010, FP-011, EI-013 and the v1.0 specifications.

The principal Architecture v2.0 flow is:

```text
Observable Reality
→ Sources
→ Evidence
→ Observations
→ Enterprise Models
→ Commercial Digital Twins
→ Presentation Models
→ Knowledge Packs
→ Flora
→ Executive action and learning
```


### Architecture v2.0 intelligence domains

**Enterprise Intelligence** is the governed discipline that turns evidence-backed Observations into durable Enterprise Models, graph state, behaviour state, commercial reasoning and learning. It owns canonical meaning through EI-001, EI-002, EI-003, EI-012 and related Enterprise Intelligence papers.

**Commercial Digital Twins** are governed, time-aware representations of commercially relevant reality. The v2.0 twin taxonomy includes:

- **Enterprise Twin** — durable model of a monitored enterprise and its leadership, economics, operations, technologies, pressures, behaviours, opportunities and relationships.
- **Industry Twin** — durable model of industry structure, change, demand, regulation, participant movement and common transformation pressure.
- **Market Participant Twin** — durable model of a supplier, competitor, partner or other participant in a market, including role, capabilities, account-relative strengths, weaknesses, fit, access, incumbent position and supporting evidence.
- **Opportunity Twin** — durable model of a specific potential commercial opportunity, including need, timing, route to market, blockers, hypotheses, conviction and next best learning action.
- **Relational Twin** — durable model of relationships between enterprises, executives, suppliers, partners, competitors, programmes, contracts and opportunities.

**Presentation Intelligence** is governed interpretation for human consumption. Presentation Models, including Twin Presentation Models, explain and render what the system understands, but they are not canonical fact unless their claims are separately accepted by the owning model process.

**Knowledge Exchange Architecture** is the exchange boundary for portable intelligence. Knowledge Packs package Knowledge Assets, Presentation Models, lineage and metadata for validation, repository handling, rendering, comparison and distribution without silently mutating canonical memory.

### Cross-Twin intelligence and change flow

Commercial advantage compounds when CIOS compares Twins rather than repeatedly reconstructing single-account context. Cross-Twin intelligence compares Enterprise, Industry, Market Participant, Opportunity and Relational Twins to identify patterns, contradictions, role changes, account-relative strengths and weaknesses, participant fit, opportunity adjacency and portfolio-level learning.

The **Industry Change Queue** is the governed queue of material industry events, weak signals, participant moves, regulation, demand shifts and contradictions awaiting triage against Industry Twins and affected Enterprise, Market Participant, Opportunity and Relational Twins. It supports continuous monitoring, weekly triage, monthly release, quarterly assurance and event-driven review as documented lifecycle cadences; these cadences are documentation commitments, not runtime implementation in this reference update.

An **account–participant assessment** compares a Market Participant Twin against an Enterprise Twin or Opportunity Twin. It must distinguish supplier, competitor and partner roles; account-relative strengths and weaknesses; relationship access; incumbent position; provider fit; evidence quality; Unknowns; and Contradictions.

### GPT, Flora and canonical-memory responsibility split

GPT and other generative providers may create candidate intelligence, including draft Twin releases, Presentation Models and Knowledge Packs. Their output remains candidate interpretation until governed validation and acceptance occur.

Flora is responsible, as target architecture, for Knowledge Repository handling, Knowledge Pack validation, Twin Registry lookup, Presentation rendering, lineage services, release and comparison services, change queues and Cross-Twin Intelligence workflows. Flora governs, versions, renders, compares and compounds accepted packages and models; it does not convert interpretation into fact merely because it accepted, rendered or distributed a package.

Flora-native AI should focus preferentially where accumulated context creates advantage: cross-Twin intelligence, release comparison, change detection, account–participant assessment and learning across accepted Knowledge Packs.

### Runtime reasoning boundary

Account-level runtime reasoning remains permitted. It is optional when an accepted Presentation Model already exists for the intended executive view. Runtime reasoning output must never silently mutate canonical Enterprise Models, graph state, behaviour state or Observations; canonical writes require the owning model acceptance process.

This flow extends rather than replaces CIRM. FP-009 continues to govern hypothesis validation and inspectable recommendation lineage. Knowledge Pack acceptance means the package is valid for repository handling; it does not silently promote contained claims into EI-001 Enterprise Models, EI-002 graph state, EI-003 behaviour state or EI-012 Observations. Flora may later validate, version, store, render and distribute accepted Knowledge Packs, but this reference update is documentation-only and does not implement Flora runtime functionality.

## Progressive Assurance operating modes

ADR-009 defines how CIOS applies assurance proportionately while preserving architectural invariants.

### Initial Decision Twin

The default mode for creating or refreshing a Commercial Digital Twin. It requires durable model state, material-claim lineage, visible uncertainty and decision-useful reasoning. It does not require a formal publication package.

### Assured Release

An explicit promotion mode for external publication, provider-specific pursuit, sponsor outreach or other high-consequence reliance. It adds deeper review, reconciliation, release validation and owner acceptance.

### Architectural boundary

Flora creates and updates governed Twin state. Publisher renders views and formal releases from that state. Reports, manifests and release packages remain conditional views and controls; they are not durable memory and are not prerequisites for an Initial Decision Twin.

Assurance increases with the strength, audience and consequence of the proposed action. Core Observation, Enterprise Model, lineage, uncertainty and human-knowledge rules apply in both modes.


## CIOS Architecture Layers

### 1. Source and Evidence Layer

- **Purpose:** Collect permissible, attributable and quality-assessed evidence about observable enterprise reality.
- **Major objects:** source, source tier, evidence item, evidence acquisition plan, source quality score, freshness marker, collection handbrake.
- **Related architecture papers:** FP-004 Evidence Acquisition Standard, FP-005 Enterprise Intelligence Collection Framework, FP-006 Source Quality Standard.
- **Future runtime implications:** Flora collection should remain governed by source boundaries, evidence acceptance rules, quality scoring and recovery logic before downstream reasoning begins.

### 2. Observation Layer

- **Purpose:** Convert accepted evidence into reusable memory atoms that preserve what changed, when it changed, why it is credible and what remains unknown.
- **Major objects:** Observation, Observation Demand, observed attribute, evidence link, confidence, contradiction, unknown, decay and half-life.
- **Related architecture papers:** EI-012 Enterprise Observation Model, FP-003 Flora Intelligence Architecture, FP-004 Evidence Acquisition Standard.
- **Future runtime implications:** Runtime reasoning should prefer Observations over direct raw-evidence reasoning wherever an Observation can be created.

### 3. Enterprise Model Layer

- **Purpose:** Maintain the durable Commercial Digital Twin for each monitored enterprise.
- **Major objects:** Enterprise Model, enterprise profile, leadership, financial performance, operating model, technology estate, transformation portfolio, supplier ecosystem, procurement activity and opportunity outlook.
- **Related architecture papers:** EI-001 Enterprise Model Specification, EI-003 Enterprise Behaviour Model, EI-011 Enterprise Economics Model.
- **Future runtime implications:** Flora should update stable Enterprise Models rather than treating reports or evidence packets as durable memory.

### 4. Enterprise Knowledge Graph Layer

- **Purpose:** Connect enterprise entities, relationships, attributes and evidence-backed edges so CIOS can reason across people, organisations, contracts, suppliers, technologies and transformation themes.
- **Major objects:** node, edge, relationship, evidence-backed edge, inferred edge, human-supplied edge, temporal edge, contradiction.
- **Related architecture papers:** EI-002 Enterprise Knowledge Graph, EI-007 Executive Intelligence Model, EI-012 Enterprise Observation Model.
- **Future runtime implications:** Queryable graph structures should support temporal reasoning, contradiction handling, relationship lineage and cross-enterprise pattern discovery.

### 5. Behaviour and Dynamics Layer

- **Purpose:** Explain how an enterprise behaves over time under pressure, momentum, weather, economics and operating constraints.
- **Major objects:** enterprise behaviour, Enterprise Weather, Transformation Pressure, Transformation Inevitability, Enterprise Momentum, Enterprise Economics.
- **Related architecture papers:** EI-003 Enterprise Behaviour Model, EI-008 Enterprise Weather Model, EI-009 Transformation Pressure Model, EI-010 Enterprise Momentum Model, EI-011 Enterprise Economics Model.
- **Future runtime implications:** Runtime scoring should distinguish temporary noise from durable behavioural direction and should preserve pressure, momentum and economic context separately.

### 6. Commercial Reasoning Layer

- **Purpose:** Convert Observations, Signals and model state into commercial interpretation while distinguishing fact, inference, hypothesis, thesis and recommendation.
- **Major objects:** Strategic Signal, Commercial Insight, Pattern, Hypothesis, Commercial Thesis, Commercial Conviction, reasoning lineage.
- **Related architecture papers:** FP-007 Strategic Signal Standard, FP-008 Commercial Conviction Model, FP-009 Hypothesis Validation Standard, EI-004 Commercial Reasoning Framework.
- **Future runtime implications:** Newton-style reasoning should expose inspectable lineage and should not create recommendations without visible evidence and hypothesis logic.

### 7. Prediction and Opportunity Layer

- **Purpose:** Estimate what is likely to happen next and where commercially valuable action may exist.
- **Major objects:** Transformation Prediction, Opportunity Prediction, opportunity outlook, likelihood, timing, access path, blocker, next best learning action.
- **Related architecture papers:** EI-005 Transformation Prediction Model, EI-006 Opportunity Prediction Engine, FP-008 Commercial Conviction Model.
- **Future runtime implications:** Opportunity prediction should separate enterprise need from commercial accessibility and should prioritise learning actions before sales actions.

### 8. Executive Intelligence Layer

- **Purpose:** Understand executive actors, governance, ownership, decision influence and relationship context.
- **Major objects:** executive profile, role, mandate, influence, sponsor, detractor, relationship edge, executive recommendation.
- **Related architecture papers:** EI-007 Executive Intelligence Model, architecture research on Executive Ownership, future People and Executive Intelligence Source Standard.
- **Future runtime implications:** Executive intelligence should be evidence-backed or explicitly human-supplied, with role freshness and lineage visible.

### 9. Runtime and Product Layer

- **Purpose:** Operationalise CIOS architecture through user-facing and internal systems such as Flora, Newton, Observatory and Publisher.
- **Major objects:** runtime workflow, research workspace, evidence library, executive view, report, briefing, product surface, runtime compliance check.
- **Related architecture papers:** FP-003 Flora Intelligence Architecture, docs/Architecture/CIRM_Runtime_Compliance.md, Flora runtime alignment and product maturity documents.
- **Future runtime implications:** Product surfaces should be views over evidence, Observations, Enterprise Models and reasoning lineage rather than independent memory stores.

### 10. Learning and Feedback Layer

- **Purpose:** Improve future evidence collection, Observation creation, reasoning and recommendations from outcomes, human calibration and failed hypotheses.
- **Major objects:** feedback, outcome, learning event, rejected hypothesis, source yield, model calibration, Curiosity Engine prompt.
- **Related architecture papers:** future EI-013 Enterprise Learning Model, future EI-016 Enterprise Curiosity Engine, FP-009 Hypothesis Validation Standard.
- **Future runtime implications:** CIOS should learn which sources, Observations, patterns and recommendations improved commercial judgement and which should decay or be retired.

## CIRM — CIOS Intelligence Reference Model

CIRM defines how CIOS reasons. It is the reference model that turns observable enterprise reality into strategic commercial judgement.

Canonical CIRM chain:

```text
Observable Enterprise Reality
→ Governed Source Collection
→ Raw Evidence
→ Evidence Quality Assessment
→ Observation
→ Strategic Signal
→ Commercial Insight
→ Transformation Theme
→ Transformation Thesis / Hypothesis
→ Hypothesis Validation
→ Commercial Conviction
→ Executive Recommendation
→ Commercial Outcome
→ Continuous Learning
```

The Founding Papers FP-003 to FP-009 define the core CIRM volumes. The canonical chain requires an Observation between accepted Evidence and Strategic Signal wherever an Observation can be created. Observation Networks and Patterns may aggregate multiple Observations during reasoning, but they are optional reasoning structures rather than mandatory stages for every individual Observation.

Inspectable recommendation lineage uses the reverse chain:

```text
Executive Recommendation
→ Commercial Conviction
→ Hypothesis or Transformation Thesis
→ Commercial Insight
→ Strategic Signal
→ Observation
→ Raw Evidence
→ Source
```

### Volume I — Observation

- FP-003 Flora Intelligence Architecture
- FP-004 Evidence Acquisition Standard
- FP-005 Enterprise Intelligence Collection Framework
- FP-006 Source Quality Standard

Volume I defines how CIOS observes reality, collects evidence and assesses whether that evidence is usable.

### Volume II — Reasoning

- FP-007 Strategic Signal Standard
- FP-008 Commercial Conviction Model
- FP-009 Hypothesis Validation Standard

Volume II defines how CIOS interprets evidence-backed change, validates hypotheses and decides whether commercial action is justified.

## Enterprise Intelligence Architecture

Enterprise Intelligence defines what CIOS knows about an enterprise.

CIRM = how CIOS reasons.  
Enterprise Intelligence = what CIOS knows.  
Flora = first runtime implementation.

A Commercial Digital Twin is the evidence-backed, time-aware, confidence-scored, contradiction-aware model of a monitored enterprise.

### Enterprise Intelligence series

#### Volume 1 — Enterprise Modelling

- EI-001 Enterprise Model Specification
- EI-002 Enterprise Knowledge Graph
- EI-003 Enterprise Behaviour Model

#### Volume 2 — Commercial Intelligence

- EI-004 Commercial Reasoning Framework
- EI-005 Transformation Prediction Model
- EI-006 Opportunity Prediction Engine

#### Volume 3 — Human Intelligence

- EI-007 Executive Intelligence Model

#### Volume 4 — Enterprise Dynamics

- EI-008 Enterprise Weather Model
- EI-009 Transformation Pressure Model
- EI-010 Enterprise Momentum Model
- EI-011 Enterprise Economics Model

#### Volume 5 — Intelligence Foundations

- EI-012 Enterprise Observation Model
- EI-013 Enterprise Learning Model future
- EI-014 Commercial Conversation Model future
- EI-015 Enterprise Question Model future
- EI-016 Enterprise Curiosity Engine future

## Observation Doctrine

EI-012 defines the Enterprise Observation Model: the reusable intelligence atom between evidence acquisition and higher-order reasoning.

Evidence is proof.  
Observation is memory.  
Signal is meaning.  
Hypothesis is interpretation.  
Recommendation is action.

CIOS should not reason directly over raw evidence where an Observation can be created. Raw evidence proves that something was observed; an Observation turns that proof into durable, traceable and reusable enterprise memory.

## Commercial Digital Twin

The Commercial Digital Twin is the central Enterprise Intelligence object. It is not a static profile or report; it is the maintained model that accumulates enterprise change and supports commercial judgement.

It should contain:

- enterprise identity;
- enterprise profile;
- leadership;
- board and governance;
- financial performance;
- enterprise economics;
- operating model;
- technology estate;
- transformation portfolio;
- supplier ecosystem;
- procurement activity;
- competitive position;
- regulatory/political environment;
- people/workforce signals;
- relationship graph;
- enterprise behaviour;
- transformation pressure;
- transformation inevitability;
- commercial conviction;
- opportunity outlook.

## Enterprise Knowledge Graph

The Enterprise Knowledge Graph gives CIOS structure across enterprise memory. It:

- connects entities;
- stores evidence-backed edges;
- supports inferred and human-supplied edges;
- preserves contradictions;
- supports temporal reasoning;
- enables queries.

Example query patterns:

- Which enterprises have rising cost pressure and a new CFO?
- Which contracts expire in the next 18 months?
- Which enterprises show high Transformation Pressure but low procurement evidence?
- Which executives own transformation themes?
- Which opportunities are blocked by incumbent contracts?

## Flora Runtime Role

Flora is the first CIOS runtime that operationalises evidence acquisition, observation creation, enterprise modelling, commercial reasoning and executive intelligence.

Runtime roles are architectural rather than final branding if product names change.

### Flora

- collects evidence;
- creates Observations;
- updates Enterprise Models;
- renders executive views;
- manages research and evidence libraries.

### Newton

- commercial reasoning and opportunity shaping engine.

### Observatory

- cross-enterprise market and transformation pattern view.

### Publisher

- briefing and report generation.

## Governance and Trust

CIOS architecture depends on trust. Runtime capabilities should preserve:

- traceability;
- confidence;
- freshness;
- decay;
- contradiction handling;
- human-supplied knowledge labelling;
- public/permissible source boundaries;
- privacy and ethics;
- rejection of unsupported inference;
- no recommendation without inspectable reasoning lineage.

## Architecture Compliance

Architecture compliance should become a future runtime and PR governance mechanism. Every significant runtime PR should answer:

- Which architecture papers apply?
- Which principles are implemented?
- Which are partially implemented?
- Which are deferred?
- Does this introduce new terminology outside the Reference Architecture?
- Does this improve traceability?
- Does this improve commercial judgement?
- Does this preserve evidence lineage?
- Does this reduce unsupported inference?

## Maturity Model

### Level 0 — Evidence Collector

CIOS can collect and store evidence. Capability is limited to acquisition and attribution; intelligence remains mostly manual.

### Level 1 — Evidence Intelligence Platform

CIOS can assess evidence quality, freshness and relevance. Limitations remain because evidence is not yet durable enterprise memory.

### Level 2 — Enterprise Model Platform

CIOS maintains Enterprise Models. It can accumulate profile, operating and commercial knowledge, but prediction and graph reasoning remain limited.

### Level 3 — Commercial Digital Twin Platform

CIOS maintains evidence-backed, time-aware and contradiction-aware Commercial Digital Twins. It can support richer executive views and account planning, but prediction is still emerging.

### Level 4 — Predictive Enterprise Intelligence Platform

CIOS reasons over pressure, momentum, economics and opportunity signals to predict likely enterprise change and commercial opportunity. Human validation remains central.

### Level 5 — Autonomous Business Development Partner

CIOS recommends learning, engagement and action plans while continuously improving from outcomes. It remains governed by traceability, human calibration and source boundaries.

## Strategic Roadmap

- **Phase 1 — Architecture foundation complete.** Consolidate the Founding Papers, EI papers and Reference Architecture.
- **Phase 2 — Flora runtime alignment with CIRM.** Align evidence, signal, hypothesis and conviction flows to the reference chain.
- **Phase 3 — Build Enterprise Model runtime.** Make Enterprise Models durable runtime memory.
- **Phase 4 — Add Observation Engine.** Create and manage Observations as intelligence atoms.
- **Phase 5 — Add Enterprise Knowledge Graph.** Connect enterprise entities, edges and contradictions.
- **Phase 6 — Add Commercial Reasoning and Opportunity Prediction.** Shape Newton-style reasoning, conviction and opportunity outlook.
- **Phase 7 — Add Executive Conversation and Account Planning.** Turn intelligence into explainable commercial dialogue and account plans.
- **Phase 8 — Add Learning and Curiosity Engine.** Improve collection, reasoning and recommendations from outcomes and unknowns.

## Research Agenda

Future papers and specifications:

- EI-013 Enterprise Learning Model
- EI-014 Commercial Conversation Model
- EI-015 Enterprise Question Model
- EI-016 Enterprise Curiosity Engine
- Commercial Digital Twin Runtime Specification
- Enterprise Model Data Contract
- Observation Engine Runtime Design
- Source Discovery and Recovery Architecture
- Procurement Intelligence Architecture
- People and Executive Intelligence Source Standard

## Closing Statement

CIOS exists to convert observable enterprise reality into strategic commercial judgement.

Every capability should help CIOS detect, understand, explain, predict or act on meaningful enterprise change.
