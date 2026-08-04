# TEL-001 shared profile end-to-end evidence

## Exact package

The regression package is `docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip`; tests assert its SHA-256 remains `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`, its manifest profile version is `1.0.0`, and the archive is unchanged while Flora stages candidates.

## Before and after runtime evidence

Before the shared governed selector contract was executed, Flora could load the profile but TEL-001 pages still showed unmapped or pending placeholders: Industry Overview was supporting context, candidate programmes and participants were not rendered substantively, opportunities recommissioned mapped fields, and seven reinvention records were not reconciled into the candidate presentation.

After this revision, the unchanged package follows manual Import Twin's application path: receive, inspect, validate and stage, assemble the semantic Twin, construct candidate executive view models, render the deployed page routes, and render Research Gaps from the same staged candidates. The observed after-state is:

| Area | After evidence |
| --- | --- |
| Industry Overview | Renders the supplied scope/definition, market economics such as `£34.7bn, down £0.3bn / 0.8% year-on-year`, and regulatory/transformation implications under Commercial Implications. |
| Enterprises | Renders six enterprise cards; BT Group dossier includes its supplied UK-headquartered telecoms description, FTTP build and take-up strategy/transformation posture, and links such as Openreach FTTP / EV-BT-FY26. |
| Market Participants | Renders 17 candidate participants and supplied role/capability evidence, including Ofcom as Regulator with telecoms access, spectrum, complaints and infrastructure reporting. |
| Major Programmes | Renders 13 supplied programme hypotheses, including BT FY30 cost and operating-model transformation, owner/objective details and FY26-FY30 timing. |
| Opportunities | Renders exactly 17 canonical opportunity hypotheses; supplied values include Virgin Media O2, client problem, Shaping opportunity, commercial type/timing/value fields and evidence references. |
| Reinvention Assessments | Reconciles all seven source records as `ai_reinvention_assessment`; valid candidate records are visible in the reinvention assessment presentation. |
| Evidence | Renders 92 evidence records and preserves candidate evidence references used by enterprises, participants, programmes, opportunities and reinvention records. |
| Unknowns | Renders 30 Unknown records as candidate intelligence rather than hiding them. |
| Contradictions | Renders 11 Contradiction records as candidate intelligence rather than hiding them. |
| Research Gaps | Research Gaps now distinguish owner-assessment pending governance from missing source fields, and no longer recommission mapped candidate fields such as organisation description when they are present but unassessed. |

## Broader test reconciliation

| Test | Actual output | Previous expected output | Runtime defect? | Obsolete expectation? | Governing architecture |
| --- | --- | --- | --- | --- | --- |
| `test_primary_pages_consolidate_incomplete_records` / programmes | `9 programme hypotheses · 0 owner-assessed programmes` with owner-assessment pending governance. | `9 programme hypotheses identified`. | No; the runtime now exposes supplied candidates while preserving owner assessment. | Yes; wording predates candidate-visible presentation. | Candidate import may project staged intelligence, but completeness remains with IT-001 owner assessment. |
| `test_primary_pages_consolidate_incomplete_records` / opportunities | `9 supplied candidate hypotheses · owner assessment pending governance` and candidate cards remain inspectable. | `9 hypotheses require further research` and hidden candidate cards. | No; hiding substantive candidates caused the accepted TEL-001 evidence to disappear. | Yes; the expectation was superseded by the deployed candidate-presentation route. | Flora is a projection executor; Research Gaps must not recommission mapped candidate intelligence. |
| `test_primary_pages_consolidate_incomplete_records` / participants | `10 participant concepts · 0 owner-assessed participant profiles`. | `10 participants identified` and `0 sufficiently classified`. | No; output is more precise about candidate concepts versus owner-assessed profiles. | Yes; classification authority remains with Market Participant Twin governance. | MPT-001 owns participant semantics; Flora renders candidate concepts and assessment status. |
| `test_bbc_dossier_has_ordered_honest_consolidated_sections` | `Organisation description pending owner assessment` and `9 candidate record(s) are associated`. | `Organisation overview incomplete` and `9 hypothesis record(s)`. | No; current wording is the governed distinction between supplied candidate fields and unassessed completeness. | Yes; the old wording falsely implied source absence. | Candidate intelligence remains visible; readiness and eligibility remain under canonical owners. |

## Shared profile governance

`cios/contracts/twin_object_profiles/researcher_v1.json` is the canonical shared Researcher portable Twin Object Profile. Its architectural owner is CIOS Architecture / Twin Object Profile governance; status is current governed shared profile. It uses semantic versioning: additive selector aliases may increment minor versions; breaking canonical field or class changes require a major version and dual-consumption tests. Superseded versions remain loadable for declared historical packages until an architecture decision retires them. The profile is manually maintained as a controlled contract compiled from canonical implementation profiles, not generated at runtime. It consolidates Researcher portable selectors for existing Implementation Profiles without replacing IT-001, MPT-001, OT-001, EI-012, EOD-001 or release-manifest owners. Canonical object owners keep semantic authority; Flora's adapter executes selectors, aliases classes, preserves the source payload and reports diagnostics rather than becoming a second semantic owner.

## External Researcher and drift protection

The same JSON profile is included in the Researcher Knowledge Pack at `knowledge-packs/researcher/contracts/researcher_v1.json` and listed in `knowledge-packs/researcher/manifest.yaml`. Tests prove the pack copy equals Flora's loaded contract, conformant Researcher opportunity objects pass validation, non-conformant objects fail, unsupported profile classes fail, and profile-version drift fails. Drift protection asserts that the Researcher Knowledge Pack profile version, Flora loaded profile version, package-declared profile version and test fixture profile version all equal `1.0.0`.
