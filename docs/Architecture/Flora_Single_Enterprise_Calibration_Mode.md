# Flora Single-Enterprise Calibration Mode

## Purpose

Single-enterprise calibration isolates the full Flora intelligence path for one governed enterprise:

```text
Authoritative source → Evidence → Observation → Enterprise Model → Observatory
```

It is intended for Digital Twin validation, not for adding enterprise-specific production branches.

## Enterprise scoping

A scoped run carries a canonical enterprise ID, display name, aliases, collection profile, permitted source IDs, run ID and collection mode. The first governed profile is `bt-group-plc` for BT Group plc.

## Identity resolution

Flora uses one resolver for enterprise identity. The aliases `BT`, `BT Group`, `BT Group plc` and `British Telecommunications` resolve to `bt-group-plc`. Evidence, Observation fingerprints, Observation persistence, Enterprise Model filenames, model lookup, Observatory-facing lookup and manifests use the canonical ID.

## Collection profiles

Profiles live in repository-native JSON under `config/flora/collection_profiles/`. The BT calibration profile is:

```text
config/flora/collection_profiles/bt-group-plc.json
```

Profiles are governed source plans. They are not canonical enterprise knowledge.

## Collection modes

Supported modes are:

- `live_authoritative` — only authoritative live evidence is accepted for scoring and memory projection.
- `live_plus_seeded` — compatibility mode for live evidence plus existing seeded fallback behaviour.
- `test_fixture` — deterministic fixture mode for tests.

The BT profile defaults to `live_authoritative`.

## Run manifests

Every scoped collection persists a manifest in `.flora_pilot/collection_manifests/<run_id>.json`. The manifest records run identity, profile, start/completion time, mode, planned/attempted/retrieved/rejected sources, accepted/rejected/downgraded Evidence, created/corroborated/rejected Observations, model attribute changes, Unknowns, Contradictions, errors and warnings.

The terminal and progress state report outcome counts instead of only a percentage completion message.

## Source authority

The BT profile records exact locators where available, publisher, source type, expected enterprise scope, collection purpose, authority tier, freshness expectation, enabled state and controlled pass membership.

## Seeded/live separation

`live_authoritative` excludes seeded, synthetic, fallback and non-selected human-supplied Evidence from live confidence and scoring. Missing source coverage remains visible through diagnostics and manifests. Collection completion does not imply model completeness.

## Reset and archive behaviour

Developer calibration reset is selective. `archive_and_reset_enterprise("BT", confirm="reset bt-group-plc")` archives the BT model and BT Observation references, rewrites the ledger preserving other enterprises, writes an audit file and removes only `bt-group-plc` projected state.

## BT pilot procedure

Baseline pass:

```bash
python -m cios.applications.flora.live.collect --profile bt-group-plc --mode live_authoritative --pass baseline
```

Change-event pass:

```bash
python -m cios.applications.flora.live.collect --profile bt-group-plc --mode live_authoritative --pass change_event
```

Recollection/idempotency pass:

```bash
python -m cios.applications.flora.live.collect --profile bt-group-plc --mode live_authoritative --pass recollection
```

Inspect lineage via the calibration inspection view or `inspection_rows("BT")` to see Evidence → Observation → Enterprise Model attribute mapping.

## Limitations

- The runtime remains file-backed JSON/JSONL; no database is introduced.
- PDF retrieval depends on current fetcher capabilities and remote access.
- The profile controls authoritative source targeting; it does not assert durable enterprise facts by itself.
- Broad autonomous web discovery remains out of scope.
- Score suppression is limited to excluding non-live provenance from live-authoritative collection and suppressing strong conclusions when model state is absent.
