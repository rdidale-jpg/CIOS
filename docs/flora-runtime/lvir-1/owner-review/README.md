# LVIR-1 owner review · Landscape proof

Compared against the rejected PR #696 head `beda24fd30cb27e4550ffc7cf4c69822ce619897`. This correction follows the owner review supplied with the sprint brief. The GitHub PR had no additional comments or formal reviews when checked.

## Presentation standard

| Depth | What the reader should get | How the proof applies it |
| --- | --- | --- |
| Understand | A question, a short visual answer and the scope needed to read it correctly | Follow deposits into lending, interest and profit. The picture is explicitly conceptual. A separate band identifies the Group's reported deposit balance and statutory pretax profit with their dates and bases. |
| Explore | Select a step and learn the business mechanism that changes its outcome | The three map objects jump to funding, lending, or costs and losses. Insight compares what happens when loan and deposit rates change at different speeds, and explains how expected credit losses can offset interest gains. The reading mode retains the Lloyds Group economic subject. |
| Investigate | Open deeper analysis and evidence through their existing owners | The second deposit date and eligible stock comparison sit below the mechanism. The existing financial analysis route carries the reporting basis. Full source and research controls remain within their existing authorised boundary. Legal-bank complaints have an independent service link. |

This is presentation order within Main. Top keeps the accepted perspectives, and Facts and FLORA Insight remain the two reading modes. The original art and Left retain their navigation role. The anchors in the diagram move within the same subject; they create no new route or model. [Experience Contract](../../../product/flora-experience/FLORA-Experience-Contract-v1.0.md) · [VP-1 #631](https://github.com/rdidale-jpg/CIOS/pull/631) · [Accepted evidence boundary](../../../../architecture/decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md)

## Before and after

These are Chromium captures from the reviewed head and the correction at the same emulated viewports. In portrait the opening and reported figures can be read with Left collapsed. Guest access and original artwork are used in both.

| Viewport | Facts | FLORA Insight |
| --- | --- | --- |
| iPad portrait | [Before](before-facts-ipad-portrait.jpg) · [After](after-facts-ipad-portrait.jpg) | [Before](before-insight-ipad-portrait.jpg) · [After](after-insight-ipad-portrait.jpg) |
| iPad landscape | [Before](before-facts-ipad-landscape.jpg) · [After](after-facts-ipad-landscape.jpg) | [Before](before-insight-ipad-landscape.jpg) · [After](after-insight-ipad-landscape.jpg) |
| Mobile | [Facts](after-facts-mobile.jpg) | [FLORA Insight](after-insight-mobile.jpg) |

## Comprehension review

- A non-specialist should be able to explain that deposits help fund loans, loans earn interest and funding costs, operating costs and losses affect what remains. The opening supplies the answer in one diagram and one sentence before asking the reader to interpret figures.
- A salesperson should be able to ask whether deposit costs or loan rates are changing faster, and whether expected credit losses could offset any benefit. Use the question to guide investigation. It is not a confirmed Lloyds pressure or opportunity.
- A reader should identify £502.8bn as Group deposits at a date and £6.6bn as Group statutory pretax profit over nine months. Neither figure establishes the bank's rate sensitivity, business-line profitability or a funding-to-profit reconciliation. The £496.5bn comparison is another balance at a date.
- The opening is designed for a roughly ten-second read. This was a specialist walkthrough of the rendered artefacts, not a timed participant study. An independent reviewer was unavailable. For owner acceptance, show the portrait opening to a non-specialist for ten seconds, then ask them to explain the arrows and identify which information Lloyds reported. Repeat with Insight and ask what question they would investigate.

## Inside proposal for a later review

The credit and service column headers name broad journeys, while the cells alternate between actions, decisions and safeguards. The row labelled Technology and controls mixes a potential reusable capability with the means of enabling it. Intersection implies a relationship but cannot establish a sequence, common accountable team or actual system. The Envoy disclosure sits separately and does not establish a workflow connection.

Use a journey with a trigger, a recognisable customer outcome and a few labelled actions. For example, a conceptual credit journey could show **request credit → assess affordability → decide and explain → service the account**. Underneath, attach durable capabilities to the actions they may support. Use **Credit assessment** and **Account servicing** as capabilities, and move audit records and platform controls into an enabling layer. Add organisation and accountable roles only when the exact enterprise and workflow are evidenced. Keep disclosed Group technology in its own evidence inset until a source can connect it to a particular action. Insight would show the effect of one hand-off or decision on the same selected journey.

## Forces proposal for a later review

Use a dated **Observed decision → Possible business effects → Lloyds evidence needed** visual. The decision card states what changed. Two alternative branches show the bank paying more for savings first, or earning more on new or variable-rate loans first. Put the possible effect on interest earned less interest paid beside each branch. In a separate evidence area identify the Lloyds data needed to compare the branches, including the rates and timing for deposits and lending. The Group's efficiency target belongs outside the response chain unless a source connects it to that decision. Any Material Pressure remains subject to ADR-026.

The official minutes and the existing reviewed excerpt agree. The meeting ending **4 November 2026** voted **8–1 to raise Bank Rate by 0.25 percentage points to 4%**. The stated move implies a previous rate of **3.75%**. The dissenting member preferred a rise of 0.5 percentage points to 4.25%. The current Forces phrase “raises Bank Rate to 4%” is consistent with the source. “Funding costs reprice first” and “lending reprices first” are alternative mechanisms, with no reported Lloyds direction attached. A future treatment should use “what the bank pays for deposits” and “what borrowers pay” before introducing technical terminology. [Official minutes](https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2026/november-2026) · [ADR-026](../../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md)

## Scope and rollback

The change touches Landscape composition in `lloyds_recovery.py`, one dispatch in `visual_panels.py`, Landscape styles in `visual_stream_assets/lloyds.css`, tests and before/after evidence. The existing eligibility, identity and financial owners resolve each claim. The published dates and reporting bases are unchanged. The £6.3bn stock comparison is conditional on both eligible inputs. `tools/research/ux_unify_compatibility.py` pins the two-line dispatcher change against the existing predecessor; security and regression baselines are unmodified. `tools/ci/flora_eai2_preview.cjs` and the experience browser fixture follow the revised public presentation while continuing to test the existing service route and its access boundary.

The browser comparisons cover Facts and Insight at five viewport sizes, keyboard and emulated touch, no JavaScript, history, text enlargement, and unchanged guest response content on nine surveyed routes. Native Safari and hardware touch were outside this run. Revert the correction commit to restore the reviewed head's Landscape UX without a migration. Inside and Forces remain proposals pending owner acceptance. [Browser evidence](browser-results.json)
