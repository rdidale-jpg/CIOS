# EIRP-001 — Enterprise Intelligence Reasoning Pipeline Specification

**Document class:** Supporting Flora runtime specification  
**Status:** Proposed  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-18  
**Owning decision:** [ADR-024](../../decisions/ADR-024-Hybrid-Enterprise-Intelligence-Runtime.md)  
**Owning architecture:** [FEIR-001](FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md)  
**Authority:** Proposed operational reasoning contract subordinate to ADR-024 and FEIR-001. It does not supersede accepted Enterprise Intelligence, Founding Paper, ADR, Banking or Enterprise Knowledge authority.

## 1. Mission and doctrine

EIRP-001 defines how Flora converts a user question, runtime trigger or human review trigger into typed, inspectable, testable, interruptible, lineage-preserving, uncertainty-aware and commercially useful Enterprise Intelligence. It operationalises the chain:

```text
Enterprise Knowledge
→ Flora orchestration
→ bounded GPT workers or deterministic services
→ candidate intelligence objects
→ deterministic validation
→ Strategic Sales views
```

EIRP-001 preserves the governing doctrine:

- Evidence proves change.
- Observations remember change.
- Enterprise Models accumulate change.
- Reports are views.
- Observation remains the atomic commercial object.
- Living Commercial Digital Twins remain the durable core asset.
- Unknowns, Contradictions, competing hypotheses and human-supplied knowledge labels survive reasoning.
- Recommendations require inspectable lineage and proportionate human accountability.
- Where conviction is incomplete, Flora learns before selling.

## 2. Authoritative inputs reviewed

EIRP-001 was drafted against the following authoritative inputs and preserves their decisions: ADR-024, FEIR-001, CIOS Reference Architecture, CIOS-AI, Chief Architect Handbook, CIOS Design Doctrine, Architecture Principles, EI-001, EI-002, EI-003, EI-012, FP-003, FP-009, EGM-001, Glossary, Document Map, Banking Strategic Sales Navigation Specification, Banking Strategic Sales Navigation Validation Report, Banking Reinvention Hypotheses, Banking Observation Register references, Banking mechanism material, and Banking Industry and Enterprise Twins.

No accepted-architecture conflict was identified. The main unresolved governance issue is policy ownership for confidence, recommendation thresholds, runtime persistence and human approval workflows; these are recorded as Architectural Unknowns rather than decided here.

## 3. Scope and non-goals

EIRP-001 defines pipeline stages, object contracts, lineage rules, validation gates, orchestration rules, stopping conditions, failure behaviour, observability, persistence boundaries, review points, worker responsibilities, Banking walkthrough, prototype contract and acceptance tests.

EIRP-001 does not redesign FEIR-001, define frontend technology, invent Banking knowledge, prescribe one LLM provider, encode hidden model chain-of-thought, replace governed Observations or Hypotheses with generated prose, create arbitrary commercial scoring, or automate strong Recommendations without governed policy and human controls.

## 4. Canonical pipeline

```text
Question or Trigger
→ Intent Analysis
→ Context Planning
→ Knowledge Retrieval
→ Observation Selection
→ Mechanism Analysis
→ Enterprise Context Assessment
→ Competing Hypothesis Assessment
→ Challenge and Contradiction Analysis
→ Executive Relevance Assessment
→ Commercial Assessment
→ Recommendation Eligibility
→ Presentation
→ Learning Capture
```

The pipeline supports full execution, partial execution, stage skipping, early stopping, branching, comparison paths, re-entry when new evidence arrives, human interruption and deterministic rejection of invalid output. The orchestrator records skipped stages where the skip affects confidence, output eligibility or audit.

## 5. Entry types

| Entry type | Required metadata | Identity | Scope | Expected confidence | Permitted output class | Audit requirements |
| --- | --- | --- | --- | --- | --- | --- |
| User question | `question`, `user_role`, `initiated_at`, requested answer class, target industry/enterprise/hypothesis/time scope when known | Authenticated user or delegated session | User-selected or inferred, then validated | As requested, but constrained by evidence | Transient view, derived runtime assessment, evidence demand, candidate intelligence, recommendation eligibility result | Run start, intent, access context, clarifications, output and user-visible caveats |
| Runtime trigger | Trigger event ID, trigger type, affected asset IDs, source system, freshness/policy rule, timestamp | System/service identity | Triggered assets plus configured dependency radius | Policy-defined minimum for trigger type | Derived assessment, evidence demand, candidate relationship, candidate hypothesis update, monitoring output | Trigger provenance, policy version, affected IDs, validation and stop/continue decision |
| Human review trigger | Review request ID, reviewer role, challenged object IDs, reason, requested action | Named reviewer or governance role | Reviewed object and dependent reasoning paths | Reviewer-specified or policy minimum | Review decision, candidate update, contradiction, Unknown, change proposal or transient explanation | Reviewer identity, rationale, before/after status, human-supplied labels and approval event |

