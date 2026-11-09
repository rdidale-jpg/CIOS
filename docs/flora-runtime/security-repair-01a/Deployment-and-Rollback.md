# Security Repair 01A deployment safety and rollback plan

This is a plan only. Do not deploy, merge, provision or change Render settings as
part of this PR. Repair 01B is not authorised by the 01A implementation request.

## Prerequisites and read-only checks

The trusted deployment operator verifies the exact existing service, repository,
branch, deployed commit, startup module, disk mount and effective FLORA_DATA_DIR.
The repository's render.yaml is not evidence of actual Render settings. No
production SHA, mount or owner binding has been verified by this repair.

Keep the disk and existing root unchanged. Take an independently protected backup
of import, canonical, ACL and audit state. Recover existing identities/workspaces
read-only; retain Unknowns and do not derive ownership from deployment control.

## Closed 01A rollout after separate human approval

1. Review the source diff, security cases, exact-case regressions and limitations.
2. Verify the existing disk/root and record a predeployment manifest.
3. Deploy the approved 01A SHA with the canonical module
   `python -m cios.applications.flora.web.app`; do not switch roots or reset data.
4. Read /deployment and verify commit/module and
   `pilot_import_mode=disabled-security-repair-01a`.
5. Check public Banking, source discovery and the closed sign-in notice.
6. Verify forged/anonymous protected reads deny without disclosing data.
7. Verify legacy cookies/header flags cannot grant authority. No real upload,
   approval, deletion, recovery or promotion is part of this smoke test.
8. Reinspect existing records read-only against the predeployment manifest.

No new variable is required to keep 01A closed. Existing legacy authentication,
auto-sign-in and proxy-header flags cannot enable privilege. This PR changes no
Render environment variables. FLORA_PUBLIC_ORIGIN optionally permits only the
non-authority reference-navigation preference POST with exact Origin; absence
keeps that POST closed. It never enables privileged operations.

## Activation dependencies for 01B

Separate implementation authorisation and reviewed architecture are required.
Then verify human/account/workspace binding; offline operator provisioning;
transactional membership/audit persistence; individual credentials/enrollment;
revocable sessions; eight-hour absolute/thirty-minute idle policy validation;
workspace selection and revocation; resource ACL intersection; recent
reauthentication; CSRF/origin controls; protected independent bootstrap backup;
full isolated owner review/promotion/logout journey; negative tests and explicit
human production-activation approval. Existing shared pilot acknowledgements
must not be upgraded or reattributed. No existing candidate is automatically
accepted. Do not create production credentials during 01A review.

## Rollback

Stop privileged traffic first. A rollback must retain these trust-boundary
controls or serve a closed maintenance response. Do not restore a release that
accepts unsigned identity/role cookies, shared auto-owner sessions or public
mutation dispatch. Keep the disk, intelligence, import history and audit records.
Do not restore revoked sessions from a snapshot when 01B later exists. There is
no 01A security database or migration to reverse.

## Assurance limitations

01A intentionally makes legacy privileged workflows unavailable. No verified
owner journey exists yet. Some formerly unauthenticated dashboards and the
alternate local workspace listener are also closed. Public source routes remain
available. Local policy/HTTP evidence is not deployed-origin verification.
Independent protected backup provides operational assurance; enterprise immutable
archives and multi-party attestation are deferred under the approved amendment.
