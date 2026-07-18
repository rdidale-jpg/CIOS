# Banking Strategic Sales Navigation Validation Report

**Asset ID:** `BK-GOV-SSN-VAL-001`  
**Document class:** Governance validation report  
**Domain:** Banking  
**Validation date:** 2026-07-18  
**Runtime boundary:** Repository discovery assessment only. No operational Flora runtime, loader or UX test harness was executed.

## 1. Executive finding

Repository discovery readiness: **PARTIAL**  
Runtime ingestion validation: **NOT EXECUTED**  
Runtime UX validation: **NOT EXECUTED**

The governed Banking domain contains enough source material to support a Strategic Sales Director’s Explore journey and parts of Focus and Shape. It does not yet fully support the desired commercial navigation experience because many relationships are prose-based, hypothesis-to-evidence lineage is inherited rather than directly machine-addressable, executive specificity is mostly generic role-level, and Flora-facing manifests do not expose derived journey views.

## 2. Assets inspected

- `BK-IND-001` Banking Industry Foundation.
- `BK-IND-002` Banking Industry Twin.
- `BK-REF-001` Banking Mechanisms and Tensions Model.
- `BK-INF-001` UK Banking Payments Infrastructure Twin.
- `BK-ENT-001` Lloyds Enterprise Twin.
- `BK-ENT-002` NatWest Enterprise Twin.
- `BK-ENT-003` Nationwide / Virgin Money Enterprise Twin.
- `BK-ENT-004` Monzo Enterprise Twin.
- `BK-ENT-005` Starling Enterprise Twin.
- `BK-ENT-006` Barclays Enterprise Twin.
- `BK-ENT-007` Santander UK Enterprise Twin.
- `BK-CMP-001` Banking Mechanism Differential Matrix.
- `BK-CMP-002` Four-Bank Mechanism Differential Matrix.
- `BK-FLR-001` Banking Knowledge Register for Flora.
- `EK-BANK-RHYP-001` Banking Reinvention Hypotheses v0.1.
- EGM-001 Enterprise Growth Method.
- EI-012 Enterprise Observation Model.
- FP-009 Hypothesis Validation Standard.
- Enterprise Knowledge Architecture and Production Protocol.
- CIOS Reference Architecture and accepted ADRs including human-knowledge and recommendation-lineage decisions.

## 3. Journeys tested

| Journey | Starting question | Result | Reason |
|---|---|---|---|
| 1 — Understand the industry | What is changing in Banking? | **PARTIAL PASS** | Industry assets expose pressures, mechanisms, participant variants, hypotheses, Unknowns and Contradictions. A user would still need a derived Flora view because the manifest does not encode the journey. |
| 2 — Why change matters now | Why is this issue commercially important now? | **PARTIAL PASS** | Observations and hypotheses contain evidence cut-off and some monitoring indicators. Observation-level freshness and timing triggers are not consistently machine-exposed. |
| 3 — Identify affected enterprises | Which enterprises are most exposed or most likely to act? | **PARTIAL** | Enterprise twins and matrices support comparison, but no governed priority view distinguishes commercially interesting, requires more learning, inaccessible, weakly evidenced and not priority. |
| 4 — Understand a specific enterprise | Why this enterprise? | **PARTIAL** | Enterprise twins provide enterprise-specific narrative and mechanisms. Executive-owner and decision-owner fields are inconsistent and usually not explicit. |
| 5 — Inspect a hypothesis | What do we believe may need to change? | **PASS for human inspection; PARTIAL for machine navigation** | Hypotheses include statements, confidence, observations, mechanisms, enterprise models, evidence, contradictions, Unknowns and evidence required. Direct evidence IDs and reverse lineage are not structured per hypothesis. |
| 6 — Decide next commercial action | What should I do next? | **PARTIAL / NOT READY FOR AUTOMATION** | The domain supports proportionate learning actions, but recommendations are not governed navigation objects and must not be generated as sales actions without additional lineage. |

## 4. Flora working modes assessed

| Mode | Readiness | Notes |
|---|---|---|
| Explore | **PARTIAL PASS** | Strong content exists for industry change, mechanisms and Unknowns. Needs a derived Banking Industry Overview view. |
| Focus | **PARTIAL** | Enterprise and participant comparisons exist, but access indicators, timing and priority categories are incomplete. |
| Shape | **PARTIAL** | Hypotheses and executive tensions support shaping conversations, but executive specificity and action lineage are not sufficient for confident recommendations. |

