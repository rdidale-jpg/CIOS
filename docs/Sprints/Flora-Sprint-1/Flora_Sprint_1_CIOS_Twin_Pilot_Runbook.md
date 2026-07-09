# Flora Sprint 1 — CIOS Twin Pilot Runbook

## Purpose
This runbook proves the governed Blueprint workflow with a CIOS Commercial Digital Twin package without committing the real MOD package or extracted material to GitHub.

## File to provide
Provide the accepted CIOS Commercial Digital Twin ZIP package. The ZIP must contain `blueprint_manifest.json` and the final Twin Spine workbook declared in the manifest as `final_twin_spine_workbook` or as a file with role `final_twin_spine_workbook` / `twin_spine`.

## Where to provide it
Place the real package in a protected local path outside the repository, for example:

```bash
/protected/flora-pilot/cios-commercial-digital-twin.zip
```

Do not copy the real archive, extracted workbook, PDFs, DOCX files or generated sensitive fixtures into this repository.

## What starts the pilot
Run the governed receipt, validation, review, dry-run, explicit promotion, Canvas and feedback checks from an operator shell with `FLORA_DATA_DIR` pointing at disposable local pilot storage:

```bash
export FLORA_DATA_DIR=/tmp/flora-cdt-pilot-state
python -m pytest -q tests/test_flora_cios_twin_pilot.py
```

For the real MOD package, use the same runtime entry points from an operator script that reads the archive from `/protected/flora-pilot/cios-commercial-digital-twin.zip`, records the SHA-256 checksum, calls `BlueprintPackageRegistry.receive(...)`, then `BlueprintPackageValidator.validate_and_stage(...)`, records review decisions, creates a dry-run plan, requires explicit promotion approval, opens `/digital-twins/{enterprise_id}/canvas`, validates lineage, submits governed feedback, repeats the run to confirm `repeat_no_change`, and writes a redacted report containing metadata only.

## Successful completion
Successful completion means:

- the package checksum is recorded;
- the immutable archive remains in Flora runtime storage and the source protected path remains outside Git;
- the final Twin Spine workbook is discovered;
- supported Evidence and Observation records are staged and promoted only after approval;
- analytical projections such as Pain Points remain non-canonical;
- the Enterprise Canvas shows imported intelligence;
- tile detail lineage reaches package, workbook, sheet and source record metadata;
- governed feedback is captured without direct canonical mutation;
- a second import/promotion returns duplicate or repeat/no-change behaviour;
- unauthorised import, Canvas and feedback access are blocked.

## Where the Canvas is opened
Open:

```text
/digital-twins/{enterprise_id}/canvas
```

Tile detail is available at:

```text
/digital-twins/{enterprise_id}/canvas/tiles/{tile_view_id}
```

## How to remove the package after testing
Remove disposable pilot state after the validation report is accepted:

```bash
rm -rf /tmp/flora-cdt-pilot-state
```

Also delete the protected source copy if the operator no longer needs it:

```bash
rm -f /protected/flora-pilot/cios-commercial-digital-twin.zip
```

Never use `git add` on real package material. Confirm before commit:

```bash
git status --short
git diff --cached --name-only
```
