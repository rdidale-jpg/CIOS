# TEL-001 Researcher-to-Flora Translation Audit

**Change ID:** TEL-001-TRANSLATION-AUDIT-2026-08-05  
**Evidence package:** `docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip` (unchanged)  
**Scope:** architecture and runtime audit only. No semantic translation, validation, governance, promotion, Observation logic, adapter, or TEL-001 package changes are proposed or implemented in this sprint.

## 13. Executive summary for the Chief Architect

- **What contract was the Researcher following?** The Researcher pack directs missions to emit `industry-overview`, `enterprise-dossier`, `market-participant`, `programme`, `opportunity`, `reinvention-assessment`, `industry-membership`, release manifest, Evidence, Unknown and Contradiction objects using the shared Researcher portable Twin Object Profile `TOP-RESEARCHER-PORTABLE-OBJECTS-v1`, plus mission instructions preserving EI-001/EI-002/EI-003/EI-012, IT-001 and MPT-001 ownership.
- **What contract is Flora actually consuming?** Flora consumes a Blueprint package envelope and manifest through package detection, then executes the `researcher_v1.json` selectors in `cios_twin_adapter.py` into staged `CandidateRecord` objects. Executive pages consume the later `SemanticTwin` read projection and owner-assessment/readiness projection, not the raw Researcher records directly.
- **Where do they diverge?** The Researcher package contains rich object-family JSON fields; Flora's runtime boundary normalises those into candidate payloads, semantic collections and owner-assessment requirements. Divergence occurs where profile selectors, adapter aliases, semantic constructors, subject resolution, Observation builders, owner assessment and page projections do not share one executable canonical contract.
- **Why did earlier fixes not change the screens?** Tests often exercised package acceptance, profile loading, staging counts, diagnostics or page snippets without proving full unchanged TEL-001 import through semantic assembly, owner assessment and rendered executive pages. Existing stale staging can also preserve pre-change candidate state until a fresh import/restage occurs.
- **Which parts now work?** TEL-001 is recognised as a Flora import package, staged as candidate records and materially classified for industry overview, enterprises, market participants, opportunities, reinvention assessments, Evidence, Unknowns and Contradictions. Runtime diagnostics report balanced candidate-to-semantic counts for many families.
- **Which parts do not?** Owner-assessed completeness and Observation-backed executive intelligence are incomplete or inconsistent by object family: industry overview reports missing statement/dimension coverage; enterprises report missing subject/owner assessment; opportunities lack complete metric/value/buyer/timing projection; reinvention remains partially projected; programmes can generate observations but are inconsistently surfaced.
- **What should be fixed first?** Make `TOP-RESEARCHER-PORTABLE-OBJECTS-v1`/Blueprint manifest/Twin semantic construction the single executable producer-consumer contract, then add stale-candidate control and end-to-end TEL-001 route coverage.
- **What visible outcome should that produce?** A fresh TEL-001 import should show factual industry, enterprise, participant, programme, opportunity and reinvention content on executive pages with Research Gaps distinguishing absent evidence from unmapped or unassessed evidence.
- **What should not be changed?** Do not hard-code TEL-001, weaken validation, add another adapter, change governance/promotion, or create Observation logic outside EI-012 ownership.

## 1. Authoritative contract inventory

