# Factual Synthesis Qualification and Human Import Governance Closure

## Governing architecture and programme state

### Architectural intent

The Enterprise Intelligence Experience Standard requires Unknowns and Contradictions to be visible where they affect judgement and requires user input to remain governed candidate knowledge. The Governed Blueprint Import Runtime Specification owns receive, validate, stage, human review and explicit promotion: adapter output is candidate-only, review is human, and promotion is never automatic. Accepted ADR-001/EI-012 owns atomic evidence-backed Observation statements; reports remain projections over governed intelligence rather than new canonical knowledge.

### Implemented runtime capability

`semantic_twin` constructs read-only candidate Enterprises. `canonical_factual_projection` (CFP) owns factual dimensions, qualification and synthesis. Its `EnterpriseFactualProposition` is a derivative trace record, not a new Observation model: it retains the source dimension/field, deterministic fact ID, verbatim statement, Evidence, confidence and explicitly relevant uncertainty. `factual_projection_for_enterprise` carries the one synthesis result to `executive_workspace._dossier`; Organisation Overview and Advanced Inspection consume that result. Candidate, review and promotion persistence are unchanged.

### Current programme state

The unchanged TEL-001 package is staged candidate intelligence. The Chief Architect's existing import review is the human governance activity. An attributable approval and promotion remain separate existing actions. Synthesis neither reviews nor promotes.

## Canonical owners

| Concern | Canonical owner |
|---|---|
| Factual qualification and Enterprise synthesis | `canonical_factual_projection.enterprise_factual_synthesis` |
| Organisation / Enterprise Profile factual state | CFP `profile` dimension and `EnterpriseFactualSynthesis` |
| Unknown and Contradiction preservation | semantic candidate attributes projected by CFP |
| Executive consumption | `factual_projection_for_enterprise` to `executive_workspace._dossier` |
| Rendered Organisation Overview | `_dossier`, consuming (not rebuilding) CFP synthesis |
| Human import state | existing `ImportHumanReviewRepository` plus `ImportLifecycleService`; shared presentation vocabulary in `presentation_contract.human_import_state` |

No new canonical factual, Observation, governance or lifecycle model was introduced.

## Governed fixture and source trace

The inspected file is `docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip`. Its measured SHA-256 is `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`, exactly the governed value. The archive was not modified.

BT source `ENT-BT` contains an `executive_overview.what` proposition, corporate operating role, corporate strategy/challenges and linked Evidence. The adapter retains these as candidate `description`, `operating_model` and `strategy`; semantic construction retains them on the Enterprise identity; the CFP exposes Profile, Operating Model and Strategy. Therefore usable meaning is present through source, candidate, semantic construction and factual dimensions.

## Old qualification rule and exact BT failure

The old rule built the relevant set from present Profile, Operating Model and Strategy dimensions, but then required **Profile to be present and at least two relevant dimensions in total**. Any failure returned `INSUFFICIENT EVIDENCE` and empty prose. It did not evaluate whether each proposed clause independently had Evidence. In the proven persisted runtime BT had Source Profile absent while Operating Model and Strategy were present, so `not profile.present` was true even though two supported contextual propositions and six Evidence references survived.

| Rule/condition | Why it existed | Proven BT value | Result | Architecturally justified |
|---|---|---:|---|---|
| Only Profile, Operating Model and Strategy may answer Organisation Overview | Prevent unrelated facts filling a profile | Operating Model, Strategy | PASS | YES |
| Explicit Profile required | Intended to ensure an answer to “what is it?” | absent in proven runtime | FAIL | PARTIAL: useful precedence, invalid as a universal gate |
| At least two relevant dimensions | Intended to avoid thin prose | 2 | PASS | NO as a fact-count proxy for proposition sufficiency |
| Evidence gathered from qualifying identity dimensions | Preserve lineage | 6 refs | PASS | YES, but old rule did not qualify each clause with it |
| Confidence retained | Do not turn confidence into certainty | supplied | PASS | YES |
| Unknowns retained | Preserve uncertainty | UN-002, UN-004, UN-005, UN-011 | PASS | YES |
| Contradictions retained | Preserve disagreement | CR-003, CR-004 | PASS | YES |
| Unknown/Contradiction presence as universal veto | Not explicitly coded | not a veto | PASS | Universal veto would be NO |

