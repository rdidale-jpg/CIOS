# FLORA Visual Intelligence v1

The existing Industry and Enterprise pages now provide illustrated, evidence-linked introductions for Banking/Lloyds and Aviation/easyJet. They retain the five product navigation entries, six original SVG contracts and canonical research/evidence destinations.

## Try the six flagship views

| View | Existing application destination | Desktop | Landscape tablet |
| --- | --- | --- | --- |
| Banking Signature Landscape | `/industries/banking` | [Preview](previews/banking-landscape-desktop.png) | [Preview](previews/banking-landscape-tablet.png) |
| Aviation Signature Landscape | `/industries/aviation` | [Preview](previews/aviation-landscape-desktop.png) | [Preview](previews/aviation-landscape-tablet.png) |
| How Lloyds works | `/enterprises/lloyds` | [Preview](previews/lloyds-story-desktop.png) | [Preview](previews/lloyds-story-tablet.png) |
| How easyJet works | `/enterprises/easyjet` | [Preview](previews/easyjet-story-desktop.png) | [Preview](previews/easyjet-story-tablet.png) |
| Lloyds strategic timeline | `/enterprises/lloyds?lens=timeline` | [Preview](previews/lloyds-timeline-desktop.png) | [Preview](previews/lloyds-timeline-tablet.png) |
| easyJet strategic timeline | `/enterprises/easyjet?lens=timeline` | [Preview](previews/easyjet-timeline-desktop.png) | [Preview](previews/easyjet-timeline-tablet.png) |

Choose an actor/activity/event to open its disclosure, follow capability or programme links, then **Read the evidence and exact passage**. Keyboard Enter performs the same action and moves focus to the summary. Text navigation duplicates SVG selection; native disclosures remain available with JavaScript disabled. Timeline filters select a year/event meaning without inventing precision; undated items always remain on their separate shelf. Large diagrams pan internally. Narrow screens use the text navigation rather than shrinking labels illegibly.

The optional `?lens=ai-disruption` on either industry reuses the same signature scene. Two scenario cards expose mechanisms, structural defences, capability links and evidence, not named invented AI competitors or a displacement forecast. [Aviation scenario preview](previews/aviation-ai-lens.png).

## Before and after

These are matched 1440 × 1080 browser viewports at the same URLs, using main `5e93023df8b9410fef22a0340095f94530d6e8ad` and the new worktree. No records were seeded and no production service was contacted.

| Page | Before | After |
| --- | --- | --- |
| Banking | [Conventional PESTLE-first page](previews/banking-landscape-before.png) | [Illustrated industry introduction](previews/banking-landscape-after.png) |
| Aviation | [Conventional PESTLE-first page](previews/aviation-landscape-before.png) | [Sector-specific industry introduction](previews/aviation-landscape-after.png) |
| Lloyds | [Capability boxes](previews/lloyds-story-before.png) | [Banking activity model](previews/lloyds-story-after.png) |
| easyJet | [Capability boxes](previews/easyjet-story-before.png) | [Airline operating system](previews/easyjet-story-after.png) |

The change adds recognisable sector artwork, business-purpose disclosure, provenance-aware measures and a seven-lane temporal view. The original PESTLE and capability diagrams remain in expandable sections and the explicit old lenses remain intact. This is a visual comparison, **not evidence of faster executive understanding**; see the [unmeasured evaluation protocol](Comprehension-Evaluation.md).

## Reuse and implementation

See [Design and reuse](Design-and-Reuse.md) for the mandatory pre-implementation inventory and visual grammar. The shared page shell, `visual_specs`, validated Assessment Overlay, v3 `understanding.assess`, existing evidence/source passages and SemanticTwin-backed relationships remain the owners of knowledge. No graph, Evidence store, canonical object model or frontend dependency was introduced.

`visual_intelligence_specs.py` adds three opt-in derived specs. Each pins assessment, v3 review and presentation-profile digests plus an explicit as-of date. `validate_intelligence_specs` compares the complete deterministic derivation, rejecting modified measures, dates, identities or relationship semantics. The existing six-spec JSON route is unchanged. `visual_intelligence.py` contains reusable editable SVG illustrations, HTML disclosures and a small local interaction script; no factual labels or metrics are baked into artwork.

Two `Visual-Profile.json` files contain editorial structure, icons, research selectors and declared conceptual/scenario interpretations. They are **presentation mappings, not canonical findings**. Existing claims and reviews are not rewritten. A newly researched supplier is automatically available as research context. A reviewed status/quotation change affects the derived state/measure; new curated event mappings can resolve an evidenced date without editing rendering code. Missing support keeps measures absent and dates undated. Changed assessment inputs require an explicitly corresponding v3 review, preserving the existing pinned-review boundary.

## Evidence boundaries and limitations

- Equal-sized cards are navigation categories, not rank, spend, influence, market share or a comprehensive industry census. Illustrations do not depict actual enterprise estate layouts.
- Dashed activity arrows express the **conceptual business model**, not verified enterprise topology or causal relationships. The disclosed supplier relationship keeps its own historical period; activity dependency, current contract, exclusivity and workshare remain unknown unless explicitly researched.
- Banking industry market-size/GVA and employment measures are not established. Lloyds deposits and nine-month profit are enterprise measures, not industry scale or customer budgets.
- Aviation revenue is a **global 2026 forecast**; UK/Crown Dependency airport passenger journeys are a different measure/period, not unique people or directly comparable company revenue. easyJet H1 OTP and half-year loss are separate outcomes, not proof of AI contribution.
- A published announcement is dated as **publication, not go-live**. Rollout/strategy ranges retain half-year, quarter or year precision. Industry policy does not prove enterprise applicability, non-compliance or readiness. No contract expiry was inferred.
- Reviewed excerpts are not independently verified enterprise outcomes. Index-only, unavailable and unsupported evidence does not supply numeric measurements. Conflicting estate/platform findings remain visible. No new external research or independent human review occurred in this visual increment.
- AI entrants, displacement, contract value, buying intent and causal benefits remain unverified. Commercial hypotheses stay separate. Pipeline qualification, sessions, workspace authority and private routes are unchanged.
- Desktop/tablet browser coverage is Chromium; Safari/iPad hardware and assistive-technology usability remain untested. Dynamic layout is tested for sparse/dense/missing/competing/unavailable states; comprehension is unmeasured. No production deployment or automatic data promotion occurs.

Next increment: owner evaluation and the short comprehension study; research verified activity-level system/supplier dependencies and dated commercial events before enriching the visuals with factual edges, sizes or additional timeline milestones.

## Verification

Functional suite: `python -m pytest tests/test_flora_visual_intelligence.py -q` — **32 passed**. Existing unified/multi-industry suites: **23 passed**. The strict baseline adds only these 32 expected passing identities; every previously recorded identity, inherited signature and skip reason remains unchanged. Workflow/actionlint and the 25 CI-policy tests are also checked. The full local gate **passed**: **1,084 passed, 57 signature-matched inherited failures, 10 original skips (1,151 exact identities)**, including **388 strict security passes** and the **32 new visual passes**. The inherited breakdown remains 21 domain + 12 financial diagnostics + 24 historical legacy failures. No new/changed failure or unexpected skip was accepted. GitHub-hosted acceptance is separately verified on the published PR candidate; this local result is not substituted for it.

[Browser checks](Browser-Checks.json) record desktop 1440 × 1080, landscape tablet 1180 × 820 and narrow 390 × 844 behaviour, keyboard disclosure, evidence navigation, timeline filtering, reduced-motion configuration, no-JS fallback and console errors. Captures use disposable local stores and public repository research; no identities or synthetic demo records were provisioned.
