# FLORA Visual Experience v2 — two-screen design proof

Separate draft for [#583](https://github.com/rdidale-jpg/CIOS/issues/583). **No design acceptance, canonical Home replacement, merge or deployment is claimed.** The owner's change request on #582 and the restraint principle in #581 guide this work; #582 remains an unchanged, unaccepted comparison baseline.

Base: integration #580 / #578 at `34e34570c52847e16eb5f0d00579ca923983af7c`. This draft targets that integration branch, with Home v1 deliberately absent from its ancestry. No release/integration branch or existing product screen is modified beyond the two finite preview-route connections. Resolve the final integrated base and rerun current-head CI before eventual promotion.

## Look at the two screens

| View | Desktop 1440 | iPad landscape 1194 | iPad portrait 834 | Mobile 390 | Mobile 320 |
|---|---|---|---|---|---|
| Full UK economy | [View](previews/desktop-economy.jpg) | [View](previews/ipad-landscape-economy.jpg) | [View](previews/ipad-portrait-economy.jpg) | [View](previews/mobile-economy.jpg) | [View](previews/mobile-320-economy.jpg) |
| PESTLE, initial | [View](previews/desktop-pestle.jpg) | [View](previews/ipad-landscape-pestle.jpg) | [View](previews/ipad-portrait-pestle.jpg) | [View](previews/mobile-pestle.jpg) | [View](previews/mobile-320-pestle.jpg) |
| PESTLE, selected technology | [View](previews/desktop-pestle-technological.jpg) | [View](previews/ipad-landscape-pestle-technological.jpg) | [View](previews/ipad-portrait-pestle-technological.jpg) | [View](previews/mobile-pestle-technological.jpg) | [View](previews/mobile-320-pestle-technological.jpg) |
| PESTLE, selected economy | [View](previews/desktop-pestle-economic.jpg) | [View](previews/ipad-landscape-pestle-economic.jpg) | [View](previews/ipad-portrait-pestle-economic.jpg) | [View](previews/mobile-pestle-economic.jpg) | [View](previews/mobile-320-pestle-economic.jpg) |
| Before: unaccepted Home v1 | [View](previews/desktop-home-v1-before.jpg) | [View](previews/ipad-landscape-home-v1-before.jpg) | [View](previews/ipad-portrait-home-v1-before.jpg) | [View](previews/mobile-home-v1-before.jpg) | [View](previews/mobile-320-home-v1-before.jpg) |

All six desktop selections: [Political](previews/desktop-pestle-political.jpg), [Economic](previews/desktop-pestle-economic.jpg), [Social](previews/desktop-pestle-social.jpg), [Technological](previews/desktop-pestle-technological.jpg), [Legal](previews/desktop-pestle-legal.jpg), [Environmental](previews/desktop-pestle-environmental.jpg).

[Annotated economy zones](Economy-Interactions.svg) · [Annotated PESTLE geometry](PESTLE-Interactions.svg) · [Economy print](previews/economy-print.pdf) · [PESTLE print](previews/pestle-print.pdf) · [Browser results](previews/Browser-Checks.json)

[Design assessment](Design-Assessment.md) · [Taxonomy and economic sources](Taxonomy-and-Scale.md) · [Interaction and ownership contract](Interaction-Contract.md) · [Validation](Validation.md)

## Acceptance walkthrough

1. Open the UK desktop preview, then both iPads. Within five seconds, assess national identity, the full economic breadth, typography and the restrained country GVA line. There is only one header navigation; the illustration ends the page.
2. Read the five on-image benchmarks as **2024 shares of UK GVA**, not market sizes of Banking/Technology/Aviation. Open Sources & method once to inspect the full 20-section comparison and rounding. Building/land area carries no quantitative meaning.
3. Use Tab/Enter or touch on the three solid-green research labels. Technology, Banking and Aviation reach existing experiences. Other labelled districts remain visible text, with no false research links or negative coverage badges.
4. Use PESTLE in the same compact header. All six labels are present before interaction. Choose each: one concise insight appears over the image and all six factors remain available. No explanation is placed further down the page. Close it using its cross, or Escape when JS is available.
5. Read Economic: a UK real-GDP volume change over three months is distinct from annual current-price GVA. Read Legal: a reviewed proposal cannot become a current duty. Social uses the existing narrowly scoped social-value evidence, not invented population research.
6. Inspect the one optional Sources & method disclosure. Selected PESTLE lineage, original source URLs/dates, existing review cutoff, scope and counter-evidence remain available. No repeated inspection prompts appear on the primary image.
7. On mobile 390/320, scroll through the two consecutive halves of the **same complete economy artwork**. This preserves legibility instead of shrinking twenty labels into a thumbnail. PESTLE uses its portrait companion artwork and a single over-image reveal. No horizontal page panning is required.
8. Exercise no-JS navigation, 44px targets, keyboard focus/skip and the single Sources/menu controls. Sign-in and CSRF-protected sign-out remain accessible from Menu. Public and signed-in users see the same uncluttered world; private employer/offers/mission content is not loaded into these screens.
9. Compare the before screenshots: the old content modules, Explore strip and per-development source prompts are removed from **this proof only**. Current canonical Home and all Industry/Enterprise/Offers/Pipeline pages retain their prior owners and presentation.

## Run the bounded prototype locally

Only two new HTML routes: `/visual-v2?market=GB` and `/visual-v2/pestle?market=GB`. `factor=political|economic|social|technological|legal|environmental` selects a state of the second screen, not another screen. These are **local preview paths, not deployed links**. No live URL is claimed.

Use the repository's normal isolated development setup, or reproduce the safe, temporary preview server/screenshots with:

```sh
PYTHONPATH=. python tools/ci/flora_visual_v2_preview.py --output /tmp/flora-visual-v2-previews --baseline-root /path/to/clean-home-v1-9aaaa692-checkout
```

The helper bootstraps disposable synthetic local authority and HTTPS, uses a synthetic password only inside a temporary directory, and cleans it up. It does not connect to production, create commercial objects, run research or deploy. Screenshots are actual browser renders; illustration assets are conceptual generated artwork. Physical iPad/Safari, screen-reader and high-zoom acceptance remain manual.
