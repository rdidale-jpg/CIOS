# Visual Intelligence v3 — architecture and reuse, before implementation

Controlling specification: [Issue #552](https://github.com/rdidale-jpg/CIOS/issues/552). PR #551 is **open, not merged**. Verified base `e03b2fff29a0236d69fad4e522654d3a2a557990`; its [hosted gate](https://github.com/rdidale-jpg/CIOS/actions/runs/42819764848) passed. Main remains `650b92c377b7295a01cb59deec7195fae21e8a93`. V3 branches from #551 and initially targets `codex/flora-living-industry-maps-v2`. After a separately authorised #551 merge, retarget v3 to main, verify the effective diff and rerun candidate CI. No merge/retarget is performed here.

## Inventory and reuse

| Existing owner | Reuse |
| --- | --- |
| `living_map_specs` / `living_map` | Keep v2 scene, activities, canonical capability references, source projections, AI/regulatory lenses and print handling. Add an opt-in Commercial Opportunities lens and better return-selection/touch navigation |
| `model.candidate`, `commercial_candidates` | Reuse all nine Lloyds and six easyJet hypothesis identities and existing analyst assessments. Counts are inventory/context counts, never a new market-attractiveness score |
| `visual_intelligence_specs` / `understanding.assess` | Reuse exact quoted passages, source classes, dates, retained scope conflicts and dated relationship states. New projection is read-only presentation, not a graph, research store or canonical promotion |
| Existing public candidate routes / enterprise `lens` | Enhance candidate inspection and add an enterprise commercial lens. Use finite activity fragments for reversible navigation; no new browser workspace selector or public resource lookup |
| `sales_views.capture_controls` / existing POST capture | Deliberate, CSRF-protected creation **or idempotent linking** through the existing producer. Public views never enumerate private records |
| `sales_pipeline` | Preserve capability/resource evaluator, verified writer, workspace scope, immutable provenance, version checks, duplicate handling, audit and stage machine. No permission engine, migration or new opportunity store |
| `commercial_mission` / employer context | Private operational seller profiles stay private; the public lens uses the existing repository seller assessment, without reading workspace profiles |
| Existing qualification UI | All ten note/reference pairs, evidence review and explicit stage confirmation remain required for Qualified/advanced stages. Completeness is not probability or external verification |
| Original six diagrams / primary navigation | Retain contracts, routes, canonical identities and Home/Industries/Enterprises/Opportunities/Pipeline |

## Bounded implementation

A commercial presentation projection associates existing hypotheses to an industry activity through validated research capability/programme references. This is explicitly a **research coverage association**, not confirmed enterprise ownership, an implementation dependency or a customer requirement. Count source-supported context separately from total hypotheses; zero signals and missing evidence stay valid.

The enterprise lens and hypothesis inspection reuse current problem, offer, proposed services, strategic/access/evidence/seller-fit dimensions, inferred buying roles, competitive context, gaps and next actions. Relevant v3 contradictions retain their own claim IDs and periods; a contradiction is not proof of an unmet commercial need. No new buyer, budget, contract, procurement date or win probability is generated.

Capture preserves existing provenance fields and adds an immutable review snapshot for **new captures only**, including counterevidence IDs/digests. Existing linked records are returned unchanged. Current presentation can differ from a historical capture; do not rewrite it. No read of private Pipeline data is needed on a public research page.

## Material trade-offs

The existing Pipeline **first captures Discovered, then qualifies privately**. Do not invent a pre-Pipeline draft model to reverse that order. The user deliberately creates/links the private research-stage record; the existing qualification action later changes stage only when all controls pass. The inherited `demonstration` flag and demonstration wording remain truthful; this increment does not certify a production revenue forecast or validate customer evidence independently.

The established workflow does not trigger for a PR targeting the v2 branch. Add **only that exact base** to `pull_request.branches`; retain path filters, commands, permissions and strict failure comparison. This is needed for hosted validation of the authorised stacked candidate.

## Validation plan

Test complete HTTP capture/qualification/link flow, source/counterevidence, empty/unsupported context, unknown buyer/budget, historical supplier scope, immutable provenance and no record creation on GET. Reuse real isolated test sessions for capability, workspace, membership and CSRF denials and unchanged business-store hashes. Preserve every inherited baseline identity/signature/skip. Run focused tests, CI policy/actionlint, full strict gate and actual-candidate hosted CI. Capture Chromium desktop/tablet/mobile, keyboard/touch, all lenses and print; human comprehension remains unmeasured. All accounts/qualification evidence used for validation are explicitly synthetic and isolated; no production seeding or deployment.
