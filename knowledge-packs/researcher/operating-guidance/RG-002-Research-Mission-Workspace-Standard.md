# RG-002 — Research Mission Workspace Standard

**Subtitle:** Operational Standard for Persistent Enterprise Intelligence Research  
**Document ID:** RG-002  
**Status:** Approved operating standard  
**Classification:** Research Guidance / Operating Standard  
**Canonical Owner:** Chief Architect  
**Version:** 1.0.0

## 1. Executive Summary

Enterprise Intelligence is developed through the progressive acquisition, validation and synthesis of evidence. It is not created through isolated research exercises, individual conversations or document production.

Research Missions exist to maximise defensible Executive Understanding by progressively improving the breadth, depth, quality and explainability of Enterprise Intelligence artefacts.

This standard defines the operational model for persistent, autonomous and resumable Research Missions. It establishes the Research Mission Workspace as the authoritative operational state for long-running research activity.

The Workspace enables research to continue across multiple execution cycles while preserving evidence, reasoning, maturity, uncertainty and research intent.

This standard governs mission operation. It does not alter Enterprise Intelligence doctrine, Twin semantics or Knowledge Pack architecture.

## 2. Foundational Doctrine

Enterprise Intelligence SHALL be developed through cumulative understanding.

Research SHALL maximise defensible Executive Understanding rather than document production.

Research SHALL maximise learning rather than activity.

Evidence SHALL govern conclusions.

Conversation SHALL orchestrate research and SHALL NOT constitute persistent mission state.

Unknowns, contradictions and competing hypotheses SHALL be preserved explicitly until resolved or bounded by evidence.

Research SHALL continue while productive evidence opportunities remain.

A Research Mission exists to maximise defensible Enterprise Intelligence through the cumulative acquisition, validation and synthesis of evidence. Every requirement in this standard exists to preserve, advance or explain that objective.

## 3. Purpose

RG-002 defines how long-running autonomous Research Missions operate over time.

It standardises:

- persistent mission state;
- mission lifecycle;
- autonomous continuation;
- research prioritisation;
- checkpointing;
- deterministic recovery;
- evidence accumulation;
- evidence saturation;
- escalation recording;
- evidence exhaustion;
- completion assessment.

## 4. Design Goals

A conformant Research Mission SHALL:

- accumulate understanding continuously;
- avoid unnecessary repetition;
- preserve complete operational state;
- support deterministic recovery;
- maximise explainable Executive Intelligence;
- remain resilient to technical interruption;
- preserve provenance for material conclusions;
- preserve Unknowns and contradictions;
- expose current maturity and remaining work;
- continue without repeated conversational prompting while productive research remains.

## 5. Scope

RG-002 applies to Research Missions developing or materially improving:

- Industry Twins;
- Enterprise Twins;
- Market Participant Twins;
- Control Body Twins where already governed;
- Candidate Twins;
- the evidence, relationship and insight structures supporting them.

RG-002 does not modify:

- Enterprise Intelligence doctrine;
- existing Twin types or their semantics;
- Knowledge Graph semantics;
- Blueprint specifications;
- runtime reasoning architecture;
- Knowledge Pack exchange architecture.

## 6. Definitions

**Research Mission** — A bounded objective to develop or materially improve governed Enterprise Intelligence through autonomous evidence acquisition, validation and synthesis.

**Research Mission Workspace** — The complete persistent operational state required to understand, continue, audit and resume a Research Mission deterministically.

**Research Wave** — A bounded cycle of prioritisation, evidence acquisition, synthesis, Twin update, maturity reassessment and checkpointing.

**Research Increment** — A focused unit of work selected because it is expected to produce the highest-value material improvement in Enterprise Intelligence.

**Research Queue** — The ordered operational backlog of evidence demands and research increments.

**Completion Gate** — A declared breadth, depth, evidence, relationship, maturity or Executive Insight requirement that must be assessed before a mission may complete.

**Evidence Route** — A source, source class, query strategy, entity path, archive, relationship, hypothesis or corroboration path capable of producing relevant evidence.

**Evidence Saturation** — The progressive reduction in material new understanding produced by successive research waves.

**Evidence Exhaustion** — The evidenced condition in which all applicable permitted and reasonably discoverable evidence routes have been explored, all unaffected research has been completed, and further autonomous research is unlikely to produce material improvement.

