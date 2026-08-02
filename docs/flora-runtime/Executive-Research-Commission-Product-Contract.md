# Executive Research Commission Product Contract

## Acceptance basis

This matrix records product acceptance against complete responses generated on 2 August 2026 by the configured `python -m cios.applications.flora.web.app` runtime path. The repository TMS-001 package was submitted through the configured import handler, the unique acceptance context was submitted through the Commercial Mission save handler, and all outputs were then requested afresh from the active route owners. Evidence is retained in `executive-research-commission-final-acceptance/`.

## Product Contract Matrix

Every “Observed after” value below was asserted against the complete configured HTTP response or downloaded file retained in `executive-research-commission-final-acceptance/`; none is a code-inspection result.

| Contract row | Expected | Observed before | Root cause | Correction | Observed after | Evidence | PASS/FAIL |
|---|---|---|---|---|---|---|---|
| Industries export | Media; Telecommunications | Not supplied | Active export read legacy aliases instead of resolved tuple | Render resolved `CommercialMission.industries` | Media; Telecommunications | 03 form + 04 full export | PASS |
| Priority-customer export | BT Group; BBC; ITV | Not supplied | Priority field was lost before active resolver | Persist/reload `priority_accounts`; exact export binding | BT Group; BBC; ITV | 03 + 04 | PASS |
| Capabilities/services export | Five submitted values | Not supplied | Employer form name did not reach canonical capabilities | Map `employer_capabilities` through employer store/resolver | Digital transformation; Cloud; Data; AI; Managed services | 03 + 04 | PASS |
| Competitor export | Accenture; Cap Gemini; IBM | Populated inconsistently | Parallel context paths | One resolved Employer Context binding | Accenture; Cap Gemini; IBM | 03 + 04 | PASS |
| Enterprise count | 14 profiles | 93 profiles | Export counted all canonical IDs attached to 14 dossiers (underlying records), not dossier subjects | Typed collection count uses canonical enterprise identities | 14 everywhere; 93 is never labelled profiles | 01, 02, 04, 07 | PASS |
| Reinvention count semantics | Separate records, domains, enterprises/units, assessed, unassessed, projections | 1 and 8 reused under ambiguous labels | Change objects, assessment records and projections were conflated | Emit every typed unit independently | 1 record; 3 domains; 0 explicitly linked enterprises/units; 0 owner-assessed; 0 unassessed; 1 projection | 02 + 04 | PASS |
| Participant classification | Seven allowed classifications; non-organisations get adapted research | All concepts treated as organisations | Generic participant template ignored supplied type | Resolve supplied type fail-closed; category/capability/relationship contracts | Hyperscalers category; EE/BT unresolved identity, neither organisation | 08 + 04 Appendix C | PASS |
| Subject-type enterprise requirements | Requirements adapt to supported type | One generic list for 14 | Generic collection schedule used for every dossier | Bind supplied form/role evidence to existing owner schedules | BBC, CityFibre, IFR, Premier League and Sport England differ | 04 + 07 | PASS |
| Researcher-facing language | Business questions/actions in primary content | Architecture-heavy assessment prose | Traceability prose occupied primary contract | Business translation primary; architecture in details/Appendix A | Primary sections state research, sources, value and acceptance | 02 + 04 | PASS |
| Readiness-authority cleanup | One owner-backed status | Owner absence plus local “Insufficient” | Legacy heuristic rendered beside projection | Remove heuristic from primary; retain diagnostics as non-authoritative | “Not yet assessed against the governed standard” only | 02, 06–08; 05 diagnostics | PASS |
| Markdown H1 | Exact single H1 | H1 missing | Old builder/renderer output | Fixed first line plus fail-closed validation | Exact H1, count 1 | 04 + 09 | PASS |
| Markdown section 14 | Complete heading | Truncated “eliverables” | Malformed generated heading | Fixed required heading validation | `14. Required Structured Deliverables` complete | 04 + 09 | PASS |
| Complete Markdown validity | 16 sections, A–D, valid EOF | Orphan/truncated structure | No complete-document structural gate | Validate complete file before response | 1,034-line file accepted | 04 + 09 | PASS |
| Complete research scope | No mission filtering | Scope not proven | Emphasis and commission ordering were coupled | Separate full commission from matched emphasis | 1/14/10/9/9 plus timing and gaps retained | 01, 02, 04 | PASS |
| Mission emphasis | Only explicit, inspectable matches | Arbitrary broad matching | Text matching leaked member facts to collection reasons | Exact identity/domain/relationship/timing gates | BT Group, BBC, ITV alone receive named-priority reason | 04 §5 + Appendix D | PASS |
| Import regression | Configured upload works | Previously working | Risk from correction | Exercise native multipart handler | HTTP 303 and complete imported workspace | 01 + runtime run ID | PASS |
| Mission persistence regression | Save/reload/restart retains fields | Three field groups lost | Split alias and persistence paths | Atomic canonical stores and resolved reload | Restarted runtime returned all values | 03 + 04 | PASS |
| Promotion fail-closed regression | No automatic promotion | Previously fail-closed | Regression risk | No governance-owner changes | Candidate inspection remains separate; governance tests pass | 05 + automated suite | PASS |

