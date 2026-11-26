# Beautiful Simplicity: visual and rendering diagnosis

**No design or runtime fix was implemented.** Raw screenshots precede diagnostic callouts. The overlays exist only in the isolated browser session and identify evidence; they are not proposed UI. The app, artwork and styles remain at the deployed baseline. [Machine geometry, routes and file hashes](previews/Browser-Diagnostic.json).

## Reproduction boundary

Desktop 1440×1000; emulated iPad landscape 1194×834 and portrait 834×1194; Chromium Guest public views, default zoom and reduced motion. Nineteen desktop selections and seven corresponding tablet selections give **33 measured views**; the 96-state semantic census is a separate measure. A4 PDFs use default existing app print CSS with 10mm margins. PDFs reproduce FLORA output, not publisher reports. No authenticated workspace state, private intelligence, real iPad/Safari or owner-supplied PDF was available.

Render verifies this exact code is live. Direct browser access to that service is unavailable under the existing execution network policy; these are **same-code isolated reproductions**, not live geometry certification. No egress, Source or production permission was changed. Exact live reproduction of the owner's particular defect remains an explicit limit.

## Representative evidence

| Problem | Desktop | iPad landscape | iPad portrait |
| --- | --- | --- | --- |
| Technology title forced into icon column | [Annotated](previews/desktop-credit-layer-annotated.jpg) / [raw](previews/desktop-credit-layer.jpg) | [Annotated](previews/ipad-landscape-credit-layer-annotated.jpg) / [raw](previews/ipad-landscape-credit-layer.jpg) | [Annotated](previews/ipad-portrait-credit-layer-annotated.jpg) / [raw](previews/ipad-portrait-credit-layer.jpg) |
| Conceptual economics blocks displace substantive figures | [Annotated](previews/desktop-economics-annotated.jpg) | [Annotated](previews/ipad-landscape-economics-annotated.jpg) | [Annotated](previews/ipad-portrait-economics-annotated.jpg) |
| Commercial Banking has little business-specific substance | [Annotated](previews/desktop-commercial-annotated.jpg) | [Raw](previews/ipad-landscape-commercial.jpg) | [Raw](previews/ipad-portrait-commercial.jpg) |
| Long conceptual credit layers and limitations | [Annotated](previews/desktop-credit-annotated.jpg) | [Annotated](previews/ipad-landscape-credit-annotated.jpg) | [Annotated](previews/ipad-portrait-credit-annotated.jpg) |
| SWOT works as selection, but labels are not a commercial argument | [Annotated](previews/desktop-swot-annotated.jpg) | [Annotated](previews/ipad-landscape-swot-annotated.jpg) | [Annotated](previews/ipad-portrait-swot-annotated.jpg) |

Additional raw views include all default subjects, Costs, Capital and the credit detail. Group and Strategy also have desktop callouts. The image folder contains 57 hashed diagnostic files, including three app PDFs and their first-page renderings.

## Separate the four reported rendering concerns

| Concern | Observed reproduction | Root cause / confidence | What is not established |
| --- | --- | --- | --- |
| **Severe text wrapping** | Credit technology/data/infrastructure/contract titles are exactly **65 CSS px wide** in all three tested viewports; “Technology / infrastructure” wraps to six lines | High confidence: `.canvas-layer-stack` defines 65px icon + flexible content columns. A region also has class `.canvas-technology`; the later `.canvas-technology .canvas-mark` rule makes its icon absolute, taking it out of grid flow. The unassigned title then occupies column one. Computed layout records the 65px width and absolute icon | Not evidence of missing facts; not a browser-wide font or only-PDF issue. No CSS was repaired |
| **Icons competing with text** | Computed icon/title bounding boxes intersect in 14 of the 33 views; arrow/title boxes intersect in 11. Representative Commercial Banking and credit captures visibly show the icon/text collision | Region/container class reuse and shared selectors apply container icon positioning to individual targets. Absolute glyphs lack protected layout space. Box intersection is a candidate diagnostic; visible glyph collision was inspected in representative images, not asserted for every box | Not every geometric intersection is a visible collision. Hover/focus and clickability passing do not establish visual quality |
| **Clipped numerical values** | No overflow was detected in the selected `.gold-stocks strong`, `.le-measure strong` and title boxes; no page horizontal overflow in the 33-view sample | **Not reproduced in this bounded sample.** Amount fields in the inspected A4 economics page remain legible | Does not refute the owner's report. Other selections, zoom/font/browser, authenticated content or an original PDF could differ. No claim that all values or all environments are free of clipping |
| **Excessive target sizes / low information density** | Economics is 2,082px high at desktop and 2,270px in iPad landscape; strategy 2,737/2,729px; credit 2,494/2,512px. In iPad landscape only 2 of 9 strategy targets meet the first viewport. Four conceptual mechanism targets precede most financial content | Explicit min-heights/padding and repeated diagram marks consume space irrespective of evidence density. Some panels restate a concept or unavailability instead of adding an enterprise-specific answer. Vertical scrolling itself is not a defect | No invented “beauty score” or target height threshold. These are diagnostic measurements supporting an editorial critique |

## Screen versus PDF

- [Economics PDF](previews/print-economics.pdf) and [first page](previews/print-economics-page1.jpg): three A4 pages, extracted text lengths 779 / 993 / **63** characters. The last page is effectively sparse footer/continuation content. The screen layout becomes a fragmented document without a dedicated print composition.
- [Credit PDF](previews/print-credit.pdf): three pages; [first page](previews/print-credit-page1.jpg). Main's large conceptual layers survive into print and extend the journey across pages.
- [Strategy PDF](previews/print-strategy.pdf): three pages; [first page](previews/print-strategy-page1.jpg). Goal rails are not a compact progress/decision view. Dates describe different disclosure/target horizons, not a uniform delivered timeline.

These are export-specific consequences in addition to the screen CSS collision. PDF text extraction is not a complete clipping detector. Physical printing and the owner's original PDF have not been inspected. No source table was copied and no restricted financial output activated to produce these diagnostics.

## Architectural support and inhibition

**Keep:** the premium original artwork, warm palette, three-region frame, native accessible links, URL/history behaviour, Source withdrawal, precise caveats and separate inspection. The existing finite presentation functions can accommodate richer eligible facts without replacing the intelligence owners.

**Change later, after content recovery:** scalar decorative shapes and repeated large tiles are standing in for business economics, organisation and actual dependencies. The current Lloyds `scene()` uses the same `twin.ART` Inside scene for all three streams, with different labels. Original Landscape/Forces assets are retained, but byte preservation is not the same as using their differentiated story. That is a future composition decision, not permission for another artwork programme.

The CSS reuses semantic type names as layout-container names, causing selector leakage. The old and CEO composition paths coexist in one module; canonical routes dispatch to `_ceo_journey`, `_ceo_people`, `_ceo_financial` and `_ceo_goals` for relevant states. Audits must inspect the path actually executed, not the similarly named older helper alone. Current tests are strong on allowed navigation and authority; they cannot establish commercial information value just by counting click targets or passing no-horizontal-overflow checks.

Future prototypes should show one enterprise-specific relationship or causal economic mechanism per selection, with the right amount of qualified evidence. They should reduce repeated disclaimers and placeholder tables without suppressing material uncertainty. First secure the facts and the intended commercial answer; do not hide an absent answer behind a prettier tile, more click-downs or a fictional graph.
