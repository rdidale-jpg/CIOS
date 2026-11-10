# FLORA Visual Intelligence v2 — Living Industry Maps

Banking and Aviation now use illustrated operating systems rather than a skyline/runway above a participant-card grid. Activities, participants and conceptual flows are selectable. A single inspection area reveals relevant context; the secondary research remains in **03 / Investigate**. Enterprise operating models, six original diagrams, research history and authorised Pipeline controls remain intact.

## Evaluate the maps

| Industry | Existing route | Desktop | Landscape tablet |
| --- | --- | --- | --- |
| UK Banking | `/industries/banking` | [Map](previews/banking-desktop.png) | [Map](previews/banking-tablet.png) |
| Commercial Aviation | `/industries/aviation` | [Map](previews/aviation-desktop.png) | [Map](previews/aviation-tablet.png) |

Choose an illustrated activity, participant or dashed arrow. Inspect the selected panel, follow its scoped evidence, or open Lloyds/easyJet. **AI disruption** highlights potentially affected activities; **Regulation & resilience** shows conceptual exposure to investigate. Neither overlay asserts adoption, harm, readiness or enterprise failure. Dated context links to the existing strategic timeline.

- Banking: customers → funding → lending/payments, with credit/control, resilience and data/platform support. [Inspection example](previews/banking-inspection.png).
- Aviation: passenger/booking → schedule → aircraft/crew → airports/flights → recovery/outcome, with maintenance, fuel, data and regulatory roles. [Inspection example](previews/aviation-inspection.png).
- AI lenses: [Banking](previews/banking-ai-disruption-desktop.png), [Aviation](previews/aviation-ai-disruption-desktop.png).
- Regulatory lenses: [Banking](previews/banking-regulation-tablet.png), [Aviation](previews/aviation-regulation-tablet.png).

The map has internal panning and an explicit larger-scale view. Full names remain in accessible labels and text navigation where visual labels are shortened. Enter selects and focuses the inspection summary. Narrow screens provide equivalent text navigation. Native disclosures remain usable without JavaScript; unavailable enhancement controls stay hidden.

## Before and after

Matched 1440 × 1080 browser viewports on verified v1 main and v2; local disposable data directories, no identities or application demo records created.

| Industry | V1 | V2 |
| --- | --- | --- |
| Banking | [Before](previews/banking-before.png) | [After](previews/banking-after.png) |
| Aviation | [Before](previews/aviation-before.png) | [After](previews/aviation-after.png) |

V2 adds spatial business roles, recognisable operating assets, labelled money/passenger/resource/control flows, integrated scale, selective exposure lenses and contextual disclosure. Large lists remain available in supporting research. Browser geometry is recorded in [Browser checks](Browser-Checks.json); this is layout evidence, not a measured comprehension gain. See the [unmeasured v1/v2 evaluation protocol](Comprehension-Evaluation.md).

## Architecture and research reuse

The [pre-implementation assessment and design](Design-and-Reuse.md) inventories the existing architecture. `living_map_specs` derives the map from `visual_intelligence_specs`, the existing assessment overlay, v3 support/relationship reviews and a presentation-only `Living-Map.json` per industry. `living_map` reuses v1 SVG glyphs, evidence rendering, semantic states and native interaction patterns. There is no new graph database, frontend framework, Evidence store or canonical object family.

Input digests cover the assessment, review and complete presentation mapping. The validator compares the full derived output, including metric, relationship, scope and identity changes. Research changes update the visual projection; a changed reviewed relationship changes its marker without a drawing-code edit. Generic new supplier records remain research context, not automatic incumbency. Artwork size is not enterprise influence; equal participant typography and shortened names are navigation treatments, not measured ranking.

All arrows in the operating illustration are **conceptual industry flows**. The square supplier marker denotes only a dated source-supported reference-company relationship. In Aviation, easyJet’s S.FP+ relationship retains **November 2023**, missing current term/workshare/value, and a link to the v3 assertion. It does not prove industry-wide use, current exclusivity or a specific activity implementation. Contradicted Lloyds platform/estate findings remain visible, not erased.

