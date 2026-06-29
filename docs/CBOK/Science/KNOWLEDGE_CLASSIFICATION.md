# Knowledge Classification

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-SCI-001-CLASS |
| Title | Knowledge Classification |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Purpose

This document defines the formal knowledge classes used by CBOK-SCI-001. Each material CBOK knowledge statement should be assigned one primary class and may reference related classes when appropriate.

## Knowledge Classes

| Class | Definition | Purpose | Required Evidence | Typical Lifecycle | Example | Related CBOK Artefacts |
|---|---|---|---|---|---|---|
| Observation | A recorded fact, event, measurement or practitioner-noted occurrence in a stated context. | Capture raw or interpreted signals for later evaluation. | Provenance, context, date or period and observer or source. | Idea → Observation → Claim or Archived. | Sales teams report that onboarding friction increased after a workflow change. | Evidence records, claims, experiments. |
| Claim | A declarative statement that asserts something may be true. | Provide a reviewable unit of knowledge. | At least one observation, source or rationale; confidence may be low. | Observation → Claim → Working Paper or Archived. | Shorter response times may improve buyer trust in renewal workflows. | Working papers, hypotheses, review records. |
| Definition | A controlled meaning assigned to a term. | Ensure consistent terminology across CBOK and engineering. | Authoritative source, governance decision or accepted internal usage. | Claim → Candidate Artefact → Approved Artefact → Standard. | Operational Confidence means readiness for governed operational use. | Glossaries, standards, reference models. |
| Principle | A durable normative rule or design commitment. | Guide decisions and reviews where detailed procedures are absent. | Evidence, doctrine or governance rationale proportionate to impact. | Working Paper → Candidate Artefact → Approved Artefact → Standard. | Claims shall remain proportionate to evidence. | Standards, review checklists, engineering guidance. |
| Pattern | A repeatable solution or recurring structure observed across contexts. | Support reuse without overclaiming universality. | Multiple observations or cases showing recurrence and constraints. | Observation → Working Paper → Validation Report → Approved Artefact. | A staged adoption pattern reduces risk for new recommendation models. | Reference models, engineering standards, playbooks. |
| Hypothesis | A falsifiable proposition intended for testing. | Direct research, experiments and validation plans. | Clear variables, expected relationship, scope and evidence rationale. | Literature Review → Hypothesis → Experiment → Validation Report. | If explanation quality improves, adoption of recommendations increases. | Experiments, validation reports. |
| Model | A structured representation of entities, relationships, behaviours or mechanisms. | Enable explanation, analysis, simulation, prediction or implementation. | Definitions, assumptions, validation evidence and limits. | Hypothesis → Validation Report → Candidate Artefact → Approved Artefact. | A trust formation model linking transparency, consistency and adoption. | Reference models, standards, engineering specifications. |
| Law | A durable relationship repeatedly observed across commercial contexts. | Establish a stable constraint or expectation for science and engineering. | Strong repeated evidence, limits, counterevidence review and governance approval. | Validation Report → Candidate Artefact → Approved Artefact → Standard. | A documented invariant relating friction and conversion within defined bounds. | Law registry, standards, engineering constraints. |
| Framework | An organising structure for concepts, processes or evaluation. | Coordinate multiple artefacts into a coherent system. | Definitions, rationale, reviewed scope and traceability. | Working Paper → Candidate Artefact → Approved Artefact → Standard. | CBOK-SCI-001 Scientific Knowledge Framework. | Standards, governance processes, checklists. |
| Standard | A normative controlled document that establishes required or recommended practice. | Create authoritative obligations for authors, reviewers or engineering consumers. | Approved rationale, traceability, review history and confidence assessment. | Candidate Artefact → Approved Artefact → Standard. | A standard requiring evidence levels for knowledge promotion. | Engineering standards, CBOK standards. |
| Reference Model | A structured model intended as a common reference for analysis or implementation. | Align terminology, structure and downstream engineering mapping. | Model rationale, validation evidence, constraints and adoption guidance. | Model → Candidate Artefact → Approved Artefact → Standard. | A reference model for commercial actor decision states. | Models, standards, architecture documents. |
| Recommendation | A bounded advised action or interpretation based on evidence and context. | Guide decisions while preserving uncertainty and constraints. | Supporting claims, evidence level, confidence rating and applicability limits. | Claim → Candidate Artefact → Approved Artefact or Superseded. | Use controlled pilots before productionising unvalidated heuristics. | Review checklists, standards, operational guidance. |

## Classification Rules

- Authors shall choose the most specific class that matches the statement's role.
- A knowledge artefact must not be promoted solely by renaming it to a stronger class.
- Stronger classes such as Law, Standard and Reference Model require explicit evidence and review records.
- Related artefacts should be linked using stable CBOK identifiers.
