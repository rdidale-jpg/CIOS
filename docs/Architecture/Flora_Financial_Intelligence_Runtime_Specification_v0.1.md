# Flora Financial Intelligence Runtime Specification v0.1

**Status:** Working Draft  
**Owner:** Rob / CIOS  
**Date:** 2026-07-05  
**Architecture owners:** EI-001, EI-012 and ADR-010  
**Runtime:** Flora  
**Maturity:** Pilot

## Purpose

Define how Flora converts governed financial sources into accurate, page-grounded Observations and Commercial Digital Twin state. This document is a runtime specification, not a replacement for EI-001, EI-012 or ADR-010.

## User Outcome

Primary strategic-user journey:

```text
Open enterprise
→ Refresh Financial Intelligence
→ Flora obtains governed sources automatically
→ Flora validates and understands the evidence
→ valid facts update the Commercial Digital Twin
→ Flora explains what changed and what requires attention
```

File upload is an administrative fallback, not the primary journey. Provider settings, API keys and technical request details are not part of the strategic-user experience.

## Architecture Boundaries

- **Source:** governed origin such as filing, API, annual report, XBRL record or permissible human source.
- **Evidence:** attributable record proving what was reported.
- **Provider candidate fact:** untrusted structured provider output awaiting validation.
- **Canonical financial fact:** domain-valid fact satisfying EI-001's Financial Metric Data Contract.
- **Observation:** EI-012 memory atom created or strengthened from accepted Evidence and canonical fact.
- **Enterprise Model:** EI-001 durable Commercial Digital Twin state.
- **Signal and inference:** reasoning over Observations and model state, not over provider output directly.
- **Product view:** report, page, workspace or outcome surface over canonical memory.

Runtime MUST NOT reason from provider output directly into model state.

## Source Acquisition Hierarchy

ADR-010 controls the acquisition hierarchy:

1. structured filing, API, authoritative data or XBRL route;
2. source-specific deterministic adapter route;
3. local document structure, text and table extraction route;
4. bounded AI interpretation route;
5. governed human exception route.

Use the least ambiguous and least expensive adequate route.

## Source Registry

Minimum governed-source metadata:

- enterprise;
- source family;
- authority tier;
- source URL or identifier;
- reporting period;
- retrieval time;
- content hash;
- content type;
- source status;
- expected refresh cadence.

## Document Adapter

The document adapter handles PDF retrieval, parser selection, parser-quality gates, canonical page representation, original page numbering, text/table/visual availability and fallback when embedded text is corrupt. The architecture does not mandate one permanent library. Pilot implementation choices may be recorded as implementation notes only.

## Section Selection

Section selection uses deterministic financial relevance, table-of-contents cues, heading and term scoring, bounded visual-navigation fallback and preservation of original page numbers. Whole-document submission is avoided where bounded sections are sufficient because bounded packets improve cost control, explainability and validation.

## Packet Construction

When AI interpretation is used, real PDF pages or images MUST be physically supplied to the model. Each packet records packet-to-original-page mapping, bounded size, cost/token preflight, packet identity, packet hash and validation before submission.

## Provider Boundary

A provider adapter owns provider request/response handling, provider DTOs, structured-output compatibility, configurable model choice, provider lineage, response completeness checks, refusal handling and error handling. Candidate output is untrusted data. OpenAI-specific or other provider-specific DTOs are not canonical CIOS objects.

## Financial Candidate Lifecycle

Every candidate must end with one auditable final disposition:

- `extracted`;
- `structurally_valid`;
- `canonicalised`;
- `accepted`;
- `quarantined`;
- `rejected`;
- `deduplicated`;
- `merged_as_corroborating_evidence`;
- `unsupported`;
- `superseded`.

## Financial Normalisation

EI-001's Financial Metric Data Contract controls normalisation. Scale, currency, period, scope, financial measurement state, accounting basis and page or record lineage are mandatory for accepted canonical financial facts. Scale ambiguity is a validation failure unless resolved by governed review.

## Deduplication and Corroboration

Equivalent metrics create one Observation, retain multiple Evidence records, strengthen confidence where appropriate, preserve rounding and precision differences and remain separate when scope, accounting basis, period or measurement state differs.

