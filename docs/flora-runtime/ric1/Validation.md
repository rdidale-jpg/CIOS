# Reproducible validation and limits

Run from the RIC-1 worktree with the project's Python3.12 dependencies installed:

```sh
python docs/flora-runtime/ric1/research-tools/consolidate.py
python tools/research/ric1_validation.py
python -m pytest tests/test_flora_ric1_research_acceptance.py -q
python docs/flora-runtime/ric1/research-tools/import_dry_run.py
python -m unittest discover -s tests/ci -v
PYTHONPATH=. python tools/ci/flora_ci.py --output /tmp/ric1-final-ci
```

Consolidation reads three immutable unmerged Git inputs, so fetch repository history including their branches first; checkout is based on validated main, not either research PR. The dedicated read-only research workflow checks those commit objects explicitly and tests the PR head SHA. The existing full FLORA workflow is triggered by additive tests/tools changes; its gate, baseline and security tests are unchanged. Hosted conclusions and exact tested SHA belong in the final PR validation comment/completion report once runs finish; a workflow configuration is not a passing run.

Research QA checks lossless source/claim identities and aliases, original inspection dates/rights/extent, no invented original-file hashes, financial sign/basis/period/entity, atomicity, A–E boundaries, eight stable issue identities/twelve versions, all preserved gaps, sector partial coverage, pinned owner bytes, negative cases and deterministic consolidation. It executes pinned RIE-2 financial/customer/peer reconciliation checks, including statutory/APM bridges, represented comparators, insurer/bank boundaries and FOS/FCA period separation. Negative tests corrupt individual fields and must fail. This proves internal consistency and guarded classifications, not independent source completeness.

The isolated rehearsal uses the **actual** proposed NDJSON, existing Researcher adapter and receipt/staging/planning services in a temporary directory. It verifies lossless source payloads, all eight atomic statements, compound quarantine, analytical projection retention, unresolved unreviewed Evidence/Observations, repeated-plan idempotency and denied cross-workspace inspection/planning. It uses the repository's explicit SERVICE-TEST context double, not a real login/HTTP/production identity. It records no review, approval or canonical action. The normal388-test strict suite remains the broader HTTP/authentication/security assurance.

Three original tables were freshly inspected via the approved web tool on15November2026. Selected factual rows and source locators are retained; no original PDF/HTML bytes or original-source hash was available, and no whole-file redistribution rights are asserted. Numeric survey labels were not visually verified and remain excluded. Other research source records retain earlier inspection cutoffs and outstanding B decisions. Financial arithmetic does not independently verify issuer reporting.

Production health/import history could not be retrieved through the available read-only service. Live imports, Evidence decisions, deployed revision and model projection are **UNVERIFIED**. Owner-executable read-only checks are in Production-Verification; no service-test result substitutes for them. No full production readiness or ingestion GO is claimed.
