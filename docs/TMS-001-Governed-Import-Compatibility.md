# WP1-004 — TMS-001 governed import compatibility assessment

## Assessment and owner decision

The authoritative fixture is `enterprise-knowledge/TMS-001_High_Fidelity_Industry_Twin_Upgrade.zip` (SHA-256 `25e8ef0f49b4320e3fff2b347b06708ed231a670b5497a7402abf7ca26380371`). It has one wrapper root, a governed `00_manifest.json`, 47 declared members with byte counts and SHA-256 hashes, and `21_industry_twin_delta_for_flora.json`. The source ZIP is preserved unchanged.

The package is supportable without weakening governance. Its Delta is a projection of stable identifiers rather than the generic inline/`primary_objects` shape already understood by Flora. The smallest owner-aligned correction is therefore an adapter-side TMS inventory projection, not an importer redesign or package rewrite. Flora continues to own receipt, archive, inspection, staging, review, reconciliation and explicit promotion. IT-001/TMS-001 retains release meaning, including the package's **Research-ready with conditions** and **not promotion-ready** declarations; import compatibility does not elevate either status.

## Artefact classification

Every ZIP member is persisted in `package_inspection.artefact_classification`; the following rules give the canonical owner and treatment for every class.

| Class | Package artefacts | Canonical owner | Import treatment |
|---|---|---|---|
| Promotable canonical candidate | HFT object, fact, relationship and uncertainty inventories; source evidence register; reasoning lineage; Flora Delta | Enterprise Intelligence authorities | Project stable-ID records only, validate relationship endpoints, stage and require review/approval. The Delta itself controls projection but is not duplicated as a canonical object. |
| Supporting evidence or lineage | Source/evidence registers | Evidence authority | Stage individual evidence records with package checksum and source-file lineage. |
| Derived decision or presentation output | Executive intelligence/briefs, ranked opportunities, AI/maturity/completeness products, navigation index, mission summaries and README material | Producing decision/presentation authority | Retain in immutable package lineage; exclude from canonical staging to avoid duplicate objects and status elevation. |
| Mission or workspace state | Final/HFT workspaces, restart state, checkpoints and research queue disposition | Research mission/workspace authority | Retain unchanged; never promote. |
| Release assurance or validation evidence | Manifests, baseline manifest, validation, assurance, deficiency and assessment summaries | IT-001 controlled release schedules and package authority | Validate identity/declarations/checksums and retain for audit; never treat assurance as canonical intelligence. |
| Unsupported or ambiguous | Baseline domain models, final twin products, analyst/news/capability/historical inventories, final unknown/contradiction/evidence duplicates, and other content not named by the canonical HFT projection | Respective Enterprise Intelligence or presentation owner | Retain and explicitly classify; do not infer or silently map. A future canonical-owner contract may add an unambiguous projection. |

## Compatibility findings

* **Package construction:** valid archive and internally consistent declared byte counts/checksums; no rewrite required.
* **Manifest declaration:** identity is expressed as `mission_id`/`id`, and declared members use `filename`; existing governed identity precedence resolves `TMS-001`. Flora now verifies every declared file, byte count and checksum at validation.
* **Industry Twin Delta projection:** the exact incompatibility was identifier lists named `new_twins`, `new_relationships`, `new_unknowns`, `new_contradictions` and `evidence_references`, rather than generic inline records. The adapter now resolves the canonical HFT inventories explicitly and refuses missing inventories or relationship endpoints.
* **Adapter mapping:** canonical objects map to `entity` while preserving their `object_type`; facts remain governed `fact` records rather than being silently coerced into observations; sources map to evidence; uncertainty maps to Unknowns and Contradictions; the reasoning document maps to governed lineage.
* **Staging constructors:** `fact` and `reasoning_lineage` use the existing generic stable-ID canonical store. EI-012 is the canonical owner of Contradiction semantics and requires contradictory Observations to coexist until resolved. Each TMS record supplies only one cautionary `statement`, so it is preserved in staging as an explicitly `structurally_incomplete_contradiction`, with its ID, evidence references, affected-object links, open status, confidence/freshness and checkpoint/decision lineage intact. It is quarantined from promotion: Flora neither invents a second position nor converts it into an ordinary summary assertion. Owner-approved competing positions or another accepted EI-012 representation are required before promotion.
* **Flora runtime:** no parallel lifecycle is required. Existing authenticated receipt, candidate review, dry-run reconciliation, approval, atomic promotion, repositories and completion/Explore projection are used.

## Reasoning-lineage projection contract

