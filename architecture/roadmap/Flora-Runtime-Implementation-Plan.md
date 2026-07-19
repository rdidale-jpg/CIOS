# Flora Runtime Implementation Plan

**Purpose:** Define the implementation roadmap for the Flora runtime required to realise FA-001, the Flora Product Architecture Blueprint, FEIR-001, the CIOS Reference Architecture and accepted Flora-governing ADRs.  
**Status:** Proposed implementation roadmap  
**Owner:** Rob / CIOS  
**Architecture owner:** CIOS Chief Architect  
**Date:** 2026-07-19  
**Scope:** Runtime components, epics, interfaces, dependencies and delivery sequence. This document does not implement code, select database products or create canonical object semantics.

## 1. Governing authority reviewed

This plan is derived from the following governing architecture and governance sources:

| Source | Runtime mandate used by this plan |
| --- | --- |
| FEIR-001 — Flora Enterprise Intelligence Runtime Architecture v1.0 | Flora is the governed runtime over Enterprise Knowledge, with ingestion, runtime graph, orchestration, bounded GPT workers, deterministic controls, candidate intelligence, presentation and write-back boundaries. |
| ADR-024 — Hybrid Enterprise Intelligence Runtime | Flora must own orchestration, provenance, runtime state, validation and presentation while GPT workers remain bounded and deterministic controls govern lineage, lifecycle, contradiction and recommendation eligibility. |
| ADR-025 — Flora as the Enterprise Intelligence Workspace | Flora is a contextual reasoning and action workspace over governed Enterprise Intelligence, not a chatbot, dashboard, CRM replacement or second source of truth. |
| FA-001 — Flora Enterprise Intelligence Workspace Reference Architecture | Flora must be object-centric, perspective-led, evidence-grounded and commercially actionable while preserving Focus Object context, universal actions, Unknowns, Contradictions and lineage. |
| Flora Product Architecture Blueprint | The product must expose Explore, Explain, Anticipate and Act modes over the same governed object state, with object-first actions and visible reasoning paths. |
| CIOS Reference Architecture v1.0 | Runtime and product surfaces are views over evidence, Observations, Enterprise Models and reasoning lineage; CIOS flows from sources through Evidence, Observations, Enterprise Models, twins, presentation, Flora, action and learning. |
| ADR-001 — Observations as Atomic Intelligence Unit | Runtime design must prefer Observations over raw evidence fragments and preserve evidence lineage, Unknowns, Contradictions and confidence at Observation level. |
| ADR-005 — No Recommendation Without Inspectable Lineage | Strong Recommendations require inspectable lineage back through thesis or hypothesis, Signal, Observation, Evidence and Source; weak lineage must downgrade into learning actions or evidence demands. |
| ADR-014 — Evidence-Governed Enterprise Intelligence Reasoning Runtime | Runtime reasoning requires bounded retrieval, structured evidence packages, versioned reasoning profiles, structured outputs, claim validation, provider abstraction and safe failure behaviour. |
| ADR-016 — Knowledge Packs as the Standard Exchange Mechanism | Knowledge Packs may be validated, versioned, stored and rendered, but package acceptance does not silently promote contained claims into canonical memory. |
| Flora governance documents | Feature delivery must pass FA-001 compliance, explainability, lineage, Unknown preservation, commercial reasoning validation and architecture review. |

## 2. Architectural implementation principles