**Checkpoint** — A validated persisted mission state from which research can resume deterministically.

**Escalation** — A recorded external dependency, access requirement, authority requirement, decision need or materially constrained evidence demand.

**Technical Interruption** — A temporary execution condition such as context pressure, timeout, tool failure, rate limit, output limit, file-generation failure or execution termination. It is not a mission outcome.

## 7. Architectural Principles

**RG2-P1 — Conversation is orchestration**

Conversation coordinates research. Conversation SHALL NOT be treated as the authoritative persistent state of a mission.

**RG2-P2 — Understanding accumulates**

Research SHALL extend existing validated understanding. It SHALL NOT intentionally recreate completed work unless revalidation is required by new evidence, contradiction, expiry or changed scope.

**RG2-P3 — Workspace state is authoritative**

The latest validated Workspace SHALL represent the complete operational state of the mission.

**RG2-P4 — Research is continuous**

Research SHALL continue until completion gates pass or evidence exhaustion is demonstrated.

**RG2-P5 — Evidence governs understanding**

Material claims, relationships, maturity assessments and Executive Insights SHALL be traceable to evidence or explicitly labelled as hypothesis, inference, Unknown or contradiction.

**RG2-P6 — Local uncertainty is not global failure**

An unresolved claim, entity, programme, supplier relationship, source or maturity domain SHALL NOT stop the wider mission while productive research remains elsewhere.

**RG2-P7 — Escalation is non-terminal**

Recording an escalation SHALL NOT pause, abandon, complete or otherwise terminate the mission.

**RG2-P8 — Technical interruption is resumable**

Technical interruption SHALL trigger persistence and recovery behaviour. It SHALL NOT constitute completion or evidence exhaustion.

**RG2-P9 — Executive understanding is the optimisation target**

Research SHALL prioritise material improvement in Enterprise and Executive Understanding rather than search volume, document length, elapsed time or artefact count.

**RG2-P10 — Maturity must be evidenced**

Maturity SHALL increase only where supported by demonstrable improvements in breadth, depth, evidence quality, relationship understanding, confidence or Executive Insight.

**RG2-P11 — Unknowns are preserved**

Missing evidence SHALL remain Unknown. It SHALL NOT be silently resolved by unsupported inference.

**RG2-P12 — Persistence is incremental**

The Workspace SHALL preserve complete operational state while avoiding unnecessary duplication of unchanged content, in accordance with the governed Knowledge Pack architecture.

## 8. Mission Lifecycle

Every Research Mission SHALL:

1. Create a Workspace or load the latest validated Workspace.
2. Validate Workspace integrity.
3. establish the current mission scope and completion gates;
4. assess current breadth, depth, maturity, evidence quality and coverage;
5. identify the highest-value eligible research increment;
6. execute a Research Wave;
7. acquire and evaluate evidence;
8. update affected Twins, relationships, programmes, evidence, Unknowns, contradictions and Executive Insights;
9. update maturity, coverage, saturation and queue state;
10. checkpoint the Workspace;
11. reassess whether productive evidence routes remain;
12. continue automatically unless COMPLETE or EVIDENCE EXHAUSTED is justified.

Report generation SHALL NOT replace this lifecycle.

Blueprints and bounded publications SHALL be derived from the Candidate Twin and Workspace state rather than treated as the primary purpose of research.

## 9. Research Strategy

After every checkpoint, the Researcher SHALL select the eligible research increment expected to produce the highest material improvement in defensible Enterprise Intelligence.

Prioritisation SHALL consider unresolved completion gates, strategic significance, commercial significance, expected Executive Insight value, maturity impact, relationship impact, dependency reduction, evidence quality, evidence availability, contradiction resolution, risk of unsupported conclusions and relevance to the declared mission objective.

The Researcher SHALL NOT prioritise work merely because it is easy to search, easy to write or likely to increase document volume.

The Researcher SHALL be able to state what it will research next, why that increment has priority, what evidence it seeks, and which maturity or completion gate it is expected to improve.

## 10. Research Mission Workspace

The Workspace SHALL contain all state required to resume deterministically.

Where applicable, it SHALL include:

