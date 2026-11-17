# Intelligence ownership and framework matrix

Baseline: `fbac4c37910ed07b2baa516e1a5c8d7f329086de`. **Core** means the current
UK/Banking/Lloyds seven-scene journey. **Retained** means code/finite historical
routes exist, not that they are current product navigation or fresh intelligence.
**Implemented** describes repository capability, not live data/configuration.

| Intelligence / purpose | Existing owner | Persistence and inputs → output | Actual trigger / core connection | State / deficiency |
| --- | --- | --- | --- | --- |
| Source identity/use and acquisition | `live/source_registry.py`; `memory/source_contracts.py`; `live/collect.py` | Source/profile config; receipts in `live_evidence/*.jsonl`, explicit `process_evidence` call into memory | Collection invokes factual contracts, memory processing and before/after Observatory diff | Actual mutating collection path exists; enablement/schedules/coverage not verified; not a general public ingestion API |
| Public working research | `research_intelligence/model.py`, `source_import.py` | Repository assessment overlays, snapshots, exact excerpts/bindings → candidate facts | Read-time validation after controlled source revision; selected outputs enter core | Implemented bounded working lane; not canonical Evidence/import |
| Canonical Evidence | `memory/repository.EvidenceRepository`; authorised Blueprint promotion | Operational `memory/evidence.jsonl` and governed import records | Explicit authorised review/acceptance/ingestion | Implemented stronger owner; live record contents not inspected |
| Observations | `memory/service.ObservationMemoryService`, `ObservationRepository` | `memory/observations.jsonl`; condition/period/source lineage | Accepted ingestion, explicit lifecycle/corroboration/conflict updates | Durable, but supports rewrites; not an immutable universal event bus |
| Enterprise Model | `memory/models.EnterpriseModel`, `EnterpriseModelRepository` | Derived `memory/enterprise_models/*.json` | `apply_observation` / `rebuild_from_ledger` through owning paths | Implemented memory projection; public reference IDs do not prove a loaded model |
| Governed entities/relationships | `blueprint_import/semantic_twin.py`, `twin_governance.py`, canonical repositories | Existing typed package/entity/relationship records and exact endpoints | Approved import, identity resolution, canonical mutation | Narrower graph functions; brand similarity is not a legal-entity edge |
| UK / Global / PESTLE | `macro_intelligence.context_spec`, `macro_trace.trace_projection` | `Macro-Context-v1.json`, retained traces → disposable context graph | Source/pack revision and read-time composition | Bounded UK view/global contracts; no worldwide research or automatic propagation |
| UK economic landscape | `visual_v2.py`, `visual_v2_assets/economy.json`, `visual_streams.py` | Comparable UK sector weights and source-specific metrics | Reviewed repository updates and caption validation | Core 20-sector context; financial services boundary broader than Banking |
| Industry Twins / Banking structure | `research_intelligence/model`, `twin_inspection/industry.py`, BIE-2 actors | Banking/Aviation overlays, inspected package projections | Pack revision / explicit inspection | Curated/partial; IT-001 ambition is not deployed cross-industry learning |
| Technology / Aviation journeys | `technology.load`, `technology_experience.render`, sector/unified views | 80-provider candidate directory, enterprise/table/operating-model presentations; Aviation/easyJet overlay | Source/pack revision; finite public research routes | Retained parallel journeys; Technology's browser-tab sales examples are not authorised Pipeline records or canonical Enterprise Models |
| PESTLE / Five Forces / value chain | `unified_views.industry_page`, `visual_templates`, BIE-2 analysis | Framework/actor/role analysis → alternate diagrams and dossiers | Overlay/research revision | Retained views; current Banking Forces is not Porter's five competitive forces |
| Enterprise operation / brands | `visual_streams`, `unified_views.enterprise_page`, assessment capabilities/programmes | Source associations → Inside/operating maps | Source revision; selected aspects enter core | Partial depth; no complete organisational/system architecture implied |
| Leadership / accountability | Enterprise dossiers; `leadership_agenda.py` | Declared roles, issue candidates, counter-evidence → agendas | Pinned inputs and eligibility policy on read | Synthesis, not proof of named buyer, funding or open decision |
| Suppliers / customers / regulators | Assessment relations; BIE-2 actor/relationship packs; governed resolvers | Reported/conceptual links retain types and legal scope | Revised support / approved relationships | Mixed lanes; contract, collaboration and regulation are different edges |
| Technology / transformation | Assessment programmes; Technology research owners | Disclosed platforms, programmes and reference models | Source/package revision | Curated; announcement is not actual deployment or realised benefit |
| Typed Financial analysis | `candidate_analytics.py`, `analyst.py`, `document_review.py` | Source-bound measurements/recipes; private runs; separate public projection | Explicit prepare/refresh; current inputs/rights checked on read | Real BoE/Nationwide pilot; uneven issuer coverage, no comparable industry earnings panel |
| Strategic issues / Leadership Agenda | `leadership_agenda.agenda`; SI-1 design #616 | Read-only synthesis of permitted working facts, dates and caveats | Current source/package/policy pins, not background research | Bounded read model; full design remains unmerged, no extra strategic engine |
| News candidates | BIE-2 `News-Candidates.json`; handoff #626/#614 | 17 dated candidates, all `production_news_eligible:false` | Authored tranches; frozen windows anchored 15 November | Candidate research, not production News or current-week supply |
| Legacy timelines / publications | `banking_portfolio.enterprise_event_timeline_page`; `intelligence/timeline.py`; `publisher/morning_edition.py` | Illustrative anchors / publication-date ordering / seeded brief plus optional collected evidence | Explicit invocation/generation | Historical prototypes; names/dates/scores do not establish verified event deltas |
| Observatory / signals / snapshot differences | `observatory/engine.build_observatory`, `observatory_snapshot`, `compare_observatory_snapshots` | Mixed seeded and collected evidence → heuristic signals, insights, theses, graph and recommendations; before/after deltas | Explicit build and collection before/after comparison | Existing cross-enterprise prototype/diff, not governed industry/UK synthesis; do not reuse heuristic scores as measured significance |
| External-change applicability | `ExternalChangeInterpretationService` | Governed external Evidence + relationships/Observations → disposable assessment | Explicit call; bounded Twin retrieval uses it | Implemented canonical branch; not connected to public scenes or a working-fact admission shortcut |
| Material Pressure | `memory.service.apply_observation/assess_material_pressure`; `blueprint_import.material_pressure.qualify_candidates` | State/history inside existing `EnterpriseModel.material_pressures/pressure_assessments` | Explicit qualifying descriptors and dependent fact changes trigger reassessment | Implemented qualification/maintenance, not a separate pressure store or every agenda issue; ordinary working facts do not auto-qualify |
| Imported-Twin dependencies | `TwinDependencyService.discover`, `DownstreamReconciliationRepository.create_pending` | Promoted subject references → pending-review records | Approved promotion execution | Implemented review discovery; class counts are not materiality or causal impact |
| Existing invalidation | Financial current projection; research `compare_revision`; seller `dependencies/_view` | Source rights/revisions, supersession, fact/Offer/employer/mission digests | Read or explicit reassessment | Useful primitives; no general cross-scope dispatch/upward synthesis |
| Private reasoning briefs | `EnterpriseIntelligenceRuntime.generate`, `retrieval`, `validator`, `persistence` | Bounded evidence package → validated brief/audit; approved interpretations | Explicit guarded generation, may use configured provider | Implemented optional reasoning, not invoked here or automatic news diff |
| Commercial hypothesis / matching | `buying_evidence.py`, `offers.assess_fit/discover`, `commercial_mission.py` | Source-backed facts + approved private Offer/employer/mission | Explicit discovery / read-time matching | Shared matcher, not buying intent; historical scenarios stay distinct |
| Development / Pipeline | `seller_development.py`, `sales_pipeline.py` | Private versioned candidates/customer attestations; opportunity store | Seller actions, reassessment, ten criteria, reviewed hand-off | No public event or pressure may auto-create/qualify a deal |
| Presentation / identity | `visual_streams`, `visual_panels`, `intelligence_presentation`, `public_routes`, CIOS security/Supabase adapter | Eligible projections + subject state → Top/Left/Main and six types | Request, finite route grammar, verified membership/ACL | Core selective; retained lens URLs can be shadowed by current dispatch |

