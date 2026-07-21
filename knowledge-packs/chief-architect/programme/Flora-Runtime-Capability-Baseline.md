# WP-011 — Flora Runtime Capability Baseline

## 1. Purpose and method

This report reconstructs the implemented Flora runtime from repository evidence and compares it to the released and proposed CIOS/Flora architecture set. It is an implementation baseline, not a redesign. Status labels mean:

- **Operational** — route, runtime service, persistence path and tests/demonstration evidence exist.
- **Implemented** — code and tests exist, but demonstration or integration is narrower than a full runtime route.
- **Partially Implemented** — meaningful implementation exists with known scope limits.
- **Prototype** — runnable or modelled proof exists but is explicitly non-production or sample-oriented.
- **Stub** — placeholder or safe-unavailable path exists.
- **Planned** — architecture or documentation exists without runtime implementation evidence.
- **Unknown** — repository evidence is insufficient.

## 2. Runtime Capability Catalogue

| Capability | Purpose | Architectural owner | Implementation location | Runtime status | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Flora web runtime | Render-compatible HTTP entry point for Flora routes, health, deployment metadata and product journeys. | FEIR-001 presentation layer; ARCHITECTURE application layer. | `cios/applications/flora/web/app.py` | Operational | Standard-library HTTP service, `/health`, `/deployment`, banking, object, Explore/Focus/Shape, live, digital twin, blueprint import and canvas routes are registered in `FloraWebHandler`. | Broadest operational integration point; contains many product routes over deterministic services. |
| Storage runtime | Safe local/file-backed persistence with atomic writes and startup status. | FEIR-001 runtime state and persistence policy. | `cios/applications/flora/storage.py` | Operational | Provides `data_root`, `data_path`, `ensure_writable_dir`, `atomic_write_text`, `atomic_write_json`, `storage_mode` and `startup_storage_status`. | File-backed runtime store; not a production database/object-store adapter. |
| Increment 1 read-only object runtime | Governed Lloyds focus object projection with relationships, evidence availability, unknowns, contradictions and lineage. | EI-012, ADR-001, ADR-002, FEIR-001 governed knowledge/runtime graph. | `cios/applications/flora/runtime/increment1.py`, `cios/applications/flora/runtime/increment1_views.py`, `schemas/flora-runtime/v0.1`, `fixtures/flora-runtime` | Operational for `BK-ENT-001` | Increment 1 report records governed fixture ingestion, read-only Lloyds projection, safe-unavailable responses and schema validation. | Deliberately scoped; only Lloyds `BK-ENT-001` is supported. |
| Enterprise model memory | Durable observation, attribute, unknown and enterprise model structures with stable IDs and update reports. | EI-001, EI-002, ADR-002. | `cios/applications/flora/memory/models.py`, `service.py`, `repository.py`, `views.py` | Implemented | Model classes include `Observation`, `EnterpriseModelAttribute`, `EnterpriseUnknown`, `EnterpriseModel` and `ModelUpdateResult`; repositories persist observations, enterprise models, evidence and contradictions. | Enables factual twin and memory panel; acceptance governance remains separate. |
| Factual digital twin foundation | Extract factual evidence, compute coverage/maturity and render factual twin workspace. | EI-001, EI-012, FEIR-001 durable governed objects. | `cios/applications/flora/memory/factual_twin.py`, `views.py`, `golden_import.py` | Implemented | Functions extract factual evidence, assess coverage/maturity, compare automatic extraction, load/import golden facts and render factual twin pages. | Useful for demonstrable evidence-first enterprise memory. |
| Commercial/BT digital twin workspace | Customer-facing BT digital twin workspace and governed twin landing. | Commercial Digital Twin Blueprint Contract; FEIR-001 Strategic Sales experience. | `cios/applications/flora/digital_twins.py`, `/digital-twins` routes, financial-intelligence run records | Partially Implemented / Operational for BT slices | Governed twin list reads accepted packages/canvas access; BT page is a view over enterprise model and financial intelligence run records and does not persist twin state. | Demonstrable BT twin exists, but code says BT view deliberately does not own twin state. |
| Enterprise canvas | Executive canvas over imported/accepted twin state, including lineage inspection and feedback. | ADR-013, ADR-025, FEIR-001 presentation layer. | `cios/applications/flora/enterprise_canvas/*` | Operational | Canvas models, access repository, service, views and feedback service exist; web routes dispatch enterprise canvas paths. | Demonstrable for governed/imported twin records. |
| Blueprint package import | Receive, preserve, validate, stage, review, restage, dry-run plan and promote blueprint packages into canonical outputs. | ADR-012, Knowledge Pack Specification, Enterprise Knowledge Production Protocol. | `cios/applications/flora/blueprint_import/*` | Operational | Registry, archive, validator, candidate staging, mapping, review, restage, promotion, ledger and views exist; many tests cover import lifecycle. | Strong implementation of governed import boundary. |
| Banking industry and enterprise twin experience | UK banking industry portfolio, bank pages, comparison, evidence, financial history, market/analyst pages, heatmap, timeline and opportunity pages. | IT-001, Banking Strategic Sales Navigation, FEIR-001 banking reference journey. | `cios/applications/flora/banking_portfolio.py`, `enterprise-knowledge/banking/*`, `/flora/banking/*` routes | Operational | Web routes expose banking landing, portfolio, banks, outlook, AI-native pages, pipeline, heatmap, compare, competitors and per-bank pages. | Most complete customer-demonstrable industry journey. |
| Banking enterprise knowledge assets | Governed/candidate banking industry, infrastructure and enterprise twins. | IT-001, EI-001, Market/participant and opportunity specs where applicable. | `enterprise-knowledge/banking/*` | Implemented | Repository contains Banking Industry Twin, UK Payments Infrastructure Twin, enterprise twins for Lloyds, Barclays, NatWest, Monzo, Starling, Santander UK and Nationwide/Virgin Money, plus canonical objects. | Assets exist as markdown/JSON knowledge; runtime coverage varies by route. |
| Opportunity pipeline | Generate commercial opportunity pipeline with horizons, unknowns and contradictions. | EI-006, OT-001, FEIR-001 commercial action assessment. | `cios/applications/flora/enterprise_intelligence/opportunity_pipeline.py`, `cios/applications/flora/banking_portfolio.py` | Partially Implemented / Operational for banking demo | Code defines `CommercialOpportunity`, `OpportunityPipelineRun`, horizon classification and `generate_banking_opportunity_pipeline`; banking routes expose pipeline and opportunity pages. | Pipeline is deterministic and banking-focused; not a general opportunity-twin runtime. |
| Enterprise Intelligence reasoning runtime | Evidence-bounded executive commercial brief generation with retrieval, provider integration, deterministic fallback, validation and audit persistence. | FEIR-001, EIRP-001, EI-004, EI-007, EI-012. | `cios/applications/flora/enterprise_intelligence/runtime.py`, `retrieval.py`, `provider.py`, `validator.py`, `reasoning.py`, `pipeline.py`, `views.py` | Operational with fallback | Runtime retrieves bounded twin evidence, calls configured provider for structured output, validates claims, persists audit and stores success/failure artefacts; deterministic fallback creates evidence-limited brief. | External LLM path depends on provider configuration; deterministic fallback preserves operability. |
| Executive Intelligence Brief | Present executive-relevant brief with material pressures, unknowns, contradictions, recommendations and lineage. | EI-007, FEIR-001 Strategic Sales Brief. | `cios/applications/flora/enterprise_intelligence/views.py`, runtime brief schema | Operational | `executive_intelligence_brief_page` is routed for enterprise-intelligence paths; runtime schema requires executive summary, pressures, unknowns, contradictions, recommended moves and lineage manifest. | Demonstrable where evidence packages exist. |
| Semantic explanation / evidence trust | Explain Lloyds changes, assemble context packages, evidence trust and claim summaries. | EI-012, ADR-005, ADR-014. | `cios/applications/flora/enterprise_intelligence/explain.py`, `/flora/object/BK-ENT-001/explain` routes | Operational for Lloyds | Routes expose explain, context package and lineage detail for `BK-ENT-001`; code contains context package, evidence trust and audit functions. | Narrow object scope but high demonstrability. |
| Live evidence collection | Fetch, extract, classify, deduplicate, aggregate and display live evidence and source diagnostics. | FP-004, FP-006, EI-012, FEIR-001 detection. | `cios/applications/flora/live/*`, `config/flora/collection_profiles/*` | Operational | Live modules implement fetcher, document parser, extractor, source registry, collection worker/progress, aggregation, alignment and views; routes expose live dashboard/status/sources/evidence/acquisition plans. | Network/source reliability is environmental; runtime has diagnostics and safe categories. |
| Background workers | Start evidence collection in a background thread and persist progress. | FEIR-001 ingestion/detection; persistence policy. | `cios/applications/flora/live/worker.py`, `progress.py` | Implemented | `start_collection_run` creates background collection execution and `progress.py` persists status. | Background execution exists for live collection; broader job orchestration is not implemented. |
| Financial intelligence / RAPID | Acquire official sources, parse PDF/pages, extract financial candidates, run provider-assisted RAPID AI twin, canonicalise facts and support diagnostics. | ADR-011, EI-011, FEIR-001 evidence acquisition and commercial assessment. | `cios/applications/flora/financial_intelligence/*`, `document_review.py`, `config/flora/rapid_*` | Partially Implemented / Operational for configured BT FY26 paths | Modules implement source acquisition, page-aware parsing, section packets, structured adapters, candidate validation, RAPID profile, OpenAI/Anthropic providers, schema and BT structured ingestion. | Heavily tested but still provider/config dependent for live AI extraction. |
| Prompt orchestration / provider guardrails | Structured provider calls, diagnostics, strict schema, prompt/profile packaging and guardrails. | FEIR-001 GPT worker model; ADR-014. | `enterprise_intelligence/provider.py`, `profile.py`, `financial_intelligence/openai_provider.py`, `provider_guard.py`, `instructions.py` | Implemented | Provider modules expose unavailable/static/OpenAI providers, diagnostics and structured schema; guard enforces provider-call allowance. | No general multi-agent runtime; bounded provider invocation exists. |
| Commercial Opportunity Assistant | CLI/pipeline for structured opportunity scoring, reasoning mapping, recommendation and reports. | ARCHITECTURE MVP-001, EI-004. | `cios/applications/opportunity_assistant/*` | Implemented / Prototype | Modules implement input, scoring policy, ontology/graph/memory/reasoning mappings, decision policy, explainability, reporting and main pipeline. | This is a reusable application baseline, separate from Flora web routes. |
| Commercial observatory / Newton | Monitor organisations, build signals, insights, theses, recommendations and observatory views. | FP-003, EI-004, EI-008, EI-010, ADR-008. | `cios/applications/flora/observatory/*` | Operational | Engine builds observatory snapshots, commercial signals, insights and theses; Newton computes momentum, readiness and recommendation cards; views expose observatory pages. | Demonstrable but should be labelled as observatory/recommendation support, not final sales authority. |
| Publisher / Morning Edition | Generate markdown, HTML, PDF previews and release bundles for brief publications. | Flora Publisher v0.1; FEIR-001 reports/derived views. | `cios/applications/flora/publisher/*`, `docs/Applications/Flora_Pilot_Preview/*` | Implemented | Publisher builds publication context, renders markdown/HTML/PDF and pilot packages. | Demonstrable static executive publishing. |
| Authentication and access | Pilot session cookies, owner/workspace roles, enterprise access and blueprint upload authorisation. | FEIR-001 access controls; runtime authority model. | `cios/applications/flora/pilot_auth.py`, `access.py` | Implemented | Session issue/resolve, role extraction, enterprise/run access and upload authorisation functions exist. | Lightweight pilot auth, not enterprise IAM. |
| Architecture export | Download/status page for architecture export metadata and GitHub integration. | CIOS architecture governance and release profiles. | `cios/applications/flora/architecture_export.py` | Implemented | Validates export manifests, records downloads and renders architecture export page. | Supports governance/demo distribution, not runtime intelligence. |
| Knowledge pack loading | Build and validate Researcher pack, load package manifests/enterprise knowledge assets. | FP-010, Knowledge Pack Specification, ADR-016. | `knowledge-packs/researcher/*`, `tools/knowledge-packs/build_researcher_pack.py`, blueprint import manifest reader | Implemented | Researcher pack manifest/config/templates exist; build tool and tests validate pack construction. | Pack loading for runtime is strongest through blueprint import and package build, not a generalized plug-in loader. |
| Market participant twin | Participant/account position assessment runtime. | Market Participant Twin Specification. | Architecture/spec only; no clear Flora runtime module found. | Planned | Specs exist under `architecture/specifications/market-participants`; runtime evidence not found in `cios/applications/flora`. | Genuine gap. |
| UK Government / MOD twin | MOD enterprise understanding/canvas and executive intelligence runtime path. | EU-001, FEIR-001, MOD reviews. | Enterprise Intelligence runtime, enterprise canvas, blueprint import records; MOD review docs | In Progress / Partially Implemented | Release 1.0 says MOD validation is next and not yet proven; FEIR-001 uses MOD as bounded-runtime example. | Runtime has MOD-oriented paths, but validation/commercial proof remains incomplete. |