- **Mission metadata:** mission identifier; title; objective; scope; exclusions; canonical owner; lifecycle state; Workspace version; creation and checkpoint timestamps; declared completion gates.
- **Candidate Twin:** current evolving Industry Twin or other governed target artefact; current bounded release state; release lineage.
- **Enterprise Twin Register:** enterprise identity; relevance; coverage status; maturity; priority; outstanding evidence demands.
- **Enterprise Twins:** current working Enterprise Twins using existing canonical semantics.
- **Market Participant Register:** participant identity; role; relevance; coverage; maturity; outstanding evidence demands.
- **Market Participant Twins:** current working Market Participant Twins using existing canonical semantics.
- **Control Body Twins:** only where such semantics already exist in governing architecture.
- **Transformation Portfolio:** programmes; initiatives; horizons; dependencies; intended outcomes; observed outcomes; delivery evidence; financial and operating implications.
- **Relationship Model:** enterprise relationships; market relationships; programme relationships; regulatory relationships; control relationships; commercial and supplier relationships; supporting evidence and confidence.
- **Evidence Register:** evidence identifier; source and provenance; acquisition date; source class; authority and quality assessment; claims supported or challenged; affected entities and relationships.
- **Unknown Register:** unresolved question; scope; materiality; evidence required; effect on maturity or conclusions.
- **Contradiction Register:** competing evidence; affected claims; alternative hypotheses; current assessment; resolution status.
- **Executive Insight Register:** insight; supporting evidence; reasoning; confidence; affected executives or decisions; commercial relevance; assumptions and uncertainty.
- **Coverage Matrix:** declared breadth; covered and uncovered entities; domains; programmes; participants; relationships.
- **Maturity Matrix:** current maturity by relevant Twin, domain and completion gate; supporting evidence; change since prior checkpoint; target maturity.
- **Research Queue:** ordered research increments and evidence demands.
- **Mission Journal:** chronological operational record.
- **Escalation Register:** external dependencies and material constraints.
- **Evidence Saturation Assessment:** progress and remaining productive routes.
- **Restart Conditions:** events or evidence that should reactivate exhausted research areas or a mission concluded as EVIDENCE EXHAUSTED.

## 11. Workspace Integrity

At every checkpoint the Workspace SHALL be internally coherent and resumable.

A checkpoint SHALL validate, at minimum: required mission metadata exists; all referenced Twins and entities are identifiable; material claims reference evidence or an explicit uncertainty class; maturity changes identify their evidential basis; Executive Insights identify evidence, reasoning, assumptions and confidence; queue items have valid state; escalations identify affected scope; journal entries record the completed Research Wave; unresolved contradictions and Unknowns are preserved; and the next eligible research increment can be determined.

The implementation SHALL NOT create unsupported Executive Insights, treat unsupported inference as evidence, increase maturity without evidence, discard unresolved contradictions, discard open escalations, or rely on inaccessible conversation history to reconstruct mission state.

## 12. Research Queue

Each Research Queue item SHALL include: unique identifier; research objective; rationale; affected Twin, domain, programme or relationship; expected maturity impact; expected Executive Intelligence value; evidence sought; applicable evidence routes; dependencies; priority; status; attempts made; result or disposition.

At minimum, queue statuses SHALL distinguish eligible, active, deferred, completed, constrained, exhausted and superseded.

A constrained item SHALL NOT terminate the mission.

After each checkpoint the highest-value eligible item SHALL be selected.

When a queue item cannot progress, the Researcher SHALL record the constraint, update any affected Unknown or escalation, bound the impact, and select the next highest-value eligible item.

## 13. Evidence Acquisition

The Researcher SHALL seek the broadest and deepest defensible understanding available from the permitted and reasonably discoverable evidence universe.

Applicable evidence routes may include official organisational publications; annual reports, accounts, strategies and business plans; budget, spending and financial-control material; parliamentary, legislative and committee material; audit, assurance and regulatory reports; procurement notices, contract records and framework information; programme documentation and delivery updates; operational and service-performance data; leadership statements; technical, data and architecture publications; supplier disclosures and case studies; reputable specialist analysis; credible news reporting; archived and historic sources; adjacent or relationship evidence capable of corroborating or challenging a claim.

Not every source class applies to every evidence demand. The Workspace SHALL record which applicable routes were considered and attempted.

