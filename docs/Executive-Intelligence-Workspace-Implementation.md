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
## 2026-07-28 integrated imported-Twin vertical slice

The imported-Twin Executive Intelligence Workspace now resolves the authorised
principal's declared Commercial Mission from operational profile configuration,
semantically assembles staged candidates, excludes labels and incomplete metrics
from executive conclusions, and exposes Twin exploration and per-enterprise
dossiers. Mission fields remain explicitly human-supplied context and never
become Evidence or Enterprise Intelligence. Offer alignment remains incomplete
when no governed or explicitly supplied portfolio exists.

The implementation reuses Blueprint import receipt, staging, access, inspection
and candidate-governance owners. It also preserves the accepted ADR-014/ADR-024
boundary: the provider-backed Enterprise Intelligence Runtime retrieves governed
Enterprise Twin packages, so unpromoted candidates use the existing bounded
deterministic composition path. The UI records applied, bounded and skipped
reasoning stages rather than sending candidates through the governed retrieval
contract or creating a second provider summariser.

Authorities consulted were FP-012, FP-013, FP-014, WP2-003, ADR-014, ADR-024,
EIRP-001, FEIR-001, EI-001, EI-002, EI-004, accepted identity/import/human-
knowledge governance decisions, and the WP-011 Flora Runtime Capability
Baseline. ADR-014 and ADR-024 are accepted; FP-014, WP2-003, EIRP-001 and
FEIR-001 remain newer proposed authority. Consequently this slice is a
read-only runtime projection and operational profile configuration, not a new
canonical intelligence model or durable enterprise-IAM design.

There is no data migration. New configuration covers the current pilot users;
other authenticated principals safely receive no mission unless explicitly
configured. Object dates are shown when supplied, but staged packages with no
object-level freshness metadata remain `unknown`. Governed offer resolution and
a general candidate-capable provider retrieval adapter remain unresolved; the
runtime does not fabricate either.

Before this increment, raw names and values could be promoted visually as
conclusions, Commercial Mission was normally absent, and the imported Twin had
no enterprise index. Afterwards, only semantically eligible interpretations are
prominent; every assembled enterprise is navigable to a dossier with evidence,
lineage, confidence, freshness, Unknowns, Contradictions and governance routes.