## Configured runtime and route ownership

| Request | Handler | Service | Renderer | Persistence/data source | Final owner |
|---|---|---|---|---|---|
| Render start | `python -m cios.applications.flora.web.app` | Flora HTTP server | — | `FLORA_DATA_DIR=/var/data/flora` | `render.yaml` |
| `GET /blueprint-import/{run}` | `executive_workspace_page` | semantic assembly and projections | `_twin_map` | package registry/staging repository | configured Flora module |
| `GET .../health` | `executive_workspace_page(view=health)` | `twin_readiness`, `research_requirements` | `_research_gaps` | same + resolved context | owner projections |
| `GET .../diagnostics` | `executive_workspace_page(view=diagnostics)` | semantic assembly | `_advanced_diagnostics` | staging summary | configured handler |
| `GET .../mission` | `executive_workspace_page(view=mission)` | `resolve_commercial_context` | `_mission_editor` | separate mission/employer JSON stores | context authorities |
| `POST .../mission` | `update_commercial_mission` | `save_commercial_context` | redirect/re-render | separate atomic JSON stores | context authorities |
| `GET .../research-brief` | `export_research_gap_brief` | semantic assembly, assessments, requirements | `research_gap_brief` + structural validator | registry/staging + active context | configured export owner |

Repository searches found no second configured export renderer or resolver. Older artifacts and test helpers exist but are not HTTP route owners. Counts originate from semantic Twin/business collections and owner projections, not a legacy 93-record helper.

## Commercial Context field lifecycle

All controls are parsed by `update_commercial_mission`, normalised by the canonical dataclasses, atomically persisted, reloaded by `resolve_commercial_context`, and projected to applicable pages/export. Blank is reported as “Not supplied” only after resolution.

| UI / contract field | Submitted name | Canonical/persisted property | Projection | Accepted state |
|---|---|---|---|---|
| Mission name | `mission_name` | `CommercialMission.mission_name` | form/export; generated display only | correctly mapped; optional |
| Role | `executive_role` | same | all context views | correctly mapped |
| Geography | `geography` | same tuple | form/export/lens | correctly mapped |
| Industries | `industries` | same tuple | form/export/emphasis | correctly mapped |
| Primary objective | `commercial_objective` | same | form/export/emphasis | correctly mapped |
| Additional objectives | `objectives` | same tuple | form/export | correctly mapped |
| Commercial horizon | `commercial_horizon` | same | form/export/timing match | correctly mapped |
| Focus areas | `interests` | same tuple | form/export; no unsupported match | correctly mapped |
| Priority customers | `priority_accounts` | same tuple | form/export/exact emphasis | correctly mapped |
| Target accounts | `target_customers` | same tuple | form/export/exact emphasis | correctly mapped |
| Relevant business units | `relevant_business_units` | same tuple | form/export | correctly mapped |
| Employer | `employer_organisation` | `EmployerContext.organisation` | form/export | correctly mapped |
| Relevant capabilities or services | `employer_capabilities` | `EmployerContext.capabilities` | form/export/explicit relation only | user-facing field maps to canonical capabilities |
| Services/offers | `employer_offer_portfolio` | `EmployerContext.offer_portfolio` | form/export | distinct, correctly mapped |
| Competitors / partners | `employer_competitors` / `employer_partners` | corresponding tuples | form/export/exact identity | correctly mapped |
| Propositions / target sectors | advanced `employer_*` controls | corresponding employer tuples | reopened form; context model | correctly mapped |
| Description, credentials, constraints, excluded offerings | advanced `employer_*` controls | corresponding employer properties | reopened form/context | correctly mapped |