1. **Implement complete reasoning slices, not disconnected screens.** Each increment must preserve Focus Object, evidence, Observation, reasoning, uncertainty, commercial context and action boundaries.
2. **Runtime projections are not canonical memory.** Flora may cache and compose governed objects, but canonical Evidence, Observations, Enterprise Models, graph state, hypotheses and recommendations remain governed by their owning architecture.
3. **Observations are the reusable intelligence unit.** Retrieval can include Evidence where necessary, but downstream reasoning should operate from Observations and accepted intelligence wherever possible.
4. **GPT workers produce candidate or transient outputs only.** Runtime acceptance, lifecycle movement, recommendation eligibility and write-back remain deterministic or human-governed.
5. **Unknowns and Contradictions are first-class runtime objects.** They must be returned by retrieval, shown in views, preserved in worker outputs and included in recommendation downgrades.
6. **Commercial judgement dimensions remain separate.** Need, Provider Fit, Accessibility, Commercial Conviction, timing, evidence strength and route to market must not collapse into an opaque score.
7. **Learning precedes selling.** If lineage, freshness, authority, executive relevance or conviction is incomplete, the runtime must recommend learn, monitor, gather evidence, validate, defer or reject before pursuit.
8. **Every material result is auditable.** The runtime must retain source asset IDs, retrieved context, worker identity, model metadata where available, validation results, confidence, lifecycle status and human decisions.

## 3. Runtime component model

