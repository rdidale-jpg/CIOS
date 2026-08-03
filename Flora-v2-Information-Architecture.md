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

## Home runtime correction — route and owner proof

The configured application entry point is `cios.applications.flora.web.app:app` (the
`FloraWebHandler`). The correction reuses the active runtime paths and does not add a
Home data authority.

| Experience | Route | Handler | Service | Resolver | Renderer | Canonical data owner |
|---|---|---|---|---|---|---|
| Home | `/`, `/flora`, `/flora/` | `FloraWebHandler.do_GET` | existing Home composition | `resolve_commercial_context` plus the existing banking opportunity pipeline | `_flora_home_page` / `_flora_v2_page` | Commercial Mission and Employer Context stores; existing Enterprise Intelligence pipeline |
| Twin Map | `/blueprint-import/{run_id}/workspace` | `FloraWebHandler.do_GET` | `executive_workspace_page` | `resolve_commercial_context` | Executive workspace map | promoted/staged Twin records and their existing repositories |
| Research gaps | `/blueprint-import/{run_id}/health` | `FloraWebHandler.do_GET` | `executive_workspace_page` | `resolve_commercial_context` | `_research_gaps` | governed deficiencies on the assembled semantic Twin |
| Research Commission export | `/blueprint-import/{run_id}/research-gap-brief` | `FloraWebHandler.do_GET` | `export_research_gap_brief` | `resolve_commercial_context` | `research_gap_brief` | governed deficiencies plus the same declared context |
| Opportunity workspace/detail | `/opportunities`, `/opportunities?opportunity={id}` | `FloraWebHandler.do_GET` | existing banking opportunity pipeline | existing deterministic Horizon projection | `_flora_opportunities_page` | Enterprise Intelligence opportunity pipeline |
| Industry portfolio | Home and `/flora/banking` | `FloraWebHandler.do_GET` | existing banking portfolio | existing governed banking state | `_flora_home_page` / `banking_landing_page` | governed UK Banking Twin |

The primary navigation is rendered only by `_flora_v2_page` for this experience. Its
five items remain Home, Intelligence, Opportunities, Research and Governance. Legacy
routes and Twin import routing remain registered unchanged in `FloraWebHandler`.

## Final Home composition and semantics

Home retains, in order: the Commercial Context banner, Enterprise Intelligence Map,
mission-aware or neutral opportunities, Intelligence Requiring Attention, and the
compact Industry Portfolio.

* **Commercial Context:** Home consumes the same `resolve_commercial_context` read
  contract as Twin Map, Research Gaps and the export. A complete persisted mission is
  labelled configured; genuinely incomplete operational fields produce a partial
  state; absence produces a constructive configuration prompt. Context changes only
  ordering, emphasis and relevance explanation—not Twin truth, completeness,
  evidence, confidence or research scope.
* **Opportunity state:** `Priorities for my mission` is used only when an explicit
  declared subject match changes ordering. Otherwise `Commercial opportunities` is
  used. Named customers sort ahead of unresolved hypotheses; unresolved items say
  `Strategic opportunity hypothesis` and `Customer unresolved`.
* **Tile counts:** each tile pairs a business population with a separate governed or
  assessment state. `0` means an aggregation ran and found no records. `Not currently
  summarised` means no supported aggregation exists. `Not yet assessed` means the
  represented population exists but its assessment has not been made. No neighbouring
  record count substitutes for an unavailable measure.
* **Industry states:** governed industries link to their Twin; candidates link to
  review; research-in-progress entries link to their research mission; not-started
  entries link to construction. An external mission such as TEL-001 is not a live
  Industry Twin until imported, so it is not presented as one.

## Attention ownership

| Attention category | Existing owner and rule | Destination |
|---|---|---|
| New evidence | Evidence Records added since a supported checkpoint | Research, filtered to new evidence |
| Changed opportunities | real comparison/change event for status, Horizon, value, timing or confidence | Opportunities, filtered to changed |
| New programmes | newly represented Programme Objects | Intelligence / Programmes, filtered to new |
| Research gaps | unresolved governed deficiencies | Research, filtered to gaps |
| Evidence becoming stale | Evidence Record freshness/temporal status | Research, filtered to stale evidence |
| Resolved contradictions | Contradiction Records whose resolution status changed | Governance, filtered to resolved contradictions |
| Upcoming monitoring triggers | Monitoring Trigger Records with due/upcoming review dates | Research, filtered to monitoring triggers |

Where the current runtime has no supported checkpoint, comparison, freshness summary
or Monitoring Trigger aggregation, Home says `Not currently available`. In particular,
Contradiction Records are never counted as monitoring triggers.

## Empty states, terminology and route preservation

Home distinguishes `0 represented`, `Not currently summarised`, `Not yet assessed`
and `Not currently available`. Empty populations use constructive guidance to import
or enrich a Twin. Primary-page terms use *available intelligence*, *represented
opportunities*, *supporting evidence* and *governed intelligence*. The ambiguous terms
*active candidates* and *active opportunity* are not used without procurement or
sales-pursuit evidence.

All map destinations reuse existing routes: Industries, Enterprises, Programmes and
Market Participants use filtered `/intelligence` views; Opportunities uses
`/opportunities`; Research & Readiness uses `/research`. Opportunity cards retain the
existing opportunity query destination, and UK Banking retains `/flora/banking`.
Legacy `/explore`, `/focus`, `/shape`, digital-Twin, import, Governance and Advanced
Inspection routes remain callable; this correction introduces no duplicate route.
