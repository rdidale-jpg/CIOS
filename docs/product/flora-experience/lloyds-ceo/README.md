# Lloyds CEO intelligence

This increment deepens the optional Gold Standard experience integrated in #731. It keeps the illustrated Left, Landscape / Inside / Forces, existing default Lloyds and the original preview. Main at the start was `1c13e6962516dbb071b2133f2c1a3de87647e2ac`, with [successful hosted validation](https://github.com/rdidale-jpg/CIOS/actions/runs/45372064086). #729 remains a design proposal. #712 is a separate open refinement.

## CEO questions and coverage

| Question | Support | In the preview | Evidence needed for a stronger answer |
| --- | --- | --- | --- |
| How does Lloyds create value, and how do the businesses differ? | Supported for the business mechanisms. Partial for contribution. | Landscape → Group economics. Retail, Commercial and Insurance, Pensions & Investments retain distinct economics. Group deposits are dated stocks. Statutory profit has a nine-month period. The efficiency detail explains how to read costs, risk and capital alongside those results. | LEI-1 has income, fees, impairment, capital and H1 segment and statutory bridges. Exact figures and allocations are held for this use. No segment share or full earnings bridge is implied. |
| Who makes decisions, and how is work organised? | Partial for business and workforce context. Current named mandates, workforce trends and reporting lines are unsupported in this preview. | Inside → Operating model → Organisation, accountability & workforce. Explains the functions to trace and presents existing licence and role-announcement disclosures with their limits. | The Tier 1 F05/F06 leadership records remain subject to a Source decision. LEI-1 names are research context. Obtain comparable workforce totals, perimeter, costs and internal/external delivery before assessing productivity. |
| What is leadership trying to achieve? | Supported for the selected published priorities. Partial for progress. | Forces → Strategy & change → Goals & tests of progress. Separates current-period context, transformation and longer-term efficiency. The earlier disclosed migration milestone has a separate period. | Comparable baseline, progress and realised net outcomes, with accountable delivery roles. Targets and management plans have their own dates and are not treated as delivered. |
| How does work reach applications and suppliers? | Partial. Navigation supports exploration. Actual end-to-end dependencies and delivery obligations remain unresolved. | From Retail or Commercial, follow the credit journey into risk capability and platform renewal. From the customer service journey, follow data capability and colleague technology. Existing Envoy and supplier views retain scope and limitations. | Verified service and application inventory with ownership, deployment and dependency evidence. Relationship candidates and disclosed collaboration cannot establish current contracts. |
| What could prevent success, and what should sales investigate? | Supported as qualified analytical questions. Firm-specific impacts, urgency, buying mandate and procurement are unsupported. | Compare funding repricing, remediation versus efficiency and risk-weighted capacity. Use the existing Forces choices and SWOT for counterevidence, commercial questions and dependencies. | Matched financial comparators and measurable customer/service outcomes, tested against management responses and counterexamples. |

## Reconciliation and controls

- [LEI-1](../../../flora-runtime/lei-1/README.md) and [Wave 3](../../../flora-runtime/research-enrich-all-w3-689/dossiers/lloyds.md) distinguish Group, segment and legal-entity scope, reporting period, and underlying versus statutory basis. The candidate P&L, capital ratios, expense bridge and segment figures remain outside the preview.
- [Tier 1 research and holds](../../../research/lloyds-tier1-sprint1/acceptance.md) retain appointment and mandate candidates, relationships, Unknowns and Source holds. Repository presence does not establish a canonical acceptance or public release decision.
- [Existing Gold Standard inventory](../../../flora-runtime/lloyds-gold-standard/Inventory.json) records the finite overlay and other owners. This sprint measures coverage by the questions above. It does not count the same claim twice as new knowledge.
- Existing Source/legal and Financial owners retain the Lloyds §2 decision. §5 direct PDF links remain deferred. ADR-027 remains Proposed. No production data, canonical or Pipeline changes.

## Owner walkthrough and critique

Open `/enterprises/lloyds/preview/gold` on a local Flora instance. Read Group overview, follow funding and earnings, then open the earnings, efficiency and capital decisions. From Commercial Banking follow the credit journey. Finally compare Forces strategy with the goals and tests of progress. Open **Evidence & boundaries** for source identity and periods.

The goal view makes management direction easier to scan, but the available data cannot yet support a measured performance-to-target chart. The people view provides a way to ask who owns an outcome, while missing names and reporting lines limit it as an executive directory. The interactive operating links are valuable as paths through a business question. They remain conceptual until evidenced as dependencies.

## Reproduce

From the repository root with existing dependencies, use `python -m cios.applications.flora.web.app` with an isolated local data directory. Use `python docs/product/flora-experience/lloyds-ceo/browser.py after /tmp/lloyds-ceo-preview` for Chromium evidence. Run the same script with `before` from the detached baseline to reproduce the comparison. iPad captures are emulated Chromium viewports.

| Viewport | Before, strategy overview | After, goals opened |
| --- | --- | --- |
| Desktop | [1440 × 1000](previews/before-desktop.jpg) | [1440 × 1000](previews/after-desktop.jpg) |
| iPad landscape | [1366 × 1024](previews/before-ipad-landscape.jpg) | [1366 × 1024](previews/after-ipad-landscape.jpg) |
| iPad portrait | [1024 × 1366](previews/before-ipad-portrait.jpg) | [1024 × 1366](previews/after-ipad-portrait.jpg) |
