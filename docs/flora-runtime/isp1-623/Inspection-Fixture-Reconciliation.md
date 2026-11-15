# Inspection-fixture compatibility reconciliation

The first full run on29ef8ab found29 new failures, all caused by historical anonymous-public expectations for the commissioned research inspection routes. There were **zero changed inherited-failure signatures**. The strict388 security tests passed. No comparator, security test or inherited failure/skip inventory was changed.

Each case below retains its original test ID and its source, content, relationship, counter-evidence, fragment or Pipeline assertions. Positive inspection requests now use a real authenticated owner fixture; anonymous requests are explicitly denied where applicable. Original public core/other-sector and private-Pipeline denial assertions remain. This is a route-authority expectation correction, not a source/semantic-baseline refresh.

| Suite | Original case | Correction |
|---|---|---|
| aviation_twin | `test_industry_home_navigation_reaches_easyjet_and_existing_banking` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| commercial_assessment | `test_public_shortlist_and_customer_briefs_are_navigable` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| multi_industry_integration | `test_complete_sector_to_evidence_to_confirmed_pipeline_journey[banking-lloyds-RCO-LBG-002]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| multi_industry_integration | `test_every_sector_uses_all_six_shared_templates_and_retains_score_dimensions` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| primary_enrichment | `test_public_views_expose_updated_provenance_comparison_and_full_original_limit` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| unified_experience | `test_canonical_home_industry_enterprise_opportunity_journey` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| unified_experience | `test_legacy_entry_urls_retain_supporting_content_and_canonical_destinations` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| unified_experience | `test_primary_navigation_is_consistent_and_specialist_tools_are_contextual` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| research_diagnostic | `test_diagnostic_available_for_exact_registered_enterprises_only` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| research_cycle | `test_existing_diagnostic_route_renders_research_cycle_and_evidence_links[lloyds]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| enterprise_understanding | `test_finite_public_understanding_route_and_navigation[lloyds]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| visual_intelligence | `test_all_flagship_pages_and_ai_lens_keep_canonical_navigation[banking-lloyds]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| visual_intelligence | `test_every_family_reaches_actual_evidence_and_resolvable_fragment[banking-lloyds]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| visual_intelligence | `test_original_six_spec_api_and_explicit_lenses_are_preserved` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| living_industry_maps | `test_ai_and_regulation_are_exposure_mappings_with_real_timeline_links_only[banking]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| living_industry_maps | `test_each_layer_uses_one_map_and_contextual_inspection_with_original_routes[ai-disruption-banking]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| living_industry_maps | `test_each_layer_uses_one_map_and_contextual_inspection_with_original_routes[overview-banking]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| living_industry_maps | `test_each_layer_uses_one_map_and_contextual_inspection_with_original_routes[regulation-banking]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| living_industry_maps | `test_every_major_activity_has_meaningful_scoped_content_and_evidence_link[banking]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| commercial_visual_v3 | `test_core_platform_counterevidence_keeps_exact_source_scope_and_lineage` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| commercial_visual_v3 | `test_exploration_never_reads_or_creates_private_pipeline_records` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| commercial_visual_v3 | `test_public_commercial_routes_and_other_lenses_remain_available[banking-lloyds]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| commercial_usability_v31 | `test_public_summary_does_not_lookup_private_records` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| intelligence_depth | `test_public_depth_inspection_never_creates_or_reads_private_pipeline` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| enterprise_opportunity | `test_priority_route_has_one_principal_dossier_and_visible_controlled_capture[RCO-LBG-001]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| enterprise_opportunity | `test_priority_route_has_one_principal_dossier_and_visible_controlled_capture[RCO-LBG-002]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| enterprise_opportunity | `test_priority_route_has_one_principal_dossier_and_visible_controlled_capture[RCO-LBG-009]` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| unified_integration_v1 | `test_cyber_reuses_one_visual_story_cockpit_and_deliberate_full_evidence` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |
| unified_integration_v1 | `test_integrated_public_journey_cannot_enumerate_or_modify_private_pipeline` | Existing verified-owner read; retain original content/lineage/control assertions and anonymous denial. |

The new owner HTTP fixture uses the existing real SecurityStore fixture and opaque session cookie. It performs no per-route elevation, no trusted-header bypass and no production access. Authenticated owner context may legitimately show its own workspace identity; this is distinct from exposing a private Pipeline record. Existing write and qualification services remain unchanged.

Two older whole-file owner pin tests separately verify the single explicit security_web revision in Owner-Compatibility.json, retaining all other historical owner protections. The newer VEX/ISP presentation assertions verify the owner-approved omission policy, not hidden research placeholders.

Corrected affected specialist suites:227passed locally. Final full local and hosted results for the corrected exact commit are recorded in the PR validation comment; the exploratory failing run is not acceptance evidence.

For the principal-dossier capture cases, the former anonymous no-form view is now denied403. The authenticated owner view must retain the existing CSRF-bearing POST capture form; the test continues to verify its dossier structure and deliberate hand-off boundary. No capture/qualification service or write authorisation changed.