## Observation Creation

Accepted facts create or strengthen atomic EI-012 Observations. They use a valid EI-012 lifecycle state, preserve Evidence lineage, identify affected Enterprise Model attributes and never contain interpretation or Recommendation.

## Enterprise Model Projection

Canonical runtime path:

```text
Evidence
→ governed candidate
→ canonical financial fact
→ ObservationMemoryService or canonical equivalent
→ Observation repository
→ Enterprise Model repository
→ Commercial Digital Twin view
```

Reports, case files, workspaces and outcome pages read from the same durable state.

## Run State Machine

Canonical runtime states:

- `queued`;
- `retrieving_source`;
- `reading_document`;
- `selecting_sections`;
- `preparing_packets`;
- `estimating_cost`;
- `analysing`;
- `validating`;
- `updating_memory`;
- `completed`;
- `completed_with_exceptions`;
- `completed_with_no_accepted_intelligence`;
- `failed`.

Terminal states are `completed`, `completed_with_exceptions`, `completed_with_no_accepted_intelligence` and `failed`. Progress must be monotonic. Polling must stop permanently at a terminal state. A GET request or page reload must never create a new paid run.

## Idempotency and Caching

Use document hashes, packet hashes, prompt versions, schema versions, successful response reuse, revalidation without another provider call, duplicate-click prevention and no reprocessing of unchanged successfully processed evidence.

## Cost Governance

The runtime must support model configurability, input-token preflight where available, bounded output, no automatic expensive-model fallback, actual usage recording, cost by enterprise/source/document/Observation, application-level limits and cache reuse. Pilot model names and prices belong in an implementation profile or configuration note, not permanent architecture law.

## Persistence

Production Financial Intelligence requires durable storage. The current pilot limitation is that canonical state stored only on ephemeral disk must not be described as durable Commercial Digital Twin memory. Missing historic run behaviour and repository read/write consistency must be visible until production persistence exists.

## Failure Taxonomy

Architecture-level failure categories:

- source retrieval;
- document parsing;
- section selection;
- packet construction;
- provider configuration;
- authentication or quota;
- request validation;
- incomplete response;
- candidate validation;
- financial scale ambiguity;
- persistence;
- model projection.

Low-level technical codes are not the primary strategic-user language.

## Partial Success

Valid facts may proceed while invalid candidates enter Needs Attention. Use `completed_with_exceptions` when accepted intelligence exists alongside quarantined or rejected candidates. Distinguish `completed_with_no_accepted_intelligence` from a successful twin update.

## Explainability

Every accepted value exposes source, original page or record, reported value, normalised value, scale, period, scope, basis, confidence, Observation lineage and Enterprise Model attribute.

## Security and Trust

Secrets remain server-side. Credentials must not appear in logs or interfaces. Provider payloads and document content are logged only where strictly necessary. Source use must remain within public and permissible boundaries. Unsupported inference is prohibited.

## Acceptance Profile

Golden hosted pilot journey:

```text
Open BT
→ refresh Financial Intelligence
→ governed source retrieved
→ relevant financial evidence processed
→ at least one correctly normalised fact accepted
→ one Observation created or strengthened
→ one non-null Enterprise Model attribute persisted
→ Evidence and Observation lineage visible
→ second unchanged refresh incurs no duplicate provider call
```

BT is the pilot acceptance case, not hard-coded runtime architecture.

## Known Limitations and Future Evolution

- pilot storage;
- structured financial-source integration;
- broader enterprise evidence blueprint;
- scheduled collection;
- source-yield learning;
- additional provider evaluation;
- production database transition.

## Cross-references

- [ADR-010 — Structured-Source-First, AI-Assisted Evidence Acquisition](../../architecture/decisions/ADR-010-Structured-Source-First-AI-Assisted-Evidence-Acquisition.md)
- [EI-001 — Enterprise Model Specification](../../architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md)
- [EI-012 — Enterprise Observation Model](../../architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md)
- [CIOS Reference Architecture v1.0](../../architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md)

## Slice 1 ADR-011 dual-speed orchestration shell

