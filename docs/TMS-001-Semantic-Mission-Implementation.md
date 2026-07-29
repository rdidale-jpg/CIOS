# TMS-001 semantic and Commercial Mission implementation

## Authorities consulted

This increment applies FP-012's evidence-bounded Enterprise Intelligence, FP-013's progressive Executive Inspection, FP-014's declared mission/truth boundary, WP2-003's deterministic composition contract, ADR-014 and EIRP-001's existing reasoning stages, and EI-001/EI-002 identity and relationship rules. It retains the accepted package import, candidate review and explicit promotion boundary described by WP1-005/WP1-006; canonical in-package placement does not mean governed acceptance.

## Root cause and correction

The TMS adapter previously staged only HFT upgrade inventories. Its generic `objects` collection forced all 56 inventory entries to `entity`, so capabilities, offers and other concepts became enterprise-like identities. The semantic workspace then inferred dossiers from names and subjects. It also did not stage the root evidence register or executive-intelligence object, so canonical references could not resolve.

The adapter now loads each explicitly typed root artefact before enrichment and preserves its source path, ID, candidate lineage and type. Upgrade objects retain their declared `object_type`; they cannot override the canonical enterprise collection. Enterprise dossiers are seeded only by canonical `enterprise_twin` objects (or an explicit generic enterprise identifier for non-TMS packages), then resolve typed reference arrays through an ID index. Broken references remain visible.

## Commercial Mission and composition

The existing authenticated-user JSON profile owner is reused. The Sales Director / Sopra Steria mission is persisted as human-supplied operational context and now includes the requested interests and optional named-account/campaign fields. The inspect/edit route writes atomically to that same profile store. No Sopra Steria offer portfolio was present, so offer alignment remains explicitly incomplete; no offer is invented.

Candidate executive reasoning from `11_executive_intelligence.json` is split into traceable presentation conclusions while retaining common evidence, confidence, freshness, unknowns, source and candidate status. The deterministic workspace uses supplied `why_now` content and exposes a categorical evidence-sufficiency/permitted-use assessment rather than a score.

## Reconciliation and validation

Before correction, the workspace derived 56 mixed enterprise identities from the HFT object inventory. After correction, it reports 14 canonical priority enterprises, separately from 10 canonical Market Participants, 16 upgrade capabilities/offers and nine canonical Opportunity Hypotheses. The validation panel also reports evidence, unknowns, contradictions, evidence coverage, unsupported claims, unused evidence, missing dates and unresolved references.

Canonical root records form a read-only semantic projection alongside the preserved 315 staged upgrade candidates; they do not expand promotion scope. Nothing is silently promoted: staged candidates still pass through existing quarantine, review, reconciliation and explicit promotion services.

## Remaining gaps

There is no governed Sopra Steria offer portfolio in the fixture or current stores. Offer alignment therefore remains incomplete until a human supplies operational offer context or the existing import/review workflow accepts governed corporate knowledge. Source-quality detail is inspected through linked evidence records rather than collapsed into a new score. Some upgrade-only references intentionally remain unresolved when their endpoint is not present in a canonical root collection; these are reported rather than inferred.

## Twin import recovery programme note (2026-07-28)

### Regression timeline and runtime authority

Diff inspection, rather than commit subjects alone, established this timeline:

- `ba98847` is the last known-good pilot import baseline before identity cut-over: the existing browser session propagated through package receipt and inspection, while import still staged candidates without canonical mutation.
- `e5f3f0f` is the first regressing change. Its diff changed trusted proxy identity from enabled-by-default to opt-in and made upload authority depend on a newly signed pilot session, configured owner, workspace, and role. A deployed browser without that complete state therefore reached the form but failed before `BlueprintPackageRegistry.receive`.
- `569c6d4`, `6a03f82`, `fb54dae`, `d766bd7`, `5be3060`, `f0cf19e`, `f833e4c`, and `2cf9cb5` successively patched session propagation, diagnostics, visibility, route HTML, form rendering, and auto-sign-in symptoms. `65dcf40` finally added a second route-scoped bypass flag. None removed the competing access modes, so configuration could still select the broken path.
- The deployed entry point declared by `render.yaml` is `python -m cios.applications.flora.web.app`. That module directly imports `digital_twins_landing_page`, `import_blueprint_entry_page`, and `upload_and_validate_blueprint` from repository modules. `GET /digital-twins` now renders the action owned by `digital_twins.py` without route HTML injection; `GET /blueprint-import` calls the view; multipart `POST /blueprint-import/upload` calls the same upload service; successful POST redirects to `/blueprint-import/<run>`, whose GET calls `executive_workspace_page`. Candidate creation remains owned by `BlueprintPackageValidator.validate_and_stage` and its current semantic adapters. Python resolution checks in the regression suite verify these repository paths rather than an installed shadow copy.

### Recovery decision and lesson

The original receive/inspect slice was retained and adapted to the newer typed
semantic candidate projection. The root cause was not ZIP ingestion: account,
workspace, and role prerequisites intercepted the request before receipt. Local
service tests called handlers with synthetic authorised headers, while UI tests
proved only that controls rendered; neither exercised an anonymous multipart
request through the production HTTP handler. Repeated link, session, and bypass
patches treated those symptoms and multiplied configuration states.

`FLORA_ENVIRONMENT=pilot` is now the sole import pilot mode. It records an
explicit pilot operator and import scope, marks identity/workspace capability
checks as not applicable (never passed), and preserves receipt, ZIP traversal,
decompression, contract, schema, evidence, duplicate, validation, diagnostic,
and candidate controls. The deployed-equivalent HTTP test follows the visible
link, submits multipart bytes through the production handler, proves inspection
and candidate persistence, opens the current Executive Intelligence Workspace,
and proves promotion is still denied. Full human identity, durable workspace
membership, and enterprise role resolution remain deferred. They may be
reintroduced only as the normal secure mode after a real identity provider and
workspace membership authority exist and the same end-to-end route test passes
without synthetic browser headers or route-specific fallbacks.
