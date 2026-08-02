# Commercial Context and Twin Map production-route proof

## Configured path

Render starts `python -m cios.applications.flora.web.app`. The module constructs
`FloraWebHandler`; there are no framework route decorators or alternate WSGI/ASGI
applications in this repository.

| Request | Configured entry point | Handler | Renderer/service | Access resolver | Final owner |
|---|---|---|---|---|---|
| `GET /blueprint-import/{run}` | `cios.applications.flora.web.app` | `FloraWebHandler.do_GET` catch-all blueprint route | `executive_workspace_page` → `_hero` → `_primary_nav` → `_mission_indicator` → `_domain_lenses` → `_twin_map` → `_navigation` | candidate-read boundary | imported candidate remains `flora-pilot-import` |
| Configure link / `GET /blueprint-import/{run}/mission` | same | explicit mission branch in `do_GET` | `executive_workspace_page(view="mission")` → `_mission_editor` | `commercial_context_owner` → `commercial_context_authorisation(...view...)` | `flora-pilot-operator` (`commercial-context`) |
| `POST /blueprint-import/{run}/mission` | same | explicit mission branch in `do_POST` | `update_commercial_mission` → existing mission/employer stores | `commercial_context_owner` → `commercial_context_authorisation(...edit...)` | `flora-pilot-operator` (`commercial-context`) |
| `GET /blueprint-import/{run}/explore` | same | explicit explore branch | `executive_workspace_page(view="explore")` → `_explorer` | candidate-read boundary | imported candidate remains `flora-pilot-import` |
| `GET /blueprint-import/{run}/research-brief` | same | explicit research-brief branch | `export_research_gap_brief` → `research_gap_brief` | candidate-read boundary; profiles use canonical context actor | separate mission/employer records for `flora-pilot-operator` |

Searches found one `FloraWebHandler`, one definition of `executive_workspace_page`,
one GET mission registration and one POST mission registration. The previous implementation
changed `commercial_context_authorisation`, but the production GET and POST passed the imported
package's `workspace_id`; therefore they still requested `flora-pilot-import`. Both routes now
ask the same server resolver for the commercial-context owner and never read an owner/scope from
the form.

## Render-chain proof

The production Twin Map chain previously appended `_composition(...)` immediately after
`_twin_map(...)`. `_composition` emitted `Twin Composition` and iterated
`business_collections`, the source of Enterprises, Market Participants, Opportunities,
Insights, Financial Intelligence, Transformation Programmes, Capabilities and Offers,
Relationships, Evidence Sources, Unknowns, and Contradictions. The route no longer invokes
that legacy renderer. It retains `_composition` and the underlying collections for non-home
technical capabilities; Advanced Inspection remains the route to those collections.

The final main-route chain is now exactly:

```
_hero
_primary_nav
_mission_indicator
_domain_lenses
_twin_map                 # exactly six business tiles
_navigation               # Research Gaps and Advanced Inspection
_page + compact Flora product header
```

## Configured-entry-point rendered evidence

`test_configured_module_complete_http_commercial_context_and_twin_map` launches the exact
Render module in a subprocess, uploads a real persisted candidate through HTTP, follows the
Configure href, saves both stores, follows the redirect, exports the brief, and opens Advanced
Inspection. Observed rendered markers are:

1. Settings: `<h1>Configure Commercial Mission</h1>` and no `Access denied`.
2. Saved state: `Commercial Mission: UK growth`.
3. Recomposition: `Commercial Mission not configured` absent.
4. Twin Map ending: six `<h3>` tile headings followed only by Twin navigation.
5. Export: `- Mission: UK growth` and `- Organisation: Example Supplier` in distinct sections.
6. Inspection: `<h1>Advanced Inspection</h1>`, `Technical collections`, and `Back to Twin Map`.

The complete-response assertions require each of `Industry Overview`, `Enterprises`, `Market
Participants`, `Major Programmes`, `Opportunities`, and `Reinvention Timing` exactly once as a
tile heading. They reject `Twin Composition`, `Financial Intelligence`, `Transformation
Programmes`, `Capabilities and Offers`, `Relationships`, `Evidence Sources`, `Unknowns`,
`Contradictions`, `Material Insights`, `Priority Enterprises`, `Commercial Opportunities`, and
`Pressure and Urgency` anywhere in the final Twin Map response.

## Deployment fingerprint

The Twin Map and Configure response receive the existing safe deployment comment. `/deployment`
reports the configured module, commit SHA, import implementation, route owners, and
`executive-twin-map-v4`. A local pass proves the repository revision only; production is verified
only when the deployed `commit_sha` matches the expected repository commit.
