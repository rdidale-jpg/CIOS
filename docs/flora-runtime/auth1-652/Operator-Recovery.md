# AUTH-1 — Render operator diagnosis and controlled recovery

These instructions require an authorised deployment operator. Codex has not executed them on Render. Do not post credentials, enrollment links, cookies, database files/rows, secret environment values, personal identifiers, private paths, backup contents or raw logs into GitHub/chat. A redacted diagnostic report may be shared through the owner's approved channel.

## 1. Establish the actual service and preserve evidence

In Render Dashboard, identify the service serving `flora-current.onrender.com`, its repository, tracked branch, deployed commit, start module and runtime OS user. Do not infer the service name from repository `render.yaml`. Compare `/deployment` and selected non-secret startup release/module information with the approved SHA. Record Auto-Deploy and hook settings without changing them. `FLORA_ENVIRONMENT=pilot` does not activate account authority; legacy pilot auto-login remains disabled.

Record only the effective `FLORA_DATA_DIR`, whether legacy `FLORA_PILOT_DIR` conflicts, the attached disk identity and exact mount path. Inspect those selected values privately; never dump the whole environment. Confirm the application root is on that actual disk. A `/var/data` prefix or `os.path.ismount` alone is not proof of the correct Render disk. Public `/health` is not authentication readiness.

**Use the existing service's runtime context.** Render disks are available only to that instance at runtime, not builds, pre-deploy commands, separate one-off jobs or another service. An inspection there could falsely report a missing store. [Render disk documentation](https://render.com/docs/disks) explains this distinction and ephemeral filesystem behaviour.

Before any recovery/configuration/permission change, preserve an independently protected, consistent backup and inventory of the existing authority **and** protected data, ACLs, Financial runs, audit and all SQLite/protected-journal sidecars. Verify restoration in isolation and protect the backup outside the service failure domain. A live `cp authority.sqlite3` is not a consistent database backup. Use a storage-aware consistent SQLite backup when healthy, with coordinated protected-file capture; for corrupted/unknown state first preserve the complete quiesced evidence without attempting repair. Retain original evidence. Render warns that custom databases need database-aware recovery; a disk snapshot alone is not a recovery qualification.

Do not remove/reinitialize a file, discard a journal, run `VACUUM`/checkpoint/recovery, change journal mode or reset accounts as a diagnostic. Do not attach a fresh disk over unknown existing files: that can hide the state being investigated.

## 2. Read-only checks, before any repair

Use the **reviewed AUTH-1 code** in an operator-controlled isolated checkout/runtime context. This is not permission to deploy it or change the running application. Verify its exact reviewed SHA. The script imports existing definitions without starting the web app or invoking storage initializers. Leave the service's actual root environment unchanged so mismatches are observable.

Set task-specific shell variables privately from independently verified Dashboard/inventory values:

```sh
auth1_verified_root='/operator-verified-existing-data-root'
auth1_verified_mount='/operator-verified-existing-disk-mount'
python -m cios.applications.flora.security_operator diagnose \
  --store "$auth1_verified_root/security/authority.sqlite3" \
  --expected-data-root "$auth1_verified_root" \
  --expected-mount "$auth1_verified_mount"
```

The first call performs metadata/header checks and refuses SQL with `quiescence_confirmation_required`. Earlier failures are reported first. It does not create a database or write probe. Do not substitute repository defaults for verified actual values.

For schema/count inspection, the operator must first coordinate a **quiesced context with no concurrent writers**—including authentication requests, service mutations and external scripts—or a verified consistent offline copy. Preserve public read availability only if that can be done without allowing writers. Do not kill/restart an unknown service or change its configuration merely to run a probe. This coordination needs operator control and a recovery plan. If it cannot be guaranteed, stop at metadata checks; do not add the flag.

Then, in that same verified context, repeat with `--quiesced`:

```sh
python -m cios.applications.flora.security_operator diagnose \
  --store "$auth1_verified_root/security/authority.sqlite3" \
  --expected-data-root "$auth1_verified_root" \
  --expected-mount "$auth1_verified_mount" \
  --quiesced
```

The flag attests quiescence; it does not perform shutdown, grant authority or permit recovery. Read-only SQLite still cannot establish writer readiness. If inspecting an offline copy, set `FLORA_DATA_DIR` **only for that isolated diagnostic process** to the independently verified copy root, use the same explicit expected root, and omit `--expected-mount` if it has no expected mount. This is not a service environment change. Label that report as a copy, not live Render evidence. Never point an inspection at a guessed alternative authority.

