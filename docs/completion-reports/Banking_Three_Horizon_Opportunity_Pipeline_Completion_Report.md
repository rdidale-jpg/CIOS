# Banking Three-Horizon Opportunity Pipeline — Completion Report

## Current Focus limitations found

The previous Focus Banking page was a passive enterprise-inspection page. It listed supported enterprises, showed current understanding, observations and mechanisms, but did not generate commercial opportunities, horizon rationale, movement criteria, readiness states, portfolio filters or opportunity-to-Shape context.

## Runtime components reused

- Existing Banking Enterprise Intelligence runtime pipeline.
- Existing semantic Banking interpretation layer.
- Banking observations `BK-OBS-014`, `BK-OBS-015`, `BK-OBS-016`, `BK-OBS-029`, `BK-OBS-047`.
- Banking mechanisms `BM-04`, `BM-02`, `BM-14`, `BM-15`.
- Banking Reinvention Hypothesis `BRH-003`.
- Banking Enterprise Twin and comparison assets included in the existing runtime manifest.
- Strategic Sales Navigation specification and validation assets.

## Opportunity object implemented

Implemented a typed `CommercialOpportunity` runtime object with derived-runtime authority, transient persistence, qualitative confidence, readiness, freshness, Unknowns, Contradictions, Recommendation Eligibility, movement criteria, prohibited stronger actions and inspectable lineage.

## Opportunity generation method

`generate_banking_opportunity_pipeline()` invokes the governed Banking runtime, uses its generated run ID, telemetry and semantic context hash, and derives opportunities from structured observations, mechanisms, hypotheses, assets and participant/enterprise context. The generator excludes unsupported named-bank specificity by creating a Not currently actionable/deferred candidate rather than padding the horizon board.

## Banking hypotheses used

- `BRH-003` — physical access may become shared trust infrastructure rather than proprietary distribution.

## Banking enterprises and participant types used

- Participant types: large retail incumbent, mutual/building society context, digital challenger bank, UK retail banking participant, shared-access ecosystem participant, unsupported named-bank specificity.
- Enterprise-specific display is limited to `Nationwide / Virgin Money` where current governed coverage supports partial context; other named banks remain listed as coverage context but are not fabricated into account-specific opportunities.

## Opportunities generated

1. Redesign physical and assisted access around a mixed distribution model.
2. Use mutual access and member-service positioning as a trust advantage.
3. Test whether app-first challengers need assisted-access partnerships.
4. Prepare executive provocation on customer-outcome evidence for distribution change.
5. Explore shared infrastructure as future distribution resilience.
6. Do not pursue unsupported named-bank physical access claims.

## Opportunities excluded

Unsupported bank-specific opportunities for Lloyds Banking Group, NatWest Group, Monzo, Starling, Barclays and Santander UK are not promoted unless governed Enterprise Twin or labelled human account knowledge supports enterprise specificity.

## Horizon distribution

The deterministic runtime currently produces Horizon 2, Horizon 3 and Not currently actionable candidates. Horizon 1 remains possible under policy but is not fabricated where active programme, sponsor and enterprise economics evidence are incomplete.

## Horizon classification policy

The classifier considers enterprise specificity, timing, programme evidence, executive role relevance, contradictions, Recommendation Eligibility and qualitative confidence. It returns horizon, rationale, supporting factors, constraining factors, movement criteria and human-review requirement. No universal numeric opportunity score is introduced.

## Movement criteria

Each opportunity includes movement criteria. Examples include moving from Horizon 3 to Horizon 2 when enterprise exposure or programme evidence appears, moving from Horizon 2 to Horizon 1 when sponsor/programme/economics evidence appears, and downgrading when evidence becomes stale or contradiction strengthens.

## Readiness states

Implemented: Candidate, Evidence building, Ready for executive validation, Ready to shape, Deferred and Rejected as typed readiness options. Current generated opportunities use Candidate, Evidence building, Ready for executive validation and Deferred.

## Executive roles

Roles include Chief Operating Officer, Chief Customer Officer, Retail Banking Director, Distribution leader, Chief Product Officer, Chief Risk Officer and Strategy Director. Named executives remain empty unless governed evidence exists.

## Unknown effects

Unknown named executive ownership, enterprise economics, programme evidence and enterprise exposure constrain horizon, readiness, confidence and next action.

## Contradiction effects

Participant-specific contradictions constrain action and force branching between cost-takeout, trust/inclusion and shared-infrastructure interpretations.

## Explore integration

Explore Banking now links to `View Banking Opportunity Pipeline` while preserving a secondary enterprise-inspection path.

## Shape integration

`Shape brief` passes opportunity ID and context through query parameters. Shape preserves the selected opportunity context, including scope, hypotheses, executive roles, Unknowns, Contradictions, horizon, Recommendation Eligibility and lineage.

## Filters implemented

Horizon, enterprise, participant type, executive role, hypothesis, confidence, evidence strength, Recommendation Eligibility, Unknown present, Contradiction present and reset.

## Semantic reasoning mode

The pipeline reports the existing Banking runtime semantic reasoning mode and uses deterministic fallback labelling where applicable.

## Deterministic validation

Tests assert no opportunity lacks hypothesis or observation lineage, no duplicate IDs exist, no named executive is invented, no authoritative persistence is used, no unsupported enterprise is introduced and classification constraints are enforced.

## Tests added

- `tests/test_flora_banking_opportunity_pipeline.py`.

## Tests run

- `python -m py_compile cios/applications/flora/web/app.py cios/applications/flora/enterprise_intelligence/opportunity_pipeline.py`
- `python -m pytest tests/test_flora_banking_opportunity_pipeline.py tests/test_flora_banking_v2_web.py -q`

## Manual validation

Documented in README and repeated on the Focus page for Rob.

## Production startup result

Validated by importing the production application and exercising HTTP routes during tests. Render start command remains `python -m cios.applications.flora.web.app`.

## Files created

- `cios/applications/flora/enterprise_intelligence/opportunity_pipeline.py`
- `tests/test_flora_banking_opportunity_pipeline.py`
- `docs/completion-reports/Banking_Three_Horizon_Opportunity_Pipeline_Completion_Report.md`

## Files changed

- `cios/applications/flora/web/app.py`
- `README.md`

## Limitations

- No CRM integration, revenue probability, named executive inference, proposal generation or persistence of opportunity decisions.
- Human account knowledge is represented as a future labelled evidence demand; no account-management input workflow is added.
- Horizon 1 is policy-supported but not fabricated by the current evidence set.

## Next recommended increment

Add a safe labelled human-account-knowledge capture surface and deterministic policy gates that can promote Horizon 2 candidates to Horizon 1 after explicit account validation.

## Deployment risk

Low-to-medium. The implementation is deterministic and transient, but Focus now invokes the Banking runtime and opportunity generator on request, so route latency should be monitored.

## Release metadata

Base branch: origin/main (merge-base unknown).
Working branch: work.
Remote branch: work (current branch; push/remote publication handled outside this environment).
Target branch: main.
Commit: final git commit recorded in PR metadata and final response.
PR: prepared with make_pr tool.
Merge status: unmerged.
Dependency commits: none identified.