| Source | Repository path | Identifier | Status/version | Canonical owner | Classification | Researcher consumes | Flora consumes | Test enforcement |
|---|---|---|---|---|---|---|---|---|
| Researcher pack manifest | `knowledge-packs/researcher/manifest.yaml` | Researcher Knowledge Pack | versioned pack | Researcher pack owner / Chief Architect | canonical distribution inventory | yes | indirectly | pack tests verify packaged contract names |
| Researcher GPT instructions | `knowledge-packs/researcher/configuration/Researcher-GPT-Instructions.md` | mission operating doctrine | governed prose | Chief Architect / Researcher | canonical prose for producer behaviour | yes | no | not end-to-end |
| Portable object profile | `cios/contracts/twin_object_profiles/researcher_v1.json`; copied to `knowledge-packs/researcher/contracts/researcher_v1.json` | `TOP-RESEARCHER-PORTABLE-OBJECTS-v1` | v1 | Shared Researcher portable object profile owner | canonical/derived copy pair; drift risk | yes | yes, via adapter | selector tests and TEL-001 staging tests |
| Flora Blueprint manifest schema | `knowledge-packs/researcher/package-contracts/flora-blueprint-import/blueprint_manifest.schema.json` | Flora Blueprint package contract | versioned | package exchange owner | canonical package envelope for producer | yes | yes | package-contract tests |
| Build script | `knowledge-packs/researcher/package-contracts/flora-blueprint-import/build_flora_import.py` | package builder | implementation-owned | Researcher pack | derived/generated | yes | no | pack tests only |
| TEL-001 package manifest | inside evidence ZIP: `blueprint_manifest.json` and `content/source/release_manifest_wave5_draft.json` | TEL-001 release manifest | generated draft | Researcher output owner | generated | output | yes | TEL-001 regression tests |
| Flora contract detector | `cios/applications/flora/blueprint_import/package_contracts.py` | package detection | implementation | Flora import runtime | implementation-only | no | yes | import tests |
| Flora validator/stager | `cios/applications/flora/blueprint_import/validator.py` | Blueprint validator | implementation | Flora import runtime | implementation-only | no | yes | validation/staging tests |
| Researcher adapter | `cios/applications/flora/blueprint_import/cios_twin_adapter.py` | `MAPPING_VERSION` | implementation | Flora import runtime | adapter-owned | no | yes | TEL-001 adapter tests |
| Candidate model | `cios/applications/flora/blueprint_import/candidates.py` | CandidateRecord | implementation | Flora candidate owner | implementation-only | no | yes | staging/review tests |
| Semantic Twin projection | `cios/applications/flora/blueprint_import/twin_governance.py` | SemanticTwin/readiness | implementation | Flora projection owner | implementation-only, should be derived | no | yes | page/workspace tests |
| Executive workspace pages | `cios/applications/flora/blueprint_import/executive_workspace.py` | page view models | implementation | Flora presentation owner | presentation/projection | no | yes | route snippet tests |
| EI-012 | `architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md`; pack copy | EI-012 | accepted architecture | Enterprise Observation owner | canonical | yes | partially | guardrail/prose tests only |
| ADR-024 / FEIR-001 / EIRP-001 | architecture/docs locations found by repository search | accepted runtime boundaries | accepted/proposed per source | Chief Architect | canonical governance/runtime constraints | yes | yes | scattered tests |
| Research Gap runtime rules | `cios/applications/flora/blueprint_import/executive_workspace.py`; `docs/flora-research-brief-ownership.md` | owner-projection-v1 / research brief ownership | implementation plus prose | owner assessment/readiness | duplicated/implementation-owned | no | yes | Research Gap tests |
| TEL-001 reconciliation docs | `docs/evidence/Telecommunications-Media-Sport-Executive-Research-Commission.md` and TEL-001 package source reports | generated/prose | generated | Researcher output | generated evidence | yes | no/directly | no full e2e enforcement |

**Supersession finding:** no single repository file currently acts as the executable canonical semantic contract from Researcher profile through Flora SemanticTwin, Observation, owner assessment and page view model. The portable profile is the closest source, but semantic/runtime fields are also owned by adapter code and projections.

## 2. Producer-consumer lineage map

