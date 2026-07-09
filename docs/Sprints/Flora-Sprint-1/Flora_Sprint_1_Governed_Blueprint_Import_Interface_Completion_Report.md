# Flora Sprint 1 — Governed Blueprint Import Interface Completion Report

## What users can now do

Authorised users can open Flora, choose Import Blueprint, select a Commercial Digital Twin Blueprint ZIP from their computer, upload it, see validation status, review staged findings, review dry-run canonical effects, explicitly approve or decline promotion, and open the resulting Enterprise Canvas.

## Upload route and entry point

The product entry point is `/blueprint-import`. Uploads post to `/blueprint-import/upload` using a normal browser file chooser. Import history is available at `/blueprint-import/history` and import details are available at `/blueprint-import/{import_run_id}`.

## Validation and review experience

The validation result shows package identity, enterprise, package version, checksum, inspected file count, workbook/worksheet discovery where available, warnings, errors, and accepted/quarantined/rejected/unsupported counts. The review screen shows understandable dry-run totals for create, update, mapped-without-change, duplicate, conflict, unresolved and analytical-projection effects, with important exceptions inspectable.

## Approval behaviour

Uploading and validation do not mutate canonical memory. Promotion requires an authorised user to confirm the reviewed plan, confirm the expected mutation count, and provide an approval rationale before using the explicit **Approve and update governed Twin** action. Users may decline promotion, leaving canonical state unchanged.

## Security controls

The interface enforces authenticated upload, enterprise access, upload, review, promotion approval, promotion execution and history permissions through existing Flora product-session headers and Blueprint Import services. Server-side upload handling validates ZIP extension, MIME type, maximum size and archive safety through the existing governed receipt and validation boundary. User-facing failures avoid stack traces, internal storage paths and raw package content.

## Storage treatment

The original ZIP is preserved immutably by the existing Blueprint package registry/archive service in Flora governed runtime storage under the configured data directory. The ZIP is not unpacked into a public web directory, not executed, not written into the repository, and not committed to Git.

## Tests and results

Focused Blueprint Import interface tests cover authorised upload, unauthorised rejection, valid ZIP upload, invalid ZIP rejection, checksum display, immutable archive preservation, oversized/unsafe rejection paths through the receipt boundary, validation display, quarantine and unsupported summaries, dry-run effect display, explicit approval requirement, declined promotion, successful non-mutating promotion, Enterprise Canvas link, import history, no files written inside Git-controlled paths, no automatic canonical mutation on upload, and keyboard-operable form controls.

## Remaining gaps

The UI deliberately reuses PR1–PR9 services and does not recreate receipt, validation, staging, review, mapping, promotion, Canvas or lineage business logic. Rich per-record exception drill-down remains minimal and can be expanded in a later UX hardening PR.

## Confirmations

- Uploaded packages never enter Git and are preserved outside source control.
- Upload alone creates no canonical mutations.
- No MOD package bytes, contents, screenshots, fixtures or documentation excerpts were added.