## 5. Suggested Flora view readiness

| View | Information available | Authoritative source assets | Missing data | Missing relationships | Derivation required | Confidence | Supported now? |
|---|---|---|---|---|---|---|---|
| Banking Industry Overview | Pressures, mechanisms, participant variants, hypotheses, Unknowns. | Foundation, Industry Twin, Mechanisms Model, Hypotheses. | None blocking for overview. | Journey-level links. | Summarise across assets. | Medium-High | Partial. |
| Why Now / Change Signals | Evidence cut-off, observations, monitoring indicators. | Hypotheses, Industry Twin, Observation lineage inherited. | Observation dates and freshness per evidence item. | Observation-to-source-to-hypothesis direct links. | Freshness calculation. | Medium | Partial. |
| Pressure and Mechanism Explorer | BM-01 to BM-22, tensions and decision envelopes. | Four-Bank Matrix, Mechanisms Model, Industry Twin. | Canonical mechanism catalogue asset pending upload. | Mechanism-to-observation structured edges. | Build mechanism graph. | Medium-High | Partial. |
| Participant-Type Comparison | Incumbent, challenger, mutual, universal, platform variants. | Industry Twin, matrices, enterprise twins. | Comparable cross-cycle data. | Participant-type to enterprise exposure edges. | Comparison view. | Medium | Partial. |
| Enterprise Comparison | Enterprise twins and matrix differences. | Enterprise Twins, matrices. | Access indicators, transformation appetite, timing categories. | Exposure-to-hypothesis edges. | Derived comparison. | Medium | Partial. |
| Enterprise Canvas | Enterprise-specific pressures and mechanisms. | Enterprise Twins. | Named accountable executives and blockers. | Enterprise-to-executive audience edges. | Canvas assembly. | Medium | Partial. |
| Hypothesis Workspace | Statements, lifecycle, confidence, observations, mechanisms, Unknowns. | Hypothesis register, FP-009, EGM-001. | Direct source evidence IDs per hypothesis. | Evidence-to-observation-to-hypothesis edges. | Parse hypothesis sections. | Medium-High | Partial. |
| Evidence and Contradiction View | Supporting and contradicting evidence prose. | Hypotheses, Observation Register lineage, ADR-005. | Direct evidence objects. | Contradicts/supports structured edges. | Evidence graph. | Medium | Partial. |
| Executive Stakeholder View | Generic executive tension owners. | Mechanisms Model, EI-012, FP-009. | Enterprise-specific named owners, sponsors, blockers. | Hypothesis-to-executive-owner edges. | Role mapping with warnings. | Low-Medium | Not fully. |
| Next Best Commercial Action | Method allows provoke/workshop/learn/defer. | EGM-001, EI-012, FP-009, ADR-005. | Recommendation objects and action lineage. | Hypothesis-to-action edges. | Decision constraints. | Low-Medium | Not automation-ready. |

## 6. Representative hypotheses sampled

The validation sampled `BRH-003`, `BRH-007` and `BRH-008` because they cover distribution/trust, AI/outcome evidence and platform/resilience optionality.

### 6.1 BRH-003 — Physical access may become shared trust infrastructure

Forward lineage:

| Source asset ID | Target asset ID | Relationship type | Resolves | Machine-discoverable | Understandable to Strategic Sales Director | Ambiguity / missing context |
|---|---|---|---|---|---|---|
| `BRH-003` | `BK-OBS-014`, `BK-OBS-015`, `BK-OBS-016`, `BK-OBS-029`, `BK-OBS-047` | uses_observation | Yes per prior validation report | Partially; IDs are in prose list | Yes | Observation source evidence not directly embedded. |
| `BRH-003` | `BM-04`, `BM-02`, `BM-14`, `BM-15` | uses_mechanism | Yes | Partially; IDs are in prose list | Mostly | Requires mechanism lookup. |
| `BRH-003` | `BK-ENT-003`, `BK-ENT-001`, `BK-INF-001`, industry assets | affects_enterprise_model | Yes by named model | Partially; names not all asset IDs | Yes | Enterprise model names should be asset IDs. |
| `BRH-003` | Foundation / Industry Twin / Observation Register | evidenced_by | Indirect | No direct evidence IDs | Partially | Evidence inherited; reverse lineage weak. |
| `BRH-003` | EGM-001 / FP-009 | governed_by_methodology | Register-level only | Partially | Yes | Methodology not repeated on each hypothesis. |

