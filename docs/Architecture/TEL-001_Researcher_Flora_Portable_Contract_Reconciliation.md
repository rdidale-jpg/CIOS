# TEL-001 Researcher-to-Flora Portable Contract Reconciliation

## Decision

**MERGE — C. Shared-contract consolidation.** The investigation found no single accepted pre-research machine-readable Twin Object Profile consumed by both the TEL-001 Researcher mission and Flora. The Researcher mission was pinned to Research Mission templates and contract modules owned by the Researcher Knowledge Pack, while Flora accepted the Blueprint envelope and then depended on implementation-local staging/read-model vocabulary. The smallest correction is to add one versioned machine-readable portable Twin Object Profile contract and make Flora's existing staging transformation consume that contract instead of hard-coded drift compensation.

## Authoritative contract inventory and ownership

| Authority | Path | Status | Canonical owner | Finding |
| --- | --- | --- | --- | --- |
| Master index | `docs/MASTER_INDEX.md` | Accepted catalogue | CIOS Knowledge Library | Names the Researcher Knowledge Pack as repository-managed, but does not itself define object payload semantics. |
| Research Mission Templates | `knowledge-packs/researcher/research-missions/templates/templates-v1.json` | implementation-owned | Researcher Knowledge Pack | Pre-research TEL-001 commissions pin profile and module versions. |
| Research Mission Contract Modules | `knowledge-packs/researcher/research-missions/contracts/contracts-v1.json` | implementation-owned | Researcher Knowledge Pack / `CIOS-RMC-*` modules | Defines deterministic mission obligations including object construction, evidence, unknown and contradiction modules. |
| Researcher Knowledge Pack | `knowledge-packs/researcher/README.md`, `knowledge-packs/researcher/manifest.yaml` | generated package | Researcher Knowledge Pack | Exchange pack; includes templates and some canonical sources but not a single Flora-consumed object schema for all TEL-001 object families. |
| Implementation Profiles | `knowledge-packs/researcher/research-missions/contracts/contracts-v1.json`, `knowledge-packs/researcher/profile-versions.json` | implementation-owned | Researcher Knowledge Pack | The newer deterministic profile layer used by TEL-001; absent from the Chief Architect Knowledge Pack. |
| Industry Twin profile/spec | `architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md` | Review | Industry Twin specification | Governs Industry Twin semantics; explicitly not production profile membership. |
| Twin Presentation Model | `architecture/specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md` | Draft Normative Specification | Presentation Model spec | Owns presentation payload semantics; not canonical fact promotion. |
| Industry Twin Lifecycle | `architecture/specifications/industry-twins/Industry-Twin-Lifecycle-Specification-v1.0.md` | normative lifecycle source | Industry Twin lifecycle | Owns behavior, release and lifecycle controls, not Flora's local staging vocabulary. |
| Market Participant Twin | `architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md` | Draft Normative Specification | Market Participant Twin spec | Owns MPT semantics; Flora did not import a generated schema from it. |
| Enterprise Dossier | `knowledge-packs/researcher/templates/Enterprise-Intelligence-Pack-Template.md`, `architecture/reference-architecture/standards/EIF-001-Enterprise-Intelligence-Foundation-Model.md` | duplicated/prose | Enterprise Intelligence canonical models | Governed semantics exist as prose/templates, not a shared generated payload schema. |
| Programme Object | `knowledge-packs/researcher/templates/Programme-Catalogue-Template.md` | template | Researcher Knowledge Pack | Producer profile exists as template/implementation field set; Flora consumed local aliases. |
| Opportunity Object | `knowledge-packs/researcher/templates/Opportunity-Hypothesis-Template.md`, `architecture/specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md` | duplicated/prose | OT-001 / EOD-001 | Producer supplied `customer_problem`, `expected_procurement_timing`, `estimated_value`; Flora expected other names before consolidation. |
| Reinvention Assessment | `architecture/founding-papers/FP-012-Enterprise-Reinvention-Intelligence.md` | accepted founding paper | Enterprise Reinvention Intelligence | Governed concept exists; TEL-001 assessment fields required explicit profile binding. |
| Evidence / Unknown / Contradiction | `architecture/founding-papers/FP-004-Evidence-Acquisition-Standard.md`, `knowledge-packs/researcher/research-missions/contracts/contracts-v1.json` | accepted + implementation-owned modules | Evidence and Researcher contract modules | Semantics are governed, payload field names were not generated into Flora. |
| Relationship / Membership | `architecture/reference-architecture/standards/enterprise_domain_relationship_catalogue.md`, `knowledge-packs/researcher/research-missions/contracts/contracts-v1.json` | duplicated/prose | Enterprise relationship standards / RKP modules | No single shared schema consumed by both sides. |
| Release Manifest schema | `architecture/specifications/knowledge-packs/twin-release-manifest-v2.schema.json` | schema | Knowledge Pack specification | Governs release declaration, not object-family semantics. |
| Blueprint manifest schema | `knowledge-packs/researcher/package-contracts/flora-blueprint-import/blueprint_manifest.schema.json` | generated | Flora `BlueprintManifest` | Operational envelope only; not the TEL-001 semantic object contract. |
| Consolidated portable object profile | `cios/contracts/twin_object_profiles/researcher_v1.json` | implementation-owned consolidation | Shared Twin Object Profile contract | Added as the machine-readable profile Flora consumes for Researcher-produced portable objects. |

