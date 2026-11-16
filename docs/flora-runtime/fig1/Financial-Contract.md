# Financial contract proposal and EAR-1 reconciliation

**Proposed compatible changes under existing owners; no schema/runtime/canonical mutation in FIG-1.** EI001 identifies canonical financial ownership, EI012 Observation lifecycle, ADR010 acquisition and ADR011 the analytical/canonical distinction. Draft owning papers are not accepted wholesale by this proposal.

## Retain meaning once; derive views reproducibly

| Information | Existing owner/storage reused | Proposed treatment |
|---|---|---|
| Original reported measurement | Financial candidate/run and permitted source provenance; existing accepted financial fact path when chosen | Typed amount/scale/unit/currency, original display/precision/sign, exact reported subject/definition/basis/dates/locator/version. Durable permitted working data can exist without claiming accepted Enterprise knowledge |
| Calculation | Existing Financial/Statement analytical result | Formula/version,input references/revisions and compatibility basis; reproducible output/cache rather than new Observation for every value/chart point |
| Estimate | Existing analytical result | Visible method, assumptions, uncertainty/rounding and sensitivity/limits; no upgrade to reported/accepted fact through arithmetic |
| Working assumption/scenario | Existing financial-run analytical metadata, versioned with output | Explicit owner/version/value/scope, not source-reported or a real bank forecast; no new scenario database |
| Interpretation/hypothesis | Existing six-type presentation/reasoning owner | Retain reasoning,counter-evidence,falsifier/dependencies; no automatic financial Observation or canonical pain/opportunity |
| Accepted reusable fact | Existing Evidence→Observation→Enterprise Model | Explicit chosen canonical acceptance; atomic lineage, typed persistence, correct dates, reload verification and existing mutation authority |

This is not a proposal to discard all original measurements after rendering. Preserve permitted original values and source revisions in the existing Financial owner so analysis can be reproduced and refreshed. Separately decide which material, reusable facts should become durable accepted Enterprise knowledge. A view is not the source of truth or an alternative Evidence registry.

Avoid false distinctions: converting a reported amount between millions and base units is a representation of that same measurement, not automatically another analytical claim, Evidence approval or Observation. A newly derived ratio/scenario is different and needs its own method/assumption provenance, without automatically becoming canonical knowledge.

## Minimum measurement meaning

Reuse `NumericFactValue` and existing source/financial fields. The candidate contract preserves reported subject identity from the original and authorised run context; it does not invent a canonical Enterprise ID to satisfy a display. Actual canonical target/tenant mapping remains required for a private Twin write. Remove the BT fallback only in a separately authorised implementation with regression/identity tests.

Every material measurement needs:

- Original source and located row/column/tag/span with honest verification/capture extent, publisher/issuer/version/publication/retrieval dates, applicable source-use reference and semantic type.
- Reported numeric value and sign convention, explicit currency/scale/unit, display precision/rounding and named metric definition. Amounts need not be forced through a small canonical metric whitelist merely to be shown as an accurately labelled analytical candidate.
- Legal/reporting subject, Group/subsidiary/segment/geography perimeter, consolidation scope, statutory/underlying/adjusted/APM or other named basis, actual/target/guidance/forecast state.
- **Temporal kind:** `instant(as_at)` for stocks, `duration(start,end)` for flows; ratios also retain denominator/average/point-in-time definition. Publication/retrieval dates are different. Fiscal calendars must come from the issuer/context, not an April–March default.
- Source reliability/lifecycle, contradiction/supersession, uncertainty and actual canonical status as separate dimensions.

The existing canonical catalogue remains valuable for standardised matching, comparisons and durable metric IDs. Candidate labels can be meaningful before that mapping exists, but cannot be silently equated to another metric or used in unsupported arithmetic. Reuse one Financial-owner definition catalogue across adapters/normalisation/projection; do not create another financial engine.

## Comparison and derivation rules