## 6. Standard runtime envelope

The envelope is implementation-neutral and may be represented as YAML, JSON or typed records. Mandatory fields are marked **M**; conditional fields are **C**; optional fields are **O**.

| Field | Status | Semantics |
| --- | --- | --- |
| `run_id` | M | Stable identifier for this pipeline execution. |
| `parent_run_id` | O | Prior run for re-entry, branch or reassessment lineage. |
| `trigger_type` | M | `user_question`, `runtime_trigger` or `human_review_trigger`. |
| `initiated_by` | M | User, reviewer, service or policy identity. |
| `initiated_at` | M | Timestamp for audit and freshness calculations. |
| `user_role` | C | Required for user and review-triggered Strategic Sales outputs. |
| `question` | C | Natural-language question, review request or trigger summary. |
| `intent` | C | Intent Object after Intent Analysis; absent only before stage 1. |
| `industry_scope` | C | Industry identifiers or explicit Unknown. |
| `enterprise_scope` | O | Enterprise IDs, participant types or Unknown. |
| `hypothesis_scope` | O | Governed or candidate hypothesis IDs under assessment. |
| `time_scope` | C | Evidence horizon, freshness requirement or default policy horizon. |
| `authority_context` | M | Authority rules, accepted/candidate boundaries and lifecycle constraints. |
| `permitted_sources` | M | Source classes and asset IDs the run may use. |
| `restricted_sources` | M | Exclusions, access-limited assets and provider-boundary limits. |
| `required_output` | M | Output class requested or selected by policy. |
| `confidence_requirement` | M | Qualitative requirement or explicit user demand, bounded by policy. |
| `human_review_requirement` | M | Required, optional, not required or triggered-by-condition. |
| `pipeline_version` | M | Version of EIRP pipeline and stage contracts. |
| `policy_version` | M | Version of access, confidence, recommendation and validation policies. |

## 7. Stage contract standard

Every stage returns structured output only. Unclassified prose may be displayed as transient explanation but never becomes authoritative intelligence.

Each stage contract includes: stage ID; purpose; responsible component or worker; permitted inputs; required inputs; prohibited inputs; required output object; output status; lineage requirements; confidence requirements; Unknown handling; Contradiction handling; deterministic validations; failure conditions; retry, timeout and escalation behaviour; persistence classification; human review requirement; and observability events.

## 8. Stage definitions

