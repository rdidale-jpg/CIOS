# VEX-1 integration and provenance

Issue [#612](https://github.com/rdidale-jpg/CIOS/issues/612) authorises this application implementation, with no merge or deployment. The implementation branch starts at validated main `0cb07c2e78ccb16240c799b31cd62736e2135529`, not at design PR #610. The reviewed design is `c6bf2280594922db6951c5c36205984c85ca4aea`. No rejected or historical prototype page is imported.

## Existing owners, new presentation

| Responsibility | Owner / integration |
|---|---|
| HTTP, session/origin, forms and CSRF | Existing `FloraWebHandler` and security services; all requests still enter the existing request guard. No new forms or mutations. |
| Public vs private identity | Existing finite `public_route_catalog`; exact public Banking/Lloyds references, not a prefix or an arbitrary Enterprise Model lookup. |
| Industry/Enterprise research | Existing validated `research_intelligence.model.load_assessment`, registry public references and original source snapshots. |
| UK economic basis and macro | Existing `visual_v2.basis` / `insight`, macro context and original country-source filters. |
| Fact/interpretation/target/history | Existing `claim_state`; current statements, reporting periods, metric values, source URLs and limitations are resolved at render time. |
| Material Pressure | Accepted ADR-026 and existing canonical runtime remain authoritative. No qualification call, object creation, store or ranking is added. These Forces are public research and labelled interpretations. |
| Private Canvas | Existing authorised Canvas service remains separate. A public reference ID never resolves or enumerates private Canvas, Evidence, workspace, Offers or Pipeline records. |
| Product and verified account navigation | Existing design-system header and account resolver, with an optional compact mode used only for these scenes. Other consumers keep their existing presentation. |
| New visual component | Stateless `visual_streams.Context`, finite scope bindings, presentation geometry and native server-first URLs. No session, browser storage, intelligence store, matcher or model call. |
| Offers, seller development, Pipeline | Existing owners/services unchanged. Their global navigation remains available; visual browsing never captures or qualifies an opportunity. |

The bounded pilot is UK → Banking → Lloyds. Banking's five major banks are equal direct enterprise links; Lloyds opens Inside. Other banks retain their existing public profiles. Aviation and Technology keep their current experiences and genuinely available UK links. No Inside/Forces controls are invented for unsupported enterprises. The scope/stream/context renderer is shared; additional approved bindings need their own sourced projection and artwork, not an enterprise-specific URL-prefix permission rule.

## Route contract

| Route | Default / supported views |
|---|---|
| `/`, `/flora`, `/flora/` | UK Landscape; `stream=landscape` or `forces` |
| `/industries/banking` | Banking Landscape; `stream=landscape` or `forces` |
| `/enterprises/lloyds` | Lloyds Inside; `stream=inside`, `landscape` or `forces` |
| Existing explicit `?lens=...` specialist links | Retained by their original renderer. Mixed `lens` and stream selectors fail closed. |
| `/visual-v2` and `/pestle` | Existing visual study and six-factor PESTLE retained; UK Forces is a distinct parallel view, not a replacement evidence owner. |

Optional `market=GB` is exact and UK-only. Layers are `enterprises`, `suppliers`, `regulators`; UK accepts only its default layer. `selected` is a finite public industry/bank selection compatible with scope; a Lloyds view cannot select another enterprise. `detail` must be present in the current stream's supported interactive labels. Missing, duplicate, empty, incompatible, foreign-country, private-entity and unknown selectors fail closed. No country/workspace/role is inferred from a client header.

Every stream switch is a native link. It preserves scope, compatible selected bank/industry and layer, while clearing a focused topic that has no corresponding meaning in the destination stream. Back from Lloyds restores Banking with Lloyds selected. Browser history and copied URLs require no JavaScript. A small script adds focus/Escape and missing-image feedback only; it does not fetch or manage navigation state.

Context layers highlight the relevant existing labels; they do not assert a relationship, apply a ranking or add new actors. The country artwork retains all 20 original labels and green outlines only on currently public, registered industry journeys. Selected industry state survives a UK lens switch and is highlighted again on Landscape.

News, Topic Cards, Tools and Enterprise Builder remain future scope. Only implemented global tools appear in the existing Explore menu. There is no placeholder CTA or new modelling engine.

## Source-to-view mapping

| View | Existing bindings and truth limits |
|---|---|
| UK Landscape | Original 20 SIC 2007 districts; 2024 current-basic-price GVA and distinct three-month real GDP growth from the existing ONS presentation basis. Area/building size is not scale. |
| UK Forces | Existing UK `economic`, `technological`, `legal`, `environmental` insights. UK-only source IDs; no French-source substitution or universal enterprise applicability. |
| Banking Landscape | Public bank references; BoE monetary context, PRA prudential function within BoE, FCA conduct context, generic payments function. `REG-01` / `INF-01` remain unresolved; no firm-specific permission or participation edge is inferred. Finance & insurance GVA is broader than Banking. |
| Banking Forces | `UK-RATE-NOV26`, `UK-PRA-REPORT27`, `LBG-ENVOY-CONTROLS`, `UK-VALUE`; original periods, kind and verification remain attached. Enterprise examples are not sector-wide evidence. |
| Lloyds Inside | Deposits `LBG-Q326-DEPOSITS` are a stock; `LBG-Q326-PROFIT` is a nine-month flow. Strategy target `LBG-A2030-CIR` is not an actual. Brand timetable, Envoy and core/data priorities reuse existing claims. Current hierarchy, leadership, cost/income/growth and systems are not fabricated. |
| Lloyds Landscape | Customer/peer/infrastructure roles are conceptual context. Only the existing verified relationship decision supporting `LBG-ENVOY-GOOGLE` enables the named announced collaboration in detail. Withdrawing that decision suppresses the rendered relationship; the source register retains history. No named client, contract, workshare, exclusivity or renewal is invented. |
| Lloyds Forces | `LBG-A2030-PLATFORMS`, `LBG-A2030-CIR`, `LBG-ENVOY-CONTROLS`, `LBG-BRAND26-TIMING`; editorial affected-area questions are explicitly interpretation, with counter-evidence and unknown external need. |

Nine original deficiencies remain visible in optional detail: FIN-01/02, ORG-01/02, OPS-01, REL-01, REG-01, INF-01, COM-01. Business-language unknowns appear in relevant selected content; technical IDs stay in optional inspection. Existing primary excerpts retain their extent, dates, rights and source limitations. No research collection, refresh, promotion or new canonical fact occurs.

The renderer reads current source-owner claims instead of copying the prototype's prose as live facts. The accepted small on-image annotations are supplementary frozen captions; they disappear if any underlying source/basis pin changes. Rendered detail still comes from current validated sources. This prevents silently presenting a stale design annotation as refreshed intelligence.

## Exact artwork and delivery

[Accepted original hashes](Accepted-Artwork.json) pin all seven source files from the reviewed design commit. The [runtime artwork manifest](../../../cios/applications/flora/visual_stream_assets/artwork.json) retains original path, SHA-256, dimensions, byte size, rights/classification, and every responsive output hash. The original bytes remain unchanged in PR #610; no new image generation, crop, repaint or relationship drawing occurs. The existing original UK file in the application is also untouched.

The 21 WebP variants are proportional 768/1152/1536px encodings at quality 87 using Pillow 12.3.0; Pillow is an offline preparation dependency only. Runtime uses the standard library and existing dependencies. Overlay geometry is extracted from the seven reviewed primary HTML compositions into a presentation-only file; no historical prototype HTML/JS is served by the application.

Only the selected scene is requested. Two responsive halves share the same selected image resource; the right half is lazy and alternative streams are not prefetched. Original dimensions reserve layout space. DOM labels, native text links and stream controls remain usable if artwork fails. Native image `srcset`/`sizes` chooses a variant without client routing logic.

Image URLs use explicit extensionless content-addressed route keys, preserving the existing public-path grammar. The image handler verifies the full SHA-256 and rejects symlinks/traversal/unlisted manifest/config files. Only these pure public images receive immutable caching and ETags; HTML and presentation code retain `no-store`. No verified account details enter a shared image response. Conditional image requests can return 304.

## Changed-file overview

- `visual_streams.py` and `visual_stream_assets/`: projection/renderer, seven scene geometries, three responsive variants per exact original, manifests, CSS/focus enhancement.
- `design_system.py`: optional compact header; existing default callers remain unchanged.
- `web/app.py`: guarded scope dispatch, strict legacy/stream separation, pure immutable image delivery, existing HEAD type mapping and Home delegation.
- `public_routes.py`: explicit registered route/selector entries only; public path grammar and private-route authority remain unchanged.
- `.github/workflows/flora-validation.yml`: one additional VEX-1 test step; unchanged strict gate/comparator and existing suites.
- `tests/test_flora_visual_streams_612.py`: new navigation, source, staleness, relationship, asset/cache and permission negatives.
- Four existing presentation test files: targeted approved-default expectations, described in the review report. No tests are removed; no baseline, strict security test or skip is changed.
- `tools/ci/flora_visual_stream*`: reproducible asset preparation and isolated application preview/measurement tooling.
- This review directory: provenance, responsive before/after images, browser/performance evidence, acceptance and rollback.

No changes to canonical/research data, ADRs, security/IAM services, matching, Offers, seller-development or Pipeline services. PR #603/#609/#610 remain independent and untouched.
