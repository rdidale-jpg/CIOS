# Flora persistent pilot storage: inode recovery

## Ownership and layout

Flora's shared filesystem JSON adapter owns atomic replacement writes. A successful
update replaces the destination through one uniquely named temporary file; it does
not create a version. The helper removes its temporary name in `finally`, although a
process or node termination can leave a hidden `*.tmp` name.

Blueprint receipt stores one immutable archive per package checksum, one package
record and one import-run record. Archives are inspected in memory and are not
unpacked into persistent workspaces. A failed receipt removes only the new archive
and run that it owns. Its audit ledger is append-only but occupies one inode.

The canonical high-file-count owner is Blueprint candidate staging: each discovered
candidate is one JSON file under
`blueprint_import/staging/<run>/candidates/`. Restaging also copied every candidate
into every `blueprint_import/staging_history/<run>/<version>/candidates/` directory.
Those superseded, non-canonical snapshots had no retention bound, so repeated
restaging multiplied the candidate file count. They are the repository-proven
unbounded file family; production inventory is still required to prove which family
filled the deployed 65,536-inode filesystem.

## Persistence classification and cleanup boundary

| Class | Examples | Automatic removal | Retention | Canonical owner |
|---|---|---:|---:|---|
| Canonical / required | `memory/evidence.jsonl`, observations, contradictions, enterprise models; promoted Twin governance and promotion ledgers; immutable received archives, package records and audit | **No** | Yes | Memory repositories, promotion repository, package registry/archive and audit ledger |
| Candidate / import | Active staging candidates, summaries, live reviews, plans, mappings and import runs | **No** while live | Yes | Blueprint import repositories |
| Derived / regenerable | Financial packet/AI caches, publications and architecture exports | Not by this recovery tool | Product-specific | Their financial intelligence/publisher/export owners |
| Diagnostic / operational | Financial diagnostic/run records, restage job status and application logs | Not by this recovery tool | No policy proven | Their runtime owners |
| Temporary / transient | Atomic-write `*.tmp` and write probes | Architecturally disposable, but this recovery tool only reports them | No | Shared storage adapter |
| Superseded / historical | `blueprint_import/staging_history` snapshots | **Yes**, except the newest two versions per import | Two-version rollback window | Blueprint restage service |

The cleanup implementation is path-locked to `blueprint_import/staging_history`.
It cannot reach active staging, governed Evidence, enterprise models, package
archives, audit, reviews or promoted intelligence. Diagnostics and temporary files
are counted but deliberately not deleted without a separately proven age/ownership
policy.

## Read-only production inspection

Run inside the deployed Flora container with the production volume mounted:

```bash
python -m cios.applications.flora.storage_maintenance > /tmp/flora-storage-inventory.json
```

The report reads directory entries and metadata only, never contents. It includes
total files, top-level and determinable record-family counts, the 20 largest
file-count directories, temporary/diagnostic/candidate-history counts, timestamps,
and byte/inode filesystem facts. `/tmp` must not resolve onto the exhausted Flora
volume; print directly to the operator console if it does.

Preview the exact governed cleanup scope:

```bash
python -m cios.applications.flora.storage_maintenance \
  --cleanup-superseded-staging --keep-versions 2
```

If `blueprint_import/staging_history` is a material consumer, apply only that cleanup:

```bash
python -m cios.applications.flora.storage_maintenance \
  --cleanup-superseded-staging --keep-versions 2 --apply
```

Then rerun the inventory and `/health`. Do not retry an import until health reports
ready and available inodes meet `FLORA_MIN_AVAILABLE_INODES` (default 128). If the
inventory does not find enough removable staging history, do not delete arbitrary
files: increase the persistent volume's inode capacity or migrate it to a filesystem
with an adequate inode allocation.
