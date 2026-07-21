# FEIR-001 — Flora Enterprise Intelligence Runtime Architecture v1.0

**Identifier:** FEIR-001
**Version:** 1.0
**Document Type:** Runtime Architecture Specification
**Authority Classification:** Proposed canonical runtime architecture specification
**Document class:** Owning architecture paper
**Status:** Proposed
**Owner:** Rob / CIOS
**Last updated:** 2026-07-18
**Decision record:** [ADR-024](../../decisions/ADR-024-Hybrid-Enterprise-Intelligence-Runtime.md)
**Authority:** Proposed Flora runtime specification under accepted ADR-024; does not supersede accepted Enterprise Intelligence, Founding Paper or ADR authority.

## 1. Mission and outcomes

Flora is the governed Enterprise Intelligence runtime that converts governed Enterprise Knowledge into inspectable Strategic Sales experience. It improves:

- **Detection:** changes in evidence and Observations can trigger candidate Signals, Hypotheses, gaps and reassessments.
- **Understanding:** GPT workers interpret mechanisms and enterprise context while deterministic services preserve source boundaries.
- **Prediction:** competing Hypotheses are strengthened, weakened, retired or held as Unknowns under FP-009 lifecycle control.
- **Executive specificity:** executive relevance is derived from accepted Executive, role, capability, programme and relationship knowledge; unsupported specificity is withheld.
- **Commercial action:** Recommendation eligibility follows evidence-to-hypothesis lineage and downgrades weak conviction into learning, monitoring or validation.
- **Cumulative Enterprise Intelligence:** durable learning is written back through governed knowledge processes so Living Commercial Digital Twins accumulate change without silently rewriting history.

## 2. System boundaries

| Boundary | Responsibility | Not responsible for |
| --- | --- | --- |
| Governed repository | Source of governed architecture, Enterprise Knowledge assets, accepted releases and change history. | Runtime inference, session state or silent learning insertion. |
| Enterprise Knowledge | Durable Evidence, Observations, Enterprise Models, graph relationships, hypotheses, Unknowns and Contradictions. | Transient prose or session-specific answers. |
| Flora ingestion | Reads governed assets, validates manifests, resolves identifiers and prepares runtime indexes. | Changing canonical knowledge without governance. |
| Flora runtime graph | Runtime projection and working graph over governed knowledge, candidate intelligence, user annotations and session state. | Owning canonical Enterprise Model semantics. |
| Reasoning orchestrator | Plans stages, selects workers, assembles context, records provenance and invokes deterministic controls. | Making unreviewed outputs authoritative. |
| GPT workers | Bounded interpretation, challenge, hypothesis, assessment and explanation tasks using supplied context only. | Autonomous collection, canonical writes, policy overrides or unclassified authoritative prose. |
| Deterministic policy services | Identity, authority, lineage, freshness, lifecycle, confidence bounds, contradiction, access and recommendation checks. | Commercial imagination or narrative generation. |
| Human reviewers | Approve high-consequence judgements, promotion, external use and write-back proposals. | Replacing machine validation controls. |
| Presentation layer | Explore, Focus and Shape views that hide repository internals while exposing lineage. | Durable memory ownership. |
| Write-back and governance | Converts validated runtime learning into repository changes, review, acceptance and re-ingestion. | Runtime agents directly rewriting authoritative assets. |

## 3. Authority model

| Subject | Authoritative system |
| --- | --- |
| Architecture | Repository architecture documents, accepted ADRs and authority registry. |
| Governed knowledge | Enterprise Knowledge repository and accepted Knowledge Packs after governed acceptance. |
| Runtime state | Flora runtime store. |
| Candidate intelligence | Flora runtime, labelled candidate with provenance. |
| Accepted intelligence | Governed Enterprise Knowledge after lifecycle acceptance; Flora may cache accepted state. |
| User annotations | Flora runtime, labelled by user, time, enterprise and access scope. |
| Human-supplied knowledge | Governed knowledge only after labelled acceptance; otherwise runtime annotation or candidate input. |
| Recommendations | Flora recommendation policy over governed lineage plus candidate/accepted assessments; strong recommendations require human approval before external use. |
| Reports and derived views | Presentation layer; transient unless promoted into governed objects. |