| Component | Primary responsibilities | Required interfaces | Governing trace |
| --- | --- | --- | --- |
| Governed Asset Connector | Read accepted architecture, Enterprise Knowledge, Knowledge Packs, twins, presentation models and manifests without mutating them. Resolve repository paths, release identifiers and asset metadata. | `AssetRead`, `ManifestRead`, `KnowledgePackRead`, `TwinRead`, `ReleaseLookup` | FEIR system boundaries; ADR-016 exchange boundary; CIOS Reference Architecture Knowledge Exchange and Runtime layers. |
| Ingestion and Normalisation Service | Validate manifests, classify object types, resolve stable IDs, detect missing metadata, build runtime indexes and record ingestion status. | `IngestAssetSet`, `ValidateManifest`, `ResolveIdentifier`, `IndexProjection`, `IngestionReport` | FEIR Flora ingestion boundary; FA-001 universal object identity; ADR-012 governed import boundary where applicable. |
| Runtime Object Registry | Maintain runtime projections of governed objects and candidate intelligence classes without duplicating canonical ownership. Track status, authority, provenance and persistence class. | `GetFocusObject`, `ListObjectRelationships`, `RegisterCandidate`, `GetCandidateStatus`, `ResolveObjectAuthority` | FEIR runtime object classes and authority model; ADR-025 no second source of truth; FA-001 Focus Object contract. |
| Runtime Knowledge Graph Projection | Provide queryable relationships among governed objects, Observations, Signals, Hypotheses, Unknowns, Contradictions, executives, capabilities, programmes, opportunities and candidate objects. Preserve lineage and temporal context. | `GraphQuery`, `RelationshipResolve`, `TemporalQuery`, `ContradictionQuery`, `UnknownQuery` | FEIR runtime graph boundary; EI-002 graph ownership; FA-001 relationships, history and inspectability. |
| Workspace State Service | Hold focus, perspective, navigation, exploration trails, watch state, filters, comparison state and user preferences as non-canonical runtime state. | `SetFocus`, `GetWorkspaceState`, `RecordTrailStep`, `SetPerspective`, `WatchObject`, `CompareObjects` | FA-001 navigation model and Exploration Trails; ADR-025 runtime authority boundary. |
| Context Planning Service | Convert a user question, trigger or workspace action into retrieval, stage and worker plans. Record skipped stages and confidence impact. | `PlanContext`, `PlanReasoningStages`, `DeclareEvidenceDemand`, `RecordSkippedStage` | FEIR canonical reasoning stages and Context Planner worker; Product Blueprint Flora reasoning panel. |
| Bounded Retrieval Service | Select governed, access-authorised, object-scoped, decision-relevant records and accepted intelligence. Rank by materiality, recency, authority, evidence strength, uncertainty, contradiction and commercial relevance. | `RetrieveContextPackage`, `RetrieveEvidencePackage`, `RetrieveObservationSet`, `RetrieveLineage`, `RetrievePresentationPayload` | ADR-014 bounded retrieval and evidence-package construction; ADR-001 Observation preference; FA-001 evidence and observations contract. |
| Evidence Package Builder | Build structured packages with IDs, class, statement, truth status, confidence, freshness, lineage, linked objects, Unknowns, Contradictions and human-supplied labels. | `BuildEvidencePackage`, `BuildObservationPackage`, `ValidatePackageCompleteness`, `PackageMetadata` | ADR-014 structured evidence packages; ADR-004 human-supplied labelling; ADR-005 recommendation lineage. |
| Reasoning Orchestrator | Execute FEIR reasoning stages, select deterministic checks and GPT workers, pass bounded context, collect structured outputs, persist audit and route failures safely. | `RunReasoningPipeline`, `InvokeWorker`, `ValidateWorkerOutput`, `PersistReasoningRun`, `ReturnSafeFallback` | ADR-024 hybrid runtime; FEIR reasoning orchestrator; EIRP reasoning pipeline. |
| GPT Worker Gateway | Provide provider-abstracted, versioned worker invocation for context planning, observation analysis, mechanism interpretation, hypothesis generation, challenge, executive relevance, commercial action and narrative. Enforce structured I/O. | `InvokeWorkerTask`, `WorkerSchemaValidate`, `ModelMetadata`, `ProviderConfig`, `RetryWithinPolicy` | FEIR GPT worker model; ADR-014 provider abstraction and structured output. |
| Candidate Intelligence Store | Persist material candidate Observations, relationships, Signals, Hypotheses, executive relevance, commercial assessments, Recommendations, validation states and audit references. | `CreateCandidate`, `UpdateCandidateValidation`, `ListCandidatesForObject`, `SupersedeCandidate`, `CandidateLineage` | FEIR candidate intelligence objects and persistence policy; ADR-024 candidate outputs. |
| Deterministic Policy and Validation Services | Enforce identity, authority, access, lineage, freshness, confidence bounds, lifecycle, Unknown preservation, Contradiction preservation, human-knowledge labelling, recommendation eligibility and write-back eligibility. | `ValidateClaim`, `ValidateLineage`, `ValidateLifecycleTransition`, `CheckRecommendationEligibility`, `CheckWriteBackEligibility`, `AccessDecision` | FEIR deterministic controls; ADR-005 lineage; ADR-014 claim validation; FP-009 hypothesis lifecycle. |
| Recommendation Policy Service | Apply the minimum Evidence → Observation → Mechanism/Signal → Enterprise Context → Hypothesis → Commercial Assessment → Recommendation boundary and downgrade unsafe actions. | `AssessActionEligibility`, `DowngradeAction`, `ExplainEligibility`, `RequireHumanApproval` | FEIR recommendation policy; ADR-005; ADR-025 learning before selling and distinct commercial dimensions. |
| Human Review and Approval Service | Capture approvals, rejections, comments, lifecycle decisions, contradiction resolutions, external-output approvals and write-back decisions with user, time and lineage. | `RequestReview`, `RecordDecision`, `ApproveExternalUse`, `ApproveLifecycleChange`, `RejectCandidate` | FEIR human decision points; Flora Definition of Done; ADR-009 progressive assurance. |
| Presentation View Composer | Render Explore, Explain, Anticipate and Act views, Focus headers, intelligence canvas, context panel, reasoning panel, lineage drill-down and safe unavailable states. | `ComposeFocusView`, `ComposeReasoningPath`, `ComposeWhatChanged`, `ComposeCommercialContext`, `ComposeSafeFallback` | FA-001 workspace regions; Product Blueprint workspace architecture; ADR-025 reports and screens are views. |
| Audit and Provenance Ledger | Retain initiating user or trigger, time, source asset IDs, retrieved package, worker/model/task versions, outputs, validation results, confidence, lifecycle, human interventions and supersession. | `RecordAuditEvent`, `GetReasoningRunAudit`, `GetLineageGraph`, `GetDecisionHistory`, `RetentionPolicy` | FEIR provenance and audit; ADR-024 provenance ownership; ADR-014 telemetry. |
| Write-back Proposal Service | Convert validated runtime learning into repository change proposals with originating candidate IDs, validation results and reviewer decisions; never silently mutate governed assets. | `CreateWriteBackProposal`, `AttachCandidateOrigin`, `GenerateRepositoryChange`, `TrackAcceptance`, `TriggerReingestion` | FEIR write-back architecture; ADR-025 governed update process; CIOS Reference Architecture learning loop. |
| Runtime Observability and Operations | Monitor ingestion, retrieval, worker invocation, validation failures, stale indexes, dependency failures and policy rejections. Fail closed when runtime dependencies are unavailable. | `HealthCheck`, `RuntimeMetrics`, `DependencyStatus`, `PolicyFailureReport`, `OperationalAlert` | FEIR failure behaviour; ADR-014 safe unavailable state. |

