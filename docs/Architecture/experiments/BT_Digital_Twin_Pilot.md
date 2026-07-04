# BT Digital Twin Pilot

**Status:** Experiment complete  
**Enterprise:** BT Group plc  
**Stable enterprise ID:** `bt-group-plc-9f2c6a`  
**Execution date:** 2026-07-04  
**Inspected repository commit:** `a3268157799504c49bb640006d1bd11b9dd98a57`  
**Branch:** `experiment/bt-digital-twin-pilot`

## Mission

This pilot evaluated whether Flora can construct, retain, update and explain a bounded Commercial Digital Twin of BT Group plc from public permissible Evidence. The pilot was intentionally an architecture calibration, not a polished company report.

The tested chain was:

```text
Public Source -> Evidence -> atomic Observation -> BT Enterprise Model attribute -> temporal change -> explainable model-backed view
```

## Architecture baseline read

The pilot read and applied the merged architecture and runtime baseline:

- `CIOS-AI.md`.
- `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md`.
- `architecture/reference-architecture/CIOS-Design-Doctrine.md`.
- `architecture/handbook/CIOS-Chief-Architect-Handbook.md`.
- `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md`.
- `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md`.
- `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-003-Enterprise-Behaviour-Model.md`.
- `architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md`.
- `architecture/founding-papers/FP-003-Flora-Intelligence-Architecture.md`.
- `architecture/decisions/ADR-009-Observation-Identity-and-Minimal-Model-Projection.md`.
- `docs/Architecture/Flora_Observation_Enterprise_Memory.md`.
- Flora collection, Evidence, memory, Observatory and runtime-alignment implementation under `cios/applications/flora/`.
- Tests under `tests/test_flora*.py`.

ADR-009 is Accepted. The canonical Observation-backed memory implementation is present under `cios/applications/flora/memory/`.

## Starting-state record

The requested remote bootstrap could not be completed because this checkout has no configured `origin` remote. The local inspected commit was therefore used as the baseline and recorded explicitly.

```text
git fetch origin -> failed: origin does not appear to be a git repository
git checkout main -> not reached during combined command
git pull --ff-only origin main -> not reached during combined command
git status --short -> clean before changes
git rev-parse HEAD -> a3268157799504c49bb640006d1bd11b9dd98a57
```

## Source set

Retrieval date for web sources: 2026-07-04.

| Source ID | Title | Publisher | Publication date | Type | Authoritative status | URL / locator | Relevant enterprise | Freshness | Extraction status |
|---|---|---:|---:|---|---|---|---|---|---|
| BT-SRC-001 | BT Group plc Annual Report 2026 | BT Group plc | 2026-06-11 | Annual report PDF | First-party authoritative | https://www.bt.com/about/annual-reports/2026summary/assets/files/BT-Annual-Report-2026.pdf | BT Group plc | Current | Extracted |
| BT-SRC-002 | Results for the full year to 31 March 2026 | BT Group plc | 2026-05-22 | Results release PDF | First-party authoritative | https://www.bt.com/content/dam/bt-plc/assets/documents/investors/financial-reporting-and-news/quarterly-results/fy26/h2/fy26-release.pdf | BT Group plc | Current | Extracted |
| BT-SRC-003 | Our strategy | BT Group plc | Current page retrieved 2026-07-04 | Corporate web page | First-party authoritative | https://www.bt.com/about/bt/our-company/our-strategy | BT Group plc | Current | Extracted |
| BT-SRC-004 | Our businesses | BT Group plc | Current page retrieved 2026-07-04 | Corporate web page | First-party authoritative | https://www.bt.com/about/bt/our-company/group-businesses | BT Group plc and units | Current | Extracted |
| BT-SRC-005 | Our leadership | BT Group plc | Current page retrieved 2026-07-04 | Corporate web page | First-party authoritative | https://www.bt.com/about/bt/our-board | BT Group plc leadership | Current | Extracted |
| BT-SRC-006 | BT Group and Verizon to form joint venture | BT Group newsroom | 2026-06-29 | Announcement | First-party authoritative | https://newsroom.bt.com/bt-group-and-verizon-to-form-joint-venture-creating-a-scaled-international-connectivity-platform-for-multinational-customers/ | BT Group, BT International, Verizon | Current | Extracted |
| BT-SRC-007 | Verizon and BT form joint venture | Verizon | 2026-06-29 | Announcement | First-party corroborating | https://www.verizon.com/about/news/verizon-bt-group-international-joint-venture | Verizon, BT Group | Current | Extracted |
| BT-SRC-008 | BT adjusts financial guidance for change in accounting treatment of BT International | BT Group via RNS/FT | 2026-06-29 | Regulatory announcement | First-party/regulatory | https://markets.ft.com/data/announce/full?dockey=1323-17661058-0666B896TH50O0KV0HF7TPOSUR | BT Group, BT International | Current | Extracted |
| BT-SRC-009 | Responsible Business Addendum 2026 | BT Group plc | 2026-06-11 | Addendum PDF | First-party authoritative | https://www.bt.com/about/annual-reports/2026summary/assets/files/Responsible-Business-Addendum-2026.pdf | BT Group plc | Current | Partially extracted |
| BT-SRC-010 | The Guardian coverage of BT-Verizon venture | The Guardian | 2026-06-29 | Secondary reporting | Secondary only | https://www.theguardian.com/business/2026/jun/29/bt-verizon-joint-venture-deal-telecoms-international | BT Group, Verizon | Current | Used for contradiction discovery only |
| BT-SRC-011 | WSJ coverage of BT-Verizon venture | Wall Street Journal | 2026-06-29 | Secondary reporting | Secondary only | https://www.wsj.com/business/deals/bt-verizon-to-form-international-joint-venture-556f9848 | BT Group, Verizon | Current | Used for contradiction discovery only |

