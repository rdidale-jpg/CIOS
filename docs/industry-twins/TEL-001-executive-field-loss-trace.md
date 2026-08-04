# TEL-001 executive field-loss trace

## Result

The first loss boundary was the **executive presentation projection**. The
Researcher adapter output was persisted losslessly, reloaded losslessly into the
review detail, and copied losslessly into `SemanticObject.attributes`. The
deployed explorer then rendered only `statement` (or an eligibility warning),
discarding the attributes from its page model. This explained why population
counts were right while content appeared absent.

The correction introduces one canonical semantic-owner page contract,
`executive_record_view_model`, and makes the explorer render that output. It
does not read `source_payload`, add a second Researcher mapping, promote a
candidate, or change the immutable ZIP.

## Representative end-to-end traces

Values below are from the unchanged package (SHA-256
`bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`).
“Constructor N/A” is significant: these six governed business wrappers are
reviewable canonical candidates, but `planning.PERSISTABLE_CANONICAL_CLASSES`
does not grant them a promotion constructor. It would be incorrect to pretend
that candidate display requires promotion.

| Family / representative | 1 raw NDJSON | 2 adapter output | 3 persisted candidate | 4 review representation | 5 constructor input | 6 constructor output | 7 semantic repository | 8 executive projection | 9 page field | 10 rendered value |
|---|---|---|---|---|---|---|---|---|---|---|
| Industry Overview (`industry_overview_wave5.ndjson`, sole row) | `economics.annual_market_revenue.uk_telecoms_sector_2025` = “£34.7bn, down £0.3bn / 0.8% year-on-year” | `adapt_researcher_payload`: retained in canonical `industry_profile` | `_candidate` → `CandidateImportRecord.payload.industry_profile`: present | `BlueprintReviewPlanCoordinator._run` detail `candidates[].payload.industry_profile`: present | N/A; `industry_twin` is not auto-persistable | N/A; no mutation | `assemble_semantic_twin` → `SemanticObject.attributes.industry_profile`: present | **Before:** `_explorer` replaced it with “Supporting context…”; **after:** `executive_record_view_model.fields[Industry profile]` | `ExecutiveRecordViewModel.fields` | `_executive_record_card`: “Uk Telecoms Sector 2025: £34.7bn…” |
| Enterprise (`ENT-BT`) | `executive_overview.what` = “BT Group is a UK-headquartered telecommunications group…” | `description` renamed from `executive_overview.what`; `strategy`, `operating_structure`, `financial_context`, `technology` present | same names and values in candidate JSON | same values in review detail candidate | N/A; `enterprise_twin` is review-only | N/A | `SemanticObject.attributes.description` and other owner fields present | **Before:** `_enterprise_card` suppressed most fields behind an unrelated completeness gate; **after:** canonical view-model fields | Overview, Strategy, Operating structure, Financial context, Technology, Ecosystem, Pressures, Programmes, Transformation posture | substantive dossier fields appear on Enterprise Dossiers and dossier links |
| Market Participant (`MP-OFCOM`) | `role` = “Telecoms access, spectrum, complaints and infrastructure reporting”; `classification` = `Regulator` | `role` preserved; `domain` renamed from `classification`; capabilities and relationships preserved | present in candidate payload | present in review detail candidate | N/A; `market_participant_twin` is review-only | N/A | present in `attributes.role/domain/capabilities/relationships` | **Before:** statement-only fallback; **after:** canonical participant view model | Role, Domain, Capabilities, Relationships, Current activity, Market significance | “Role: Telecoms access…” and “Domain: Regulator” |
| Programme (`PROG-BT-TRANSFORMATION`) | `programme_name` = “BT FY30 cost and operating-model transformation”; `timeline` = `FY26-FY30` | renamed to `title` and `timing`; owner, objective, phase and investment mapped | present | present in review detail candidate | N/A; `transformation_programme` is review-only | N/A | present in semantic attributes | **Before:** title/attributes replaced by fallback; **after:** programme view model | Owner, Business unit, Objective, Stage, Timing, Investment | programme name and “Timing: FY26-FY30” |
| Opportunity (`OPP-VMO2-AI-CX`) | customer `Virgin Media O2`; nested `client_problem.customer_problem`; `commercial_type_wave5` = “Shaping opportunity” | customer renamed to `affected_enterprises`; problem flattened to `client_problem`; timing, type, value type and evidence mapped | present; exactly one candidate for the source row | present; nested scorecard/support rows remain ignored lineage, not hypotheses | N/A; `opportunity_hypothesis` is review-only | N/A | one semantic opportunity with canonical attributes | **Before:** special card read a smaller/legacy vocabulary; **after:** common canonical opportunity view model | Customer, Client problem, Business unit, Buyer, Timing, Procurement status, Commercial type, Value type, Value | “Customer: Virgin Media O2”; “Commercial type: Shaping opportunity” |
| Reinvention (`RA-IND-UK-TELECOMS`) | `current_operating_model` = “Capital-intensive, regulated network operators…”; `expected_tipping_point` begins `2026-2028` | renamed to `summary`; affected functions, mechanism, timing, tipping point and implications mapped | present; seven candidates persisted | present; seven review detail candidates | N/A; `ai_reinvention_assessment` is review-only | N/A | seven semantic objects with canonical attributes | **Before:** statement-only fallback; **after:** reinvention view model | Current operating model, Affected functions, AI disruption mechanism, Timing, Expected tipping point, Executive implications | substantive operating-model and 2026-2028 timing text |