## 4. Runtime object classes

### Durable governed objects

Flora reuses existing Enterprise Intelligence ownership for Evidence, Observation, Enterprise, Executive, Capability, Programme, Mechanism, Enterprise Model, Industry Model, Behaviour Model, Hypothesis, Unknown and Contradiction. FEIR-001 does not create duplicate durable objects for those concepts.

### Candidate intelligence objects

Candidate Observation, Candidate Relationship, Candidate Signal, Candidate Hypothesis, Candidate Executive Relevance, Candidate Commercial Assessment and Candidate Recommendation are runtime objects. Each has identifier, status, authority, provenance, confidence, lifecycle, source relationships, validation state and persistence class.

### Derived runtime views

Industry Change, Enterprise Exposure, Commercial Urgency, Executive Relevance, Hypothesis Assessment, Evidence Gap, Next Best Action and Strategic Sales Brief are governed runtime views over durable and candidate objects.

### Transient presentation objects

Summaries, explanations, comparison views, executive narratives and session-specific answers are normally transient and must not be treated as governed knowledge.

## 5. Canonical reasoning stages

```text
Question or trigger
→ Context planning
→ Knowledge retrieval
→ Observation selection
→ Mechanism interpretation
→ Enterprise-context assessment
→ Competing hypothesis generation
→ Challenge and contradiction analysis
→ Executive relevance assessment
→ Commercial action assessment
→ Validation
→ Presentation
→ Learning capture
```

Stages may be skipped when irrelevant, but skipped stages must be recorded where their absence affects confidence, recommendation eligibility or audit.

## 6. GPT worker model

All workers return structured outputs with worker ID, task type, input asset IDs, output class, Unknowns, Contradictions, confidence rationale, validation hints, model metadata and task version. They must not use public model memory as evidence, change lifecycle state, suppress contradictions or return unclassified prose as authoritative intelligence.

| Worker | Purpose | Permitted inputs | Required outputs | Prohibited behaviour | Lineage/confidence/failure/output class |
| --- | --- | --- | --- | --- | --- |
| Context Planner | Plans context and stages. | User question, trigger, access scope, asset index. | Retrieval plan, stage plan, required object classes, gaps. | Answering the commercial question. | Cite planned asset IDs; confidence in context sufficiency; fail to evidence-demand; transient plan. |
| Observation Analyst | Interprets selected Evidence and Observations. | Evidence packages, Observations, source metadata. | Candidate Observation changes, materiality notes, Unknowns. | Accepting Observations or inventing evidence. | Evidence lineage required; confidence bounded by source and freshness; invalid output rejected; candidate intelligence. |
| Mechanism Analyst | Connects Observations to mechanisms or Signals. | Observations, mechanisms, behaviour and pressure models. | Candidate Signal/mechanism interpretation. | Creating durable mechanisms. | Observation and mechanism IDs required; confidence limited by relationship strength; candidate intelligence. |
| Hypothesis Generator | Creates competing explanations. | Observations, Signals, enterprise context, Unknowns. | Candidate Hypotheses with support, challenge points and gaps. | Collapsing alternatives into one preferred answer. | Support and contradiction lineage required; confidence qualitative; candidate intelligence. |
| Hypothesis Challenger | Tests hypotheses against counter-evidence. | Candidate/accepted Hypotheses, Contradictions, evidence gaps. | Challenge findings, weakened assumptions, evidence demands. | Resolving contradictions without authority. | Cite challenged object IDs; confidence in challenge coverage; fail to preserve current lifecycle; candidate intelligence. |
| Executive Relevance Analyst | Assesses who may care and why. | Executives, roles, programmes, capabilities, hypotheses. | Candidate Executive Relevance and Unknown ownership. | Inventing named executives or reporting lines. | Executive/role lineage required; low evidence becomes Unknown; candidate intelligence. |
| Commercial Action Analyst | Proposes proportionate next action. | Hypothesis assessments, conviction, access, contradictions. | Candidate Recommendation or lower action. | Recommending sale directly from documents. | Minimum recommendation chain required; confidence and downgrade reason; candidate intelligence. |
| Explanation/Narrative Worker | Presents validated intelligence. | Validated objects and presentation contract. | Summary, brief, comparison, narrative with lineage links. | Adding new facts or changing validation. | Uses approved output IDs; confidence inherited; failure falls back to structured view; transient presentation. |

