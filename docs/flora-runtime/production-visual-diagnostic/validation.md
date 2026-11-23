# Production capture and validation

Public guest, 19 November 2026. Captures are Chrome viewport emulations at 1440×1000, 1180×820, 820×1180 and 390×844. The iPad captures describe viewport behaviour. Safari, hardware touch, the owner's authenticated configuration and the owner's original PDF workflow remain unverified. The owner observations supplied in the commission guided comparison. No owner screenshot files were available in this run.

| View | Accepted prototype comparator | Live browser capture |
| --- | --- | --- |
| UK Landscape | [VP-1 portrait](https://github.com/rdidale-jpg/CIOS/blob/f4059a34a55277adbd2a2337239827cab96d962e/docs/flora-design/vp1-629/previews/original-desktop-uk-landscape.jpg) | [Desktop Facts](previews/uk-landscape-facts-desktop.jpg) · [Desktop Insight](previews/uk-landscape-insight-desktop.jpg) · [Mobile Facts](previews/uk-landscape-facts-mobile.jpg) |
| UK Forces | [VP-1 illustrated Forces](https://github.com/rdidale-jpg/CIOS/blob/f4059a34a55277adbd2a2337239827cab96d962e/docs/flora-design/vp1-629/previews/original-ipad-landscape-uk-forces.jpg) | [iPad Facts](previews/uk-forces-facts-ipad-landscape.jpg) · [iPad Insight](previews/uk-forces-insight-ipad-landscape.jpg) |
| Banking Landscape | [VP-1 Banking composition](https://github.com/rdidale-jpg/CIOS/blob/f4059a34a55277adbd2a2337239827cab96d962e/docs/flora-design/vp1-629/previews/original-ipad-landscape-banking-landscape.jpg) | [Desktop Facts](previews/banking-landscape-facts-desktop.jpg) · [iPad Insight](previews/banking-landscape-insight-ipad-landscape.jpg) · [Mobile Facts](previews/banking-landscape-facts-mobile.jpg) |
| Banking Forces | [VP-1 illustrated Forces](https://github.com/rdidale-jpg/CIOS/blob/f4059a34a55277adbd2a2337239827cab96d962e/docs/flora-design/vp1-629/previews/original-ipad-landscape-banking-forces.jpg) | [iPad Facts](previews/banking-forces-facts-ipad-landscape.jpg) · [iPad Insight](previews/banking-forces-insight-ipad-landscape.jpg) |
| Lloyds Landscape | [VP-1 economics composition](https://github.com/rdidale-jpg/CIOS/blob/f4059a34a55277adbd2a2337239827cab96d962e/docs/flora-design/vp1-629/previews/original-ipad-landscape-lloyds-landscape.jpg) | [iPad Facts](previews/lloyds-landscape-facts-ipad-landscape.jpg) · [iPad Insight](previews/lloyds-landscape-insight-ipad-landscape.jpg) |
| Lloyds Inside | [VP-1 Inside portrait](https://github.com/rdidale-jpg/CIOS/blob/f4059a34a55277adbd2a2337239827cab96d962e/docs/flora-design/vp1-629/previews/original-ipad-landscape-lloyds-inside.jpg) | [Desktop Facts](previews/lloyds-inside-facts-desktop.jpg) · [iPad portrait Insight](previews/lloyds-inside-insight-ipad-portrait.jpg) · [Mobile collapsed](previews/lloyds-inside-facts-mobile.jpg) · [Mobile open](previews/lloyds-inside-mobile-open.jpg) |
| Lloyds Forces | [VP-1 illustrated Forces](https://github.com/rdidale-jpg/CIOS/blob/f4059a34a55277adbd2a2337239827cab96d962e/docs/flora-design/vp1-629/previews/original-ipad-landscape-lloyds-forces.jpg) | [iPad Facts](previews/lloyds-forces-facts-ipad-landscape.jpg) · [iPad Insight](previews/lloyds-forces-insight-ipad-landscape.jpg) |
| Banking cohort | The cohort postdates VP-1 | [NatWest](previews/natwest-landscape-facts-ipad-landscape.jpg) · [HSBC](previews/hsbc-uk-forces-facts-ipad-landscape.jpg) · [Nationwide](previews/nationwide-landscape-facts-ipad-landscape.jpg) · [Starling](previews/starling-inside-facts-ipad-landscape.jpg) · [Bank of England](previews/boe-inside-facts-ipad-landscape.jpg) |

The captures review visual hierarchy and available information. Their viewport crops show the initial visible region. Lower sections remain reachable via the live route. Count and presence of visuals supplement screen review and cannot assess commercial quality by themselves.

## Exact-source checks

The hosted FLORA validation run succeeded on the inspected release SHA. A focused local rerun passed 197 existing tests covering the visual shell, Facts-first navigation, global experience, Banking depth and Banking cohort. Pytest emitted a dependency deprecation warning. These are checkout tests. The browser checks below use the public Render origin. [Hosted exact-main validation](https://github.com/rdidale-jpg/CIOS/actions/runs/44407873433)

The five cohort selections are contextual enterprise views under `/industries/banking?selected=…`. They are reachable in Landscape, Inside and Forces. Use the selected legal-entity or institutional label to verify identity. The headings and scope show four separate models across five selections. NatWest and HSBC share a service-led pattern. The other Inside views reuse the same visual grammar even when their conceptual activity varies.

| Release input | Merged commit | Diagnostic relevance |
| --- | --- | --- |
| #671 | `ad5345f7379e3b22b4a2ef012b7036170726e8d0` | Shared Facts-first reading modes |
| #675 | `15a950e4fe641e5f80bd432e95e1aff2d86dd8bf` | Banking editorial illustration |
| #677 | `df475865cc367a28f355c38bc4c23054abe88502` | Banking economic stage depth |
| #692 | `2757e459f90fc4e1156180acf5f7ed9a40c292d9` | Banking cohort and expected release |

## Live results

- All 176 view requests returned HTTP 200 with the requested Facts or FLORA Insight control selected. All 44 desktop Main text comparisons matched a local checkout of the inspected SHA exactly. There was no document-level horizontal overflow in the sampled views. These are sampled guest results, not a claim about all paths or visual equivalence of every pixel.
- All seven scene images sampled from rendered wide views downloaded successfully and matched bytes served by the local checkout. The JSON records the body SHA-256 and byte count. Image entries on closed disclosures can refer to unloaded resources. Use the captures and the expanded mobile check to assess visibility.
- Lloyds Inside opened its illustrated scene on mobile and successfully decoded the image, including by emulated touch with JavaScript disabled. With print media emulated, computed display for the Left region was `none`. Browser screenshots corroborate the closed and open layouts.
- The capture set contains 43 public browser previews. The inventory records viewport, heading, state and asset evidence rather than authenticated content. [Browser and asset evidence](render-evidence.json) · [Complete capture set](previews)
