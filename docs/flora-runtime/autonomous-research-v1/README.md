# FLORA autonomous research foundation v1

## What works

An operator-invoked, bounded **establish** workflow: programme → existing Researcher mission validation → permissioned acquisition requests → durable receipts → independent reacquisition → deterministic assurance → versioned candidate research publication → existing FLORA Industries navigation. There is no scheduler, model API, new canonical database, automatic promotion or Pipeline capture.

Open **Industries → UK Technology → Provider baseline / Evidence & assurance / Gaps** (`/research/programmes/uk-technology`). Seven overlapping coverage categories distinguish operating-model segments from capability/role tags. The public route reads only five exact-hash-pinned repository assets. It cannot read job databases, archives or tenant stores. Existing Banking/Aviation navigation and Pipeline owners remain unchanged.

## Demonstrated, not simulated

On 12 November 2026 the approved web research tool retrieved five official GCA pages, then separately retrieved all five again after verifier requests were issued. Actual request IDs, retrieval times, excerpt checksums and distinct tool references are in [Acquisition-Receipts-v1.json](../../../enterprise-knowledge/technology/research-foundation-v1/Acquisition-Receipts-v1.json). Researcher references are `turn830034view0`–`view4`; verifier references are `turn448024view0`–`view4`. This is a **separate acquisition**, using the same orchestration environment/tool provider; it is not independent human review, an independent model, guaranteed cache bypass or multiple-source corroboration.

- Four catalogue cohorts × first four displayed headings. Annodata's brand/group label is excluded pending identity resolution. **15 distinct candidate labels**, plus a source-specific provider-page claim: **16 literal claims**, five source pages, **one publisher family**.
- Provider: **ADVANIA UK (CCS) LIMITED**. Its published supplier-page name is supported; its catalogue labels are inspectable evidence. **ADVANIA UK LIMITED remains separate.** No parent/subsidiary/registry identity link has been accepted.
- Actual measurements: 10 logical source requests, no retries, retained short-excerpt byte count in the execution receipt. Original page bytes/network byte counts are not measured or retained. Paid/model clients are not configured; no new paid-service commitment was made, and actual tool/model cost is not metered.
- Accepted means **accepted for bounded research publication**, using existing SourceSegment/CandidateClaim objects. It does not mean a verified real-world enterprise fact or promoted canonical Observation. All 12 baseline dimensions remain open/partial research requirements; procurement presence is a very thin provider baseline.

This demonstrates the machinery, **not a complete UK industry twin or deeply researched provider**. Unknown publication/effective dates remain null. Retrieval freshness does not establish a publication date or current contractual eligibility.

## Coverage rules and next population increment

[Programme.json](../../../enterprise-knowledge/technology/research-foundation-v1/Programme.json) defines comparable industry structure, economics, value chain, capabilities, ecosystem, change forces, enterprise business models/divisions/strategy/published context and evidence-linked hypotheses. [Population-v1.json](../../../enterprise-knowledge/technology/research-foundation-v1/Population-v1.json) is a rebuildable projection, with selection evidence, entity-label kinds, exclusions and gaps.

The catalogue order, not familiarity, determines the sample. Alphabetical truncation is strongly biased; catalogue counts were not promoted into market-size claims. UK procurement participation alone does not establish UK headquarters, significant UK operations, scale, strategic importance or manufacturer/reseller roles. The population is proposed **research candidates**, not confirmed key enterprises. Data/AI, channel roles and emerging technology are explicit coverage gaps; no AI deployment is inferred from a framework tag.

Next: resolve exact public legal identities and significant UK operating scope without retaining personal officer/contact data; acquire licensed enterprise/statistics/register sources for comparable scale and role evidence; expand every segment using documented pagination, quotas and stopping rules, including firms outside public procurement. Rank key enterprises only after those criteria have evidence. Then run the same baseline requirements across the selected population. Commercialisation, buyer discovery and pricing remain out of scope.

## Contracts, modes and execution

The frozen, extra-field-forbidden Pydantic operational envelopes in `foundation/contracts.py` are version 1; source-policy/output-schema IDs are pinned. They wrap existing canonical classes rather than replacing them. `mission_manifest()` uses the existing Researcher registry, profile versions, mandatory outputs and **owner validator**. This creates a candidate work order; it does not falsely claim all mandatory canonical registers are already populated.