## 7. Deterministic controls

Flora enforces independently of GPT judgement: asset identity, relationship resolution, source authority, evidence lineage, observation status, confidence bounds, freshness, hypothesis lifecycle, Unknown preservation, Contradiction preservation, competing-hypothesis visibility, human-knowledge labelling, recommendation eligibility, action downgrading, write-back eligibility and audit records.

## 8. Recommendation policy

Minimum reasoning boundary:

```text
Evidence → Observation → Mechanism or Signal → Enterprise Context → Hypothesis → Commercial Assessment → Recommendation
```

A Recommendation must not be produced directly from raw evidence or retrieved documents. Where lineage, freshness, contradiction handling or conviction is incomplete, Flora must prefer learn, gather evidence, validate, monitor or defer before selling.

Inspectable eligibility conditions:

| Outcome | Conditions |
| --- | --- |
| Learn | Material Unknown, stale source, unresolved relationship or failed worker validation. |
| Monitor | Evidence indicates change but mechanism, enterprise impact or timing remains weak. |
| Gather evidence | Missing source lineage, missing executive ownership or contradiction needs external proof. |
| Engage executive | Hypothesis lineage exists, executive relevance is supported and action is exploratory. |
| Prepare provocation | Supported pressure and enterprise relevance exist, but external asset requires human approval. |
| Shape workshop | Multiple accepted/candidate hypotheses indicate material shared problem and human reviewer approves. |
| Develop future enterprise model | Runtime learning is material but not yet governed knowledge. |
| Develop proposal | Requires accepted opportunity/positioning authority and human approval; FEIR-001 does not grant automatic proposal generation. |
| Defer | Conviction, access, freshness or authority is insufficient for action. |
| Reject | Candidate is unsupported, contradicted, out of scope or violates policy. |

No arbitrary numeric scoring is introduced by FEIR-001.

## 9. Human decision points

| Decision | Automated | Suggested | Human approval required |
| --- | --- | --- | --- |
| Accepting an Observation | No | Yes | Yes, under governed lifecycle. |
| Accepting/promoting a Hypothesis | No | Yes | Yes. |
| Changing hypothesis lifecycle | Policy may validate allowed transition | Yes | Yes for material promotion, rejection or retirement. |
| Labelling contradiction resolved | No | Yes | Yes. |
| Approving a strong Recommendation | No | Yes | Yes before strong or external use. |
| Generating external commercial asset | No | Yes | Yes. |
| Writing runtime learning back | No | Yes | Yes through repository governance. |

## 10. Persistence policy

Must persist: material candidate outputs, lineage metadata, validation results, user approvals/rejections, write-back proposals and audit records. May persist: session plans, narrative versions and presentation preferences when useful for audit or product experience. Normally transient: routine summaries, generated wording, comparison prose, regenerated briefs and session-specific answers.

Persistable learning includes new or changed Observations, evidence-backed relationships, material Signals, candidate or revised Hypotheses, Contradictions, Unknowns, evidence demands, explicit human judgements, commercial outcomes and learning events.

## 11. Write-back architecture

```text
Runtime candidate
→ validation
→ human or policy review
→ repository change
→ governance
→ acceptance
→ re-ingestion
```

Flora must not silently rewrite authoritative repository assets. Runtime learning becomes governed Enterprise Knowledge only through a repository change that references originating candidate IDs, validation results and reviewer decisions.

## 12. Provenance and audit

For every material reasoning output, Flora retains initiating user or trigger, time, source asset IDs, retrieved context package, worker identity, model identity/version where available, instruction or task version, structured output, validation results, confidence, lifecycle status, human intervention and supersession/rejection. Auditability focuses on inputs, outputs, rules, lineage and decisions; unrestricted private hidden model reasoning is not required.

