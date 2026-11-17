# Independent security architecture critique

An explicitly authorised separate review agent inspected the Issue #652 baseline, call paths, proposed diagnostic, runtime diff, fault tests, browser-proof code and operator documentation. This is implementation critique, not an owner's operational approval or a live security audit.

## Findings resolved

| Finding | Disposition |
|---|---|
| The generic503 cannot identify a missing database specifically; PermissionError is an OSError. | Report actual Render cause UNKNOWN. Separate finite operator observations without publishing details to Guest. |
| transaction/preauth/startup probes and protected recovery are not read-only. | Diagnostic invokes none of them and does not bootstrap, write-probe, recover, clean up or grant authority. |
| Early PRAGMA failure leaked its connection; absent schema row and malformed journal JSON could escape controlled failure. | Existing cleanup envelope includes setup; explicit missing-row denial and manifest parse/type guard retain fail-closed behaviour and evidence. |
| mode=ro alone cannot guarantee zero ancillary writes under concurrent WAL changes. | Refuse observed sidecars/header-WAL; SQL requires operator-attested quiescence. No immutable bypass. Documentation explicitly limits that attestation and no-write proof. |
| Invalid home/environment configuration could escape the finite report. | Sanitized configuration/error fallback; no exception/row/path material in output. |
| Schema check omitted unexpected trigger/view/index objects; LIKE underscore wildcard could hide non-system names. | Compare schema1 objects against the existing owner's DDL, using literal-underscore GLOB filtering for SQLite internals. Unknown schema is not migrated. |
| Offline-copy root handling could be confused with changing service configuration. | Only isolated diagnostic-process FLORA_DATA_DIR may identify a verified offline copy; the live service environment is left unchanged. Copy report is not live evidence. |

## Independent results and limits

The reviewer independently ran the45 functional AUTH-1 cases successfully, including real process-interrupted journal retention. The later one-path security-owner compatibility record and unknown-change rejection were also independently reviewed; all four targeted compatibility checks passed. No remaining code/documentation blocker was found. The reviewer inspected the110-check browser harness but did not personally rerun it. Parent/hosted execution and full388 security/comparator results are separately required at the final SHA.

Existing schema/provisioning, membership/resource/source permissions, writer/recovery protocol and public visuals remain with their original owners. No new authority producer, canonical engine, Render mutation or credential change was approved.

**Live root cause, writer readiness and owner authentication on Render remain UNKNOWN.** Exact-head CI and owner review are the final code-review gates; actual Render service/root observations and any recovery remain separately controlled operator work.
