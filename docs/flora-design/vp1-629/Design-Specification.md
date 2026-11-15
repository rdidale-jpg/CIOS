# Three-panel design specification

## Thesis

Keep FLORA’s illustrated world as the means of discovery, while giving intelligence enough room to be read. The country remains the visual identity; the scene becomes a portrait navigator; the Main area becomes an editorial workspace. The owner-approved full scenes remain available as immutable design authority, not overwritten by this proposal.

| Region | Ownership | Proposed dimensions / behaviour |
| --- | --- | --- |
| Top | UK skyline; FLORA/global tools; generic role identity; single current-scope trail; active contextual streams; accessible skip link | Desktop 148px and 310px Left; 1280px laptop 148px/310px; iPad landscape 128px/260px. Height grows for enlarged text. No separate breadcrumb band. |
| Left | Purpose-composed scene; subject selection; compact collapse control | Desktop/iPad landscape visible. Portrait iPad and phones start as a closed native disclosure. Reopening retains scope, stream and selected subject. The new scene’s full 2:3 composition is contained, never squeezed or recropped by layout. |
| Main | Intelligence, comparative chart, sources, caveats, agenda and future tool composition | Flexible remaining width, ivory background, editorial serif headlines, restrained rules and small semantic annotations. Sources expand inline here; no right rail or detached window. |

Every product composition has exactly these three direct body regions. No footer, fourth panel, floating action bar, additional banner or full-width section sits outside them. Responsive visual expansions remain inside Left; chart data and source disclosures remain inside Main. The separate art-comparison sheet is a review artifact, explicitly not a product screen.

## Navigation contract

- UK and Banking: **Landscape | Forces**. Lloyds: **Inside | Landscape | Forces**. Each stream is a native link, visibly selected with underline plus shape/colour.
- UK scene’s Banking label → Banking scene’s Lloyds label → Lloyds. Exactly two deliberate selections, no Banking Groups or mandatory Builder page.
- Static file names encode finite country/scope/stream/subject selections, not entity access authority. Compatible subjects persist across stream switches. Enterprise economics/technology receive a different contextual headline/background while retaining the same underlying facts. The shared Leadership Agenda remains the same agenda across lenses.
- Native fragments focus Main after subject selection and the active stream after switching; scroll margins retain Top context. Browser Back/Forward and file deep links use normal browser history, not a bespoke router.
- Offers and Pipeline are visually referenced as inert global labels. This public, local design bundle cannot grant access to private product journeys. News/Tools are absent from live stream navigation. Separate `concept-news.html` / `concept-tools.html` files are conspicuously labelled future layouts, not functional tabs or workflows. Topic Cards remain a future extension, with no dummy control.

## Responsive and accessible composition

Desktop 1440×900 and laptop 1280×720 keep all three panels visible. iPad landscape 1194×834 retains a 260px Left and meaningful Main width. At 834×1194, Left collapses to a strip rather than permanently taking a quarter of the screen. At 390/320px, Top wraps compactly, Left stays closed and Main gets full reading width. A landscape phone, effective 200% viewport reflow, Retina DPR2 and all-element 200% text enlargement are tested separately.

No JavaScript is shipped. Native anchors, summaries, checkbox and chart tables support keyboard/touch. The source disclosure is inline, not a modal. One `h1` names Main, logical headings follow, landmarks are named and decorative images are hidden from the accessibility tree. Missing images retain labelled subject navigation. Watermarks disappear in forced colours; active state retains an underline. Motion is absent and reduced-motion preferences are respected.

The deposit reference checkbox hides/shows only the dated 2025 comparison, with a constant linear scale and matching table; current data remains. It is a presentation control, not financial calculation or saved state. New native navigation prioritises Main on narrow screens; collapse itself retains keyboard focus.

## Architecture and future implementation boundary

Governing references: CIOS-AI, Reference Architecture, Design Doctrine, Chief Architect Handbook, Glossary/Document Map, accepted ADRs 002/005/009/010/012/013/014/015/016/024/026, merged VEX/INT and the six-type presentation policy. This is a view of existing owners, consistent with ADR-013 Canvas/lens navigation. It creates no Tile/Evidence/Observation/Enterprise Model, Source registry, matching engine or qualification state.

The build reads merged public Banking/Macro/economy view owners and calls the existing semantic policy. Source bytes must match the exact baseline. The dated agenda snapshot explicitly freezes only the design’s clock to 15 November 2026; it does not alter the production expiry/freshness policy. The exported HTML is a design document, not a live intelligence owner, cache, acceptance service or runtime endpoint. No pending EAI material enters it.

A later implementation would map these three regions to current `visual_streams.Context/resolve/url`, current owner projections and existing IAM. Permissions must be resolved before rendering, not inferred from a URL or static “Owner” design label. Owner inspection and source acceptance remain separate. This sprint makes none of those runtime changes.

The bounded prototype wires three prominent visual subjects per scene and the requested UK→Banking→Lloyds path. It does not reproduce every existing hotspot or private journey; [Interaction-Mapping.json](Interaction-Mapping.json) records the full accepted source geometry for later mapping. Existing production addresses/functionality are untouched. The owner must accept the discovery-versus-reading tradeoff before an implementation sprint; no silent functional removal is proposed.
