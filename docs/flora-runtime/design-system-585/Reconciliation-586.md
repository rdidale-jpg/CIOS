# PR #586 — individual inherited-failure reconciliation

## Evidence and method

The approved #584 render reference is `19ab36d241dbca2099ffb9b5d519c68c493a914a`; the failing #586 candidate is `297373bc90339c5024ed413fcc46c9fb361641c0`. We executed the same 21 original test identities on the clean reference worktree. **All 21 failed there and matched the approved baseline signatures exactly.** All candidate first failing assertion frames were identical to their original frames. Each exception headline changed because pytest embeds an abbreviated rendered HTML operand: the shared shell inserts the viewport/styles/header and changes the serialized suffix. This was evidence of changed rendering, not proof that every underlying requirement remained valid.

The cases below distinguish layout contracts, research/scenario limits, routing and obsolete authorisation/reasoning fixtures. The original failed expectations were not restored as hidden compatibility text. Each corrected test exercises current meaningful behavior. Semantic HTML parsing ignores styles/scripts/hidden compatibility spans, tolerates quote/class changes, and keeps optional source-disclosure contents addressable.

**No production code, security selection, test identity, comparator, baseline entry or approved skip changed.** The 57 approved inherited-failure records remain byte-identical. The comparator already records a formerly failing test that now passes as `fixed`; it does not need a new exception or a changed signature. No xfail, skip, assertion-message substitution, legacy renderer snapshot or failure whitelist was added. Other tests in the seven edited modules have identical ASTs to the initial candidate. The authenticated import case uses real producer fixtures and is marked as a real security boundary, not synthetic header authority.

The development reproduction passes **21/21**. Final acceptance requires the unchanged full 1,432-identity local and hosted comparison on the corrected committed SHA: expected 1,386 pass / 36 remaining approved failures / 10 unchanged skips, **388/388 strict security pass**, all 21 cases `fixed`, **zero changed_failure_signature/new_failure/unexpected_skip/identity issues**. These are acceptance conditions, not preclaimed full-run results. The PR handoff and linked Actions run identify the final SHA and observed outcomes. No merge/deployment.

The complete machine-readable record, including full original/candidate exception headlines, their SHA-256 signatures, original assertions and per-case decisions, is [Reconciliation-586.json](Reconciliation-586.json). These are bounded presentation assertion headlines from public/synthetic test views, not raw logs, fixture stores, cookies, configuration or credentials.

## Per-case findings

### 01. `test_account_default_opportunities_breadcrumbs_and_evidence_drilldown`

- Test: `tests/test_flora_banking_increment44_executive_navigation.py::test_account_default_opportunities_breadcrumbs_and_evidence_drilldown`
- Classification: **Presentation contract**.
- Original assertion, identical on reference and initial candidate: `assert "data-default-opportunities='3'" in html`
- Baseline/reference headline:

```text
assert "data-default-opportunities='3'" in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Lloyds Banking Group</title><style>\n    body{font-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

- Candidate headline before correction:

```text
assert "data-default-opportunities='3'" in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

The obsolete default-count attribute and Account priorities breadcrumb no longer describe the executive overview. Check the three exact opportunity identities, current heading, evidence destination and explicit missing claim citations.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 02. `test_ai_native_reference_model_collapsed_and_separate`

- Test: `tests/test_flora_banking_increment44_executive_navigation.py::test_ai_native_reference_model_collapsed_and_separate`
- Classification: **Presentation contract**.
- Original assertion, identical on reference and initial candidate: `assert "Explore capability model" in top`
- Baseline/reference headline:

```text
assert 'Explore capability model' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>AI-native UK Banking</title><style>\n    body{font-...hidden>proactive virtual financial advice consents human specialist Vulnerable-customer safeguard</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'Explore capability model' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...hidden>proactive virtual financial advice consents human specialist Vulnerable-customer safeguard</span></body></html>"
```

The landing uses Today versus AI-native and an Explore all 12 capabilities destination. Verify every actual REFERENCE_DOMAINS name on the separate model, rather than counting CSS-dependent cards or expecting the former label.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 03. `test_pestle_only_outlook_not_landing_or_portfolio`

- Test: `tests/test_flora_banking_increment44_executive_navigation.py::test_pestle_only_outlook_not_landing_or_portfolio`
- Classification: **Presentation contract**.
- Original assertion, identical on reference and initial candidate: `assert "UK Banking PESTLE view" in industry_outlook_page()`
- Baseline/reference headline:

```text
assert 'UK Banking PESTLE view' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>UK Banking industry outlook</title><style>\n    bod...h Industry force Management pressure Likely behaviour Required reinvention Commercial opportunity</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'UK Banking PESTLE view' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...h Industry force Management pressure Likely behaviour Required reinvention Commercial opportunity</span></body></html>"
```

The dedicated Banking outlook uses Prioritised industry-force board rather than UK Banking PESTLE view. Check all six actual force records and ensure they are not duplicated on landing/portfolio. Follow the existing landing route to the outlook fragment.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 04. `test_featured_subset_has_full_exploration_route_and_counts_match_projection`

- Test: `tests/test_flora_banking_increment451_visual_correction.py::test_featured_subset_has_full_exploration_route_and_counts_match_projection`
- Classification: **Presentation contract**.
- Original assertion, identical on reference and initial candidate: `assert "Featured intelligence" in html`
- Baseline/reference headline:

```text
assert 'Featured intelligence' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>UK Banking executive landing</title><style>\n    bo... timeline Now 1–2 years 3–5 years 6–10 years Inspectable assumptions</span><span hidden>2–3 years</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'Featured intelligence' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-... timeline Now 1–2 years 3–5 years 6–10 years Inspectable assumptions</span><span hidden>2–3 years</span></body></html>"
```

Use Three featured industry signals, actual signal/Pipeline destinations and their full rendered inventories. Preserve both projection-count comparisons; do not manufacture Featured/Available badges.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 05. `test_ai_native_maturity_journey_renders_as_visual_progression`

- Test: `tests/test_flora_banking_increment45_visual_intelligence.py::test_ai_native_maturity_journey_renders_as_visual_progression`
- Classification: **Presentation/model contract**.
- Original assertion, identical on reference and initial candidate: `assert "AI-native maturity rail" in html`
- Baseline/reference headline:

```text
assert 'AI-native maturity rail' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>AI-native UK Banking</title><style>\n    body{font-...hidden>proactive virtual financial advice consents human specialist Vulnerable-customer safeguard</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'AI-native maturity rail' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...hidden>proactive virtual financial advice consents human specialist Vulnerable-customer safeguard</span></body></html>"
```

The older five-stage rail was already replaced by nine Today/AI-native dimensions. Verify every current dimension and both distinct descriptions, customer/employee journeys, human role, barriers and the capability drill-down. No claim of measured bank maturity is added.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 06. `test_financial_behaviour_narrative_has_required_causal_sections`

- Test: `tests/test_flora_banking_industry_reinvention_increment42.py::test_financial_behaviour_narrative_has_required_causal_sections`
- Classification: **Presentation/research boundary**.
- Original assertion, identical on reference and initial candidate: `assert "What the financial results imply about behaviour" in html`
- Baseline/reference headline:

```text
assert 'What the financial results imply about behaviour' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Lloyds Banking Group</title><style>\n    body{font-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'What the financial results imply about behaviour' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

Use the current financial overview and performance drill-down. Lloyds has four actual causal financial narratives; other banks explicitly disclose missing comparable history. Preserve management-pressure/behaviour/buying-posture model checks; do not fill missing histories.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 07. `test_heatmap_cells_show_pressure_barrier_supplier_and_whitespace`

- Test: `tests/test_flora_banking_industry_reinvention_increment42.py::test_heatmap_cells_show_pressure_barrier_supplier_and_whitespace`
- Classification: **Presentation contract**.
- Original assertion, identical on reference and initial candidate: `assert term in html`
- Baseline/reference headline:

```text
assert 'Supplier:' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Compare UK banks</title><style>\n    body{font-fami...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'Supplier:' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

Six-mode comparison replaces verbose cells. Follow every bank opportunity and verify its actual barrier, supplier-landscape/whitespace/next-action headings and underlying values. Commercial detail remains tested rather than adding obsolete labels to the UI.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 08. `test_industry_opportunity_totals_reconcile_to_account_opportunities`

- Test: `tests/test_flora_banking_industry_reinvention_increment42.py::test_industry_opportunity_totals_reconcile_to_account_opportunities`
- Classification: **Scenario/Pipeline boundary**.
- Original assertion, identical on reference and initial candidate: `assert f"Flora working estimate £{portfolio_mid}m" in html or f"Flora working estimate: £{portfolio_mid}m" in html`
- Baseline/reference headline:

```text
assert ('Flora working estimate £910m' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Compare UK banks</title><style>\n    body{font-fami...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>" or 'Flora working estimate: £910m' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Compare UK banks</title><style>\n    body{font-fami...ailable Opportunity-value summary not a win probability</s...
```

- Candidate headline before correction:

```text
assert ('Flora working estimate £910m' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>" or 'Flora working estimate: £910m' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...ailable Opportunity-value summary not a win probability</s...
```

A gross £910m working-pipeline claim is not the current contract. Verify all bank sums and £910m arithmetic, plus overlapping/unverified scenario and non-qualified/non-customer-budget disclosures. No Pipeline writes or valuation changes.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 09. `test_pestle_forces_map_to_specific_banks_themes_and_non_generic_outputs`

- Test: `tests/test_flora_banking_industry_reinvention_increment42.py::test_pestle_forces_map_to_specific_banks_themes_and_non_generic_outputs`
- Classification: **Presentation/research boundary**.
- Original assertion, identical on reference and initial candidate: `assert category in html`
- Baseline/reference headline:

```text
assert 'Political' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Compare UK banks</title><style>\n    body{font-fami...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'Political' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

PESTLE forces belong to the dedicated outlook, reached through Banking, rather than repeated in comparison. Verify all category/force/bank records there and the explicit limit that industry relevance is not a qualified enterprise pressure.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 10. `test_rendered_acceptance_artefacts_exist`

- Test: `tests/test_flora_banking_industry_reinvention_increment42.py::test_rendered_acceptance_artefacts_exist`
- Classification: **Presentation contract**.
- Original assertion, identical on reference and initial candidate: `assert artefact in industry`
- Baseline/reference headline:

```text
assert 'UK Banking PESTLE view' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Compare UK banks</title><style>\n    body{font-fami...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'UK Banking PESTLE view' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

Replace the obsolete single-page artefact checklist with the actual Banking, comparison, outlook, competitors and per-opportunity journey. Check all bank names in the accessible heatmap table, scenario-method section, and Lloyds barriers/whitespace.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 11. `test_supplier_names_render_and_unnamed_labels_are_suppressed_when_names_exist`

- Test: `tests/test_flora_banking_industry_reinvention_increment42.py::test_supplier_names_render_and_unnamed_labels_are_suppressed_when_names_exist`
- Classification: **Supplier evidence boundary**.
- Original assertion, identical on reference and initial candidate: `assert "Google Cloud" in html`
- Baseline/reference headline:

```text
assert 'Google Cloud' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Compare UK banks</title><style>\n    body{font-fami...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'Google Cloud' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

Named suppliers are in account-specific opportunity detail, not all comparison cells. Check every actual supplier name, rationale and inference basis there, require Unknown for empty supplier sets and preserve Google Cloud/Microsoft coverage. No contract ownership is inferred.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 12. `test_analyst_views_preserve_attribution_without_fake_consensus`

- Test: `tests/test_flora_banking_portfolio_increment3.py::test_analyst_views_preserve_attribution_without_fake_consensus`
- Classification: **Presentation/provenance contract**.
- Original assertion, identical on reference and initial candidate: `assert "What analysts broadly like" in html`
- Baseline/reference headline:

```text
assert 'What analysts broadly like' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Lloyds Banking Group</title><style>\n    body{font-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'What analysts broadly like' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

Analyst detail has its own route and current headings. Check every positive/concern statement and each source via the evidence route, with generic-citation limits and no consensus claim. Old overview subheadings and attribution slogan are not evidence.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 13. `test_each_bank_page_uses_executive_structure_and_preserves_inspection`

- Test: `tests/test_flora_banking_portfolio_increment3.py::test_each_bank_page_uses_executive_structure_and_preserves_inspection`
- Classification: **Presentation contract**.
- Original assertion, identical on reference and initial candidate: `assert section in html`
- Baseline/reference headline:

```text
assert '1. Account in one minute' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Lloyds Banking Group</title><style>\n    body{font-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

- Candidate headline before correction:

```text
assert '1. Account in one minute' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

The numbered thirteen-section brief is obsolete. Check current executive sections, real top-three opportunity routes/titles, actual snapshot date and inspection/source limits for all five banks. Unknown bank now correctly returns 404; do not turn absence into a 200 account.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 14. `test_increment_41_pipeline_reconciliation_horizons_and_value_meaning`

- Test: `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_pipeline_reconciliation_horizons_and_value_meaning`
- Classification: **Scenario/Pipeline boundary**.
- Original assertion, identical on reference and initial candidate: `assert "What the financial results are telling us" in html`
- Baseline/reference headline:

```text
assert 'What the financial results are telling us' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Lloyds Banking Group</title><style>\n    body{font-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'What the financial results are telling us' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

Retain low/high/midpoint arithmetic and every timing/supplier model check. Validate actual account rollups, non-qualified wording, financial drill-down and explicit unknown procurement/customer milestones for each opportunity instead of invented qualified/CRM totals.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 15. `test_increment_41_portfolio_cards_and_heatmap_are_scannable_with_expansion`

- Test: `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_portfolio_cards_and_heatmap_are_scannable_with_expansion`
- Classification: **Presentation/scenario contract**.
- Original assertion, identical on reference and initial candidate: `assert text in html`
- Baseline/reference headline:

```text
assert 'Near-term pipeline' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>UK Banking account priorities</title><style>\n    b...Settings</a></nav><p>Destination permissions apply. These links do not grant access.</p></details></div></body></html>"
```

- Candidate headline before correction:

```text
assert 'Near-term pipeline' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...'/flora/banking/santander-uk'>Open bank scenario overview</a></article></section></details></main></div></body></html>"
```

Near-term pipeline and expansion boilerplate were obsolete before #585. Check five linked accounts, every retained scenario title/range, accessible bank comparison table and on-demand sizing assumptions/non-qualified limits.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 16. `test_increment_41_supplier_traction_is_sourced_or_human_labelled_and_unknown_is_bounded`

- Test: `tests/test_flora_banking_portfolio_increment3.py::test_increment_41_supplier_traction_is_sourced_or_human_labelled_and_unknown_is_bounded`
- Classification: **Supplier evidence boundary**.
- Original assertion, identical on reference and initial candidate: `assert "No reliable view" in html`
- Baseline/reference headline:

```text
assert 'No reliable view' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Santander UK</title><style>\n    body{font-family:I... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'No reliable view' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

Keep all supplier date/rationale/basis/traction validations. Follow Santander opportunity details: two have no reliable view, while its platform case has an explicitly inferred group supplier. Verify both branches rather than falsely declaring all Santander suppliers Unknown.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 17. `test_opportunities_have_values_feedback_and_preserve_originals`

- Test: `tests/test_flora_banking_portfolio_increment3.py::test_opportunities_have_values_feedback_and_preserve_originals`
- Classification: **Read-only workflow contract**.
- Original assertion, identical on reference and initial candidate: `assert action in html`
- Baseline/reference headline:

```text
assert 'Useful' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Lloyds Banking Group</title><style>\n    body{font-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'Useful' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-... commercial scope → opportunity title</span><span hidden>Independently derived title?</strong> No</span></body></html>"
```

The old unconnected feedback buttons were already absent; they must not masquerade as capture. Preserve every estimate/assumption check, actual opportunity details and unknown budget, verify the read-only component has no form/buttons, retain its vocabulary and compare original pipeline objects before/after rendering.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 18. `test_theme_relevance_ranking_and_pipeline_are_deterministic`

- Test: `tests/test_flora_banking_portfolio_increment3.py::test_theme_relevance_ranking_and_pipeline_are_deterministic`
- Classification: **Presentation/scenario contract**.
- Original assertion, identical on reference and initial candidate: `assert theme in first`
- Baseline/reference headline:

```text
assert 'Customer experience transformation' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Compare UK banks</title><style>\n    body{font-fami...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

- Candidate headline before correction:

```text
assert 'Customer experience transformation' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...ailable Opportunity-value summary not a win probability</span><span hidden>Flora working estimate</span></body></html>"
```

Theme cells live in the dedicated heatmap; the six-mode comparison is a summary. Verify deterministic output, every mode, every actual theme and linked bank, monetary/non-monetary distinction and unqualified scenario limits.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 19. `test_digital_twins_home_uses_governed_registry_and_import_breadcrumbs`

- Test: `tests/test_flora_enterprise_canvas.py::test_digital_twins_home_uses_governed_registry_and_import_breadcrumbs`
- Classification: **Routing and acceptance fixture**.
- Original assertion, identical on reference and initial candidate: `assert "href='/digital-twins/MOD'>Open Twin" in home`
- Baseline/reference headline:

```text
assert "href='/digital-twins/MOD'>Open Twin" in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Digital Twins</title><style>\n    body{font-family:...Settings</a></nav><p>Destination permissions apply. These links do not grant access.</p></details></div></body></html>"
```

- Candidate headline before correction:

```text
assert "href='/digital-twins/MOD'>Open Twin" in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...canvas'>Open Enterprise Canvas / Commercial Digital Twin view</a></article></div></section></main></div></body></html>"
```

Current discovery uses canonical lower-case /digital-twins/mod/canvas and import history, not the obsolete Open Twin label/uppercase URL. Verify history/validation references, registry uniqueness, correct Enterprise population and read-only file hashes. The fixture has candidate-only intelligence, not accepted assurance: assert actual version and candidate-only status, plus the unavailable reasoning guard. No automatic acceptance or grant is introduced.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 20. `test_mod_executive_commercial_canvas_read_model`

- Test: `tests/test_flora_enterprise_canvas.py::test_mod_executive_commercial_canvas_read_model`
- Classification: **Reasoning fixture / research boundary**.
- Original assertion, identical on reference and initial candidate: `assert "executive situation briefing" in html`
- Baseline/reference headline:

```text
assert 'executive situation briefing' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Enterprise Canvas — MOD</title><style>\n    body{fo...Settings</a></nav><p>Destination permissions apply. These links do not grant access.</p></details></div></body></html>"
```

- Candidate headline before correction:

```text
assert 'executive situation briefing' in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...d source lineage. Select any Model Explorer area to inspect detailed lineage.</p></section></main></div></body></html>"
```

No validated reasoning result exists in this fixture. First verify the default view says Brief unavailable and does not expose an executive success briefing. Then exercise the existing diagnostic read-model projection explicitly with include_reasoning=False/force_overview=True, preserving all original commercial/lineage/Unknown/contradiction/no-mutation assertions. No provider-success gate is patched and no paid model is called.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

### 21. `test_deployed_equivalent_pilot_route_imports_candidate_to_executive_workspace`

- Test: `tests/test_flora_pilot_import_bypass.py::test_deployed_equivalent_pilot_route_imports_candidate_to_executive_workspace`
- Classification: **Authentication fixture / security**.
- Original assertion, identical on reference and initial candidate: `assert status == 200 and "href='/blueprint-import'>Import Twin" in landing`
- Baseline/reference headline:

```text
assert (200 == 200 and "href='/blueprint-import'>Import Twin" in "<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Digital Twins</title><style>\n    body{font-family:...t.executive_workspace.executive_workspace_page | executive_twin_implementation=executive-twin-map-v4 --></body></html>")
```

- Candidate headline before correction:

```text
assert (200 == 200 and "href='/blueprint-import'>Import Twin" in "<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-...t.executive_workspace.executive_workspace_page | executive_twin_implementation=executive-twin-map-v4 --></body></html>")
```

The original fixture assumed ambient pilot-mode authorisation, retired before #585. Use existing real offline enrollment/session/workspace/CSRF fixtures. Verify public import-authorisation landing grants no upload, anonymous POST is denied without writes, verified human stages candidate records only with correct workspace/actor, no canonical Model/Observation promotion, and revoked membership denies the staged receipt. Legacy flags remain powerless; no production guard is changed.

**Development result: PASS.** No new failure signature is accepted; this identity must be reported fixed by the unchanged full gate.

## Reproduction and review boundary

1. Read the 21 identities from `Reconciliation-586.json` and run those exact identities on a detached `19ab36d241dbca2099ffb9b5d519c68c493a914a` worktree with the repository dependencies and a separate temporary data/test directory. Its 21 failure fingerprints must equal the unchanged baseline records.
2. Compare the recorded initial `297373bc90339c5024ed413fcc46c9fb361641c0` full-gate evidence: same assertion frames, different abbreviated HTML exception headlines, no extra missing identities.
3. Run the 21 identities on the corrected branch: each must pass. Run `python tools/ci/flora_ci.py --output /tmp/flora-586-final` on a clean, committed checkout. The baseline and comparator bytes stay fixed; remaining failures/skips must match normally.
4. Run the 238-case UI/Offers/Pipeline selection documented in [Validation.md](Validation.md), plus `python -m unittest discover -s tests/ci -v`. GitHub's complete validation workflow must succeed on the exact candidate or its identical-tree test merge. Physical-device acceptance and #578 release readiness remain separate.

Existing 108 previews and 692 browser checks remain applicable because reconciliation changes test contracts/fixtures and documentation only; no renderer, stylesheet, image, model, source record, matcher, permission handler or Pipeline writer changes. No new illustration, research, employer setup, paid provider call or deployment is performed.