## 3. Capability Matrix

| Capability | Architecture | Runtime Status | Evidence | Notes |
| --- | --- | --- | --- | --- |
| Observation Runtime | EI-012 / ADR-001 | Operational | Increment 1 validates evidence/observation availability, unknowns, contradictions and lineage; memory models define stable observations. | Complete for Lloyds fixture and memory services; broader runtime coverage exists via live evidence. |
| Enterprise Model | EI-001 / ADR-002 | Implemented | Enterprise model, attributes, unknowns, repositories and factual twin services. | Durable model exists; governance acceptance external to runtime. |
| Enterprise Twin | EI-001 / FEIR-001 | Partially Implemented | Banking enterprise twins exist as assets; canvas/digital twin routes render governed twin records. | Multiple enterprise twins exist; runtime depth varies. |
| Commercial Twin | Commercial Digital Twin Blueprint Contract | Operational for BT and imported governed twins | `digital_twins.py`, blueprint import and enterprise canvas. | BT demonstrator is operational but uses underlying run/model records. |
| Market Participant Twin | Market Participant Twin Spec | Planned | Architecture specs only. | No runtime module identified. |
| Opportunity Twin | OT-001 / EI-006 | Partially Implemented | Banking opportunity pipeline and opportunity assistant. | Operational pipeline demo, not full opportunity twin lifecycle. |
| UK Government Twin | EU-001 / FEIR-001 | In Progress | MOD validation identified as next phase; enterprise intelligence runtime has MOD defaults. | Not yet proven as completed customer outcome. |
| Commercial Reasoning | EI-004 / FEIR-001 | Operational | Enterprise intelligence runtime, observatory, opportunity assistant and deterministic fallback. | Multiple components implement this capability. |
| Executive Brief | EI-007 / FEIR-001 | Operational | Enterprise Intelligence runtime schema and views; publisher. | Demonstrable from bounded evidence packages. |
| Knowledge Pack Loading | FP-010 / ADR-016 | Implemented | Researcher pack and build tool; blueprint import package manifest handling. | General runtime hot-loading is not evident. |
| Prompt Orchestration | FEIR-001 GPT worker model | Implemented | Provider adapters, structured schema, runtime prompt packaging and validator. | Single bounded orchestration path rather than agent society. |
| Live Evidence Collection | FP-004 / FP-006 / EI-012 | Operational | Live collect/fetch/extract/progress/views modules. | Dependent on source availability. |
| Financial Intelligence | ADR-011 / EI-011 | Partially Implemented | RAPID source acquisition, PDF parsing, candidates, providers, canonicalisation. | BT-focused configs and tests; provider-dependent. |
| Enterprise Canvas | ADR-013 / ADR-025 | Operational | Canvas service/models/views/access/feedback. | Strong demonstrable UI capability. |
| Background Workers | FEIR-001 ingestion | Implemented | Live worker/progress modules. | Collection-only worker baseline. |
| Architecture Governance Runtime | RELEASE-1.0 / AP-001 / AP-002 | Implemented | Profile compiler and runtime package generation are in Release 1.0. | Separate from Flora product runtime but operational in repo. |

