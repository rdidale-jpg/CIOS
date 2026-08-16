# TEL-001 Material Pressure Governance Assessment

**Assessment date:** 2026-08-16  
**Decision:** ARCHITECTURAL GOVERNANCE INSUFFICIENT  
**Runtime change authorised:** No

**Qualification contract status:** PROPOSED — awaiting governance

## Authority reviewed

The Chief Architect pack identifies `CURRENT-PROGRAMME-STATE` (2026-07-21) as
the programme-state baseline and WP-011 as the runtime baseline. ADR-014 and
ADR-024 contain accepted decisions for evidence-bounded interpretation and the
hybrid reasoning runtime. EIF-001 is Review; EI-001, EI-002, EI-003, EI-004
and EI-012 are Draft; and FEIR-001 and EIRP-001 are Proposed runtime
specifications. Those non-accepted documents inform this assessment but cannot
silently create runtime doctrine.

The governed Knowledge Pack copy of EI-001 also declares its status as
**Draft**. Inclusion in the pack makes the document available for architectural
assessment; it does not promote it to Accepted authority. References elsewhere
to EI-001 as a canonical model owner describe the intended ownership boundary,
not an accepted qualification contract.

The accepted ADRs require bounded Enterprise evidence, applicability, lineage,
validation, Unknown and Contradiction preservation, and safe failure. They
permit pressure *assessment* as a transient interpretation. They do not define
the acceptance contract by which an imported financial, strategy, challenge,
risk, programme or market fact becomes a qualified **Material Pressure**.

## Proven root cause

The TEL-001 canonical factual projection reads Material Pressures only from the
explicit Enterprise identity field `pressures`. Pressure-like text held in
Financial Position, Strategy, Transformation, Programme and Opportunity fields
is therefore visible elsewhere but is not a Material Pressure. The executive
quality diagnostic tests only whether the projected `pressures` dimension is
present, so an empty projection is described as truthful absence without first
testing whether governed candidate signals were under-used.

This is a **reasoning gap**, **runtime gap**, **presentation gap**, and
**architectural gap**. It is not established as a source gap: the package
contains candidate pressure-like intelligence. Nor is it safely classifiable as
only an extraction gap, because promoting those other facts requires the missing
qualification semantics.

The canonical owners of the currently displayed pressure-like intelligence are
their existing factual dimensions and business objects: Financial Position,
Strategy, Transformation, Programme, Opportunity, and their linked Evidence.
They are not implicitly owned by Material Pressures.

## Stop condition

No keyword, alias, regex, telecom-domain inference, or dossier-copying rule may
bridge this discontinuity. Implementing one would allow plausible language to
become a new governed conclusion without accepted identity, materiality,
applicability, consequence, singularity, or lifecycle rules.

The precise unresolved architectural question is:

> Which accepted owner and deterministic acceptance contract authorises Flora
> to transform an Enterprise-applicable governed Observation (or other
> canonical factual object) into a distinct Material Pressure, and what are the
> mandatory identity/singularity, materiality, consequence, commercial
> significance, uncertainty, contradiction, lifecycle, and evidence-lineage
> fields and rejection rules for that transformation?

## Authority reconciliation and required governance action

The authority hierarchy produces the following unambiguous result:

| Question | Finding |
|---|---|
| Proposed architecture | The six-gate contract in the annex below is a candidate architecture only. |
| Accepted architectural authority | ADR-002 accepts the Enterprise Model as durable memory; ADR-014 and ADR-024 constrain evidence-bounded interpretation and hybrid reasoning. None accepts a Material Pressure identity or qualification contract. |
| Runtime implementation readiness | Not ready. No runtime implementation, projection change or TEL-001 change is authorised by this assessment. |

There is therefore no existing Accepted owner that can genuinely be clarified
without enlarging its decision. ADR-002 establishes *where* durable Enterprise
Model state belongs, but does not decide *what qualifies* as a Material
Pressure. ADR-014 and ADR-024 provide reasoning constraints, not the missing
domain-object acceptance semantics. Treating an amendment to any of them as a
mere clarification would conceal a new architectural decision.

