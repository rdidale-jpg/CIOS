# Lloyds Enterprise Twin 2.0

## What was reconciled

| Cut | Direct observation |
| --- | --- |
| Live Render | Public deployment metadata reported `6af7ef0afeb8e8ad4059fbb27460add7f80d4ec1`. The public Lloyds Landscape returned the funding-to-earnings composition and Inside returned the credit/service matrix. The flagship link was absent. |
| GitHub main | Same commit SHA. A loopback render reproduced both views. `render.yaml` describes the `flora` Python service and pilot configuration. Render’s private service settings, deployment history and auto-deploy policy were outside the public evidence. |
| Draft #710 | `e66ace2fefd66f1db27bc467f4b394c05eb1fc5f`. A dedicated Lloyds Landscape detail already contained the governed source checks, segmented analysis, legal-bank peer data and connected issue. Its first screen was predominantly prose and disclosures. |
| This draft | Keeps the #710 detail and its reading and evidence owners. Adds a visual picture of the three reporting segments, a compact set of operating touchpoints and a highlighted core-renewal path. No route, artwork, financial contract or source permission changes. |

[Render deployment metadata](https://flora-current.onrender.com/deployment) · [Live Lloyds entry](https://flora-current.onrender.com/enterprises/lloyds) · [Predecessor draft](https://github.com/rdidale-jpg/CIOS/pull/710)

## Try the prototype

From the candidate checkout with the repo’s Python requirements installed, run the normal local Flora application:

```sh
FLORA_ENVIRONMENT=development FLORA_AUTH_PROVIDER=local FLORA_DATA_DIR="$(mktemp -d)" FLORA_HOST=127.0.0.1 PORT=8000 python -m cios.applications.flora.web.app
```

Open `http://127.0.0.1:8000/enterprises/lloyds?stream=landscape&detail=flagship` or select **Explore the Lloyds flagship** on the Lloyds Landscape. From **Inside Lloyds**, inspect the branch, platform or AI examples and follow their existing detail links. In **FLORA Insight**, choose **Core renewal**, then follow **Operations**, **Technology**, **Pressure**, **Strategy** or **Economics**. Back restores the prototype. Open **Perspectives** for the supporting evidence, caveats and alternatives.

## Evidence and scope

| Visible component | Evidence and treatment |
| --- | --- |
| Retail, Commercial Banking, Insurance, Pensions & Investments | Reporting names independently checked against the issuer-filed FY2025 Form 20-F, segment reporting, SEC filer CIK 1160106 and accession 0001160106‑26‑000010. Customer descriptions and products orient the reader. The economic drivers are explicitly illustrative. Cards do not encode segment size or imply internal ownership. No filing content, financial cells or direct PDF links added to the runtime. |
| Branch service, platform renewal, AI controls | Existing verified Lloyds Source owners `PR-LBG-BRAND26`, `PR-LBG-AR25`, `PR-LBG-ENVOY`. Matched claims are rechecked on each render. Board accountability, internal hand-offs, cloud workshare and independent control effectiveness remain unverified. |
| Core renewal, efficiency and pressure | Existing `PR-LBG-A2030`, with the cost-to-income ambition and platform priority, plus the migration and control sources and `PR-PRA-PS726`. The highlighted path joins related evidence and never asserts causal delivery or Lloyds non-compliance. Options retain counterarguments. No new qualified Material Pressure was created. |
| SWOT, risks, competition, benchmarks and timeline | All #710 analyses remain available with the same evidence and uncertainty. Peer counts are FCA same-period legal-bank service activity, with mixed customer/product denominators. HM Treasury’s 2024 policy and the AI-assistant scenario remain separate. No verified named AI-native entrant launch, Lloyds pilot participation, ranking or seller opportunity is implied. |

[SEC filing index](https://data.sec.gov/submissions/CIK0001160106.json) · [FY2025 original statutory filing](https://www.sec.gov/Archives/edgar/data/1160106/000116010626000010/lyg-20251231_d2.htm) · [Inherited evidence register and restrictions](../lloyds-flagship/README.md)

## Comparison and browser evidence

| Capture | Desktop | iPad landscape | iPad portrait |
| --- | --- | --- | --- |
| Main | [Desktop](previews/main-desktop.jpg) | [Landscape](previews/main-ipad-landscape.jpg) | [Portrait](previews/main-ipad-portrait.jpg) |
| #710 | [Desktop](previews/710-desktop.jpg) | [Landscape](previews/710-ipad-landscape.jpg) | [Portrait](previews/710-ipad-portrait.jpg) |
| New Landscape | [Desktop](previews/after-desktop.jpg) | [Landscape](previews/after-ipad-landscape.jpg) | [Portrait](previews/after-ipad-portrait.jpg) |
| Inside Lloyds | [Desktop](previews/inside-desktop.jpg) | [Landscape](previews/inside-ipad-landscape.jpg) | [Portrait](previews/inside-ipad-portrait.jpg) |
| Connected issue · Insight | [Desktop](previews/insight-desktop.jpg) | [Landscape](previews/insight-ipad-landscape.jpg) | [Portrait](previews/insight-ipad-portrait.jpg) |

[Harness](browser.py) · [Main observations](previews/main.json) · [#710 observations](previews/710.json) · [Candidate observations](previews/after.json). Screenshots use loopback Chromium and simulated iPad dimensions and touch. The candidate runtime commit differs from the PR head only in the review pack. Physical iPad, Safari and assistive-technology acceptance remain open.

## Visual critique and limits

The first screen gives Lloyds a recognisable commercial shape. Reporting segments have equal-weight cards, while the core-renewal links provide a second path through the same enterprise. The accepted artwork in the scene rail gives geographic context and the separate accepted interior crop supports the product view. The prototype can explain why renewal matters before the reader opens the evidence. It still requires a click from the accepted arrival and retains the existing scene navigation alongside the shorter in-page jumps. Some users may benefit from consolidating those paths after visual acceptance.

Operating examples connect to existing pages whose detail can still be more generic than the prototype. Particular systems, supplier contracts, segment contribution, customer outcomes and comparisons with properly matched denominators need additional governed evidence. The dual-control design question remains separate. Lloyds §2 stays inactive where required, §5 direct PDF links stay deferred, and ADR‑027 remains Proposed. Existing Financial, Source, Evidence acceptance, permissions, canonical records and Pipeline remain under their existing owners.
