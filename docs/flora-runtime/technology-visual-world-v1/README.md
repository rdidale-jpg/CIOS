# UK Technology — visual-world reset

Replaces #570's role tiles, programme panels and commercial card grid with one bespoke illustrated SVG landscape. The picture is now the primary navigation surface. This change is stacked above #570; neither #570 nor main is merged, retargeted or deployed.

## Before and after

| Lens | #570 foundation | Visual reset |
| --- | --- | --- |
| How it works | Eight icon tiles with a persistent side inspector | Sculpted operating landscape: application towers, cloud/data basin, AI constellation, cyber canopy, services bridges, distribution routes, infrastructure and frontier research |
| Who uses what | Programme list beside boxed customer/product details | One blue programme ribbon across the same landscape; a native chooser changes the retained record; selecting the imagery reveals scoped evidence |
| Where work may emerge | Six commercial-theme cards | Six amber seams in the operating map; selection reveals the evidence, alternative explanation and customer qualification question |
| Provider drill | Directory/profile as the primary page body | The scene stays central, the selected provider's role is highlighted, and its partial profile appears in a contextual overlay; the complete directory is secondary |

### Preview gallery

| Lens | Before | New desktop | New landscape tablet | New portrait tablet |
| --- | --- | --- | --- | --- |
| How it works | [#570](../technology-visual-foundation/previews/how-it-works-desktop.png) | [Full view](previews/how-it-works-desktop.png) / [Scene](previews/how-it-works-scene-desktop.png) | [View](previews/how-it-works-tablet.png) | [View](previews/how-it-works-portrait-tablet.png) |
| Who uses what | [#570](../technology-visual-foundation/previews/who-uses-what-desktop.png) | [Full view](previews/who-uses-what-desktop.png) / [Scene](previews/who-uses-what-scene-desktop.png) | [View](previews/who-uses-what-tablet.png) | [View](previews/who-uses-what-portrait-tablet.png) |
| Where work may emerge | [#570](../technology-visual-foundation/previews/where-work-may-emerge-desktop.png) | [Full view](previews/where-work-may-emerge-desktop.png) / [Scene](previews/where-work-may-emerge-scene-desktop.png) | [View](previews/where-work-may-emerge-tablet.png) | [View](previews/where-work-may-emerge-portrait-tablet.png) |

Detail selection: [role](previews/role-overlay-desktop.png), [provider](previews/provider-overlay-desktop.png), [hypothesis](previews/hypothesis-overlay-desktop.png), [programme](previews/programme-overlay-desktop.png). These are browser captures, not owner visual acceptance.

## How navigation works

1. Open `/industries/technology`. The eight illustrated districts are native links. Select a miniature to inspect its conceptual role, economic boundary and provider research views.
2. Select a provider. The map remains visible and highlights the provider's explanatory role; the overlay retains profile limitations, source links and unbound identity. No duplicate Enterprise Model entity is created.
3. Choose **Who uses what**. Follow one published programme, then select the ribbon's customer or provider end to inspect exact offerings, roles, dates and source limits. Existing Lloyds/easyJet links and evidence disclosures retain their owners.
4. Choose **Where work may emerge**. Select an amber seam. The scene reveals the corresponding unqualified theme's evidence, alternative explanation, intervention and customer qualification question. Follow its underlying programme, then its exact research passage.
5. Use the close/return links to restore the unobscured image. Native text navigation and programme selection work without JavaScript. On small phones, pan within the landscape or use the text alternative.

## Preserved from #570

- All research JSON and the deterministic handoff are byte-identical, including all 80 provider views, 34 scoped relationship/programme records, 24 passage references and six unqualified themes.
- `technology.py`, the enterprise navigation registry, source importer, Evidence/Observation and review/promotion owners, and Pipeline implementation are unchanged.
- Existing Banking, Aviation, Macro and enterprise journeys are not redesigned. No data model, canonical identity, research claim, acceptance status, budget, buying intent or current contract is introduced.
- The complete 160-file historical research corpus and all #570 test records/failure signatures/skip reasons remain unchanged. New scene test identities are additive.
- #568/#569 remain separate paused experiments. No agent code or paid model client is introduced or activated.

## Reusable contract

[Visual-Contract.md](Visual-Contract.md) defines FLORA visual-world v1: conceptual districts/flows, attributed programme ribbons, hypothesis seams, provider focus, context overlays, native navigation, truth labels and responsive/accessibility behaviour. This is a presentation contract for owner review; Banking/Aviation/Enterprise adoption remains future authorised work.

## Verification

New unit/HTTP tests cover the three scene modes, all district links, all six seams, all 34 programme scopes, selected-provider context, invalid/private selectors, SVG escaping and byte-preservation of source/acceptance owners. The original 39 foundation tests remain active.

`tools/research/check_technology_world.cjs` checks desktop, landscape tablet, portrait tablet and mobile; keyboard navigation through every district, pointer selection of all six seams, no-JavaScript navigation, provider → hypothesis → programme → evidence, existing enterprise links, reduced motion and print. `check_technology_visual.cjs` preserves the original journey checks with updated scene selectors and URL fragments.

```sh
python -m pytest tests/test_flora_technology_visual_world.py tests/test_flora_technology_foundation.py -q
node tools/research/check_technology_world.cjs http://127.0.0.1:8792 OUTPUT_DIRECTORY
```

[Validation.md](Validation.md) records the completed focused/browser checks and exact acceptance boundaries. Actual full local and hosted gate conclusions must be read separately from the final completion report/current PR check. A focused or browser pass is not a substitute for actual-candidate hosted CI.

## Remaining limits

Research remains partial and unaccepted. Exact source provenance, source-operation rights, canonical identity/domain mapping and comparable provider baselines remain open; there are zero accepted imports or automatic Pipeline records. The landscape is a conceptual explanation, not a deployment architecture, geographic map, provider ranking or market-share chart. Hypothesis locations do not assert measured enterprise risk.

The presentation is implemented and browser-tested, but visual appeal, executive comprehension and owner acceptance remain unmeasured. Physical iPad/Safari and assistive-technology user studies are outstanding. Mobile uses an internally pannable landscape with a text alternative. SVG imagery is intentionally deterministic and static; no real-time monitoring or motion system was added.

Stop before merge or deployment. Review the scene-based experience before considering integration of #570 and this visual reset.