| Mode | v1 status |
|---|---|
| establish | Working bounded driver, external permitted collector bridge, checkpoints, retry/request/retained-byte caps, cancellation and idempotent research release |
| enrich | Versioned contract accepted; execution explicitly unsupported |
| monitor | Versioned contract accepted; execution unsupported; no scheduling/unattended access |
| reconcile | Versioned contract accepted; execution unsupported; bounded explicit withdrawal/supersession is implemented separately |

The network bridge is intentionally external: it must use an approved acquisition route, examine the requested source and return only the permitted located excerpt. The runner cannot circumvent egress restrictions. A request nonce/receipt is a lineage check, **not cryptographic proof that an arbitrary collector actually visited a URL**. Collector integration is trusted operator tooling; no public endpoint accepts receipts or `live_web_bridge` assertions. The checked-in live release is separately inspectable and content-pinned. Fixture receipts default to `fixture` and cannot satisfy the public snapshot gate.

```sh
# Run from the repository using its normal Python environment.
# Choose a new private local directory, never a production/tenant store.
python tools/research/flora_foundation.py --root /tmp/flora-research-example create \
  --programme enterprise-knowledge/technology/research-foundation-v1/Programme.json --key example-v1
python tools/research/flora_foundation.py --root /tmp/flora-research-example advance --job JOB_ID
# The pending request goes to the approved web collector. Ingest its actual receipt:
python tools/research/flora_foundation.py --root /tmp/flora-research-example ingest --job JOB_ID --receipt ACTUAL_RECEIPT.json
# Repeat advance/ingest: verifier gets a new request, without the researcher's text.
# On completion advance assures and creates an idempotent research release.
python tools/research/flora_foundation.py --root /tmp/flora-research-example status --job JOB_ID
python tools/research/flora_foundation.py --root /tmp/flora-research-example mission --job JOB_ID
```

`request`, `fail`, `cancel`, `assure`, `release`, `withdraw` and `rebuild` expose explicit steps; export stays inside the isolated root. `establish(operations, job_id, collector)` is the reusable synchronous driver. `AwaitingAcquisition` checkpoints without spending retries; `AcquisitionUnavailable` spends a bounded attempt. Invalid/unsafe evidence fails immediately rather than being silently retried. Exhaustion retains a gap and stops release. Reopening the database or retrying completed steps does not reacquire or duplicate claims/releases. A programme cut-off change requires a new explicit job; it is not silently rolled forward.

## Source policy and assurance

Each source separately records acquisition, deterministic extraction, model processing, retention, quotation, indexing and redistribution permissions. Unknown/blocked denies the affected operation. Five finite HTTPS GCA URLs are the only configured acquisition scope. **No semantic model processing is enabled**: its permission is unresolved, and semantic interpretation/scenario publication is withheld. Codex-assisted source discovery and policy/code review occurred during development; do not describe this sprint as wholly model-free research.

GCA's [Using our content terms](https://www.gca.gov.uk/terms-and-conditions) permit reuse of Crown-owned content under OGL v3, excluding third-party material/logos. The release retains only short Crown catalogue name/label fields, at most 25 quoted words per page; no supplier contacts, DUNS, logos, attachments or full HTML. The original TNA licence page returned 403 through the approved tool; that restriction was not bypassed. Licence scope here relies on GCA's explicit content terms. No general permission for other government/supplier pages is implied.

The Supplier Registration Service IT-goods/services listing was investigated but **excluded**: its detailed use terms conflict with a simple footer OGL assumption and DUNS has third-party rights. Companies House supplied a possible identity research lead, but unresolved site reuse scope means no register record/person/address was imported or used to accept a legal identity. No leaked, restricted, confidential or accidentally exposed material is an approved source. A broader source registry needs separate operation-specific review.

| Responsibility | Executable v1 gate | Limit |
|---|---|---|
| Researcher | Issued finite request; exact excerpt/hash/location/dates | No private context or tool-policy instructions accepted from sources |
| Independent verifier | Separate later request/collector/tool reference, matching excerpt and locator; archive rechecked | Same tool/publisher; no independent semantic model or uncached-origin guarantee |
| Entity/applicability checker | Exact names remain separate, no legal-ID/HQ/applicability inference | Register identity and significant UK operations remain Unknown |
| Challenger | Conflict/stale checks, fixed publisher-family identity, contrary passage withholding | No complete open-web contradiction search; absence of contradiction is not asserted |
| Synthesis reviewer | Only whole-line catalogue name claims can pass | Interpretations/scenarios remain typed and withheld pending semantic assurance |
| Publication safety | Operation rights, bounded excerpt, restricted visibility, injection/sensitive patterns, pinned public snapshot | Narrow field policy and deterministic checks, not general PII/semantic detection |
| Release controller | Immutable versioned release; current active claims only; archive/hash gate | Research publication only, no canonical mutation/qualification authority |

