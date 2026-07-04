# BT AI Document Understanding Spike

## Mission
Determine whether modern multimodal document-understanding can convert authoritative BT financial and corporate documents into strict, evidence-backed foundation facts for the Commercial Digital Twin.

## Starting state
Remote `origin` was not configured in this workspace, so `git fetch origin` could not run. The inspected local starting commit was `e7cc5b2cc0cb3610e3f9740c3be6aaa10888b6fa`.

## Mandatory architecture reading inspected
The spike implementation was aligned to `CIOS-AI.md`, the CIOS reference architecture, design doctrine, Chief Architect handbook, accepted ADRs, EI-001, EI-012, FP-003, BT factual twin documentation, PDF ingestion, evidence extraction, factual claim and Observation code, and existing Flora tests.

## Current Flora architecture and model inventory
Runtime inspection shows Flora factual collection is deterministic Python code. PDF retrieval and embedded text extraction are implemented in `cios/applications/flora/live/documents.py`. Evidence candidate classification is regex, keyword, source-tier and gate based in `cios/applications/flora/live/extractor.py`. Factual claims and Observations are produced by deterministic decomposition and validation in `cios/applications/flora/memory/service.py`.

Configured AI providers for factual document understanding: none in runtime code.

Current model names used for factual document understanding: `flora-pdf-text-v1` for PDF text extraction and deterministic claim decomposition; no LLM model identifier is invoked.

Stages invoking a language model: none in the factual document ingestion, evidence extraction, factual claim decomposition, or Observation memory path inspected for this spike.

Deterministic stages: PDF fetch, embedded-text extraction, keyword classification, evidence gates, factual claim regex decomposition, claim validation, Observation creation, Enterprise Model projection.

PDF multimodal handling: PDF bytes are not passed to a multimodal model. Flora extracts embedded text and reasons over snippets.

Evidence extraction LLM use: current Evidence extraction does not use an LLM.

Signal and report generation: reports are generated from deterministic views over seeded/live evidence and memory. No separate factual-understanding model path was found.

Required environment variables for the experiment routes: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`, `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY`.

Provider abstraction: this spike adds a provider-neutral experiment interface only; it does not alter production collection.

Answer: no AI model currently performs factual document understanding in Flora. Current Flora performs deterministic PDF text parsing plus rule-based evidence and claim extraction.

## Provider documentation used
OpenAI official documentation describes PDF/file inputs as `input_file` items for the Responses API and Structured Outputs as JSON-schema-constrained responses. Anthropic official documentation describes JSON structured outputs for Claude. The implementation keeps these details behind experiment-only providers.

## Experiment design
The target chain is authoritative document to document structure understanding to structured facts to independent verification to atomic Observations to Enterprise Model projection. This spike deliberately stops before production Observation creation for provider outputs.

Routes:
- Route A: current Flora deterministic baseline.
- Route B: OpenAI direct native PDF understanding, model `gpt-5.5`, Responses API, strict structured JSON schema.
- Route C: Anthropic direct native PDF understanding adapter boundary; not executed without credentials and SDK wiring.
- Route D: Layout service plus OpenAI reasoning boundary; not executed without Google or Azure layout credentials.

## Documents and pages
Governed BT source profile documents selected:
- BT Group Annual Report 2026.
- BT FY26 full-year results release.

Stage 1 focused page ranges:
- Annual report pages 1-20: identity, highlights, strategy, organisation.
- Annual report pages 90-100: leadership.
- FY26 results pages 1-5: group and segment financial metrics, outlook.

Stage 2 wider-document testing was not executed in this PR because credentialed provider runs and cost approval are required.

## Schema
The experiment schema is `FoundationFact` / `FoundationFactSet` in `experiments/document_understanding/schema.py`. It rejects unknown fields, unsupported claim types, unsupported states, missing page references, overlong excerpts, and multi-metric financial facts.

## Verification
The deterministic verifier checks page existence, excerpt presence, numeric support, currency, scale, period, business unit support, allowed vocabularies, and financial atomicity.

## Results
No external provider credentials were present in this workspace, so no external model route was truthfully executed. The harness records missing credentials as `not_executed`, not success.

Current Flora baseline result: deterministic baseline implemented and documented as the control route. It does not perform native PDF understanding and therefore is expected to have low recall on table-heavy annual-report facts unless embedded text and regex patterns align.

OpenAI direct PDF: implemented. Not executed here because `OPENAI_API_KEY` was unavailable.

Anthropic direct PDF: provider boundary retained. Not executed because `ANTHROPIC_API_KEY` was unavailable.

Layout plus reasoning: provider boundary retained. Not executed because neither Google Document AI nor Azure Document Intelligence credentials were configured.

## Accuracy, recall, lineage, cost and latency
The sanitised summary JSON records provisional not-executed route metrics. No fabricated precision or recall is claimed for unavailable provider routes. Cost and latency are recorded as unknown for not-executed routes.

## Limitations
- Golden facts are provisional and require human review.
- No copyrighted PDF or full raw provider response is committed.
- The OpenAI direct route is implemented but requires credentialed execution against focused page-range PDFs.
- Anthropic and layout routes need credentialed SDK completion before evidence-based provider selection.

## Recommendation
Recommendation: **E. None meet the quality threshold yet**.

Rationale: the architecture should not select a provider without measured execution. The next responsible step is to run the OpenAI direct-PDF route on focused page ranges, compare against the deterministic Flora baseline and provisional human-reviewed facts, then run a layout-first comparison if table/page-lineage errors appear.

Provisional target architecture if OpenAI meets gates after credentialed execution:
- document structure provider: native PDF model first, layout service fallback for table-dense documents;
- factual interpretation model: `gpt-5.5` direct PDF using strict `FoundationFactSet`;
- verification method: deterministic verifier first, optional independent model verification second;
- confidence policy: high model confidence cannot bypass deterministic support checks;
- retry policy: bounded transport/schema retries only, no silent cheaper-model fallback;
- integration boundary: experiment outputs remain outside production collection until a separate sprint;
- fallback: explicitly configured provider fallback only;
- data retention: raw responses stored outside Git and outside production memory.

## Proposed ADR
No Proposed ADR is created in this PR because no external provider route was executed and measured. Human approval and measured results are required before an enduring architecture decision.
