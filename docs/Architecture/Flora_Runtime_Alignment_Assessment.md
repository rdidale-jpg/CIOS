# Flora Runtime Alignment Assessment

## 1. Executive Summary

Flora is currently a deterministic evidence-led commercial-intelligence runtime with three overlapping product lines: seeded daily/weekly briefs, Living Commercial Case Files, and the Enterprise Transformation Observatory. The strongest implemented capabilities are governed public-source collection into local JSONL receipts, deterministic evidence extraction with specificity gates, explicit missing-evidence language, score explainability, and an Observatory reasoning chain that separates Evidence, Signals, Insights, Transformation Theses, Commercial Arguments and Executive Recommendations. The runtime is intentionally dependency-light: tests prohibit LLM and database imports across Flora paths.

The current runtime is not yet a living Commercial Digital Twin. Its durable memory is local append-only JSONL evidence, diagnostics, feedback and logbook records. Enterprise state is reconstructed at run time from seeded fixtures and live receipts rather than incrementally persisted as an Enterprise Model. Reports and UI pages are increasingly model-backed, especially the Observatory, but the Publisher and Workspace still assemble briefings directly from generated runtime objects and can become de facto memory when exported.

Most material gaps are: no durable Enterprise Model repository; no first-class persisted Observation object; no persisted Observation-to-model update lifecycle; partial and mostly generated Knowledge Graph edges; no explicit Contradiction object; incomplete human-supplied knowledge governance; and outcome/learning records that are captured but not yet applied as governed model updates.

Assessed maturity: **Level 1 — Evidence Intelligence, with partial Level 2 and Level 3 object-shape experiments**. Flora is beyond a raw Evidence Collector because it stores evidence receipts, rejects weak evidence, exposes confidence/freshness, and derives inspectable signals and theses. It is not yet an Enterprise Model Platform because model state is not durable, historical, incrementally updated or contradiction-aware.

Recommended next sprint: **Observation-to-Enterprise Memory Foundation**. The sprint should persist atomic Observation records derived from accepted Evidence and use them to update a minimal durable Enterprise Model snapshot with lineage, freshness, confidence, unknowns and supersession/contradiction hooks. This comes before richer recommendations, outcome learning or prediction because those layers need durable, inspectable memory rather than regenerated report state.

## 2. Scope and Method

Repository inspection included `cios/applications/flora`, `cios/applications/flora/live`, `cios/applications/flora/intelligence`, `cios/applications/flora/observatory`, `cios/applications/flora/publisher`, `cios/applications/flora/workspace`, `tests`, `docs/Architecture`, `docs/Applications`, and the architecture baseline under `architecture`.

Architecture baseline followed: `CIOS-AI.md` was requested but not found by repository search; the reference architecture README, v1.0 reference architecture, design doctrine, architecture principles, glossary, document map, Chief Architect Handbook, ADR-001 through ADR-008, FP-003, FP-009, EI-001, EI-002, EI-003 and EI-012 were present and reviewed. Existing Flora docs reviewed included `docs/Applications/Flora_v0.1.md`, `docs/Applications/Flora_Case_Files.md`, `docs/Applications/Flora_Live_Evidence_v0.1.md`, `docs/Applications/Flora_Pilot_Workspace_v0.3.md`, `docs/Architecture/CIRM_Runtime_Compliance.md`, `docs/Architecture/Flora_Product_Maturity_Review.md` and `docs/Architecture/Flora_Runtime_Alignment_Audit.md`.

Assessment states: **Aligned**, **Partially aligned**, **Missing**, **Conflicting**, **Unverified**, **Not currently required**. Severity levels: **Critical**, **High**, **Medium**, **Low**.

Validation performed: repository status and branch inspection; concept searches for Evidence, Observation, Enterprise Model, Digital Twin, Signal, Hypothesis, Thesis, Conviction, Recommendation, Unknown, Contradiction, lineage, freshness, decay, confidence, outcomes and learning; report/AI-generation path searches; persistence searches; runtime code review; test review; and targeted pytest execution.

Known limitations: no production database, deployment logs or external service state were inspected; local `.flora_pilot` runtime files are intentionally gitignored and were not treated as authoritative repository evidence; runtime behaviour behind live network collection was assessed from code and tests, not a live internet run.

## 3. Current Runtime Map