## Scale evidence and boundaries

A bounded primary-source check used the official [Bank of England 2026 Q2 release](https://www.bankofengland.co.uk/statistics/banking-sector-regulatory-capital/2026/2026-q2), published **30 September 2026**. One located excerpt was appended to the existing Banking v3 candidate review using existing CandidateClaim, SourceSegment and observation-fingerprint contracts. Original review records and source files are retained byte-for-byte; no finding is canonically accepted or promoted.

The Banking map reports **GBP3,118 billion risk-weighted assets**, total UK banking sector, Q2 2026, transitional regulatory-capital dataset. This is **not total assets, market value, revenue or GVA**, and is not a Lloyds balance-sheet value. Evidence remains a reviewed excerpt, not a downloaded original or independent human verification. The source hash, locator, publication/retrieval dates and candidate status are inspectable through the existing understanding/evidence route.

Aviation retains **302 million airport passenger journeys**, UK and Crown Dependency airports, calendar 2025; these are not unique people. The official [CAA release](https://www.caa.co.uk/newsroom/news/uk-aviation-officially-breaks-records-with-over-300m-passenger-journeys-in-2025/) was rechecked. Its existing source identity/history was not overwritten. The separate global revenue forecast remains in supporting research and is not compared with UK journeys or used to size airline labels.

Unresolved: banking-only employment/GVA, comparable current market shares, named AI-native entrants, many specific providers, supplier current terms and industry-wide deployment/readiness. Broader financial-services employment/GVA was found but deliberately not presented as Banking-only evidence. No budgets, buying intent, procurement dates, contract expiries or AI displacement dates were manufactured.

## Browser and print verification

[Browser checks](Browser-Checks.json) record 18 industry/lens/viewport combinations: desktop 1440 × 1080, landscape tablet 1180 × 820 and narrow 390 × 844; all 54 activity keyboard selections, single-panel state, real evidence/enterprise/timeline navigation, internal zoom/panning, flow selection, reduced motion, no-JS fallback and zero console errors.

Print is tested **separately**. A3 portrait fits the whole vector map and all nine activity labels on page one even when larger-scale browser zoom was selected. Source context prints on later pages; print restores the original browser disclosure state. [Print checks](Print-Checks.json), [Banking PDF](previews/banking-print.pdf), [Aviation PDF](previews/aviation-print.pdf), [Banking first-page preview](previews/banking-print-page1.png), [Aviation first-page preview](previews/aviation-print-page1.png). Each full PDF includes 23 pages of public contextual/supporting research; it is an evidence appendix, not a one-page marketing handout. No user-supplied PDF files accompanied this brief, so no claim is made to have inspected those specific captures.

Functional regression: **29 new map tests passed** and **91 existing visual/unified/multi-industry/understanding tests passed**. CI-policy: **25 passed**; actionlint passed. The strict baseline adds only the 29 passing identities; prior expected outcomes, inherited signatures and original skip reasons are unchanged. The full local gate **passed: 1,113 passed, 57 signature-matched inherited failures and 10 original skips (1,180 exact identities)**, including **388 strict security** and **29 new map** passes. The inherited breakdown remains 21 domain + 12 financial diagnostic + 24 historical legacy failures. No new/changed failure or unexpected skip was accepted. Hosted acceptance is verified separately on the published PR candidate; local results are not substituted for GitHub execution.

## Limitations and next increment

Human comprehension remains **unmeasured**. Desktop/tablet automation uses Chromium; physical iPad/Safari and assistive-technology usability remain untested. Provider completeness, role-specific evidence and verified current system dependencies remain uneven. Generic activities and pressure statements are interpretation even where reference-company evidence illustrates them. No production data, settings, account provisioning, Pipeline qualification or deployment occurred.

Next: owner evaluation plus the short counterbalanced comprehension study; verify activity-level supplier/system roles, current contract scope and directly comparable industry economic measures before adding factual edges or proportional actor sizing. No new industry or research architecture is needed.