## 13. Failure and uncertainty behaviour

| Condition | Safe behaviour |
| --- | --- |
| Evidence absent | Return Unknown and evidence demand. |
| Evidence stale | Downgrade confidence and prefer monitor/gather evidence. |
| Sources disagree | Preserve Contradiction; do not collapse. |
| Relationships do not resolve | Block durable relationship and mark relationship Unknown. |
| GPT worker invalid output | Reject output, retry within policy or use deterministic fallback. |
| No hypothesis meets thresholds | Present learning/deferment, not selling. |
| Executive ownership unknown | Use role-level audience or Unknown; do not invent names. |
| Human knowledge conflicts with evidence | Preserve labels, source dates and Contradiction until reviewed. |
| Runtime dependency unavailable | Fail closed; do not corrupt governed knowledge. |

## 14. Strategic Sales experience contract

Flora supports:

- **Explore:** industry change, pressures, affected participant types and evidence gaps.
- **Focus:** selected enterprise exposure, mechanisms, Observations, Hypotheses, Contradictions and Unknowns.
- **Shape:** executive relevance, commercial assessment and proportionate next action.

It answers **Who? Why now? Why them? What evidence? What next?** without requiring Strategic Sales Directors to understand manifests, repository paths or schemas. Lineage remains inspectable behind the experience.

## 15. Banking reference journey

Representative journey using existing governed Banking assets:

```text
Banking industry change
→ priority pressure
→ affected participant types
→ selected enterprise
→ enterprise-specific observations
→ competing hypotheses
→ contradictions and Unknowns
→ relevant executive audience
→ proportionate next action
```

Available governed assets include the Banking Industry Twin, Banking Industry Foundation, Banking Mechanisms and Tensions Model, UK Banking Payments Infrastructure Twin, enterprise twins for Barclays, Lloyds, NatWest, Nationwide/Virgin Money, Santander UK, Starling and Monzo, the Banking Reinvention Hypotheses v0.1 candidate register, Four-Bank Mechanism Differential Matrix and the Banking Knowledge Register for Flora.

Minimum example: select Banking; select an existing Banking pressure from governed industry/tension assets; select a governed enterprise such as Barclays or NatWest; retrieve enterprise-specific Observations and candidate hypotheses where present; run one challenge pass; preserve any missing executive ownership as an Unknown; produce a proportionate next action such as gather evidence, monitor, engage executive or defer according to lineage. This paper does not invent unsupported Banking facts.

Authoritative Banking Strategic Sales Navigation inputs were subsequently located on this branch and reviewed:

- `BK-FLR-SSN-SPEC-001` — `enterprise-knowledge/banking/flora/Banking-Strategic-Sales-Navigation-Specification.md`.
- `BK-GOV-SSN-VAL-001` — `enterprise-knowledge/banking/governance-reports/Banking-Strategic-Sales-Navigation-Validation-Report.md`.
- `BK-GOV-SSN-COMP-001` — `enterprise-knowledge/banking/governance-reports/Banking-Strategic-Sales-Navigation-Completion-Report.md`.

The Banking specification preserves the Strategic Sales Director outcome, Explore/Focus/Shape modes, Who / Why now / Why them / What evidence / What next contract, evidence and contradiction controls, hypothesis lifecycle expectations, executive-specificity limits and proportional next-best action boundaries. The Banking validation report confirms repository discovery is partial but usable, runtime ingestion readiness requires derived journey views and direct relationship exposure, runtime UX validation is not proven by repository validation alone, and gaps remain around machine-addressable lineage, executive specificity and derived Flora views. These findings strengthen FEIR-001's hybrid architecture rather than altering the decision.

## 16. Security and access considerations

Architecture requirements: role-based access, enterprise confidentiality, labelled user-supplied knowledge, protection of sensitive commercial judgement, explicit model-provider boundaries, prompt/context leakage controls, cross-enterprise data isolation, restricted audit access and external output approval. External assets must be generated only from authorised context and approved recommendations.