Current flow is:

```text
Governed source registry / seeded fixtures
→ synchronous HTML collection or seeded signal loading
→ JSON/dict Evidence receipts and seeded CommercialEvidence
→ deterministic extraction, gating, scoring and Observatory object construction
→ local JSONL evidence/diagnostics/feedback persistence; transient in-memory Observatory
→ deterministic scores, score adjustments and signals
→ RecommendedAction / ExecutiveRecommendation text
→ daily, weekly, case-file, publisher, workspace and Observatory views
→ user feedback/logbook capture
→ partial learned-score adjustment, but no durable model update lifecycle
```

**Source.** Live sources are governed by allow-listed `SourceRecord` objects and enabled-source filtering. Seeded signal and case-file data remain a major input path.

**Collection.** `collect()` fetches each enabled source synchronously, extracts evidence, writes evidence and diagnostics JSONL, and returns a summary. There is no queue, database or crawler.

**Evidence.** Live evidence receipts include IDs, source URL/name/type, source tier, snippet, cleaned observation, commercial condition, capability, confidence, evidence dossier, extraction timestamp and missing evidence. Seeded `CommercialEvidence` includes attribution, confidence, freshness, dossier, related signals/patterns/playbooks/propositions and tags.

**Interpretation.** Interpretation is deterministic code, not LLM prompts. The extractor maps keywords to commercial conditions and capabilities, recalibrates confidence, rejects boilerplate/context-only evidence and creates evidence dossiers. The Observatory then derives Commercial Signals, Insights, Theses, Arguments and Recommendations in memory.

**Persistence.** Durable persistence is JSONL: `.flora_pilot/live_evidence/live_evidence.jsonl`, diagnostics JSONL, feedback JSONL and logbook JSONL. There are no migrations and tests explicitly guard against database imports.

**Scoring.** Seeded scores are calculated from signal strength, confidence, freshness, priority, sector fit, incumbents and competitors. Live score adjustment adds live evidence, learned evidence and Rob score adjustment while applying missing-evidence penalties.

**Recommendation.** Legacy daily briefs create `RecommendedAction` directly inside `build_assessment`. The Observatory creates `ExecutiveRecommendation` from commercial arguments only when confidence clears a threshold.

**Report / UI.** CLI reports, publisher editions, workspace pages and Observatory pages render generated objects. The Observatory is the most model-backed view; Publisher and Workspace still assemble reports from runtime generation and local evidence files.

**User action and learning.** Feedback and logbook records are append-only local JSONL. They can affect learned evidence scoring, but they do not yet update Observations, Hypotheses, Enterprise Models or recommendations as governed durable memory.

## 4. CIOS Architecture Layer Assessment

| Layer | Current implementation | Evidence | State | Gap / consequence | Severity | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| Source and Evidence | Governed source registry, fetcher, extractor, JSONL evidence store, seeded evidence. | `live/collect.py`, `live/extractor.py`, `live/store.py`, `intelligence/evidence_engine.py`, tests in `test_flora_live.py`. | Partially aligned | Good source/evidence discipline but local JSONL and seeded fallback limit durability and governance. | Medium | Preserve and make Evidence feed Observations. |
| Observation | Free-text `cleaned_observation`, extracted observations in evidence, and Observatory `CommercialSignal.observation`; no persisted atomic Observation model. | `live/extractor.py`, `evidence_engine.py`, `observatory/models.py`. | Partially aligned | Observations are embedded strings, not governed lifecycle objects. | Critical | Implement Observation records first. |
| Enterprise Model | Transient `OrganisationObservatory.enterprise_profile`, seeded BT profile, case files. | `observatory/models.py`, `observatory/engine.py`, `case_file.py`. | Partially aligned | No durable per-enterprise model state or incremental update. | Critical | Persist minimal Enterprise Model snapshot. |
| Enterprise Knowledge Graph | In-memory `KnowledgeGraphEdge` with source/target/reasoning/confidence. | `observatory/models.py`, `_graph_edges`. | Partially aligned | No graph store, temporal edge lifecycle, query layer or contradiction node model. | High | Defer until observations/model are durable. |
| Behaviour and Dynamics | ForceAssessment, GenomeDimension, TransformationWindow, weather, TII labels. | `observatory/models.py`, `_organisation`, `_weather`. | Partially aligned | Dynamics are regenerated calculations, not accumulated history. | High | Persist model state before expanding prediction. |
| Commercial Reasoning | Signals, Insights, Theses, Arguments and Recommendations are explicit in Observatory. Legacy pipeline collapses them. | `observatory/models.py`, `pipeline.py`. | Partially aligned | Split between stronger Observatory path and weaker daily-brief path. | High | Route recommendations through lineage objects. |
| Prediction and Opportunity | TransformationWindow and opportunity wording exist, but no predictive validation loop. | `observatory/models.py`, `engine.py`, `opportunity_shaping.py`. | Partially aligned | Risk of false precision if predictions mature before memory. | Medium | Defer. |
| Executive Intelligence | Executive owner heuristics and board-level case-for-change views. | `_executive_for`, `_executive_owners`, `CaseForChange`. | Partially aligned | Ownership is inferred and often unknown; no correction lifecycle. | Medium | Add labelled human correction later. |
| Runtime and Product | CLI, web/workspace/publisher views; deterministic tests; no LLM/db imports. | `main.py`, `workspace`, `publisher`, tests. | Aligned for current maturity | Product is report/workspace-oriented, not a durable twin platform. | Medium | Preserve while adding memory foundation. |