The **first divergence** was the synthesis qualification decision: usable facts reached CFP dimensions, then the Profile prerequisite rejected the entire Enterprise rather than evaluating the statement each fact could support.

## Proposition-level correction

For the governed relevant dimensions (Profile, Operating Model, Strategy):

1. no relevant candidate fact means `TRUTHFUL ABSENCE`;
2. a candidate proposition with no linked Evidence is rejected; if none remain the result is `INSUFFICIENT EVIDENCE`;
3. an explicitly dimension-mapped material Contradiction rejects that proposition; if none remain the result is `CONTRADICTED`;
4. every remaining proposition is `SUPPORTED`, retains its verbatim candidate value and atomic lineage, and may be composed deterministically;
5. an explicit evidenced Profile is used under the same Profile-first precedence, but is not required before a separately supported Operating Model or Strategy proposition can be represented;
6. no source value is paraphrased, inferred or persisted.

Unscoped Unknown and Contradiction references remain preserved on the synthesis but are not guessed to affect every proposition. Existing explicit `unknown_dimensions` and `contradiction_dimensions` mappings are honoured. No relevance score or name-based inference is introduced.

CR-003 concerns conflation of premises passed, availability and take-up. CR-004 concerns Openreach fibre monetisation versus regulatory constraints. Neither contradicts BT's supplied integrated operating structure or the existence of its listed current challenges, so both remain visible and neither blocks those propositions. Where an input explicitly maps a Contradiction to the same dimension, that dimension is rejected and unrelated supported dimensions remain eligible.

## BT result

BT is `SUPPORTED` from `FACT-ENT-BT-PROFILE`, `FACT-ENT-BT-OPERATING-MODEL`, and `FACT-ENT-BT-STRATEGY`. Evidence is `EV-BT-FY26`, `EV-BT-Q1FY27`, `EV-BT-AI26`, `EV-BT-KYNDRYL`, `EV-BT-DYNATRACE`, and `EV-BT-CMA-NEXFIBRE-RESPONSE26`. Unknowns UN-002, UN-004, UN-005, UN-011 and Contradictions CR-003, CR-004 remain preserved; none is explicitly mapped as blocking these propositions.

The rendered statement is:

> BT Group is a UK-headquartered telecommunications group spanning consumer broadband/mobile, business connectivity, international services and Openreach fixed-access infrastructure. Business Model: Integrated operator with Consumer, Business, International and Openreach CFUs. Current Challenges: Revenue pressure; Debt/capex intensity; Regulated pricing constraints; Enterprise complexity; PSTN/copper migration execution.

## Six-Enterprise comparison

All facts below are the relevant Profile, Operating Model and Strategy source facts. All three qualify for each Enterprise; none is rejected because each identity has linked Evidence and no dimension-mapped contradiction. Global Unknowns and Contradictions remain preserved and non-blocking.

