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
