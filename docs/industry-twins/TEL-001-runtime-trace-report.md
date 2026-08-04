# TEL-001 imported candidate runtime trace

## Finding and classification

**First deployed failing boundary: validation-cache invalidation after checksum deduplication.** Receipt deliberately identifies an unchanged package by checksum and returns its existing import run. The semantic classifier had changed, but its mapping version had not. `validate_and_stage` therefore treated the old summary as current and returned before candidate creation, leaving the 1,060 persisted pre-semantic wrappers for Explore Twin. Validator-only tests passed because each used an empty temporary data directory and could not exercise the duplicate-package branch. The reusable correction advances the shared mapping version, forcing the existing governed validation service to restage an unchanged package without changing its identity or granting promotion authority.

The historical classifier and presentation vocabulary remain reusable: `validator.DECLARED_RECORD_SET_CLASSES` maps manifest declarations, and `semantic_twin.BUSINESS_COLLECTIONS` maps the persisted candidate class. The deployed divergence occurred before those corrected candidates reached persistence. After restaging, the runtime reads `candidate_object_class` (not a filename, wrapper type, implementation profile, or `payload.record_class`) and promotion remains a separate, explicitly authorised operation with zero canonical mutations during validation.

## Runtime flow and first boundary

```text
TEL-001 ZIP (immutable SHA-256 bd3924…1d07)
  ↓ BlueprintPackageRegistry.receive
Receipt: archive + BlueprintPackageRecord
  ↓ BlueprintPackageValidator.validate_and_stage
Validation / generic Blueprint inspection
  ↓ manifest record-set declaration → reusable semantic class mapping
Semantic candidate creation
  ↓ CandidateStagingRepository.save_candidate
blueprint_import/staging/<run>/candidates/<candidate-id>.json
  ↓ CandidateStagingRepository.list_candidates
Candidate governance / review planning
  ↓ assemble_semantic_twin → business_collections / executive_assessments
Twin Map and Executive Intelligence
  ↓ research_requirements / research_count_contracts
Research Gaps
```

The regression execution trace is: `receive` reads and immutably archives the bytes; `validate_and_stage` invokes `_inspect`; generic Blueprint record sets are assigned their declared semantic class; constructor validation changes seven pressure views to quarantined; `save_candidate` writes 1,060 JSON candidate records; `staging_summary` obtains them through `list_candidates`; the Executive Workspace passes those candidates through `_semantic_candidates` and `assemble_semantic_twin`; Twin Map reads `twin_readiness`; Research Gaps reads the same semantic twin through `research_requirements` and `research_count_contracts`.

## Repository map

| Owner/service | Stored or returned objects | Consumer |
|---|---|---|
| `BlueprintPackageRegistry` | Package receipt metadata and immutable archive location | validator, workspace identity, governance context |
| `CandidateStagingRepository` | dry-run summary and one JSON file per candidate | validation, governance/review, semantic Twin projection |
| `CandidateReviewRepository` | append-only decisions keyed by candidate | governance and promotion planning |
| `DryRunPlanRepository` / `ImportMappingRepository` | approved plan and proposed mappings | explicitly authorised promotion only |
| `CanonicalPromotionRepository` and canonical domain repositories | promoted canonical objects | post-promotion canonical runtime |
| `assemble_semantic_twin` | in-memory read-only semantic objects over staging | Twin Map, Executive Intelligence, Research Gaps |

Candidate persistence, candidate lookup, governance enumeration, Twin Map, and Research Gaps share `CandidateStagingRepository` for an unpromoted imported Twin. Governance decisions have a separate append-only repository, but that repository does not own candidate discovery. No projection reads the promotion repository for the pre-promotion candidate view.

The previous regression path always created a new registry under `tmp_path`; the deployed upload path first calls `BlueprintPackageRegistry.receive`, which returns the existing package/run for an identical SHA-256. Before this revision, the unchanged mapping-version marker made `validate_and_stage` return that run's old summary and candidates. This exact duplicate-upload branch is now covered through `upload_and_validate_blueprint`, persisted repository reads, `executive_workspace_page` Explore collections, and the Research Gap projection.

## Candidate inventory

The machine-readable inventory is [`TEL-001-runtime-candidate-inventory.json`](TEL-001-runtime-candidate-inventory.json). It enumerates all **648 semantic candidates** individually with candidate identifier, canonical class, owner, persistence location, governance state, visibility state, projection eligibility, source file, and original identifier.

| Validation / visibility state | Count | Governance | Projection |
|---|---:|---|---|
| accepted candidate | 641 | awaiting explicit candidate review | read-only semantic projection eligible |
| quarantined candidate | 7 | quarantined by validation | advanced inspection only |
| ignored lineage | 412 | not a semantic governance candidate | ineligible |

Accepted class inventory: 1 Industry Twin, 6 Enterprise Twins, 17 Market Participant Twins, 17 Opportunity Hypotheses, 13 Transformation Programmes, 92 Evidence, 30 Unknowns, 11 Contradictions, 308 Relationships, 50 Memberships, 1 Release Manifest, and 95 Refresh Triggers. The seven quarantined records are Transformation Pressure Views.