Role IDs separate responsibilities; they do not represent seven independent people/models. No confidence score or model agreement authorises release. Schema/date/hash/scope checks are deterministic; stale dated publications and conflicting passages are retained but withheld. Copied pages from the GCA remain one family. Arithmetic/financial prose is outside the literal-name extractor and cannot become a numerical claim. Unresolved information becomes a gap, not routine factual review for Rob.

Facts, interpretations and scenarios use distinct envelopes around existing claim identities. Relationship predicates distinguish product supply, capability support, declared alliance, implementation, industry relevance and named deployment. Every relationship/hypothesis is withheld in this increment; evidence dependencies do not constitute semantic approval. Alliances imply neither contracts nor adoption; market relevance implies neither enterprise use nor customer demand/budget.

## Storage, privacy and corrections

- **Archive:** private, permitted content-addressed excerpts only; never original full pages or private source data.
- **Evidence/verification and operations:** private SQLite transaction/checkpoint ledger and immutable receipts; explicit isolated root; symlink and known production-store roots rejected.
- **Canonical intelligence:** existing Evidence/Observation, SemanticTwin and Blueprint owners unchanged. Candidate adaptation exposes `eligible_conclusion=False`; no promotion API called.
- **Derived index/visual state:** reconstructable from active candidates, not a source of truth. Dependency edges are operational lineage, not a competing knowledge graph.
- **Public research release:** versioned source-controlled projection with exact hashes; existing history guard preserves every old source byte and accepts only the five specifically pinned additions. The prior exact inventory assertion is explicitly extended 160→165; it is not disabled.
- **Private boundary:** v1 supports `shared_public` programmes only. Tenant-private acquisition/publication is rejected, not mixed with shared research. The public view has no operational DB/cache/log reader or write form.

Withdrawal traverses bounded dependency edges and invalidates relationships, hypotheses, indexes and visuals; a new release excludes the withdrawn claim. Earlier payloads/releases remain immutable. Supersession requires an active same-label candidate and cannot silently swap subsidiaries; this is still not legal-entity identity proof. Corrections may invalidate a stopped job's evidence for safety, while cancellation blocks further acquisition, assurance, release and rebuild. See the **explicitly synthetic** [correction drill](Correction-Drill.json); no real provider fact was withdrawn. Updating a public snapshot after a real correction requires a versioned reviewed code delta; no running production instance is mutated automatically.

## Visual walkthrough and limitations

1. Industries → UK Technology.
2. Select a category; green indicates an acquired cohort, amber a coverage gap. These lines describe taxonomy, not enterprise relationships.
3. Provider baseline → inspect the distinct Advania catalogue identity and unresolved business-model scope.
4. Evidence & assurance → five exact excerpts, dated receipts, source links, hashes and licensing.
5. Gaps & next actions → comparable baseline requirements and population expansion work.

[Desktop](previews/programme-desktop.png) · [Tablet](previews/programme-tablet.png) · [Mobile](previews/programme-mobile.png) · [Provider](previews/provider-desktop.png) · [Before](previews/before-industries-desktop.png) / [After](previews/after-industries-desktop.png).

Actual Chromium/Playwright checks cover navigation, all four views, category interaction, five evidence cards, 16 gap/action rows, desktop keyboard activation and no horizontal overflow at 1440/1024/390 widths. Mobile uses equivalent category controls. No JavaScript exceptions were observed. The evidence print PDF was generated locally; extracted text retains source hashes/receipts (not a formal PDF accessibility certification). This is engineering validation, not owner usability acceptance.

Remaining work: licensed acquisition adapters, complete population discovery and comparable provider baselines; independent semantic verification with explicit rights; meaningful contrary-source/arithmetic/entity verification beyond literal catalogue fields; enrich/monitor/reconcile runners; authorized canonical-promotion integration; private research isolation if required. These are explicit next increments, not represented as delivered autonomous research depth.
