# AUTH-1 — Authentication storage diagnosis and bounded repair

Implements [Issue #652](https://github.com/rdidale-jpg/CIOS/issues/652) from main `836a4c29015c59117b873e6324c9618f7eb41930`; [post-merge CI passed](https://github.com/rdidale-jpg/CIOS/actions/runs/44043967254) before the implementation branch was created.

## Incident finding

**Live Render root cause: UNKNOWN. Live authentication repaired: NOT VERIFIED.**

The owner reported “Security storage unavailable” on `/auth/sign-in`. That is the existing503 response from `security_web.auth_get` for an operational security-store failure. It covers missing storage, ownership/mode violations, SQLite failures and protected-journal failures. `PermissionError` is also an `OSError`, so the message alone cannot distinguish those cases. It does not prove that the database was never provisioned, deleted, corrupted or unmounted.

Public Banking can work independently of the private authority. A readable public scene or successful `/health` storage-root probe does not establish an existing authority database, enrolled account, active workspace membership, resource ACL, writable SQLite or sign-in. `Guest` is the effective absence of verified workspace authority; no cosmetic role change can fix it.

Read-only attempts to inspect public Render `/auth/sign-in`, `/deployment` and `/health` were unavailable through both the web connector and this execution environment. No Render connector, service configuration, log, authority database or operator-supplied diagnostic was available. The owner's stated deployed SHA is not independent live deployment verification. Repository `render.yaml` declares a `/var/data/flora` disk/root but does not prove the effective service's configuration.

## Small code repair

Three narrowly scoped existing runtime/operator changes:

1. `SecurityStore.transaction`: SQLite PRAGMA setup now runs inside its existing cleanup envelope, so setup failure closes the connection. A missing schema-version row explicitly denies authority instead of raising an unhandled `TypeError`.
2. `ProtectedJournal.recover`: malformed UTF-8/JSON or a non-object manifest becomes a controlled storage error before validation/restore. Existing journal validation, writer lock, durable backup, restore and evidence-retention rules remain unchanged.
3. Existing offline `security_operator` gains `diagnose`, backed by `security_readiness`. No web diagnostic endpoint, new role, new authority producer or new storage owner is introduced.

The repair does **not** create a missing store, migrate schema, fix permissions, change roots/mounts, recover a journal, enroll an account or reset credentials. Existing authentication, Argon2 settings, sessions, workspace selection, ACLs, CSRF/origin, audit, Offers and Pipeline remain under their existing owners. No production/canonical data was changed.

## Operator-only diagnostic

[Operator recovery instructions](Operator-Recovery.md) define the sequence and stop conditions. The diagnostic accepts an explicit existing store and independently verified expected root; it detects configuration mismatch, missing root/directory/database, unsafe owner/mode/type/symlink/hardlink, observed mount mismatch, read-only/capacity conditions, pending protected/SQLite journals, read failures/locks/corruption, unrecognised schema/metadata and incomplete provisioning signals.

Only fixed codes, booleans and aggregate counts are returned. Paths, principals, workspace names, role contents, credentials, token/password hashes, audit payloads, database rows and exception text are not emitted. No public endpoint exposes the report. The OS user must satisfy the existing private-store ownership boundary; the tool does not grant authority.

SQL inspection requires explicit **operator-attested quiescence**. `mode=ro` alone does not guarantee an absence of ancillary WAL writes if another process changes journal mode concurrently. The tool refuses observed SQLite sidecars/WAL headers and pending protected journals; it does not use `immutable=1`, bypass locks, run startup write probes or recover/clean up evidence. Quiescence is an operator assertion, not a machine-proven fact.

`read_only_checks_passed` means only that those observations succeeded. Writer readiness, Render persistence, live authentication and specific workspace/Financial access remain `UNKNOWN`. Zero enrolled accounts/memberships or absent ACL records are warnings, not an invitation to invent a replacement Owner. Aggregate counts do not establish ownership or a correct specific ACL.

## Proof and review

[Validation](Validation.md) documents test commands and exact-head gates. [Previews and isolated HTTP proof](Previews.md) show the real unavailable state and the valid existing-authority journey; these are not production credentials or a claim of Render restoration. [Independent review](Independent-Review.md) records the security critique and limitations.

The original seven scenes, responsive variants, public intelligence and navigation are untouched. Source permissions, research history and private Financial run governance are unchanged. The existing source-withdrawal check still removes dependent financial output while retaining history.

## Rollback

Before integration, close/revise this draft; nothing live has changed. After separate approval and integration, revert the repair through protected GitHub review, then run full CI. This has no data/schema migration to reverse. Keep the existing authority, data root, ACLs, audit, sessions and all recovery evidence. Do not use an old database/snapshot to roll back code: doing so can restore revoked sessions or lose later audit/data. Do not return to pilot auto-login or pre-security access behaviour. A failed operational recovery must leave privileged traffic closed until the operator restores a verified consistent state under separate approval.

**Stop for owner review. No merge or Render deployment is authorised by this PR.**