| Family | Researcher source profile | Package record shape | Manifest declaration | Flora adapter | Candidate shape | Semantic shape | Observation shape | Owner assessment shape | Page view-model shape | First material risk |
|---|---|---|---|---|---|---|---|---|---|---|
| Industry Overview | `industry-overview` selectors | `industry_overview_wave5.json` object | release manifest object versions | researcher profile adapter | CandidateRecord payload with source diagnostics | `SemanticTwin.industry_overview` | often missing_statement | readiness aspect industry-overview | Twin Map/Industry aspect | dimensions flattened vs owner completeness |
| Enterprise Dossier | `enterprise-dossier` | 6 dossier objects | release manifest | adapter class aliases | enterprise candidates | semantic enterprises | missing/limited subject observations | enterprises readiness | enterprise cards/aspects | canonical subject/owner assessment absent |
| Market Participant | `market-participant` | 17 participant objects | release manifest | adapter | participant candidates | semantic market participants | limited observations | participant delegation unresolved | participant aspect cards | useful facts render despite incomplete owner assessment |
| Transformation Programme | `programme` | 13 programme objects | release manifest | adapter | programme candidates | semantic programme hypotheses | programme observations can be built | programme readiness | major programmes/aspects | source/staged count may diverge on page summary |
| Opportunity | `opportunity` | 17 opportunity objects | release manifest | adapter | opportunity candidates | semantic opportunity hypotheses | metric/value incompleteness | opportunity readiness | opportunity table/developing hypotheses | value/timing/buyer fields incomplete for sales-ready projection |
| Reinvention Assessment | `reinvention-assessment` | 7 assessment objects | release manifest | adapter | reinvention candidates | semantic timing assessments | incomplete | reinvention readiness | Reinvention Timing | affected subject/function mapping incomplete |
| Evidence | EI-012/Evidence profile | 92 evidence records | evidence snapshot | adapter/preservation | support candidates | semantic evidence/support | input to observations | evidence coverage | details/inspection | lineage preserved but not always used in pages |
| Unknown | EI-012 Unknown | 30 unknown records | unknown snapshot | adapter | unknown candidates | semantic unknowns | not observations | gap dispositions | Research Gaps | conflated with unmapped/unassessed states |
| Contradiction | EI-012 Contradiction | 11 contradiction records | contradiction snapshot | adapter | contradiction candidates | semantic contradictions | not observations | gap dispositions | Research Gaps | contradiction state not separated from incompleteness |
| Relationship | EI-002 relationship | 308 relationships | relationship sets | adapter/reference resolver | relationship candidates | semantic relationships | support lineage | owner-assessment input | Advanced Inspection | target normalisation/reference drift |
| Membership | membership profile | 50 membership records | membership sets | adapter | membership candidates | semantic memberships | support lineage | industry/member coverage | Advanced Inspection | owner unresolved for participant delegation |
| Release Manifest | package/release profile | manifest objects | package envelope | detector/manifest reader | package identity | import context | none | stale/profile version context | headers/history | draft/generated vs canonical release states |
| Residual Other | unmatched records | package files/records | record_sets | unsupported/projection-only | residual candidates | `other` collection | none | none | Advanced Inspection | unsupported content can be hidden from executive pages |

## 3. Object-family support matrix using TEL-001 counts

Counts from the unchanged ZIP: Industry 1, Enterprise 6, Market Participant 17, Programme 13, Opportunity 17, Reinvention 7, Evidence 92, Unknown 30, Contradiction 11, Relationship 308, Membership 50. Runtime diagnostics observed in tests show balanced candidate/semantic/projection/rendered counts for many families but zero owner-assessed counts before governance.