| Stage | Purpose | Responsible component / worker | Required output | Deterministic validations | Failure, review and persistence rules |
| --- | --- | --- | --- | --- | --- |
| EIRP-S01 Intent Analysis | Determine what the question or trigger asks Flora to do. Distinguish Explore, Focus and Shape; explanation, comparison, validation, hypothesis generation, recommendation and evidence demand; ambiguity and clarification need. | Intent Analyst or deterministic classifier | Intent Object | Valid intent type, answer class, scope fields, confidence need and ambiguity flags; no unsupported target IDs | If ambiguous, request clarification or downgrade to Explore. Persist intent audit; normally transient. |
| EIRP-S02 Context Planning | Create smallest sufficient retrieval and reasoning plan without unrestricted repository retrieval by default. | Context Planner | Context Plan | Required asset classes, relationship types, time horizon, authority constraints, worker/stage sequence, skips, comparison sets and likely failure points are present | Invalid or over-broad plans are rejected once and retried; persistent as audit context. |
| EIRP-S03 Knowledge Retrieval | Retrieve governed and permitted context, prioritising structured Enterprise Knowledge over raw prose. | Retrieval service plus Context Planner | Retrieval Set | Asset IDs resolve; authority, path, relationship, freshness, access and completeness recorded; raw evidence distinguished from accepted Observations | No assets causes early stop with Unknown/evidence demand. Broken relationships remain unresolved references. |
| EIRP-S04 Observation Selection | Select relevant governed Observations and identify evidence gaps. | Observation Analyst | Observation Selection | Observation IDs exist and are accepted/candidate as labelled; evidence IDs and temporal coverage present; no Recommendation emitted | No relevant Observation stops recommendation path. Candidate Observation may be proposed only as candidate. |
| EIRP-S05 Mechanism Analysis | Identify mechanisms plausibly explaining selected change while keeping mechanisms distinct from Observations. | Mechanism Analyst | Mechanism Assessment | Mechanism IDs resolve; observation-to-mechanism links present; alternatives and applicability conditions retained | Missing mechanism creates Unknown/evidence demand; no durable mechanism creation. |
| EIRP-S06 Enterprise Context Assessment | Assess how observations/mechanisms apply to an enterprise or participant type. | Enterprise Context Analyst | Enterprise Context Assessment | Enterprise/participant IDs resolve; industry-wide, participant-type and enterprise-specific inference levels separated | Unsupported enterprise specificity is rejected; missing evidence downgrades Why them. |
| EIRP-S07 Competing Hypothesis Assessment | Retrieve, compare or generate candidate hypotheses. | Hypothesis Analyst | Hypothesis Comparison and Candidate Hypothesis extensions when needed | Existing hypotheses are not rewritten; candidate hypotheses labelled; observation lineage required; falsification conditions present | Missing Observation lineage prevents assessment; lifecycle changes require review. |
| EIRP-S08 Challenge and Contradiction Analysis | Actively test and weaken unsupported interpretations; preserve alternatives. | Hypothesis Challenger | Challenge Report | Contradictions, missing evidence, alternative explanations, weakening conditions and confidence adjustments present | Challenger cannot resolve contradictions; max loop governed by orchestration policy. |
| EIRP-S09 Executive Relevance Assessment | Determine who is likely to care and why. | Executive Relevance Analyst | Executive Relevance Assessment | Named executive requires governed evidence; otherwise role-level output plus Unknown; ownership evidence cited | Unsupported named person fails validation and is retried or downgraded. |
| EIRP-S10 Commercial Assessment | Assess commercial relevance without issuing a Recommendation. | Commercial Assessment Analyst | Commercial Assessment | Significance, urgency, exposure, timing, access, evidence completeness, ownership, appetite, Unknowns, Contradictions and permitted action range present; no arbitrary score | Low evidence downgrades to learning/gather evidence. Human judgement must be labelled. |
| EIRP-S11 Recommendation Eligibility | Determine permitted action classes by evidence and policy. | Recommendation policy service plus Commercial Assessment Analyst | Recommendation Eligibility Result | Enforces Evidence → Observation → Mechanism/Signal → Enterprise Context → Hypothesis → Commercial Assessment → Recommendation; prohibits raw-document Recommendations | Strong action requires human approval. Missing lineage yields learn, monitor, gather evidence, defer or reject. |
| EIRP-S12 Presentation | Create a transient Strategic Sales view answering Who, Why now, Why them, What evidence, Unknowns, Contradictions, What next and What not yet. | Narrative Worker | Strategic Sales Brief | Uses validated objects only; preserves confidence, lifecycle, lineage, Unknowns, Contradictions and human labels | Presentation cannot upgrade status. Normally transient; may persist as regenerated view/audit snapshot. |
| EIRP-S13 Learning Capture | Decide whether material learning should persist. | Learning Capture service plus reviewer where needed | Learning Capture Decision | Classifies transient, candidate runtime object, human annotation, evidence demand, candidate Observation/relationship/Hypothesis update, Contradiction, Unknown, commercial outcome or change proposal | No silent mutation. Write-back requires validation → review → change proposal → repository governance → acceptance → re-ingestion. |

All stages prohibit: hidden chain-of-thought as persisted rationale, unsupported IDs, unlabelled human knowledge, authority upgrades by a GPT worker, silent Unknown/Contradiction removal and direct repository mutation.

## 9. Runtime object schemas

These schemas define runtime extensions only. Canonical Evidence, Observation, Enterprise Model, Knowledge Graph, Behaviour Model, Hypothesis, Unknown and Contradiction semantics remain owned by their governing documents.

### 9.1 Common runtime header

```yaml
object_id: string
object_type: enum
run_id: string
status: enum[pending, completed, stopped, failed, rejected, needs_review]
authority: enum[retrieved_governed_object, derived_runtime_assessment, candidate_intelligence, human_supplied_judgement, policy_decision, accepted_governed_object, transient_presentation]
created_at: timestamp
created_by: worker_or_user_or_service_id
source_asset_ids: [string]
relationship_paths: [string]
confidence: enum[unknown, low, medium, medium_high, high]
freshness: string
unknowns: [UnknownRef]
contradictions: [ContradictionRef]
human_supplied_knowledge: [HumanKnowledgeRef]
validation_state: enum[not_validated, valid, invalid, needs_review]
persistence_class: enum[transient_only, runtime_audit, candidate_runtime_object, governed_change_proposal]
```

### 9.2 Object contracts

