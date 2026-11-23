# Four verified changes in existing Flora views

This increment targets main after #717. Merge `f9b939c31dfc4993fe3a59d1e9d05dbe24683226` matches reviewed head `4de8211f1430ba45a8d752797742a31a8abdf044` at the tree level. See the [main check](https://github.com/rdidale-jpg/CIOS/actions/runs/45135219288).

## Reproduce the four proofs

Run from the repository root with the project's test dependencies. The capture command also requires Playwright, Pillow and either system or Playwright-installed Chromium.

```sh
python -m tools.research.verified_factory_proof /tmp/flora-proof-new
CIOS_VERIFIED_ROUTE_OUTPUT=/tmp/flora-proof-routes python -m pytest -q tests/test_flora_verified_factory.py
PYTHONPATH=. python docs/research/initial-factory/verified/browser.py /tmp/flora-proof-routes
```

The first command retrieves the four original HTML articles and the separate Microsoft publication. It matches each record against the existing [discovery proof](../discovery/proof.json), checks the scoped publisher URL, exact date and multiple nearby body-text anchors, then runs the existing Source provenance validator and commercial candidate compiler. It writes candidate Blueprints to a new local directory. It reads no production workspace. An inaccessible, held or changed source can suppress the affected candidate. Raw documents are transient. The [review manifest](lead-review.json) records the factual restatements, locations, review caveats and proposed wording. The [isolated records](isolated-records.json) retain source digests and Microsoft's counterparty confirmation. That file is the recorded live run used for deterministic fixture tests.

The second command stages each candidate Blueprint, records candidate decisions, creates a dry-run plan, approves it and executes using the existing services and test-only workspace authority. A second execution makes no changes. Before and after responses come from existing Flora handlers against the same temporary workspace. The Chromium harness uses those responses, serves repository assets and opens the evidence disclosure with keyboard or simulated touch. It checks viewport overflow. The captures do not represent a deployed environment.

## Evidence assessment