## 5. Intelligence Object Inventory

| Runtime object | Architecture equivalent | Storage/lifecycle | Lineage/confidence/freshness | Downstream use | Coverage and concerns |
| --- | --- | --- | --- | --- | --- |
| `Signal` | Early signal / seeded evidence proxy | In-memory seeded Pydantic object | Source, evidence text, confidence, strength, freshness, date | Scoring and daily briefs | Collapses evidence and signal concepts. |
| `EvidenceItem` | Evidence summary | In-memory in assessments | Source/date/related signal/confidence | Reports | Not persisted independently. |
| `CommercialEvidence` | Evidence | Seeded generated object | Source attribution, confidence, freshness, dossier, related IDs | Case files, insights | Strong shape but mostly seeded. |
| Live evidence dict | Evidence receipt / Observation candidate | JSONL durable local file | Source URL, snippet, cleaned observation, confidence, extraction timestamp, missing evidence | Aggregation, publisher, Observatory | Best durable runtime object; not typed as Observation. |
| `cleaned_observation` / `extracted_observation` | Observation candidate | Field inside Evidence | Evidence-local only | Displays, conversion to CommercialEvidence | Not atomic lifecycle object. |
| Observation Demand | Evidence demand / curiosity | Generated in acquisition plans and missing evidence lists | No persisted object | Source planning and reports | Partially present as strings. |
| `OrganisationObservatory` | Partial Enterprise Model view | In-memory regenerated | Evidence IDs, confidence, unknowns | Observatory UI | Not durable memory. |
| `enterprise_profile` dict | Enterprise profile / partial Digital Twin | In-memory, BT-specific seeded profile | Mixed known/inferred/unknown labels | Observatory page | Useful, not persisted, not generalized. |
| `KnowledgeGraphEdge` | KG edge | In-memory tuple | Evidence IDs, inferred flag, reasoning, confidence | Observatory | No graph repository or query API. |
| `CommercialSignal` | Signal | In-memory Observatory | Supporting evidence IDs, confidence, missing evidence, freshness | Insights/theses/UI | Aligned in Observatory path. |
| `CommercialInsight` | Pattern / hypothesis-like insight | In-memory | Supporting signal IDs, contradictory IDs, unknowns | Theses | No persisted lifecycle. |
| `ResearchHypothesis` | Hypothesis | In-memory generated notebook | Supporting/contradictory evidence IDs, status, confidence, last_updated | Observatory | Status exists but no review/update lifecycle. |
| `TransformationThesis` | Commercial Thesis | In-memory | Evidence, signals, insights, validation required, confidence | Arguments | Strong object shape but transient. |
| StrategicConviction | Commercial Conviction | In-memory | Facts, hypothesis, unknowns, evidence IDs | Case for change | Collapses conviction and action text. |
| `ExecutiveRecommendation` | Recommendation | In-memory | Argument IDs and confidence | Observatory UI | Stronger than legacy; lacks action type/expiry/outcome. |
| Unknowns | Unknown object | Tuples/lists/strings | Often carried near evidence/signals | UI/report language | Not first-class persisted object. |
| Contradictions | Contradiction object | Empty tuples/edge labels/counterarguments | Sparse | UI counterarguments | Not first-class; mostly absence/caveat. |
| Outcomes | Outcome / learning record | Feedback/logbook JSONL | Timestamp, action/comment/value | Learned scoring | Not linked to Recommendation lineage. |
| Learning records | Calibration | JSONL feedback/logbook and alignment feedback | Timestamped, target ID in some paths | Learned score adjustment | Not governed model learning. |

