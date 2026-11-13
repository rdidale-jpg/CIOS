# Offers pilot validation

Current candidate identity and hosted result are available on the draft PR's **Checks** tab. Require the latest head's successful FLORA validation; neither an earlier run nor this document authorises integration.

## Local evidence

- 58 focused Offers scenarios: real revocable sessions; workspace/employer/private isolation; fresh-workspace owner setup through the existing EmployerContext service, explicit binding; delegated independent approvals; immutable/concurrent versions; master authorisation; protected/stale parent and ancestor versions; deterministic cross-journey pair identity; pattern-specific relevance; mission exclusions; source-cutoff handling and upstream snapshot drift rejection; account permissions; Studio opt-in, component proof/lineage/rights, target scope and withdrawal; audit rollback; forged headers, CSRF, route/query rejection and XSS; zero Pipeline/canonical writes or network/model calls.
- 61 retained Technology owner journey and Pipeline tests passed.
- 25 CI-policy tests passed; baseline comparator and security discovery unchanged.
- 247 responsive/owner browser checks passed; [sanitized checks](previews/Browser-Checks.json). Real local HTTPS and browser sign-in; synthetic data only. Desktop 1440×1000, iPad 1024×1366, mobile 390×844; native keyboard interaction, source expansion, private save/submission, default-off and reversible Studio, private composition, no horizontal overflow, no page errors and no Pipeline file created.
- 15 pixel comparisons against clean main `854a783b3c5f83d6ee3604f49a76772529b7339a`: Banking industry, Aviation industry, Lloyds enterprise, easyJet enterprise and Technology experience at each viewport; all identical. The intentional Opportunities change is a single contextual Offers entry; the five primary destinations stay unchanged.
- 36 committed screenshots, linked in the [acceptance walkthrough](Acceptance-Walkthrough.md). They are fixture previews, not a deployed service or real employer approval.

The first full local preflight passed all **388 strict security tests** and found one new regression: a sixth primary navigation item violated FLORA's existing five-destination contract. The change was corrected by restoring primary navigation and adding a contextual Opportunities entry. The full gate is rerun on the corrected committed candidate; its final result is reported in the draft PR/Checks. The failing preflight is not represented as a passing regression run.

Full gate policy: preserve all 1,432 baseline test identities, exactly 57 inherited failures (21 domain, 12 financial, 24 legacy) and 10 inherited skips with their approved signatures/reasons. Strict security must pass 388/388 without skips. New Offers scenarios run separately in hosted CI; no exception, fingerprint or baseline adjustment is permitted.

## Reproduction and limitations

Commands are in the walkthrough. The workflow runs strict security, the versioned regression comparator, CI-policy tests, the retained Technology owner tests and new Offers tests on the current candidate. Hosted execution tests GitHub's synthetic merge against main; inspect the run's head SHA and checkout SHA when checking exact identity. No GitHub token, private research, environment configuration or raw local logs are published here. Sanitized hosted test artifacts follow the existing retention policy.

The pilot generates no financial/people estimates: economics are omitted unless future accepted inputs support them. Existing citation-only and candidate research is not promoted. No source refresh was purchased or run. Offers and rights approvals remain human declarations; actual delivery proof, source-operation rights, account access and customer validation must be reviewed before real commercial use. No deployment config, paid client, autonomous agent, outreach integration or Pipeline writer is added.