| Family | Source | Imported | Staged | Semantic | Obs generated | Persisted Obs | Owner-assessed | Projected | Rendered | Residual | Rejected/quarantined | First failing boundary | Current runtime owner |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Industry Overview | 1 | 1 | 1 | 1 | 0/incomplete | 0 | 0 | 1 | 1 | 0 | 0 | owner completeness/Observation statement | SemanticTwin/readiness |
| Enterprise Dossier | 6 | 6 | 6 | 6 | 0/incomplete | 0 | 0 | 6 | 6 | 0 | 0 | canonical subject/owner assessment | enterprise projection |
| Market Participant | 17 | 17 | 17 | 17 | limited | 0 | 0 | 17 | 17 | 0 | 0 | owner delegation | participant projection |
| Programme | 13 | adapter-dependent | adapter-dependent | hypotheses | some | 0 | 0 | page-dependent | page-dependent | possible | 0 | page/semantic collection mismatch | programme projection |
| Opportunity | 17 | 17 | 17 | 17 | incomplete metrics | 0 | 0 | 17 | developing only | 0 | 0 | sales-ready projection completeness | opportunity projection |
| Reinvention | 7 | 7 | 7 | 7 | incomplete | 0 | 0/1 projections | 7 | 7 | 0 | 0 | affected subject/function resolution | reinvention projection |
| Evidence | 92 | 92 | 92 | 92 | support only | 0 | 0 | 92 | inspection | 0 | 0 | evidence-to-observation use | evidence/support owner |
| Unknown | 30 | 30 | 30 | 30 | n/a | n/a | n/a | 30 | gaps/inspection | 0 | 0 | reason-state interpretation | gap projection |
| Contradiction | 11 | 11 | 11 | 11 | n/a | n/a | n/a | 11 | gaps/inspection | 0 | 0 | contradiction vs deficiency | gap projection |
| Relationship | 308 | 308 | 308 | semantic links | n/a | n/a | partial | inspection | inspection | possible | reference failures possible | reference resolution | relationship runtime |
| Membership | 50 | 50 | 50 | memberships | n/a | n/a | partial | inspection | inspection | possible | owner unresolved | membership runtime |

## 4. Field-level reconciliation matrix with TEL-001 values

Representative source fields were inspected from the TEL-001 JSON files.

| Family/field | Source field | Profile selector | Adapted/persisted candidate | Semantic field | Canonical subject | Observation field | Owner assessment input | Projection/rendered field | Final result |
|---|---|---|---|---|---|---|---|---|---|
| Industry definition/boundary | `definition`, `executive_summary` | industry overview selector | payload/source_payload | industry overview summary | Industry Overview | statement expected but often missing | boundary/definition dimension | industry aspect text | present as candidate; incomplete as owner-assessed statement |
| Industry subsectors | source overview structure | selector | payload | subsector/list dimensions | Industry Overview | none/limited | required overview dimension | Research Gaps | may be treated as missing dimension |
| Industry value chain | `value_chain` | selector | payload | value chain | Industry Overview | none/limited | value-chain completeness | aspect/gap | present but can be flattened |
| Industry economics | `economics` | selector | payload | economics | Industry Overview | none/limited | size/economics | aspect/gap | present candidate, incomplete owner assessment |
| Industry regulation/PESTLE | regulatory/pressure fields | selector | payload | pressures | Industry Overview | none/limited | PESTLE | gaps | unmapped or insufficiently projected |
| Enterprise identity | `id`, `name`, `corporate_identity` | enterprise selector | enterprise candidate | enterprise identity/name | enterprise | subject expected | identity | enterprise card | renders name; owner assessment pending |
| Enterprise purpose/strategy | `executive_overview`, `corporate_strategy` | selector | payload | description/strategy | enterprise | statement limited | purpose/strategy | enterprise details | partial factual render |
| Enterprise operating/financial/tech/ecosystem | `business_units`, `financial_intelligence`, `operating_model`, `technology_landscape`, `transformation_portfolio` | selector | payload | enterprise attributes | enterprise | none/limited | density requirements | aspects/gaps | source present but not fully assessed/projected |
| Market participant identity/role | `id`, `name`, `classification`, `role` | participant selector | participant candidate | participant identity/role | participant | limited | identity/role | participant cards | useful rendered content despite owner gap |
| Market capabilities/relationships/activity | `capabilities`, `relationships`, `current_activity` | selector | payload | participant attributes | participant | limited | relationship completeness | cards/inspection | partial |
| Programme owner/objective | `owning_enterprise`, `programme_name`, `summary`, `problem` | programme selector | programme candidate | programme hypothesis | enterprise/programme | programme observation candidate | owner/objective | major programmes | can generate observations; page support inconsistent |
| Programme phase/timing/milestones | `phase`, `timeline`, `procurement` | selector | payload | phase/timing | programme | observation timing | milestones/procurement | gaps/aspects | incomplete where milestones absent |
| Opportunity customer/problem | `named_customer`, `business_unit`, `customer_problem` | opportunity selector | opportunity candidate | opportunity hypothesis | customer/account | incomplete | customer/problem | opportunity developing hypotheses | present but not sales-ready |
| Opportunity value/timing/confidence | `commercial_value`, `expected_procurement_timing`, `confidence` | selector | payload | value/timing/confidence | opportunity | metric completeness expected | value/timing | opportunity table | metric incompleteness blocks ready state |
| Reinvention subject/mechanism | `scope`, `ai_disruption_mechanism`, `business_functions_affected` | reinvention selector | assessment candidate | timing assessment | affected subject | incomplete | pressure/function | Reinvention Timing | affected subject resolution incomplete |
| Reinvention timing/response/evidence | `expected_tipping_point`, `timing`, `evidence`, `confidence` | selector | payload | timing/confidence | affected enterprise/domain | incomplete | timing evidence | Reinvention Timing/gaps | partial projection only |