## 6. Durable Memory Assessment

Flora persists live evidence receipts, source diagnostics, feedback records and logbook records in local JSONL. Seeded evidence, daily briefs, case files, Observatory organisations, theses, arguments and recommendations are recreated from code and local evidence at run time. Enterprise state is therefore durable only as raw-ish evidence receipts and user feedback, not as a maintained Enterprise Model.

Reports are partially acting as memory. Published Markdown/HTML previews and generated case files contain executive summaries, recommended actions, missing evidence and evidence receipts. Because there is no persisted Enterprise Model, exported reports can become the human source of continuity even though doctrine says reports should be views.

The runtime cannot incrementally update an Enterprise Model because there is no model repository, no observation ledger, no supersession policy and no historical state table. New evidence can change regenerated Observatory snapshots and score adjustments, and the collection summary can explain snapshot deltas, but those deltas are not persisted as model history.

Using Flora can make future scoring somewhat better through feedback/logbook and Rob-score adjustments, but not yet through governed Observation/Enterprise Model learning.

## 7. Observation Alignment

Flora partially converts evidence into observation-like strings: `cleaned_observation`, `extracted_observation` and `CommercialSignal.observation`. The live extractor applies boilerplate gates, relevance gates, confidence recalibration, source quality and accepted/rejected classification before allowing evidence to support claims. The Observatory tests protect that strategic signals are independent from recommendations and reference evidence.

However, free-text observation fields do not satisfy full Observation doctrine. They are not persisted as first-class records, do not have lifecycle states, do not explicitly prohibit all speculation by schema, do not update durable Enterprise Model state, and do not preserve contradictory observations as independent durable objects. Reuse occurs only inside a single regenerated run.

Observation Demand exists as missing-evidence strings and acquisition-plan evidence demand, not as a persisted object with status, owner, source plan or resolution.

## 8. Enterprise Model and Commercial Digital Twin Alignment

Flora maintains partial enterprise profiles in generated case files and Observatory organisations. Identity, sector, evidence, pressure, capability themes, executive heuristics, confidence, unknowns and BT-specific profile dimensions are visible. The BT profile explicitly separates Known, Inferred and Unknown technology state.

Missing or weak areas include durable enterprise identity/profile history, governance, leadership correction, supplier ecosystem, procurement activity, model decay, contradiction objects, human-supplied calibration and incremental update behaviour. Transformation Pressure and Transformation Inevitability are generated dimensions, not persisted state. Opportunity Outlook is present as commercial opportunity/conversation wording, not a maintained model field.

Current runtime classification: **Evidence Intelligence and report/workspace generator with partial Enterprise Model views**. It is not yet a Commercial Digital Twin because the maintained core asset is not durable enterprise state.

## 9. Knowledge Graph Alignment

The Observatory has explicit `KnowledgeGraphEdge` records with source, relationship, target, evidence IDs, inferred flag, reasoning and confidence. `_graph_edges` links evidence to signals, insights, theses, arguments and recommendations. This is a meaningful in-memory graph-shaped lineage capability.

It is not yet a genuine Enterprise Knowledge Graph capability: edges are not persisted, queryable across runs, temporal, versioned, human-labelled or contradiction-aware as objects. It is best assessed as a deterministic lineage graph inside a report-generation pipeline.

## 10. Commercial Reasoning Alignment

The Observatory path distinguishes Evidence, Signal, Insight, Transformation Thesis, Commercial Argument and Executive Recommendation. It also uses ResearchHypothesis objects. This is the strongest architecture alignment in the runtime.

The legacy daily-brief path collapses seeded signals, scoring, assessment prose and recommended actions inside `build_assessment`. It does not require thesis or argument lineage before creating a recommended action. Hypotheses outside the Observatory have no lifecycle states, review dates, strengthen/weaken/reject/retire behaviour or contradiction handling.

