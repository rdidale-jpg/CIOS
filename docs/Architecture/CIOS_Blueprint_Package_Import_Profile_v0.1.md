# CIOS Blueprint Package Import Profile v0.1

**Status:** Approved exchange profile for Flora Sprint 1  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-09  
**Authority:** ADR-012  
**Purpose:** Define the minimum package metadata, record envelopes and referential rules required for governed Blueprint import.

## 1. Scope

This profile standardises the boundary between an external Commercial Digital Twin Blueprint package and Flora's import runtime.

It does not redefine CIOS canonical object semantics.

The profile supports two modes:

1. **Profile-native package** — contains a conforming machine-readable manifest and record exports.
2. **Legacy governed package** — contains accepted structured artefacts such as a Twin Spine and documents. A Package Adapter generates a Normalised Receipt Manifest without altering the archive.

The accepted MOD v1.2 package is the first legacy governed package.

## 2. Package principles

A package must be:

- identifiable;
- immutable after receipt;
- versioned;
- bounded by enterprise, effective date and source cut-off;
- explicit about governing standards;
- explicit about file inventory and checksums;
- explicit about truth class and lineage;
- capable of partial import;
- capable of delta comparison;
- honest about unsupported or missing fields.

## 3. Package layout

A profile-native package should use:

```text
/
├── package-manifest.json
├── records/
│   ├── sources.ndjson
│   ├── evidence.ndjson
│   ├── observations.ndjson
│   ├── entities.ndjson
│   ├── relationships.ndjson
│   ├── enterprise-model-candidates.ndjson
│   ├── unknowns.ndjson
│   ├── contradictions.ndjson
│   ├── human-knowledge.ndjson
│   ├── refresh-triggers.ndjson
│   └── analytical-projections.ndjson
├── publications/
├── structured/
└── supporting/
```

Not every record file is mandatory. The manifest must declare what is present.

A legacy package may use its existing layout. Flora records the adapter and adapter version that interpreted it.

## 4. Manifest

### 4.1 Required fields

```json
{
  "profile_version": "0.1",
  "package_id": "string",
  "package_type": "commercial_digital_twin_blueprint",
  "enterprise_id": "string",
  "enterprise_name": "string",
  "twin_id": "string",
  "twin_version": "string",
  "parent_twin_id": null,
  "effective_date": "YYYY-MM-DD",
  "source_cutoff": "YYYY-MM-DD",
  "created_at": "ISO-8601",
  "created_by": "string",
  "acceptance_state": "candidate|accepted_baseline|superseded",
  "governing_contract_version": "string",
  "governing_architecture": ["string"],
  "supersedes_package_id": null,
  "files": [],
  "record_sets": [],
  "known_limitations": []
}
```

### 4.2 File entry

```json
{
  "path": "structured/twin-spine.xlsx",
  "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "sha256": "hex",
  "role": "governed_structured_state",
  "required": true,
  "authoritative_precedence": 1
}
```

Recommended roles:

- governed_structured_state;
- governed_register;
- package_manifest;
- validation_record;
- governed_narrative;
- executive_publication;
- evidence_appendix;
- supporting_material.

### 4.3 Record-set entry

```json
{
  "record_class": "observation",
  "path": "records/observations.ndjson",
  "count": 123,
  "schema_version": "owned-contract-version",
  "truth_classes": ["evidence_backed"],
  "required": false
}
```

## 5. Candidate record envelope

Every record exported for import should use:

```json
{
  "external_id": "OBS-MOD-0001",
  "record_class": "observation",
  "truth_class": "evidence_backed",
  "payload": {},
  "source_location": {
    "file": "MOD-CDT-01-Twin-Spine-v1.2.xlsx",
    "section": "Observations",
    "locator": "OBS-MOD-0001"
  },
  "supporting_refs": ["EVD-MOD-0001"],
  "contrary_refs": [],
  "effective_from": "YYYY-MM-DD",
  "effective_to": null,
  "observed_at": "ISO-8601",
  "freshness": null,
  "confidence": null,
  "human_knowledge": null,
  "content_fingerprint": "sha256"
}
```

Fields that do not apply remain absent or null. The envelope does not authorise a field to become canonical; the owning object contract still applies.

## 6. Truth classes

Supported profile truth classes:

- `evidence_backed` — supported directly by governed Evidence or accepted Observation lineage;
- `inferred` — derived and explicitly labelled;
- `human_supplied` — contributed by a named or governed human source and dated;
- `analytical_projection` — a view derived from governed state;
- `package_metadata` — delivery, version or validation metadata;
- `unknown` — an explicitly represented absence of knowledge.

A package must not label a Recommendation, inference or human statement as Evidence.

## 7. Supported record classes

### 7.1 Canonical-eligible candidate classes

| Record class | Owning architecture | Minimum import rule |
| --- | --- | --- |
| enterprise | EI-001 | Stable identity and scope |
| twin | EI-001 / ADR-002 | Enterprise, version and effective boundary |
| source | FP-004/006 | Attributable permissible source |
| evidence | FP-004 | Source lineage and exact location |
| observation | EI-012 | Atomic fact, Evidence support, no speculation |
| entity | EI-001/EI-002 | Owned type and identity |
| relationship | EI-002 | Typed endpoints, provenance, time and confidence |
| enterprise_model_candidate | EI-001 | Existing owned path and attribute governance |
| unknown | EI-012 / future EI-015 | Clear missing knowledge and consequence |
| contradiction | EI-002/EI-012 | Claims or objects in tension |
| human_knowledge | ADR-004 | Contributor, date, scope and effect |
| refresh_trigger | Runtime view | Event and affected state |
| publication_reference | Runtime layer | Exact Twin version and files |

