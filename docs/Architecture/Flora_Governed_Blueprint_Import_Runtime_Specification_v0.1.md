# Flora Governed Blueprint Import Runtime Specification v0.1

**Status:** Approved implementation baseline for Flora Sprint 1  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-09  
**Authority:** ADR-012, ADR-002, ADR-004, ADR-005, ADR-010  
**Applies to:** Flora runtime  
**Does not own:** Evidence, Observation, Enterprise Model, Knowledge Graph or Hypothesis semantics

## 1. Purpose

This specification defines how Flora receives, validates, stages, reviews and imports an accepted Commercial Digital Twin Blueprint package without treating the package, workbook or publication as automatic canonical Enterprise Memory.

Sprint 1 proves one bounded workflow using the accepted MOD Commercial Digital Twin v1.2 package.

The runtime must make it possible to:

- preserve the exact received package;
- understand which records it contains;
- identify what may map to existing CIOS objects;
- expose unsupported or contradictory content;
- accept valid records selectively;
- record every canonical effect;
- render the imported Twin through a governed Enterprise Canvas;
- navigate from a displayed judgement to supporting lineage.

## 2. Architecture boundary

### 2.1 This runtime owns

- Package Registry;
- Import Run;
- Package Adapter;
- Candidate Import Record;
- staging workflow;
- validation results;
- Import Mapping;
- acceptance decision;
- Canonical Promotion transaction;
- Import Ledger;
- package-level delta;
- import reversal;
- package and projection lineage;
- import completion and exception reporting.

### 2.2 This runtime does not own

- canonical Source or Evidence meaning;
- Observation definition or lifecycle;
- Enterprise Model canonical paths;
- Knowledge Graph edge meaning;
- Hypothesis or Recommendation semantics;
- Pain Point as a canonical object;
- publication approval;
- Provider Fit or pursuit logic.

Where an imported record cannot satisfy an owning contract, it remains staged, rejected or quarantined.

## 3. Governing principles

1. The immutable package is evidence of what was delivered, not itself canonical Enterprise Memory.
2. Every canonical mutation is explicit, attributable and reversible where safe.
3. Original stable IDs and package locations remain inspectable.
4. Identical re-imports are idempotent.
5. Runtime state, intelligence lifecycle state, freshness and domain measurement state remain separate.
6. Unknowns and Contradictions are preserved.
7. Human-supplied knowledge remains labelled.
8. Analytical projections remain views.
9. Import performs no silent research.
10. The MOD adapter must not define universal CIOS semantics.

## 4. Runtime components

### 4.1 Package Registry

Stores one immutable registration for each received package version.

Minimum fields:

```yaml
package_id: string
enterprise_id: string
twin_id: string
twin_version: string
parent_twin_id: string | null
profile_version: string
governing_contract_version: string | null
received_at: datetime
received_by: actor_id
effective_date: date | null
source_cutoff: date | null
package_sha256: string
archive_uri: string
manifest_uri: string
package_acceptance_state: received | validated | accepted_baseline | rejected | superseded
supersedes_package_id: string | null
```

The registry record does not imply canonical promotion.

### 4.2 Immutable Package Store

Stores:

- original archive;
- extracted files in a content-addressed or immutable area;
- original file names;
- checksums;
- generated receipt manifest;
- antivirus and archive-integrity results where available.

The runtime must never rewrite the original archive.

### 4.3 Import Run

Represents one attempt to process a package.

Minimum fields:

```yaml
import_run_id: string
package_id: string
adapter_id: string
adapter_version: string
initiated_at: datetime
initiated_by: actor_id
state: received | integrity_validated | parsed | staged | reviewed | partially_accepted | accepted | rejected | reversed | failed
completed_at: datetime | null
prior_import_run_id: string | null
summary_counts: object
failure_reason: string | null
```

An Import Run is not an Observation or reasoning object.

### 4.4 Package Adapter

A Package Adapter converts an external package format into the Candidate Import Record envelope.

Interface obligations:

```text
identify(package) -> adapter_match
validate_structure(package) -> structure_results
extract_manifest(package) -> normalised_manifest
enumerate_records(package) -> candidate_stream
resolve_source_location(candidate) -> package_location
report_adapter_limitations() -> limitation_set
```

Adapter output is candidate data only.

Sprint 1 adapter:

`mod_cdt_v1_2_adapter`