## 4. Architecture-to-Runtime Mapping

### 4.1 Runtime components mapped to architecture

| Runtime component | Implements | Mapping assessment |
| --- | --- | --- |
| `web/app.py` | FEIR-001 presentation layer; ARCHITECTURE application layer | One route host integrates many architecture capabilities. |
| `runtime/increment1.py` and views | EI-012, ADR-001, ADR-002 | Implements read-only observation/object projection and safe-unavailable behaviour. |
| `memory/*` | EI-001, EI-002, ADR-002 | Implements enterprise model memory and factual twin support. |
| `enterprise_intelligence/*` | FEIR-001, EIRP-001, EI-004, EI-007, ADR-014 | Implements bounded retrieval, prompt orchestration, validation, audit and executive brief. |
| `live/*` | FP-004, FP-006, EI-012 | Implements live source collection and evidence diagnostics. |
| `financial_intelligence/*` | ADR-011, EI-011 | Implements source acquisition, financial extraction, canonicalisation and provider-assisted analysis. |
| `blueprint_import/*` | ADR-012, Knowledge Pack Specification, EKPP | Implements governed external package ingestion/promotion boundary. |
| `enterprise_canvas/*` | ADR-013, ADR-025, FEIR-001 | Implements executive twin navigation and lineage/feedback. |
| `banking_portfolio.py` + `enterprise-knowledge/banking` | IT-001, banking reference journey | Implements the strongest industry demonstration. |
| `observatory/*` | EI-008, EI-010, ADR-008 | Implements commercial signal and recommendation support. |
| `publisher/*` | Presentation/reporting models | Implements generated executive publications. |
| `opportunity_assistant/*` | ARCHITECTURE MVP-001, EI-004 | Implements separate opportunity-scoring assistant. |