| Enterprise and destination | What the source supports | Corroboration and limit |
| --- | --- | --- |
| Lloyds · Forces | On 18 November 2026 Lloyds described review of complex AI cases by its Data & AI Ethics Committee. | The companion guide is Lloyds material. It establishes the bank's description of oversight. It does not establish how often it is used or whether there is budget for tooling. [Issuer release](https://www.lloydsbankinggroup.com/media/press-releases/2026/lloyds-banking-group/responsible-ai-guide.html) |
| BT · Enterprise Canvas | On 2 November 2026 BT announced completion of its upgrade to the Scottish Wide Area Network. | NHS National Services Scotland independently supports the buyer–supplier relationship. Scottish Government material describes earlier migration schedules. Those scoped dates cannot verify the date or buyer acceptance of the broader completion milestone. The preview attributes completion to BT and makes no claim about being ahead of schedule. [BT release](https://newsroom.bt.com/bt-transforms-scotlands-public-sector-connectivity--upgrading-the-nations-digital-infrastructure/) · [NSS award](https://www.nss.nhs.scot/news/nhs-national-services-scotland-nss-awards-350million-swan-contract-to-bt-for-enhanced-public-sector-connectivity/) · [Scottish Government schedule](https://www.gov.scot/publications/foi-202500493355/) |
| Arm · Technology Enterprise Landscape | On 17 November 2026 the Azure Cobalt 200 announcement described general availability. | Microsoft confirmed availability in its own publication separately from Arm. Microsoft is the service provider. Neither source establishes adoption, measured customer savings or a specific workload and region. [Arm release](https://newsroom.arm.com/news/arm-microsoft-azure-cobalt-200) · [Microsoft Azure announcement](https://azure.microsoft.com/en-us/blog/azure-cobalt-200-vms-now-available-proven-on-real-workloads-and-built-for-the-agentic-era/) |
| easyJet · Inside | On 26 October 2026 easyJet announced a plan to start deploying Starlink in the first half of 2027. | Reuters attributes the timing to easyJet. That coverage verifies the reported announcement and gives no independent confirmation of installation or delivery. [Airline release](https://www.easyjet.com/en/news/airline/story/easyjet-to-offer-connectivity-onboard-for-the-first-time-with-starlink-the-fastest-wi-fi-in-the-sky-with-rapid-roll-out-coming-from-2027) · [Reuters via Euronext](https://live.euronext.com/en/financial-news/easyjet-offer-starlink-internet-onboard-some-flights-2027) |

## Before and after

| Enterprise | Desktop | iPad portrait | iPad landscape |
| --- | --- | --- | --- |
| Lloyds | [Desktop](previews/lloyds-banking-group-plc-route-desktop.jpg) | [Portrait](previews/lloyds-banking-group-plc-route-ipad-portrait.jpg) | [Landscape](previews/lloyds-banking-group-plc-route-ipad-landscape.jpg) |
| BT | [Desktop](previews/bt-group-plc-route-desktop.jpg) | [Portrait](previews/bt-group-plc-route-ipad-portrait.jpg) | [Landscape](previews/bt-group-plc-route-ipad-landscape.jpg) |
| Arm | [Desktop](previews/arm-holdings-plc-route-desktop.jpg) | [Portrait](previews/arm-holdings-plc-route-ipad-portrait.jpg) | [Landscape](previews/arm-holdings-plc-route-ipad-landscape.jpg) |
| easyJet | [Desktop](previews/easyjet-plc-route-desktop.jpg) | [Portrait](previews/easyjet-plc-route-ipad-portrait.jpg) | [Landscape](previews/easyjet-plc-route-ipad-landscape.jpg) |

## Critique and decisions

The commercial distinction between reported complete, available and planned is the most useful part of the proof. Each change ends with a practical question rather than an opportunity. BT could be useful for a service conversation after a reported migration, pending customer confirmation. Arm gives a concrete platform to evaluate, pending workload and regional checks. The Lloyds finding gives an oversight point. It does not identify an owner with buying authority. The easyJet plan gives a timely delivery question. It does not identify open work beside the chosen supplier.

The small change card appears next to existing page headings or reading controls. Its collapsible evidence keeps the primary view short. Approved changes render in explicit slots owned by the Banking/Aviation visual panel, Technology Enterprise view and Enterprise Canvas. The original #716 isolated fallback continues to render its own legacy demonstration records. The new cards remain gated to the development fixture and existing workspace ACL. BT uses Enterprise Canvas. Lloyds Forces still opens a wider economic view alongside this change in oversight context. Physical iPad and Safari acceptance remain open.

The reachable audience in this proof is the authenticated, allowlisted isolated workspace member with the existing Canvas grant. A live audience requires an explicit Source-use decision covering seller display, attribution and withdrawal for each article. The live approver must be an existing account with `candidate.promote` and the proper enterprise/workspace scope under ADR-012, with scoped execution and Canvas access. The live account and workspace grants were not available for verification. The owner must identify them through the existing authority store before any production consideration. Fixture approval does not grant additional authority. Lloyds §2 output and §5 direct PDFs, BT and easyJet issuer-use restrictions, the Financial boundary and Pipeline are unchanged. The Source owner can supply the revision lifecycle file described below. The read-through dependency check removes a withdrawn Source’s Evidence from current projections immediately.

Factory v1.0 remains incomplete. The proof covers four reviewed claims, human-selected body anchors, scoped counterparty confirmation and existing approval under isolated authority. Broader automated extraction, material conflict adjudication, binding to live Source withdrawal, stable native component slots, and operational authorisation remain open. Production research, recurring work and public seller publication stay disabled.


## Source revision withdrawal

The proof reads the Source owner's current revision file beneath the existing Flora data root, at `research_intelligence/document-lifecycle.json`. Its envelope is `{"schema_version":"1.0","revisions":[{"url":"<exact original URL>","sha256":"<exact captured digest>","lifecycle":"current"}]}`. An owner-maintained revision changes lifecycle to `withdrawn` (or stops being current). Only exact, unique, current revision pairs count. An absent, invalid or duplicate state file fails closed. The application exposes no writer or approval endpoint. The fixture supplies the owner state via the existing atomic storage utility. Actual operational delivery must be approved before production use.

Each reviewed commercial Evidence record lists required original revisions, including the Microsoft confirmation for Arm. Withdrawal of either supporting revision suppresses the Evidence and the native card on the next read. An absent or mismatched revision also suppresses both. The stored Evidence and Enterprise Model remain intact for audit. Changing the file does not grant Source reuse or seller publication. Existing unrelated Evidence keeps its established lifecycle path.
