# WP1-005 — Decision-oriented Twin import

## Current-state assessment

Flora already owns the complete governed intake path: authenticated upload, contract
detection, validation, immutable package receipt, candidate staging, review-plan
generation, reconciliation, rationale-gated approval, atomic promotion, history and
the Enterprise Canvas handoff. The runtime already exposes package identity and
maturity metadata, candidate class and disposition, dry-run effects, reference
resolution, Unknowns, Contradictions, lineage classifications, and expected mutation
counts. No package or canonical data contract is required for this presentation work.

Before WP1-005, inspection displayed those values primarily through package metadata,
candidate staging terminology, and the execution trace. Review grouped records by
technical disposition rather than the commercial subject. Promotion exposed creates,
updates and conflicts, but not a complete plain-language account of exclusions and
unresolved uncertainty.

The staged payload does not consistently provide a commercial-relevance narrative,
materiality, industry/sub-sector, buying theme, organisation name, or regulatory-event
field for every record. These remain owned by the source Researcher package and the
Enterprise Intelligence canonical models. Flora therefore displays “not available in
staged data” rather than inventing facts or adding fields.

## UX design and implementation

The inspection hierarchy is now:

1. executive import summary and recommended next action;
2. commercially named candidate categories;
3. a clearly labelled derived commercial-impact view;
4. risk and uncertainty, separating blockers from expected lineage exclusions;
5. the existing proposed-change action;
6. closed-by-default technical diagnostics with the original inspection, validation,
   deployment, execution-trace, package, workbook, reference and staging detail.

Review uses business-category summaries with create, update, duplicate/no-change,
quarantine, rejection and manual-review counts. Individual rows retain identifiers,
decision disposition and proposed effects while moving the full payload behind
progressive disclosure. The promotion page states the affected Twin, creates, updates,
exclusions, quarantines, rejections, unresolved Unknowns and Contradictions, and the
expected mutation count before retaining the existing mandatory rationale control.

## Recommendation translation

These labels are read-model translations of existing state; they are not lifecycle
states and do not constitute a second readiness engine.

* **Ready to Review** — validation has no blocking errors, candidate extraction and
  staging produced records, the expected type matches, and canonical mutation has not
  occurred.
* **Review Required** — staging produced no reviewable candidates or existing warning
  conditions require examination.
* **Not Safe to Continue** — existing blocking validation errors, an expected-type
  mismatch, or rejected staged records prevent safe continuation.
* **Ready for Promotion** is only appropriate after the existing review and
  reconciliation services report readiness and the authorised owner reaches the
  rationale-gated promotion step.
* **Promotion Blocked** reflects an existing invariant such as failed validation,
  unresolved reconciliation, stale review, authorisation failure, missing confirmations
  or empty rationale.

Quarantines, Unknowns and Contradictions remain visible as commercial uncertainty or
conditions. Workspace, execution, release-assurance and presentation artefacts that the
contract intentionally retains or excludes are described as expected non-blocking
governance behaviour.

## TMS-001 rendered acceptance evidence

The repository TMS-001 lifecycle fixture asserts the executive summary, Industry Twin
detection, successful validation, 315 resolved references, zero unresolved references,
315 staged candidates, 14 visible Contradictions, 40 expected lineage exclusions,
closed technical diagnostics, no pre-promotion canonical files, rationale enforcement,
301 canonical mutations after approval, and the Explore handoff.

## Pull-request recommendation

**Merge.** The change is confined to Flora read-model rendering and acceptance tests.
It preserves package contracts, lifecycle services, review decisions, reconciliation,
canonical constructors, authorisation and explicit-rationale promotion controls.
