# FLORA UX refinement — Issue #573

Implements the owner's 13 November 2026 display contract over the Technology experience released in `854a783b3c5f83d6ee3604f49a76772529b7339a`. This branch is for owner review: **no merge or deployment**.

## Delivered stages

1. **Illustrated industry navigation.** The existing approved artwork stays embedded as a local WebP asset. All eight district names are visible on desktop/iPad. On phones, numbered image pins pair with an always-visible two-column name key; each remains a native link with a 44px minimum target. Selecting a district opens its comparison directly. Primary navigation stays small; source/governance tools remain secondary.
2. **Participant comparison.** Every district uses a compact sortable table: participant, UK revenue, UK workforce, role, specialty and commercial signal. The all-participant view preserves the existing population of 80 views. Native links sort by number/text, with blank values last in either direction; search, sticky participant names and an independently scrollable table support smaller screens. Metrics open their period, scope, exact value, basis and sources on request. A real estimate must show **EST** and carry a source, dated basis and uncertainty range. This dataset uses sourced UK figures or blanks; it does not manufacture UK estimates to fill the table.
3. **Enterprise intelligence, starting with NVIDIA.** Financial context, strategy, pressures, deployment users, partners, suppliers, UK programmes and three evidence-backed opportunity hypotheses replace the oversized diagram. Global group financials and the reviewed quarterly update show their period and currency explicitly. Opportunity development reveals buyer scope, observed basis, qualification questions, an alternative explanation and macro-theme links. Pipeline navigation inherits the enterprise scope, while opportunity creation remains an explicit browser-preview action.

NVIDIA is the first fully enriched profile. Equinix retains its sourced financial drill; Computacenter has sourced UK operating context; other participant links reuse the available public research rather than fabricated enterprise detail. Comparison coverage is intentionally sparse: one participant currently has reviewed comparable UK revenue and workforce metrics; blank cells are deliberate.

## Acceptance walkthrough

Entry: `/industries/technology/experience`.

1. On desktop/iPad, confirm all eight names are visible without hovering. On a phone, confirm eight pins and the eight-name key fit the arrival experience. Tab to a district and press Enter.
2. Select **AI & data**. Inspect the participant rows, then sort **Participant** ascending/descending. NVIDIA's UK revenue and workforce cells remain blank.
3. Open **NVIDIA**. Read the global FY2026 financial context and separate Q2 FY2027 update. Select a financial figure to open report detail, then inspect a source on request.
4. Read strategy and pressures. Inspect **Customers & deployed use**, **Partners** and **Suppliers**: the roles and event dates differ deliberately. Named deployment users are not inferred to be direct contracting customers. Anonymous concentration figures are not mapped to named firms.
5. Inspect the **$250m UK programme**: it is an announced five-year compute-access donation, not UK sales or completed expenditure.
6. Open **Develop this opportunity** under a hypothesis. Check the observed basis, buyer scope, next conversation and alternative explanation. Source links and existing macro categories remain accessible.
7. Open **Pipeline**. It is scoped to NVIDIA and starts without a seeded NVIDIA opportunity. Add an **illustrative** opportunity explicitly; edit its value, dates, owner and next action; reload. No live Pipeline record is created. A fresh browser context cannot retrieve the tab's preview.
8. Return to **Channels & distribution**. Computacenter shows £1.419bn rounded UK segment revenue and 4,357 average monthly UK segment employees, both FY2025. Open the cells to inspect the exact value and basis. Sort UK revenue in either direction; blanks remain last.
9. Revisit Banking, Aviation, Lloyds, easyJet and Macro using their existing routes. Their presentation and live-Pipeline destinations remain unchanged. See [Parity audit](Parity-Audit.md) for actual gaps and follow-up recommendations.

## Before/after gallery

Before images show the released Technology experience: unlabelled arrival, AI district with a large illustration/list, and the then-current generic enterprise screen (Equinix). After images show labelled arrival, participant comparison and the first enriched NVIDIA profile. Enterprise images compare presentation patterns, not the same company or accounting scope.

