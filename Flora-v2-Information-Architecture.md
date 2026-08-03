# Flora v2 Information Architecture

## Architecture Impact Summary

### Architectural intent

Flora is an Enterprise Intelligence product. Its intended interaction path is **Flora Map → Industry Twin Map → Enterprise Dossier → Programme → Opportunity → Evidence**. The Flora Map is an estate-level summary and does not replace or duplicate an Industry Twin Map.

### Implemented runtime

The standard-library HTTP application in `cios/applications/flora/web/app.py` owns request routing and composes HTML returned by capability-specific view functions. Existing runtime owners remain unchanged:

- Banking Industry Twin and portfolio views are implemented in `banking_portfolio.py`.
- Twin Explorer and enterprise views are implemented by `digital_twins.py`, `twin_inspection.py`, and the enterprise canvas views.
- Executive Workspace, Commercial Mission, research-gap and import inspection views are implemented by `blueprint_import/executive_workspace.py`.
- Blueprint Import remains implemented by the `blueprint_import` package.
- Commercial opportunity candidates and Horizon rationale are supplied by `enterprise_intelligence/opportunity_pipeline.py`.
- Research collection, evidence, settings, observatory and financial-intelligence routes retain their existing owners.

No object contract, import lifecycle, Twin runtime, researcher runtime, evidence ownership rule, or implementation profile is changed by Flora v2.

### Legacy navigation

Earlier shells exposed the history of capability delivery: Executive Brief, Observatory, Portfolio, Evidence, Digital Twins, Financial Intelligence, Research, and Settings. Later prototype composition used Explore, Focus, and Shape. These labels no longer form the primary navigation. Their routes remain available as deep links and as contextual destinations from the new workspaces.

### Current composition change

This sprint changes presentation composition only. `/`, `/flora`, and `/flora/` now render the Enterprise Intelligence Workspace and its Flora Map. Five stable top-level destinations organise the existing capabilities around executive work. Settings is exposed as a profile/control action rather than a primary workspace.

## Navigation hierarchy

1. **Home** — the Flora Map and default Enterprise Intelligence Workspace.
2. **Intelligence** — common exploration across industries, enterprises, programmes, participants, and relationships.
3. **Opportunities** — the commercial pipeline organised by Horizon and commercial lenses.
4. **Research** — imports, missions, gaps, closure, and briefs.
5. **Governance** — evidence, Unknowns, Contradictions, promotion, validation, release identity, and advanced inspection.
6. **Controls** — profile and Settings action in the application header.

## Workspace purpose and composition

### Home / Flora Map

Home answers what intelligence exists, why it matters, and where to inspect next. Its sections are:

1. Commercial Context — configured mission, industry focus, time horizon, last update, and mission configuration action. Values unavailable from the estate runtime are explicitly shown as “Not yet assessed”.
2. Enterprise Intelligence Map — six linked domains: Industries, Enterprises, Opportunities, Major Programmes, Market Participants, and Research & Readiness. Metrics are derived from the current opportunity runtime or explicitly unavailable.
3. Mission Priorities — current opportunities with customer, problem, timing, value, Horizon, rationale, and evidence confidence. Without a mission, all intelligence remains visible in runtime order.
4. Intelligence Requiring Attention — the estate inbox categories. Only runtime-supported counts are displayed.
5. Industry Portfolio — compact cards for industries with a real state; currently the governed UK Banking state.

### Intelligence

Tabs provide Industries, Enterprises, Programmes, Market Participants, and Relationships. Each tab links into an existing detailed workspace. Twin Explorer remains the advanced inspection route and Industry Twin Maps continue to own industry-level exploration.

### Opportunities

Tabs provide Horizon 1, Horizon 2, Horizon 3, Procurement Activity, Opportunity Hypotheses, and Estimated Pipeline. Horizon cards are composed from existing runtime candidates and link to the existing full opportunity detail. Unsupported timing or value is not inferred.

### Research

Research consolidates links to Imports, Research Missions, Research Gaps, Evidence Closure, and Research Briefs. Import behavior is unchanged.

### Governance

Governance consolidates Evidence, Unknowns, Contradictions, Promotion and Validation, Release Manifest, and Advanced Inspection. It delegates each action to the existing runtime owner.

## Routing map

| Primary route | Composition | Existing capability destinations |
| --- | --- | --- |
| `/`, `/flora`, `/flora/` | Home / Flora Map | `/flora/banking`, `/blueprint-import`, `/opportunities` |
| `/intelligence` | Intelligence tabs | `/flora/banking`, `/digital-twins`, `/flora/banking/competitors` |
| `/opportunities` | Commercial pipeline tabs | `/focus`, `/shape` |
| `/research` | Research launchpad | `/blueprint-import`, `/blueprint-import/history`, `/explore`, `/live/evidence`, `/shape` |
| `/governance` | Governance launchpad | `/live/evidence`, `/explore`, `/blueprint-import/history`, `/deployment`, `/digital-twins` |
| `/settings` | Profile/control action | Existing Settings runtime |

All other route branches in `FloraWebHandler` remain intact, including Blueprint Import, Executive Workspace, Mission Configuration, Twin inspection, Twin Explorer, opportunity detail, research, evidence, and financial intelligence routes.

## Legacy mapping

| Legacy destination or language | Flora v2 location | Deep link status |
| --- | --- | --- |
| Executive Brief / Shape | Opportunities and Research Briefs | Preserved (`/shape`) |
| Observatory | Intelligence or contextual deep link | Preserved (`/observatory`) |
| Portfolio | Home Industry Portfolio / Intelligence | Preserved (`/portfolio`, `/flora/banking/portfolio`) |
| Evidence | Governance / Research Evidence Closure | Preserved (`/evidence`, `/live/evidence`) |
| Digital Twins | Intelligence Twin Explorer | Preserved (`/digital-twins`) |
| Financial Intelligence | Contextual runtime route | Preserved (`/financial-intelligence`) |
| Research | Research workspace | Preserved legacy research routes plus `/research` |
| Settings | Header Controls | Preserved (`/settings`) |
| Explore / Focus / Shape | Intelligence / Opportunities / Research Briefs | Preserved (`/explore`, `/focus`, `/shape`) |

## Future extensibility

Future industries and estate metrics can be added to the Flora Map when existing runtimes expose governed state. New summary tiles must link to an owning workspace rather than reproduce its runtime. Additional tabs may compose existing capability routes, but must not create new architectural owners, Twin concepts, evidence contracts, or parallel import/research paths. Mission configuration may affect ordering only; it must never hide otherwise available intelligence.