| Object | Required runtime extension fields |
| --- | --- |
| Question Object | `question_text`, `entry_type`, `requested_answer_class`, `requested_scope`, `user_role`, `clarification_state`. |
| Intent Object | `intent_type`, `mode`, `answer_class`, `target_flags`, `ambiguities`, `clarification_requirements`. |
| Context Plan | `asset_classes_required`, `relationship_types_required`, `time_horizon`, `authority_constraints`, `worker_sequence`, `stages_to_execute`, `stages_to_skip`, `comparison_sets`, `thresholds`, `likely_failure_points`. |
| Retrieval Set | `retrieved_assets`, `object_types`, `authority_status`, `source_locations`, `relationship_paths`, `access_classification`, `retrieval_completeness`, `unresolved_references`. |
| Observation Selection | `selected_observation_ids`, `relevance_rationale`, `supporting_evidence_ids`, `temporal_coverage`, `applicability`, `conflicting_observations`, `missing_observation_classes`, `evidence_demands`. |
| Mechanism Assessment | `mechanism_ids`, `observation_links`, `affected_capabilities`, `alternative_mechanisms`, `missing_relationships`, `contradicting_mechanisms`, `applicability_conditions`. |
| Enterprise Context Assessment | `enterprise_or_participant_ids`, `capabilities`, `programmes`, `operating_model_dependencies`, `behaviour_implications`, `strategic_ambition`, `transformation_appetite`, `timing_indicators`, `executive_ownership_indicators`, `inference_level`. |
| Candidate Hypothesis | `statement`, `scope`, `supporting_observations`, `supporting_mechanisms`, `affected_models`, `conviction`, `lifecycle_state`, `competing_explanations`, `required_evidence`, `falsification_conditions`, `candidate_label`. |
| Hypothesis Comparison | `hypothesis_ids`, `comparison_dimensions`, `supporting_lineage`, `contradicting_lineage`, `relative_readiness`, `preserved_alternatives`. |
| Challenge Report | `challenged_objects`, `contradictory_evidence`, `source_disagreement`, `missing_evidence`, `alternative_explanations`, `weakening_conditions`, `confidence_adjustment_proposal`, `evidence_demands`. |
| Executive Relevance Assessment | `role`, `named_executive_id`, `decision_ownership`, `programme_ownership`, `sponsor_influencer_blocker`, `executive_concern`, `affected_outcomes`, `evidence_source`. |
| Commercial Assessment | `commercial_significance`, `urgency`, `enterprise_exposure`, `timing`, `access`, `evidence_completeness`, `executive_ownership`, `transformation_appetite`, `opportunity_maturity`, `human_judgement`, `permitted_action_range`. |
| Recommendation Eligibility Result | `eligible_actions`, `eligibility_reason`, `required_lineage`, `evidence_sufficiency`, `approval_requirement`, `prohibited_stronger_actions`, `expiry_or_reassessment_trigger`. |
| Strategic Sales Brief | `question`, `current_interpretation`, `who_should_care`, `why_now`, `why_this_enterprise_or_participant`, `supporting_evidence`, `supporting_observations`, `mechanisms`, `competing_hypotheses`, `contradictions`, `unknowns`, `confidence_and_lifecycle`, `recommended_next_action`, `not_yet_actions`, `evidence_required_next`, `lineage`. |
| Learning Capture Decision | `learning_classification`, `materiality`, `candidate_objects`, `review_route`, `change_proposal_id`, `repository_write_back_allowed=false_until_governed`. |
| Pipeline Validation Result | `validated_object_ids`, `failed_object_ids`, `schema_results`, `policy_results`, `lineage_results`, `access_results`, `retry_count`, `stop_reason`. |

## 10. Authority and status rules

Permitted authority states are: retrieved governed object, derived runtime assessment, candidate intelligence, human-supplied judgement, policy decision, accepted governed object and transient presentation. GPT workers may not directly assign Accepted, Authoritative, Governed, Resolved Contradiction or Approved Recommendation unless a deterministic or human approval rule explicitly permits it. Candidate objects remain candidate even when the explanation is compelling.

## 11. Lineage propagation

Every derived object inherits source asset IDs, relationship paths, worker/component ID, model and version where applicable, task version, policy version, validation result, confidence, timestamp, human intervention and supersession. Lineage must trace back to Evidence, Observations, Mechanisms, Enterprise Models, Hypotheses and governing methodology. Narrative citations are helpful presentation affordances but cannot replace structured lineage.

Lineage transformation rules:

1. Retrieval establishes the permitted asset set.
2. Observation Selection narrows lineage to relevant Observations and supporting evidence.
3. Mechanism Analysis adds mechanism paths without collapsing them into Observations.
4. Enterprise Context adds enterprise, participant, capability and programme paths with inference level.
5. Hypothesis Assessment binds hypotheses to Observations and mechanisms.
6. Challenge adds contradicting and weakening paths.
7. Executive and Commercial Assessment add ownership, timing, access and judgement lineage.
8. Recommendation Eligibility records the complete eligibility chain and prohibited stronger actions.
9. Presentation renders lineage; it does not create lineage.
10. Learning Capture records supersession or proposed write-back lineage.