## Experiment method

The pilot used the merged file-backed `ObservationMemoryService` without production code changes. A controlled source set was represented as deterministic Evidence dictionaries, accepted into a temporary runtime memory directory, rendered through the existing Enterprise Memory panel, then exported as a sanitised snapshot at `docs/Architecture/experiments/BT_Digital_Twin_Snapshot.md`.

### Controlled passes

| Pass | Purpose | Inputs | Result |
|---|---|---|---|
| Pass 1 | Baseline construction | Annual Report, FY26 results, strategy, organisation pages | 16 accepted Observations, 5 projected attributes, 0 Unknowns |
| Pass 2 | Change evidence | BT-Verizon announcement and accounting guidance | 26 accepted Observations, 9 projected attributes, 1 projected Unknown |
| Pass 3 | Recollection | Reprocessed one organisational source | Observation count remained 26 |
| Restart | Durability | Reopened repositories from disk | 26 Observations, 9 attributes, 1 Unknown |
| Observatory | Model-backed view | Rendered persisted model | Render succeeded |

## BT twin scope populated

| Domain | Populated? | Notes |
|---|---:|---|
| Enterprise identity | Partial | Stable ID and public-listed identity captured. Legal subsidiary detail remains shallow. |
| Enterprise structure | Partial | Consumer, Business, International, Openreach, Digital and Networks represented as distinct Observations; projection collapses many facts into a small attribute set. |
| Strategy | Partial | Build, Connect, Accelerate and ambition captured as stated strategy. Runtime projection stores latest statement per condition rather than rich strategy object. |
| Leadership and ownership | Partial | CEO-designate for proposed JV captured; current executive roster documented from source set but not fully projected. |
| Transformation programmes | Partial | Full fibre, mobile network and modernisation themes captured. Named programme taxonomy remains limited. |
| Financial commitments | Partial | FY27-FY30 commitment class captured; distinction between target, guidance and actual is documented but weak in projection. |
| Material relationships | Partial | Proposed Verizon JV captured with ownership, conditionality and independent-operation state. |
| Pressures and constraints | Partial | Capital intensity, UK focus, regulatory completion conditions and transaction uncertainty captured. |
| Unknowns | Partial | Final completion date and post-completion operating model identified; runtime collapsed two unknown statements into one domain-level Unknown. |

## Material BT entities resolved

- BT Group plc.
- British Telecommunications plc / operating-company perimeter: noted as requiring deeper subsidiary evidence.
- Consumer.
- Business.
- International.
- Openreach.
- Digital.
- Networks.
- BT brand.
- EE brand.
- Plusnet brand.
- Proposed BT-Verizon international connectivity joint venture.
- Verizon international operations relevant to the proposed transaction.
- Martijn Blanken as CEO-designate of the proposed joint venture.

## Accepted Observations

26 accepted Observations were persisted. Representative accepted Observation statements included:

- BT Group plc is a public listed telecommunications group headquartered in the United Kingdom.
- BT Group has four customer-facing lines of business.
- Consumer is a BT customer-facing line of business.
- Digital is a BT internal service unit.
- BT strategy includes Build.
- BT ambition is to become the UK most trusted connector of people business society.
- BT Openreach full fibre build reached twenty three million premises in FY26.
- BT Group announced a proposed international connectivity joint venture with Verizon on 29 June 2026.
- The proposed joint venture ownership is fifty percent BT Group.
- The joint venture transaction is subject to regulatory clearances.
- BT International continues to operate independently until joint venture completion.
- Martijn Blanken is CEO designate of the proposed joint venture.
- The final joint venture completion date is unknown.

## Rejected or flagged candidate Observations

8 candidate Observations were manually rejected or rewritten before persistence:

| Candidate problem | Example issue | Disposition |
|---|---|---|
| Compound statement | One sentence combined ownership, conditions and timing | Split into atomic Observations |
| Promotional prose | “future-ready scaled organisation” copied from announcement | Excluded from Observation layer |
| Recommendation language | Suggested sales pursuit | Rejected |
| Inference as fact | “BT is exiting global enterprise services” | Recast as conditional/future-state question |
| Organisational flattening | “BT and Openreach are the same unit” | Rejected |
| Target treated as result | FY30 free-cash-flow commitment presented as achieved | Rewritten as target |
| Conditional appointment treated as current | CEO-designate rendered as current CEO | Rewritten as designated/conditional |
| Future JV treated as completed | JV shown as operating company today | Rewritten as proposed conditional future state |

## Golden-question results

| # | Question | Model-backed result | Evidence IDs | Assessment |
|---:|---|---|---|---|
| 1 | What is BT Group? | A UK-headquartered public listed telecommunications group with group brands and organisational units. | BT-EV-001, BT-SRC-001, BT-SRC-002 | Partial pass |
| 2 | How is BT currently organised? | BT presents one business made up of organisational units. | BT-EV-002, BT-SRC-004 | Pass |
| 3 | Which units face customers? | Consumer, Business, International and Openreach. | BT-EV-003..BT-EV-007 | Pass |
| 4 | Which units provide internal capabilities? | Digital and Networks. | BT-EV-008, BT-EV-009 | Pass |
| 5 | How is Openreach related to BT Group? | Openreach is represented as a BT customer-facing line of business; governance independence requires deeper evidence. | BT-EV-007 | Partial pass |
| 6 | What is BT trying to become? | The UK most trusted connector of people, business and society. | BT-EV-013 | Pass |
| 7 | What do Build, Connect and Accelerate mean? | The labels were captured; semantic decomposition remains report-level rather than model-level. | BT-EV-010..BT-EV-012 | Partial pass |
| 8 | Which commitments have measurable time horizons? | Full fibre and 5G FY26 actuals were captured; FY30 free-cash-flow target was captured. | BT-EV-014..BT-EV-016 | Partial pass |
| 9 | Which statements are strategy rather than observed delivery? | Strategy labels and ambition remain separable from FY26 deployment facts in the curated evidence set. | BT-EV-010..BT-EV-016 | Partial pass |
| 10 | What changed on 29 June 2026? | A proposed BT-Verizon international connectivity JV was announced. | BT-EV-017 | Pass |
| 11 | What did not change immediately? | BT International and Verizon international operations continue independently until completion. | BT-EV-022, BT-EV-023 | Pass |
| 12 | Which future state is conditional? | The new 50:50 JV future state is conditional on clearances and closing conditions. | BT-EV-018..BT-EV-021 | Pass |
| 13 | Which current model attributes were affected? | Material relationships, conditional state, current state, leadership and Unknowns. | BT-EV-017..BT-EV-026 | Pass |
| 14 | What prior state remains historically valid? | BT International existed as a current customer-facing line before the announcement. | BT-EV-006 | Pass |
| 15 | Which Evidence supports each answer? | Evidence IDs are retained in the Observation ledger and snapshot. | Snapshot | Pass |
| 16 | What is explicitly stated? | Strategy labels, units, ownership, conditions and independent-operation state are explicit. | BT-SRC-003..BT-SRC-008 | Pass |
| 17 | What is inferred? | Commercial pressure and operating-model implications are pilot interpretation, not facts. | Report analysis | Partial pass |
| 18 | What remains Unknown? | Completion date, post-completion operating model and detailed integration choices. | BT-EV-025, BT-EV-026 | Pass |
| 19 | Are any sources contradictory? | No material contradiction was found among authoritative sources. Secondary sources were consistent on major transaction facts. | BT-SRC-006..BT-SRC-011 | Pass |
| 20 | Which information is stale or due for review? | Leadership, transaction status and guidance should be refreshed at Q1 FY27 and transaction-completion milestones. | BT-SRC-005, BT-SRC-008 | Pass |
| 21 | Which enterprise pressures are evidenced? | UK focus, cost transformation, capital intensity, network build and transaction uncertainty. | BT-SRC-001, BT-SRC-002, BT-SRC-006 | Partial pass |
| 22 | Which transformation themes are visible? | Full fibre, 5G, modernisation, simplification, customer experience, data/AI-enabled IT. | BT-SRC-001, BT-SRC-003 | Partial pass |
| 23 | Which executive domains appear affected? | Group strategy, International leadership, finance/accounting guidance and network/digital delivery. | BT-SRC-005, BT-SRC-008 | Partial pass |
| 24 | What additional Evidence is needed before a commercial thesis? | Programme ownership, supplier landscape, integration architecture, budget authority and procurement route. | Unknowns | Pass |
| 25 | What should Flora monitor next? | Completion approvals, JV name, leadership effective dates, accounting updates, Q1 FY27 guidance and Openreach/network milestones. | Unknowns | Pass |