At stages 3 and 4, `source_payload`, every adapted top-level field, and
`mapping_diagnostics` survive. The review *effect* intentionally contains only
mutation metadata, while `review_summaries/.../details.json` retains the joined
candidate. No constructor silently discards these wrapper fields because
governance deliberately provides no automatic constructor for them.

## Test path versus deployed UI path

Previous tests called `BlueprintPackageValidator.validate_and_stage`, then
asserted candidate dictionaries or directly called `assemble_semantic_twin`.
They stopped before the presentation branch in `_explorer`; consequently they
proved adaptation but could not detect the statement-only fallback.

The new regression follows the web service call graph:

`upload_and_validate_blueprint` → `BlueprintPackageRegistry.receive` →
`BlueprintPackageValidator.validate_and_stage` →
`CandidateStagingRepository.list_candidates` (via `staging_summary`) →
`executive_workspace_page(view="explore")` → `_semantic_candidates` →
`assemble_semantic_twin` → `business_collections` →
`executive_record_view_model` → `_executive_record_card` → `_page`.

It uses objects loaded from the persisted staging repository, not synthetic
`SemanticObject` instances, and checks the final HTML for all six collections.

## Governance and count reconciliation

The unchanged import yields 17 opportunity hypotheses, seven reinvention
assessments, 92 Evidence, 30 Unknowns and 11 Contradictions. Supporting
qualification rows remain lineage-only and do not inflate opportunities.
`canonical_mutations` remains zero and no memory directory is created.

Candidate-mode and promoted-mode are intentionally different: the Blueprint
executive route reads governed staging candidates so operators can review
intelligence before promotion. Promoted canonical memory has no constructor for
these six wrapper classes. This correction aligns candidate pages with their
existing semantic owner; it does not broaden promotion authority.

## Deployment evidence

The repository baseline identifies merged adapter commit `d0401f3` and merge
commit `77b74e5`. Runtime commit and import timestamps are exposed by
`deployment_metadata` and persisted candidate `created_at`, respectively, but
this checkout contains neither a deployed Flora URL nor Render credentials or
mounted `/var/data/flora`. Therefore the actual Render SHA and fresh production
import timestamp cannot be truthfully recovered from this environment. They
must be captured from the deployed review page before production acceptance;
repository history alone is not deployment proof.

## Before/after rendered snapshot

```text
BEFORE
Industry Overview
  [record identity]
  Supporting context; not presented as an executive insight.

AFTER
Industry Overview
  Industry profile: ... Economics: Annual Market Revenue:
  Uk Telecoms Sector 2025: £34.7bn, down £0.3bn / 0.8% year-on-year ...

BEFORE
Opportunity
  Client problem not established

AFTER
Opportunity
  Customer: Virgin Media O2
  Client problem: VMO2 needs to improve customer-service resolution ...
  Commercial type: Shaping opportunity
```

These snippets are asserted against final `_page` HTML by the end-to-end test,
so a recurrence of identity-only output fails the suite.