The Researcher SHALL prefer authoritative primary evidence where it should reasonably exist, use secondary evidence to corroborate, contextualise or identify further routes, distinguish evidence from inference, preserve source conflict, and avoid asserting certainty beyond the evidence.

## 14. Maturity Model

RG-002 SHALL use the maturity model already governed by RG-001 and applicable Twin specifications. It SHALL NOT create a competing maturity scale.

The Workspace SHALL continuously record breadth, depth, evidence quality, confidence, relationship understanding, transformation understanding, financial and operating understanding where applicable, Executive Insight usefulness, and completion-gate status.

Maturity SHALL be local as well as aggregate. An unresolved issue SHALL affect the smallest defensible scope, such as a claim, relationship, programme, domain, Enterprise Twin, Market Participant Twin or completion gate. It SHALL NOT automatically invalidate unrelated research.

## 15. Checkpointing

The Researcher SHALL checkpoint after every Research Wave; after material changes to a Twin; after material maturity changes; after completing a material enterprise, participant or programme increment; before anticipated execution interruption; when explicitly requested; and before producing a terminal mission assessment.

Each checkpoint SHALL persist the current Workspace; validate integrity; update the Mission Journal; update maturity and coverage; update the Research Queue; update saturation; preserve open Unknowns, contradictions and escalations; identify the next priority; and support deterministic resume.

The latest validated checkpoint SHALL be made available as a downloadable Research Mission Workspace Package using the existing governed Knowledge Pack exchange mechanism wherever applicable.

Do not invent a parallel arbitrary archive format where ADR-016, FP-010 or the Knowledge Pack Specification already provides the required mechanism.

## 16. Recovery and Resume

Every resumed mission SHALL:

1. locate the latest validated Workspace checkpoint;
2. validate its integrity;
3. load mission scope, completion gates and current state;
4. reconcile interrupted or active queue items;
5. preserve previously completed work;
6. reassess maturity and productive evidence routes;
7. select the next highest-value eligible increment;
8. continue.

The Researcher SHALL NOT depend on prior conversation history, ask the user to reconstruct completed work, restart the mission from the beginning, or rewrite completed Twins without evidence-driven reason.

## 17. Mission Journal

The Mission Journal SHALL record checkpoint identifier and time; Research Wave objective; evidence routes attempted; evidence acquired; Twins and relationships changed; maturity changes and rationale; Unknowns opened or closed; contradictions opened or resolved; escalations opened, updated or resolved; Executive Insights added, changed or withdrawn; prioritisation decisions; next research priority; and technical interruption and recovery events.

The Mission Journal is operational traceability. It SHALL NOT replace the Evidence Register or canonical Twin content.

## 18. Escalation Register

Escalations SHALL be recorded when a material issue depends on restricted or inaccessible evidence, an external authority, a user decision, access not available to the Researcher, authoritative clarification, or a material unresolved conflict that cannot be autonomously resolved.

Each escalation SHALL record: identifier; status; date raised and updated; affected scope; issue; materiality; completion gate or maturity domain affected; evidence routes attempted; alternative hypotheses; consequence if unresolved; minimum resolution required; requested owner or authority; continuing research response.

Permitted statuses SHOULD include OPEN, PARTIALLY_RESOLVED, RESOLVED, ACCEPTED_UNKNOWN and SUPERSEDED.

Raising an escalation SHALL NOT change the wider mission from CONTINUE while any productive research increment remains.

After recording an escalation, the Researcher SHALL continue with the highest-value unaffected work.

Open escalations MAY remain when the mission completes, provided their uncertainty is explicit, their impact is bounded, no unsupported conclusion depends upon them, and they do not prevent the declared completion gates from passing.

## 19. Evidence Saturation

After every Research Wave, the Researcher SHALL assess material new evidence acquired; new entities discovered; new relationships discovered; maturity improved; Unknowns closed; contradictions resolved or introduced; Executive Insights added or materially changed; new evidence routes identified; and remaining productive routes.

Research SHALL continue where the wave produced material improvement or credible productive evidence routes remain.

Evidence saturation SHALL NOT be inferred solely from repeated search results, one unavailable source, elapsed time, document size, number of searches, model fatigue, context pressure or temporary technical failure.

## 20. Evidence Exhaustion

EVIDENCE EXHAUSTED MAY be declared only when every condition below is met:

