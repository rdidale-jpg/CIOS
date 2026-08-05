# Current Deployed Change Acceptance Report

## Current change

- **Change ID:** TEL-001-CFP-SHARED-READ-CONTRACT-2026-08-05
- **Title:** Canonical Factual Projection shared read-contract consolidation
- **Purpose:** Make executive pages, diagnostics, Research Gaps and owner-assessment inputs consume one governed Canonical Factual Projection or explicitly governed derivative.
- **Expected merged implementation SHA:** `88f053e6cee6fe2fef7feba1e7f4553194b7a040`
- **Deployed SHA:** runtime value from `deployment_metadata().commit_sha`, displayed on `/blueprint-import`.
- **Deployed branch:** runtime value from `deployment_metadata().branch`, displayed on `/blueprint-import`.
- **Deployment/build timestamp:** runtime value from `deployment_metadata().build_timestamp`, displayed on `/blueprint-import`.
- **Runtime version:** runtime value from `deployment_metadata().deployment_version`, displayed on `/blueprint-import`.
- **Wrong-commit gate:** if the deployed SHA does not match the expected implementation SHA, the panel displays `WRONG DEPLOYED COMMIT` and does not claim the functionality is available.

## Repository evidence summary

- `cios/applications/flora/blueprint_import/canonical_factual_projection.py` defines the shared Canonical Factual Projection read model, executive-safe value formatting, projection versions and runtime fingerprint.
- `cios/applications/flora/blueprint_import/executive_workspace.py` consumes that projection or explicit governed derivatives for Industry Overview, Enterprise Dossiers including BT Group, Market Participants, Major Programmes, Opportunities, Reinvention, Research Gaps and Advanced Diagnostics.
- `cios/applications/flora/blueprint_import/views.py` exposes deployment metadata, import timestamp and runtime fingerprint evidence so operators can identify stale candidates before judging output.
- The TEL-001 fixture remains unchanged.

## Expected visible outcomes

### Industry Overview

- Supplied industry facts should render in executive-friendly sections.
- Raw dictionaries and Python-style lists should not appear.
- Diagnostics should report the same Evidence, Unknowns and Contradictions as the page.

### BT Group Enterprise Dossier

- Supplied operating model, suppliers, Evidence, Unknowns and Contradictions should remain visible.
- Owner-assessment sections must distinguish “fact present but assessment pending” from “fact absent”.
- Research Gaps must not request the entire dossier where facts already exist.

### Market Participants

- Existing role, capability, relationship, activity and Evidence output should remain unchanged.

### Major Programmes

- All 13 programmes should remain visible.
- Summary, stage and Evidence should remain visible.

### Opportunities

- Exactly 17 opportunities should remain visible.
- Supplied customer, problem, timing and commercial fields should render where present.

### Reinvention

- All seven source records must have an explicit visible disposition.

### Research Gaps

- Supplied facts must not be described as wholly absent.
- Assessment pending must not be presented as missing research.

## Exact operator test

1. Confirm this panel shows the currently deployed SHA.
2. Confirm whether Flora says a fresh import is required.
3. Import the unchanged TEL-001 ZIP if required.
4. Open Industry Overview.
5. Open BT Group.
6. Open Market Participants.
7. Open Major Programmes.
8. Open Opportunities.
9. Open Reinvention.
10. Open Research Gaps.
11. Open Advanced Diagnostics.
12. Compare the visible results against the checklist above.

## Fresh-import decision

The Import Twin panel calculates and displays exactly one of:

- Fresh import not required
- Fresh import required
- Cannot determine — deployment metadata missing

The decision uses deployed commit SHA, deployment timestamp, latest TEL-001 import timestamp, candidate runtime fingerprint and current runtime fingerprint.

## Automated validation results

- **TEL-001 fixture checksum:** `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`
- **Expected checksum:** `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`
- **Checksum status:** PASS
- **End-to-end test status:** PASS — `tests/test_tel001_blueprint_import_regression.py`
- **Rendered-route test status:** PASS — `tests/test_flora_blueprint_import_interface.py::test_upload_page_shows_current_deployed_change_acceptance_panel`
- **Diagnostics reconciliation status:** PASS — repository TEL-001 diagnostics assertions passed in this Codex run.
- **Research Gap reconciliation status:** PASS — repository TEL-001 Research Gap assertions passed in this Codex run.
- **Known failing tests:** None in required acceptance subset run for this panel change.
- **Last validation timestamp:** 2026-08-05T00:00:00Z

## Known limitations

- Operator validation cannot be inferred from repository tests and remains NOT TESTED until a human records PASS, PARTIAL or FAIL outside this repository-owned metadata.
- Fresh-import guidance is `Cannot determine — deployment metadata missing` when deployment timestamp, latest TEL-001 import timestamp, candidate runtime fingerprint or current runtime fingerprint is unavailable.
- Rendered-route tests prove the acceptance panel content is visible; they do not prove a live Render deployment has been manually inspected.
- Owner assessment and promotion remain governed external authorities; this change preserves candidate factual display but does not auto-authorise recommendations.

## Merge gate

**SAFE TO MERGE** when the panel is visible, current, accurate, shows the deployed SHA, includes required operator steps, links to every required test page, and the rendered-route test passes without semantic runtime file changes.