### 4.2 Multiple runtime components implementing one architecture capability

- **Commercial reasoning** is implemented by Enterprise Intelligence runtime, Observatory/Newton, banking portfolio interpretation and Opportunity Assistant.
- **Observation/evidence lineage** is implemented by Increment 1 runtime, Memory/Factual Twin, Live Evidence and Enterprise Intelligence explainability.
- **Presentation layer** is implemented by web routes, Enterprise Canvas, Banking pages, Digital Twin pages, Publisher and Increment 1 views.
- **Recommendation/action policy** appears in Enterprise Intelligence recommended moves, Observatory recommendations and Opportunity Assistant decision policy.

### 4.3 Runtime capabilities with weak or unclear architectural ownership

- `architecture_export.py` is useful governance/product infrastructure but is not a core Enterprise Intelligence runtime capability.
- `rob_score.py` and workspace feedback/logbook support product operation but need clearer architecture ownership if retained as runtime primitives.
- Pilot auth is an implementation necessity; architecture describes access controls, but not this concrete lightweight cookie model.

### 4.4 Architecture without runtime implementation evidence

- Full Market Participant Twin runtime.
- Fully general Opportunity Twin lifecycle runtime beyond banking/opportunity assistant slices.
- General-purpose GPT worker society with all FEIR-001 named workers as independently orchestrated components.
- Production storage/IAM adapters.
- Governed write-back all the way to accepted Enterprise Knowledge without repository-human workflow.
- MOD/UK Government demonstrable validation as a completed outcome.

