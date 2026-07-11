# Researcher and Reviewer Knowledge-Pack Profile Audit

**Status:** Governance audit  
**Owner:** CIOS Architecture  
**Date:** 2026-07-11  
**Scope:** Generated Researcher and Reviewer knowledge-pack profiles for Architecture v2.0 documentation work.

## Executive conclusion

The generated profile counts are explainable and structurally sound, but the packs should be treated as role packs rather than repository mirrors:

- **Researcher pack: 93 files.** It is larger because the Researcher must create or amend governed Architecture v2.0 material. It therefore needs the shared authority baseline plus authoring guidance, lifecycle guidance, research-agent operating guidance, publication contracts, templates and selected runtime context that prevent invented terminology or ungoverned release artefacts.
- **Reviewer pack: 68 files.** It is smaller because the Reviewer only needs to check correctness, governance, dependency completeness and exclusion discipline. It needs the same authority baseline, ADRs and model specifications, but does not need authoring templates, research workflow aids, sprint evidence or generated publication examples.

The smallest authoritative, dependency-complete pack is therefore **not the largest possible pack**. The Reviewer profile is the control baseline. The Researcher profile should be the Reviewer baseline plus only the files required to author compliant candidate changes and Knowledge Pack payloads.

## Why the Researcher pack contains 93 files

The Researcher profile contains the 68-file authoritative review baseline plus 25 additional role-enabling files. Those additional files are justified only when the Researcher is expected to produce candidate architecture or Knowledge Pack-compatible outputs, not merely review them.

| Purpose | Include in Researcher | Include in Reviewer | Reason |
| --- | ---: | ---: | --- |
| Core AI operating context | Yes | Yes | Establishes current north-star, progressive assurance, GPT output boundaries and mandatory reading order. |
| Reference Architecture and doctrine | Yes | Yes | Provides system-level authority, glossary, document map, design doctrine and architecture principles. |
| Accepted ADRs | Yes | Yes | Provides binding decision constraints, especially Evidence, Observation, Lineage, Progressive Assurance and Knowledge Pack exchange rules. |
| Founding Papers | Yes | Yes | Defines durable intelligence, evidence, source quality, signal, conviction and Knowledge Pack architecture. |
| Enterprise Intelligence specifications | Yes | Yes | Defines Enterprise Model, Knowledge Graph, Behaviour, Commercial Reasoning, Opportunity, Executive, Weather, Pressure, Momentum, Economics, Observation and Knowledge Asset semantics. |
| Exchange and presentation specifications | Yes | Yes | Defines Knowledge Pack, Twin Release, Presentation Model, Industry Twin and Market Participant contracts. |
| Research-agent and authoring guidance | Yes | No | Needed to create candidate outputs; not needed to review whether outputs comply. |
| Templates and checklist aids | Yes, minimal | No, unless reviewing template compliance | Useful for producing consistent candidate artefacts; they add noise to the Reviewer pack. |
| Runtime implementation examples | Limited | No | Only include when a profile must understand a live boundary. Generated examples are not authority. |
| Sprint, phase and completion reports | No by default | No | They are historical evidence of work done, not standing architectural authority. |

## Why the Reviewer pack contains 68 files

The Reviewer profile contains only files required to answer four governance questions:

1. **Is the output compatible with current CIOS doctrine?**
2. **Does it preserve Evidence, Observation, Unknown, Contradiction, Hypothesis, Recommendation and lineage semantics?**
3. **Does it respect the Knowledge Pack and Presentation Model contracts?**
4. **Does it avoid importing drafts, duplicates, generated outputs or sprint artefacts as authority?**

The Reviewer therefore excludes role-production aids and historical delivery records. This is why it is 25 files smaller than the Researcher pack while remaining dependency-complete for approval.

## Required exclusion rules

The generated profiles must apply these exclusions unless a file is specifically required for a named task and clearly labelled in the pack manifest as non-authoritative context:

| File class | Default action | Exception rule |
| --- | --- | --- |
| Draft working notes outside the governed Architecture v2.0 authority set | Exclude | Include only if the task is explicitly to review or promote that draft. |
| Historical DOCX copies | Exclude | Include only as labelled historical review evidence when Markdown authority is missing or disputed. |
| Duplicate DOCX/PDF publication copies | Exclude | Include only as labelled publication-format checks, never as source authority. |
| Sprint folders and sprint completion reports | Exclude | Include only for delivery audit, not for model or doctrine authority. |
| Experiment folders and experimental instructions | Exclude | Include only for experiment review and label as experimental/non-baseline. |
| Generated reports, previews, exports, manifests, inventories and ZIPs | Exclude | Include only for release-validation tasks and label as generated output. |
| Runtime tests and fixtures | Exclude | Include only for runtime implementation tasks, not architecture-pack review. |

## Safe removals from the generated packs

The following can be safely removed without reducing role capability for ordinary Researcher or Reviewer operation:

- **Both packs:** sprint reports, phase completion reports, generated manifests, release ZIPs, static preview outputs, experiment code/instructions, binary DOCX duplicates and generated publication examples.
- **Reviewer pack:** Researcher-only authoring templates, publication workflow examples, Research GPT operating guide copies, package assembly aids and any runtime implementation examples not needed to verify a specific boundary.
- **Researcher pack:** historical delivery reports and duplicate binary copies should still be removed; if a Researcher needs provenance, cite the canonical Markdown authority or the Document Map instead.

## Minimum pack definitions

### Reviewer minimum pack

The Reviewer pack should contain only:

- `CIOS-AI.md`;
- Reference Architecture overview, doctrine, glossary, document map and meta-model;
- Accepted ADRs relevant to evidence, observations, lineage, progressive assurance, human-supplied knowledge and Knowledge Packs;
- Founding Papers that define intelligence, evidence, source quality, signals, conviction and Knowledge Pack exchange;
- Enterprise Intelligence model specifications and indexes;
- Knowledge Pack, Twin Release, Presentation Model, Industry Twin and Market Participant specifications.

### Researcher minimum pack

The Researcher pack should contain the Reviewer minimum pack plus:

- canonical Research Agent Guide Markdown;
- authoring and lifecycle guidance needed to create compliant candidate content;
- minimal templates/checklists needed to avoid missing lineage, validation or manifest fields;
- only task-specific runtime context when the Researcher is asked to align documentation with implementation.

## Confirmation

This audit confirms that Draft, historical, duplicate DOCX, sprint, experiment and generated files are **excluded by default** from both profiles. Any exception must be explicitly listed in the pack manifest with:

- the reason it is required;
- whether it is authoritative, contextual, historical, experimental or generated;
- the role that needs it;
- the review expiry or removal trigger.
