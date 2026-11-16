# Existing-owner implementation and versioned contract

Accepted ADR-011 permits useful attributed candidate analysis before canonical verification; ADR-012 separates analytical baseline use from object-specific canonical promotion. Accepted FIG-1 OptionB authorises F1's bounded implementation, not new source permission or canonical writes. No accepted architecture files are changed.

## Path

`official BoE Database → existing banking Source snapshot/provenance → Financial Measurement v1 → existing Financial runs repository → typed reload → exact input-revision compatibility → existing Statement/difference + fixed percentage formula → authorised existing Financial result page`.

`financial_intelligence.candidate_analytics` is an adapter inside the Financial owner. Its Pydantic DTOs describe working data, not canonical objects. It uses `NumericFactValue` and normalisation's existing scale factors. Fingerprinting reuses the existing `enterprise_intelligence.models.stable_hash` utility, without importing visual agenda/rendering code into the Financial contract.

Storage is `document_review._run_path` / `load_run`, under the existing `ai_financial_reports/runs`. `create_run` uses the existing verified `package.upload` service transaction, active workspace, exact resource ACL and atomic JSON persistence. It rechecks source and authority after writing; the existing protected journal rolls back failed writes. Identical workspace/resource/source/recipe content yields an idempotent immutable run ID. Changed source or meaning needs another revision; no historical rewrite.

## Measurement meaning

| Field group | v1 contract |
|---|---|
| Number | Existing typed Decimal amount, currency, currency unit and canonical scale. Signed value, original display, declared decimal precision and rounding survive storage/reload; no amount hidden in prose |
| Time | `instant(as_at)` requires exactly one explicit date. `duration(start,end,fiscal_year_end)` requires explicit issuer calendar and boundaries. No April–March guess; publication/retrieval are separate |
| Subject | Reported identity/name and perimeter, source definition, metric, accounting basis and actual/target/guidance/forecast remain distinct |
| Provenance | Original publisher URL/title, source/record IDs and revisions, located row, nullable actual publication day, timezone-aware retrieval and use reference |
| Semantics | Reported, Estimated or Working assumption input. Assumption-dependent input needs owner/version/caveats. Calculations never upgrade it to Reported |

The pilot's research-local aggregate identity is **not** a canonical Enterprise or Lloyds. `BK-IND-002` is the existing Banking context/resource used for the workspace permission intersection. It does not become the reported statistical subject. Access checks do not create or modify that resource's real production ACL.

## Arithmetic and comparison

Only `difference` and `percent_change`, version1; no expression evaluator, generic modelling engine, FX, annualisation or unsupported peer league table. Recipes persist exact measurement IDs/revisions and comparison mode. No precomputed result is trusted on read.

Same subject/name/perimeter/metric/definition/basis/state and currency/unit/scale are required. Stock comparisons require ordered explicit dates. Same-period duration comparisons require identical semantic dates/fiscal calendar; display-label wording is not a financial incompatibility. Conflicting same-period Reported values are rejected. Duplicate IDs, missing revisions, reversed dates, unsupported units and non-positive percentage denominators fail closed. Different financial metrics/APM reconciliation bridges need separately defined future adapters rather than an arbitrary subtraction.

After compatibility validation, the existing Statement/difference performs subtraction in a comparison context retaining both original stock dates. The bounded percentage operation divides by the positive opening amount. Local Decimal precision is34digits; display rounding is explicit. Actual/target state and estimated/assumed dependency semantics survive derivation. No target becomes an actual through matching periods or calculation.

## Current-use and privacy

The source package is confined to the existing banking snapshot boundary and pinned to its exact source/claim/use content. Existing `source_import.official_url` and `model.primary_text` validate publisher, genuine excerpt digest, original retrieval extent and provenance. Unknown selections, changed versions, denied rights, withdrawal, contradictions, supersession, owner-only data or expired review return no dependent projection.

The external `document_review.read_run` always replaces analytical output with a freshly checked projection and strips raw candidate history. A missing payload cannot revive a forged persisted `analysis` field. Existing scoped pages consume that current read; old caches/serialized result data are not an entitlement. `read_analysis` and `render_run` intersect the same actual verified capability/workspace/resource/ACL. No public download/cache is introduced.

Sharing a repository exposed a legacy integration hazard: global latest-run BT summaries must not display another workspace's analytical candidate. `_legacy_run_paths` excludes F1 IDs/workflows/payloads from all four old scans, while generic `_outcome_summary` never renders analytical data. Canonical review/apply explicitly reject this workflow even if its payload was removed. The valid result route has a completed state and direct result link; the legacy progress service dispatches it to the current scoped view.

Old records, auto-acceptance rules, Evidence/Observation/Enterprise Model serialization and projection are unchanged. EAR-1's optional canonical numeric projection corrections remain separate. No source receipt, canonical ID, approval or successful promotion is fabricated. Adapters for eligible Technology/Aviation sources can reuse these same typed fields/storage/compatibility operations; F1 does not pretend those source admissions or full financial bridges exist.