| Operation | Required meaning | Example / refusal |
|---|---|---|
| Same-period additive bridge | Same subject/perimeter,currency,scale,period,basis and explicit signed components | HSBC UK reported USD revenue/ECL/expenses/associates→PBT |
| Statutory/APM reconciliation | Source-disclosed bridge/definitions, not an assumed equality of unlike bases | Nationwide underlying+income adjustment−cost adjustment−member rewards→statutory PBT |
| Stock-date trend | Same definition/perimeter and two explicit dates; acquisition/transfer/FX adjustments separately stated | Published-stock delta is not automatically organic flow or cash flow |
| Ratio | Defined numerator/denominator and compatible temporal/perimeter/basis; source method or explicit analytical method | LCR average, ROCE and CET1 have different denominators; no generic banking quality ranking |
| Cross-bank comparison | Matched period/currency/perimeter/definition/business model, or explicit justified reconciliation | No direct HSBC USD bank versus NatWest GBP Group league table or Nationwide retail deposits versus all customer deposits |
| Estimate/scenario | Explicit assumption inputs, method/version, uncertainty and limitations | Synthetic cost scenario is not forecast, net benefit, supplier spend or customer demand |

Pure arithmetic should not require a canonical promotion transaction. It must still pass financial compatibility. A calculation from estimated/assumed inputs retains that weaker basis. The current `difference` preserves dependency types but calls the output Calculated; a future adapter must present it as Estimated or explicitly assumption-dependent, never as Reported truth. The fixed proof demonstrates this limitation and the existing Estimated/Working assumption classes without changing runtime semantics.

## Smallest compatible EAR-1 corrections

| Finding | Proposed correction in existing owner | Guardrail |
|---|---|---|
| Missing deposit definitions/aliases | Shared definitions for total/ex-central/customer/retail deposits and relevant banking measures; candidate display need not wait for canonical mapping | Never map all deposit labels to one metric; retain source definition and proper Group/legal-bank scope |
| Stock date misnormalised asFY26 flow | Financial temporal-kind/as-at contract; require correct explicit dates/issuer fiscal calendar for new values | Preserve old IDs/history; version new temporal identity and aliases; do not reinterpret historicalFY records silently |
| Dynamic numeric field lost on Observation serialization | Persist a versioned validated Financial-owner payload through an existing owned serialized field; consume that payload on reload | The existing `human_provenance` dictionary can retain structured data despite its historical name. Namespace/document machine financial provenance; do not relabel source facts as human-supplied knowledge or attach ad-hoc Python attributes |
| Prose fallback | Explicit typed Financial-owner projection rather than financial regex re-extraction, retaining original statement/source lineage | Current metadata persistence is not implemented numeric projection; require exact value/unit/basis/date after actual repository reload before success |
| Incomplete lifecycle checks | Reconcile current source/measurement/Observation/use states through owning semantics and dependencies | Accepted+stale/boolean withdrawn/retracted cases currently pass the mapping helper; preserve history and stop dependent use, do not simply call the helper complete |

The payload route is a proposed small compatible correction, not a new model or a universal use of an unvalidated dictionary. A clean optional typed field could be chosen by the Chief Architect if preferable; the first implementation must preserve old schema/readers and explicit data provenance. No current Model success is inferred from the metadata round-trip fixture.

## Canonical boundary and future compatibility

Do not remove Observations from accepted financial memory as part of Option B. Existing canonical facts remain Evidence-backed and accepted through their current owners. Option C's broader removal/reinterpretation of financial Observation copying would require explicit accepted-doctrine reconciliation and a separately approved migration.

Existing canonical IDs, source identities, Evidence records, review decisions, approved failure/skip baselines and original research must remain unchanged. New fields/temporal identities need versioned readers and migration previews; obsolete prose may remain historical until safely rebuilt through governed accepted lineage. No reinterpretation or blanket reacceptance of existing records.