## Typed canonical count contract

| Collection | Canonical subject count | Underlying record count | Owner assessment count | Affected subject count | Presentation/recommendation eligibility |
|---|---:|---|---:|---|---|
| Industry | 1 | Preserved in Appendix B | 1 projection | 1 Twin | unchanged by mission |
| Industry Overview | 1 | Preserved | 1 | 11 required dimensions incomplete | owner-controlled |
| Enterprises | 14 | Separately inspectable | 1 collection projection | 14 | owner-controlled |
| Market Participants | 10 concepts | Separately inspectable | 1 collection projection | 10 | classification-gated |
| Major Programmes | 9 hypotheses | 9 canonical programme objects | 1 collection projection | 9 | owner-controlled |
| Opportunities | 9 hypotheses | 9 canonical opportunity objects | 1 collection projection | 9 | owner-controlled |
| Reinvention Timing | Explicit applicable subjects | Existing assessment records separately labelled | projection count separately labelled | separately labelled | owner-controlled |
| Evidence deficiencies | Not a subject count | claims/evidence records | n/a | deficiency count explicitly labelled | never called enterprise profiles |

## Classification and subject-language contract

| Explicit canonical classification | Commissioned research |
|---|---|
| organisation | legitimate organisation profile |
| organisation group | group definition and member identities |
| participant category | category definition, criteria and members |
| capability | providers, users, application, relations and evidence |
| relationship | source, target, type, significance, timing and evidence |
| regulator | mandate, jurisdiction, regulated entities and evidence |
| unresolved identity | identity/type resolution first; source ID retained |

| Enterprise subject type | Adapted requirement language |
|---|---|
| commercial company | ownership, purpose, segments, finance, operating model, ecosystem, programmes, procurement, risks, AI adoption |
| regulator | mandate, jurisdiction, powers, priorities, enforcement, regulated entities, funding and technology |
| public body | mandate, funding, beneficiaries, programmes, public outcomes and transformation |
| league / governing body | governance, members, rights/revenue, competitions, partners, data/technology and procurement |
| broadcaster | ownership/remit, audience, funding/revenue, content/distribution economics, regulation and technology |
| unresolved | classification research before inappropriate company assumptions |

## Evidence register

- Twin Map: `executive-research-commission-final-acceptance/01-twin-map.html`
- Research Gaps: `executive-research-commission-final-acceptance/02-research-gaps.html`
- Advanced Inspection: `executive-research-commission-final-acceptance/05-advanced-inspection.html`
- reopened Commercial Mission: `executive-research-commission-final-acceptance/03-commercial-mission.html`
- complete canonical deliverable: `executive-research-commission-final-acceptance/04-research-commission.md`
- validator results: `executive-research-commission-final-acceptance/09-validation.txt`

The export proves complete scope and deterministic mission emphasis. BT Group, BBC and ITV receive exact named-priority-customer reasons; no other enterprise receives that reason. Capability and timing reasons require explicit Twin relations. The canonical register preserves all subjects regardless of emphasis.

## Remaining known limitations

Canonical records that do not supply an owner type remain explicitly unresolved rather than being guessed. This is a classification research requirement, not a manual-edit defect. Paid or unavailable evidence remains represented as an Unknown under the existing evidence contract. Neither limitation makes the commission malformed or narrows its scope.

## Recommendation

Every contract row is proven against a complete configured-path response and is **PASS**. The generated Markdown can be issued without manual editing. **MERGE**.