The imported classes that remain lineage-only are: `analyst_estimate_register`, `buyer_intelligence_register`, `change_log_wave4_to`, `composite_industry_twin`, `corrected_horizon_pipeline`, `corrected_opportunity_ids`, `existing_award_register`, `framework_market_register`, `horizon_reclassification_report`, `identity_resolution_table`, `named_open_opportunity_pipeline`, `opportunity_overlap_register`, `opportunity_qualification_scorecard`, `pipeline_totals`, `procurement_register`, `qualified_opportunity_register`, `residual_opportunity_register`, `shaping_opportunity_register`, `strategic_hypothesis_register`, `unclassified_register`, `unresolved_business_units`, and `unresolved_customer_identities`. They fail deliberately because the package declares register/report classes for which the runtime has no canonical semantic adapter. Their rows retain source class and payload as lineage rather than being guessed from filenames.

Wrapper types and `record_class` values are not discarded: `_records` preserves the manifest declaration as `candidate_object_class`, and semantic assembly preserves it as `SemanticObject.kind`. The evidenced causes were an incomplete declaration adapter (formerly all bare rows) and an incomplete business projection vocabulary (Industry Overview, Membership, and Release Manifest). Implementation profiles are validated but do not supply an alternative type adapter; legacy-only projection was not the cause.

## Projection inventory and trace

All counts below are for the unchanged archive after validation and before promotion.

| Twin Map section | UI / view model | Projection query | Repository count | Expected / projected count | Filtering and reason |
|---|---|---|---:|---:|---|
| Industry Overview | `_twin_map` / `twin_readiness` | `twin.objects` where kind is `industry_twin` | 1 | 1 / 1 concept | Owner-assessed completeness is 0 because no `high_fidelity_completeness_assessment` candidate was supplied; identity remains visible |
| Enterprises | `_aspect_page` / `business_collections` | assembled authoritative `enterprise_twin` identities | 6 | 6 / 6 | No identity candidates filtered; owner-assessed detail is separately 0 |
| Market Participants | `_aspect_page` / `business_collections` | kind `market_participant_twin` | 17 | 17 / 17 concepts | Detailed cards require owner assessment plus role, domain, evidence and consequence; these eligibility filters do not erase concept count |
| Major Programmes | `_aspect_page` / `twin.objects` | kind `transformation_programme` | 13 | 13 / 13 hypotheses | Sales/executive-ready detail additionally requires owner assessment, owner, consequence, stage, timing and evidence |
| Opportunities | `_aspect_page` / `business_collections` | canonical owner kind `opportunity_hypothesis` | 17 | 17 / 17 hypotheses | Recommendation eligibility additionally requires the opportunity contract and owner assessment |
| Reinvention Timing | `_aspect_page` / `twin.objects` | reinvention assessment kinds | 0 accepted; 7 quarantined pressure views | 0 / 0 assessment records | Seven pressure views are quarantined; pressure views are not silently reclassified as canonical Reinvention Timing assessments |

Evidence (92), Unknowns (30), Contradictions (11), Relationships (308), Memberships (50), one Release Manifest, and Refresh Triggers (95) remain available to advanced semantic inspection. The principal map intentionally shows six governed completeness aspects rather than every technical collection.

## Governance trace

“Review candidate governance” is linked when Twin identity/scope has not yet been confirmed. Identity recognition comes from package inspection and is independent of review decisions; therefore recognising an Industry Twin and asking for governance is consistent. Candidates are expected under `blueprint_import/staging/<run>/candidates`. The review workflow loads the same staging summary/candidates and joins append-only decisions from `CandidateReviewRepository`. It can now enumerate 1,060 persisted records, including all 641 accepted semantic candidates. An empty governance page in the failing runtime was a consequence of semantic candidate creation never occurring, not evidence that governance had removed candidates.

## Research Gap trace

Research Gap does **not** assume canonical promotion. It receives the same `SemanticTwin` assembled from imported staging candidates. `executive_assessments` then looks for the owner-produced `high_fidelity_completeness_assessment`; when absent, it returns `legacy_unassessed`. `research_requirements` and `research_count_contracts` preserve the non-zero subject inventory but commission missing completeness fields for those subjects.

Consequently, the corrected result is “6 enterprise profiles require enrichment”, “17 participant concepts require enrichment or classification”, “13 programme hypotheses require enrichment”, and “17 opportunity hypotheses require enrichment”—not an empty Twin. The breadth of research remains because owner completeness outputs and required detail are absent or incomplete, not because imported objects are invisible. The prior conclusion that nearly the whole Twin needed research while showing zero subjects was a **projection consequence of the candidate-creation defect**, not a genuine research deficiency.

## Merge recommendation

**MERGE.** The first boundary is evidenced as candidate creation; the reusable manifest declaration mapping is already active; the unchanged TEL-001 package produces visible candidates; governance and projections enumerate the shared staging repository; Research Gaps now retains non-zero runtime inventory; there is no TEL-001-specific importer or logic; and promotion remains explicitly authorised.
