# Validation, scope and self-critique

This review separates implementation proof from visual acceptance and deployment. Exact head, final file inventory, hosted links and final results are maintained in the draft PR. Browser proof records the captured checkout and runtime hashes; subsequent evidence-only commits do not imply a different application build.

## Reproducible checks

Use the repository's existing test environment. All services and storage used below are isolated local test instances.

```sh
python tools/ci/flora_ci.py --output /tmp/flora-recovery-ci
python -m pytest tests/test_flora_accepted_ux_recovery.py tests/test_flora_lloyds_flagship.py tests/test_flora_ux_unify_670.py tests/test_flora_uxr1_650.py tests/test_flora_experience_684.py tests/test_flora_banking_cohort_691.py tests/test_flora_et_integrate_672.py tests/test_flora_enterprise_economics_a1.py -q
python docs/flora-runtime/accepted-ux-recovery/validate.py
python docs/flora-runtime/accepted-ux-recovery/browser.py /tmp/flora-recovery-browser after
python tools/research/enterprise_economics_preview.py --output /tmp/flora-economics-browser
```

The existing Enterprise Economics hosted workflow also runs the recovery tests and browser harness. It retains the original strict-security invocation and existing A1 historical integrity check. No new release environment or approval gate is introduced.

The historical comparator, approved failures/skips and original security tests remain unchanged. The compatibility adapter accepts **only exact reviewed file bytes and named presentation-function changes** against the verified predecessor. It retains prior AST checks and rejects any unreviewed mutation; this grants no runtime authority.

## Individual stale assertion reconciliation

| Test family | Old assertion | Justified correction / retained boundary |
| --- | --- | --- |
| `test_flora_lloyds_flagship.py` | Analysis absent in Facts; four old SWOT title prefixes; evidence accordion; old root link label | Unified typed content, eight theme anchors, no executive accordion and Explore Lloyds label. Source, relationship and withdrawal negatives retained. |
| `test_flora_ux_unify_670.py` | Reading-mode links, fact/analysis separation, source-unavailable reading placeholder | Same public composition on legacy URLs; reported numbers and scoped interpretation coexist. Source rights, private-run, provenance and request-boundary negatives retained. |
| `test_flora_enterprise_economics_a1.py` | Public Source & basis accordion and separate assumed/insight stage | Both existing types in one stage; zero public basis accordion. No new measures or permissions; invalid units/entities/periods and source withdrawal retained. |
| `test_flora_experience_684.py` | Separate reading selector, only one branch visible | Existing per-stream facts, conceptual mechanisms and eligible conditional implications together; exact subject/stream and source negatives retained. |
| `test_flora_et_integrate_672.py` | Insight exists only on insight URL; unsupported-source placeholder | Existing eligible interpretation in both legacy URLs. Withdrawal denies the specific fact and dependent analysis while keeping independent conceptual operating activities. |
| `test_flora_banking_cohort_691.py` | Reading-mode selector; complaint fact hidden from insight; Nationwide Society count absent from Group view | Unified display with **explicit separate legal entity and period**, not a new aggregation. Restore existing cohort conditional mechanisms; complaint cohorts remain non-comparable. Withdrawal still removes facts and interpretation. |
| `test_flora_uxr1_650.py` | A1 exception required exactly one public Economics source accordion | Remove obsolete exception. The stronger original zero-research-controls assertion now applies there too; all access/privacy tests remain. |
| Existing A1 browser harness | Click Facts / FLORA Insight and expect public basis accordion | Verify selector absent, legacy URL equivalence, typed stage, close/history/reload and no basis accordion. Existing print/ARIA/Back withdrawal, invalid/private queries and zoom checks remain. |

Each is an explicit presentation-contract change. No test is deleted, skipped, mass-refreshed or marked expected-failing; no source/financial/access assertion is weakened to admit content. New tests exercise eight themes and independent-versus-dependent withdrawal, the unchanged owner gate (genuine/guest/forged/expired/revoked), direct HTTP denials and exact-cut rejection.

## Visual and architectural self-critique

Strength: reuse, rather than replacement. The premium images, header, Top / Left / Main frame, industry-specific stages and source owners survive. Native choices remove repeated accordion interaction; typed facts and interpretation can be understood in one place. The baseline/after renders visibly show the removed reading selector and evidence expanders.

Limitations: the recovered flagship is still a long editorial composition with several perspective choices, not a newly designed compact application. It inherits #712's prototype wording and illustrative operating maps. Combining previously separate content increases some pages' length; scoped caveats are intentionally retained. Do not call the result executive-ready solely because tests pass: the owner must judge commercial usefulness and visual density in the walkthrough. No unrequested visual design programme is started to address these judgments.

Public factual access does not imply private-run access or owner inspection. Detailed provenance remains restricted where it already was restricted. Legal attribution still uses the existing eligible-source collector. Canonical acceptance and Pipeline qualification remain separate. No new architecture/registry is necessary.

## Evidence limits and remaining decisions

- Current Render revision and live behavior are not verified. No production change was made.
- November 23 owner PDFs are unavailable here. Local baseline screenshots do not substitute for them; direct comparison remains open.
- Browser iPads are simulated (1194×834 and 834×1194); desktop is 1440×1000. Existing Economics checks additionally cover mobile, touch, keyboard, 200% zoom, print and ARIA withdrawal. Physical-device validation remains owner work.
- Final owner visual and implementation acceptance is required; the branch remains draft. Deployment and merge remain unauthorised.
- The unrelated main release-preflight/environment failure is documented, not bypassed or fixed by inventing infrastructure.