## 17. Non-functional requirements

- **Explainability:** every material output exposes lineage and validation status.
- **Repeatability:** deterministic context packages and versioned worker tasks support rerun comparison.
- **Observability:** orchestration, validation, latency, cost and failure events are logged.
- **Model replaceability:** worker contracts isolate model providers.
- **Latency:** stage plans may skip irrelevant workers and use bounded context.
- **Cost control:** context limits, retry limits and worker selection are policy-controlled.
- **Resilience:** failure modes prefer uncertainty and deterministic fallback.
- **Versioning:** models, prompts/tasks, policies, context packages and outputs are versioned.
- **Testability:** fitness tests validate lineage, lifecycle and recommendation controls.
- **Portability:** repository source remains canonical; runtime graph can be rebuilt.
- **Extensibility:** new workers must implement the standard contract.
- **Rollback:** rejected or superseded candidates do not alter governed knowledge.
- **Data minimisation:** only necessary context is sent to workers/providers.

## 18. Evolution strategy

1. **Stage 1 — Governed GPT-assisted reasoning:** controlled context assembly, bounded workers, structured outputs, asset-ID lineage, deterministic validation and human review.
2. **Stage 2 — Policy-controlled intelligence:** freshness, recommendation thresholds, hypothesis lifecycle enforcement, contradiction effects and action downgrading.
3. **Stage 3 — Event-driven intelligence:** Observation changes trigger reassessment, hypothesis strengthening/weakening, monitoring and evidence demands.
4. **Stage 4 — Outcome-informed learning:** commercial outcomes, executive feedback, calibration, preserved historical record and controlled write-back.

## 19. Explicit non-goals

FEIR-001 v1.0 does not attempt to create artificial general intelligence, fully automate strategic selling, eliminate human judgement, encode all commercial reasoning deterministically, allow unrestricted autonomous agents, treat GPT prose as authoritative knowledge, build all Flora user-interface views or resolve every current Banking knowledge gap.

## 20. Runtime Intelligence Object Model

| Field | Requirement |
| --- | --- |
| Object class | Durable governed, candidate intelligence, derived runtime view or transient presentation. |
| Identifier | Stable runtime ID; durable objects retain canonical asset IDs. |
| Status | Draft, candidate, validated, rejected, accepted, superseded or transient as applicable. |
| Authority | Repository, Flora runtime, human reviewer or presentation layer. |
| Provenance | Source IDs, worker IDs, user/trigger, time and context package. |
| Confidence | Qualitative confidence with rationale and policy bounds. |
| Lifecycle | Governed lifecycle for accepted objects; candidate lifecycle for runtime objects. |
| Source relationships | Evidence, Observation, mechanism, hypothesis, enterprise and executive links. |
| Validation state | Not validated, passed, failed, downgraded, needs human review. |
| Persistence class | Must persist, may persist or normally transient. |

## 21. GPT Worker Contract

Standard interface fields: worker ID, task type, permitted context, required input schema, required output schema, lineage fields, confidence fields, Unknowns, Contradictions, validation errors, model metadata, prompt/task version, timeout and failure behaviour. Outputs must be machine-validated before presentation or persistence.

## 22. Architectural questions and answers