## 12. Confidence handling

Confidence states are qualitative: Unknown, Low, Medium, Medium-High and High. Worker confidence is advisory and must be constrained by source authority, freshness, lineage completeness, unresolved Contradictions, missing enterprise-specific evidence, missing executive evidence and candidate lifecycle. A derived object cannot be more authoritative than its strongest permitted source class; stale evidence constrains confidence; unresolved Contradictions reduce or block strong action; missing enterprise evidence downgrades Why them; missing executive evidence downgrades Who; and candidate status survives eloquent narrative.

## 13. Unknown and Contradiction preservation

Unknowns and Contradictions must survive stage transitions, remain linked to affected objects, influence recommendation eligibility, remain visible in the final Strategic Sales Brief, trigger evidence demands where material and never be silently resolved by narrative synthesis.

Valid resolution paths are: Unknown resolved by governed evidence; Contradiction explained with scoped evidence; Contradiction superseded by later accepted evidence; source invalidated by governance; scope difference established; or human judgement recorded and labelled. All resolutions require validation and audit, and material resolutions require human review.

## 14. Orchestration rules

Default dependency graph: S01 → S02 → S03 → S04 → S05 → S06 → S07 → S08 → S09 → S10 → S11 → S12 → S13. S05 and S06 may branch by mechanism or enterprise; S07 and S08 may loop within a challenge-loop limit; S09 may run in parallel with parts of S10 once enterprise context exists; S12 waits for validation of objects it presents.

Retries are limited by policy and never permit unvalidated output to advance. Model fallback may use another provider or deterministic service within access boundaries. Deterministic fallback returns structured Unknowns, evidence demands and lower action classes. Caches must be keyed by knowledge snapshot, policy version, access scope and freshness; restricted data must not leak through cache reuse.

Early stopping conditions include: no authoritative evidence found; no relevant Observation found; unresolved identity; enterprise specificity unavailable; worker output invalid after retry; hypothesis lineage insufficient; recommendation threshold not met; access policy denies required context; or human interruption. Early stops return the strongest justified learning outcome.

## 15. Failure behaviour

| Failure condition | Safe behaviour |
| --- | --- |
| Retrieval returns no assets | Return Unknown and evidence demand; no generated answer as intelligence. |
| Relationships are broken | Mark unresolved references; block dependent lineage. |
| Evidence is stale | Downgrade confidence; prefer monitor or gather evidence. |
| Sources disagree | Preserve Contradiction and alternative explanations. |
| Worker hallucinates unsupported ID | Reject output, retry with ID list, then escalate/stop. |
| Output schema invalid | Reject before downstream use. |
| Confidence fields absent | Reject or set Unknown with validation failure. |
| Worker omits Unknowns or Contradictions | Reject when material; otherwise inject carried-forward Unknowns/Contradictions and log downgrade. |
| Model service unavailable | Use deterministic fallback or stop transparently. |
| Policy service unavailable | Fail closed; no Recommendation or write-back. |
| User requests stronger certainty than evidence permits | Explain limit and downgrade. |
| Sensitive enterprise data restricted | Withhold restricted detail and record access-limited lineage. |

## 16. Human review points

Human review may be required to accept a candidate Observation, promote a candidate Hypothesis, change lifecycle state, resolve a Contradiction, confirm a named executive, approve a strong Recommendation, create an external-facing commercial asset or write learning back into governed Enterprise Knowledge. Reviewer roles include Analyst, Strategic Sales Director, Enterprise Intelligence Assurance reviewer and Chief Architect. Each review emits a `human_review_requested` and `human_review_decision_recorded` audit event with reviewer identity, scope, rationale, outcome and affected object IDs.

## 17. Worker responsibilities

| Worker | Stage ownership | Permitted context | Prohibited actions | Output schema | Validation and escalation |
| --- | --- | --- | --- | --- | --- |
| Intent Analyst | S01 | Question, trigger, user role, access scope | Answering substance, retrieving broad content | Intent Object | Schema check; ambiguity escalation. |
| Context Planner | S02 | Intent, asset index, authority/access policies | Unrestricted repository dump, final answer | Context Plan | Plan minimality/access validation. |
| Observation Analyst | S04 | Retrieval Set, governed Observation/evidence metadata | Accepting Observations, Recommendations | Observation Selection | ID/status/evidence validation; analyst review for candidates. |
| Mechanism Analyst | S05 | Observations, mechanism catalogue/tension model | Creating durable mechanisms | Mechanism Assessment | Mechanism ID and applicability validation. |
| Enterprise Context Analyst | S06 | Enterprise/participant twins and relationship paths | Inventing enterprise specificity | Enterprise Context Assessment | Inference-level validation. |
| Hypothesis Analyst | S07 | Observations, mechanisms, enterprise context, governed hypotheses | Rewriting governed hypotheses | Hypothesis Comparison/Candidate Hypothesis | FP-009 lifecycle and lineage checks. |
| Hypothesis Challenger | S08 | Hypotheses, contradictions, evidence gaps | Merely summarising support, resolving contradiction | Challenge Report | Contradiction/Unknown preservation check. |
| Executive Relevance Analyst | S09 | Roles, executives, programmes, capabilities | Inventing names/reporting lines | Executive Relevance Assessment | Named executive evidence check. |
| Commercial Assessment Analyst | S10/S11 support | Validated hypotheses, context, access, judgement labels | Direct sale from documents, arbitrary scoring | Commercial Assessment | Policy review and action downgrade. |
| Narrative Worker | S12 | Validated objects and presentation contract | Adding facts or changing status | Strategic Sales Brief | Presentation validation; fallback to structured view. |