## 11. Recommendation and Lineage Assessment

Recommendation paths:

1. **Legacy daily/case-file path:** `build_assessment` creates a `RecommendedAction` from account, seeded signals, score, playbook heuristics and generated prose. It links to evidence through the assessment’s evidence list and related signal IDs, but not through Observation → Signal → Hypothesis → Thesis → Recommendation lineage. This is partially aligned and high risk for strong recommendation language if reused beyond pilot context.
2. **Case-file insights:** `generate_insights` emits recommended next steps from combined evidence IDs and assessments. These are learning/validation actions and are safer, but not typed as Recommendation objects with lifecycle.
3. **Observatory path:** `build_executive_recommendations` creates ExecutiveRecommendations only from CommercialArguments above confidence threshold. `_graph_edges` then connects recommendations back to arguments and evidence. This is the most aligned path, but still lacks action type, expiry/review, outcomes and persisted lineage.

Direct `Evidence → Recommendation` and `Prompt output → Recommendation` concerns: no LLM prompt path was found, but the legacy deterministic pipeline effectively goes `seeded Signal/Evidence → RecommendedAction` without durable intermediate reasoning objects.

## 12. Unknowns, Contradictions and Curiosity

Unknowns are visible throughout the runtime as tuples/lists: missing evidence on live receipts, signal missing evidence, force unknowns, genome unknowns, thesis validation required, case-for-change unknowns and report “cannot know” language. Acquisition plans turn coverage gaps into collection objectives.

Contradictions are weaker. Models include contradictory evidence IDs and counterarguments, and graph edges can use `contradicts_signal` for over-broad extrapolations. But no first-class persisted Contradiction object, resolution lifecycle or contradictory Observation preservation was found. Most uncertainty is still string-based and regenerated.

## 13. Human-Supplied Knowledge

Human-supplied knowledge appears as `CommercialDNA`, watchlist notes, known incumbents/competitors, Rob score adjustment, feedback records, logbook records and source-alignment feedback. Feedback/logbook records are timestamped and persisted locally. Rob score and learned scoring are visible in scoring UI.

Governance is incomplete. User notes and watchlist context are not consistently labelled as human-supplied, dated, attributed, scoped or sensitivity-aware. Human input can affect scoring and recommendations without a general provenance model that distinguishes it from external evidence. This is high architecture debt under ADR-004.

## 14. Report, Briefing and UI Alignment

| Surface | Classification | Assessment |
| --- | --- | --- |
| CLI Daily Brief | Report-first workflow | Renders generated daily brief and assessment objects; recommendation created in same pipeline. |
| CLI Weekly Brief | Report-first workflow | Recomputes movement and evidence from ranked items; movement is seeded/computed rather than historical state. |
| Living Case File | Partially model-backed view | Uses seeded CommercialEvidence, assessment, insights and timeline; stronger evidence structure but not durable model. |
| Publisher Morning Edition | Partially model-backed/report-first | Builds context from generated daily/weekly, live evidence, portfolio radar and shaping reports; exported edition can become memory. |
| Workspace | Partially model-backed UI | Reads live evidence and generated briefs; captures feedback/logbook; not a model editor. |
| Observatory | Best model-backed generated view | Renders explicit evidence/signals/insights/theses/arguments/recommendations with lineage, but objects are transient. |

Confidence and missing evidence are commonly visible. Unknowns are visible in Observatory and reports. Contradictions are mostly counterarguments. Recommendation action type and expiry/review are not consistently visible.

## 15. Scoring and Prioritisation

Seeded scoring has defined formula components: pressure, AI suitability, readiness, commercial attractiveness, influence potential and opportunity score. It separates some commercial pressure and influence components, and uses confidence/freshness as inputs. Live scoring adds live evidence score, learned evidence score, Rob-score adjustment and missing-evidence penalty. UI text explains score components.

Concerns: enterprise need, accessibility, provider fit, timing and route to market are not fully separated; freshness is an input/label but no decay lifecycle; confidence and importance can be blended into scores; scoring can create false precision when seeded fallback data is sparse; and score history is not durably preserved.

## 16. Outcome and Learning Alignment

Flora captures recommendation feedback and pilot logbook records with timestamps. Learned evidence scoring can read feedback/logbook signals and adjust scores. Source feedback can affect evidence quality.