Reverse lineage:

| Source asset ID | Target asset ID | Relationship type | Resolves | Machine-discoverable | Understandable | Ambiguity / missing context |
|---|---|---|---|---|---|---|
| Foundation / Industry Twin branch-access evidence | `BK-OBS-014` etc. | evidenced_observation | Indirect | Weak | Yes | Requires Observation Register availability. |
| `BK-OBS-047` | `BM-04`, `BM-02` | indicates_mechanism_or_signal | Indirect | Weak | Yes | Branch cost/trust contradiction must remain visible. |
| `BM-04` / `BM-02` | `BRH-003` | supports_hypothesis | Yes by hypothesis list | Partially | Yes | No reverse index. |
| `BRH-003` | Potential action | enables_commercial_action | No governed action object | No | Yes if derived with warnings | Should be learning/provocation, not proposal. |

Executive specificity:

- **Who:** Generic likely owners exist in the Executive Tension Register for digital efficiency vs inclusion: COO, Retail CEO and Customer Director. Enterprise-specific named owner, sponsor, influencer and blocker are missing.
- **Why now:** App-first/not app-only access and shared access models are recorded; evidence freshness is not fully exposed per observation.
- **Why them:** Nationwide and Lloyds variants are visible; enterprise-specific branch/hub economics and customer segment reliance remain Unknown.
- **What evidence:** Supporting observations, mechanisms, contradiction and Unknowns are visible; direct source evidence lineage is inherited.
- **What next:** Proportionate action is learn more or prepare an executive provocation that tests branch/hub usage, inclusion outcomes and trust economics. Do not propose branch transformation or shared-access implementation without enterprise-specific evidence.

### 6.2 BRH-007 — Banking AI may mature as governed decision infrastructure

Forward lineage:

| Source asset ID | Target asset ID | Relationship type | Resolves | Machine-discoverable | Understandable | Ambiguity / missing context |
|---|---|---|---|---|---|---|
| `BRH-007` | `BK-OBS-017`, `BK-OBS-019`, `BK-OBS-020`, `BK-OBS-040`, `BK-OBS-042`, `BK-OBS-048` | uses_observation | Yes per prior validation report | Partially | Yes | No direct evidence IDs per observation in hypothesis. |
| `BRH-007` | `BM-17`, `BM-20`, `BM-14`, `BM-13`, `BM-11`, `BM-12` | uses_mechanism | Yes | Partially | Mostly | Requires lookup to translate mechanism IDs. |
| `BRH-007` | `BK-ENT-001`, `BK-ENT-002`, `BK-ENT-004`, `BK-ENT-005`, `BK-ENT-006`, `BK-ENT-007`, `EGM-001` | affects_enterprise_model | Yes by named model | Partially | Yes | Affected list mixes enterprise twins and methodology. |
| `BRH-007` | enterprise-twin AI use-case evidence | evidenced_by | Indirect | Weak | Yes | Deployment evidence is not benefit evidence. |
| `BRH-007` | EGM-001 / FP-009 | governed_by_methodology | Register-level | Partially | Yes | Hypothesis lifecycle state is register-level candidate. |

Reverse lineage:

| Source asset ID | Target asset ID | Relationship type | Resolves | Machine-discoverable | Understandable | Ambiguity / missing context |
|---|---|---|---|---|---|---|
| Enterprise-twin AI use-case evidence | `BK-OBS-017` etc. | evidenced_observation | Indirect | Weak | Yes | Source-to-observation mapping not exposed in Flora manifest. |
| `BK-OBS-048` | `BM-17` / `BM-20` / `BM-14` | indicates_mechanism_or_signal | Indirect | Weak | Yes | AI benefit vs assurance contradiction must remain visible. |
| `BM-17` / `BM-20` / `BM-14` | `BRH-007` | supports_hypothesis | Yes by hypothesis list | Partially | Yes | No reverse index. |
| `BRH-007` | Potential action | enables_commercial_action | No governed action object | No | Yes if derived with constraints | Best action is validation conversation or evidence request. |

