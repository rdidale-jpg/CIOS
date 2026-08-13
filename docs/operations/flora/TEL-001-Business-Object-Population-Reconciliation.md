# TEL-001 Business Object Population Reconciliation

## Governed source

This test-only manifest was read directly from the unchanged `TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip`. Its SHA-256 is `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`. Production code does not read this document or the test oracle.

| Source business/support family | Source set | Count |
|---|---|---:|
| Industry | `composite_industry_twin_wave5.ndjson` | 1 |
| Enterprises | `enterprise_dossiers_wave5.ndjson` | 6 |
| Market Participants | `market_participant_profiles_wave5.ndjson` | 17 |
| Programmes | `programme_objects_wave5.ndjson` | 13 |
| Opportunities | `opportunity_objects_wave5.ndjson` | 17 |
| Reinvention assessments | `reinvention_assessments_wave5.ndjson` | 7 |
| Evidence | `evidence_register_wave5.ndjson` | 92 |
| Unknowns | `unknown_register_wave5.ndjson` | 30 |
| Contradictions | `contradiction_register_wave5.ndjson` | 11 |
| Relationships | `relationship_register_wave5.ndjson` | 308 |
| Memberships | `membership_register_wave5.ndjson` | 50 |

Every manifest row is represented by source set, source identifier, canonical identifier (the immutable source ID), family, title/name, supplied subject/owner, relationship/membership references, and commercial type in the validator candidates. The executable oracle is `tests/fixtures/tel001_expected_truth.json`; the rendered reconciliation is `rendered-population-reconciliation/acceptance.json`.

## Boundary trace

| Boundary | Row count | Unique Opportunity IDs | Expected | Divergence |
|---|---:|---:|---:|---|
| ZIP Opportunity objects | 17 | 17 | 17 | none |
| Manifest/validator accepted Opportunity declarations | 17 | 17 | 17 | none |
| Persisted accepted candidates | 17 | 17 | 17 | none |
| Semantic business objects | 17 | 17 | 17 | none |
| Canonical factual/read projection | 17 | 17 | 17 | none |
| Executive collection/view model | 17 | 17 | 17 | none after correction |
| Rendered entity containers | 17 | 17 | 17 | none after correction |

The pre-correction read path admitted 272 opportunity-shaped presentation rows at the executive Opportunity query: 17 canonical Opportunity objects, 187 qualification scorecards, 17 qualified-register rows, 17 residual-register rows, 8 named-open-pipeline rows, 7 overlap rows, 7 shaping-register rows, and 12 corrected-ID rows. `17 + 187 + 17 + 17 + 8 + 7 + 7 + 12 = 272`. Evidence, Unknowns, Contradictions, Relationships and Memberships were not part of those 272.

## Identity reconciliation

All 17 source IDs below are their canonical source identity, their executive entity ID, and occur once in `opportunities.html`: `OPP-VMO2-AI-CX`, `OPP-BT-AI-ENGINEERING`, `OPP-BT-AIOPS`, `OPP-OPENREACH-FIBRE-AUTOMATION`, `OPP-OPENREACH-CP-ENABLEMENT`, `OPP-VT-NETWORK-AI-OPS`, `OPP-VT-ENTERPRISE-5G`, `OPP-CITYFIBRE-PROJECT-GIGABIT`, `OPP-CITYFIBRE-WHOLESALE`, `OPP-TALKTALK-COST`, `OPP-PXC-PLATFORM-EFFICIENCY`, `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE`, `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE`, `OPP-VMO2-NEXFIBRE-MIGRATION`, `OPP-VT-WHOLESALE-REMEDY-ASSURANCE`, `OPP-GOV-NS4-TELCO-PUBLIC-SECTOR`, and `OPP-BT-VERIZON-JV-INTEGRATION`. Result: **17/17 PASS**.

The same invariant holds for the 13 Programme IDs in `programme_objects_wave5.ndjson`: source 13, semantic 13, executive 13, rendered 13. Supporting fields, Evidence, Unknown and Contradiction references remain attributes/sections of the business entity; candidate state remains unreviewed and unpromoted.