Missing: outcome records are not linked to specific Recommendation IDs, Hypotheses, Theses, Observations or Enterprise Model fields; no accept/reject/retire lifecycle exists; conversation outcomes and opportunity outcomes do not update durable model state; source usefulness and recommendation effectiveness are not governed calibration objects.

## 17. Test and Governance Coverage

Tests protect: no LLM/database/broad-crawl imports; seeded evidence labelling; evidence specificity gates; source diagnostics; signal/recommendation separation in Observatory UI; recommendation references to commercial arguments/hypotheses; knowledge graph edge evidence IDs; hypothesis status and evidence; live evidence preference; and snapshot delta explanation.

Tests do not yet protect: persisted Observation atomicity; Observation-to-Evidence lineage as a durable invariant; no speculation in Observations by schema; no Recommendation without persisted lineage across all paths; Unknown and Contradiction preservation as first-class objects; human-knowledge labelling; model persistence; historical state; report-as-view behaviour; action downgrade behaviour in all recommendation paths.

## 18. Maturity Assessment

| Level | Criteria met | Missing | Assessment |
| --- | --- | --- | --- |
| Level 0 — Evidence Collector | Governed source collection and local evidence receipts. | N/A | Fully met. |
| Level 1 — Evidence Intelligence | Evidence gates, confidence, freshness, missing evidence, deterministic scores, source diagnostics, evidence-backed signals. | Durable observations and model memory. | **Current demonstrated level.** |
| Level 2 — Enterprise Model Platform | Partial generated organisation profiles, genome/forces/case-for-change, evidence IDs. | Durable Enterprise Model, incremental updates, history, contradiction handling. | Partial only. |
| Level 3 — Commercial Digital Twin | BT-specific profile and Observatory shape approximate twin views. | Maintained core asset, prediction/learning loops, model-backed reports. | Not met. |
| Level 4 — Predictive Enterprise Intelligence | TransformationWindow and TII labels. | Validated prediction, outcomes, calibration, history. | Not met. |
| Level 5 — Autonomous BD Partner | Cautious recommended conversations. | Autonomous action, governed learning and human control loops. | Not met. |

## 19. Architecture Debt Register

| Priority | Debt item | Type | Severity | Consequence | Remediation | ADR needed |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | No durable Observation ledger | Missing foundation | Critical | Evidence cannot become governed memory. | Add persisted Observation records from accepted Evidence. | Implements ADR-001/002. |
| 2 | No durable Enterprise Model repository | Missing foundation | Critical | Reports remain memory; future reasoning not reliably improved. | Minimal model snapshot updated by Observations. | Implements ADR-002. |
| 3 | Legacy recommendation path bypasses Thesis/Argument lineage | Accidental drift | High | Unsupported pursuit language can appear outside Observatory. | Gate strong recommendations or downgrade to validation actions. | Implements ADR-005. |
| 4 | Human-supplied knowledge not consistently labelled | Governance gap | High | Human notes can masquerade as external fact. | Add provenance fields and labels for user inputs. | Implements ADR-004. |
| 5 | Contradictions not first-class | Missing foundation | High | Conflicts become prose and are hard to resolve. | Add Contradiction/Unknown lifecycle after Observation foundation. | Possibly. |
| 6 | Knowledge graph transient only | Runtime/document mismatch | High | Lineage cannot be queried across runs. | Persist graph edges after model foundation. | No if implementing EI-002. |
| 7 | Outcome learning not linked to reasoning objects | Missing foundation | Medium | Learning cannot calibrate recommendations. | Link feedback to Recommendation/Hypothesis/Observation IDs. | Possibly. |
| 8 | Score history and decay absent | Test/runtime gap | Medium | False freshness and false precision risk. | Persist score events and decay policy. | Possibly. |

## 20. Sprint Options

### Option A — Observation-to-Enterprise Memory Foundation

Mission: persist accepted Evidence as atomic Observations and update minimal Enterprise Model snapshots. Capability: durable memory, lineage and model-backed future views. Layers affected: Evidence, Observation, Enterprise Model, Runtime. Likely modules: new Flora memory/observation service, live collection integration, Observatory input path, tests. Risks: overbuilding schema; conflating Observation with Signal. Testing: atomicity, lineage, idempotence, freshness, confidence, no recommendation language. Value: foundational memory. Deferred: full KG, outcomes, recommendation engine. Leverage: very high. Reason not to select first: requires careful boundaries, but that is acceptable.

