# Single Factual Truth and Assessment-Language Closure

## Governing architecture

This correction follows the existing governed path rather than introducing a
new factual or lifecycle model. The Canonical Factual Projection (CFP) owns
Enterprise factual dimensions and `enterprise_factual_synthesis`; its
`EnterpriseFactualSynthesis` is a read-only derivative with proposition-level
Evidence lineage. `factual_projection_for_enterprise` carries that synthesis
to the Enterprise dossier. The Governed Blueprint Import Runtime owns receive,
validate, candidate staging, human review and explicit promotion. Candidate
facts remain candidate facts and are never promoted by presentation.

Architectural intent, implemented capability and programme state remain
distinct. Enterprise Economics and Leadership / Governance are architectural
intent without independent TEL-001 runtime dimensions. Domain remains absent
without an explicit semantic domain. The staged TEL-001 candidate set remains
the current programme state; synthesis does not constitute a human decision.

## Canonical owners

| Concern | Existing owner | Consumer |
|---|---|---|
| Enterprise qualification and synthesis | `canonical_factual_projection.enterprise_factual_synthesis` | CFP, dossier and diagnostics |
| Executive factual state | `factual_projection_for_enterprise` carrying `enterprise_synthesis` | `executive_workspace._dossier` |
| Organisation Overview | dossier projection of the carried CFP synthesis | Enterprise route |
| Reconciliation | `_population_and_association_reconciliation` | Advanced Inspection |
| Human import lifecycle | `ImportHumanReviewRepository` and `ImportLifecycleService` | `presentation_contract.human_import_state` and all normal surfaces |
| Confidence | source `SemanticObject.confidence` provenance | Opportunity presentation, without a lifecycle suffix |
| Current Change | `config/current_pilot_change.json` through `pilot_change.current_pilot_change` | top panel and deployment proof |

No new canonical factual, Observation, governance, assessment or lifecycle
model was introduced.

## First divergence and diagnostic consumer defect

The BT source does not supply the explicit `organisation_description` profile
field. Candidate semantic construction nevertheless retains other governed
Profile aliases and the qualifying Operating Model and Strategy facts. CFP
synthesis qualifies evidence-backed propositions and the dossier consumes the
result as a populated Organisation Overview.

The first divergence was subsequently in the reconciliation consumer. Its
Organisation / Enterprise Profile row was built only from
`enterprise_factual_dimensions.profile`. It copied that explicit/pre-synthesis
presence into its canonical, executive and rendered columns. It never read the
`EnterpriseFactualSynthesis` already carried by
`factual_projection_for_enterprise`. Thus explicit source absence was
incorrectly presented as final truthful absence even while the dossier rendered
the supported synthesis.

The corrected Organisation / Enterprise Profile row preserves explicit source
and candidate-explicit absence, then obtains the canonical/governed result,
executive consumption, rendered presence, Evidence, Unknowns and
Contradictions from the same carried synthesis as the dossier. Other factual
dimensions retain their existing dimension-specific semantics. The existing
Synthesis Trace remains and agrees with reconciliation; no competing panel was
added.

## Human-import consumer audit and confidence semantics

| Occurrence class | Finding | Correction |
|---|---|---|
| Canonical owner | review repository plus lifecycle service | unchanged |
| Valid consumer | `presentation_contract.human_import_state` | unchanged canonical vocabulary |
| Duplicated derivation | Enterprise index candidate pill | consumes the canonical candidate wording |
| Obsolete language | Opportunity confidence appended “assessment not yet performed” | confidence now reports only the supplied provenance |
| Obsolete language | owner-assessment presentation and diagnostics implied pending governance | reports that no owner assessment is supplied, without inventing a queue/review process |
| Obsolete language | general opportunity timing/value placeholders said “not yet assessed” | reports “Not supplied” |
| Test/fixture only | internal `assessment_pending_governance` compatibility state | retained where it is an internal owner-projection contract, not rendered as a fictional process |

Confidence and human import state are intentionally separate. `Supplied` says
that confidence metadata came with the candidate source. It does not say that a
second assessment occurred or is queued. Human import state remains `Candidate
— awaiting human import decision` until the existing review/promotion owners
say otherwise.

## Current Change ownership defect

The top Import panel already loaded `current_pilot_change.json`, but
`runtime_proof.proof_html` independently hard-coded the historical title
“Deployment-to-Runtime Proof Audit”. Deployment proof now loads the same
Current Change declaration as the top panel. The active title is **Single
Factual Truth & Assessment-Language Closure**, its deployed marker is aligned,
and its operator outcomes/checklist describe this correction. No historical
sprint identity remains in the runtime proof implementation.

## Six-Enterprise comparison

Validation used the unchanged governed fixture
`docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip`
with SHA-256
`bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.

| Enterprise | Explicit profile | Governed synthesis | Dossier | Diagnostic final state | Result |
|---|---|---|---|---|---|
| BT Group | Absent | SUPPORTED | Present | Present | PASS |
| CityFibre | Absent | SUPPORTED | Present | Present | PASS |
| Openreach | Absent | SUPPORTED | Present | Present | PASS |
| TalkTalk | Absent | SUPPORTED | Present | Present | PASS |
| Virgin Media O2 | Absent | SUPPORTED | Present | Present | PASS |
| VodafoneThree | Absent | SUPPORTED | Present | Present | PASS |

The controlled empty-Enterprise regression remains `TRUTHFUL ABSENCE`, proving
that alignment does not force presence. The BT supported statement, proposition
Evidence, unresolved Organisation Overview requirements, Unknowns and
Contradictions remain unchanged.

## Route validation and implementation proof

The real Import Twin, Advanced Inspection, all six Enterprise dossier routes
and Commercial Opportunities route were rendered from a fresh staging of the
unchanged fixture. Each returned HTTP 200. Page values were compared, not only
route status: BT retained the supported Organisation Overview; reconciliation
showed explicit Absent followed by governed/executive/rendered Present; every
Enterprise final state agreed; opportunity confidence remained Supplied; and
the obsolete assessment/governance-review phrases were absent.

The correction is implemented in consumers, executed during route assembly,
consumed from the CFP/human lifecycle/Current Change owners, and rendered on
the operational pages.

## Protected regressions

Fixture validation preserves 308 Relationship candidates (252 resolved, 56
unresolved, zero promoted), 13 Programmes, 17 Opportunities and six Enterprise
identities. Exact Enterprise Programme and Opportunity association sets remain
reconciled. Synthesis persistence, source mapping and candidate lifecycle are
unchanged, so no fresh import is required.

## Remaining genuine capability boundaries

* Enterprise Economics and Leadership / Governance remain architectural intent,
  not implemented independent TEL-001 factual dimensions.
* Domain remains Not established because Twin membership is not evidence of an
  explicit Enterprise domain.
* Candidate Evidence is retained at its actual source granularity; no narrower
  lineage is invented.
* Owner assessment, recommendation and promotion remain separate capabilities;
  factual presence does not imply any of them.