| Enterprise | Qualifying fact IDs | Evidence | Unknowns | Contradictions | Result / rendered overview |
|---|---|---|---|---|---|
| BT Group | PROFILE, OPERATING-MODEL, STRATEGY | EV-BT-FY26, EV-BT-Q1FY27, EV-BT-AI26, EV-BT-KYNDRYL, EV-BT-DYNATRACE, EV-BT-CMA-NEXFIBRE-RESPONSE26 | UN-002, UN-004, UN-005, UN-011 | CR-003, CR-004 | SUPPORTED / PRESENT |
| CityFibre | PROFILE, OPERATING-MODEL, STRATEGY | EV-CITYFIBRE-FY25, EV-BDUK-PG-JUL2026, EV-BDUK-CAMBS, EV-BDUK-SUSSEX, EV-BDUK-KENT | UN-002, UN-004, UN-005, UN-014 | CR-003, CR-005 | SUPPORTED / PRESENT |
| Openreach | PROFILE, OPERATING-MODEL, STRATEGY | EV-BT-FY26, EV-OR-FTTP26, EV-BDUK-OR-FRAMEWORK, EV-BDUK-PG-JUL2026, EV-BT-CMA-NEXFIBRE-RESPONSE26 | UN-002, UN-004, UN-005, UN-011, UN-014 | CR-003, CR-004 | SUPPORTED / PRESENT |
| TalkTalk | PROFILE, OPERATING-MODEL, STRATEGY | EV-TALKTALK-CH-2025, EV-PXC-REBRAND24, EV-TALKTALK-FT-FUNDING26 | UN-002, UN-003, UN-004, UN-007, UN-005 | none | SUPPORTED / PRESENT |
| Virgin Media O2 | PROFILE, OPERATING-MODEL, STRATEGY | EV-VMO2-Q4FY25-PDF, EV-VMO2-RAN-2026, EV-VMO2-LUMI-2025, EV-NEXFIBRE-SUBSTANTIAL26, EV-CMA-NEXFIBRE-P2-26 | UN-002, UN-004, UN-009, UN-012 | CR-006, CR-007 | SUPPORTED / PRESENT |
| VodafoneThree | PROFILE, OPERATING-MODEL, STRATEGY | EV-VT-OWN-COMPLETE26, EV-VT-5GSA26, EV-VT-WRO25, EV-CMA-VT-CLOSE25 | UN-002, UN-004, UN-008, UN-011 | CR-002 | SUPPORTED / PRESENT |

The complete verbatim statement for each Enterprise is visible in the route/diagnostic acceptance output; the table does not introduce alternate prose.

## Human import lifecycle and terminology

Previous runtime wording included “Assessment not yet performed” beside imported candidates. That implied an undefined extra assessment after import. The actual implementation is: received/validated/staged candidate → Chief Architect human import review/decision → separately approved promotion. Runtime wording now uses one derived state on normal surfaces:

* `Candidate — awaiting human import decision`;
* `Human import decision recorded — not promoted`;
* `Human import decision accepted — promoted`.

This is presentation over the existing review and lifecycle repositories, not a new state machine. Factual synthesis does not mark review complete, approve Evidence, resolve uncertainty or promote anything.

## Diagnostics and protected regressions

Advanced Inspection now reports source Profile presence; candidate, qualifying and rejected input counts; qualification result; proposition count; source dimensions and fact IDs; rejection reasons; Evidence and confidence; preserved and blocking Unknowns/Contradictions; executive/rendered presence; human import state; and first divergence. The presentation reconciliation uses the same candidate human-import terminology.

Acceptance against the unchanged ZIP preserves 308 accepted Relationship candidates, 13 Programmes, 17 Opportunities, six Enterprise identities, exact Enterprise Programme/Opportunity association sets, and the candidate/read-only boundary. Controlled regressions prove truthful absence, unsupported facts, same-dimension contradiction exclusion with unrelated fact eligibility, unrelated Unknown preservation, and non-empty Evidence lineage for every synthesized proposition.

No fresh import is required because candidate persistence and semantic construction are unchanged; qualification is a read-only CFP operation over existing candidates. Existing Deployment-to-Runtime Proof remains present and was not expanded or reinvestigated.

## Remaining genuine boundaries

* TEL-001 supplies Evidence at Enterprise identity level rather than a distinct Evidence set for every nested source field. Propositions retain that actual lineage; the runtime does not invent narrower mappings.
* Only explicit source mappings can establish that an Unknown or Contradiction blocks a particular dimension. Unscoped references are preserved but not speculatively classified.
* Enterprise Economics and Leadership/Governance remain unsupported independent TEL-001 dimensions.
* Industry/domain remains absent where no explicit Enterprise domain exists; Twin membership is not evidence.
* Synthesis remains a deterministic candidate read projection, not owner assessment, inference, recommendation or canonical promotion.