The package's `reasoning_lineage.json` is one governed **lineage-relationship candidate**, not a generic replacement for its stage objects. Its `LINEAGE-TMS-001-HFT` stable ID and the stable IDs, typed arrays and endpoint fields nested below it round-trip unchanged. Reconciliation is by that document ID and package fingerprint; repeat import is unchanged. Promotion accepts the lineage relationship/document only. It does not independently accept the embedded reasoning claims, elevate package status, or flatten stage distinctions.

| Supported stage | Canonical owner | Candidate type and stable-ID treatment | Reconciliation and promotion | Unsupported/ambiguous handling |
|---|---|---|---|---|
| Source | EI-013 Knowledge Asset/Evidence authority | Independently staged `evidence` source candidates from the source register; source IDs are unchanged. The lineage document also retains its `sources` references. | Reconcile by source/evidence ID; approved source candidates promote through Evidence storage. | Unresolved IDs fail projection; source-like material outside the declared register remains package lineage. |
| Evidence | EI-012 Evidence/Observation model and Evidence authority | `evidence` candidates retain `E-*` IDs; `facts` remain distinct `fact` candidates. | Reconcile by stable ID; promote only reviewed candidates. | Ambiguous evidence elsewhere is retained, classified and not inferred. |
| Observation | EI-012 | Typed `observations` remain embedded in the `reasoning_lineage` candidate with each `OBS-*` ID and source endpoints unchanged. | Reconciled as part of the lineage document; **not** promoted as canonical Observations because this package projection does not satisfy the independent Observation constructor/acceptance contract. | Missing/ambiguous stage records remain package lineage and cannot acquire Observation authority. |
| Strategic Signal | EI-004 commercial reasoning authority | Typed `strategic_signals` remain embedded, preserving `SIG-*` IDs and `observation_ids`. | Lineage-document reconciliation only; no independent canonical promotion. | Retain without promotion until an owning candidate contract exists. |
| Hypothesis | EI-004 | Typed `hypotheses` remain embedded, preserving `HYP-*` IDs and `strategic_signal_ids`. | Lineage-document reconciliation only; no independent canonical promotion. | Retain without promotion; never coerce to Observation or Signal. |
| Commercial Thesis | EI-004 | Typed `commercial_theses` remain embedded, preserving thesis IDs and `hypothesis_ids`. | Lineage-document reconciliation only; no independent canonical promotion. | Retain without promotion; no status inference. |
| Recommendation | EI-004 and the owning decision/approval authority | Typed `recommendations` remain embedded, preserving recommendation IDs, `commercial_thesis_ids`, uncertainty and status. | Lineage-document reconciliation only; no independent Recommendation promotion or approval. | Retain without promotion; package acceptance is not Recommendation approval. |
| Lineage relationship | EI-002 Knowledge Graph / EI-013 exchange lineage | One `reasoning_lineage` candidate with stable ID `LINEAGE-TMS-001-HFT`; `chain_model`, typed collections and endpoints are preserved verbatim. | Reconcile by stable ID and content fingerprint; reviewed document may promote to the generic lineage store without changing any participating object's authority. | Missing inventories/endpoints fail; ambiguous additional lineage is retained in immutable package lineage. |

## Import-result evidence

| Result | Proven value |
|---|---:|
| Staged | **315** |
| Quarantined | **14** structurally incomplete Contradictions |
| Rejected | **0** |
| Promoted | **301** |
| Candidate classes | entity 59; fact 63; evidence 56; relationship 102; unknown 20; contradiction 14; reasoning_lineage 1 |
| Excluded-lineage artefacts | **40** of 48 archive members (the eight projection/control inputs are the Delta plus seven declared HFT inventories/registers) |
| Relationship endpoints | **204/204 resolved**, 0 unresolved |
| Repeat import/execution | `repeat_no_change`; zero additional writes |
| Failed-promotion rollback | `restored_canonical_file_backups`; the atomic-failure test proves no partial canonical files survive |
| Post-promotion Explore/read | Completion renders **Explore promoted Twin** and reports 301 created records; stable object, evidence, Unknown and reasoning-lineage IDs read back from canonical stores |

The unsupported-content list is explicit: `01`–`15` baseline/final domain, executive, opportunity, AI and assessment products; duplicate final registers `16`–`18`; research disposition/restart/readme/mission summaries `19`, `20`, and `22`; the baseline manifest; HFT deficiency and assessment summaries; Executive briefs/summaries; Flora navigation output; `analyst_intelligence.json`, `assurance_inventory.json`, `capabilities_offers.json`, `historical_states.json`, and `news_intelligence.json`; validation output; both Research Workspace/checkpoint files; the final workspace; and the HFT upgrade README. The governed manifest is validation/audit evidence rather than canonical intelligence. All remain immutable package lineage and none is silently mapped.