A worker need not equal one model call. A deterministic service, specialist model or human may execute any stage if it returns the same typed contract.

## 18. Strategic Sales modes

| Mode | Likely intents | Required stages | Optional stages | Prohibited outputs | Minimum lineage |
| --- | --- | --- | --- | --- | --- |
| Explore | What is changing? Why does it matter now? Evidence demand | S01-S05, S08, S12-S13 | S06-S07 for selected themes | Enterprise ranking, strong Recommendation, named executive certainty | Evidence, Observations, mechanisms, Unknowns, Contradictions. |
| Focus | Which participant types or enterprises are exposed? Compare and assess timing | S01-S08, S10, S12-S13 | S09-S11 if action requested | Unsupported enterprise specificity, arbitrary scoring | Observation, mechanism, participant/enterprise inference-level, hypotheses, challenge lineage. |
| Shape | Why this enterprise? Who should care? What next? | S01-S13 | Branch comparisons and human review loops | Strong external action without approval; proposal without policy | Full Evidence → Observation → Mechanism/Signal → Enterprise Context → Hypothesis → Commercial Assessment → Recommendation chain. |

## 19. Banking reference walkthrough using BRH-003

BRH-003 is suitable because it is a real governed candidate Banking hypothesis with explicit supporting Observations, mechanisms, enterprise models, Contradicting Evidence, Unknowns, Confidence, Evidence Required and monitoring indicators.

Question: “What is changing in Banking, why does it matter, who should care, and what should I do next?”

| Pipeline point | Derived runtime view over governed assets |
| --- | --- |
| Intent Object | Mode: Shape with Explore opening. Answer class: explanation plus recommendation eligibility. Scope: UK Banking; participant type and enterprise specificity allowed only where evidenced. Required confidence: Medium or better for action; lower permitted for learning. |
| Context Plan | Retrieve `EK-BANK-RHYP-001`, BRH-003 section, Banking Industry Foundation, Banking Industry Twin, Banking Mechanisms and Tensions Model, Nationwide/Virgin Money Enterprise Twin, Lloyds Enterprise Twin, UK Banking Payments Infrastructure Twin, Banking Strategic Sales Navigation Specification and Validation Report. Execute all stages with one challenge pass; skip named-executive output unless governed evidence exists. |
| Retrieval Set | Asset IDs include `EK-BANK-RHYP-001`, `BRH-003`, `BK-OBS-014`, `BK-OBS-015`, `BK-OBS-016`, `BK-OBS-029`, `BK-OBS-047`, `BM-04`, `BM-02`, `BM-14`, `BM-15`, Banking Industry Foundation, Banking Industry Twin, Nationwide/Virgin Money Enterprise Twin, Lloyds Enterprise Twin, UK Banking Payments Infrastructure Twin, `BK-FLR-SSN-SPEC-001`, `BK-GOV-SSN-VAL-001`. |
| Observation Selection | Select BRH-003 supporting Observations only as governed references. Missing machine-addressable source-to-observation mappings from the Banking validation report become an evidence-demand caveat. No new Observation is accepted. |
| Mechanism Assessment | Mechanisms: assisted-access substitution (`BM-04`), current-account/distribution context (`BM-02` as cited by BRH-003), Consumer Duty outcome evidence (`BM-14`) and legacy complexity cost-to-income (`BM-15`). Keep physical-access trust, cost and inclusion mechanisms distinct. |
| Enterprise Context | Participant-type inference is stronger than enterprise-specific inference. Nationwide/Virgin Money supports a mutual branch/trust variant; Lloyds supports incumbent cost/simplification relevance. No unsupported named enterprise exposure ranking is produced. |
| Competing Hypotheses | Primary: `BRH-003`. Competing explanations preserved: branches may be primarily cost-removal levers; shared hubs may only partially substitute; digital engagement may reduce physical relevance. Candidate alternatives remain labelled candidate unless already governed. |
| Challenge Report | Contradiction: `BK-OBS-047` says branches can be both cost burdens and trust assets depending on participant type. Unknowns: shared-access economics, segment reliance, measurable retention/acquisition effect and regulatory/political pressure. Downgrade: do not proceed to proposal. |
| Executive Relevance | Role-level only unless enterprise-specific governed executive evidence exists. Likely roles: Retail Banking / Distribution, Customer Experience, Operations, Risk/Regulatory/Consumer Duty, Transformation. Named executives remain Unknown. |
| Commercial Assessment | Commercial significance: material where branch strategy, assisted access, vulnerable customer service, cost-to-income or Consumer Duty evidence are live issues. Urgency: Medium where closures/hubs/regulatory pressure are current; enterprise-specific urgency requires fresh evidence. |
| Recommendation Eligibility | Permitted: gather evidence, validate with executive, shape discovery conversation, monitor. Prohibited stronger actions: shape workshop, develop proposal, external provocation without human approval and enterprise-specific proof. |
| Strategic Sales Brief | Present a derived runtime view with Who / Why now / Why participant type / Evidence / Observations / Mechanisms / Competing hypotheses / Contradictions / Unknowns / Next action / Not yet. |
| Learning Capture Decision | Persist runtime audit, evidence demands for BRH-003 and possible human annotation. No governed repository mutation; any candidate update requires change proposal. |

