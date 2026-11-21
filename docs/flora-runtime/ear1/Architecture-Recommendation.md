# Narrow existing-owner recommendation — proposed, not accepted

## Authorities and boundary

Read CIOS-AI, Reference Architecture, Design Doctrine, Chief Architect Handbook, Glossary/Document Map, accepted ADR-001/002/005/009/010/011/012/014/015/016/024/026, the source contracts and current runtime. Authority follows the owner's explicit bounded commission and accepted ADRs. EI-001/EI-012 retain their repository status; references identify ownership without accepting draft papers wholesale. ADR-024 has legacy Draft metadata but an explicit Accepted body and accepted index entry. ADR-027 remains **Proposed**, ONS/SEC-scoped, with no NatWest authority. No architecture file is changed here.

**Decision requested:** Defer production admission now; review the exact-use proposal and authorise only a subsequent bounded implementation in the existing owners if its prerequisites are met. Do not introduce a second source registry, admission engine, Evidence store, financial model or public candidate bypass. The offline CLI is an assurance observer, not a production rule or rights evaluator.

## Genuine compatibility findings

| Existing implementation | Pure observed behaviour for these two claims | Consequence / proposed bounded work |
|---|---|---|
| `source_import.official_url` / `provenance` | Original issuer host denied; enabled/verification flags do not change it | Preserve denial. Exact document/use authority must be represented and checked by the existing source owners before a separately reviewed implementation |
| `live.source_registry.SourceRecord` | Source identity/enabled/purpose fields do not represent an executed document-specific rights decision | Enabled is not permission. Chief Architect must decide the minimal source-owner contract/decision linkage; no new registry invented here |
| `memory.source_contracts` | `investor_results` permits financial metrics | Source-type capability only, not publisher rights or acceptance |
| `Financial NumericFactValue` / `normalise_amount` | Two GBP-billion amounts represent and scale correctly | Representation is not verified metric/date mapping or canonical Evidence |
| `PdfFinancialTableAdapter._recognised_row` / metric catalogue | Neither customer-deposit definition is recognised | Owner-approved distinct metric definitions/aliases and scope/basis tests needed. Do not relabel deposits as revenue/net debt |
| `normalise_reporting_period` | Date text alone becomesFY26 with2025-04-01→2026-03-31. Explicit end preserves that end but still does not establish a faithful point-in-time stock period | Add explicit as-at stock semantics in the existing financial owner. Never use a fiscal default or publication date to repair stock semantics |
| `FactualClaim` validator | Blank real Enterprise ID rejects; prefixed attribute/numeric format alone can pass when fixture strings supplied | Field validation is not repository identity, Evidence acceptance or numeric durable integration |
| `Observation` / memory service / repository | Dataclass has no persistent numeric value/unit/currency/basis/normalised_amount fields. Dynamically attached amount is omitted by `to_dict` and absent after reload | Existing owner must define compatible persistent typed financial lineage/projection, retaining old records; do not attach transient fields and claim durability |
| `_financial_model_value` | Deposit sentence is not recognised by its limited regex and is returned as prose | A supported reviewed Observation could create a textual attribute, but that is not a proven durable numeric financial projection. No successful numeric Model integration claimed |
| `CanonicalPromotionService` | Actual receipt includes projection status; transaction success can coexist with partial/not_projected projection | Owner acceptance must reconcile values/scope/Evidence/Observation/Model **after reload**, not just execution status |
| `mapping.evidence_is_current` | Inactive lifecycle strings deny, but an accepted row with `freshness:stale` or boolean `withdrawn`/`retracted`/`core_contradiction` is still returned current by this helper | This is not a complete source/rights/revocation policy. Explicit current encodings and source dependencies must be resolved in existing owners before admission; do not use this helper alone as proof of safe end-to-end use |

These are contract limitations for the selected deposit use, not a claim that every existing financial or textual Model path is broken. Four observational tests record the lifecycle-helper gap without endorsing its current result as desired future policy. The EAR proof remains denied independently. No catalogue, regex, schema, runtime route, source policy or projection implementation is changed by EAR-1.

## Smallest subsequent implementation proposal

1. **Document-use decision first:** actual rights/source owner resolves each audience/purpose with supporting permission evidence, exact document/field identity and attribution/retention/export/revocation limits. An internal business use is not presumed personal use. This cannot be replaced by this JSON, an enabled source, a research validation score or accepting ADR-027 by implication.
2. **Source admission design:** preserve the current positive publisher policy and all default denials. If authorised, extend the existing provenance/admission owner to consume the genuine scoped decision; do not broadly add an issuer hostname. URL-only calls without a valid exact-document/use/audience binding must continue to deny. The design must bind original/retrieval identity and authentic version where required, reject ambiguous paths/redirects and use owner-controlled expiry/revocation before dependent content. No caller-supplied callback/boolean can grant authority.
3. **Financial owner compatibility:** define distinct total versus excluding-central metric/basis, as-at stock periods and persistent typed representation/lineage using existing financial, Observation and Model owners. Preserve the original reported amount/scale and rounded precision, signed-value capability, historical schema compatibility and exact Group target. A textual compatibility check is not the acceptance criterion.
4. **Governed execution only after separate authority:** existing supported candidate/staging/review/mapping/plan/promotion transaction and receipt reconciliation; idempotency, scoped identity, target snapshots, contradictions and compensation unchanged. Each of the two assertions gets an individual Evidence decision. No automatic Material Pressure or Pipeline action.
5. **Read-only view later:** use existing accepted financial/Twin projection and six-type presentation policy; preserve caveats and source revocation/tenant checks. No static rendering of blocked candidate financials to make a demo look complete.

Source-use/publisher authority may require a narrowly reviewed architecture/source-owner decision because its executed document-use contract is absent today. Metric/as-at/persistent numeric support is bounded implementation under existing owning doctrine if the Chief Architect confirms compatibility; it need not invent another canonical owner or approve an unrelated ADR. Neither decision is selected here.

## Required future implementation test matrix

| Area | Must pass before any authorised transaction or public use |
|---|---|
| Scope/identity | Exact HTTPS host/path/document/version/issuer/report date and only selected fields; deny redirects, credentials, fragment/query/path ambiguity, another report/issuer/subsidiary, guessed canonical ID, wrong workspace |
| Rights/authority | Exact audience/purpose, real rights decision/evidence, expiry/revocation and verified role; deny unknown/malformed/withdrawn/retracted decisions, edited JSON approval, unverified headers and unapproved targets |
| Financials | Two distinct definitions, source precision, explicit GBP scale/sign, actual stock date, correct basis, original cell lineage; deny swapped rows, target/actual, publication-as-period, flow/stock and Group/legal-bank mixing |
| Acquisition | Honest missing original hash; authentic bytes/hash/bundle for PDF route; correct excerpt route without fabricated archive/bounding box; no proxy/relabel workaround |
| Review/mapping | Individual decisions, scoped exact-content fingerprints, unchanged/corroboration/update distinction, duplicate targets and contradictions fail closed, no fuzzy/URL merge |
| Transaction | Verified recent authority, plan/source/review/mapping/Twin/target fingerprints, count reconciliation, repeated plan idempotency, approval invalidation and safe existing compensation |
| Durable projection | Repository round-trip preserves typed amount/scale/date/basis and lineage; exact Model values/identities after reload; reject partial/not_projected as proof of full success |
| Presentation | No content/title/count/cache/export from denied/private/stale/contradicted support; preserve current UI, artwork, Offers/Pipeline and existing six semantics |

Current EAR-1 tests exercise current denials/limitations and existing-owner pure reconciliation, not this unimplemented future matrix as if it already passed.
