# LVIR-2 · Interactive Lloyds Landscape

Baseline for the implementation and captures is the reviewed PR #696 head `c0de14246589f9a23456a58aaf4e56e703f39518`. Fetched main was `2757e459f90fc4e1156180acf5f7ed9a40c292d9`. The experience builds on the accepted comprehension direction, the original visual shell and the two reading modes. [LVIR-1 review pack](../owner-review/README.md) · [Experience Contract](../../../product/flora-experience/FLORA-Experience-Contract-v1.0.md) · [VP-1 #631](https://github.com/rdidale-jpg/CIOS/pull/631)

## What changed

- **Understand.** The opening connects three selectable parts of a conceptual bank model. Funding supports lending and other earning activities. Interest and fees create income. Funding costs, operating costs and credit losses reduce profit. No arrow connects a reported deposit balance directly to reported profit.
- **Explore.** The chosen object and path in the model are highlighted. One panel brings the mechanism, available Group evidence and one question into view. Facts starts on Funding. The same finite selection persists across Facts, FLORA Insight, direct links, reload and history. A regular server-rendered link works without JavaScript.
- **Investigate.** Follow the existing financial analysis link for reporting basis, or the separately scoped Lloyds Bank plc service evidence link. The two deposit dates remain identifiable as balances. The difference between them only renders when both inputs and the existing calculated statement are eligible.

## Evidence and commercial questions

| Selection | Source and exact scope | What a salesperson can investigate |
| --- | --- | --- |
| Funding | `LBG-Q326-DEPOSITS`, `PR-LBG-Q326`. £502.8bn Group customer deposits at 30 September 2026. The £496.5bn comparison is the 31 December 2025 Group balance from `LBG-AR25-DEPOSITS`, `PR-LBG-AR25`. | What share of deposits earns interest, and how quickly are the rates paid changing? A similar balance can cost more if its mix changes. These figures give no deposit mix or rate. |
| Lending & income | `LBG-Q326-PROFIT`, `PR-LBG-Q326`. £6.6bn consolidated Group statutory pretax profit for nine months to 30 September 2026. This is Group context. The eligible figures used here give no lending income, yield or loan-rate split. | How much lending changes rate within a year, and how does interest on it compare with funding cost? Fixed-rate and variable-rate loans respond at different speeds. |
| Profit & costs | Same reported Group total. No operating cost or impairment allocation follows from it. | How much of the change in profit came from interest, operating costs or expected loan losses? Rising profit drivers can be offset by higher expenses or losses. |

The renderer reuses the public claim view, exact unit, period and Group checks, existing funding comparison, and existing eligibility and source owners. Withdrawal removes the dependent measure, comparison and its investigation prompt. General mechanisms remain explicitly conceptual. No candidate research or future commercial state is admitted. [Assessment overlay](../../../../enterprise-knowledge/banking/research-model/Assessment-Overlay.json) · [Interpretation boundary](../../../../architecture/decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md) · [Material Pressure ownership](../../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md)

## Visual comparison

| Viewport | Reviewed head | Funding | Lending & income | Profit & costs |
| --- | --- | --- | --- | --- |
| iPad portrait | [Before](before-facts-ipad-portrait.jpg) | [Facts](after-funding-facts-ipad-portrait.jpg) · [Insight](after-funding-insight-ipad-portrait.jpg) | [Facts](after-lending-income-facts-ipad-portrait.jpg) · [Insight](after-lending-income-insight-ipad-portrait.jpg) | [Facts](after-profit-costs-facts-ipad-portrait.jpg) · [Insight](after-profit-costs-insight-ipad-portrait.jpg) |
| iPad landscape | [Before](before-facts-ipad-landscape.jpg) | [Facts](after-funding-facts-ipad-landscape.jpg) · [Insight](after-funding-insight-ipad-landscape.jpg) | [Facts](after-lending-income-facts-ipad-landscape.jpg) · [Insight](after-lending-income-insight-ipad-landscape.jpg) | [Facts](after-profit-costs-facts-ipad-landscape.jpg) · [Insight](after-profit-costs-insight-ipad-landscape.jpg) |
| Mobile 390 px | | [Facts](after-funding-facts-mobile.jpg) · [Insight](after-funding-insight-mobile.jpg) | | |

The walkthrough assessed whether the model answers the opening question before the measures, whether an observer can identify the active object and whether each prompt leads to a specific missing measure. Lending is the weakest evidence view because Group profit supplies context rather than a lending measure. The ten-second target still needs a timed test with a non-specialist. No independent participant review, native Safari or hardware touch test was available.

## Validation and rollback

[Browser results](browser-results.json) record the five viewport sizes, component and mode states, keyboard, emulated touch, no JavaScript, history, direct navigation, 200% text, print/PDF and adjacent route parity. Existing evidence and rights tests also apply. The change is limited to the Lloyds Landscape composition and CSS, the existing detail allowlist and dispatch, tests, presentation lineage pins, and this review evidence. Revert the LVIR-2 commit to restore the reviewed LVIR-1 head's behaviour. No data migration is needed.