It must isolate MOD workbook sheet names and publication conventions from the generic workflow.

### 4.5 Candidate Staging Store

Holds parsed candidates before promotion.

Minimum envelope:

```yaml
candidate_id: string
import_run_id: string
package_id: string
external_id: string | null
record_class: string
truth_class: evidence_backed | inferred | human_supplied | analytical_projection | package_metadata | unknown
payload: object
source_file: string
source_location: string
content_fingerprint: string
validation_state: pending | valid | warning | invalid | quarantined
mapping_state: unmapped | proposed | mapped | ambiguous | unsupported
proposed_canonical_type: string | null
proposed_canonical_id: string | null
proposed_action: create | update | unchanged | conflict | contradiction | reject | quarantine
```

### 4.6 Mapping Registry

Preserves external-to-canonical identity.

Minimum fields:

```yaml
mapping_id: string
package_id: string
package_version: string
external_id: string
record_class: string
canonical_type: string
canonical_id: string
mapping_status: proposed | accepted | superseded | rejected
mapping_method: stable_id | owned_identity_rule | content_match | human_review
accepted_by: actor_id | null
accepted_at: datetime | null
```

A mapping must not create a new identity rule outside the owning object specification.

### 4.7 Validation Engine

Executes deterministic checks before promotion.

Validation groups:

#### Package integrity

- archive readable;
- file inventory complete;
- checksums match;
- no duplicate conflicting file names;
- required files present;
- package version recognised;
- archive and extracted files safe to process.

#### Structural integrity

- required worksheets or registers present for the adapter;
- stable-ID columns present where expected;
- duplicate external IDs detected;
- date fields parseable;
- required lineage fields populated;
- references resolvable within the package.

#### Semantic eligibility

- record class supported;
- truth class known;
- human knowledge labelled;
- Observation candidate has supporting Evidence;
- Evidence candidate has Source lineage;
- Enterprise Model candidate maps to an owned path;
- Contradiction references the claims or objects in tension;
- analytical projections are not proposed as canonical EI objects.

#### Delta and identity

- identical content recognised;
- existing mapping found;
- changed payload detected;
- prior canonical state located;
- conflicting identity reported.

#### Architecture protection

- no unowned canonical field;
- no unsupported enum;
- no lifecycle overloading;
- no publication paragraph promoted as an Observation;
- no Unknown converted into a negative fact.

Each result records severity, rule ID, object, message and remediation.

### 4.8 Acceptance Workspace

Allows an authorised user to:

- inspect package summary;
- inspect validation failures and warnings;
- compare package and current canonical state;
- filter by record class and proposed action;
- inspect source location;
- accept all eligible records;
- accept selected records;
- reject or quarantine records;
- record decision rationale;
- preview the Import Ledger.

A package may be accepted as a baseline while canonical promotion remains partial.

### 4.9 Canonical Promotion Service

Promotion must be transactional.

For each accepted candidate it must:

1. revalidate eligibility;
2. resolve the canonical target;
3. record prior state;
4. apply the create or update through the owning service;
5. create or update the Mapping Registry;
6. write an Import Ledger entry;
7. preserve package lineage;
8. fail safely without partially committing a grouped transaction.

The service must call existing canonical object services where they exist. It must not bypass owned validation by writing directly to persistence for convenience.

### 4.10 Import Ledger

One immutable entry per proposed or executed effect.

Minimum fields:

```yaml
ledger_entry_id: string
import_run_id: string
candidate_id: string
external_id: string | null
canonical_type: string | null
canonical_id: string | null
decision: accepted | rejected | quarantined | unchanged | conflict | contradiction
operation: create | update | no_op | compensating_reversal | none
prior_state_ref: string | null
new_state_ref: string | null
decision_by: actor_id
decision_at: datetime
decision_rationale: string | null
```

### 4.11 Analytical Projection Registry

Stores versioned view definitions and imported projection records.

Examples:

- pain portfolio;
- current-response view;
- residual-pain view;
- Burning Platform view;
- Transformation Pressure view;
- prioritisation view;
- executive publication reference.

Minimum fields:

```yaml
projection_id: string
projection_type: string
package_id: string
twin_version: string
external_id: string | null
title: string
summary: string | null
supporting_object_refs: array
source_location: string
effective_date: date | null
projection_status: imported | validated | superseded
```

These records are queryable view state, not new EI canonical objects.

### 4.12 Lineage Resolver

