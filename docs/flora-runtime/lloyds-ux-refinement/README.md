# Lloyds flagship UX refinement

Baseline `63df0cbf8e1de98d8a782cd0a448c7ec7bab4147`. Open Lloyds Landscape and select **Explore the Lloyds flagship**. The canonical arrival, original artwork and Facts / FLORA Insight control are reused.

## Walkthrough

1. Pick Retail, Commercial Banking, or Insurance, Pensions & Investments. Each choice shows the customer and product context, illustrative economics, and links to the Group operating examples and strategy. Evidence does not support segment allocation or ownership.
2. Open **Core renewal**. Select Economics, Operations, Technology, Pressure or Strategy. Each choice displays its disclosure and an existing detail link. The sequence is an analytical association. Its order establishes no causal effect.
3. Switch to **FLORA Insight**, select **Perspectives**, then explore the SWOT quadrants, risk categories, AI and payments, horizontal timeline, options or peer bars. The bars measure complaints received across distinct legal entities and cannot rank service quality.
4. Select **Sources** in context to open the one inspection panel at the relevant evidence. It includes available publisher, publication date, locator, scope, authority and caveats. Browser Back restores the previous selection. All evidence already passes through the original eligibility gates.

## Review captures

| View | Desktop | iPad landscape | iPad portrait |
| --- | --- | --- | --- |
| Before | [Desktop](previews/before-desktop.jpg) | [Landscape](previews/before-ipad-landscape.jpg) | [Portrait](previews/before-ipad-portrait.jpg) |
| After | [Desktop](previews/after-desktop.jpg) | [Landscape](previews/after-ipad-landscape.jpg) | [Portrait](previews/after-ipad-portrait.jpg) |
| SWOT | [Desktop](previews/swot-desktop.jpg) | [Landscape](previews/swot-ipad-landscape.jpg) | [Portrait](previews/swot-ipad-portrait.jpg) |

[Browser harness](browser.py) · [Before observations](previews/before.json) · [After observations](previews/after.json). All three viewports went from 31 flagship disclosures to one Sources panel, closed on arrival. Counts exclude the shared shell and the separate accepted Landscape arrival.

## Critique

The first screen communicates organisation and customer context before supporting evidence. Same-page selections shorten deep reading, while ordinary links preserve the existing route and browser history. The prototype still has an in-page navigation row alongside the established shell, and contextual Sources opens a panel below the perspectives instead of taking over the screen. Without scripting, sections remain readable in document order and Sources remains a native disclosure. Chromium emulates touch and viewport sizes. Physical iPad, Safari and assistive-technology review remain open.

Existing conclusions and inputs stay with their current owners. The AI view identifies the company-disclosed Envoy capability and separates a policy pilot from a hypothetical assistant. Named entrant launches remain unverified. Disclosed controls, inferred execution risk and dated regulatory pressure retain their separate treatments. Existing private Financial and Pipeline access is outside the visual change. Lloyds §2 stays inactive, §5 PDF links stay deferred and ADR‑027 stays Proposed.