## 5. Translation ownership map

| Component | Translation performed | Canonical owner | Governed contract? | Duplicates/drift risk | Test protection |
|---|---|---|---|---|---|
| Profile JSON | selectors and class aliases | portable object profile | yes | can drift from semantic code | profile tests |
| Python adapter | executes selectors; normalises classes; emits mapping diagnostics | Flora import | partially | high | TEL-001 import tests |
| Validator aliases | record-set/package class acceptance | Flora validator | no/prose | medium | validation tests |
| Candidate class mappings | CandidateRecord classifications | Flora candidate owner | no | high | staging tests |
| Semantic constructors | CandidateRecord to SemanticTwin | Flora projection owner | no executable shared contract | high | partial page tests |
| Subject resolvers | names/identity keys | Flora projection/governance | partial | high | scattered |
| Observation builders | candidate facts to Observation-like records | EI-012 owner should govern | partial | high | incomplete |
| Projection mappings | semantic to readiness/page DTOs | Flora presentation | no | high | snippet route tests |
| Template fallbacks | missing content text | Flora presentation | no | medium | UI tests |
| Research Gap rules | deficiency/action generation | owner assessment/readiness | partial | high | Research Gap tests, not full state matrix |

## 6. Earlier successful-runtime comparison

Earlier Banking/BT Flora experiences proved that Flora can render useful executive intelligence when data enters through Flora-native runtime structures, direct memory records, hand-built observations/fixtures, legacy Blueprint shapes or demonstrator-specific projections. They did **not** prove that a Researcher-produced portable Twin Object Profile package could travel unchanged through package manifest, adapter, candidate staging, semantic assembly, Observation lifecycle, owner assessment and page rendering. BT/Banking success therefore validated page and runtime concepts, not this portable Researcher-to-Flora contract.

## 7. Observation architecture/runtime decision report

Observation generation is inconsistent by object family in the current runtime:

- Factual rendering is not universally mandatory; Market Participants and Enterprises can render candidate/semantic facts without persisted Observations.
- Conclusions, reasoning and durable memory should be Observation-backed under EI-012.
- Programmes generate more Observation-like outputs because owner/objective/phase/timing statements map naturally to atomic change activity.
- Industry reports `missing_statement` because broad overview dimensions do not become a single supported EI-012 statement cleanly.
- Enterprises report `missing_subject` where canonical subject resolution/owner assessment is not complete.
- Market Participants render useful content because presentation can use semantic candidate facts even while owner assessment remains unresolved.
- Opportunities report metric incompleteness because sales-ready projection requires value, timing, customer/problem and confidence fields, not just source presence.
- Reinvention remains incomplete because affected subject/function/timing-pressure mapping crosses domain, enterprise and programme ownership.