ADR-011 introduces dual-speed Financial Intelligence as a single user-facing run with separated runtime lanes. Slice 1 implements only the orchestration and persistence shell behind the explicit `dual_speed_financial_intelligence` mode. The production default remains `structured_standard_financials` until official rapid evidence retrieval is approved.

### Unified user-facing run

The authoritative Slice 1 record is the existing standard run file:

```text
ai_financial_reports/runs/<run_id>.json
```

The record owns the user-visible run ID, support reference, result URL, overall status, completion class, rapid lane, verification lane, canonical-update lane, cost summary and diagnostics. Legacy `ai_financial_reports/rapid_runs` records may exist for compatibility but are not required by the standard progress or result renderer.

### Overall status and completion class

Allowed overall status values are `queued`, `running`, `completed` and `failed`. `completed` can include partial or unverified outcomes when a trustworthy user result exists. `failed` is reserved for the `no_trustworthy_evidence` completion class.

Allowed terminal completion classes are `verified`, `unverified`, `partial` and `no_trustworthy_evidence`. Slice 1 fixture rapid output with unavailable structured verification completes as `unverified` rather than failing the whole run.

### Rapid lane state

The `rapid_intelligence` lane records `status`, `evidence_status`, `source_receipts`, `candidate_fact_count`, `candidate_facts`, `management_commitments`, `hypotheses`, `unknowns`, `contradictions`, `user_result`, `exceptions` and elapsed time. Slice 1 marks seeded rapid prototype output as `fixture_only`. Fixture-only candidates are non-canonical and are not production evidence.

### Verification lane state

The `verification` lane records `status`, `source`, adapter handoff state, adapter result, facts checked, facts verified, facts rejected, facts contradicted, exceptions, diagnostics and elapsed time. Slice 1 records structured verification as `unavailable` without attempting live BT, FCA, ESEF or other external retrieval. No adapter result is reported before adapter handoff.

### Canonical-update state

The `canonical_update` lane records status, Evidence IDs, Observation IDs, Enterprise Model update flag, updated attributes, transaction result, idempotency result and exceptions. For Slice 1 fixture-only rapid candidates the status is `not_applicable`, `enterprise_model_updated` is false and Evidence, Observation and attribute arrays remain empty.

### Preservation rules

When the rapid lane has a non-empty `user_result` and is `ready` or `partial`, verification unavailability or failure must not blank the rapid result, replace it with a structured-source-unavailable message, fail the overall run solely because verification failed, delete candidate facts or write candidates to canonical memory.

### Fixture-only restriction

Seeded rapid prototype data is permitted only as a local orchestration fixture in Slice 1. User-facing rendering must visibly label it as fixture-only, not verified official evidence and not production-ready. Cost instrumentation for fixture-only Slice 1 runs must show zero AI calls, zero provider cost and zero live source calls.

### Deferred architecture debt

Slice 1 deliberately defers official rapid source retrieval, source identity and period validation, cited source-backed candidates, non-blocking live structured verification, unified candidate classes, canonical acceptance refactoring, removal of legacy rapid persistence and any production default change.

## Slice 2A governed rapid official-source acquisition

Slice 2A adds a runtime-only acquisition boundary for official rapid Financial Intelligence sources. It is limited to source configuration, governed retrieval, deterministic PDF validation and an inspectable `RapidSourceReceipt`. It does not extract financial facts, generate candidate facts, update Evidence, create Observations, update Enterprise Models, change UI routes or change the production default mode.

### Runtime objects

`RapidSourceManifest` represents the validated source configuration loaded from `config/flora/rapid_sources/*.json`. The approved Slice 2A manifest is `config/flora/rapid_sources/bt-group-plc-fy26.json` and contains the source identity, reporting period, artifact URL, approved hosts, accepted content types, byte limits and deterministic identity and period markers.

`RapidSourceReceipt` is runtime lineage, not canonical Evidence. It records source identity, requested and final URLs, final artifact host, HTTP status, content type, actual bytes downloaded, SHA-256 over the actual downloaded bytes, retrieval time, redirect chain, PDF magic result, parse result, identity result, period result, validation result and controlled failure fields. A receipt must not report acceptance merely because source metadata exists.

