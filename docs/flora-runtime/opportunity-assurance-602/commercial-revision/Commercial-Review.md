# Commercial presentation correction — PR #603

Addresses the owner's [review](https://github.com/rdidale-jpg/CIOS/pull/603#issuecomment-6874911809) of 14 November 2026. Before: validated PR head `3dfa171fdadb15efe937f4e5b828823aef347c99`. The owner rejected its visual/commercial design despite passing CI. This revision does not claim owner acceptance or independent sales-practitioner sign-off.

## Default experience

The first screen now asks whether there is a useful customer conversation. Detail contains customer/Offer, **potential business challenge → opportunity to influence → best next action → biggest uncertainty**, with unquantified possible value. One clear action opens each conversation. Saved work appears first, then alphabetical order; this is a display order, not a new sales ranking. No confidence percentage, qualification gauge, raw research tier, source ID, policy digest or evaluation JSON is shown by default.

The former technical inspection remains behind an optional **Advanced Inspection** disclosure and explicit link. It retains the same owner checks, original facts and tiers, qualifications, typed seller/customer evidence, hand-off decisions, source rights, policy versions, full replay and non-mutating challenges. Sources and material cautions also remain available in a short, understandable disclosure on the commercial screen. Back navigation returns to actual commercial context, not a hypothetical changed state.

| Question | Before | After |
|---|---|---|
| What is the customer issue? | Source facts, tiers and counts led the page | A specific potential customer problem, phrased as a question |
| Can we still influence it? | Freshness/validation priority could suggest a strategic pursuit | Explicit uncertainty; Santander may already be late |
| What should I do next? | Long playbook text and several technical panels | One concrete residual-need or customer-validation action |
| What is unknown? | Distributed across technical details | Biggest uncertainty visible without opening anything |
| What is the financial value? | Risk of confusing record completeness with quality | Unquantified benefit mechanisms; no invented amount |
| Where is the detailed logic? | Default screen with many disclosures and gauges | Separate optional Advanced Inspection |

## Santander source correction