## 20. Example Strategic Sales Brief structure

The following is a derived runtime view, not accepted Banking knowledge:

```markdown
# Strategic Sales Brief

## Question
What is changing in Banking, why does it matter, who should care, and what should I do next?

## Current interpretation
Physical and assisted access may be shifting from proprietary branch distribution toward a mixed trust infrastructure of branches, shared hubs, Post Office access and participant-specific models.

## Who should care
Role-level: Retail Banking / Distribution, Customer Experience, Operations, Risk / Consumer Duty and Transformation leaders. Named executive: Unknown unless governed enterprise evidence exists.

## Why now
The hypothesis is supported by governed Banking observations about app-first but not app-only banking, assisted access and branch cost/trust tension.

## Why this enterprise or participant type
Participant-type inference: incumbents face cost and access pressure; building-society/mutual variants may treat branches as trust assets. Enterprise-specific proof is required before stronger claims.

## Supporting evidence
Governed Banking assets only; raw evidence remains distinct from Observations.

## Supporting Observations
BK-OBS-014; BK-OBS-015; BK-OBS-016; BK-OBS-029; BK-OBS-047.

## Mechanisms
BM-04; BM-02; BM-14; BM-15.

## Competing hypotheses
Branch reduction as cost simplification; shared access as incomplete substitute; digital engagement as sufficient replacement.

## Contradictions
BK-OBS-047: branches may be cost burdens or trust assets depending on participant type.

## Unknowns
Shared access economics; customer segment reliance; measurable retention/acquisition effect; regulatory or political access pressure; named executive ownership.

## Confidence and lifecycle
Medium-High candidate hypothesis; action confidence downgraded by enterprise and executive Unknowns.

## Recommended next action
Gather evidence and validate with the relevant role-level executive stakeholder before shaping a workshop.

## What should not yet be done
Do not develop a proposal, assert named ownership or claim enterprise-specific urgency without governed evidence and approval.

## Evidence required next
Branch/hub usage, cost-to-serve, retention/acquisition effect, regulatory obligations and enterprise-specific ownership evidence.

## Lineage
EK-BANK-RHYP-001 → BRH-003 → BK-OBS-014/015/016/029/047 → BM-04/BM-02/BM-14/BM-15 → participant-type context → challenge report → commercial assessment → recommendation eligibility.
```

## 21. Observability and audit

Required events: run started; intent classified; context plan created; retrieval completed; worker invoked; worker output received; schema validation; policy validation; challenge completed; human review requested; recommendation allowed or downgraded; presentation produced; learning captured; run stopped; run failed.

Minimum metrics: duration by stage; token/model cost where available; retrieval count; relationship resolution failures; invalid output count; retry count; Unknown count; Contradiction count; confidence downgrade count; human intervention count; recommendation downgrade count. Hidden private chain-of-thought is not stored.

## 22. Versioning and repeatability

Every run records pipeline version, stage-contract versions, worker task versions, schema versions, policy versions, model/provider versions, prompt or instruction versions, knowledge snapshot identifier and presentation template version. Historical inspection must survive model, prompt, policy and knowledge-domain changes. Repeatability means reproducible inputs, rules, validation and object outputs where practical, not identical generative wording.

## 23. Security and access

