# CIOS AI Context

**Status:** Living document
**Owner:** Rob / CIOS
**Last updated:** 2026-07-21

## Purpose

This document defines how any AI assistant, Codex session or human contributor should work on CIOS. It preserves project memory, architecture doctrine and AI operating rules outside chat history.

Treat this file, the Reference Architecture, Accepted ADRs and the Architecture v2.0 Phase 1 authorities as source of truth for CIOS project direction unless Rob explicitly changes the architecture. Treat the CIOS Chief Architect Handbook as the primary guide for judgement and working practice. Treat the Reference Architecture, Accepted ADRs and owning architecture papers as authoritative for detailed architecture and model decisions.

## One-page quick-start for AI agents

CIOS is an Enterprise Intelligence platform that detects meaningful enterprise change, builds Commercial Digital Twins, reasons over Observations and recommends commercially valuable action.

The current north-star is: **Move Flora from report generation to living Commercial Digital Twins.**

Before proposing work, ask whether the change improves durable enterprise memory, evidence-backed Observations, inspectable reasoning lineage and commercially useful action. If it only creates more output text, dashboards or summaries without improving memory or traceability, challenge the assumption.



## Mandatory Runtime Context inputs

ADR-015 requires every AI mission to declare or inherit a Runtime Context composed of Mission, Research Policy and Capability Profile. Research Policy is mandatory for every AI mission because it governs research depth, source-seeking posture, assurance burden, stop rule and escalation threshold without redefining Evidence.

Canonical Research Policies:

- **Discovery** — rapidly understand the problem, surface candidate concepts, identify uncertainties and avoid premature architectural commitment.
- **Research** — build a sufficiently evidenced view, create or update Observations where appropriate and preserve Unknowns and Contradictions.
- **Decision** — support an explicit architectural, commercial or product decision with traceable rationale, alternatives, consequences and boundaries.
- **Assurance** — validate conformance, conflicts, lineage, terminology, authority and release readiness without weakening existing doctrine.

Research Policy does not change CIOS Evidence doctrine. Evidence remains universal proof, Observation remains universal memory and runtime configuration does not modify durable architecture doctrine.

## Progressive Assurance operating rule

ADR-009 governs Commercial Digital Twin production.

The default operating mode is **Initial Decision Twin**. AI agents and Researchers should complete a useful governed Twin autonomously, with the shortest practical elapsed time and the minimum required output set:

1. governed Commercial Digital Twin state;
2. executive decision view;
3. source, uncertainty and lineage ledger.

Do not require intermediate owner approval for ordinary source selection, Observation creation, outside-in Hypothesis formation, pressure prioritisation or bounded learning recommendations.

Do not create manifests, completion reports, duplicate publication formats, release JSON, package inventories or release ZIPs unless the owner requests **Assured Release** or a promotion trigger in ADR-009 applies.

### Mandatory integrity checks

Run these once near completion and report exceptions rather than turning each check into a conversational gate:

- **Truth:** material claims are attributable and correctly classified.
- **Memory:** useful findings update durable Observations and Twin state.
- **Decision value:** the output improves a named decision or learning action.
- **Safety:** Unknowns, Contradictions, boundaries and recommendation limits remain visible.

### Stop rule

Stop research when the immediate decision is adequately supported and further collection is unlikely to change it materially. Record residual Evidence Demands instead of pursuing exhaustive completeness.

### Escalation rule

Escalate only for provider-specific pursuit or rejection, external outreach, material unsupported inference, unclear legal/security boundary, decisive confidential account knowledge, or explicit Assured Release.

### Interaction expectation

Optimise for one autonomous run and one completion response. Ask Rob only for information that materially changes the bounded decision. Rob is the strategic sales director and should not be required to administer research workflow.


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

- Do not invent canonical fields, enums, lifecycles, object meanings or Enterprise Model paths in runtime code when the owning specification is silent. Identify the owning architecture document, raise an architecture question, update the data contract or create an ADR before implementation.
- Provider output is candidate data, not canonical intelligence.
- Provider-specific DTOs must be mapped into canonical CIOS objects before reasoning or model updates.
- Preserve state-semantics separation: Observation lifecycle, domain measurement state, accounting basis, freshness and runtime run state are different concepts.