`AcquiredRapidSource` represents the temporary source file available only inside the acquisition context manager together with its receipt. `RapidSourceAcquisitionError` is the controlled failure type and carries a precise code, stage, user-safe message, optional field-level errors and the rejected receipt where available.

### Acquisition boundary and acceptance rules

The acquisition boundary is `acquire_rapid_financial_source(enterprise_id, reporting_period, configuration_key=None)`. It loads a selected manifest, validates configuration before any network request, retrieves through Flora's governed `fetch_document` boundary, applies rapid-source-specific validation, computes lineage from actual bytes and yields the temporary PDF path plus receipt in a context manager.

`official_source_retrieved` is meaningful only when configuration is valid, a request was attempted, HTTP retrieval succeeded, the final host is approved, content type is accepted, size is within configured bounds, PDF magic is valid, deterministic PDF parsing succeeds with at least one page, issuer identity markers are present, reporting-period markers are present and SHA-256 is available. Validation failures are rejected states, not success with warnings.

### Failure codes

Slice 2A uses these controlled rapid acquisition failures: `rapid_source_configuration_missing`, `rapid_source_configuration_invalid`, `rapid_source_not_selected`, `rapid_source_url_missing`, `rapid_source_url_invalid`, `rapid_source_host_not_approved`, `rapid_source_http_error`, `rapid_source_redirect_rejected`, `rapid_source_content_type_rejected`, `rapid_source_too_small`, `rapid_source_too_large`, `rapid_source_not_pdf`, `rapid_source_parse_failed`, `rapid_source_identity_mismatch`, `rapid_source_period_mismatch`, `rapid_source_integrity_failed` and `rapid_source_timeout`.

Configuration failures occur before retrieval and must have `request_attempted=false`. Identity mismatch, period mismatch and parser failure are validation failures, not download or configuration failures. User-safe messages must not expose stack traces or temporary filesystem paths.

### Resource, cost and memory rules

The full PDF is not persisted by Slice 2A. The temporary source file is deleted when the context exits on success or failure. If the reused governed fetch boundary writes its existing cache file, the rapid-source wrapper removes that cache file before returning control. Production persistence of the full PDF remains prohibited for this slice.

The Slice 2A boundary has a zero-AI contract: AI call count is zero, provider cost is zero and no provider dependency is introduced. A successful live acquisition records one external source call; configuration validation failures record zero external source calls. The boundary must not instantiate or call Evidence, Observation, Enterprise Model or observation-memory repositories.

### Relationship to ADR-010 and ADR-011

This increment implements ADR-010's structured-source-first discipline for rapid official-source lineage by validating an official issuer document before any interpretation. It implements ADR-011's dual-speed separation by preparing the rapid lane to carry inspected official source receipts while keeping provider output and future extracted facts outside canonical memory until governed acceptance.

### Explicit deferral to Slice 2B

Source-backed financial fact candidates, page/table locators, metric interpretation, scale and basis handling, rapid outlook generation, verification, canonical acceptance and production-default changes are deferred to Slice 2B or later architecture-approved increments.

## Slice 2B-1 source-backed runtime candidate extraction

Slice 2B-1 adds a deterministic, runtime-only extraction boundary for accepted Slice 2A official issuer results PDFs. `FinancialFactCandidate` is the authoritative runtime candidate contract for this slice. It may carry a proposed canonical metric identity, original displayed value, period start and end, verification status, ambiguity details, source SHA-256, source locator and evidence bundle metadata, but it remains candidate data and is not EI-001 canonical state.

The Slice 2B-1 extractor is limited to three statutory Group actual metrics: revenue, operating profit and profit before tax. It returns a candidate extraction result with status `completed`, `partial`, `failed_precondition` or `failed_extraction`, the source receipt reference, source SHA-256, extraction version, candidate and exception counts, candidates, exceptions, pages examined, table or section matches, elapsed time, AI call count, provider cost and canonical write count. `completed` means all three facts were safely produced; `partial` means one or two were produced and missing or ambiguous facts remain explicit exceptions.

Source preconditions are mandatory: the receipt must be accepted, PDF magic valid, parser validation successful, issuer identity matched, reporting period matched, actual-byte SHA-256 present and bytes downloaded greater than zero. A receipt/byte SHA mismatch fails precondition. The extractor makes zero AI calls, incurs zero provider cost, performs no OCR, performs no external calls after acquisition and writes nothing to Evidence, Observation or Enterprise Model repositories.

