# Public Route Classification Matrix — PR 539 closure

The catalogue below is exhaustive: 127 exact paths. There are no public prefix
exemptions. New source records require explicit catalogue registration and review.
Every row is exercised against its actual HTTP handler with protected Evidence,
Enterprise Model, package registry and Canvas access reads replaced by failure
sentinels. Synthetic private records, including an Evidence ID collision, remain
undisclosed. Canonical and imported-store hashes remain unchanged.

All rows have the same access boundary: anonymous source presentation only;
path identifiers select only the named repository source catalogue, never a
workspace/account record. Listed query keys filter source scenarios or presentation;
unknown keys, duplicate keys and malformed encodings are rejected before dispatch.
No query value establishes authority. Downstream discovery filters protected owners
before rendering; protected service entry points independently require a verified
context. There is no downstream private service on the source-only rows.

| Exact path | Exact handler | Data source / public justification | Accepted query keys |
| --- | --- | --- | --- |
| `/` | `_flora_home_page` | Repository Banking pipeline; private discovery short-circuits without authority | None |
| `/ask` | `_flora_question_page` | Bounded public Banking question or escaped unavailable response | question |
| `/blueprint-import` | `import_blueprint_entry_page` | Public closed setup; no protected registry enumeration | None |
| `/deployment` | `deployment_payload` | Allowlisted public code fingerprint only | None |
| `/digital-twins` | `digital_twins_landing_page` | Public source discovery shell; protected owners remain filtered | None |
| `/evidence/BK-CMP-002` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-ENT-001` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-ENT-003` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-FLR-001` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-FLR-SSN-SPEC-001` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-GOV-SSN-VAL-001` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-IND-001` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-IND-002` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-INF-001` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-OBS-014` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-OBS-015` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-OBS-016` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-OBS-029` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-OBS-047` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BK-REF-001` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BM-02` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BM-04` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BM-14` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BM-15` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/BRH-003` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/evidence/EK-BANK-RHYP-001` | `_flora_evidence_detail_page` | Exact repository retrieval ID; never canonical Evidence repository | None |
| `/explore` | `_flora_explore_page` | Repository Banking pipeline | None |
| `/flora` | `_flora_home_page` | Repository Banking pipeline; private discovery short-circuits without authority | None |
| `/flora/` | `_flora_home_page` | Repository Banking pipeline; private discovery short-circuits without authority | None |
| `/flora/banking` | `banking_landing_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/` | `banking_landing_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/ai-native` | `ai_native_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/ai-native/capability-model` | `ai_native_capability_model_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/banks` | `banks_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/barclays` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/barclays/analyst-history` | `analyst_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/barclays/briefing` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/barclays/event-timeline` | `enterprise_event_timeline_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/barclays/evidence` | `banking_evidence_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/barclays/financial-performance` | `financial_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/barclays/market-analyst-view` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/barclays/market-reaction` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/barclays/opportunity/COH-BAR-001` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/barclays/opportunity/COH-BAR-002` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/barclays/opportunity/COH-BAR-003` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/barclays/research-backlog` | `research_backlog_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/compare` | `banking_compare_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/competitors` | `banking_competitors_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/heatmap` | `heatmap_page` | Public source scenario view labels only | mode |
| `/flora/banking/heatmap/detail` | `heatmap_detail_page` | Public bank/theme scenario lookup only | bank, mode, theme |
| `/flora/banking/hsbc-uk` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/hsbc-uk/analyst-history` | `analyst_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/hsbc-uk/briefing` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/hsbc-uk/event-timeline` | `enterprise_event_timeline_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/hsbc-uk/evidence` | `banking_evidence_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/hsbc-uk/financial-performance` | `financial_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/hsbc-uk/market-analyst-view` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/hsbc-uk/market-reaction` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/hsbc-uk/opportunity/COH-HBUK-001` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/hsbc-uk/opportunity/COH-HBUK-002` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/hsbc-uk/opportunity/COH-HBUK-003` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/hsbc-uk/research-backlog` | `research_backlog_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/inspect` | `twin_inspection_page` | Curated repository industry inspection, not imported package inspection | None |
| `/flora/banking/lloyds` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/lloyds/analyst-history` | `analyst_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/lloyds/briefing` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/lloyds/event-timeline` | `enterprise_event_timeline_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/lloyds/evidence` | `banking_evidence_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/lloyds/financial-performance` | `financial_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/lloyds/market-analyst-view` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/lloyds/market-reaction` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/lloyds/opportunity/COH-LBG-001` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/lloyds/opportunity/COH-LBG-002` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/lloyds/opportunity/COH-LBG-003` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/lloyds/research-backlog` | `research_backlog_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest/analyst-history` | `analyst_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest/briefing` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest/event-timeline` | `enterprise_event_timeline_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest/evidence` | `banking_evidence_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest/financial-performance` | `financial_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest/market-analyst-view` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest/market-reaction` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/natwest/opportunity/COH-NWG-001` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/natwest/opportunity/COH-NWG-002` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/natwest/opportunity/COH-NWG-003` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/natwest/research-backlog` | `research_backlog_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/outlook` | `industry_outlook_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/pipeline` | `pipeline_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/portfolio` | `banking_portfolio_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/santander-uk` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/santander-uk/analyst-history` | `analyst_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/santander-uk/briefing` | `banking_bank_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/santander-uk/event-timeline` | `enterprise_event_timeline_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/santander-uk/evidence` | `banking_evidence_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/santander-uk/financial-performance` | `financial_history_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/santander-uk/market-analyst-view` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/santander-uk/market-reaction` | `market_reaction_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/santander-uk/opportunity/COH-SAN-001` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/santander-uk/opportunity/COH-SAN-002` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/santander-uk/opportunity/COH-SAN-003` | `banking_opportunity_page` | Exact opportunity belonging to this public bank scenario | None |
| `/flora/banking/santander-uk/research-backlog` | `research_backlog_page` | Exact public bank slug in repository BANKS; no private Enterprise lookup | None |
| `/flora/banking/signals` | `industry_signal_explorer_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/banking/timeline` | `timeline_page` | Repository banking_portfolio constants and public source scenarios | None |
| `/flora/lloyds` | `increment1_workspace_page` | Frozen repository Increment 1 fixture; no Enterprise Model store | None |
| `/flora/object/BK-ENT-001` | `increment1_workspace_page` | Frozen repository Increment 1 fixture; no Enterprise Model store | None |
| `/flora/object/BK-ENT-001/context-package` | `_flora_increment2_context_package_page` | Fixed repository semantic evaluation dataset | None |
| `/flora/object/BK-ENT-001/explain` | `_flora_increment2_explain_page` | Fixed repository semantic evaluation dataset | question_id |
| `/flora/object/BK-ENT-001/lineage/CHG-LBG-001` | `_flora_increment2_lineage_page` | Exact fixed-dataset claim; no arbitrary lineage lookup | None |
| `/flora/object/BK-ENT-001/lineage/CHG-LBG-002` | `_flora_increment2_lineage_page` | Exact fixed-dataset claim; no arbitrary lineage lookup | None |
| `/flora/object/BK-ENT-001/lineage/CHG-LBG-003` | `_flora_increment2_lineage_page` | Exact fixed-dataset claim; no arbitrary lineage lookup | None |
| `/flora/object/BK-ENT-001/lineage/CHG-LBG-004` | `_flora_increment2_lineage_page` | Exact fixed-dataset claim; no arbitrary lineage lookup | None |
| `/flora/reference` | `reference_workspace_page` | Repository source pipeline and non-authority preference cookie | saved |
| `/focus` | `_flora_focus_page` | Public scenario filtering only | confidence, contradiction, enterprise, evidence_strength, executive_role, horizon, hypothesis, opportunity, participant, recommendation_eligibility, unknown |
| `/governance` | `_flora_governance_page` | Repository-source governance summary; fixed protected navigation links | None |
| `/health` | `health_response` | Fixed service availability; no owner records | None |
| `/industries/uk-banking` | `twin_inspection_page` | Curated repository industry inspection, not imported package inspection | None |
| `/intelligence` | `_flora_intelligence_page` | Public source discovery shell; protected owners remain filtered | tab |
| `/opportunities` | `_flora_opportunities_page` | Repository Banking scenario pipeline | tab |
| `/pilot-sign-in` | `sign_in_page` | Fixed closed-access notice; no credential issuer | None |
| `/research` | `_flora_research_page` | Fixed navigation; no research/import records | None |
| `/shape` | `_flora_shape_page` | Repository Banking brief/scenario pipeline | horizon, opportunity |
| `/shape/banking` | `_flora_shape_page` | Repository Banking brief/scenario pipeline | horizon, opportunity |
| `/shape/banking/strategic-sales-brief` | `_flora_shape_page` | Repository Banking brief/scenario pipeline | horizon, opportunity |
| `/shape/strategic-sales-brief` | `_flora_shape_page` | Repository Banking brief/scenario pipeline | horizon, opportunity |
| `/workspace/enterprise/BK-ENT-001` | `increment1_workspace_page` | Frozen repository Increment 1 fixture; no Enterprise Model store | None |
| `/workspace/reference` | `reference_workspace_page` | Repository source pipeline and non-authority preference cookie | saved |

## Source trace and exceptions

`banking_portfolio.py` owns the five public bank slugs, source summaries and
opportunity IDs. Financial, analyst, event, signal and scenario views use these
constants, not workspace intelligence. `market-analyst-view` composes
`market_reaction_page` and `analyst_history_page`; both share this source boundary.
`enterprise_intelligence/pipeline.py` retrieves fixed repository
`enterprise-knowledge` observations, mechanisms and assets; derived pipeline output
is presentation material. Its configured reasoning adapter receives this public
source context, with no private retrieval path. Public tests use the deterministic
adapter and temporary derived-output location.

`increment1.py` reads frozen repository Increment 1 fixtures.
`enterprise_intelligence/explain.py` reads the fixed Lloyds semantic evaluation
JSON and four change IDs. `twin_inspection/industry.py` uses the public BANKS,
INDUSTRY_SIGNALS and PESTLE catalogues. The `/evidence/` name does not delegate
to canonical Evidence: `_flora_evidence_detail_page` searches only the fixed
pipeline source lists. Public source IDs already exist in the repository and
are not production workspace/account identifiers.

`/focus`, `/shape`, heatmap and `/ask` values operate only on source scenarios;
unknown source labels give source-only empty/unavailable results. Explain accepts
only its fixed public question ID. No account/workspace/run/package selector is
accepted. All unregistered Evidence, Enterprise, package and metadata paths deny.

`/deployment` exposes generic service availability, allowlisted code capabilities
and repository commit SHA. It no longer exposes environment-derived repository,
service labels or build/start commands. Governance and Digital Twins use the same
repository-only revision boundary. `/health` is fixed availability. Import setup
and sign-in are closed notices, with no registry enumeration or issuer.

Explain/context/lineage views may append the existing noncanonical runtime audit;
this is not canonical Evidence or imported intelligence. Reference preferences
remain non-authority navigation cookies under the existing exact-origin POST
rule. These exceptions grant no identity or resource access.

Raw origin-form request targets must match the dispatch path. Absolute-form,
double slash, semicolon, traversal, encoded path, extra segments and unregistered
IDs fail closed. Query bounds are 16 fields, 1024 characters per value and a 4096
character target. GET and HEAD share classification. Tests cover 21 unexpected
paths, eight query attacks, three HEAD paths and every catalogue handler.