## Architecture v2.0 operating rules

- Treat ADR-016, FP-010, FP-011, EI-013, the Knowledge Pack Specification v1.0, Twin Presentation Model Specification v1.0, Industry Twin Lifecycle Specification v1.0, the Phase 1 Conflict and Reconciliation Report, the ADR index and the Document Map as governing inputs for Architecture v2.0 documentation work.
- Do not implement Knowledge Repository, Knowledge Pack import/export, presentation rendering, Industry monitoring or Flora runtime behaviour unless explicitly asked in a runtime implementation task.
- Specialist GPT-authored Twin Presentation Models are labelled interpretation payloads. They may be rendered or exchanged but are not evidence and are not canonical fact without separate owning-model acceptance.
- Knowledge Pack acceptance means valid repository handling; canonical promotion remains governed by EI-001, EI-002, EI-003, EI-012 and other owning model papers.
- Hypotheses and recommendations carried in Knowledge Packs must retain FP-009 and ADR-005 lineage.

### Architecture v2.0 AI responsibility rules

- GPT output is candidate intelligence. It may be useful, structured and persuasive, but it is not canonical Enterprise Intelligence by default.
- GPTs may create draft Twin releases, Presentation Models and Knowledge Packs. Those artefacts must preserve lineage, Unknowns, Contradictions and interpretation labels.
- Flora governs, versions, renders, compares and compounds accepted Presentation Models, Twin releases and Knowledge Packs through repository, registry, rendering, lineage, release-comparison, Change Queue and Cross-Twin Intelligence services.
- Acceptance of a Presentation Model, Twin release or Knowledge Pack does not upgrade interpretation into fact. Canonical promotion remains governed by EI-001, EI-002, EI-003, EI-012, FP-009 and other owning model papers.
- Flora-native AI should focus preferentially on Cross-Twin Intelligence: comparing Enterprise, Industry, Market Participant, Opportunity and Relational Twins; identifying account-relative strengths and weaknesses; detecting contradictions; and compounding learning across accepted Knowledge Packs.
- Account-level runtime reasoning remains permitted. It is optional when an accepted Presentation Model already exists for the executive view, and its output must never silently mutate canonical memory.
- Industry Twin work should preserve the lifecycle cadences of continuous monitoring, weekly triage, monthly release, quarterly assurance and event-driven review.
- Market Participant Twin work should model supplier, competitor and partner roles, account-relative strengths and weaknesses, fit, access, incumbent position, evidence quality, Unknowns and Contradictions.


## Research GPT and Knowledge Pack publishing rules

Research GPTs must use the canonical Markdown [Commercial Digital Twin Research Agent Guide](architecture/research/Commercial-Digital-Twin-Research-Agent-Guide.md). The DOCX copy in `architecture/research/` is a historical review copy, not canonical source.

For Knowledge Pack publishing, Research GPT outputs must be compatible with `manifest.json`, `metadata.json`, `validation.json`, `lineage.json`, `checksums.sha256`, `payload/twin/`, `payload/presentation-model/` and `attachments/` where appropriate. Do not require a GPT to create a ZIP unless an existing text-based publishing workflow explicitly gives it that job.

Research GPTs must produce governed Twin candidate data, atomic Observations, Twin Presentation Models, enterprise topology, executive themes, stakeholder landscape, commercial relevance, Unknowns, Contradictions, Recommendations, lineage manifests, validation reports, release manifests and completion reports. They must use enterprise-specific language, stable IDs, explicit truth status, source cut-off, confidence and freshness. Facts must remain separate from interpretation; projections and human-supplied knowledge must be labelled; Recommendations must link to Hypotheses and Evidence; Unknowns and Contradictions must be preserved.

Executive-facing output for `strategic_sales_director_v1` must answer: Who? Why now? Why them? What evidence? What remains unknown? What contradicts the current view? What next? What not to claim? It must not expose raw worksheet or database labels and must not assert profit-centre or cost-centre classifications without support.

Industry Research GPTs must review the Flora Change Queue, distinguish signal from material change, create atomic Industry Observations, publish incremental Industry Knowledge Packs, run weekly triage, monthly governed release, quarterly structural assurance and event-driven release for material events, propose cross-Twin impacts and make no silent updates to related Twins.

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
