# Codex Task — Install Flora Sprint 1 Architecture from Flat Staging Files

## Mission

Install the approved Flora Sprint 1 Architecture Package v0.1 from flat staging files already committed under:

`docs/Sprints/Flora-Sprint-1/`

Do not look for a ZIP archive. The ZIP is intentionally not present.

Use:

`docs/Sprints/Flora-Sprint-1/STAGING-INSTALL-MAP.json`

as the authoritative source-to-target map.

## Scope

This is a documentation and architecture installation task only.

- Move new files to their mapped targets.
- Reconcile the four mapped authoritative documents marked `reconcile`.
- Place package metadata under `docs/Sprints/Flora-Sprint-1/package/`.
- Remove all temporary flat staging files after successful validation.
- Create an installation report.

Do not implement runtime code.

## Required procedure

1. Read `STAGING-INSTALL-MAP.json`.
2. Verify that every listed `staging_file` exists in `docs/Sprints/Flora-Sprint-1/`.
3. Verify each staging file SHA-256 against the map.
4. Stop without changing files if any staging file is missing or any hash differs.
5. Inspect every target path before changing it.
6. Create missing target directories.
7. For entries with action `move`:
   - if the target does not exist, install the staged file unchanged;
   - if the target exists and is byte-identical, remove the staged duplicate;
   - if the target exists and differs, stop and report the conflict rather than overwrite it.
8. For entries with action `reconcile`:
   - compare the package candidate with the existing authoritative target;
   - preserve all existing content that is newer, unrelated or already authoritative;
   - integrate only the Flora Sprint 1 additions;
   - do not delete existing ADRs, terms, decisions or cross-references;
   - record the exact reconciliation in the installation report.
9. Remove obsolete `.gitkeep` files from directories that now contain real files.
10. Validate all Markdown and JSON files.
11. Remove the flat staging files, `STAGING-INSTALL-MAP.json`, this Codex task file and `FLAT-UPLOAD-README.md` only after successful installation.
12. Do not alter repository-root `README.md` or `CHANGELOG.md`.

## Controlled reconciliation targets

The following already exist and must not be overwritten wholesale:

- `architecture/decisions/README.md`
- `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md`
- `architecture/reference-architecture/Document-Map.md`
- `architecture/reference-architecture/Glossary.md`

The staged package candidates contain the intended Flora Sprint 1 additions concerning:

- ADR-012 and ADR-013;
- governed Blueprint package import;
- package acceptance versus object-level canonical acceptance;
- immutable package retention;
- staging, validation and canonical promotion;
- Enterprise Canvas;
- Enterprise Lenses;
- Intelligence Tiles;
- progressive disclosure;
- lineage navigation;
- uncertainty and freshness representation;
- the new runtime, import-profile, experience-standard and Canvas-pattern documents.

Integrate these additions without weakening or replacing existing authoritative content.

## Constraints

1. Do not change application code.
2. Do not change schemas, migrations, dependencies, tests or runtime configuration.
3. Do not alter EI-001, EI-002 or EI-012 semantics.
4. Do not add the MOD Twin or client-sensitive material.
5. Do not create a permanent package wrapper directory.
6. Do not leave staging candidate files in the final tree.
7. Preserve exact target filename capitalisation.
8. Do not silently resolve conflicting authoritative decisions.
9. Stop and report where safe reconciliation is not possible.

## Required final structure

Confirm these governed locations contain the installed documents:

- `architecture/decisions/`
- `architecture/reference-architecture/`
- `docs/Architecture/`
- `docs/Sprints/Flora-Sprint-1/`
- `docs/Sprints/Flora-Sprint-1/package/`

## Installation report

Create:

`docs/Sprints/Flora-Sprint-1/package/INSTALLATION-REPORT.md`

Include:

1. installation date;
2. staging files discovered;
3. SHA-256 validation results;
4. final target path for every package file;
5. files newly installed;
6. authoritative files reconciled;
7. exact reconciliation summaries;
8. conflicts found;
9. `.gitkeep` files removed;
10. staging files removed;
11. validation commands and results;
12. confirmation that no runtime implementation occurred.

## Validation

Run and report:

```bash
git status --short
git diff --check
find architecture/decisions \
     architecture/reference-architecture \
     docs/Architecture \
     docs/Sprints/Flora-Sprint-1 \
     -type f | sort
```

Also verify:

- all mapped target files exist;
- all new-file target contents retain the mapped SHA-256;
- package metadata is under `docs/Sprints/Flora-Sprint-1/package/`;
- repository-root README changed: no;
- repository-root changelog changed: no;
- application-code files changed: 0;
- runtime files changed: 0;
- existing files deleted: 0;
- temporary staging files remaining: 0;
- `git diff --check` passes.

## Acceptance criteria

Pass only when:

- every mapped package file has a governed destination;
- the package was not flattened in the final repository;
- duplicate README names are separated by directory;
- authoritative existing documents were reconciled, not replaced;
- all staging files have been removed;
- no runtime implementation occurred;
- the installation report accurately describes the result.

## Commit

Use:

`docs: install Flora Sprint 1 architecture package v0.1`

## Pull request

Create or update the documentation pull request titled:

`Flora Sprint 1: install governed import and Enterprise Canvas architecture`

## Completion report

Return:

1. final installed tree;
2. new files created;
3. files reconciled;
4. conflicts or decisions required;
5. validation results;
6. commit hash;
7. pull-request link or identifier;
8. confirmation that staging files were removed;
9. confirmation that no runtime code changed.
