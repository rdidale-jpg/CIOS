# FLORA Visual Atlas VA-1 — owner design decision

Design proposal for [#605](https://github.com/rdidale-jpg/CIOS/issues/605), based on `origin/main` at `0cb07c2e78ccb16240c799b31cd62736e2135529`. No proposed design is accepted by writing this document. The current accepted runtime remains unchanged. PR #603's owner-assurance work is separate and is not incorporated into this branch.

**Recommendation: choose A, Continuous Panorama, for further design development.** Its warm daylight palette and shared sky preserve the approved FLORA world while improving cross-level continuity. Accept a visual direction first, then commission distinct Banking and enterprise artwork with reviewed hotspot geometry. These studies reuse approved conceptual imagery, not newly verified company operating models. Owner acceptance is pending; VA-1 does not authorise implementation.

## Three alternatives

| Direction | What changes | Strength | Cost / risk |
|---|---|---|---|
| **A — Continuous Panorama** | Wide daylight scene with shared paper/sky, open headline, quiet metrics and three spatial entry points | Closest to approved FLORA; welcoming, image-led; strongest continuity UK → industry → enterprise | Complex artwork needs quiet text surfaces; future image-specific anchors must be reviewed |
| **B — Spatial Atlas** | Deep forest surround, subdued landscape, luminous actor/navigation layers | Strong layer separation; memorable immersive workspace; good selected-context emphasis | Dimming sacrifices artwork detail; night-like tone may feel less open; contrast must be measured in each state |
| **C — Editorial Landscape** | Stable reading rail beside a continuous image field; typography leads, actors sit within image | Best scanning of economic context and long enterprise names; predictable reading order | Less panoramic on desktop; split composition must collapse deliberately on iPad/phone |

All share Explore / News / Signals / Opportunities / Pipeline, a visible Strategic Sales **design persona**, separate scope breadcrumb, Economy/Government lens at UK, contextual Explore deeper and optional understandable financial context. Role display is not a role switch, login or grant of permission. News and the other tools lead to labelled static design explanations, not product functionality. Signals answers what changed; News is an editorial weekly synthesis; neither implies opportunity. Forces of Change is the ordinary wording; PESTLE stays its underlying methodology.

### Open the design studies

[Comparison index](index.html). Serve this folder locally: `python -m http.server 8776 --bind 127.0.0.1 --directory docs/flora-runtime/visual-atlas-va1`, then visit `http://127.0.0.1:8776`. These are review artifacts, not application routes. The PR also contains rendered JPEG previews for review without running anything.

| Direction | UK | Banking | Technology | Banking enterprise | Technology enterprise | Government lens |
|---|---|---|---|---|---|---|
| A | [UK](a-uk.html) | [Banking](a-banking.html) | [Technology](a-technology.html) | [Lloyds](a-lloyds.html) | [NVIDIA](a-nvidia.html) | [Government](a-government.html) |
| B | [UK](b-uk.html) | [Banking](b-banking.html) | [Technology](b-technology.html) | [Lloyds](b-lloyds.html) | [NVIDIA](b-nvidia.html) | [Government](b-government.html) |
| C | [UK](c-uk.html) | [Banking](c-banking.html) | [Technology](c-technology.html) | [Lloyds](c-lloyds.html) | [NVIDIA](c-nvidia.html) | [Government](c-government.html) |

## Preview gallery

Each of the 18 screens is captured at desktop 1440, iPad landscape 1194, iPad portrait 834, mobile 390 and narrow mobile 320 CSS pixels. Three additional 720px captures represent the layout width of a 1440px desktop at 200% zoom; this is not physical-device or OS magnification certification.

| Direction | Desktop UK | iPad Banking | Mobile Enterprise | Government |
|---|---|---|---|---|
| A | [Preview](previews/desktop-a-uk.jpg) | [Preview](previews/ipad-landscape-a-banking.jpg) | [NVIDIA](previews/mobile-a-nvidia.jpg) | [Preview](previews/desktop-a-government.jpg) |
| B | [Preview](previews/desktop-b-uk.jpg) | [Preview](previews/ipad-landscape-b-banking.jpg) | [NVIDIA](previews/mobile-b-nvidia.jpg) | [Preview](previews/desktop-b-government.jpg) |
| C | [Preview](previews/desktop-c-uk.jpg) | [Preview](previews/ipad-landscape-c-banking.jpg) | [NVIDIA](previews/mobile-c-nvidia.jpg) | [Preview](previews/desktop-c-government.jpg) |

Additional filenames follow `{device}-{a|b|c}-{uk|banking|technology|lloyds|nvidia|government}.jpg` in [previews](previews). [Architecture / metric review](Review-and-Contracts.md), [art provenance](Artwork-Provenance.json), [browser results](previews/Browser-Checks.json).

## Owner walkthrough and decision

1. Compare desktop UK in A/B/C. Choose whether panorama, immersion or editorial reading best expresses FLORA.
2. Follow UK → Banking → Lloyds, then UK → Technology → NVIDIA. Check continuity, recognisable context, readable economic slots and one clear next exploration.
3. Open Explore deeper. Buildings group enterprises, suppliers/infrastructure and public actors. These are navigable role concepts, not unsupported business relationships. Equivalent text links remain available.
4. Compare Government with Economy. Public administration has GVA; spending, receipts, borrowing and procurement remain separate, never summed into output.
5. Review iPad in both orientations, 390/320px phone and zoom-width captures. Try keyboard skip, the five product destinations and disclosures without JavaScript.
6. Confirm A/B/C or request a bounded combination. Do not infer metric, relationship or implementation acceptance from visual acceptance.

Before implementation: owner sign-off; #607 metric reconciliation and source review; #608 actor identity/edge/geometry contract; #606 News editorial/rights design. #604 early influence, #599 research assurance and #597 Ripple remain separate. Preserve Command Centre as restricted optional inspection; seller-facing views receive commercial language, not forensic traces.

No functional implementation, production configuration, historical research change, merge or deployment. Undoing this design branch requires no data rollback. Actual browser runs do not read accounts or call any app service. Manual Safari/iPad, VoiceOver/NVDA, colour perception and slow-network assessment remain acceptance work, not claimed passes.

## Validation record

90 responsive page captures passed 540 layout/navigation assertions, plus three keyboard/zoom-width cases and the UK → Banking → Lloyds journey. Static link validation covers all 19 HTML documents (including index), with no broken internal destination or script. These checks review design artifacts; they do not certify physical-device accessibility or live authorisation. The branch also runs the existing full security/regression CI against its exact committed head. That gate's published result, SHA and sanitized artifact are authoritative; no baseline or comparator is modified.
