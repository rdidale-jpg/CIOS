# TEL-001 Enterprise Factual Synthesis & Operational Acceptance Correction

## Decision and owners

**Finding: PARTIAL.** Accepted ADR-001/EI-012 already owns atomic, evidence-backed Observation statements and requires them to remain separate from narrative, inference and recommendation. The imported-Twin runtime already implements that doctrine in `observation_runtime.py`: it deterministically selects governed canonical executive fields, emits stable Observation-compatible IDs, and retains evidence, confidence, subject, originating fields and candidate/read-only status. The Canonical Factual Projection (CFP) already composes the full Enterprise read model and preserves Evidence, Unknowns, Contradictions and source lineage. What did not exist was an explicit, reusable CFP result for composing multiple qualifying Enterprise factual dimensions into an executive description.

The **canonical owner** is the existing Canonical Factual Projection. The **runtime owner** is `enterprise_factual_synthesis` in `canonical_factual_projection.py`, downstream of semantic candidate construction and compatible with the existing imported-Twin Observation builder. No second Observation or Enterprise model was introduced. Organisation Profile previously read only literal description aliases in page code, so it did not ask the shared factual owner whether sufficient facts existed.

The correction adds a read-only `EnterpriseFactualSynthesis`. It requires the governed Profile dimension plus at least one Operating Model or Strategy dimension; selects only canonical values; composes those values without paraphrase; and returns input dimensions, deterministic fact IDs, Evidence, confidence, Unknowns, Contradictions, source object and candidate object. It neither persists nor changes candidate state.

## Semantic distinctions

| Concept | Meaning in this correction |
|---|---|
| Source fact | A supplied candidate field/value with source lineage. |
| Observation | An atomic, evidence-backed statement owned by EI-012 and represented by the imported-Twin Observation-compatible builder. |
| Factual projection | The CFP read contract over qualifying retained candidate facts. |
| Factual synthesis | Deterministic composition of qualifying CFP propositions, with all lineage retained. |
| Inference | A proposition beyond supplied facts; excluded. |
| Assessment | Owner judgement about facts or effectiveness; not invoked. |
| Recommendation | Proposed action supported by reasoning lineage; not eligible and not invoked. |

The synthesis reuses Observation-compatible inputs but does not pretend that a multi-proposition executive description is itself an atomic Observation. It is a view over facts, consistent with EI-012's rule that reports are views over governed intelligence.

## BT factual input trace

The unchanged candidate `ENT-BT` supplies Profile, Operating Model and Strategy. The generated fact IDs are `FACT-ENT-BT-PROFILE`, `FACT-ENT-BT-OPERATING-MODEL`, and `FACT-ENT-BT-STRATEGY`. Material Evidence includes `EV-BT-FY26`, `EV-BT-Q1FY27`, `EV-BT-AI26`, `EV-BT-KYNDRYL`, `EV-BT-DYNATRACE`, and `EV-BT-CMA-NEXFIBRE-RESPONSE26`. Confidence is “High for finance/structure; Medium for procurement detail”. Unknowns `UN-002`, `UN-004`, `UN-005`, `UN-011` and Contradictions `CR-003`, `CR-004` remain attached.

The rendered synthesis is:

> BT Group is a UK-headquartered telecommunications group spanning consumer broadband/mobile, business connectivity, international services and Openreach fixed-access infrastructure. Business Model: Integrated operator with Consumer, Business, International and Openreach CFUs. Current Challenges: Revenue pressure; Debt/capex intensity; Regulated pricing constraints; Enterprise complexity; PSTN/copper migration execution.

Every clause is reproduced from one of the three qualifying CFP dimensions. It is candidate factual intelligence. Assessment remains “not yet performed”, recommendation remains ineligible, and governance remains candidate.

## All-six result

All six candidates have sufficient qualifying evidence and therefore generate synthesis. Their Organisation Overview begins with the following supplied Profile fact and adds the first qualifying Operating Model and Strategy values with the same trace contract:

| Enterprise | Status | Profile proposition | Lineage / assessment |
|---|---|---|---|
| BT Group | GENERATED | BT Group is a UK-headquartered telecommunications group spanning consumer broadband/mobile, business connectivity, international services and Openreach fixed-access infrastructure. | PASS / independent |
| CityFibre | GENERATED | CityFibre is a wholesale full-fibre infrastructure operator and altnet consolidator. | PASS / independent |
| Openreach | GENERATED | Openreach is BT Group's structurally separated wholesale fixed-access network business. | PASS / independent |
| TalkTalk | GENERATED | TalkTalk is a UK retail broadband and connectivity group with PXC as its wholesale/platform arm. | PASS / independent |
| Virgin Media O2 | GENERATED | Virgin Media O2 is a UK fixed/mobile operator jointly owned by Liberty Global and Telefónica, with cable/fibre broadband, O2 mobile, wholesale/MVNO and business services. | PASS / independent |
| VodafoneThree | GENERATED | VodafoneThree is the combined UK mobile operator formed from Vodafone UK and Three UK and now wholly owned by Vodafone Group following completion of the CK Hutchison stake buyout. | PASS / independent |

A controlled input without Profile plus contextual dimensions returns `INSUFFICIENT EVIDENCE` and empty prose. Contradictions are returned in the trace and never resolved by selection or prose.

## Industry/domain and Research Gaps

BT and the other five controls remain **NOT SUPPORTED** for Industry/domain. Their semantic Enterprise domain field is absent. Twin title/membership is deliberately not treated as evidence, so the dossier retains “Not established”. This does not prevent factual description, and factual description no longer appears wholly missing in the Organisation Overview or Research Gap presence rule. Ownership, headquarters, employee count, explicit industry classification, and other absent requirements remain genuine gaps.

## Relationship wording

“No relationship references supplied” described references embedded in the identity factual record, not the separately resolved canonical Enterprise associations used by Programme and Opportunity sections. The shared factual presentation now says “No relationship references embedded in this factual record.” The relationship resolver, its direction/type semantics, 308 candidates and association queries were not changed.

## Operational acceptance root cause and correction

`deployment_status.decide_deployment_status` is the existing canonical decision owner for current-change inclusion evidence, functional validation, metadata limitations, candidate freshness and human readiness. It previously reached `METADATA INCOMPLETE / No` whenever release identity metadata could not prove inclusion, even after its automated functional checks passed. Candidate freshness also inferred regeneration risk from a broad component-name set and timestamps.

The owner now treats these states separately:

* failed required functional checks => `FUNCTIONAL ACCEPTANCE FAILED`, `Should I test now? NO`, with exact failed keys;
* passed functional checks plus incomplete optional metadata => `READY FOR FUNCTIONAL TEST — DEPLOYMENT METADATA INCOMPLETE`, `YES`, with exact metadata limitations;
* passed functional checks and complete inclusion metadata => `READY FOR TESTING`, `Yes`;
* explicit `candidate_state_impact=read-only` => fresh import `No`, independent of metadata timestamps.

A genuine open deployment window still reports waiting; wrong branch or a reported deployment failure remains blocking. This sprint changes only read/projection/synthesis and operational decision behaviour over retained candidates, so no fresh import is required.

## Acceptance and protected baseline

Automated acceptance loads the unchanged ZIP, builds the actual candidate/executive runtime, renders Import Twin, Advanced Inspection/Explore, Enterprise list and all six dossiers, and verifies synthesis lineage and governance. Advanced Inspection exposes `ENTERPRISE FACTUAL SYNTHESIS TRACE` with status, statement, dimensions, fact IDs, Evidence, confidence, Unknowns, Contradictions and assessment requirement.

Protected reconciliation remains 308 Relationship candidates, 13 Programmes, and 17 Opportunities across source/candidate/canonical/executive counts. All Enterprise Programme and Opportunity sets remain exact; `PROG-BT-VERIZON-JV` remains unassociated without an explicit Relationship and `OPP-BT-VERIZON-JV-INTEGRATION` remains associated through explicit relationship truth. The governed fixture checksum remains `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.
