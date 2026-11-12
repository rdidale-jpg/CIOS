# Runtime diagnosis — completion of Sprint 2

Verified current dependency heads: #568 b4a2c2c680d21bc252f3bc7e365c7eb08af178d3 (draft, base main); #569 cb21f641ae246fbe2e9c33f301994d7e5e104f59 (draft, base #568 branch). Work continues on #569, not a new sprint or PR. No applicable AGENTS.md found in the repository areas or ancestors.

The previous broad statement that no model integration exists was incomplete. Existing owners are `enterprise_intelligence/provider.py` (`provider_from_env`, `OpenAIResponsesProvider`, `LLMResult`), `financial_intelligence/openai_provider.py` (installed Responses SDK readiness and token/cost helpers), `financial_intelligence/config.py` (model/cost conventions), `provider_guard.py` (bounded call guard), and strict schema conversion in `financial_intelligence/schema.py`.

The current factory selects `UnavailableProvider`. Safe metadata checks confirm provider/model unset and no reasoning/OpenAI key present. SDK 2.54.0 imports successfully and exposes Responses and token counting. Managed status reports current observations, enforced restricted policy, no configured secrets/outbound identities; the startup allowlist excludes api.openai.com and official research hosts. No secret value was read or printed. Production/Render configuration was not inspected or changed.

The blocker was **configuration plus implementation**. #569 supplied a deterministic controlled-language proof but no general semantic model adapter. Existing financial PDF extraction is not a research verifier and can write raw responses; existing enterprise structured generation does not pass a complete strict schema. Reuse the existing provider selection, SDK, schema and budget conventions through a research-specific adapter; do not call the PDF workflow or broaden shared production routes.

Endpoint: existing OpenAI Responses API (`https://api.openai.com/v1/responses` by default), configurable only through the existing approved provider base URL. Secret: `FLORA_REASONING_API_KEY` or existing `OPENAI_API_KEY`; no new vendor/account is required. Exact environment configuration and no-charge readiness/model-access checks are documented with the adapter. Adding a credential alone is insufficient: model identity, explicit bounded spend, reviewed rates, source rights and permitted egress are required.

Existing API usage can incur token charges even though no new service contract is created. This completion performs no billable call while configuration/spend authorisation is absent. Synthetic provider tests are labelled fixtures. A configured independently retrieved second context is not an independent model family or a guarantee of truth. Researcher outputs/confidence/reasoning must not be supplied to the verifier. Release also requires deterministic scope/provenance/rights/correction gates and an explicit contradiction challenge.

## Exact non-production configuration path

Use the managed development executor's secret/settings facility, not a repository `.env`, public route, chat, Render or production service. Reuse the existing authorised OpenAI account. Configure `FLORA_REASONING_PROVIDER=openai`, `FLORA_REASONING_MODEL` to an account-authorised structured-output model, and secret `FLORA_REASONING_API_KEY` (existing `OPENAI_API_KEY` also works for this provider). Optional approved endpoint names are `FLORA_REASONING_BASE_URL` / `FLORA_REASONING_API_BASE`; `FLORA_REASONING_API_VERSION` is forwarded if that existing endpoint requires it. The diagnostic aliases `FLORA_ENTERPRISE_INTELLIGENCE_PROVIDER/MODEL` do **not** select the current factory; use the exact reasoning names.

Explicitly approve a per-invocation `FLORA_RESEARCH_MAX_RUN_COST_USD` and reviewed model-specific `FLORA_FINANCIAL_INTELLIGENCE_INPUT_COST_PER_1M`, `FLORA_FINANCIAL_INTELLIGENCE_OUTPUT_COST_PER_1M`, plus `FLORA_RESEARCH_PRICING_VERSION`. No prices or budgets are guessed for an arbitrary model. `FLORA_FINANCIAL_INTELLIGENCE_MAX_OUTPUT_TOKENS` is reused, capped at 2,000 per generation. The adapter reserves exact preflight input-token plus maximum output-token cost and limits a cycle to three generation calls, with no SDK retries. A failed call retains its reservation. Provider pricing changes, account entitlement and token-count compatibility still require verification before use.

Have the managed executor administrator permit the approved model endpoint host (default `api.openai.com`) and the exact selected source hosts: `www.gov.uk`, `assets.publishing.service.gov.uk`, `www.gca.gov.uk` or `ec.europa.eu`, only as needed. Do not bypass the session proxy/network policy or enable unrestricted egress. Companies House is an optional future registry acquisition host; the runtime currently selects the eight reviewed authority excerpts only. Current metadata inspection found no secrets/runtime variables/outbound identities. No such settings were changed by this work.

From the repository, with the existing Python environment:

```sh
python tools/research/flora_semantic.py readiness
python tools/research/flora_semantic.py connectivity
python tools/research/flora_semantic.py calibration-plan
# Only after configuration and bounded existing-account spending approval:
python tools/research/flora_semantic.py cycle --source AWS-PLAN --execute
python tools/research/flora_semantic.py calibration-case --case REAL-ms-ai-role --execute
```

`readiness` and `calibration-plan` make zero network/model calls. `connectivity` performs only authenticated `models.retrieve` metadata access when the existing provider and approved egress are present; it sends no evidence, generates no tokens, and does not prove generation support. Current actual result is **blocked**, zero calls. `cycle` and a single selected `calibration-case` can incur existing-account token charges; neither enables a background job. CLI errors expose the exception class only. Do not redirect structured research results into shared logs if a future source policy has not cleared publication.

## Separation and publication boundary

The one-claim cycle retrieves reviewed public evidence as researcher, extracts a complete candidate, then separately reacquires each source for verifier and challenger with role-bound new nonces, request timestamps, distinct acquisition references, matching source identities/bytes and a no-cache request. The verifier receives the proposed claim and its own acquired evidence, not researcher responses/confidence or private reasoning. The challenger uses another context/retrieval but the **same selected source set and model**: not an external literature search, a different model family or a guarantee of independent truth. Edited/missing snippets, redirects, changed scope, unresolved rights, source supersession/conflict, unsupported citations and stale current claims fail closed.

Strict structured output includes eight semantic facets and concise quotable evidence justifications. Deterministic identity, geography, period, source-state, exact citation/hash and publication-safety gates remain necessary. Scenario claims cannot publish. Fixture decisions are marked as fixtures. A positive adapter result is only a **candidate decision** (`release_eligible=false`), never a canonical write or Pipeline qualification. A future governed handoff must use the existing scoped operations/correction owner; its GCA-only programme is deliberately not broadened to admit new source families. Thus live release and actual correction propagation for newly generated semantic claims remain undemonstrated. Existing correction tests exercise the original owner with synthetic fixtures, not live data.

The adapter is implemented and fixture-tested. Live integration, model entitlement/generation behaviour, provider-side processing/retention settings, real-source calibration and scoped operational publication are not accepted merely because the adapter compiles or its fixtures pass. Rob is not assigned routine enterprise-fact review: the engineering path must close these gates before autonomous publication.