## Temporal-change test

The BT-Verizon announcement was represented as a temporal change, not as a completed current-state overwrite:

- **Before announcement:** International existed as a BT customer-facing line of business.
- **At announcement:** BT Group announced a proposed international connectivity joint venture with Verizon on 2026-06-29.
- **Current state:** The transaction remains subject to regulatory clearances and customary closing conditions.
- **Current continuity:** BT International and Verizon international operations continue independently until completion.
- **Future possible state:** A new 50:50 international connectivity joint venture may become operational after completion.
- **Unknowns:** Final completion date and post-completion operating model remain unresolved.

## Scoring

Scores are 0-5. No aggregate score is used.

| Capability | Score | Notes |
|---|---:|---|
| Evidence quality | 4 | First-party evidence dominated; extraction was partly manual. |
| Observation atomicity | 4 | Manual review achieved atomicity; runtime validator is crude. |
| Entity and organisational resolution | 3 | Units distinguished in Observations; projection lacks entity graph. |
| Model completeness within scope | 3 | Bounded domains populated partially. |
| Attribute-level lineage | 4 | Projection retains Observation IDs and Evidence IDs. |
| Temporal accuracy | 4 | Conditional future state did not overwrite current state. |
| Idempotency | 5 | Recollection produced no duplicate Observation. |
| Corroboration handling | 3 | Duplicate/corroborating evidence attaches, but semantic corroboration is limited. |
| Contradiction handling | 3 | Mechanism exists, but no BT contradiction was materially exercised. |
| Unknown preservation | 3 | Unknowns persist, but multiple unknowns collapsed by affected attribute. |
| Current versus future-state separation | 4 | Achieved through curated atomic statements and dates. |
| Strategic coherence | 3 | Strategy captured as facts, not a rich strategy model. |
| Behavioural interpretation | 2 | Behavioural model mostly report-level. |
| Commercial relevance | 3 | Pressures identified without unsupported sales claims. |
| Model-backed view quality | 3 | Observatory renders state but not a domain-native BT twin. |
| Explainability | 4 | Lineage visible from attributes to Observations and Evidence. |
| Freshness handling | 3 | Freshness labels are stored but not operationally scheduled. |
| Selective update behaviour | 3 | New facts updated affected attributes, but projection granularity is coarse. |

## Failures and correction register for scores below 4