1. **Runtime graph:** Flora should maintain a runtime graph projection derived from Enterprise Knowledge plus runtime candidate state; whether this is physically separate or generated on demand remains an Architectural Unknown for implementation ADR.
2. **Durable classes:** Evidence, Observation, Enterprise, Executive, Capability, Programme, Mechanism, Enterprise Model, Industry Model, Behaviour Model, Hypothesis, Unknown and Contradiction are durable only under existing governed models.
3. **Human acceptance:** Candidate Observations, Relationships, Signals, Hypotheses, Commercial Assessments, strong Recommendations and write-back proposals require human acceptance when material.
4. **Confidence/freshness:** Deterministic policy services calculate and bound them; workers may provide rationale but not final authority.
5. **Model/worker versions:** Recorded in every material output audit record.
6. **Competing hypotheses:** Stored as separate candidate/accepted hypotheses with visible support, contradictions and lifecycle status.
7. **Recommendation display:** Display internally only after minimum lineage and validation; weak outputs display as learning actions.
8. **External sharing:** Requires human approval and external-output controls.
9. **User knowledge:** Enters as labelled annotation/candidate input with user, time, scope and confidence; governed only after acceptance.
10. **Learning write-back:** Proposed through validated candidate, review, repository change, governance, acceptance and re-ingestion.
11. **Subsequent ADRs:** Runtime graph persistence, recommendation policy acceptance thresholds, audit retention/privacy, external commercial asset approval and model-provider boundary.
12. **Minimum viable Banking implementation:** One industry, one pressure, small enterprise set, one to three hypotheses, asset-ID lineage, one challenge pass, one next-action policy and human confirmation.

## 23. Minimum vertical prototype

Prototype journey:

```text
Select Banking
→ select one pressure
→ view affected enterprises
→ select one enterprise
→ inspect one hypothesis
→ inspect supporting and contradicting evidence
→ identify likely executive audience
→ receive a proportionate next action
```

Initial scope: one industry, one pressure, a small set of enterprises, one to three hypotheses, explicit asset-ID lineage, one challenge pass, one next-action policy and human confirmation. It is not a complete Flora product.

## 24. Architectural fitness tests

- No material Recommendation without hypothesis lineage.
- No accepted Observation without evidence lineage.
- Unknowns survive every reasoning stage.
- Contradictions remain inspectable.
- Competing hypotheses are not silently collapsed.
- GPT outputs are marked candidate until validated.
- Every candidate output records its worker and source context.
- Unsupported executive specificity is not invented.
- Low-conviction outputs resolve to learning rather than selling.
- Reports may be regenerated without losing durable intelligence.
- Changing the GPT model does not alter authoritative historical records.
- Runtime failure does not corrupt governed knowledge.
- Repository write-back always uses governed change control.

## 25. Architecture diagrams

### System context

```text
Governed Repository / Enterprise Knowledge
        | governed assets and manifests
        v
Flora Runtime ---- Human Reviewers
        |              ^
        v              | approvals, judgements
Strategic Sales Experience
        |
        v
Explore / Focus / Shape users
```

### Runtime components

```text
Ingestion -> Runtime Graph Projection -> Reasoning Orchestrator
                                        |
                                        +-> GPT Worker Pool
                                        +-> Deterministic Policy Services
                                        +-> Audit Store
                                        +-> Presentation Layer
                                        +-> Write-back Queue
```

### Canonical reasoning flow

```text
Trigger -> Plan -> Retrieve -> Select Observations -> Interpret Mechanisms
 -> Assess Enterprise Context -> Generate Hypotheses -> Challenge
 -> Assess Executive Relevance -> Assess Commercial Action -> Validate
 -> Present -> Capture Learning
```

### Candidate-intelligence lifecycle

```text
Created -> Structured validation -> Policy validation -> Human review needed?
   |              |                      |
   |              v                      v
   |           Rejected/Downgraded    Accepted for runtime use
   |                                      |
   +--------------------------------------v
                              Superseded / proposed for write-back / retained
```

### Governed write-back flow

```text
Runtime Candidate -> Validation Evidence -> Reviewer Decision
 -> Repository Change -> Governance Review -> Accepted Knowledge
 -> Flora Re-ingestion -> Runtime Projection Updated
```

### Strategic Sales user journey

```text
Explore industry change -> Focus on enterprise exposure
 -> inspect hypothesis, evidence, Unknowns and Contradictions
 -> Shape proportionate next action
 -> approve, defer, monitor or request learning
```

## 26. Completion report

### Authoritative documents reviewed