Decision: Observation alignment is required for durable conclusions, but factual candidate presentation can improve visibly before all Observation lifecycle work is complete, provided it remains clearly candidate/projection-only.

## 8. Research Gap reason-state matrix

| State | Meaning | Current conflation risk | Correct gap wording |
|---|---|---|---|
| source_absent | Researcher did not provide evidence/field | genuine research gap | Research source field |
| source_present_unmapped | field exists in TEL-001 but selector/adapter missed it | mislabeled as research gap | mapping/contract gap |
| source_present_not_persisted | adapter saw it but candidate storage lost it | mislabeled as source absence | staging defect |
| semantic_field_absent | candidate exists but SemanticTwin omitted field | mislabeled as researcher deficiency | semantic construction defect |
| observation_absent | fact exists but no EI-012 Observation | may block reasoning incorrectly | Observation alignment required |
| owner_assessment_pending | semantic candidate exists but canonical owner has not assessed | currently common | governance/owner assessment pending |
| projection_absent | semantic/assessment exists but page DTO omits | hidden as no content | presentation/projection defect |
| genuine_owner_deficiency | owner assessed required dimension incomplete | true research gap | owner-assessed deficiency |
| Unknown | explicit unresolved state supplied | should not be failure | preserve Unknown and monitor |
| Contradiction | competing claims supplied | should not be missing | preserve contradiction and resolution action |

## 9. Stale-candidate audit

Audit fields available or needed: deployed SHA from `deployment_metadata()`, import timestamp from `BlueprintPackageRecord.received_at`, staging timestamp/version from validator staging history, profile version from package identity/profile metadata, adapter version from `MAPPING_VERSION`, semantic/projection versions from runtime code constants where available, Observation profile version from EI-012/profile metadata.

Reliable mechanism proposed: persist a `runtime_fingerprint` on every staging result containing commit SHA, branch, build timestamp, adapter mapping version, portable profile checksum, semantic constructor version, owner assessment version and projection version. On `/blueprint-import` and every candidate page compare active staging fingerprint with current runtime fingerprint and show `Stale candidate` / `Requires fresh import or restage` when any material translation component changed.

## 10. Test coverage audit

| Test family | Contract loading | Validator | Adapter | Candidate staging | Semantic assembly | Observation builder | Projection | Rendered route | Research Gaps | Full unchanged TEL-001 |
|---|---|---|---|---|---|---|---|---|---|---|
| researcher pack tests | yes | no | no | no | no | no | no | no | no | no |
| Flora package contract tests | yes | yes | no | no | no | no | no | no | no | partial |
| TEL-001 blueprint regression | partial | yes | yes | yes | partial | limited | limited | snippets | limited | yes, but not all visible outcomes |
| executive workspace tests | no | no | no | fixture | yes-ish | no | yes | yes | partial | no |
| Research Gap tests | no | no | no | fixture | partial | no | yes | yes | yes | no |
| UI upload tests | no | no | no | no | no | no | no | yes | no | no |

Missing coverage: one deployed-equivalent end-to-end test should import the unchanged TEL-001 ZIP, force restage under current runtime fingerprint, visit Twin Map, Industry, Enterprises, Participants, Programmes, Opportunities, Reinvention, Research Gaps and Diagnostics, and assert concrete source values appear or reason states correctly explain why not.

## 11. Root-cause classification

