# FLORA Visual Intelligence v1 — design and reuse

Baseline verified before development: main `5e93023df8b9410fef22a0340095f94530d6e8ad` (Research Intelligence v3 merged). [Actual post-merge push CI](https://github.com/rdidale-jpg/CIOS/actions/runs/42798558756) passed. Deployment state is not inferred.

## Visual capability inventory (before implementation)

| Existing capability | Actual implementation | Reuse / bounded extension |
| --- | --- | --- |
| Product shell and five-part navigation | `unified_views.page`, `_flora_v2_page`, current Industries/Enterprises/Opportunities/Pipeline routes | Keep the shell, breadcrumbs, private Pipeline boundary and legacy routes. Add contextual lenses on the existing pages |
| PESTLE | Six-part linked ring in `visual_templates.pestle` | Retain; use framework forces as evidence-linked pressure labels in the signature landscape |
| Five Forces | Standard five-position geometry in `forces` | Retain direct lens, no new market-position scoring |
| Value chain | Linked chevrons in `chain` | Reuse existing structured activity names and links in sector-specific illustrations; retain original diagram |
| Capability / operating model | Four-column conceptual capability boxes in `operating` | Retain as the detailed capability lens; add an illustrated, enterprise-specific operating-story layer |
| Supplier ecosystem | Explicit solid / reported-unknown dashed relationships in `ecosystem` | Retain; new activity details link to this view and preserve dated relationship/contract limitations |
| Opportunity landscape | Existing independent ordinal dimensions and account-specific ranks | Retain unchanged, separate from knowledge/operating views; never imply qualification |
| Aviation / easyJet illustration | `sector_views` is a thin adapter; `operating_model` currently renders the shared value-chain geometry. Existing screenshots/specs show capabilities, not a separate reusable illustrated scene engine | Evolve the common SVG vocabulary with airline activities, runway/aircraft/terminal context; no parallel aviation app |
| Visual specifications | `visual_specs.build_visual_specs`, `validate_visual_spec`; six public JSON specifications | Preserve the six-contract API. Add a derived specification extension for signature / illustrated operation / timeline, using the same source IDs, node metadata and validator principles |
| v1 / v2 research | Finite diagnostic pages, source importer, deterministic cycles/checkpoints, Researcher mission generation | Read current source/gap data, no new research system or acquisition in this increment |
| v3 understanding | `understanding.assess`, scoped exact-support reviews, canonical SemanticTwin relationship resolver, contradictions and dated candidate passages | Carry evidence class, entity/period, interpretations and unresolved dependencies into the visuals |
| Canonical intelligence | SemanticTwin / SemanticObject, EvidencePackageItem, SourceSegment / CandidateClaim, existing graph and Observation identities | Presentation projections only; no new canonical graph, store or automatic promotion |
| Public/private boundary | Exact `public_routes` catalogue; public research overlays versus governed Canvas / account / Pipeline authority | Keep exact route boundaries. New lenses accept no workspace/resource selector. Source and evidence destinations remain finite public views |
| Responsiveness/accessibility | Inline SVG, existing teal/cream system, native links, details, keyboard focus, text alternatives and diagram-local scrolling | Extend with consistent state badges, selection, reduced-motion support and small dependency-free progressive enhancement |

## Three levels

**Understand:** signature panorama or illustrated operating system; a few properly scoped metric disclosures; visible uncertainty. The intended 30–60-second reading target is unmeasured.

**Explore:** select an actor/activity/pressure, switch existing lenses, investigate a seven-lane timeline or an AI-disruption scenario lens.

**Investigate:** native detail panels with purpose, applicable capabilities, dated source claims, supplier/contract limits, conflicts and research questions; retain existing Evidence, Understanding and authorised Pipeline destinations.

## Visual grammar

- FLORA forest green = business structure and attributable disclosures; warm sand = interpretation; amber/diamond = explicit Unknown; plum/dashed outline = hypothesis/scenario; rust/split marker = contradiction. Always accompany colour with text and shape/dash semantics.
- Equal-sized actor/activity markers describe categories and navigation, **not** market share, spend, influence or value. No unmeasured ranking or proportional sizing. Numeric cards state entity/geography, unit, measure, source period and forecast/actual status separately.
- Illustrated terrain, terminals, bank buildings, aircraft, rails and symbols provide conceptual context, not verified topology or ownership. Factual labels, data and selectable elements remain SVG/HTML layers generated from the specification.
- Solid relationship lines are allowed only for the scoped supported relationship they represent. Dashed conceptual activity flows are explicitly illustrative; co-location never establishes a relationship or proven causation.
- Timeline: dated historical disclosure, current-at-snapshot condition, announced commitment, forecast and scenario are different labels/symbols. Year/half-year/range precision is retained. Unknown dates have an undated shelf, never a fictional point on the time axis.
- Every material object retains original reference IDs, evidence/source references, scope, applicable/reporting dates, state, limitations and a navigation destination. Presentation-only activity slots do not become canonical graph objects.
- Selection is progressive enhancement over native anchors/details. Equivalent text navigation is always present. Focus is visible; reduced motion has no loss of meaning. Large scenes pan internally; the page must not overflow.

## Data boundary and reproducibility

Existing assessment overlays and v3 reviews remain unchanged. New presentation profiles contain activity organisation, icon choices, labels, research-reference mappings and explicitly labelled conceptual/scenario interpretation. They cannot turn missing measurements, relationships or dates into facts.

The builder validates references against the existing intelligence, resolves evidence through current contracts and pins all input digests plus an explicit research cut-off. Rendering contains no company facts, dates, metrics or market rankings embedded in drawing code. A changed research snapshot changes its derived visual; earlier accepted/candidate history is retained by its owning system.

## Planned priority slice

1. Banking and Aviation signature landscapes, with distinct sector illustration and a shared grammar.
2. Lloyds and easyJet operating-story scenes, retaining the original detailed capability/supplier/opportunity lenses.
3. Both strategic timelines with seven lanes, accessible filtering, actual precision and explicit unscheduled gaps.
4. AI-disruption lens over the same signature scene; no invented AI-native entrants or displacement dates.
5. Desktop/tablet/browser/strict CI validation, before-and-after captures and an executive-comprehension protocol. No measured comprehension claim without actual participants.

Sparse knowledge is displayed honestly. Banking market size/employment, named AI-native entrants, current enterprise dependency/contract scope and many programme readiness/causal outcomes are not established by current research. They are visible gaps, not artistic licence.