## 5. Runtime Maturity Matrix

| Maturity | Capabilities |
| --- | --- |
| Operational | Flora web runtime; Increment 1 Lloyds runtime; Enterprise canvas; Banking portfolio/twin journey; Live evidence collection; Enterprise Intelligence brief with fallback; Semantic explain/evidence trust for Lloyds; Blueprint import; Commercial observatory; BT digital twin slices. |
| Implemented | Storage runtime; enterprise model memory; factual twin foundation; prompt/provider guardrails; publisher; pilot auth/access; architecture export; knowledge pack build/loading; background collection worker. |
| Partially Implemented | Enterprise twin; Commercial/BT twin; Opportunity twin; Financial intelligence/RAPID; UK Government/MOD twin. |
| Prototype | Opportunity Assistant CLI/pipeline; sample/static workspace and publication previews where not wired to governed live state. |
| Stub | Safe-unavailable for unsupported Increment 1 object identities and unsupported routes. |
| Planned | Market Participant Twin runtime; production write-back loop; production object store/IAM; fully general agent society. |
| Unknown | Customer deployment readiness of every route beyond tests and rendered acceptance artefacts; external source reliability in live runs. |

## 6. Demonstrable Capability Register — what Flora can prove today

| Demonstrable capability | What can be shown | Evidence path |
| --- | --- | --- |
| UK Banking strategic sales workspace | Landing, bank cards, industry outlook, AI-native thesis, timeline, heatmap, compare, bank-specific briefing, evidence and opportunities. | `/flora/banking/*` routes and rendered acceptance HTML under `docs/flora-runtime/increment-4.7.1-rendered-acceptance`. |
| Lloyds evidence-first object workspace | Governed focus object with relationships, evidence/observation availability, unknowns, contradictions and lineage. | `/flora/object/BK-ENT-001`; Increment 1 report. |
| Lloyds explanation and evidence trust | Explain what changed, inspect context package and lineage. | `/flora/object/BK-ENT-001/explain`, `/context-package`, `/lineage/*`. |
| Executive Intelligence Brief | Evidence-bounded executive brief with material pressures, unknowns, contradictions, recommended next moves and lineage manifest. | Enterprise Intelligence runtime and views. |
| Enterprise Canvas | Executive navigation over a governed/imported twin with lineage and feedback. | Enterprise canvas models/service/views/access. |
| Blueprint import and progressive assurance | Upload, inspect, validate, stage, review, restage, approve/promote and view history. | Blueprint import route set and modules. |
| BT financial/digital twin slice | BT commercial digital twin page, source/run status, search/progress and RAPID snapshot CSV when runs exist. | `digital_twins.py` and financial intelligence modules/config. |
| Live evidence dashboard | Source coverage, collection status/progress, rejected claims, source effectiveness and acquisition plans. | `/live/*` routes and live modules. |
| Commercial observatory | Enterprise monitoring, evidence scores, hypotheses, momentum/readiness and recommendations. | Observatory engine/Newton/views. |
| Static executive publication | Morning Edition markdown/HTML/PDF preview bundle. | Publisher modules and pilot preview docs. |