The smallest honest governance action is **B: a narrowly scoped ADR** that
accepts (or rejects/amends) the Material Pressure qualification contract,
establishes Material Pressure as durable Enterprise Model state, and names
EI-001 as the intended durable-model owner once EI-001 is reconciled with that
Accepted decision. Until that ADR is accepted, ADR-002 remains the Accepted
authority only for the general durable-memory boundary; **there is no Accepted
authority for Material Pressure qualification**, and EI-001 is only the
candidate durable-model owner.

This assessment and its annex do not themselves perform that governance action.
They may be merged as a record of a proposed architecture and stop condition,
but may not be cited as normative runtime doctrine.

## Proposed Material Pressure qualification contract (non-normative annex)

**Classification:** PROPOSED architecture awaiting governance. This annex is
not Accepted, does not normatively authorise qualification, and is not runtime
implementation authority.

A candidate may become a qualified Material Pressure only when it passes all
six gates. Failure or unresolved evidence at any gate rejects qualification;
the source object remains in its existing canonical factual dimension and the
unresolved issue may be preserved as an Unknown or Contradiction.

1. **Governed candidate and lineage.** The candidate is a governed Observation
   or canonical factual object with inspectable Evidence lineage, source type,
   observation time, confidence and freshness. Narrative resemblance alone is
   not a candidate.
2. **Enterprise applicability.** The candidate identifies the affected
   Enterprise and monitored scope. Industry or market context without evidenced
   Enterprise applicability does not pass.
3. **Pressure identity and singularity.** The candidate expresses one distinct
   constraint, demand or forcing condition with a stable identity. Duplicate,
   compound or merely restated facts are reconciled or rejected rather than
   emitted as additional pressures.
4. **Materiality.** Evidence supports a material effect on an enterprise
   objective, outcome, economics, operation, obligation, risk or change agenda.
   Importance inferred only from keywords or domain familiarity does not pass.
5. **Consequence and commercial significance.** The pressure has an explicit,
   evidence-bounded consequence and explains why it matters commercially to
   the Enterprise. This gate does not manufacture an Opportunity, procurement
   claim or provider fit.
6. **Assurance and lifecycle.** Confidence, uncertainty, Contradictions,
   effective/observed dates, freshness/decay and lifecycle state are explicit;
   supporting and counter-evidence are preserved. The pressure can be updated,
   weakened, contradicted, retired or re-qualified without erasing history.

The prospective ADR must define the required fields and deterministic rejection
rules for these gates before implementation. Acceptance of that ADR would make
the contract architectural authority; a subsequent implementation change would
still need to demonstrate conformance and runtime tests. Architecture
acceptance and runtime implementation readiness are separate gates.

## Merge decision record

- **EI-001 status:** Draft.
- **Accepted authority for Material Pressure qualification:** None. ADR-002,
  ADR-014 and ADR-024 are Accepted constraints/precedent, not the qualification
  owner.
- **Governance action:** B — narrowly scoped ADR.
- **Canonical durable-model owner:** ADR-002 owns the Accepted general durable
  Enterprise Model boundary; EI-001 is the proposed future detailed owner once
  reconciled by the Accepted ADR.
- **Qualification contract status:** PROPOSED.
- **Runtime authorised after this PR:** NO.
- **Architecture ready for subsequent runtime implementation:** NO; first
  accept the narrowly scoped ADR, then reconcile EI-001.
- **Decision:** SAFE TO MERGE, because this document records a proposal and a
  stop condition and does not rely on Draft EI-001 to create normative doctrine.

Until that question is resolved by accepted architecture, the correct action is
to preserve the existing empty projection, report the under-utilisation risk as
a governance failure rather than truthful absence, and make no runtime or
TEL-001 fixture change. The requested six-enterprise pressure qualification and
functional acceptance therefore cannot truthfully pass.

## Fixture integrity

The TEL-001 ZIP was not modified. Its SHA-256 at assessment time was
`bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.
