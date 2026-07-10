# Migration: Blueprint owner import authority

Date: 2026-07-10

## Policy

The canonical Blueprint import capabilities remain:

- `package.upload` for package receipt and upload.
- `package.review` for validation inspection, candidate review, mapping and dry-run planning.
- `candidate.promote` for approval and canonical promotion execution.
- `blueprint_import_admin` as the existing Blueprint import administrative aggregate.

The `cios_owner` role is the highest operational authority in CIOS. Product sessions that carry `cios_owner` automatically inherit the Blueprint import capability set above. This is a role-policy backfill, so existing owner accounts receive the authority at their next session/policy evaluation without manual database edits or hidden user-specific grants.

## Runtime behaviour

Owner inheritance is enforced server-side by the Flora access helpers before Blueprint upload, validation inspection, review planning and promotion execution. The owner must still have access to the target enterprise or workspace (`X-Flora-Enterprises` containing the enterprise ID or `*`); cross-workspace import remains denied.

Unauthorised users should see: "You do not have permission to import Blueprints in this workspace." Owners should not be told to ask an administrator. If an owner is identifiable but owner-inherited authority is inconsistent, the UI should show an internal configuration error and the attempt should be audited for investigation.

## Safety and audit

Authorisation occurs before package registry writes, import-run creation, validation staging, dry-run planning or canonical promotion. Denied uploads leave no canonical changes, no import job and no retry package. Blueprint import audit events record actor, workspace/enterprise when known, effective roles, permission decision, stage, result and failure reason without logging package contents or secrets.
