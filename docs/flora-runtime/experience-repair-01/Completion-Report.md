# Experience Reconciliation Repair 01 — completion report

Baseline main: `7f40bf2242f3b49da2eaac6c05a6db9450f78b95`, merge of #536,
including #530–#536. The [pre-change assessment](Claim-Authority-Assessment.md)
records the claim/authority paths before implementation. This is a bounded
presentation repair in three existing source files; analytical sizing data,
formulas, canonical owners and approval services are unchanged.

## What changed and why

| Audit finding | Existing implementation changed | Result / evidence |
| --- | --- | --- |
| F01 constructed sizing | [banking_portfolio.py](../../../cios/applications/flora/banking_portfolio.py): existing Banking-only page boundary and scenario helpers, bank/card/portfolio/pipeline/comparison/heatmap/detail renderers | Values visibly say **Illustrative, unverified commercial scenario**, identify external-services sizing, show original calculation, rounding, assumptions, duration and annualised comparator, and distinguish enterprise economic value, customer budget and qualified pipeline. Barclays remains £60m–£120m / £85m midpoint; its £205m aggregate remains 85+80+40, explicitly not qualified pipeline. Aggregation may overlap and cannot establish additive funded demand. |
| F01 timing / unsupported demand | Existing COH detail keeps familiar headings/order; timing explains literal scenario assumption, constructed window and assumed start | Confirmed procurement dates, customer milestones and buying triggers remain Unknown. The unsupported generic “entering buying activity” text is removed; the retained What Flora sees conclusion explicitly says no current buying activity is established. Sponsor/buyer/funding/procurement/scope are Unknown. No eligibility or acceptance service is bypassed or fabricated. |
| F01 supplier inference | Existing _supplier_cell and shared pilot disclosure | Accenture and other supplied relationships retain their original metadata. Detail exposes inferred position, rationale, source date (potential pilot default, not verified contract date), editorial confidence, absent contract-specific accepted Evidence and verification need. No incumbency, renewal or displacement is verified from general market presence. |
| F06 conviction, priorities and forecasts | Existing industry signal cards, account cards, timelines and Banking page source scope | Signal conviction is editorial and assigned by display-list position, not calibrated Evidence confidence. Rankings and AI-native horizons are strategic working scenarios. Industry relevance cannot establish an enterprise-specific qualified Material Pressure. Existing narratives, charts and values remain available. |
| F02 Home / Intelligence authority | [web/app.py](../../../cios/applications/flora/web/app.py): read-only _industry_import_counts, existing Home and Intelligence copy | The UK Banking link remains, labelled curated repository pilot. Candidate-import and current partial-release counts read existing Industry classification, import lifecycle and both account access/inspection checks. Anonymous/inaccessible/terminal imports are excluded; unreadable status is unavailable, not a fabricated zero. Complete Industry Twin acceptance is not established by this workspace. Static six-enterprise/owner-assessment claims are replaced by scoped source context; derived participant/gap counts are labelled as such. No fake Canvas registration or unified navigation is added. |
| F02 inspection authority | [twin_inspection/industry.py](../../../cios/applications/flora/twin_inspection/industry.py): existing profile, conclusions and source section | Replaces Governed / Owner-backed runtime declarations with curated repository presentation and explicitly unestablished canonical acceptance. Conclusions carry editorial conviction; no new Industry owner is introduced. |
| F05 provenance | Existing Evidence page and page disclosure | Generic source labels are retained but identified as unverified labels, not accepted citations. Canonical Evidence IDs, accepted Observation mappings and source locators remain Not supplied in the pilot. The hash is view identity only and does not prove claim provenance. Existing inspection paths remain. Actual Factory Evidence mappings/acceptance are untouched. |
| F06 event precision | Existing enterprise event timeline | Fixed date anchors are explicitly illustrative, not verified source-located events, procurement dates or programme milestones. No source event is invented. |

