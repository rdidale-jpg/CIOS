# Current Deployed Change Acceptance Report

## Non-technical status

- **Status:** Metadata incomplete until Render exposes a release marker/build metadata, or Ready for testing when the deployed build proves the stable change ID or source commit is included.
- **Should the Chief Architect test now?** The Import Twin panel answers this directly as **Yes** only when inclusion and candidate freshness are proven.
- **Reimport required:** **No** for the current operational panel change because changed components are classified as UI-only and diagnostics-only. Material import, adapter, semantic construction, Canonical Factual Projection, Observation runtime, owner assessment or Research Gap logic changes require reimport only when the candidate predates the material change.

## Deployment evidence

- Stable expected change ID: `TEL-001-CFP-SHARED-READ-CONTRACT-2026-08-05`.
- Expected source SHA: recorded as `source_commit_sha` in pilot metadata.
- Expected branch: `main`.
- Expected service: `flora`.
- Inclusion can be proven by deployed change marker, runtime build metadata, Git ancestry/containment, merge/squash mapping, or exact SHA fallback.

## Unresolved metadata

- Render service/repository/build/start/auto-deploy/status values are unknown unless exposed as runtime environment variables.
- Deployment timestamps may be unavailable on Render unless explicitly configured.
- Candidate runtime fingerprint is unavailable for old imports that did not persist it.

## Expected visible outcomes

- The Import Twin panel leads with **Status**, **Should I test now?**, and **Next action**.
- Technical SHA evidence is in a collapsed **Technical deployment evidence** section.
- Valid merge commits, squash commits, rebase/direct commits and later main commits no longer produce a false wrong-commit conclusion.
- Missing metadata degrades to **Metadata incomplete** rather than **Wrong deployed commit**.

## Merge gate

**MERGE WITH KNOWN LIMITATIONS** — status logic handles merge/squash/rebase/later-main cases and the panel gives clear non-technical instructions. Some Render metadata remains unavailable unless deployment environment variables expose it, but the panel degrades safely.
