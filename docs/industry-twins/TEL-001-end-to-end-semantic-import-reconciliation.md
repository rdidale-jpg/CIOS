# TEL-001 end-to-end semantic import reconciliation

## Operational validation

- Regression package: `docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip`.
- Package SHA-256: `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.
- The package is consumed unchanged by the manual Import Twin path; tests assert the checksum before and after import.
- Import staging remains candidate-only: canonical mutation count is `0`, no memory repository is created, and promotion permission remains separate.
- A fresh upload re-stages persisted candidates for the deployed UI when a checksum-deduplicated run contains legacy unclassified candidates, preventing stale pre-semantic inspection.

## Runtime architecture trace

| Boundary | Runtime owner | TEL-001 behaviour |
| --- | --- | --- |
| Package receipt | `BlueprintPackageRegistry.receive` | Stores immutable archive receipt, inspection metadata, package checksum, package reference and import run identifier. |
| Package inspection | Blueprint package inspection and manifest contracts | Reads `blueprint_manifest.json`, 88 governed content files and 36 declared record sets without inferring object type from filenames. |
| Record-set validation | `BlueprintPackageValidator.validate_and_stage` | Validates declared rows, profile versions and per-row semantics; stages 1,060 candidate records with 648 accepted and 412 ignored lineage/residual records. |
| Semantic adaptation | `researcher_profile_adapter.adapt_researcher_payload` | Maps Researcher profile fields to canonical candidate vocabulary while preserving the full source row in `source_payload` and recording mapped/unmapped field diagnostics. |
| Candidate staging | `CandidateStagingRepository` | Persists accepted, ignored and diagnostic candidate records by import run; staged records remain non-canonical. |
| Candidate persistence | Candidate staging JSONL and summary | Stores `candidate_object_class`, validation state, source file, source location, original source identifier and untouched source payload. |
| Canonical-object construction | `assemble_semantic_twin` | Builds the read-only semantic Twin from persisted candidates, resolves enterprise identity owners and reference links, and reports unresolved references. |
| Canonical-owner assessment | `executive_assessments` / owner-projection-v1 | Projects declared owner assessment outputs only. Candidate intelligence that has not crossed governance is marked `assessment_pending_governance`; supplied Reinvention Assessment rows are projected as candidate owner outputs. |
| Review-plan generation | Blueprint review plan | Produces candidate governance review without promotion and keeps Twin identity, scope and canonical owner unresolved when not governed by the package contract. |
| Candidate-mode presentation | `executive_workspace_page` and `executive_record_view_model` | Uses the same persisted semantic Twin and canonical executive-record view model for deployed explorer, aspect and enterprise dossier pages; substantive fields render from canonical candidate attributes, not from raw presentation source reads. |
| Promoted-mode presentation | Existing promotion repositories | Not exercised for TEL-001 because the package remains unpromoted; promotion controls and owner boundaries are preserved. |
| Research Gap projection | `research_requirements` plus `executive_assessments` lifecycle states | Does not commission already-supplied candidate intelligence again when it is present and mapped but awaiting governance or owner assessment. |

## Object-family reconciliation matrix

| Family | Source collection | Count | Declared class | Semantic adapter | Staged/persisted class | Canonical owner | Owner assessment | Executive collection | Rendered count | Rejected | Quarantined | Projection-only / residual disposition |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| Industry Overview | `record_sets/industry_overview_wave5.ndjson` | 1 | `industry_twin` | Researcher profile adapter | `industry_twin` | IT-001 Industry Twin | Pending governance unless owner assessment is declared | `industry-overview` | 1 | 0 | 0 | No loss; substantive profile fields render. |
| Enterprise Dossier | `record_sets/enterprise_dossiers_wave5.ndjson` | 6 | `enterprise_twin` | Researcher profile adapter | `enterprise_twin` | EI-001 / EIF-001 Enterprise Twin | Pending governance | `enterprises` | 6 | 0 | 0 | No loss; six identity owners anchor linked records. |
| Market Participant | `record_sets/market_participant_profiles_wave5.ndjson` | 17 | `market_participant_twin` | Researcher profile adapter | `market_participant_twin` | IT-001 participant delegation | Pending governance | `market-participants` | 17 | 0 | 0 | No loss; roles/domains/capabilities project. |
| Transformation Programme | `record_sets/programme_objects_wave5.ndjson` | 13 | `transformation_programme` | Researcher profile adapter | `transformation_programme` | EI-001 / EI-002 change landscape | Pending governance | `transformation-programmes` | 13 | 0 | 0 | No loss; programme owner, objective, phase and timing project. |
| Opportunity | `record_sets/opportunity_objects_wave5.ndjson` | 17 | `opportunity_hypothesis` | Researcher profile adapter | `opportunity_hypothesis` | EI-004 / FP-009 opportunity owner | Pending governance | `opportunities` | 17 | 0 | 0 | Exactly 17 canonical hypotheses; nested support records do not inflate counts. |
| Reinvention Assessment | `record_sets/reinvention_assessments_wave5.ndjson` | 7 | `ai_reinvention_assessment` | Researcher profile adapter | `ai_reinvention_assessment` | EI-001 / EIF-001 / EI-003 / FP-012 | Supplied candidate owner assessment output | `reinvention-assessments` | 7 | 0 | 0 | All seven have explicit candidate dispositions. |
| Evidence | `record_sets/evidence_register_wave5.ndjson` | 92 | `evidence` | Researcher profile adapter | `evidence` | EI-013 Evidence authority | Not a completeness assessment | `evidence-sources` | 92 | 0 | 0 | Linked by stable evidence references. |
| Unknown | `record_sets/unknown_register_wave5.ndjson` | 30 | `unknown` | Researcher profile adapter | `unknown` | Unknown / investigation authority | Explicit Unknown state | `unknowns` | 30 | 0 | 0 | Visible and not converted into fabricated content. |
| Contradiction | `record_sets/contradiction_register_wave5.ndjson` | 11 | `contradiction` | Researcher profile adapter | `contradiction` | EI-012 contradiction authority | Review required | `contradictions` | 11 | 0 | 0 | Visible conflict state is preserved. |
| Relationship | `record_sets/relationship_register_wave5.ndjson` | 308 | `relationship` | Researcher profile adapter | `relationship` | EI-002 Knowledge Graph | Linkage support, not assessment | `relationships` | 308 | 0 | 0 | Endpoints retained as references. |
| Membership | `record_sets/membership_register_wave5.ndjson` | 50 | `membership` | Researcher profile adapter | `membership` | Governed collection membership | Linkage support, not assessment | `memberships` | 50 | 0 | 0 | Parent/child references retained. |
| Release Manifest | manifest record set | 1 | `release_manifest` | Staging adapter | `release_manifest` | Release governance | Not an assessment | `release-manifests` | 1 | 0 | 0 | Package governance declaration retained. |
| Other Twin content | Refresh/lineage/supporting record sets | 412 ignored, 95 accepted residual triggers | Mixed / unsupported | Staging classification | `refresh_trigger` and ignored residual classes | Lineage/support owner | Not assessed | `other` | 507 runtime total / 95 accepted projection | 0 | 0 | Residual reason distinguishes lineage-only, unsupported and non-executive support material. |

## Field-level mapping matrix using TEL-001 values

| Family | Source field | Adapted/canonical field | Assessment state | Executive view-model/rendered value |
| --- | --- | --- | --- | --- |
| Industry Overview | `definition`, `executive_summary`, economics in profile | `description`, `industry_profile` | Present and mapped; owner assessment pending governance | `£34.7bn, down £0.3bn / 0.8% year-on-year`; `Commercial Implications`. |
| Enterprise Dossier | `name`, `executive_overview.what`, `corporate_strategy`, `operating_model`, `financial_intelligence`, `technology_landscape`, `transformation_portfolio`, `reinvention_assessment` | `enterprise_name`, `description`, `strategy`, `operating_structure`, `financial_context`, `technology`, `programmes`, `transformation_posture` | Present and mapped; owner assessment pending governance | BT Group renders `BT Group is a UK-headquartered telecommunications group` and `FTTP build and take-up`. |
| Market Participant | `name`, `classification`, `role`, `capabilities`, `relationships`, `current_activity`, `commercial_significance` | `organisation_name`, `domain`, `role`, `capabilities`, `relationships`, `current_activity`, `significance` | Present and mapped; owner assessment pending governance | Ofcom renders `Telecoms access, spectrum, complaints and infrastructure reporting` and `Regulator`. |
| Transformation Programme | `programme_name`, `owning_enterprise`, `owning_business_unit`, `strategic_objective`, `phase`, `timeline`, `budget`, `evidence` | `title`, `owner`, `business_unit`, `objective`, `phase`, `timing`, `investment`, `evidence_refs` | Present and mapped; owner assessment pending governance | `BT FY30 cost and operating-model transformation` renders with `FY26-FY30`. |
| Opportunity | `opportunity_title`, `named_customer`, `client_problem.customer_problem`, `business_unit`, `buyer`, `procurement_status_control`, `commercial_type_wave5`, `wave5_pipeline_qualification.value_type_wave5`, `timing.estimated_procurement_window`, `value.estimated_contract_value_range`, `evidence`, `unknowns`, `contradictions` | `title`, `affected_enterprises`, `client_problem`, `business_unit`, `buyer`, `procurement_status`, `commercial_type`, `value_type`, `procurement_timing`, `value_range`, `evidence_refs`, `unknown_refs`, `contradiction_refs` | Present and mapped; owner assessment pending governance | Opportunity page renders `Virgin Media O2` and `Shaping opportunity`; it does not show `Client problem not established` for supplied TEL-001 opportunities. |
| Reinvention Assessment | `scope`, `current_operating_model`, `business_functions_affected`, `ai_disruption_mechanism`, `timing`, `expected_tipping_point`, `executive_implications`, `evidence` | `title`, `summary`, `affected_functions`, `ai_disruption_mechanism`, `timing`, `expected_tipping_point`, `consequence`, `evidence_refs` | Supplied candidate owner assessment output | Reinvention page renders `Capital-intensive, regulated network operators` and `2026-2028`. |

## Field-loss boundary report

- Renaming is intentional and centralized in the Researcher profile adapter; presentation consumes only adapted canonical candidate fields.
- Source rows are retained in `source_payload`, and `mapping_diagnostics` records source, mapped and unmapped fields for every transformed family.
- Nested evidence, Unknowns and Contradictions are converted into reference fields where supported; relationship rows and evidence rows remain their own object families and are not promoted into opportunities.
- No field is accepted only in staging for the executive families covered by the regression: actual deployed explorer, aspect and enterprise dossier pages assert substantive TEL-001 values per major object family.
- Assessment-gated material is labelled as pending governance or supplied candidate owner assessment rather than rendered as fabricated completeness.

## Deployed page-path correction

Executable evidence identified that the explorer path already consumed `executive_record_view_model`, but the page-specific Industry Overview, Enterprise Dossier, Market Participant, Transformation Programme, Opportunity and Reinvention paths still used owner-assessment gates before rendering candidate fields. That contradicted this document's candidate-mode claim: staging and semantic-model assertions passed while deployed aspect/dossier HTML could report research gaps for fields already present in the candidate semantic model.

The corrected runtime keeps governance and promotion separate, but no longer uses pending owner assessment as a presentation suppressor. Page-specific routes now render inspectable canonical candidate attributes and carry explicit candidate / pending-governance labels; research-gap projection continues to distinguish supplied-but-unassessed fields from genuinely absent, invalid, unmapped, Unknown, Contradiction and owner-assessed deficiency states.

## Reinvention reconciliation

All seven `ai_reinvention_assessment` source rows are accepted, persisted, projected and rendered through `reinvention-assessments`. Their canonical owner is EI-001 / EIF-001 / EI-003 / FP-012. The final disposition for each row is `owner_assessment_supplied_candidate`: the package supplies assessment-shaped intelligence, but the import remains a candidate and is not automatically promoted.

## Opportunity reconciliation

TEL-001 contains exactly 17 Opportunity Objects and Flora renders exactly 17 canonical opportunity hypotheses. Evidence rows, relationship rows, source lines, sub-observations and commercial classifications are retained as support/fields; they are not counted as additional opportunity hypotheses. Opportunity titles/identifiers use the canonical title fields instead of falling back to generic scope labels.

## Research Gap interpretation

Research Gaps classify deficiencies through owner-projection lifecycle state. Present mapped candidate intelligence is not recommissioned merely because governance or owner assessment is pending. Genuine research actions remain available for explicit Unknowns, Contradictions requiring review, semantically invalid records, unmapped required content and owner-assessed deficiencies.

## Final recommendation

MERGE: the unchanged TEL-001 package is imported, staged, projected and rendered as coherent candidate Enterprise Intelligence across the executive workspace while governance and promotion controls remain intact.