- Duplicated contract: portable profile, adapter, semantic constructors and projections all encode field meaning.
- Adapter drift: selector aliases can change independently from source profile and page needs.
- Semantic construction defect: rich candidate fields are not uniformly represented in SemanticTwin.
- Canonical subject resolution defect: enterprises/reinvention/participant ownership remains unresolved in places.
- Observation generation defect: object-family treatment differs without one EI-012 executable boundary.
- Owner assessment lifecycle defect: candidate facts are treated as pending governance but pages can imply missing research.
- Projection defect: opportunity/programme/reinvention completeness rules suppress facts that exist but are not recommendation-ready.
- Research Gap interpretation defect: absent, unmapped, unassessed, unknown and contradicted states can be collapsed.
- Stale candidate/runtime state: previous staging can survive newer profile/adapter/runtime changes.
- Governance ambiguity: participant and industry owner delegation remains less executable than enterprise owners.
- Test coverage defect: repository tests pass without verifying visible executive intelligence across full TEL-001.

## 12. Prioritised remediation proposal (not implemented)

| Priority | Canonical source to change | Derived components affected | Implementation impact | Operational impact | Migration | Test requirement | Expected visible outcome | Risk | Rollback |
|---|---|---|---|---|---|---|---|---|---|
| 1 Contract alignment | `TOP-RESEARCHER-PORTABLE-OBJECTS-v1` plus Blueprint manifest docs | adapter, validator, semantic constructors | make executable selectors and semantic target fields shared | producer and consumer speak same contract | restage candidates | contract compatibility and TEL-001 e2e | source fields no longer vanish | medium | revert profile/semantic checksum |
| 2 Stale-state control | staging/runtime fingerprint contract | registry, staging history, upload UI | persist/compare fingerprints | operators know when to reimport/restage | no data migration, restage old candidates | stale detection tests | no false validation from old candidates | low | ignore fingerprint with warning |
| 3 Shared semantic construction | semantic mapping spec owned by contract | adapter and SemanticTwin | remove duplicated field mapping | consistent object family output | restage | semantic count/field tests | richer factual pages | medium | use prior constructor version |
| 4 Canonical subject resolution | owner assessment contracts | subject resolver/readiness | governed identity rules | fewer missing_subject gaps | restage/identity review | subject-resolution tests | enterprise/reinvention subjects resolve | medium | prior resolver |
| 5 Factual candidate presentation | presentation model spec | page DTOs | show candidate facts distinctly from governed conclusions | visible executive value before observations | none | route assertions for TEL values | factual content visible with candidate labels | medium | hide candidate section |
| 6 Observation alignment | EI-012 | observation builders/persistence | object-family observation rules | durable reasoning improves | possible migration to observations | EI-012 builder tests | programme/industry/enterprise observation parity | high | disable new observation writes |
| 7 Owner assessment | owner assessment lifecycle | readiness/research gaps | run assessments after staging without promotion | gaps become precise | assessment state migration | owner-assessed counts | true completeness status | high | return to pending governance |
| 8 Research Gap correction | Research Gap ownership rules | gap projection/templates | reason-state matrix implemented | researcher brief stops asking for already supplied facts | none | reason-state e2e | gaps distinguish unmapped vs unknown vs absent | medium | previous gap projection |

Smallest coherent sequence: align the portable contract and semantic target first, add stale-state control immediately after, then improve candidate factual presentation before deeper EI-012 Observation and owner-assessment lifecycle changes.

## Appendix A — TEL-001 package source inventory

- `industry_overview_wave5.json`: 1 object.
- `enterprise_dossiers_wave5.json`: 6 objects.
- `market_participant_profiles_wave5.json`: 17 objects.
- `programme_objects_wave5.json`: 13 objects.
- `opportunity_objects_wave5.json`: 17 objects.
- `reinvention_assessments_wave5.json`: 7 objects.
- `evidence_register_wave5.json`: 92 objects.
- `unknown_register_wave5.json`: 30 objects.
- `contradiction_register_wave5.json`: 11 objects.
- `relationship_register_wave5.json`: 308 objects.
- `membership_register_wave5.json`: 50 objects.

## Appendix B — Current sprint implementation summary

This PR adds the main upload-screen change record backed by `cios/applications/flora/config/current_pilot_change.json` and documents this audit. It intentionally makes no semantic translation changes.