CIOS Chief Architect Handbook, CIOS Reference Architecture, CIOS-AI, Accepted ADRs, Enterprise Knowledge Architecture, Enterprise Knowledge Production Protocol, EI-001, EI-002, EI-003, EI-012, FP-003, FP-009, EGM-001, CIOS Design Doctrine, Architecture Principles, Glossary, Document Map, Banking governed asset registers, available Banking twin/reinvention assets, `BK-FLR-SSN-SPEC-001`, `BK-GOV-SSN-VAL-001` and `BK-GOV-SSN-COMP-001` were reviewed. The earlier statement that the exact Banking Strategic Sales Navigation documents were not found was inaccurate for the committed repository state after the Banking branch merge.

### Existing decisions preserved

Observation primacy, Enterprise Model durable memory, CIRM/EI separation, labelled human knowledge, inspectable recommendation lineage, progressive assurance, structured-source-first acquisition, dual-speed financial intelligence, blueprint import boundaries, Enterprise Canvas navigation, evidence-governed reasoning runtime and Knowledge Pack exchange boundaries are preserved.

### Conflicts found

No accepted-architecture conflict was found. The Banking Strategic Sales Navigation documents exist on the current branch and expose no material conflict with FEIR-001. The previous Architectural Unknown about exact Banking source documents is resolved.

### ADR identifier and status

ADR-024 — Hybrid Enterprise Intelligence Runtime — Accepted.

### Owning architecture paper identifier and status

FEIR-001 — Flora Enterprise Intelligence Runtime Architecture v1.0 — Proposed.

### Documents created

- `architecture/decisions/ADR-024-Hybrid-Enterprise-Intelligence-Runtime.md`
- `architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md`

### Documents changed

- Architecture Decision Record index.
- Architecture Authority Registry.
- Document Map.
- Flora specification README.

### Principal decisions

Flora is a hybrid governed runtime; GPT workers are bounded; outputs are candidate until validated; deterministic controls own policy; strong Recommendations require lineage and human approval; durable learning writes back only through governance.

### Architectural Unknowns

Physical runtime graph design; final accepted recommendation thresholds; audit retention/privacy periods; external-output approval workflow details. The exact Banking Strategic Sales Navigation source document Unknown is resolved by `BK-FLR-SSN-SPEC-001`, `BK-GOV-SSN-VAL-001` and `BK-GOV-SSN-COMP-001`.

### Subsequent ADRs recommended

Runtime graph persistence, recommendation eligibility thresholds, audit retention and privacy, model-provider boundary and external commercial asset approval.

### Banking journey used

Banking industry change to selected pressure, affected participants, selected governed enterprise, enterprise observations, competing hypotheses, contradictions/Unknowns, executive audience and proportionate next action using available governed Banking assets.

### Minimum prototype scope

One industry, one pressure, small enterprise set, one to three hypotheses, asset-ID lineage, one challenge pass, one next-action policy and human confirmation.

### Validation performed

Repository search for AGENTS, ADR numbering, document-map conventions, authority registry conventions, Flora runtime architecture locations, Banking governed asset availability and specified authoritative source paths. Markdown links and duplicate ADR identifier checks were performed locally.

### Validation failures and corrections

No duplicate ADR identifier was found. A new Flora specifications directory was created because no governed Flora architecture-specification hierarchy existed under `architecture/specifications/`. Follow-up reconciliation found the Banking Strategic Sales Navigation documents in the merged current branch; the earlier missing-document statement was a validation timing/search discrepancy, not evidence that the assets were absent from committed repository history.

### Commit hash and PR reference

To be completed by the implementing agent after commit and PR creation.

### Chief Architect decisions still required

FEIR-001 specification acceptance; runtime graph persistence approach; recommendation policy promotion; audit retention/privacy constraints; external sharing approval boundary; implementation of Banking derived journey views and relationship exposure gaps.

## 21. Subordinate reasoning pipeline specification

[EIRP-001 — Enterprise Intelligence Reasoning Pipeline Specification](EIRP-001-Enterprise-Intelligence-Reasoning-Pipeline-Specification.md) defines the proposed operational stage contracts, runtime object contracts, lineage propagation, validation gates, recommendation eligibility rules and Banking walkthrough beneath this owning FEIR-001 architecture. FEIR-001 remains the owning runtime architecture; EIRP-001 must not be used as a competing architecture.