## 4. Implementation epics

### Epic 1 — Governed runtime foundation

**Outcome:** Flora can ingest governed assets, identify objects, project relationships and maintain non-canonical workspace state.

**Components:** Governed Asset Connector, Ingestion and Normalisation Service, Runtime Object Registry, Runtime Knowledge Graph Projection, Workspace State Service, Audit and Provenance Ledger baseline.

**Responsibilities:**

- Read governed Enterprise Knowledge, Knowledge Packs and architecture assets through stable adapters.
- Build a runtime index of Focus Objects, relationships, Observations, Unknowns and Contradictions.
- Expose object identity, status, provenance, freshness and lineage to the workspace.
- Persist focus, perspective, watch and exploration trail state without creating canonical knowledge.

**Key dependencies:** accepted Knowledge Pack contracts; Enterprise Knowledge asset identifiers; graph relationship semantics; access and tenant model; audit retention policy.

**Architectural integrity gate:** A user can focus a governed object and inspect identity, relationships, evidence/Observation availability, Unknowns and Contradictions without any generated recommendation or canonical mutation.

### Epic 2 — Evidence-governed retrieval and context packaging

**Outcome:** Flora can retrieve decision-relevant, access-authorised context packages that preserve source boundaries and Observation-led reasoning.

**Components:** Context Planning Service, Bounded Retrieval Service, Evidence Package Builder, deterministic access and lineage validation baseline.

**Responsibilities:**

- Convert user questions and triggers into explicit retrieval plans.
- Prefer accepted Observations and governed intelligence over raw evidence where available.
- Build packages that expose truth status, confidence, freshness, lineage, human labels, Unknowns and Contradictions.
- Record evidence demands and skipped reasoning stages.

**Key dependencies:** source authority and freshness metadata; Observation lifecycle metadata; human-supplied knowledge labels; package schema versioning.

**Architectural integrity gate:** Every material context package is inspectable and rejects or downgrades unsupported, stale, cross-enterprise or unlabelled human-supplied claims.

### Epic 3 — Hybrid reasoning orchestration and worker contracts

**Outcome:** Flora can execute bounded reasoning stages with structured GPT worker outputs while deterministic services retain authority.

**Components:** Reasoning Orchestrator, GPT Worker Gateway, worker schemas, Candidate Intelligence Store, worker-output validation, audit event expansion.

**Responsibilities:**

- Implement FEIR canonical stages: context planning, retrieval, Observation selection, mechanism interpretation, enterprise-context assessment, competing hypotheses, challenge, executive relevance, commercial action, validation, presentation and learning capture.
- Invoke specialist workers only with supplied context and task-specific schemas.
- Store outputs as candidate or transient objects with provenance, confidence rationale, Unknowns, Contradictions and validation hints.
- Reject unclassified prose and preserve deterministic failure behaviour.

**Key dependencies:** provider abstraction; task and prompt versioning; structured output schemas; candidate object lifecycle; retry and failure policy.

**Architectural integrity gate:** GPT output cannot become authoritative intelligence, alter lifecycle state, suppress contradictions, invent executives or bypass validation.

### Epic 4 — Deterministic policy, lifecycle and recommendation controls

**Outcome:** Flora can validate claims, preserve lifecycle boundaries and produce only proportionate actions backed by inspectable lineage.

