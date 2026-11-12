# Technology owner-testing journey

Implements the owner-accepted visual direction and end-to-end commercial journey above the preserved PR #571 prototype (`22b8527ba1ce111e366f3b326895a32b7a55140c`). **Beautiful simplicity** is the governing screen-design principle: artwork first at industry level, useful insight at market/enterprise level, practical tables and clear next actions in Pipeline. No merge or deployment.

## Walkthrough

Entry: `/industries/technology/experience`, also linked from the Industries catalogue and original Technology prototype.

1. Select **Cloud & data centres** in the artwork, then **Explore this area**. The eight districts remain addressable by keyboard and by the text-navigation alternative.
2. Read the market benchmark, delivery constraints, potential needs and existing macro-category links. Select **Equinix** from the real provider population.
3. Open a financial figure or **Business & financials** for reporting detail. **Strategy & investment** distinguishes reported expansion drivers from Flora analysis. **Explore enterprise** opens the conceptual operating view.
4. Switch between **Facilities** and **Interconnection**. These are conceptual activity areas, not an asserted organisation chart. Potential sales angles remain hypotheses.
5. Open **Pipeline** at industry, district or enterprise level. Both the primary navigation link and contextual link inherit that scope. Equinix initially has no preview opportunity: a research hypothesis is not silently promoted.
6. Add an **illustrative** enterprise-scoped opportunity explicitly, or use the fictitious examples in the industry table. Search, stage/owner filters and numeric/date sorting work. Selecting a title opens quick detail; **Open full opportunity** opens the detail screen. The date pencil opens editing with that field focused.
7. Edit dates, value, ownership, stakeholders, buying need, next action, procurement and competition; change stage; add a note; reload to test tab-local continuity. Reset restores the illustrative seed rows.

The CI workflow adds the owner-journey tests as a separate required step and supports review against the preserved #571 branch. Its 1,432-case baseline, 388-test strict-security selection, inherited exception records and comparator are unchanged.

The live Pipeline remains available through the collapsed supporting links, with its existing sign-in and workspace checks. This owner-testing slice does not read or mutate it.

## Implementation boundary

- New presentation module, approved generated artwork, CSS and small vanilla-JavaScript interaction layer. No application dependency or build step added.
- Six finite HTML routes and three exact extension-free asset routes. The existing public-path grammar, duplicate-query rejection and private-access guards remain unchanged. No new POST/API endpoint.
- Approved master artwork is a separate WebP asset (1536×1024). Image-relative district geometry is in `DISTRICTS`, outside the research model. A dedicated artwork frame keeps coordinates aligned when the selected card moves below the image on small screens. Replacing art requires a reviewed geometry update, not rewriting research logic.
- Original three-lens SVG prototype, 80 provider views, 34 programmes/relationships, six unqualified themes, evidence links, handoff and research JSON remain available. Only an additive visual-experience link was added to the original landing view.
- Existing Banking, Aviation, Macro, live Pipeline, source importer, review/promotion, canonical registry and Evidence/Observation owners remain unchanged. No agents or runtime paid-model calls.
- Sales examples use browser **sessionStorage**, not localStorage, a backend table or the existing Pipeline store. Explicit preview editing persists through reload within a tab. It is not a shared CRM, durable sales system or workspace record. Fresh browser contexts do not retrieve those edits. Storage failures show a clear message and fall back to in-memory interactions.
- All user-entered strings are rendered as text/escaped markup. Dates and non-negative full-term contract value are validated. Close dates earlier than opening dates are rejected. Missing value remains “Not set”, rather than zero. TCV is GBP, excluding VAT; start date means opportunity opened, close means expected signature.

## Public presentation data

Checked 12 November 2026. These are source-attributed presentation facts, not newly accepted canonical intelligence. The existing source/candidate/evidence architecture and withholding decisions remain authoritative.

| Item | Scope and source |
| --- | --- |
| £10.5bn public cloud spend | UK, 2024, IaaS/PaaS; [CMA 2025 final decision](https://assets.publishing.service.gov.uk/media/688b20e6ff8c05468cb7b120/summary_of_final_decision.pdf). Not a combined cloud/data-centre district valuation and not a claim of 2026 market value. |
| Power, grid and planning constraints | [House of Commons Library briefing](https://commonslibrary.parliament.uk/research-briefings/cbp-10315/). General market context, not a finding about a named enterprise. |
| Equinix financials | Latest available annual filing checked: FY2025 Form 10-K, filed 11 February 2026. [Annual filing](https://investor.equinix.com/sec-filings/all-sec-filings/content/0001101239-26-000032/eqix-20251231.htm), consolidated statements and Note 18: $9.217bn revenue, $6.475bn colocation, $1.655bn interconnection. Global group, USD, not UK entity revenue. The two service lines do not exhaust group revenue. Annual baseline, not the latest quarterly trading update. |
| Enterprise identity | Equinix, Digital Realty and VIRTUS reuse existing selected provider views. No new canonical enterprise entity. UK operating and contracting scope remains unresolved. |
| Macro | Reuses existing category IDs `technology`, `economy`, `sustainability`, `cyber`. Category selection opens a Technology-specific interpretation over the existing industry context. It does not inherit the shared Macro prototype’s default Banking applicability, invent enterprise duties, or quantify opportunities. The shared cross-industry Macro reference remains a separately labelled supporting destination. |
| Sales angles | Flora analysis for investigation; no confirmed requirement, budget, mandate, buyer, procurement or current contract. The cooling/interconnection model is conceptual and the illustrated campus is not an Equinix facility. |

## Verification and remaining limits

See `Validation.json` and `previews/Browser-Results.json` for completed results. New HTTP tests cover finite routing, scope inheritance, native navigation, synthetic data boundaries and asset safety. The browser check exercises the accepted journey, image alignment at four viewport sizes, 24 keyboard district activations, scope/search/filter/sort, creation/editing, stage persistence, date rejection, escaped notes, fresh-context isolation, no-JavaScript reading, blocked-storage fallback and print/reduced motion.

Physical iPad/Safari and screen-reader user studies remain owner-testing tasks. Chromium viewport simulation does not substitute for them. The sparse master art does not convey every enterprise relationship. Non-cloud districts retain explanatory/provider research rather than fabricated market figures. The real Pipeline's durable/authenticated CRUD and cross-workspace behaviour are intentionally outside this preview; its existing implementation remains in place.

## Local preview and rollback

Run from repository root with an isolated scratch data directory:

```sh
FLORA_DATA_DIR=/absolute/scratch/preview-data HOST=0.0.0.0 PORT=8793 python -m cios.applications.flora.web.app
```

Open `http://localhost:8793/industries/technology/experience`. The process is a local development preview, not a deployment. Runtime storage must never point at an owner's live data just to test these screens.

To roll back, stop the preview and revert this feature branch/commit. The original prototype is still at `/industries/technology`; no research or live Pipeline migration needs reversing. Browser-only preview edits can be removed with **Reset preview changes** or by clearing that tab's session storage. Review and integration are separate future steps; #568/#569/#570/#571 were not merged or retargeted.

### Browser captures

[Arrival](previews/arrival-desktop.png) · [Selection](previews/selection-desktop.png) · [Market](previews/market-desktop.png) · [Enterprise](previews/enterprise-desktop.png) · [Conceptual enterprise](previews/enterprise-model-desktop.png) · [Pipeline](previews/pipeline-desktop.png) · [Opportunity](previews/opportunity-desktop.png)

[iPad portrait selection](previews/selection-ipad-portrait.png) · [iPad landscape Pipeline](previews/pipeline-ipad-landscape.png)