### 7.2 Projection-only classes

| Projection class | Meaning |
| --- | --- |
| pain_point | Governed statement of a material enterprise pain |
| current_response | What the enterprise is doing about a pain or pressure |
| response_effectiveness | Evidence-backed assessment of whether a response works |
| residual_pain | What remains unresolved |
| burning_platform | Derived urgent-pressure classification |
| transformation_pressure_view | Derived pressure view |
| priority_disposition | Why a candidate was selected, nested, deferred or rejected |
| stakeholder_hot_button | Stakeholder-specific consequence or concern |
| solution_pattern | Provider-neutral response pattern |
| executive_publication | Rendered report or brief |

Projection-only does not mean unimportant. It means the record is stored and rendered as a versioned view rather than promoted to a new canonical EI object.

## 8. Lineage requirements

### 8.1 Source and Evidence

An Evidence candidate must reference a Source and exact source location.

### 8.2 Observation

An Observation candidate must reference at least one Evidence item unless the owning Observation rule explicitly permits another governed origin. Human-supplied knowledge must not masquerade as Observation Evidence.

### 8.3 Enterprise Model candidate

Must reference:

- owned canonical path;
- supporting Observation or governed source;
- effective period;
- truth class;
- confidence or limitation where required.

### 8.4 Relationship

Must reference:

- from entity;
- relationship type;
- to entity;
- supporting Evidence or Observation;
- effective period;
- truth class;
- confidence;
- contradiction state where applicable.

### 8.5 Analytical projection

Must reference one or more supporting governed objects or explicitly state that lineage is incomplete.

## 9. Identity and stable IDs

External stable IDs must be unique within:

`package_id + record_class`

A newer package should preserve stable IDs for unchanged conceptual records.

Flora canonical IDs are separate. Mapping must preserve both.

Packages must not change an external ID merely because wording changed. They should create a new ID where the underlying conceptual record changes materially.

## 10. Dates and time

Packages should distinguish:

- created date;
- observed date;
- effective date or period;
- source publication date;
- source cut-off;
- last reviewed date;
- expiry or refresh trigger.

A package-wide effective date must not imply that every record has the same freshness.

## 11. Human-supplied knowledge

Minimum fields:

```json
{
  "external_id": "HSK-MOD-0001",
  "record_class": "human_knowledge",
  "truth_class": "human_supplied",
  "payload": {
    "statement": "string",
    "contributor": "string or governed pseudonym",
    "contributed_at": "ISO-8601",
    "scope": "string",
    "effect_on_reasoning": "string",
    "validation_need": "string|null"
  }
}
```

## 12. Unknown and Contradiction

### Unknown

Should state:

- what is not known;
- why it matters;
- affected objects or decisions;
- evidence that would resolve it;
- priority or refresh trigger.

### Contradiction

Should state:

- claims or records in tension;
- why they cannot all be accepted without qualification;
- supporting refs for each side;
- current status;
- resolution action.

## 13. Package precedence

The manifest should assign authoritative precedence to files.

Default:

1. governed structured state;
2. governed registers;
3. manifest and validation;
4. governed narrative;
5. executive publication.

A lower-precedence contradiction still remains visible.

## 14. Legacy package receipt

For a legacy package, Flora generates:

`normalised-receipt-manifest.json`

This records:

- original archive checksum;
- discovered files and checksums;
- selected adapter;
- inferred file roles;
- missing profile fields;
- validation results;
- adapter limitations.

Generated metadata must be marked as runtime-generated and must not be inserted into the original archive.

## 15. Nested Twins

A package may identify:

- parent enterprise;
- parent Twin;
- nested-Twin type;
- inherited context;
- local scope;
- local effective date;
- local access classification.

A nested package does not duplicate parent canonical state unless needed for bounded portability. Imported duplicate context must map back to the parent rather than create competing truth.

## 16. Import report requirements

Every import should produce:

- package identity and checksum;
- profile and adapter version;
- file validation result;
- candidates by class;
- accepted canonical changes;
- unchanged mappings;
- rejected and quarantined items;
- projection registrations;
- Unknowns and Contradictions;
- unresolved lineage;
- architecture gaps;
- resulting Twin maturity statement.

## 17. Profile conformance tests

A profile-native package conforms when:

- manifest parses;
- all declared files exist and match checksums;
- record sets match declared counts;
- external IDs are unique;
- record classes and truth classes are recognised;
- all mandatory lineage references resolve or are explicitly incomplete;
- human knowledge is labelled;
- projection-only classes are not declared as canonical;
- dates use supported formats;
- package version and supersession are coherent.

## 18. Future evolution

A future profile version may add:

- signed manifests;
- schema registry links;
- encrypted record sets;
- access-control labels;
- canonical export from Flora;
- cross-enterprise exchange;
- package signatures;
- streaming deltas.

These are not required for Sprint 1.