The pilot snapshot date `2026-07-19` is distinguished from claim-level source,
effective and customer-confirmation dates, which are Unknown here. Supplied FY
periods and supplier dates are preserved; this change does not refresh research or
turn a rendering snapshot into source verification.

The Banking-only page boundary covers legacy wrappers, so qualifications are
visible on existing executive routes rather than only in a dataclass or hidden
compatibility text. Object-specific formulas and inference are rendered next to
estimates/detail; portfolio/pipeline/comparison/heatmap views also expose their
constituent scenario assumptions. No new hidden compatibility strings were added.
Original source objects, numerical estimates and sizing logic were not changed.

## Ownership and permission boundaries

Home reads existing identity/classification, lifecycle and permission services;
it does not write an identity, access record, model or acceptance result. A
current promoted subset remains a **partial release**, never complete Industry
Twin acceptance. Canonical Evidence/Observations, Enterprise Models, pressure
qualification and commercial action eligibility retain their current owners.

The COH pilot has no actual accepted claim-level mappings to disclose. This repair
says so; it does not replace missing citations with generic labels or manufacture
IDs. Existing Factory mappings and model-backed reasoning remain separate,
including their ClaimValidator and action gates. No second reasoning or
opportunity-generation engine was introduced.

Accepted ADRs are unchanged. ADR-014/024 retain their existing Draft header versus
Accepted body ambiguity, recorded in the assessment; it was not resolved by editing
either decision or weakening its evidence boundary.

## Before/after results

[Regression-Comparison.json](Regression-Comparison.json) compares exact test IDs,
with the final targeted reruns overriding intermediate results.

| Check | Pinned main | Repair 01 |
| --- | ---: | ---: |
| 409 distinct cases across 25 relevant modules | 357 passed / 52 failed | 387 passed / 22 failed |
| New repair module (31 cases) | 1 passed / 30 failed | 31 passed |
| Existing Factory Repair 01 Evidence identity/release | 41 passed | 41 passed |
| Existing Factory Repair 02 Researcher/model integration | 32 passed | 32 passed |
| Existing Factory Repair 03 retained presentation/import | 23 passed | 23 passed |
| Claim/integrity suite | 44 passed | 44 passed |
| Durable Material Pressure lifecycle suite | 51 passed | 51 passed |

**30 corrected failures; zero new failing test IDs; 22 remaining pre-existing
failures.** Both sides contain the same 409 cases, with no missing IDs or skips.
No existing tests were weakened, xfailed or removed. The new baseline cases are
intentionally negative regression tests against the unchanged main implementation.

The remaining failures are the same baseline Banking/legacy presentation and Canvas
expectations observed in the audit: portfolio increment 3 (7), navigation increment
44 (4), visual increment 45 (1), visual correction 45.1 (1), reinvention increment
42 (6), and Enterprise Canvas/landing (3). Exact IDs and failure messages are in
the comparison. The focused six-module run has 61 passed / 10 inherited failures;
the standalone new module has 31 passed. Broad runs exit nonzero because of the
reported baseline failures; the new focused module exits 0. This is not a claim
that the entire repository or product is green.

Four intermediate presentation compatibility failures were corrected while
retaining safe headings/order, a bounded What Flora sees conclusion, catalogue
links without new internal-code exposure, and an accurately scoped Governed
import lifecycle description. A browser expectation was corrected to check the
signal explorer’s actual editorial disclosure rather than requiring a High label
which that route never displayed. These intermediate outcomes are not omitted
or counted as unresolved regressions.

Actual original TEL W5, TEL W6 and BNK W1 archives were supplied to the existing
hash-pinned isolated Factory tests. All passed, with original bytes unchanged:

- TEL W5: `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`
- TEL W6: `c24cbf67c687883947fc4020b098c81c84b343e618980989b0af9665e2210ffb`
- BNK W1: `1c2d18ebf0d48a32f4093c9ff7ce16a2e1203fedd2cc8ef3760367b033a56313`

No source archive is added or altered by this PR. Fixtures use explicit isolated
identity/approval decisions, not real owner acceptance or production promotion.