The 14 contradiction records are included in staged and class counts but excluded from promoted count. Their statements, evidence references, affected objects, unresolved state, confidence/freshness, checkpoints and resulting decision constraint remain inspectable; their quarantine is itself the promotion decision impact.

## Baseline full-suite failures

`pytest -q` on this branch produced **70 failed, 888 passed, 2 skipped**. The same command in a detached worktree at merge base `76d7f47` produced **72 failed, 885 passed, 2 skipped**. Every current failure reproduced at the merge base; the merge base additionally failed `tests/test_commercial_signal_architecture.py::test_bt_enterprise_profile_financial_pestle_and_sufficiency_render` and `tests/test_flora.py::test_text_only_preview_bundle_is_generated_without_binaries`. Therefore none of the current full-suite failures is introduced by WP1-004.

Exact current failures:

- `tests/knowledge_packs/test_chief_architect_pack.py::test_manifest_completeness_sources_and_shared_authorities`
- `tests/knowledge_packs/test_chief_architect_pack.py::test_deterministic_build_zip_checksum_index_pack_state_and_completeness_matrix`
- `tests/test_bt_structured_ingestion.py::test_bt_structured_ingestion_creates_evidence_observations_model_and_is_idempotent`
- `tests/test_dual_speed_financial_intelligence_orchestration.py::test_dual_speed_fixture_is_not_default`
- `tests/test_dual_speed_financial_intelligence_orchestration.py::test_unsupported_mode_still_rejected`
- `tests/test_dual_speed_financial_intelligence_orchestration.py::test_default_structured_mode_does_not_invoke_rapid_acquisition`
- `tests/test_flora_ai_financial_report_review.py::test_financial_intelligence_records_source_retrieval_failure`
- `tests/test_flora_ai_financial_report_review.py::test_financial_intelligence_records_provider_not_configured`
- `tests/test_flora_ai_financial_report_review.py::test_financial_intelligence_refresh_creates_missing_nested_directories`
- `tests/test_flora_ai_financial_report_review.py::test_financial_intelligence_persistence_failure_is_not_provider_failure`
- `tests/test_flora_ai_financial_report_review.py::test_provider_request_failures_remain_classified`
- `tests/test_flora_ai_financial_report_review.py::test_provider_timeout_is_distinct_and_records_safe_diagnostic`
- `tests/test_flora_ai_financial_report_review.py::test_section_packet_diagnostics_page_reasons_and_partial_success`
- `tests/test_flora_banking_increment44_executive_navigation.py::test_landing_budget_conclusion_and_signals`
- `tests/test_flora_banking_increment44_executive_navigation.py::test_pestle_only_outlook_not_landing_or_portfolio`
- `tests/test_flora_banking_increment44_executive_navigation.py::test_ai_native_reference_model_collapsed_and_separate`
- `tests/test_flora_banking_increment44_executive_navigation.py::test_account_default_opportunities_breadcrumbs_and_evidence_drilldown`
- `tests/test_flora_banking_increment451_visual_correction.py::test_featured_subset_has_full_exploration_route_and_counts_match_projection`
- `tests/test_flora_banking_increment45_visual_intelligence.py::test_ai_native_maturity_journey_renders_as_visual_progression`
- `tests/test_flora_banking_industry_reinvention_increment42.py::test_financial_behaviour_narrative_has_required_causal_sections`
- `tests/test_flora_banking_industry_reinvention_increment42.py::test_pestle_forces_map_to_specific_banks_themes_and_non_generic_outputs`
- `tests/test_flora_banking_industry_reinvention_increment42.py::test_supplier_names_render_and_unnamed_labels_are_suppressed_when_names_exist`
- `tests/test_flora_banking_industry_reinvention_increment42.py::test_heatmap_cells_show_pressure_barrier_supplier_and_whitespace`
- `tests/test_flora_banking_industry_reinvention_increment42.py::test_industry_opportunity_totals_reconcile_to_account_opportunities`
- `tests/test_flora_banking_industry_reinvention_increment42.py::test_rendered_acceptance_artefacts_exist`
- `tests/test_flora_banking_portfolio_increment3.py::test_each_bank_page_uses_executive_structure_and_preserves_inspection`
- `tests/test_flora_banking_portfolio_increment3.py::test_analyst_views_preserve_attribution_without_fake_consensus`
- `tests/test_flora_banking_portfolio_increment3.py::test_theme_relevance_ranking_and_pipeline_are_deterministic`
- `tests/test_flora_banking_portfolio_increment3.py::test_opportunities_have_values_feedback_and_preserve_originals`
- `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_pipeline_reconciliation_horizons_and_value_meaning`
- `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_supplier_traction_is_sourced_or_human_labelled_and_unknown_is_bounded`
- `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_portfolio_cards_and_heatmap_are_scannable_with_expansion`
- `tests/test_flora_deterministic_financial_refresh.py::test_standard_refresh_fails_closed_without_ai_fallback`
- `tests/test_flora_deterministic_financial_refresh.py::test_route_level_golden_persists_evidence_and_idempotent`
- `tests/test_flora_deterministic_financial_refresh.py::test_structured_standard_refresh_uses_structured_adapter_and_no_fallback`
- `tests/test_flora_deterministic_financial_refresh.py::test_structured_missing_source_preserves_existing_trusted_state`
- `tests/test_flora_deterministic_financial_refresh.py::test_structured_missing_source_marks_fresh_ephemeral_absence`
- `tests/test_flora_enterprise_canvas.py::test_digital_twins_home_uses_governed_registry_and_import_breadcrumbs`
- `tests/test_flora_enterprise_canvas.py::test_mod_executive_commercial_canvas_read_model`
- `tests/test_flora_financial_fact_capture_v2.py::test_route_level_golden_deterministic_refresh_second_refresh_zero_openai`
- `tests/test_flora_increment46_product_coherence.py::test_banking_landing_links_outlook_and_separates_featured_from_all_signals`
- `tests/test_flora_increment46_product_coherence.py::test_outlook_has_visual_narrative_pestle_and_actionable_conclusions`
- `tests/test_flora_increment46_product_coherence.py::test_ai_native_vision_branch_tension_and_distinct_pages`
- `tests/test_flora_increment46_product_coherence.py::test_major_visuals_have_before_and_after_explanation`
- `tests/test_flora_increment46_product_coherence.py::test_comparison_narrative_and_opportunity_value_mode`
- `tests/test_flora_increment47_enterprise_depth.py::test_ai_native_vision_and_capability_drilldown`
- `tests/test_flora_increment47_enterprise_depth.py::test_timeline_separates_industry_timing_from_pipeline_visual`
- `tests/test_flora_increment47_enterprise_depth.py::test_visual_guidance_and_bank_links`
- `tests/test_flora_increment47_enterprise_depth.py::test_enterprise_tab_structure_for_each_bank`
- `tests/test_flora_increment47_enterprise_depth.py::test_financial_history_does_not_fabricate_missing_values`
- `tests/test_flora_increment47_enterprise_depth.py::test_market_and_analyst_views_separate_fact_from_interpretation`
- `tests/test_flora_live.py::test_morning_edition_live_and_fallback_banner`
- `tests/test_flora_live.py::test_repeated_collection_does_not_increase_evidence_count`
- `tests/test_flora_live.py::test_current_status_reports_unique_evidence_objects`
- `tests/test_flora_live.py::test_morning_edition_coverage_summary`
- `tests/test_flora_live.py::test_flora_v07_sources_page_and_morning_summary`
- `tests/test_flora_live.py::test_flora_v08_portfolio_radar_and_source_effectiveness`
- `tests/test_flora_live.py::test_bt_profile_run_manifest_identity_counts_and_memory_chain`
- `tests/test_flora_live.py::test_rejected_claims_link_and_route_states`
- `tests/test_flora_live.py::test_live_collection_persists_factual_diagnostics_and_digital_twin`
- `tests/test_flora_web.py::test_root_renders_morning_edition_content`
- `tests/test_flora_web.py::test_live_status_returns_json`
- `tests/test_flora_web.py::test_live_evidence_empty_state`
- `tests/test_flora_web.py::test_homepage_morning_edition_live_banner`
- `tests/test_flora_web.py::test_watchlist_links_to_score_pages`
- `tests/test_flora_web.py::test_root_renders_flora_v2_home`
- `tests/test_flora_web.py::test_flora_v2_navigation_routes_work`
- `tests/test_flora_web.py::test_home_accessibility_basics`
- `tests/test_mod_twin_spine_mapping.py::test_v12_core_mapping_contract_and_review_summary`
- `tests/test_mod_twin_spine_mapping.py::test_v13_proven_mod_header_shapes_and_safety`

## Recommendation

**Merge.** The real repository package now traverses the existing governed lifecycle with evidence, Unknowns and typed reasoning lineage preserved; structurally incomplete Contradictions remain quarantined and inspectable, while derived/workspace/ambiguous content remains retained but non-promotable and Research-ready status is not promoted into Accepted or Architecture-ready status.