### Option B — Recommendation lineage and action typing

Mission: make every recommendation reference Thesis/Argument lineage and an explicit action type. Capability: stronger trust and safer commercial actions. Layers affected: Commercial Reasoning, Executive Intelligence. Risks: lineage remains transient without durable memory. Testing: no strong recommendation without lineage; downgrade behaviour. Value: high trust. Reason not first: fixes top-layer safety but not durable memory.

### Option C — Unknown and Contradiction Foundation

Mission: persist Unknowns and Contradictions from missing evidence, counterarguments and weak signals. Capability: curiosity and conflict governance. Layers affected: Observation, Enterprise Model, Reasoning. Risks: lacks Observation ledger to attach conflicts to. Testing: preservation, resolution, contradiction visibility. Value: high. Reason not first: should attach to durable Observations and model fields.

### Option D — Outcome and Learning Capture

Mission: link feedback/logbook/outcomes to recommendations and future reasoning. Capability: calibration loop. Layers affected: Runtime, Reasoning, Action. Risks: learning from ungoverned recommendation IDs and transient hypotheses. Testing: outcome lineage and score/model update. Value: medium-high. Reason not first: depends on durable reasoning objects.

## 21. Recommended Next Sprint

### Sprint mission

Create the **Observation-to-Enterprise Memory Foundation**: accepted Flora Evidence becomes persisted atomic Observations, and Observations update a minimal durable Enterprise Model snapshot with inspectable lineage.

### Why now

Repository evidence shows Flora already collects and gates evidence well, and the Observatory already has strong transient reasoning objects. The limiting architecture dependency is memory: without persisted Observations and model state, stronger recommendations, contradictions, learning and predictions remain report-generated.

### Scope

- Define minimal Flora Observation record for accepted live and seeded evidence inputs.
- Persist Observation records in the existing dependency-light style or agreed repository pattern.
- Add idempotent Evidence→Observation creation with fingerprint/lineage.
- Add minimal Enterprise Model snapshot per organisation: identity, sector, evidence/observation links, current pressure themes, confidence, freshness, unknowns and last-updated.
- Feed Observatory from model/observations where available while preserving seeded fallback.
- Add tests for atomicity, lineage, idempotence, no recommendation language in Observations, freshness/confidence and model updates.

### Non-goals

No full database migration unless separately authorised; no full graph database; no LLM prompts; no recommendation redesign; no outcome learning; no UI redesign beyond small inspection if needed; no production configuration changes.

### Acceptance criteria

- Each accepted live evidence receipt can create one or more atomic Observation records with source Evidence lineage.
- Re-running collection does not duplicate unchanged Observations.
- A per-organisation Enterprise Model snapshot is updated from Observations and stores confidence, freshness and unknowns.
- Reports can cite model/Observation IDs for at least one path without making reports the memory.
- Tests prove no recommendation/action language is stored inside Observations.

### Architecture constraints

Evidence proves change; Observations remember change; Enterprise Models accumulate change; reports are views; human-supplied knowledge must be labelled; Unknowns must remain visible; no strong Recommendation without inspectable lineage.

### Validation requirements

Run existing Flora tests plus new targeted tests for Observation creation, persistence, model update and idempotence. Manually inspect generated Observatory and Publisher outputs to confirm no runtime behaviour regressed.

### Deferred work

First-class Contradiction objects, full Enterprise Knowledge Graph persistence, recommendation action typing, outcome learning, score decay/history and human-supplied knowledge governance across all inputs.

### ADR implications

No new ADR is required if the sprint implements ADR-001 and ADR-002. An ADR may be needed only if choosing a new persistence technology or changing the established dependency-light runtime constraint.

## 22. Conclusion

Flora today is an evidence-intelligence and report/workspace runtime with increasingly strong deterministic reasoning shapes. It is not yet a living Commercial Digital Twin because durable enterprise memory is not the maintained core asset. The most important architecture truth is that Flora’s reasoning is becoming structurally aligned faster than its memory layer. The next sprint should make this true: accepted Evidence creates durable atomic Observations, and those Observations update a minimal Enterprise Model that future reports render rather than recreate.
