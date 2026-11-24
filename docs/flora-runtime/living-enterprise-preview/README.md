# Optional Lloyds Living Enterprise preview

Implementation for owner technical and visual review. Design reference: [PR #729](https://github.com/rdidale-jpg/CIOS/pull/729), exact head `da1a6c7b5e4b95e85ef2de3697bc8c506368192c`. Branch starts from verified main `97d316c640c96d99c2301819f8aac00b3b9c1398`, with [successful full baseline CI](https://github.com/rdidale-jpg/CIOS/actions/runs/45255984476). The design PR is not merged or changed.

## Owner walkthrough after an approved release

1. In existing Flora, **Industries → Banking → Lloyds**, or **Enterprises → Lloyds**.
2. The current experience remains the default. Select **Preview New Experience**.
3. The preview is labelled **Experimental design**. Use the existing Top **Landscape | Inside | Forces** control.
4. Select the four illustrated regions in Left. Main explains the selected subject; the active region is outlined. On iPad portrait/mobile, **Explore Lloyds** opens the scene and selection returns to Main.
5. Check the commercial progression: business/economics → operating capabilities/technology → change, timeline and eight SWOT themes. The original subject remains visible when a view has only Group-level context; no unverified divisional exposure is implied.
6. Use keyboard/Enter, touch, Back/Forward and direct reload. Select **Return to current experience** to reach the existing Lloyds view in the corresponding perspective.

**Preview route:** `/enterprises/lloyds/preview`. Planned existing-service URL: `https://flora-current.onrender.com/enterprises/lloyds/preview`. **It is not deployed by this PR.** Current production remains at the confirmed baseline until a separately approved merge and manual deployment.

## Bounded integration

The approved Phase A region geometry, original Lloyds artwork, explanatory compositions and native SWOT choices are adapted into the existing runtime. The shared frame accepts optional presentation slots; it is not replaced or monkey-patched. Existing Lloyds content is byte-equivalent after removing the single authorised entry link; the browser proof compares all three current perspectives against actual main.

The preview reads the same current, source-eligible public intelligence on every request. Its financial values pass the existing governed fact adapter and exact Group/period/unit/type guards. It does **not** serve the design's downloadable HTML or rendered state templates. There is no static snapshot/export endpoint, client intelligence cache, private Financial-run discovery or persistence. HTML/HEAD responses are `no-store`; restored browser pages reload through Source checks. Revoked source-dependent figures, marker/accessibility labels, SWOT, timeline and analytical diagrams are omitted.

One original architectural image remains recognizable across three overlays. The rooms and explanatory flows are conceptual, not actual Lloyds premises, a legal hierarchy, measured divisional economics or a verified system topology. Group deposit stock and nine-month statutory profit retain their correct scope and dates. No new facts or research are introduced. Lloyds §2 projection stays inactive, §5 PDF links deferred, ADR-027 Proposed; there is no new source admission or publication authority.

The current routes, flagship, Financial Analyst, authorised research inspection, navigation, Offers, Pipeline, authentication and canonical ownership remain in place. Detailed evidence is available through existing authorised capabilities, not a new preview administration interface. Public reading requires no new login; expired or forged authority does not confer private access.

[Changes and provenance](Implementation.md) · [Validation and exact rollback](Validation.md) · [Existing-service deployment instructions](Deployment.md) · [Exact file inventory](Integrity-Proof.json).

## Actual browser captures

| View | Desktop | iPad landscape | iPad portrait |
| --- | --- | --- | --- |
| Current Lloyds | [Current](previews/after-desktop-current-lloyds.jpg) | [Current](previews/after-ipad-landscape-current-lloyds.jpg) | [Current](previews/after-ipad-portrait-current-lloyds.jpg) |
| Preview Landscape | [View](previews/after-desktop-preview-landscape.jpg) | [View](previews/after-ipad-landscape-preview-landscape.jpg) | [Scene](previews/after-ipad-portrait-preview-landscape.jpg) · [Compact](previews/after-ipad-portrait-preview-landscape-compact.jpg) |
| Preview Inside | [View](previews/after-desktop-preview-inside.jpg) | [View](previews/after-ipad-landscape-preview-inside.jpg) | [Scene](previews/after-ipad-portrait-preview-inside.jpg) · [Compact](previews/after-ipad-portrait-preview-inside-compact.jpg) |
| Preview Forces | [View](previews/after-desktop-preview-forces.jpg) | [View](previews/after-ipad-landscape-preview-forces.jpg) | [Scene](previews/after-ipad-portrait-preview-forces.jpg) · [Compact](previews/after-ipad-portrait-preview-forces-compact.jpg) |

[Baseline Lloyds](previews/before-desktop-current-lloyds.jpg) · [Eight-theme SWOT](previews/after-desktop-preview-swot.jpg) · [easyJet retained](previews/after-desktop-easyjet-inside.jpg). Additional mobile/portrait captures and machine-readable checks are committed. These are actual local application renders, not a deployed preview or physical iPad/Safari certification.

## Owner acceptance

- [ ] Entry is discoverable in ordinary Lloyds navigation; current experience remains default.
- [ ] Experimental status and return path are obvious without obscuring the art.
- [ ] Three perspectives and four visual regions are commercially understandable on desktop and both iPad orientations.
- [ ] Subject context, history, keyboard and touch work; all eight SWOT themes remain reachable.
- [ ] No financial allocation, actual topology, contract scope, integration outcome or buying demand is implied by the conceptual visual.
- [ ] Accept the exact implementation/CI head before any merge; separately approve the exact validated release before deployment.