Executive specificity:

- **Who:** Generic roles exist: CIO, COO, Chief Data/AI Officer and CRO. Enterprise-specific accountable executives, sponsors and blockers are missing.
- **Why now:** AI deployment, Consumer Duty, data quality, model assurance and control burden are visible; per-enterprise timing and programme movement are inconsistent.
- **Why them:** Enterprise twins show multiple AI use cases; maturity, benefit and adoption depth remain Unknown.
- **What evidence:** Supporting observations and contradictions are visible; independent productivity evidence is explicitly weak.
- **What next:** Seek named evidence or propose a discovery conversation about governed AI decision infrastructure, use-case maturity and assurance. Do not propose scaled AI transformation as an accepted need.

### 6.3 BRH-008 — Cloud and core migration may become a strategic optionality problem

Forward lineage:

| Source asset ID | Target asset ID | Relationship type | Resolves | Machine-discoverable | Understandable | Ambiguity / missing context |
|---|---|---|---|---|---|---|
| `BRH-008` | `BK-OBS-017`, `BK-OBS-018`, `BK-OBS-032`, `BK-OBS-033`, `BK-OBS-044`, `BK-OBS-045` | uses_observation | Yes per prior validation report | Partially | Yes | Observation-level source freshness not directly surfaced. |
| `BRH-008` | `BM-16`, `BM-19`, `BM-13`, `BM-15`, `BM-17` | uses_mechanism | Yes | Partially | Mostly | BM-16 and BM-19 must not be collapsed. |
| `BRH-008` | `BK-INF-001`, industry twin, incumbent and challenger twins | affects_enterprise_model | Yes by named model | Partially | Yes | Enterprise model names should use stable asset IDs. |
| `BRH-008` | infrastructure and enterprise-twin dependency evidence | evidenced_by | Indirect | Weak | Yes | Critical workload exposure is opaque. |
| `BRH-008` | EGM-001 / FP-009 | governed_by_methodology | Register-level | Partially | Yes | Rejection conditions are evidence demands, not formal lifecycle rules. |

Reverse lineage:

| Source asset ID | Target asset ID | Relationship type | Resolves | Machine-discoverable | Understandable | Ambiguity / missing context |
|---|---|---|---|---|---|---|
| Infrastructure/enterprise cloud evidence | `BK-OBS-017` etc. | evidenced_observation | Indirect | Weak | Yes | Direct source IDs absent from hypothesis. |
| `BK-OBS-044` / `BK-OBS-045` | `BM-16` / `BM-19` | indicates_mechanism_or_signal | Indirect | Weak | Yes | Needs separate optionality, resilience and exit-control dimensions. |
| `BM-16` / `BM-19` | `BRH-008` | supports_hypothesis | Yes by list | Partially | Yes | No reverse index. |
| `BRH-008` | Potential action | enables_commercial_action | No governed object | No | Yes if derived | Workshop only if enterprise-specific migration or CTP exposure exists. |

Executive specificity:

- **Who:** Generic likely owners exist: CIO, CTO, CRO and Supplier Risk. Enterprise-specific decision owners, sponsors, influencers and blockers are missing.
- **Why now:** Regulated dependency, cloud concentration and operational resilience pressure are visible; external deadlines and per-enterprise programme movement are incomplete.
- **Why them:** Incumbent legacy and challenger cloud-native variants are visible; enterprise-specific workload concentration and exit-plan maturity are Unknown.
- **What evidence:** Supporting observations and Unknowns are visible; exact critical workload maps are missing.
- **What next:** Seek named evidence on workload maps, exit plans and resilience testing. Shape a workshop only after enterprise-specific exposure is established.

## 7. Relationship defects and low-risk corrections

Corrected in this change:

- Added this Strategic Sales Navigation Specification as a governed Flora-facing navigation asset.
- Added this Validation Report as a governed report.
- Updated the Flora Banking Knowledge Register to include the new specification and validation report.
- Corrected a Markdown table discontinuity in the Flora Banking Knowledge Register so the reinvention-hypothesis row remains in the asset table.

Recorded but not silently repaired:

- Flora manifest asset relationships are mostly empty or prose-based for core Banking assets.
- Hypothesis supporting enterprise models use names rather than stable asset IDs.
- Observation-to-source-evidence lineage is inherited from the Observation Register and not exposed as direct machine-readable edges in the hypothesis asset.
- Reverse lineage indexes do not yet exist.
- Recommendations / next-best-actions are not governed assets.

## 8. Validation checks

| Check | Status | Notes |
|---|---|---|
| Stable asset IDs | **PASS** | Asset IDs are stable in manifests and hypothesis register uses stable hypothesis IDs. |
| Relationship targets | **PARTIAL** | Register-level methodology relationships exist; most asset relationships are empty or prose-only. |
| Document paths | **PASS** | Manifest paths for existing Banking files resolve under `enterprise-knowledge/`. |
| Manifest parsing | **PASS** | JSON manifest parses; YAML was inspected textually because PyYAML is not a project dependency. |
| Duplicate IDs | **PASS** | No duplicate asset IDs found in the JSON manifest. |
| Orphaned assets | **PARTIAL** | Some Markdown files are not listed as standalone manifest assets; not all are intended runtime assets. |
| Forward lineage | **PARTIAL** | Hypothesis to observation/mechanism/model is visible but not fully structured. |
| Reverse lineage | **FAIL / GAP** | No reverse index from evidence to observation to hypothesis to action. |
| Methodology ownership | **PASS at register level** | Reinvention register is governed by EGM-001 and references FP-009-compatible controls. |
| Confidence preservation | **PASS** | Hypotheses preserve confidence statements. |
| Unknown preservation | **PASS** | Hypotheses preserve Unknowns and evidence required. |
| Contradiction preservation | **PASS** | Hypotheses preserve contradicting evidence. |
| Human-supplied knowledge labelling | **PARTIAL** | Human-supplied comparison mechanisms are labelled in some enterprise assets; Flora metadata does not expose a universal flag. |
| Recommendation lineage | **FAIL / GAP** | No governed recommendation object with inspectable lineage exists for these journeys. |
| Local Markdown links | **PARTIAL** | New local register links resolve; broader repository link validation was executed but cannot guarantee external links. |
| Repository consistency | **PARTIAL** | Repository supports discovery but not a complete Strategic Sales navigation runtime. |

## 9. Commercial-action readiness

The domain supports learning-oriented next actions and executive provocation preparation when action wording preserves uncertainty. It is not ready to automatically recommend selling, proposing a solution, or asserting enterprise need.

Allowed action posture now:

- learn more;
- seek named evidence;
- prepare executive provocation with caveats;
- propose discovery conversation;
- shape workshop only where enterprise-specific evidence is visible;
- defer where evidence is weak.

Not supported now:

- automatic opportunity scoring;
- definitive enterprise prioritisation;
- named executive targeting without enterprise validation;
- product or transformation recommendations without additional evidence lineage.

## 10. Unknowns, Contradictions and gaps

### Unknowns preserved

- Primary-account salary-flow and direct-debit penetration.
- Deposit elasticity and duration by segment.
- Branch/hub usage, inclusion outcomes and retention effect.
- AI maturity, benefit baselines and model-risk arrangements.
- Critical workload concentration, cloud exit-plan maturity and core migration sequencing.
- Application decommissioning and realised simplification benefits.
- Post-acquisition integration outcomes.

### Contradictions preserved

- Digital engagement does not prove durable current-account primacy.
- Branches are both cost burdens and trust assets depending on participant type.
- AI productivity claims coexist with assurance and control burden.
- Cloud enables agility while increasing concentration and exit risk.
- Acquisitions can create complexity rather than reinvention.
- Product-level convergence does not prove economic convergence.

### Human-knowledge labelling gaps

- Human-supplied comparison labels exist in some enterprise prose but are not uniformly exposed in Flora-facing metadata.
- Derived relationships and sales-readiness judgements need explicit labels to avoid being mistaken for external evidence.

## 11. Architectural observations

- A Strategic Sales Director needs derived views, not repository navigation.
- The current Banking domain has strong governed content but weak machine-readable relationship density.
- The hypothesis register is human-inspectable but should gain a structured relationship table per hypothesis.
- The future Banking Mechanism Catalogue (`BK-MEC-001`) remains planned/pending, so the Four-Bank Matrix is currently the practical mechanism authority.
- Recommendation lineage should become a governed object before Flora offers next-best-action automation.
- Executive specificity should be separated into generic role evidence and enterprise-specific ownership evidence.