**Components:** Deterministic Policy and Validation Services, Recommendation Policy Service, Human Review and Approval Service baseline.

**Responsibilities:**

- Validate identity, authority, lineage, freshness, confidence bounds, lifecycle transitions, Unknowns and Contradictions.
- Enforce FP-009 hypothesis lifecycle constraints and human approval for material lifecycle decisions.
- Apply recommendation eligibility across the minimum FEIR reasoning boundary.
- Downgrade incomplete outputs into learn, monitor, gather evidence, validate, defer or reject.

**Key dependencies:** FP-009 lifecycle rules; ADR-005 lineage rules; commercial reasoning dimensions; approval roles; external-use policy.

**Architectural integrity gate:** No strong Recommendation can render unless lineage and approval state satisfy ADR-005, FEIR and human decision-point requirements.

### Epic 5 — Object-centric workspace experience

**Outcome:** Flora renders FA-001 and the Product Blueprint as an object-first workspace over governed and candidate intelligence.

**Components:** Presentation View Composer, Workspace State Service expansion, lineage drill-down, What Changed view, Explore/Explain/Anticipate/Act view contracts.

**Responsibilities:**

- Render Focus header, intelligence canvas, context panel and Flora reasoning panel.
- Support universal actions: Ask, Explain, Compare, Watch, Validate, Shape and Share where authorised and data-supported.
- Expose evidence, Observations, Questions, Unknowns, Contradictions, hypotheses, Recommendations, commercial context and history.
- Keep Need, Provider Fit, Accessibility, Commercial Conviction, timing and evidence strength separately inspectable.

**Key dependencies:** object registry; graph projection; retrieval packages; policy outputs; user experience specifications; access model.

**Architectural integrity gate:** Screens and reports remain views; users can inspect why a material conclusion is believed, what contradicts it and what remains Unknown.

### Epic 6 — Learning, write-back and governed accumulation

**Outcome:** Flora can convert validated runtime learning into governed repository change proposals and re-ingest accepted changes.

**Components:** Write-back Proposal Service, Human Review and Approval Service expansion, Candidate Intelligence Store lifecycle, ingestion reprocessing, audit decision history.

**Responsibilities:**

- Capture material runtime learning, evidence demands, human judgements, commercial outcomes and learning events.
- Generate repository change proposals that reference originating candidate IDs, validation results and reviewer decisions.
- Track governance acceptance, rejection, supersession and re-ingestion.
- Ensure accepted learning evolves Enterprise Knowledge while runtime cache remains subordinate.

**Key dependencies:** repository change workflow; reviewer roles; acceptance checklist; Knowledge Pack and Enterprise Knowledge update contracts; audit retention.

**Architectural integrity gate:** Durable learning enters canonical knowledge only through governed repository changes and re-ingestion.

### Epic 7 — Operational hardening and assurance

**Outcome:** Flora can be operated safely with compliance evidence, runtime telemetry and architecture review support.

**Components:** Runtime Observability and Operations, audit reporting, compliance checklist automation, policy failure dashboards, safe fallback states.

**Responsibilities:**

- Monitor ingestion health, retrieval coverage, validation failures, stale indexes, provider errors and policy rejections.
- Produce architecture review evidence for FA-001 compliance, lineage verification, Unknown preservation and commercial reasoning validation.
- Fail closed when runtime dependencies are unavailable.
- Support progressive assurance modes for higher-consequence use.

**Key dependencies:** operational telemetry policy; secrets and provider configuration; assurance workflow; review templates.

**Architectural integrity gate:** Runtime incidents cannot corrupt governed knowledge or produce fabricated executive content.

## 5. Interface boundary summary