| View | Desktop | iPad landscape | iPad portrait | Mobile |
| --- | --- | --- | --- | --- |
| Industry before | [View](previews/before-industry-desktop.png) | [View](previews/before-industry-ipad-landscape.png) | [View](previews/before-industry-ipad-portrait.png) | [View](previews/before-industry-mobile.png) |
| Industry after | [View](previews/after-industry-desktop.png) | [View](previews/after-industry-ipad-landscape.png) | [View](previews/after-industry-ipad-portrait.png) | [View](previews/after-industry-mobile.png) |
| District before | [View](previews/before-comparison-desktop.png) | [View](previews/before-comparison-ipad-landscape.png) | [View](previews/before-comparison-ipad-portrait.png) | [View](previews/before-comparison-mobile.png) |
| Comparison after | [View](previews/after-comparison-desktop.png) | [View](previews/after-comparison-ipad-landscape.png) | [View](previews/after-comparison-ipad-portrait.png) | [View](previews/after-comparison-mobile.png) |
| Enterprise before | [View](previews/before-enterprise-desktop.png) | [View](previews/before-enterprise-ipad-landscape.png) | [View](previews/before-enterprise-ipad-portrait.png) | [View](previews/before-enterprise-mobile.png) |
| NVIDIA overview | [View](previews/after-nvidia-overview-desktop.png) | [View](previews/after-nvidia-overview-ipad-landscape.png) | [View](previews/after-nvidia-overview-ipad-portrait.png) | [View](previews/after-nvidia-overview-mobile.png) |
| Full NVIDIA profile | [View](previews/after-nvidia-desktop.png) | [View](previews/after-nvidia-ipad-landscape.png) | [View](previews/after-nvidia-ipad-portrait.png) | [View](previews/after-nvidia-mobile.png) |
| Opportunity hypotheses | [View](previews/after-opportunities-desktop.png) | [View](previews/after-opportunities-ipad-landscape.png) | [View](previews/after-opportunities-ipad-portrait.png) | [View](previews/after-opportunities-mobile.png) |
| Sourced UK metrics | [View](previews/after-uk-metrics-desktop.png) | [View](previews/after-uk-metrics-ipad-landscape.png) | [View](previews/after-uk-metrics-ipad-portrait.png) | [View](previews/after-uk-metrics-mobile.png) |

## Implementation and governance

`technology_commercial.py` is a read-only projection of the existing foundation plus hash-pinned `Commercial-Views.json`. Source passages retain URL, period, locator, review date, rights and acceptance metadata. Its inspection adapter reuses existing `SourceSegment`, `CandidateClaim` and `EvidencePackageItem` contracts: candidates remain withheld, identities stay unbound internally, publisher-original hashes remain absent and eligible imports remain zero. There is no new evidence store, review ledger, collector, model client or promotion path.

The foundation JSON, original handoff, canonical registry, source importer, review/promotion, security/access and live-Pipeline owners are unchanged. Presentation associations allow data-centre participants in the Cloud & data centres comparison without rewriting foundation memberships. All new selectors resolve only finite existing participant keys; they do not look up arbitrary enterprise/private IDs. Unknown/duplicate/privileged selectors remain rejected.

The UI omits unavailable values and keeps normal research diagnostics in specialist/source views. Operational failures, expired access, unavailable opportunities and blocked browser storage still show actionable messages. Hypotheses are visibly labelled. Demo entries are visibly illustrative; browser editing stays in `sessionStorage`, uses escaped text, and makes no network write. Existing live Pipeline authentication, qualification and persistence are untouched.

[Source review and measurement scope](Source-Review.md) · [Validation](Validation.json) · [Source manifest](Source-Manifest.json) · [Browser results](previews/Browser-Results.json)

## Reproduce checks

```sh
python -m pytest tests/test_flora_ux_refinement_573.py tests/test_flora_technology_owner_journey.py tests/test_flora_technology_foundation.py tests/test_flora_technology_visual_world.py -q
python -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --output /absolute/scratch/new-ci-output
node tools/research/check_flora_ux_573.cjs http://127.0.0.1:8796 /absolute/scratch/new-browser-output http://127.0.0.1:8795
```

The browser command expects an isolated candidate service and an isolated baseline checkout at `854a783`, with separate scratch data directories. It never targets a hosted service. The workflow adds the new focused tests alongside the existing owner-journey step; security discovery, regression comparator and inherited exceptions are unchanged.

Physical iPad/Safari and screen-reader user testing remain acceptance tasks. Chromium viewport/keyboard checks do not establish human comprehension, factual independence or commercial qualification. No merge or deployment is performed by this sprint.
