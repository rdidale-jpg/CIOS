# LVIR-1 · Lloyds visual intelligence recovery

Implementation based on main `2757e459f90fc4e1156180acf5f7ed9a40c292d9`. The design reference is the reviewed diagnostic at `c5e7bf0f10fa14e95f5a6b0031ab88fe2b17676b`. Its branch is independent. The original art, compact and wide Left, Top, public Lloyds identity, link structure and reading controls remain under their current owners. [Diagnostic #695](https://github.com/rdidale-jpg/CIOS/pull/695) · [VP-1 #631](https://github.com/rdidale-jpg/CIOS/pull/631) · [Experience Contract](../../product/flora-experience/FLORA-Experience-Contract-v1.0.md)

## Before and after

Baseline captures are from the approved release checkout. Candidate captures use the same local application entry point in an isolated guest profile. The images show scrollable full-page views.

| Perspective | Desktop comparison | iPad portrait | Mobile 390 px |
| --- | --- | --- | --- |
| Landscape | [Before](previews/before-landscape-facts-desktop.jpg) · [Facts](previews/after-landscape-facts-desktop.jpg) · [Insight](previews/after-landscape-insight-desktop.jpg) | [Before](previews/before-landscape-facts-ipad-portrait.jpg) · [Facts](previews/after-landscape-facts-ipad-portrait.jpg) · [Insight](previews/after-landscape-insight-ipad-portrait.jpg) | [Before](previews/before-landscape-facts-mobile.jpg) · [Facts](previews/after-landscape-facts-mobile.jpg) · [Insight](previews/after-landscape-insight-mobile.jpg) |
| Inside | [Before](previews/before-inside-facts-desktop.jpg) · [Facts](previews/after-inside-facts-desktop.jpg) · [Insight](previews/after-inside-insight-desktop.jpg) | [Before](previews/before-inside-facts-ipad-portrait.jpg) · [Facts](previews/after-inside-facts-ipad-portrait.jpg) · [Insight](previews/after-inside-insight-ipad-portrait.jpg) | [Before](previews/before-inside-facts-mobile.jpg) · [Facts](previews/after-inside-facts-mobile.jpg) · [Insight](previews/after-inside-insight-mobile.jpg) |
| Forces | [Before](previews/before-forces-facts-desktop.jpg) · [Facts](previews/after-forces-facts-desktop.jpg) · [Insight](previews/after-forces-insight-desktop.jpg) | [Before](previews/before-forces-facts-ipad-portrait.jpg) · [Facts](previews/after-forces-facts-ipad-portrait.jpg) · [Insight](previews/after-forces-insight-ipad-portrait.jpg) | [Before](previews/before-forces-facts-mobile.jpg) · [Facts](previews/after-forces-facts-mobile.jpg) · [Insight](previews/after-forces-insight-mobile.jpg) |

## Source-to-view map

| Surface | Eligible owner input | Classification and limits |
| --- | --- | --- |
| Funding | `LBG-Q326-DEPOSITS` / `PR-LBG-Q326`, `LBG-AR25-DEPOSITS` / `PR-LBG-AR25` | Reported consolidated Group stocks, £502.8bn at 30 September 2026 and £496.5bn at 31 December 2025. Existing funding-base comparison remains an eligible difference between stocks. |
| Earnings | `LBG-Q326-PROFIT` / `PR-LBG-Q326` | Reported £6.6bn Group statutory pretax profit for the nine months to 30 September 2026. The conceptual system does not reconcile these stocks to earnings. Spread, risk and capital are explanatory mechanisms. |
| Landscape service context | Existing service-recovery public agenda projection | Separate regulated Lloyds Bank plc perimeter. The service observation does not establish Group economics or the selected Inside workflow. |
| Inside | `LBG-ENVOY-CONTROLS` / `PR-LBG-ENVOY` | The Group’s reported controls sit in a separate example. Every matrix relationship is conceptual. Contract, workflow use, accountable role, system allocation and operating effects are unverified. |
| Forces | `UK-RATE-NOV26` / `PR-BOE-NOV26`, `LBG-A2030-CIR` / `PR-LBG-A2030`, same Group profit claim | UK policy is industry context. The Group ambition is offered separately and carries its original measurement state. No link establishes a Lloyds-specific response or effect. The conditional branches are conceptual. |

The assessment and document rights stay in the existing Banking overlay and public claim renderer. Measures are emitted only when the eligible claim matches entity, date, measurement state and unit. No forecast, candidate research, quantified business-line economics, actual workflow or vendor assignment was introduced. Relevant residual gaps include repricing by term, credit mix, actual control effectiveness and responsibility. ADR-026 qualification remains outside this view. [Assessment overlay](../../../enterprise-knowledge/banking/research-model/Assessment-Overlay.json) · [ADR-026](../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md)

## Commercial comprehension and review

Three review prompts for an experienced Sales Director.

1. Explain which funding and profit figures are reported, why they are not a financial bridge and what would determine the direction of spread.
2. Select one capability and explain how it could be shared across credit and customer service. Identify what the separate Envoy disclosure establishes.
3. Trace funding repricing through income and efficiency. Identify what Lloyds-specific evidence would establish a response.

The implementation review traced those prompts to the visuals and both reading modes. No independent Sales Director or design panel was available. Owner visual and commercial acceptance remains open. The current scope favours a few mechanisms that can be explained with the available evidence.

## Changed surfaces and rollback

`lloyds_recovery.py` and its scoped CSS own composition. The existing visual shell selects the three Lloyds views. The existing selector allowlist adds four Inside capability details; historical drill-throughs remain available. The updated experience tests cover mode and scope, Envoy separation and withdrawal, and policy withdrawal. The browser evidence compares adjacent public output with the release checkout.

Revert the bounded PR to restore the prior Main compositions and remove the four new capability selectors. No data or deployment migration is required. Any deployment or rollback in production requires separate owner approval.

## Browser checks

Chromium rendered 60 before/after views at desktop, iPad landscape and portrait, and 390px/320px phones. Native links preserved capability and reading mode through direct navigation, reload and Back/Forward, with JavaScript disabled. Focus, keyboard activation, emulated touch, 200% CSS zoom, text-only enlargement at all five viewport sizes, horizontal reflow, and printed Main text passed. Adjacent guest response status and body text matched the baseline across the sampled UK, Banking, cohort, Aviation, easyJet, Technology and Pipeline paths. Native Safari, hardware touch and an authenticated visual session were outside this browser comparison. [Browser results](browser-results.json)

The historical owner-compatibility check uses exact pins for the two changed presentation entry points and their existing predecessor. Unexpected edits still fail that check. No regression exceptions or security baselines changed.