## 7. Runtime gaps

Genuine gaps only:

1. **Market Participant Twin runtime** — architecture exists, no implementation evidence found.
2. **General Opportunity Twin lifecycle** — opportunity pipeline exists, but full governed opportunity-twin lifecycle is not evidenced.
3. **Production persistence adapter** — current storage is file-backed; no production database/object store adapter found.
4. **Production IAM/access-control adapter** — pilot cookie/role access exists, not enterprise IAM.
5. **Full FEIR worker society** — bounded provider calls and deterministic fallback exist, but named worker components are not individually implemented/orchestrated as a full society.
6. **Governed write-back completion** — import/promotion exists, but automatic runtime learning-to-repository acceptance remains a governed human workflow rather than a completed runtime loop.
7. **MOD/UK Government validation** — implementation support exists, but Release 1.0 explicitly records MOD validation as not yet complete.

## 8. Technical Debt Register

### 8.1 Implementation debt

- File-backed storage limits production durability and concurrent operation.
- `web/app.py` is a large route dispatcher and integration hotspot.
- Financial intelligence has several provider/config-dependent paths requiring robust operational diagnostics.
- Background worker support is collection-specific rather than a general job runtime.

### 8.2 Architectural debt

- Some operational product utilities lack explicit architectural ownership.
- Recommendation/action policy is distributed across multiple components and should be reconciled without redesigning working flows.
- FEIR-001 worker model is more granular than current runtime implementation.

