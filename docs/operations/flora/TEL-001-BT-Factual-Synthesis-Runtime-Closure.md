# TEL-001 BT Factual Synthesis Runtime Closure

## 1. Previous implementation

Commit `8458ef9` changed `canonical_factual_projection.py`,
`deployment_status.py`, `executive_workspace.py`, the current-change record, its
implementation report, and two test modules. It added
`EnterpriseFactualSynthesis` and `enterprise_factual_synthesis()` to the
Canonical Factual Projection (CFP) module. The builder accepts a
`SemanticEnterprise`, reads the Profile, Operating Model, and Strategy factual
dimensions, and returns status, verbatim statement composition, input dimension
and fact IDs, Evidence, confidence, Unknowns, Contradictions, and source and
candidate identities.

Runtime synthesis therefore **existed**, executed for BT, and generated a
statement. Its previous consumers were two direct calls in
`executive_workspace.py`: the Enterprise dossier and the Advanced Inspection
trace. The returned derivative was not a member of `CanonicalFactualProjection`.
Consequently no canonical factual output or Enterprise executive view model
received it; two downstream consumers independently invoked the builder.

The previous tests appeared to pass because they imported the fixture afresh,
called the synthesis helper directly, then asserted that the first Profile
proposition occurred somewhere in a dossier assembled by a second synthesis
call. They did not assert a canonical synthesis handoff, equality of the
canonical, diagnostic, and rendered values, or preservation of the literal
source-field absence. This proved helper output and incidental text overlap,
not one governed value traversing the real consumer chain.

## 2. Pre-correction BT trace and first divergence

| Boundary | Actual value before correction |
|---|---|
| Source Enterprise | `ENT-BT`; literal `organisation_description` absent; `description`, `operating_model`, and `strategy` present |
| Candidate Enterprise | `bpi-cand-97ad22c789b93f8dca7aa06b`; candidate; same qualifying values retained |
| Synthesis input | Profile, Operating Model, Strategy; Evidence `EV-BT-FY26`, `EV-BT-Q1FY27`, `EV-BT-AI26`, `EV-BT-KYNDRYL`, `EV-BT-DYNATRACE`, `EV-BT-CMA-NEXFIBRE-RESPONSE26` |
| Eligibility | YES: Profile plus two contextual dimensions were present |
| Synthesis execution | YES; `GENERATED` |
| Canonical factual output | Organisation summary existed as an atomic section, but the governed multi-fact synthesis derivative was absent |
| Executive view model | No synthesis member; the dossier called the builder beside the view model |
| Organisation Overview | Could receive a separately regenerated value, but not through the canonical handoff |
| Advanced Inspection | Called the builder independently and did not reconcile literal source Profile, executive consumption, or rendering |

The demonstrated **first divergence** was the boundary from
`enterprise_factual_synthesis()` to `CanonicalFactualProjection`: the builder
returned a valid derivative but the canonical output did not carry it. The
canonical owner therefore could not prove that every consumer observed the same
runtime value. The dossier and diagnostics side calls masked this missing
handoff under the freshly imported test fixture.

## 3. Exact BT synthesis

The qualifying supplied facts are:

1. Profile (`description`): “BT Group is a UK-headquartered
   telecommunications group spanning consumer broadband/mobile, business
   connectivity, international services and Openreach fixed-access
   infrastructure.”
2. Operating Model (`operating_model`): “Business Model: Integrated operator
   with Consumer, Business, International and Openreach CFUs”.
3. Strategy (`strategy`): “Current Challenges: Revenue pressure; Debt/capex
   intensity; Regulated pricing constraints; Enterprise complexity;
   PSTN/copper migration execution”.

The deterministic output is:

> BT Group is a UK-headquartered telecommunications group spanning consumer broadband/mobile, business connectivity, international services and Openreach fixed-access infrastructure. Business Model: Integrated operator with Consumer, Business, International and Openreach CFUs. Current Challenges: Revenue pressure; Debt/capex intensity; Regulated pricing constraints; Enterprise complexity; PSTN/copper migration execution.

The composition introduces no proposition: punctuation is normalised and each
clause is a supplied candidate value. Fact IDs are `FACT-ENT-BT-PROFILE`,
`FACT-ENT-BT-OPERATING-MODEL`, and `FACT-ENT-BT-STRATEGY`. Unknowns `UN-002`,
`UN-004`, `UN-005`, `UN-011` and Contradictions `CR-003`, `CR-004` remain on the
derivative and are not resolved by its prose.

## 4. Canonical correction

`CanonicalFactualProjection` now carries `enterprise_synthesis` for Enterprise
projections. `factual_projection_for_enterprise()` invokes the existing builder
once, and the dossier reads that governed derivative from its factual view
model. Advanced Inspection obtains the same canonical projection and separately
reports Source profile field, Qualifying factual inputs, Governed synthesis,
Executive consumption, Rendered state, and final Status.

No new Observation, factual, synthesis, Enterprise-profile, or presentation
model was introduced. This is a read/projection correction over retained
candidate state, so a fresh import is not required.

The literal `organisation_description` source field remains absent. The
qualifying `description` proposition and other factual dimensions remain
present, which permits governed synthesis without rewriting source truth.
Ownership/form, principal activities, industry role, and other independently
required attributes continue to be reported as gaps where their dedicated
fields are absent. Industry/domain remains `Not established`.

Assessment remains `Assessment not yet performed`; review remains imported
candidate; promotion remains `Not promoted`; recommendation remains `Not
eligible`. Synthesis neither persists candidate data nor invokes any of those
owners.

## 5. Rendered acceptance and all-six regression

The same imported `SemanticTwin` and the production `_dossier()` route were
used for all six pages. BT Organisation Overview renders the exact canonical
synthesis and does not render “Organisation description not supplied.” Advanced
Inspection renders the same statement and its evidence lineage.

| Enterprise | Qualifying facts | Synthesis | Organisation Overview | Evidence lineage |
|---|---|---|---|---|
| BT Group | YES | GENERATED | PRESENT | PASS |
| CityFibre | YES | GENERATED | PRESENT | PASS |
| Openreach | YES | GENERATED | PRESENT | PASS |
| TalkTalk | YES | GENERATED | PRESENT | PASS |
| Virgin Media O2 | YES | GENERATED | PRESENT | PASS |
| VodafoneThree | YES | GENERATED | PRESENT | PASS |

The governed fixture checksum is
`bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.
Acceptance retains 308 Relationships, 13 Programmes, and 17 Opportunities; all
six Programme and Opportunity association sets reconcile exactly. Functional
acceptance PASS with incomplete deployment metadata remains “Ready for
functional test — deployment metadata incomplete”, “Should I test now? YES”,
and “Fresh import required: NO”.