## 12. Outstanding research and runtime gaps

| Gap | Classification | Required resolution |
|---|---|---|
| Direct evidence IDs per observation and hypothesis. | Research / modelling required | Add evidence objects and lineage tables. |
| Enterprise-specific executive owners and blockers. | Research required / human validation required | Validate roles against enterprise evidence and human account knowledge. |
| Recommendation objects and action lineage. | Architectural decision required | Define governed next-best-action schema. |
| Runtime loader validation. | Runtime capability gap | Execute loader/service ingestion tests when available. |
| Runtime UX validation. | Runtime capability gap | Test with operational Flora interface or harness. |
| Human-supplied knowledge flags in manifests. | Architecture / metadata gap | Add controlled metadata fields. |
| Reverse lineage index. | Architecture / implementation gap | Build evidence-to-observation-to-mechanism-to-hypothesis index. |

## 13. Completion report

### Assets inspected

See section 2.

### Hypotheses sampled

- `BRH-003` — physical access as shared trust infrastructure.
- `BRH-007` — AI as governed decision infrastructure.
- `BRH-008` — cloud and core migration as strategic optionality.

### Journeys tested

Six required journeys were tested: understand industry, explain why now, identify affected enterprises, understand a specific enterprise, inspect a hypothesis and decide the next commercial action.

### Navigation modes assessed

Explore, Focus and Shape were assessed. Explore is strongest; Focus and Shape remain partial because executive specificity, timing and action lineage are incomplete.

### Lineage results

Forward lineage is inspectable for sampled hypotheses at hypothesis-to-observation, hypothesis-to-mechanism and hypothesis-to-enterprise-model level. Evidence and governing methodology are visible mostly at register or prose level. Reverse lineage is not sufficiently machine-discoverable.

### Defects corrected

- Created `enterprise-knowledge/banking/flora/Banking-Strategic-Sales-Navigation-Specification.md`.
- Created `enterprise-knowledge/banking/governance-reports/Banking-Strategic-Sales-Navigation-Validation-Report.md`.
- Updated Flora-facing Banking register and machine manifest entries for these assets.
- Corrected the Flora register table discontinuity around the reinvention-hypothesis row.

### Unresolved content gaps

- Direct evidence IDs per hypothesis.
- Enterprise-specific executive ownership and blocker mapping.
- Timing and freshness fields at observation level for Flora display.
- Recommendation and next-best-action governed asset model.
- Human-supplied knowledge flags in all Flora-facing metadata.

### Executive specificity gaps

Generic role audiences can be identified for many pressures, but named enterprise-specific decision owners, likely sponsors, influencers and blockers are usually missing or not machine-addressable.

### Repository readiness grade

Repository discovery readiness: **PARTIAL**.

### Runtime tests executed or not executed

Runtime ingestion validation: **NOT EXECUTED**.  
Runtime UX validation: **NOT EXECUTED**.

### Files created or changed

- `enterprise-knowledge/banking/flora/Banking-Strategic-Sales-Navigation-Specification.md`
- `enterprise-knowledge/banking/governance-reports/Banking-Strategic-Sales-Navigation-Validation-Report.md`
- `enterprise-knowledge/banking/flora/Banking-Knowledge-Register.md`
- `enterprise-knowledge/banking/flora/Banking-Knowledge-Manifest.json`
- `enterprise-knowledge/banking/MANIFEST.yaml`

### Validation results

Repository checks found no duplicate JSON manifest asset IDs and all JSON manifest Banking paths resolve under `enterprise-knowledge/`. Runtime validation was not executed.

### Commit hash

To be completed after commit.

### PR reference

To be completed after PR creation.

### Chief Architect decisions still required

- Whether to define a governed Next Best Commercial Action asset model.
- Whether to require per-hypothesis structured lineage tables in Banking v0.2.
- Whether to promote `BK-MEC-001` from planned asset to canonical mechanism catalogue.
- How to model human-supplied knowledge and inferred relationships in Flora-facing manifests.
- Whether executive specificity should be a required acceptance criterion for enterprise twins.