The official [TSB announcement](https://www.tsb.co.uk/news-releases/Santander-UK-and-TSB-apply-to-transfer-the-TSB-business-to-Santander-UK.html), published **10 November 2026**, was re-read for this review on **14 November 2026**. Its opening paragraph reports acquisition completion on **30 April 2026**, followed by a legal business-transfer application. Subsequent paragraphs describe continuing integration and conditional customer migration in **H2 2027**. Notes to editors retain separate legal entities.

These dates describe different things. The announcement is not a sourcing notice. Actual sourcing-decision dates, supplier vacancies, unallocated delivery scope, funding, customer access and the ability to shape remain unknown. Significant account intelligence does not establish an early strategic sales opportunity. The new default warning says the early strategy-setting window may have passed and asks whether material decisions, residual work or future phases remain open. It does **not** declare all opportunities closed.

Digital asks about remaining customer-journey/ownership decisions. Legacy asks about unresolved estate-treatment, rights, reconciliation and rollback decisions. Both are residual-scope validation, not a greenfield strategy-setting pitch. Lloyds AI-first still asks whether process/role redesign actually exists; Computacenter Cyber asks whether internal/incumbent assurance is already sufficient; ESG remains Research only. No early signal, procurement or customer demand is invented to fill a comparison matrix.

The additional acquisition-date/context note is a **separately reviewed presentation clarification** in `opportunity_assurance_commercial.py`, not a retroactive edit to Sprint B's research register. It is gated on the original admissible Santander migration fact. An earlier cutoff with no admissible November source does not receive that later context. The original source, dated facts, policy, Prioritise research-validation tier, rank and saved private records remain unchanged. Advanced Inspection explicitly distinguishes that historical priority from an early sales opportunity.

## Boundary with Issue #604

This revision adds conservative copy and progressive disclosure only. It does not compute influence scores, introduce Early to shape classifications, re-rank fresh versus older signals by shapeability, infer historical decision windows, or silently revise customer records. [Issue #604](https://github.com/rdidale-jpg/CIOS/issues/604) owns the separately versioned influence-window assessment, supporting evidence, no-lookahead comparisons and architecture acceptance. It remains unimplemented here.

## Commercial-language review

Implementation review findings: the first-screen copy now centres on customer relevance and the next question. Santander's late/uncertain warning is visible, balanced and explicit about missing external scope. Potential value is qualitative. Technical details remain inspectable without occupying the default view. Research-only and Offer/customer restrictions retain their meaning. The view does not claim a customer has confirmed demand merely because example sales inputs are complete.

Owner or independent commercial-review acceptance remains pending. Review the desktop/iPad/mobile first screens for clarity, actionability and density; then confirm Advanced Inspection retains evidence and control detail. No human reviewer approval is fabricated.

## Evidence and validation

The preview worker compares the **actual pre-revision owner screens at `3dfa171…`** against the new commercial screens using isolated equivalent fixtures. It also captures the separate Advanced Inspection screen and source-withdrawal challenge. All private-domain, Pipeline and mission bytes must stay unchanged. Fixtures and customer attestations remain explicitly labelled examples, not real customer evidence.

New assertions cover default business headings, absence of technical traces/tiers, retained advanced evidence, Santander uncertainty and source dates, Research-only restrictions, no retrospective November context, and absence of a new influence score/model. Existing permission, matcher parity, challenge and Pipeline tests remain. Presentation assertions now explicitly select Advanced Inspection where technical content is expected; no security or baseline assertion is removed.

Full final local and hosted CI must validate the exact corrected head: 1,432 baseline identities; 388 strict security passes; 36 unchanged inherited failures; 10 unchanged skips; zero comparator issues. Supplemental workflow coverage is 355 cases, including 37 assurance tests, plus 39 CI failure-policy tests. No merge, Render deployment or production changes.

## Before / after review

| Device | Before | Commercial overview | Santander commercial detail | Advanced Inspection |
|---|---|---|---|---|
| Desktop | [Overview](previews/desktop-overview-before.jpg), [Digital](previews/desktop-digital-before.jpg) | [Overview](previews/desktop-overview-after.jpg) | [Digital](previews/desktop-digital-after.jpg), [Legacy](previews/desktop-legacy-after.jpg) | [Detail](previews/desktop-advanced-after.jpg) |
| iPad landscape | [Digital](previews/ipad-landscape-digital-before.jpg) | [Overview](previews/ipad-landscape-overview-after.jpg) | [Digital](previews/ipad-landscape-digital-after.jpg) | [Detail](previews/ipad-landscape-advanced-after.jpg) |
| iPad portrait | [Digital](previews/ipad-portrait-digital-before.jpg) | [Overview](previews/ipad-portrait-overview-after.jpg) | [Digital](previews/ipad-portrait-digital-after.jpg) | [Detail](previews/ipad-portrait-advanced-after.jpg) |
| Phone | [Digital](previews/mobile-digital-before.jpg) | [Overview](previews/mobile-overview-after.jpg) | [Digital](previews/mobile-digital-after.jpg) | [Detail](previews/mobile-advanced-after.jpg) |
| 320px / zoom | [Digital](previews/mobile-320-digital-before.jpg) | [Overview](previews/mobile-320-overview-after.jpg) | [Digital](previews/mobile-320-digital-after.jpg), [200% zoom](previews/zoom-200-digital.jpg) | [Detail](previews/mobile-320-advanced-after.jpg) |

[Browser checks](previews/Browser-Checks.json) and [read-only integrity](previews/Read-Only-Integrity.json). The original OA-1 screenshots/evidence remain preserved alongside this revision. Revert the presentation commit through a reviewed PR if needed; there is no business-data migration or assurance datastore to undo. Do not delete or reverse user records.