Privately retain root/mount, file existence/type, owner/mode, schema/inventory and protected-backup evidence. Check the aggregate enrolled-account, active-membership/workspace and ACL counts without sharing identities. Verify specific authorised bindings/resource ACLs in the existing operator process; counts alone cannot do that. `read_only_checks_passed` is not a successful-login or backup attestation.

## 3. Choose the narrow recovery from observed evidence

| Observation | Controlled action / stop condition |
|---|---|
| Configuration/root mismatch; expected mount not observed | Reconcile actual service, runtime environment, historical roots and disk identity first. Preserve all candidate existing state. An explicitly approved correction must reconnect the **verified existing** store/root; do not create a replacement disk/database or blindly switch to defaults. |
| Root, security directory or authority file missing | Determine whether inspection used the wrong instance/runtime/root, an unavailable disk, lost ephemeral state, or truly unprovisioned authority. Preserve known roots/backups. Missing does not mean safe to initialise. Restore only a verified consistent existing state under an approved recovery plan. |
| Ownership/private mode/type/symlink/hardlink failure | Confirm the correct service OS user and exact verified existing file. After protected backup, an operator may approve a targeted correction to the original owner's private directory/file boundary (normally0700/0600). No `chmod -R`, `chown -R`, world/group access or symlink workaround. Wrong owner may mean the wrong service/root; do not assume it is just a chmod problem. |
| Read-only/full filesystem, inode exhaustion or I/O error | Verify mount health/capacity privately. Preserve data and request controlled service/disk remediation. Do not delete authority, audit, canonical data or journals to make room. Existing governed storage recovery remains independently authorised and cannot be bypassed while authority is unavailable. |
| SQLite lock | Identify and quiesce the legitimate writer; inspect topology and nonparticipating processes. Retry the read-only observation only after that state changes. Do not remove lock/journal files or switch to in-memory/immutable SQLite. |
| SQLite sidecar/WAL, corruption, unrecognised schema, missing schema metadata | Retain database and all sidecars, compare verified backup/release/schema evidence and prepare a database-aware recovery. No schema guessing, migration, table creation or file recreation through this repair. Missing schema row now fails closed503; it is not repaired automatically. |
| Protected journal requires review | Retain complete journal/staging/completed evidence and protected root. Readiness does not replay it. Existing writer-locked, sealed-inventory recovery may be used only after independent backup/validation and explicit operator approval; never discard/reseal evidence to force access. |
| Accounts/memberships absent or incomplete | Check historical provisioning/inventory first. If independently proven never provisioned, legitimate activation requires a **separate authorised offline operator commission**: independently verified human/workspace bindings, reviewed plan, explicit apply, private password enrollment, resource ACL and protected backup. AUTH-1 grants none of these and supplies no replacement/default administrator. |
| Read-only checks pass but sign-in still fails | Writer availability, exact HTTPS `FLORA_PUBLIC_ORIGIN` (no trailing path/slash), cookies, effective account/member state and specific resource ACL still need authorised verification. Do not change credentials. An origin problem would affect POST verification; it does not by itself explain the reported GET storage503. |

## 4. Verify recovery using the existing owner account

Only after an approved recovery, use the owner's existing individual credentials in their own browser at the verified HTTPS origin. Confirm sign-in, explicit workspace selection, Owner/Member role, Banking access and Nationwide selection. Where legitimately absent, the existing **Prepare financial view** action requires Owner/upload authority, Banking resource ACL and CSRF/origin; it creates a private analytical run, never canonical Evidence. Do not perform that production write as a diagnostic without explicit owner authority.

Check Guest/forged/private-selector/foreign-workspace denials; source withdrawal is proved in isolation rather than by altering production source state. Reinspect the preserved inventory and audit continuity. Record the exact deployed SHA and actual successful owner journey in the approved operational record. **Until then, live restoration remains UNKNOWN.** Code CI, public Banking and a read-only report are insufficient.

## 5. Operational rollback

Keep privileged traffic closed if recovery fails. Retain the original disk/root, evidence and independently protected backup. Roll back only the explicitly approved configuration/code change under the operator's plan. Do not roll back authority independently of protected data/audit, restore revoked sessions, erase journals, initialise a replacement store or enable pilot auto-login. Database/data restoration needs a separately reviewed consistency and revocation plan, not an automatic code rollback.