### 8.3 Documentation debt

- Runtime capabilities are spread across implementation reports, increment reports, acceptance artefacts and code; this baseline should become the index for future increments.
- Banking demonstration scope and BT/MOD maturity need clearer labels to avoid overclaiming.
- Knowledge-pack runtime loading versus package build/import should be distinguished.

### 8.4 Testing debt

- Many targeted tests exist, but no single WP-011 test suite asserts the capability matrix.
- End-to-end route smoke coverage should be grouped by demonstrable capability.
- Provider-dependent financial/LLM tests need clear offline/online mode classification.

## 9. Delivery Roadmap

### Continue

- Continue Banking strategic sales runtime: it is the strongest demonstrable commercial path.
- Continue Blueprint Import and Enterprise Canvas: they provide governed twin ingestion, navigation and lineage.
- Continue Enterprise Intelligence reasoning with deterministic fallback and validator/audit controls.
- Continue Financial Intelligence/RAPID hardening for BT because it is already materially implemented.

### Complete

- Complete the full Opportunity Twin lifecycle around the existing banking pipeline.
- Complete MOD/UK Government validation only from existing runtime evidence and review outcomes.
- Complete production-grade storage/access adapter decisions without changing the domain runtime.
- Complete a capability-indexed smoke suite for the demonstrable routes.

### Improve

- Improve route/module separation in the web runtime while preserving route behaviour.
- Improve documentation labels for Operational vs Implemented vs Partial to prevent overclaiming.
- Improve provider diagnostics and offline fallbacks for financial intelligence.
- Improve traceability between runtime components and architectural owners.

### New

- Build Market Participant Twin runtime only after confirming the intended first commercial demonstration.
- Add a general job orchestration primitive if live collection, financial extraction and reasoning runs need shared operational management.
- Add production persistence/IAM adapters when commercial deployment requires them.

## 10. Shortest path to next demonstrable commercial outcome

The shortest path is **not** to start a new twin. It is to package the already operational Banking + Enterprise Canvas + Executive Intelligence path into one guided demonstration:

1. Start at UK Banking landing and select Lloyds or another governed bank.
2. Show industry pressure, bank-specific briefing, evidence and opportunity pipeline.
3. Open Lloyds evidence-first object workspace to prove observations, unknowns, contradictions and lineage.
4. Generate or display an Executive Intelligence Brief with evidence-bounded recommended next moves.
5. If using BT, show the BT financial/digital twin slice only as a focused factual/financial intelligence proof, not as the canonical proof for all twins.

This proves: governed evidence, twin navigation, reasoning, executive relevance, opportunity shaping and inspectable lineage without inventing missing runtime capabilities.
