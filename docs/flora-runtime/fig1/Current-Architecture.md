# Actual architecture audit and proportionality

Main is `e7c58feb84882b0e7a1ea38e7e1c72079402aa86`; full post-merge CI43763832158 passed before this branch. EAR-1 remains the unmerged draft reference at `d7052c9fa8598eb1f15bfa4f92440c9b6b284c06`; no file or implementation from that branch is merged. Original architecture/research/app bytes are preserved.

The [17-gate audit](Gate-Audit.json) names each implemented function, owner, risk, applicability to analysis/canonical state and proposed simplification. The following distinctions are central.

| Stage | Existing owning implementation | What is genuinely mandatory | What is not a universal requirement |
|---|---|---|---|
| Acquisition/verification | `financial_intelligence.rapid_sources`, `source_import`, live SourceRecord | Authentic source, safe transport, actual acquisition extent, identity/date/integrity appropriate to route | Every analytical result must use only the narrow current Slice2A→2B PDF route; fabricated full-byte archive for an honest excerpt |
| Source permissions | Source/use owner, publisher terms/licence and current positive policies | Applicable access/process/retention/reuse/audience authority; current denied hosts stay denied | Public URL means unrestricted use; enabled source means licence; one new legal decision per numerical cell |
| Candidate creation | `rapid`, adapters, candidate_validation, source contracts | Typed, located, appropriately labelled candidate; provider output untrusted | Canonical Enterprise ID for every research display, a BT default identity or no output until full verification |
| Financial meaning | normalisation/catalogue/table bundle and EI001 financial contract | Correct unit/scale/sign/precision/basis/legal scope and stock/flow/ratio dates | April–March for all issuers; canonical whitelist as the only valid reported label; arbitrary cross-bank arithmetic |
| Calculations/estimates | presentation `Statement`, `difference`; existing financial owners | Reproducible method, compatible inputs, explicit assumption/estimate provenance | Individual accepted Observation for every calculation/chart point; arithmetic upgrades an assumption to a fact |
| Evidence acceptance | Governed financial acceptance or Blueprint item review | Actual canonical authority and object validation if durable acceptance is chosen | All analytical use must wait for canonical promotion; every accepted record necessarily needs a manual click |
| Observation/Model | memory/service/repository, Blueprint promotion/projection | Atomic accepted memory, typed durable financial meaning and read-after-write lineage | Re-extracting numbers from prose as a substitute for structured persistence; prose projection equals complete numeric success |
| Presentation | six-type policy, existing candidate agenda releases, VP2 Main | Authorised owner input, source dependencies, caveats and meaningful scope | Rendering changes canonical state; every new dataset requires another hard-coded renderer branch |
| Lifecycle | source/research/presentation/mapping owners | Current applicability/rights, consistent revocation/contradiction/supersession before dependent output and canonical write | Editorial expiry equals legal licence expiry; withdrawn URL automatically destroys all historical permission; one helper covers every encoding |
| IAM / transaction | verified contexts, resource scope, review/planning/promotion | Server authority, exact workspace/Enterprise/ACL, approved mutation scope/target versions, audit/compensation | Issuer name, public source status, review JSON or AI confidence grants private scope or write authority |

## Implemented versus intent versus history

**Accepted intent:** ADR001/002 protect atomic durable memory; ADR010 prefers adequate structured sources and exception-focused human review; ADR011 explicitly permits useful candidate financial analysis before canonical verification; ADR012 separates analytical baseline acceptance from canonical record promotion; ADR014/024 reserve deterministic authority and high-consequence human judgement. EI001/EI012 remain their repository statuses; they identify domain ownership without wholesale acceptance of draft papers.

**Implemented analytical capability:** candidate-only `rapid_runs`; fixed source-permitted EAI/BIE releases; read-only calculations and six semantic classes. The material caller boundary matters: `intelligence_presentation.eligible` is not an IAM/source-permission evaluator, and `restricted_metadata({}) == False` is not a grant. Existing agenda callers add source/pin/use checks. A generic extension must preserve that boundary.

**Implemented canonical capability:** financial `_is_auto_acceptable/_apply_automatic_claims` already automates selected validation and writes through memory in its governed context. Blueprint review/mapping/plan/approval/execution is another governed path, with record-level history and exact target reconciliation. It is inaccurate to describe every path as one mandatory human click per fact. These consequential calls—including nominal dry-run planning—must not be used by read-only analytic rendering.

**Historical constraints:** BT-specific defaults/financial aliases/fiscal assumptions, limited source manifests and bespoke release pins came from bounded pilots. Their presence is evidence of current behaviour, not a requirement to make every new bank emulate BT or every chart emulate a canonical import.

## Genuinely excessive friction

1. Re-evaluating the same source-use basis for many cells rather than referencing one applicable document/series/category decision. Approval of the policy is still real; repetition is what can shrink.
2. Applying canonical metric/identity prerequisites to all candidate analytical output even when source meaning can be preserved without a canonical mapping. Unsupported comparison/write must remain blocked.
3. Requiring per-release code and repeated package/source/claim wiring for each small public data slice. Generate/validate integrity references through existing governed releases; do not remove hash checks or auto-allow unknown files.
4. Repeated partial metric definitions across extractors, financial normalisation and prose Model fallback. Retain one financial-domain meaning and typed payload; validate route-specific acquisition separately.
5. Confusing source receipt acceptance, candidate validation, use permission, Evidence acceptance and projection completion. They protect different risks; clear compact metadata can replace ambiguous labels and repeated explanations.

Some friction is a **missing contract**, not overengineering: deposits, instant periods, numeric serialization and inconsistent lifecycle encodings are correctness defects. More approval documents will not repair them.

## Essential repetition and automation boundary

A downloaded byte checksum and an approved target fingerprint are not the same check. Financial row definition and tenant scope are not the same check. Rechecking revocation/authority at use/execution prevents stale-cache and time-of-check/use failures. Simplify their implementation and reuse stable results, but keep their purposes separate.

Source identity/licence matching, unchanged content reuse, arithmetic, period/basis consistency, duplicate detection and unambiguous extraction can be automated under approved policies. Human attention should focus on uncertain rights, conflicting identities, material contradictions, ambiguous tables and selected durable acceptance. Confidence scores, an official logo or a successful parser never replace those authorities.