## Visible browser acceptance

[Browser-Comparison.json](Browser-Comparison.json) records the same 17 routes in
desktop 1440×1050 and iPad-like 1024×1366 Chromium touch/mobile emulation. Each
version runs 154 checks plus two click journeys. Baseline: 34 route failures;
repair: zero. Every sampled route returns 200 with zero horizontal overflow. Both
versions retain the actual Home → Banking → Barclays → scenario-detail journey.
Qualifications use real visible-locator checks, not HTML substring checks alone.

The [rendered evidence index](rendered/README.md) links before/after detail,
estimate, supplier, Home, account and industry-inspection captures. Source
qualifications, formulas, assumptions and Unknowns are not hidden. The retained
BNK current-main Factory fixture additionally shows **one partial release** and
**complete acceptance not established**, using the real successful subset receipt
and existing owner lifecycle (see [Retained-BNK-Home.json](Retained-BNK-Home.json)).
No Canvas record is created by the Home reader; the new repository-level test
checks the actual access repository, not a guessed storage path.

## Commands and environment

Use an existing Flora test environment. [run_regressions.py](run_regressions.py)
sets separate temporary module/case data roots. Both worktrees use the same
fixtures and initial empty setup; paths are separate to prevent cross-run
contamination. No production data, storage path or source record is used.

```bash
export PYTHONPATH=.
export FLORA_AUDIT_TEL_W6='/path/to/actual-retained-W6.zip'
export FLORA_AUDIT_BNK_W1='/path/to/actual-retained-BNK.zip'
python docs/flora-runtime/experience-repair-01/run_regressions.py --output /tmp/flora-assurance-after
python -m pytest -q tests/test_flora_experience_assurance_repair.py
```

The recorded interpreter is `/workspace/cios-venv/bin/python`; module commands
use `-q --tb=short --basetemp=<module-root> --junitxml=<module.xml>`. The before
worktree is pinned main with only the identical new test file copied in, using
the same runner by absolute path. Artifact absence in a later environment yields
explicit skips in existing package tests; none were skipped in this run.

Browser tooling uses installed system Playwright/Chromium; no dependency was added.
[serve_test_routes.py](serve_test_routes.py) invokes the **existing** FloraWebHandler
on loopback with an explicit isolated FLORA_DATA_DIR, development test headers and
separate derived-output directory. It avoids production startup/deployment hooks.
[browser_acceptance.py](browser_acceptance.py) uses the two loopback ports and a
required output directory. Example invocation after starting the two isolated
existing-handler servers:

```bash
python docs/flora-runtime/experience-repair-01/browser_acceptance.py --output /tmp/flora-assurance-browser
```

The server script takes its port as its argument and requires FLORA_DATA_DIR;
set FLORA_PILOT_DIR to the same isolated root, FLORA_ENVIRONMENT=development and
FLORA_TRUST_PROXY_HEADERS=1. The local headers are test fixtures, not production
account verification. Python compilation and `git diff --check` pass. This is a
selected relevant corpus, not the full repository suite.

## Remaining limitations and stop

- Source research, financial snapshots and scenario assumptions remain the existing
  pilot inputs. Generic source labels have not become claim-level Evidence.
- Unified Twin discovery, canonical Banking adapters, model/Industry reconciliation,
  the shadowed inspection alias and broad navigation repair remain outside this
  increment. No migration/backfill or new canonical store was introduced.
- This does not produce qualified opportunities, customer budgets, procurement
  intelligence, economic exposure calculations, or new Material Pressures.
- iPad evidence is local Chromium emulation, not physical iPad/Safari or a complete
  accessibility audit. Extra disclosure increases page length; it preserves the
  existing layout and inspection routes rather than redesigning the UI.
- Deployment verification of this unmerged change is **NOT TESTED**. No deployment,
  production upload/promotion or production intelligence modification occurred.
- Accepted ADRs and governance permissions are unchanged. Later repair increments
  have not begun. Work stops after this Repair 01 publication/review step.
