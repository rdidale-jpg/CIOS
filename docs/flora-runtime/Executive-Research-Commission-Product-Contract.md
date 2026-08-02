# Executive Research Commission Product Contract

## Acceptance basis

This matrix records product acceptance against complete responses generated on 2 August 2026 by the configured `python -m cios.applications.flora.web.app` runtime path. The repository TMS-001 package was submitted through the configured import handler, the unique acceptance context was submitted through the Commercial Mission save handler, and all outputs were then requested afresh from the active route owners. Evidence is retained in `executive-research-commission-product-acceptance/`.

## Product Contract Matrix

| ID | Product contract | Current observed output | Required output | Active runtime owner | Verification method | Pre-change status | Post-change status |
|---|---|---|---|---|---|---|---|
| A | Commercial Mission industries export | `Industries: Media; Telecommunications` | Every saved industry | context resolver → commission renderer | Save, fresh export, full-text assertion | FAIL: previously `Not supplied` | PASS |
| B | Priority customers export | `BT Group; BBC; ITV` | Every saved priority customer | same | Save/reload/export assertion | FAIL: previously lost | PASS |
| C | Employer capabilities/services export | Five submitted capabilities shown | Preserve “Relevant capabilities or services” as `EmployerContext.capabilities` | employer store → resolver → renderer | form, store, reopened form, export | FAIL: previously `Not supplied` | PASS |
| D | Competitors export | Accenture, Cap Gemini and IBM shown | Every configured competitor | employer store → renderer | fresh export assertion | FAIL: previously lost | PASS |
| E | Mission operational status | `Configured`; optional name remains absent; generated label shown | Optional name must not lower status | `CommercialMission.operational_status/display_name` | reopened form and export | FAIL: ambiguous optional-name status | PASS |
| F | Mission Emphasis reasons | Exact named-account/domain reasons only; limitations stated | Deterministic inspectable explicit matches | `_mission_reasons` | full emphasis section inspection/tests | FAIL: mapping could prioritise all/none | PASS |
| G | Complete research scope preserved | 1 / 14 / 10 / 9 / 9 plus timing, evidence, Unknowns and Contradictions | Mission removes no canonical subject | `research_gap_brief` | summary/register and route tests | FAIL: not proven | PASS |
| H | Enterprise canonical count | `14 enterprise profiles require enrichment` | 14 canonical enterprises | semantic Twin enterprises | Twin Map, gaps, export | FAIL: export said 93 | PASS |
| I | Market Participant canonical count | 10 participant concepts | 10 canonical concepts, classification-qualified | business collections | gaps/export/register | FAIL: unit ambiguous | PASS |
| J | Major Programme canonical count | 9 programme hypotheses | 9 | canonical object kind | routes/export | FAIL: not acceptance-proven | PASS |
| K | Opportunity canonical count | 9 opportunity hypotheses | 9 | business collections | routes/export | FAIL: not acceptance-proven | PASS |
| L | Reinvention assessment-record count | Existing records labelled separately | Explicit assessment-record unit | semantic objects | export summary | FAIL: “1” ambiguous | PASS |
| M | Reinvention affected-subject count | Applicable affected subjects labelled separately from owner projections | Explicit affected/assessed/unassessed units | owner projection + semantic Twin | gaps/export | FAIL: 1/8 ambiguous | PASS |
| N | Market Participant classification | Every concept reports supplied canonical type or `unresolved identity`; source remains inspectable | No category/capability/relationship commissioned as organisation | `participant_classification` | appendix and classification tests | FAIL: organisation assumption | PASS |
| O | Collection-level wording | Collection prose contains no arbitrary member name | Collection-wide rationale | `_COLLECTION_LANGUAGE` | complete Research Gaps response/test | FAIL: arbitrary member prose observed | PASS |
| P | Subject-type-aware Enterprise requirements | Regulator/public body/governing body/broadcaster/company schedules differ; unresolved requests classification | Subject-appropriate language, N/A compatible | `enterprise_subject_type` + translator | translator tests/export | FAIL: uniform checklist | PASS |
| Q | Primary researcher acceptance tests | Practical sourced coverage/Unknown outcomes | Research outcomes, not implementation owners | `_BUSINESS_ACCEPTANCE` | primary narrative inspection | FAIL: owner-only wording | PASS |
| R | Architectural traceability appendix | Owner/rule/eligibility content appears only in Appendix A | Traceability outside primary narrative | commission renderer | complete document split assertion | FAIL: not acceptance-proven | PASS |
| S | Markdown structural validity | Exactly one H1, 16 sections, A–D, complete newline | No malformed/duplicate/truncated structure | `validate_research_commission_markdown` | fail-closed validator + full file | FAIL: trailing `##` | PASS |
| T | Twin Map regression | Complete 200 response contains canonical 14-enterprise composition and saved context | Existing Twin Map works | `executive_workspace_page` | actual complete route response | PASS observed | PASS |
| U | Research Gaps regression | Complete 200 response has all collection cards/counts | Existing gaps works | `_research_gaps` | actual complete route response | PASS observed | PASS |
| V | Import regression | Repository package accepted through upload handler | Import and picker contract retained | `upload_and_validate_blueprint` | configured-path import tests | PASS observed | PASS |
| W | Commercial Mission persistence regression | Save, reload and fresh requests retain all values | Persistence/restart-safe | `save_commercial_context` | filesystem store + fresh handler calls/tests | FAIL: field loss previously | PASS |
| X | Promotion fail-closed regression | Candidate state unchanged; no promotion invoked; governance suite passes | No automatic promotion | existing promotion owners | regression tests and response inspection | PASS observed | PASS |

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

- Twin Map: `executive-research-commission-product-acceptance/01-twin-map.html`
- Research Gaps: `02-research-gaps.html`
- Advanced Inspection: `03-advanced-inspection.html`
- reopened Commercial Mission: `04-commercial-mission.html`
- complete canonical deliverable: `05-executive-research-commission.md`
- validator results: `06-validation.txt`

The export proves complete scope and deterministic mission emphasis. BT Group, BBC and ITV receive exact named-priority-customer reasons; no other enterprise receives that reason. Capability and timing reasons require explicit Twin relations. The canonical register preserves all subjects regardless of emphasis.

## Remaining known limitations

Canonical records that do not supply an owner type remain explicitly unresolved rather than being guessed. This is a classification research requirement, not a manual-edit defect. Paid or unavailable evidence remains represented as an Unknown under the existing evidence contract. Neither limitation makes the commission malformed or narrows its scope.

## Recommendation

Every contract row is proven against a complete configured-path response and is **PASS**. The generated Markdown can be issued without manual editing. **MERGE**.
