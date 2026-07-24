# Research Mission Template

**Document ID:** TEMPLATE-Industry-Research-Pack  
**Status:** Approved operational artefact  
**Owner:** CIOS Research Operations  
**Version:** 2.4.0

## Purpose

Provide the canonical Research Mission template for long-running Industry Twin and Enterprise Intelligence research without creating new doctrine or a new Twin type.

## Mission identity

- Mission identifier
- Title
- Owner
- Objective
- Scope
- Exclusions

## Governing architecture

Declare the governing sources for the mission:

- RG-001 for research methodology and research behaviour;
- RG-002 for Research Mission Workspace operation, persistence, checkpointing, recovery, escalation, mission outcomes and evidence exhaustion;
- applicable Twin specifications, including Enterprise Twin, Industry Twin and Market Participant Twin specifications where relevant;
- applicable Accepted ADRs and Founding Papers, including ADR-016, FP-010 and the Knowledge Pack Specification for package exchange.

## Workspace

- Create a Research Mission Workspace when no validated Workspace exists, or load the latest validated Workspace when one exists.
- Treat the latest validated Workspace as authoritative operational state independent of chat history.
- Use the existing governed Knowledge Pack exchange mechanism for the downloadable Research Mission Workspace Package; do not invent a parallel archive format.
- Checkpoint after every Research Wave, after material Twin or maturity changes, before anticipated interruption, when requested, and before terminal assessment.

## Required Workspace components

The Workspace must include, where applicable: Mission metadata; Candidate Twin; Enterprise Twin Register; Enterprise Twins; Market Participant Register; Market Participant Twins; Control Body Twins only where semantics already exist; Transformation Portfolio; Relationship Model; Evidence Register; Unknown Register; Contradiction Register; Executive Insight Register; Coverage Matrix; Maturity Matrix; Research Queue; Mission Journal; Escalation Register; Evidence Saturation Assessment; and Restart Conditions.

## Completion gates

Declare explicit gates for:

- breadth;
- depth;
- evidence quality and lineage;
- relationship coverage;
- maturity;
- Executive Insight usefulness and explainability.

## Research strategy

Operate through repeated Research Waves. After each checkpoint select the highest-value eligible Research Queue item by considering unresolved completion gates, strategic significance, commercial significance, Executive Insight value, maturity impact, relationship impact, dependency reduction, evidence quality, evidence availability, contradiction resolution, risk of unsupported conclusions and mission relevance.

Define the permitted and reasonably discoverable evidence universe, including applicable source classes such as official publications, annual reports or accounts, strategies, budgets, parliamentary or legislative material, audit and assurance reports, procurement and contract records, programme updates, operational data, leadership statements, technical publications, supplier disclosures, specialist analysis, credible news, archives and corroborating adjacent evidence.

## Escalation behaviour

Record external dependencies, inaccessible evidence, authority needs, decision needs and irresolvable material conflicts in the Escalation Register. Escalation is explicitly non-terminal: continue unaffected work and never globally block the mission while productive research remains elsewhere.

## Evidence exhaustion

Apply the strict RG-002 EVIDENCE EXHAUSTED test. Evidence exhaustion requires all applicable permitted source classes, query variations, aliases, primary routes, secondary routes, adjacent routes, contradictory evidence and unaffected research to have been explored, with no material new understanding from successive waves. Record unmet gates, maximum evidenced maturity, remaining Unknowns, open escalations, routes attempted, affected claims, consequences and restart conditions.

Technical interruption, context pressure, task size, execution duration, tool failure, rate limits, file-generation failure, one inaccessible source, open escalations or difficulty finding evidence are resumable conditions and are never evidence exhaustion.

## Outputs

- Latest validated Research Mission Workspace Package.
- Candidate Twin or bounded incomplete release where appropriate, using existing canonical Twin semantics.
- Concise mission-state summary identifying current outcome, completion-gate status, maturity and coverage, open Unknowns, contradictions, escalations, evidence saturation, progress since prior checkpoint, and next highest-value priority with rationale.

## Required lineage fields

- Source path or URL
- Evidence identifier
- Observation identifier
- Enterprise Model object
- Knowledge Graph relationship, where applicable
- Confidence
- Freshness
- Human-validation state
- Unknowns
- Contradictions

## Content separation

Record facts, inference, Hypotheses and Recommendations in separate sections. No strong Recommendation may exist without inspectable lineage.