## Producer-to-consumer lineage

```text
Research Mission Template + RMC modules
  -> TEL-001 generated commission profile pins
  -> Researcher portable object files inside the unchanged Blueprint ZIP
  -> Blueprint manifest validates package envelope only
  -> Flora candidate staging reads package records
  -> TOP-RESEARCHER-PORTABLE-OBJECTS-v1 projects profile fields into candidate payloads
  -> SemanticTwin canonical-owner projection assembles typed objects and enterprise identity groups
  -> executive_assessments / twin_readiness derive owner assessment state
  -> executive_workspace renders Industry Overview, Enterprise, Market Participant, Programme,
     Opportunity, Reinvention and Research Gap views
```

## Recovered pre-research output-contract evidence

The recoverable pre-research TEL-001 output contract was not TEL-001-specific data. It was the Research Mission subsystem: TEL-001 generated commissions identify the mission template version, Researcher Knowledge Pack version and pinned Twin Object Profile versions, and the templates are owned by the Researcher Knowledge Pack. The exact governed decision is therefore an implementation-owned Researcher Knowledge Pack decision, not an accepted cross-runtime schema decision. Flora imported the generated Blueprint manifest schema, but did not import those Research Mission object-profile pins before this correction.

## Object-family conformance matrix

| Object family | TEL-001 source shape | Flora pre-correction input | Classification | Correction |
| --- | --- | --- | --- | --- |
| Industry Overview | Single rich `industry_overview_wave5.json` object | Expected canonical `industry_twin`/insight fields | duplicated contract | Profile maps overview, title and industry profile without treating manifest as semantics. |
| Enterprise Dossiers | Rich nested dossier records | Identity grouped; substantive fields depended on local aliases | consumer non-conformant / duplicated contract | Shared profile maps overview, strategy, operating, financial, technology, ecosystem, pressures and programmes. |
| Market Participants | `market_participant_profiles_wave5.json` | Mostly aligned through local aliases | duplicated contract | Shared profile is now owner of aliases. |
| Programmes | `programme_objects_wave5.json` | Partially aligned | duplicated contract | Shared profile maps owner, unit, objective, phase, timing and investment. |
| Opportunities | `opportunity_objects_wave5.json` with `customer_problem`, `expected_procurement_timing`, `estimated_value` | Flora expected nested `client_problem`, nested `timing`, nested `value` | consumer non-conformant | Profile maps both governed and observed producer names. |
| Reinvention Assessments | `reinvention_assessments_wave5.json` | Partially aligned; `transformation_pressure_view` alias lived in code | duplicated contract | Alias and fields moved to profile contract. |
| Evidence | Evidence register records | Accepted only when field vocabulary matched | contract ambiguous | Profile declares supported evidence field selectors. |
| Unknowns | Unknown register records | Local aliases | duplicated contract | Profile declares unknown selectors. |
| Contradictions | Contradiction register records | Local aliases | duplicated contract | Profile declares contradiction selectors. |
| Relationships | Relationship register records | Local aliases | duplicated contract | Profile declares relationship selectors. |
| Memberships | Membership register records | Local aliases | duplicated contract | Profile declares membership selectors. |
| Release Manifest | Draft release manifest | Retained as release lineage | contract aligned | No semantic object promotion from manifest. |

## Earlier successful-pack comparison

Earlier Banking and BT packs rendered successfully because they used Flora-native read models, fixtures and demonstrator-specific projections already shaped for the pages. They did not prove that TEL-001 conformed to the same portable Researcher object contract, and they did not exercise producer-consumer compatibility for Researcher Implementation Profile field names.

## Adapters that compensated for drift

* `cios/applications/flora/blueprint_import/researcher_profile_adapter.py` translated Researcher nested owner documents into Flora's canonical candidate vocabulary.
* `cios/applications/flora/blueprint_import/cios_twin_adapter.py` contains legacy Blueprint workbook/class mappings.
* `cios/applications/flora/blueprint_import/industry_delta_adapter.py` translates governed delta and HFT inventory records at the staging boundary.
* `cios/applications/flora/blueprint_import/package_contracts.py` detects package contracts and keeps manifests as envelope/release lineage rather than semantic object contracts.

## Root cause

The TEL-001 package was produced against Researcher implementation profiles and templates, while Flora consumed a generated Blueprint envelope schema plus implementation-local semantic aliases. The package envelope was shared; the object semantics were not. This is shared-contract drift, not a TEL-001 data problem and not a reason to weaken validation.

## Implemented canonical correction

`TOP-RESEARCHER-PORTABLE-OBJECTS-v1` is now the machine-readable Twin Object Profile contract for Researcher portable object records consumed by Flora. Flora's existing Researcher profile adapter loads this contract and records contract diagnostics in staged payloads. Compatibility tests assert TEL-001 source shapes project through the same contract for supported object families.