| Capability | Observed failure | Architecture cause | Runtime cause | Prompt/model cause | Data-quality cause | Proposed correction | General or BT-specific |
|---|---|---|---|---|---|---|---|
| Entity resolution | Distinct units do not become graph nodes. | EI-002 not implemented in memory projection. | Minimal projection has attribute map only. | Manual curation required. | Source pages mix group and unit language. | Add generic enterprise entity and relationship projection. | General |
| Model completeness | Scope exceeds current projection domains. | ADR-009 accepts minimal model. | Domain map is narrow. | Pilot demanded richer domains. | Some subsidiary details require deeper filings. | Add schema for structure, strategy, commitments and relationships. | General |
| Corroboration | Similar facts with different wording are not merged. | Semantic corroboration deferred. | Fingerprint is exact-normalised. | Curator must standardise statements. | Sources restate facts differently. | Add governed corroboration review queue. | General |
| Contradiction | No strong contradiction exercise occurred. | Contradictions are simple coexistence records. | Detection relies on term list. | No adversarial contradictory source was accepted. | Authoritative sources aligned. | Add explicit contradiction object and manual contradiction registration. | General |
| Unknown preservation | Two Unknown statements collapsed to one Unknown. | Unknown model under-specified. | Unknown ID uses enterprise plus attribute key. | N/A. | N/A. | Fingerprint Unknowns by question plus affected domain. | General |
| Strategic coherence | Build/Connect/Accelerate not decomposed structurally. | Strategy model is not yet implemented. | Domain map treats Strategy as enterprise identity fallback. | Manual statements too compact. | Strategy page is prose-heavy. | Add Strategy attribute type with pillars, commitments and status. | General |
| Behavioural interpretation | Behaviour remains narrative interpretation. | EI-003 not projected. | No behavioural model service. | Pilot avoided unsupported inference. | Behaviour evidence is indirect. | Implement evidence-backed behavioural indicators separately from recommendations. | General |
| Commercial relevance | Pressures do not become validated commercial theses. | FP-003 reasoning loop not fully implemented. | No thesis/validation workflow in memory. | Correctly avoided sales claims. | Missing supplier/procurement evidence. | Add evidence-demand workflow before opportunity shaping. | General |
| Model-backed view | View is generic memory panel. | Product view is pilot-level. | Observatory lacks domain-specific renderer. | N/A. | N/A. | Add safe configurable twin snapshot renderer. | General |
| Freshness | No automated review scheduling by volatility. | Freshness doctrine documented but not operational. | Freshness is a string field. | N/A. | Publication cadence varies. | Add freshness policy per attribute class. | General |
| Selective update | Attribute granularity is coarse. | Minimal projection trades richness for safety. | Many conditions map to broad domains. | N/A. | N/A. | Add stable attribute taxonomy for enterprise structure and transactions. | General |

## Findings

1. Flora already demonstrates early Enterprise Model platform behaviour: durable state survives restart, Observations retain Evidence lineage and reports are not memory.
2. Flora is not yet a Commercial Digital Twin runtime for complex enterprises: entity graph, strategy model, transaction lifecycle and behavioural model are too shallow.
3. The file-backed memory layer correctly handled deterministic idempotency for exact recollection.
4. The BT-Verizon event proved the architecture can represent conditional future state when Evidence is curated into atomic Observations.
5. Manual curation carried too much responsibility for source interpretation, Observation atomicity and organisational scope preservation.
6. The Observatory can render persisted BT state, but the rendering is a generic memory panel rather than a rich twin view.

## Recommended architecture changes

1. Define an Enterprise Structure projection schema aligned to EI-001 and EI-002.
2. Define a Strategy projection object with pillars, commitments, outcomes, evidence lineage and status type.
3. Define a Transaction / Material Relationship object with current state, announced state, conditions, expected timing, future possible state and affected enterprise nodes.
4. Extend Unknown identity so each missing fact is preserved independently.
5. Add a freshness policy taxonomy by attribute volatility.
6. Add contradiction registration independent of keyword-triggered conflict detection.
7. Add a model-backed golden-question evaluation harness.

## Recommended runtime changes

No production runtime code was changed in this sprint. Recommended bounded follow-ons:

1. Add generic entity and relationship projection support.
2. Add Unknown fingerprinting by question and domain.
3. Add domain-specific safe snapshot export for Enterprise Models.
4. Add semantic-corroboration candidate review without automatic merging.
5. Add temporal transaction lifecycle fields.
6. Add regression tests for conditional future state and current-state preservation.

## Deferred questions

- What exact legal entities sit inside the BT International perimeter after accounting re-presentation?
- What is the final name and jurisdictional operating model of the proposed JV?
- Which regulatory approvals are required by jurisdiction?
- Which systems, platforms, suppliers and contracts move into the JV?
- Which executives own integration, separation and service continuity?
- How should Openreach governance separation be represented in the canonical Enterprise Model?

## Differentiator evaluation

Flora currently behaves as an **early Enterprise Model platform**, not merely a research summariser and not yet a full Commercial Digital Twin.

It exceeded a research summariser because it maintained durable state, preserved Evidence-to-Observation lineage, survived restart, rendered model-backed memory and avoided overwriting current state with future conditional state. It fell short of a full Commercial Digital Twin because entity relationships, strategy semantics, transaction lifecycle, Unknown granularity, behavioural interpretation and domain-native rendering remain incomplete.

## Conclusion

The BT pilot validates ADR-009 as a useful foundation. Flora can remember evidence-backed enterprise facts and selectively add change Observations without regenerating an opaque report. However, the pilot also shows that the current minimal projection is too narrow for a complex enterprise such as BT Group. The next sprint should implement generic structure, strategy and transaction projections before attempting broader enterprise coverage.