Candidate source locators are structured JSON strings using one-based PDF page numbers. Where available they include page, section, table, row, column, scale context and source SHA-256. A URL alone is not an adequate locator.

Scale must be explicit in source context, such as `GBP m`, `£m` or `GBP millions`, and maps to EI-001 scale values such as `millions`. Scale must not be guessed from magnitude. The current-period column must be explicitly identified from configured period markers such as `FY26`; prior-period comparators are not successful Slice 2B-1 candidates. Measurement state for successful candidates is `actual`; accounting basis for successful candidates is `statutory`. Adjusted rows and segment rows are rejected as candidate exceptions rather than silently substituted.

Candidate identity is deterministic. The fingerprint includes enterprise ID, proposed metric identity, reporting period, scope, accounting basis, measurement state, source SHA-256, source locator, reported amount and reported scale. Repeated extraction over identical bytes produces the same candidate IDs and no duplicate successful candidates.

The candidate exception catalogue for this slice includes: source precondition failed, metric label not found, multiple metric rows matched, period column not identified, amount ambiguous, scale missing, scale contradictory, currency missing, scope ambiguous, segment value rejected, accounting basis ambiguous, adjusted value rejected, supporting excerpt unavailable, source locator incomplete, duplicate candidate and parser failure. Each exception records metric identity where known, category, page/location where known, source SHA-256, a human-readable explanation, retry usefulness and evidence needed to resolve it.

Run integration, live UI enablement, broader metrics, rapid outlook generation, structured verification, canonical acceptance, Evidence creation, Observation creation and Enterprise Model updates remain deferred.

## Slice 2C — Source-backed rapid run integration

Status: implemented for the explicit `dual_speed_financial_intelligence` execution mode only.

Slice 2C connects the governed rapid-source acquisition boundary to deterministic rapid candidate extraction inside the unified Financial Intelligence run record. The coordinator loads the approved rapid source manifest, acquires the official source through Slice 2A, retains the actual-byte `RapidSourceReceipt`, runs Slice 2B extraction while the temporary PDF is available, serializes candidates and exceptions under the rapid lane, closes the acquisition context, and persists the completed run through `ai_financial_reports/runs/<run_id>.json`.

The accepted source receipt is a precondition for candidate extraction. If acquisition fails or the receipt is rejected, extraction is not run and no fixture or seeded values are substituted. The full PDF and temporary file path are not persisted.

The rapid lane records lane status, evidence status, source receipt, source configuration key, source validation result, extraction status, candidate count, candidate records, exception count, exceptions, source call count, AI call count, provider cost, canonical write count, elapsed time, pages examined and extraction version. Candidate records remain `candidate_unverified` and preserve source SHA-256, page/table locator, raw displayed value, decimal-safe amount, currency, scale, period, scope, basis and measurement state.

Success means an approved official source was retrieved, extraction completed, exactly three source-backed candidate facts were found, AI calls are zero, provider cost is zero and canonical writes are zero. Partial extraction persists the accepted receipt, available candidates and explicit exceptions. Zero-candidate extraction retains the receipt and exceptions and does not claim rapid financial facts are available. Acquisition failure persists the safe Slice 2A failure code/stage and zero candidates.

The standard Financial Intelligence result view renders an “Official-source candidate facts” section with document title, source authority, reporting period, retrieval status, candidate facts, reported amount/currency/scale, page/table citation, verification status, and the warning: “These figures were extracted from an approved official document but have not yet completed structured verification or canonical acceptance.” The view also states that canonical memory has not been updated.

Architecture boundaries: Slice 2C makes no AI calls, creates no canonical Evidence or Observations, does not update the Enterprise Model, does not run structured verification automatically, and does not change the default `structured_standard_financials` mode. Later structured verification, governed acceptance and canonical memory updates remain deferred. Automated live source proof is available only through the skipped-by-default `FLORA_LIVE_RAPID_INTEGRATION_TEST=1` smoke test; live source accessibility remains Unknown unless that automation executes successfully in an environment with outbound access.
