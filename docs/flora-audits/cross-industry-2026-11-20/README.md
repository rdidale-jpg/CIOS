# FLORA cross-industry presentation audit — 20 November 2026

**Finding:** FLORA has substantially more research and reusable runtime capability than its current experience consistently presents. It has **three public industry journeys** (Banking, Aviation, Technology), but the accepted Top / Left / Main and Facts / FLORA Insight pattern is concentrated in UK/Banking/Lloyds and the easyJet visual preview. The other represented industries are source populations, research foundations or conditional imported workspaces, not equally implemented illustrated Twins.

Audited **current main: `03719d7573f087c65d9622719273aa4b89caf7d3`**; its [full main CI passed](https://github.com/rdidale-jpg/CIOS/actions/runs/44548522149). This is a documentation-only assessment branch from that commit. **No production deployment identity, private workspace registry or canonical store was inspected.** “On main” below means repository implementation, not a claim about what Render currently serves.

## Read the report

- [Industry coverage and all ten presentation dimensions](Industry-Coverage.md).
- [Enterprise presentation inventory and population boundaries](Enterprise-Presentation.md), with [371 owner-qualified records](Enterprise-Inventory.csv). These are **not 371 unique or accepted enterprises**.
- [Specific evidenced gaps, reuse, dependencies and risks](Gaps-and-Reuse.md).
- [Priorities, smallest next sprint and owner decisions](Next-Decisions.md).
- [Source paths / design-reference map](Evidence-Map.md), [reproducible repository counts and hashes](Repository-Evidence.json), [actual responsive browser observations](Browser-Observations.json).
- [Validation, limits and self-critique](Validation-and-Critique.md).

## Main versus pending design/implementation

| Reference | Actual disposition at audit | Use in this assessment |
| --- | --- | --- |
| [Experience Contract](../../product/flora-experience/FLORA-Experience-Contract-v1.0.md) | Owner-agreed product direction; document explicitly distinguishes target from runtime and ADR authority | Assessment criteria, not proof of every feature existing |
| [PR #631](https://github.com/rdidale-jpg/CIOS/pull/631), `f4059a34a55277adbd2a2337239827cab96d962e` | Design PR remains draft/unmerged; its accepted three-panel direction is implemented through merged VP-2 #633 | Established shell, original-art fidelity, contextual streams, responsive Left and accessible Main |
| [PR #700](https://github.com/rdidale-jpg/CIOS/pull/700), `393e0467adfd5791f3a97447c86ed71a2950e6aa` | Design-only; Option A accepted as architectural/UX direction | Economics belongs within Landscape; no global toggle or invented capability allocations |
| [PR #701](https://github.com/rdidale-jpg/CIOS/pull/701), `a89fcbcc51d94eddb4e73dd9646d036244145dc3` | Validated draft implementation, **not merged into audited main** | Reusable pending Economics implementation; do not count it as main or rebuild it in another sprint |

## Practical conclusion

**Banking is the reference implementation, not a universal industry template.** Nationwide has the most directly visible admitted company financial slice; Lloyds combines the richest bespoke illustration with bounded released financial context and a still-inactive restricted slice. easyJet has a useful interactive operating-system preview, but its normal Industry/Enterprise entrances remain legacy. Technology already has 80 provider views, eleven comparison-metric rows, a substantial NVIDIA profile and an Equinix journey; its principal gap is integration with the shared presentation/semantic/lifecycle pattern, not a missing directory.

Telecoms/Media/Sport have real retained packages and generic import/runtime owners. Energy/Utilities/Public Sector have retained source and research populations; MOD also has a package and generic enterprise support. Insurance has a placeholder domain and broader sector/subsidiary context, not a dedicated implemented Insurance Twin. The remaining UK sectors have national labels and partial foundations, not standalone interactive journeys.

**Recommended smallest next implementation:** consolidate **catalogue / Aviation → easyJet entry points** onto the existing three-panel Enterprise experience, preserving legacy specialist links and source boundaries. Do not rebuild the Industry screen, admit financials, add News or generate artwork in that sprint. Review #701 separately and reuse it only after authorised integration; do not rebuild its Economics work. Broader Aviation Industry and Technology alignment then follow as distinct workstreams. See the exact scope and acceptance boundary in [Next-Decisions.md](Next-Decisions.md).

No runtime, source rights, canonical data, permissions, Offers, Pipeline, Render configuration or production data changed. **Stop for owner review; no merge or deployment.**
