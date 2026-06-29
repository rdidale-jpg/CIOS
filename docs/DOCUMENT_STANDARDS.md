# CIOS Document Standards

These standards define how controlled documents in the CIOS Knowledge Library are identified, named, versioned, reviewed and maintained.

## Document Numbering

Controlled documents use the format `CIOS-<DOMAIN>-<NUMBER>`.

- `CIOS-CON-###` for constitutional doctrine and operating principles.
- `CIOS-SCI-###` for commercial science foundations, hypotheses and theory.
- `CIOS-ENG-###` for engineering specifications, architecture standards and implementation guidance.
- `CIOS-RES-###` for research papers, validation studies and literature reviews.
- `CIOS-MOD-###` for reusable models and model specifications.

Numbers are assigned sequentially within each domain. Once assigned, a document identifier must not be reused for a different purpose.

## Naming Conventions

File names should use the pattern:

```text
CIOS_<DOMAIN>_<NUMBER>_<Short_Title>_v<MAJOR>.<MINOR>.<PATCH>.md
```

Use underscores in file names, title case in document titles and repository-relative paths in indexes. Folder names should be descriptive, stable and aligned with the library structure. Avoid ambiguous names such as `misc`, `new`, `final` or `archive2`.

## Semantic Versioning

Controlled documents use semantic versioning:

- `MAJOR` changes alter meaning, governance, interfaces, architecture or downstream obligations.
- `MINOR` changes add material guidance without breaking prior interpretation.
- `PATCH` changes clarify wording, correct errors or improve formatting without changing intent.

Draft documents may begin at `0.1.0`. A document reaches `1.0.0` when it is approved as a baseline for implementation, governance or product use.

## Status Lifecycle

Documents should use one of the following statuses:

1. `Planned` — identified but not yet drafted.
2. `Draft` — actively being written and not authoritative.
3. `Review` — ready for formal stakeholder or technical review.
4. `Approved` — accepted as authoritative for its stated scope.
5. `Superseded` — replaced by a newer controlled document.
6. `Retired` — intentionally removed from active use while preserved for history.

A document may include a more specific status such as `Engineering Baseline` when the meaning is clear and reflected in the Master Document Index.

## Document Headers

Each controlled document should begin with a concise header containing:

- Document ID
- Title
- Version
- Status
- Owner or accountable function
- Last reviewed date
- Scope or primary use

Headers should make authority and intended use clear before the body of the document begins.

## Ownership

Every controlled document should have an owner responsible for accuracy, review cadence and alignment with related documents. Ownership may sit with a person, role or accountable function. Owners are responsible for ensuring downstream documents and implementation artefacts remain traceable when the document changes.

## Review Process

Material changes should be reviewed before approval. Review should confirm that:

- The document has a valid identifier, title, version, status and location.
- Claims are clear, professional and free from placeholder text.
- Dependencies and downstream impacts are identified.
- Traceability links are added or updated where required.
- The Master Document Index reflects the current status and version.

Approved documents should be reviewed when related constitutional, scientific, engineering, SDK, application or product decisions change.

## CBOK Authoring System

CBOK documents are governed by the CBOK Authoring System in `docs/CBOK/`. CBOK documents use `CIOS-CBOK-<TYPE>-<NUMBER>` identifiers and may represent constitutions, scientific frameworks, standards, reference models, commercial laws, influence models, enterprise patterns, working papers, literature reviews, experiments, validation reports and architecture documents.

Every controlled CBOK document must include document metadata, purpose, scope, terminology, normative references, content sections, traceability, version history, review history, engineering mapping and appendices. Authors should start from the templates in `docs/CBOK/templates/` and apply the CBOK lifecycle, confidence and review standards before requesting approval.

## CBOK Scientific Knowledge Framework

CBOK-SCI-001 is the governing framework for scientific knowledge in the Commercial Body of Knowledge. It defines how knowledge is classified, evaluated, validated, promoted, traced and consumed by engineering. CBOK scientific artefacts should apply CBOK-SCI-001 when assigning knowledge classes, evidence levels, scientific confidence, operational confidence and downstream traceability.

## Ontology Standards

Ontology standards must comply with [CBOK-STD-000 Commercial Ontology Meta-Model](CBOK/Standards/CBOK-STD-000_Commercial_Ontology_Meta_Model_v1.0.0.md) and [CIOS-ENG-005 Ontology Engineering Standard](Engineering/CIOS-ENG-005_Ontology_Engineering_Standard_v1.0.0.md). CBOK-STD-000 defines the ontology grammar and primitive types; CIOS-ENG-005 governs engineering representation. Ontology documents shall keep CBOK meaning, machine-readable ontology representations, SDK mappings and knowledge graph mappings aligned.

## CBOK Playbooks and Propositions

Commercial Intelligence playbooks, patterns, anti-patterns and AI reinvention propositions are CBOK knowledge assets. They must follow CBOK-SCI-001 classification, evidence, confidence, lifecycle, traceability and review rules. Authors shall distinguish standards, models, heuristics, hypotheses, patterns and recommendations, and must not promote playbook guidance into application behaviour without governed engineering review.