| Interface family | Producer | Consumer | Contract expectation |
| --- | --- | --- | --- |
| Asset and package read interfaces | Governed repository, Knowledge Packs, Twin assets | Ingestion, retrieval, presentation | Read-only, versioned, lineage-preserving, access-controlled. |
| Runtime object interfaces | Object registry, graph projection, candidate store | Workspace, orchestrator, policy services | Stable IDs, authority labels, provenance, lifecycle, persistence class. |
| Context package interfaces | Retrieval and package builder | Workers, validators, presentation | Structured evidence/Observation packages with truth status, freshness, confidence, Unknowns, Contradictions and human labels. |
| Worker task interfaces | Orchestrator | GPT Worker Gateway | Versioned task schemas, bounded input asset IDs, structured outputs, model metadata and validation hints. |
| Policy interfaces | Deterministic validation and recommendation services | Orchestrator, workspace, review service | Explicit pass, fail, downgrade, approval-required or safe-unavailable outcomes with reasons. |
| Human decision interfaces | Review service | Candidate store, write-back, presentation | User, role, decision, time, object IDs, rationale, approval scope and audit link. |
| Presentation interfaces | View composer | Product surfaces and exports | Transient or view-class payloads with lineage drill-down and uncertainty disclosures. |
| Write-back interfaces | Write-back proposal service | Repository governance and ingestion | Candidate-originated change proposals; no silent canonical mutation; acceptance triggers re-ingestion. |

## 6. Dependency map

1. **Asset identity precedes retrieval.** The runtime cannot package or validate evidence until governed objects and source assets resolve to stable IDs.
2. **Retrieval precedes reasoning.** GPT workers must receive bounded context packages, not raw workspace prompts.
3. **Candidate storage precedes validation workflow.** Material worker outputs require candidate identifiers before human review, audit and write-back can reference them.
4. **Validation precedes presentation of material conclusions.** Unsupported claims must be rejected, weakened or labelled before rendering.
5. **Recommendation policy depends on hypothesis and commercial assessment lineage.** The Act experience cannot safely lead delivery before lineage and downgrade controls exist.
6. **Write-back depends on candidate lineage and human decisions.** Runtime learning cannot be promoted until candidate origin, validation and reviewer decision are available.
7. **Operational assurance spans all epics.** Audit and health signals must be introduced early and expanded as reasoning, recommendation and write-back consequences increase.

## 7. Recommended incremental delivery sequence

### Increment 0 — Architecture and data readiness audit

- Confirm source-of-truth repositories, Knowledge Pack locations, object identifier conventions, user/access assumptions and review roles.
- Produce interface stubs and schema version register for runtime objects, context packages, worker tasks, policy outcomes and audit events.
- Decide whether unresolved persistence, access or audit-retention choices require ADRs before implementation.

**Why first:** FA-001 and ADR-025 prohibit duplicate truth; FEIR requires clear authority and persistence classes before runtime projections are built.

### Increment 1 — Read-only object workspace slice

- Implement read-only ingestion over a narrow governed corpus, preferably the Banking reference assets already used by FEIR and UX validation.
- Deliver Focus Object lookup, relationships, evidence/Observation availability, Unknowns, Contradictions, freshness and lineage drill-down.
- Add workspace state for focus, perspective, watch and trail without canonical mutation.

**Why next:** This proves the FA-001 object-first workspace and ADR-025 no-second-source boundary before AI reasoning is introduced.

### Increment 2 — Evidence-governed Explain slice

- Add context planning, bounded retrieval and evidence/Observation package construction.
- Deliver Explain and Show Evidence actions for a focused object.
- Validate package lineage, source authority, freshness, human labels, Unknowns and Contradictions.

**Why next:** ADR-014 and ADR-001 require bounded evidence packages and Observation-led reasoning before generated interpretation or Recommendations.

### Increment 3 — Bounded reasoning without strong Recommendations

- Add orchestrated worker execution for mechanism interpretation, hypothesis generation and hypothesis challenge.
- Persist candidate Signals, Hypotheses, Unknowns and Contradictions with audit records.
- Render candidate reasoning with explicit validation status and no strong action language.

**Why next:** ADR-024 selects hybrid reasoning, but ADR-005 and FEIR require candidate status and validation before Recommendations.

