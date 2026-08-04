# Pilot Diagnostic Mode

Pilot Diagnostic Mode is temporary, read-only operational instrumentation for imported Twin validation.

## Enable

Set both environment variables before starting Flora:

```bash
FLORA_ENVIRONMENT=pilot
FLORA_PILOT_DIAGNOSTICS=1
```

`FLORA_ENVIRONMENT=test` or `FLORA_ENVIRONMENT=testing` is also accepted for automated tests.

## Disable

Unset `FLORA_PILOT_DIAGNOSTICS` or set it to any value other than `1`, `true`, `yes`, or `on`. Diagnostics are not rendered in normal executive output.

## Safety boundary

Diagnostics are labelled `PILOT DIAGNOSTICS — NOT EXECUTIVE OUTPUT`. They are read-only and explain the existing importer, semantic model, canonical-owner lifecycle, projection and template path. They do not promote candidates, alter governance, create TEL-001 mappings, change Research Gap rules, or calculate local completeness scores.