1. One or more declared completion gates remain unmet.
2. Every incomplete maturity domain has explicit evidence demands.
3. All applicable permitted source classes have been considered.
4. Reasonable query variations, aliases, entity names, programme names and historic terms have been attempted.
5. Primary evidence routes have been pursued wherever they should reasonably exist.
6. Secondary, adjacent and corroborating routes have been examined.
7. Contradictory evidence has been investigated.
8. All unaffected Enterprise Twin, Market Participant Twin, programme, relationship and industry-synthesis research has been completed.
9. Successive Research Waves are producing no material new understanding.
10. Remaining gaps depend on evidence that is unpublished, inaccessible, restricted, unavailable or not reasonably discoverable.
11. The Workspace has been checkpointed and validated.
12. Restart conditions have been recorded.

EVIDENCE EXHAUSTED SHALL NOT be declared because of context or output limits; execution duration; task size or complexity; rate limits; tool failure; temporary source failure; inability to finish in one run; file-generation failure; a single inaccessible source; the existence of open escalations; or difficulty finding evidence.

An EVIDENCE EXHAUSTED conclusion SHALL record unmet completion gates, maximum evidenced maturity achieved, remaining Unknowns, open escalations, evidence routes attempted, affected claims and Twins, consequence of the remaining gaps, restart conditions, and status of any bounded incomplete Candidate Twin.

It SHALL NOT represent the Twin as complete or mature beyond the evidence.

## 21. Mission Outcomes

The mission outcome SHALL be one of:

**CONTINUE** — Completion gates have not passed and at least one productive evidence route remains. The Researcher SHALL continue automatically.

**COMPLETE** — All declared completion gates have passed. Residual Unknowns or open escalations MAY remain only where their impact is bounded and non-material to the completion gates.

**EVIDENCE EXHAUSTED** — Completion gates remain unmet, but all criteria in Section 20 have been satisfied.

Technical interruption is an execution condition recorded as resumable. It is not a mission outcome.

No generic BLOCKED mission state shall be introduced.

## 22. Mission Health and Operational Visibility

Each checkpoint SHALL expose sufficient information for an executive or Chief Architect to determine whether the mission is advancing.

Use existing governed measures where they exist. Do not invent false precision or unsupported aggregate percentages.

At minimum expose current mission outcome; completion-gate status; Enterprise Twin coverage and maturity; Market Participant coverage and maturity where applicable; programme and relationship coverage; evidence quality and saturation; open Unknowns; open contradictions; open escalations; material Executive Insights added or changed; progress since previous checkpoint; and next research priority and rationale.

The Workspace SHALL answer: “If another productive Research Wave were executed, what should be researched next, why, and what material improvement is expected?”

## 23. Relationship to RG-001

RG-001 governs research methodology and research behaviour.

RG-002 governs persistent mission operation, autonomous continuation, checkpointing and recovery.

RG-001 SHALL reference RG-002 for long-running mission persistence.

Move duplicated persistence behaviour from RG-001 only where doing so improves canonical ownership and does not weaken existing research requirements.

Do not rewrite RG-001 unnecessarily.

## 24. Relationship to Knowledge Pack Architecture

ADR-016, FP-010 and the Knowledge Pack Specification remain authoritative for packaging and exchange.

RG-002 defines the operational semantics and required contents of mission state.

The implementation SHALL reuse the governed Knowledge Pack exchange mechanism where applicable.

Where a Workspace-specific manifest field, package classification or validation rule is required, make the smallest compatible extension, preserve backward compatibility where practical, document the extension, and do not create an unrelated packaging system.

## 25. Conformance

A conformant implementation SHALL demonstrate:

- persistent Workspace state independent of conversation history;
- deterministic resume from the latest checkpoint;
- continuous evidence accumulation;
- preservation of Unknowns and contradictions;
- traceability from Executive Insights and maturity to evidence;
- prioritised Research Queue operation;
- non-terminal escalation behaviour;
- checkpoint creation after Research Waves;
- automatic continuation while productive routes remain;
- strict evidence-exhaustion assessment;
- absence of a generic BLOCKED terminal state;
- resilience to technical interruption;
- downloadable latest Workspace package;
- clear mission health and next priority;
- use of existing Twin semantics;
- use of governed Knowledge Pack architecture.