Resolves navigation from a rendered view to:

- projection record;
- supporting Hypothesis, mechanism or Enterprise Model state;
- Observation;
- Evidence;
- Source;
- original package file and location.

The resolver must make missing links explicit.

## 5. Import workflow

### Stage 1 — Receive

- upload or register archive;
- compute package checksum;
- store immutable archive;
- create Package Registry entry;
- create Import Run.

Failure outcome: reject before extraction where the archive is unreadable or unsafe.

### Stage 2 — Validate integrity

- extract to temporary processing area;
- compute file checksums;
- compare with supplied manifest;
- create generated receipt manifest;
- identify adapter.

Failure outcome: mark failed or rejected; do not stage records.

### Stage 3 — Parse

- adapter reads governed structured sources;
- records are converted into candidate envelopes;
- original locations are attached;
- adapter limitations are recorded.

Narrative documents may be indexed for reference but are not automatically converted into canonical candidates.

### Stage 4 — Validate candidates

- run structural, semantic, identity and architecture checks;
- assign validation and mapping states;
- create summary counts.

### Stage 5 — Stage and compare

- compare candidates with accepted mappings and canonical state;
- propose create, update, unchanged, contradiction, conflict, reject or quarantine;
- generate package delta.

### Stage 6 — Human review

- user inspects effects and source lineage;
- user accepts, rejects or quarantines;
- rationale recorded for overrides.

### Stage 7 — Promote

- apply accepted canonical mutations through owned services;
- register projections;
- write Import Ledger;
- update Import Run state.

### Stage 8 — Publish import result

Produce:

- completion summary;
- accepted-object counts;
- projection counts;
- unresolved mappings;
- rejected and quarantined records;
- Contradictions created;
- architecture gaps;
- effective Twin coverage;
- next recommended action.

## 6. Source-of-truth precedence

For the MOD pilot the adapter interprets package content in this order:

1. final Twin Spine workbook;
2. governed registers and ledgers;
3. manifest and validation records;
4. governed Commercial Digital Twin narrative;
5. Executive Brief and synthesis publications.

Precedence does not erase disagreement. A mismatch produces a validation warning or Contradiction candidate.

## 7. Sprint 1 supported record classes

### Canonical-eligible where contracts are satisfied

- Enterprise identity;
- Twin identity and version;
- Source;
- Evidence;
- Observation;
- unambiguous entity;
- unambiguous relationship candidate;
- Enterprise Model attribute candidate with an existing owned path;
- Unknown;
- Contradiction;
- human-supplied knowledge;
- refresh trigger;
- publication reference.

### Projection-only

- Pain Point;
- current response;
- response effectiveness;
- residual pain;
- Burning Platform;
- Transformation Pressure;
- priority and disposition;
- stakeholder hot button;
- solution pattern;
- executive thesis or publication section.

### Unsupported in Sprint 1

- Provider Fit;
- pursuit decision;
- opportunity value;
- award probability;
- inferred wallet share;
- autonomous recommendation;
- classified readiness;
- cross-enterprise benchmarking.

Unsupported content is retained in the package and reported, not silently discarded.

## 8. Idempotency

An identical package checksum and adapter version must produce no new canonical mutations after a successful prior import.

The runtime may create a new audit attempt only when explicitly requested, but it must report it as a duplicate Import Run.

For record-level idempotency:

- use accepted Mapping Registry entries first;
- apply owned canonical identity rules;
- use content fingerprints to detect unchanged payloads;
- report ambiguous identity rather than guessing.

## 9. Version delta

A newer package must compare against:

- prior package version;
- prior accepted candidate set;
- current canonical state.

Delta classes:

- added;
- changed;
- unchanged;
- removed from package;
- superseded;
- contradicted;
- unresolved.

Removal from a package does not automatically delete canonical state. It creates a review item because absence may reflect scope or publication change rather than retirement.

## 10. Reversal

A reversal is initiated against one completed Import Run.

The runtime must:

- identify ledger entries that mutated canonical state;
- detect later dependencies;
- propose compensating operations;
- require authorised confirmation;
- preserve package, mappings and ledger history;
- mark affected projections and Import Run as reversed;
- report operations that cannot safely be reversed.

## 11. Security and access

Sprint 1 must at minimum separate:

- package upload permission;
- package inspection permission;
- canonical promotion permission;
- reversal permission;
- human-knowledge contribution permission.