### Increment 4 — Commercial context and proportional action

- Add executive relevance and commercial action workers, deterministic recommendation eligibility and downgrade controls.
- Render Act view with separate Need, Provider Fit, Accessibility, Commercial Conviction, timing and evidence strength.
- Enable only learn, monitor, gather evidence, validate, exploratory engage or defer actions until human approval flows are complete.

**Why next:** FA-001 and ADR-025 require commercial action to emerge from enterprise understanding while preserving distinct commercial judgement dimensions.

### Increment 5 — Human review and approved strong action

- Add human approval for material hypothesis lifecycle changes, contradiction resolution, strong Recommendations and external commercial assets.
- Expose review queues and decision audit.
- Permit approved strong Recommendations only when FEIR minimum lineage and ADR-005 inspectability pass.

**Why next:** Human decision points are mandatory before high-consequence commercial outputs can be safely enabled.

### Increment 6 — Governed learning and write-back

- Add write-back proposal creation for validated runtime learning.
- Integrate repository review, acceptance, rejection, supersession and re-ingestion.
- Show Memory views for accepted changes, candidate history, reasoning changes, commercial changes and model corrections.

**Why next:** CIOS value compounds through learning, but FEIR and ADR-025 forbid silent mutation; write-back follows proven candidate and review controls.

### Increment 7 — Cross-twin and domain-neutral scale-out

- Generalise from the Banking slice to additional industries, enterprises, market participants, opportunities and relational twins.
- Expand Compare, What Changed, Anticipate and portfolio learning over multiple governed objects.
- Validate that no Banking-specific mechanism or label has become a core runtime assumption.

**Why last:** Domain neutrality is a governing constraint, but scaling before the complete governed reasoning slice is proven would risk duplicating semantics and weakening lineage.

## 8. ADR and specification decisions recommended before build-out

The following decisions should be resolved through the Flora Architectural Decision Workflow before or during Increment 0:

| Decision needed | Reason |
| --- | --- |
| Runtime graph persistence ADR | FEIR leaves runtime graph persistence open; implementation must decide store responsibility, retention, cache invalidation and canonical boundary. |
| Context package and worker schema specification | ADR-014 and FEIR require structured packages and worker outputs; implementation needs versioned schemas before coding. |
| Recommendation eligibility policy specification | FEIR defines policy intent; implementation needs precise pass/fail/downgrade rules without introducing opaque numeric scoring. |
| Audit retention and observability policy | FEIR requires audit of material outputs; implementation needs retention, privacy, model metadata and telemetry boundaries. |
| Human review role and approval specification | FEIR requires human approval for high-consequence decisions; implementation needs role, authority and decision-record contracts. |
| Write-back proposal contract | FEIR defines the write-back flow; implementation needs repository change payload, candidate-origin links and re-ingestion status contract. |

## 9. Implementation review checklist for each increment

Every increment must record:

- Which FA-001 region and Product Blueprint mode it strengthens.
- Which Focus Object types are supported and which are deliberately unsupported.
- Which governed object IDs and lineage are exposed.
- How Unknowns, Contradictions, human-supplied labels, freshness and confidence are preserved.
- Whether any material output is candidate, accepted, transient view or governed write-back proposal.
- Whether Recommendations are blocked, downgraded, human-approved or external-use approved.
- Which deterministic controls ran and which failures caused safe fallback.
- Whether an ADR, UX specification or reference architecture update is required.

## 10. Summary roadmap

```text
0. Architecture and data readiness audit
1. Read-only object workspace slice
2. Evidence-governed Explain slice
3. Bounded reasoning without strong Recommendations
4. Commercial context and proportional action
5. Human review and approved strong action
6. Governed learning and write-back
7. Cross-twin and domain-neutral scale-out
```

This sequence maintains architectural integrity because it establishes authority, identity, lineage and workspace state before reasoning; candidate and validation controls before Recommendations; human approval before high-consequence action; and governed write-back before durable learning.
