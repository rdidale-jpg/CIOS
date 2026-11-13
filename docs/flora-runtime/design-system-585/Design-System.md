# FLORA unified visual system v1

Implements #585 using the owner's [visual acceptance of #584](https://github.com/rdidale-jpg/CIOS/pull/584#issuecomment-6852990986) and #581's editorial direction. Approval of the visual language is not release authorisation. This candidate changes application presentation on a separate branch; main, #580 and #584 are unchanged.

## Shared components and ownership

`design_system.py` owns presentation primitives, not intelligence or sales state:

- **One product header**, beside FLORA: Home, one-step PESTLE and a compact Explore disclosure. Explore contains canonical destinations, current-view actions, specialist tools and the existing secure account controls. The existing `navigation.PRIMARY` registry is the single destination owner. The protected live Pipeline link is never silently replaced by the Technology tab-local demo.
- **One Sources & method disclosure per view**. Existing renderers contribute already-authorised, escaped source fragments. Publication/reporting periods, source URLs/locators, counter-evidence, missing scope, rights/acceptance and assessment metadata remain available there. No client fetch or parallel Evidence model is introduced.
- **A scoped render buffer** uses ContextVar isolation and exception cleanup. Successful nested presentation shares the current view; failed nested rendering rolls back partial notes/context links. Independent/concurrent seller and public renders cannot inherit one another's buffers. Nothing is cached or persisted.
- **Economic context** reads the exact approved Home statistical extract. Technology's 6.6% is Information & communication, Banking's 8.1% is Finance & insurance, Aviation's 3.6% is Transport & logistics: broader SIC sections, not invented sub-sector market sizes. All are UK GVA shares, 2024, current basic prices. Definitions/rounding remain in Sources.
- **Image surface and native insight** primitives use the approved ivory/sage/forest palette, restrained serif headings/sans body, 44px controls, visible focus, gentle CSS edge feather and a concise over-image reveal. PESTLE retains all six factors and its source/country boundaries. Equinix demonstrates the pattern with its two existing conceptual areas, not a new organisation model.

Shared CSS/JS is served through two exact extensionless public asset paths. Native links, GET selectors and disclosure controls work without JS. The small shared script adds Escape, focus return and opening an explicit source-fragment target. It cannot call a model, fetch commercial data, store business state or write Pipeline.

## Surface archetypes

**World / industry:** illustration and labelled regions first, a short scoped scale line, no below-image briefing modules, Compare/Pipeline shortcuts or trailing Explore. The 20-sector UK artwork and Technology campus remain byte-identical to the approved assets. Phone Technology keeps eight readable labels on the image, rather than a second navigation list below it.

**Participants:** retain the shallow native industry banner and six sortable columns. Only the company name is a row link; reported/EST values are plain text, unsupported cells stay blank. Numeric sorting, descending/ascending direction, search, membership overlays and all 80 participants retain their original owners. Range/method/source detail moves to the single header disclosure.

**Enterprise:** financial context and useful commercial density take priority over decorative art. NVIDIA has three main groups: At a glance, Commercial ecosystem, Potential sales plays. Global annual and quarterly periods, revenue/profit/margin/workforce, every existing priority/pressure/relationship/programme and all three hypotheses remain. Buyer roles are visible; a role-only supply-chain hypothesis explicitly leaves the buying account to be established. No buying account is assigned to NVIDIA or a supplier without evidence.

**Commercial workspace:** Offers, discovery and Pipeline adopt the header/type/palette without sacrificing editable fields, approvals, version checks, filters, accessible records or warnings. A form reset, record return and explicit manual qualification link are workflow controls, not repeated global navigation. Studio remains opt-in/off by default. No offer content is copied to Pipeline by following a link.

## Information rules

Reported figures keep scope, currency and period. The issuer's own approximate workforce qualifier stays `c.`; FLORA-derived defensible estimates require visible **EST**, range, basis and sources. Unsupported metrics remain absent. GVA is not revenue, GDP at market prices or a sales market; global group numbers never fill UK participant cells. No sector geometry/building size encodes economic ranking.

Source consolidation does not make partial research accepted, resolve an enterprise identity, establish rights, prove customer demand or qualify a deal. Material conceptual/announced/proposed status, buyer-account uncertainty and essential legal/operational/security warnings remain meaningful. Source dates are not refreshed by rendering. The UK-only world does not change seller geography or apply UK law to France; advanced country-specific macro routes remain available without a forced UK label.

The unchanged-owner manifest protects research data/models, permissions/authentication, employer context, Offers engine/approvals/persistence, Pipeline writer, security tests, the versioned comparator and release helpers. Only presentation owners and presentation-specific assertions are adapted. No paid runtime model, autonomous agent, outreach, research enrichment or production mutation is introduced.