Pipeline controls cover role-based source access, enterprise confidentiality, cross-enterprise isolation, human-supplied knowledge labels, restricted evidence, model-provider context boundaries, prompt injection, unsupported external content, external sharing, audit visibility and data minimisation. Restricted data may influence an internal eligibility decision only within policy; it must not be exposed in a derived view merely because it contributed indirectly.

## 24. Recommendation eligibility matrix

Illustrative policy structure only; final thresholds require future governance.

| Evidence state | Hypothesis state | Executive relevance | Permitted action |
| --- | --- | --- | --- |
| Weak | Candidate | Unknown | Learn |
| Partial | Emerging | Role inferred | Gather evidence |
| Moderate | Strengthening | Role evidenced | Validate with executive |
| Strong | Validated | Named ownership evidenced | Shape workshop |
| Strong | Validated | Ownership and commitment evidenced | Develop proposal |

Policy areas requiring future ADR or methodology decision: confidence ownership, threshold semantics, action classes that require human approval, external-facing asset approval, commercial outcome feedback, expiry rules and whether any numeric score is allowed.

## 25. Minimum vertical prototype contract

Prototype scope: one industry, Banking; one user role, Strategic Sales Director; one question; one pressure/change theme; one to three hypotheses; one challenge pass; one enterprise or participant comparison; one executive relevance assessment; one Recommendation Eligibility decision; one Strategic Sales Brief; full asset-ID lineage; human confirmation.

The prototype must visibly expose each stage input, output, status, confidence, Unknowns, Contradictions, lineage, validation result and duration. It does not require production UI, multi-industry support, autonomous continuous monitoring, automated repository write-back, complex scoring or complete user management.

## 26. Acceptance and fitness tests

| ID | Acceptance criterion | Test type |
| --- | --- | --- |
| EIRP-AT-001 | A Recommendation cannot be created without Hypothesis lineage. | Machine |
| EIRP-AT-002 | A Hypothesis cannot be assessed without Observation lineage. | Machine |
| EIRP-AT-003 | An accepted Observation cannot be fabricated by a worker. | Machine |
| EIRP-AT-004 | Unsupported asset IDs fail validation. | Machine |
| EIRP-AT-005 | Unknowns survive all relevant stage transitions. | Machine/Human |
| EIRP-AT-006 | Contradictions remain visible in the Strategic Sales Brief. | Machine/Human |
| EIRP-AT-007 | Competing hypotheses are preserved. | Human |
| EIRP-AT-008 | Missing enterprise evidence downgrades Why them. | Machine/Human |
| EIRP-AT-009 | Missing executive evidence prevents unsupported named-person output. | Machine |
| EIRP-AT-010 | Low conviction results in learning or evidence gathering. | Machine |
| EIRP-AT-011 | Worker prose cannot bypass typed output validation. | Machine |
| EIRP-AT-012 | Runtime failure does not mutate governed knowledge. | Machine |
| EIRP-AT-013 | A historical run records model, policy and pipeline versions. | Machine |
| EIRP-AT-014 | Human-supplied knowledge is labelled. | Machine/Human |
| EIRP-AT-015 | External-facing asset generation requires correct approval. | Machine/Human |
| EIRP-AT-016 | The Banking walkthrough resolves all cited IDs. | Machine |
| EIRP-AT-017 | Reports can be regenerated without changing durable intelligence. | Machine |
| EIRP-AT-018 | Repository write-back is represented only as a governed proposal. | Machine |
| EIRP-AT-019 | The user receives Who / Why now / Why them / What evidence / What next. | Human |
| EIRP-AT-020 | The user is shown what should not yet be done. | Human |

## 27. Architectural Unknowns

Unresolved decisions requiring Chief Architect, ADR, methodology or implementation governance: runtime graph persistence; graph technology; event model; confidence policy ownership; recommendation threshold ownership; worker implementation pattern; model-provider boundary; audit retention; privacy and commercial sensitivity; human approval workflow; external commercial asset controls; write-back mechanism; runtime identity resolution; caching; cost limits; latency target; prompt-injection controls; production profile membership for EIRP-001; and FEIR-001 acceptance timing.

## 28. Governance registration and validation

Ownership chain:

```text
ADR-024
→ FEIR-001
→ EIRP-001
```

Dependencies: EI-012, FP-009, EGM-001 and Banking Strategic Sales Navigation assets. EIRP-001 is registered in the Flora specification index, Document Map and Architecture Authority Registry as Proposed, excluded from production profiles pending governance. FEIR-001 references EIRP-001 as its subordinate operational reasoning pipeline specification.

Validation performed locally for this commission: duplicate EIRP ID search, ADR-024/FEIR-001 consistency review, Banking BRH-003 ID review, required local link/path checks, register updates and repository status review. No material conflict with ADR-024 or FEIR-001 was found.