The collector's `process_evidence` is an existing internal mutator, not a public
read model. Source/factual eligibility does not establish a new caller's IAM.
A future News adapter must not call it as an unchecked ingestion shortcut or add
blanket human approval for every ordinary fact. No collection was invoked here.

Operational paths are code contracts, **not a production storage inventory**.
Financial runs stay in their document-review owner; Offers use existing
`commercial_context/offers-v1/context.json`; Pipeline uses
`sales_pipeline/opportunities.json`. No private production records are read here.

## Framework placement — one explanation, not separate engines

| Framework | Best level / purpose | Existing embodiment | Rule |
| --- | --- | --- | --- |
| PESTLE | External context at UK; assessed sector/enterprise relevance | Macro contracts / assessment diagrams | Context is not inherited enterprise pain |
| Five Forces | Industry competition, entrants/substitutes, buyer/supplier power | Alternate Porter diagrams and dossiers | Do not call every external driver a Porter force |
| Value chain / industry economics | Activities, value creation and operating roles | Working analysis / conceptual chains | Conceptual flows are not contracts or measured profit pools |
| Enterprise economics | Exact group/legal perimeter and actual/target figures | Typed Financial owner | Preserve basis, period, currency, units; reject unlike comparisons |
| Operating/capability/technology models | How this enterprise works and changes | Overlay / Enterprise projections / reference archetypes | Label conceptual reconstruction; no invented systems/organisation |
| Relational SWOT / positioning | Evidence-backed internal/external synthesis | Working research / SI-1 candidates | Derive from existing facts, not a separate SWOT truth store |
| Leadership Agenda | Declarative executive significance across frameworks | Bounded agenda; wider SI-1 Option A pending | Retain counter-evidence, omit research-question panels in core |
| News / event / change | Dated input and comparison | Candidates / legacy tools, no current `news` stream | Fresh retrieval is not a new event |
| Pressure / commercial validation | Enterprise consequence then customer evidence | ADR-026 helpers / seller workflow | Canonical qualification and Pipeline remain explicit stronger gates |

## Authority and historical integration

Accepted ADRs 001–005, 009–016, 024 and 026 supply enduring boundaries; 006–008,
023, 025 and 027 remain Proposed. ADR-024's Draft header conflicts with its
Accepted body/index. The Authority Registry classifies EI-001/002/003/012 Accepted
documentation, while some file headers still say Draft. Preserve accepted ADR
constraints and flag the inconsistency for owner reconciliation, not silent
promotion/demotion. Documentation acceptance is not runtime completion.

IT-001 is explicitly **Review**, documentation-only, outside production profiles;
EI-015/017 are Review mechanism/pattern proposals. Historical Banking v1's “accepted
for pilot use” closure concerns that slice, not fresh verification or current
scene coverage. ADR-026 index's “not implemented” is stale relative to qualification
helpers; helpers do not prove every governance path or live population.

Unmerged SI-1 #616, RIE-1 #618, RIE-2 #620 and RIC-1 #622 retain valuable design/
research. Selective read-only synthesis reached main through INT/EAI/BIE/RUD;
that does not merge those packs or accept their remaining Evidence proposals.
ISP-1 #624, EAI-1 #630, EAR-1 #640 and Owner #603 remain draft. News #614,
influence-window #604 and Enterprise Builder #611 are separate commissions.