Future bid and procurement workspaces may require stricter document and object-level controls. Sprint 1 must not assume all Twin artefacts are public.

## 12. Failure behaviour

The runtime must fail visibly.

Examples:

- checksum mismatch → reject integrity validation;
- duplicate external ID with different content → quarantine and report;
- Observation without Evidence → invalid for promotion;
- unsupported canonical path → quarantine as architecture gap;
- ambiguous entity identity → require mapping review;
- package narrative contradicts structured state → warning or Contradiction;
- promotion transaction fails → rollback grouped transaction and preserve error;
- lineage target missing → display incomplete lineage rather than fabricate it.

## 13. MOD v1.2 adapter boundary

The adapter should use the accepted clean-release package and:

- register all files and hashes;
- identify the final Twin Spine;
- enumerate supported governed registers;
- import stable external IDs;
- register the 24-pain portfolio as projections;
- preserve the HSK incorporation state;
- index publication references;
- isolate worksheet-to-candidate mappings in adapter configuration;
- emit unsupported-sheet and unmapped-column reports.

It must not attempt to canonicalise all workbook sheets in Sprint 1.

## 14. Observability

Record:

- package size;
- file count;
- parse duration;
- candidate count by class;
- validation results by severity;
- proposed and accepted mutations;
- quarantine count;
- unresolved mapping count;
- lineage completeness;
- duplicate import attempts;
- promotion duration;
- reversal result.

Operational telemetry must not be confused with enterprise intelligence.

## 15. Acceptance criteria

Sprint 1 passes when:

1. The exact MOD archive is stored and its checksum verified.
2. A Package Registry entry and Import Run are created.
3. The MOD adapter stages supported record classes with original IDs and locations.
4. Unsupported records remain visible.
5. The user can preview canonical effects before promotion.
6. Identical re-import creates no duplicate canonical state.
7. A partial acceptance can be completed and reported.
8. Analytical projections are available to the Canvas without becoming canonical EI objects.
9. A displayed pain can navigate to supporting lineage and package location.
10. Unknowns, Contradictions and human knowledge remain distinguishable.
11. An Import Ledger records every decision.
12. A safe reversal is demonstrated on test data.
13. No new EI canonical field or lifecycle is introduced outside an owning contract.
14. Completion reports disclose architecture debt and unsupported mappings.

## 16. Deferred capabilities

- universal package exchange;
- automated semantic reconciliation;
- automated promotion;
- cross-enterprise deduplication;
- full graph import;
- CSM nested-Twin bid workspace;
- Provider Fit;
- opportunity scoring;
- real-time collaborative review;
- package export from Flora.

## 17. Validation plan

Required validation:

- unit tests for checksum, manifest, candidate envelope and mapping;
- adapter fixture tests;
- duplicate import test;
- changed-version delta test;
- partial-acceptance integration test;
- failed-promotion rollback test;
- reversal test;
- lineage-resolution test;
- architecture terminology review;
- manual inspection against the accepted MOD package;
- security permission tests;
- accessibility validation for acceptance views.

## 18. Completion report requirements

Each implementation PR must report:

- package fixtures used;
- candidate classes implemented;
- canonical services called;
- projection classes implemented;
- validation rules added;
- idempotency evidence;
- reversal evidence;
- unsupported mappings;
- architecture debt;
- screenshots or test evidence for the acceptance workspace;
- commit and PR details.

## Sprint 1 PR2 runtime note — validation and candidate staging

Flora now implements the bounded PR2 validation and staging layer on top of the PR1 package registry. The runtime validates the exact immutable archive recorded by PR1, verifies its checksum, compares `blueprint_manifest.json` identity fields with the registry record, discovers declared `.ndjson` record sets, and creates reviewable candidate import records under `blueprint_import/staging/{import_run_id}/`.

The staging layer is deliberately non-canonical. Every dry-run summary reports zero canonical mutations, and candidate records include `canonical_mutation_count: 0`. Projection-only records such as Pain Points, Burning Platforms and Transformation Pressures are retained as quarantined staging records, not promoted into new canonical object types. Unsupported classes such as Provider Fit remain visibly quarantined.

Validation findings are recorded on candidate records and in the staging summary. Valid records can be accepted into staging while unsupported, unresolved or malformed records are quarantined or rejected. Re-running validation against the same package reuses the existing staging summary and does not create duplicate candidate identities.
