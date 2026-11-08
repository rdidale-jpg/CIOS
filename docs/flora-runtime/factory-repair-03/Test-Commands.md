# Repair 03 verification commands

Use an existing Flora test environment (`python` below). No dependency changes are
required by this increment. W5 is the retained repository fixture; external W6 and
BNK paths must point to the actual retained archives. Tests assert SHA-256, not the
filename alone.

```bash
export PYTHONPATH=.
export FLORA_AUDIT_TEL_W6='/path/to/TEL-001_UK_Telecoms_Twin_Wave6_Targeted_Enrichment_Corrected_Flora_Import.zip'
export FLORA_AUDIT_BNK_W1='/path/to/BNK-001_UK_Banking_Financial_Services_Twin_Wave1_Manifest_Compatible_Flora_Import.zip'
export FLORA_REPAIR03_EVIDENCE='/tmp/flora-repair03/retained'
python docs/flora-runtime/factory-repair-03/run_regressions.py --output /tmp/flora-repair03/after
```

The runner separates all module data roots. The actual tests also isolate every
case with pytest `tmp_path`. Missing external archives produce explicit skips;
all three were accessible and tested in the recorded run.

Recorded final focused command (existing interpreter
`/workspace/cios-venv/bin/python`; isolated basetemp under
`/workspace/work/factory-repair-03-evidence`):

```bash
python -m pytest -q \
  tests/test_flora_factory_presentation_repair.py \
  tests/test_tel001_executive_enterprise_intelligence.py \
  tests/test_tel001_evidence_utilisation_key_reports.py \
  tests/test_industry_twin_semantic_reconciliation.py \
  tests/test_flora_blueprint_import_promotion.py \
  --basetemp=/tmp/flora-repair03/final-focused \
  --junitxml=/tmp/flora-repair03/final-focused.xml
```

Result: **63 passed**. Separate unchanged-profile/portable-contract run:

```bash
FLORA_DATA_DIR=/tmp/flora-repair03/contracts python -m pytest -q \
  tests/knowledge_packs/test_flora_blueprint_portable_contract.py \
  tests/test_researcher_twin_object_profile_contract.py \
  --basetemp=/tmp/flora-repair03/contract-pytest \
  --junitxml=/tmp/flora-repair03/contract-final.xml
```

Result: **17 passed**, one expected duplicate-ZIP-member warning from a rejection
fixture. A temporary profile edit caused checksum/version mismatch failures during
development; it was removed. The final source retains the original shared profile
and pack metadata. Final reruns supersede those intermediate failures.

Before comparison used a detached worktree at main
`cf7942fabb5f456f827c08f88e0d189a46ebc69f`, with only the new regression test file
and the corrected F09 assertion copied in. The runner was invoked by absolute path
from that worktree, with separate `before` temporary roots. The profile tests ran
separately on the same baseline. The final new test file was also rerun there after
the browser-discovered anchor assertion was added. Exact test IDs are compared in
`Regression-Comparison.json`; no failing tests were deselected or marked xfail.

`git diff --check` and `python -m compileall -q` for affected Flora packages, the
new regression module and the runner passed. The full repository suite was not
run. Existing failures in the chosen corpus remain explicit, not waived as green.

Browser smoke used the installed system Playwright/Chromium with the existing
`FloraWebHandler` on loopback, development test headers and the retained tests'
isolated data roots. No application startup migrations or production endpoints
were invoked. See `rendered/README.md` and `rendered/Browser-Evidence.json` for
navigation, captured sections and limits.
