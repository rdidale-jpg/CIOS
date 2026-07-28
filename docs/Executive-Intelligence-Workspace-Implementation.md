# Executive Intelligence Workspace — import implementation

## Behaviour

After successful package parsing, the web import adapter redirects to the import
record. That route now opens a read-only Executive Intelligence Workspace. The
previous Import Inspect route remains at `/blueprint-import/{run}/inspect`, and
Candidate Review remains at `/blueprint-import/{run}/review`.

The workspace deterministically composes only package inspection metadata and
staged candidate records. It groups material conclusions by executive theme,
labels candidate and provisional interpretation explicitly, exposes provenance
and support on expansion, and aggregates missing context under Coverage and
Limitations. It does not persist narrative or mutate canonical memory.

When Commercial Mission context is absent, the brief is neutral and says that
personal commercial prioritisation has not been applied. Unsupported timing,
opportunities, evidence, identity, and scope remain limitations rather than
being inferred.

## Authorities and boundaries

The implementation applies FP-012, FP-013, FP-014 and WP2-003 through the
existing Twin Inspection, Blueprint Import candidate staging, evidence lineage,
identity resolution, and governance boundaries. In accordance with ADR-004,
ADR-005, ADR-012, ADR-013, ADR-014, ADR-015, ADR-023, ADR-024 and ADR-025, it
does not silently promote candidate intelligence, fabricate a recommendation,
or create a second canonical intelligence owner.

## Known limitations

- Composition quality is bounded by labels and fields actually supplied by the
  imported package.
- Reinvention Timing and Opportunity Hypotheses are shown only when candidate
  content explicitly supports them; no new scoring model is introduced.
- Commercial Mission metadata is consumed only when explicitly present in the
  package inspection model.
- Evidence inspection continues through the existing import diagnostics and
  Candidate Review rather than a new evidence store.
