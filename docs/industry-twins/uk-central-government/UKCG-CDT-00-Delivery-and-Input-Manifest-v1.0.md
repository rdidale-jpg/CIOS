# UKCG Candidate Blueprint Delivery and Input Manifest

**Package:** UKCG-CDT-Blueprint v1.0  
**Status:** Candidate / non-canonical / validation hold  
**Authoritative handover:** `docs/industry-twins/uk-central-government/Candidate-UK-Central-Government-Industry-Twin-Handover.md`

This manifest is the committed delivery/input authority for materialising the Candidate UK Central Government Industry Twin into the existing Flora Blueprint Package profile. The package must not be promoted beyond Candidate status and must not create canonical mutations.

## Committed inputs

| Input | Role | Governance note |
|---|---|---|
| `docs/industry-twins/uk-central-government/Candidate-UK-Central-Government-Industry-Twin-Handover.md` | authoritative candidate handover | Preserves source conclusions, Unknowns, Contradictions, explicit non-claims and the v2.54/v2.55 validation hold. |
| `tools/blueprints/materialise_ukcg.py` | source-to-Twin-Spine materialiser | Committed rebuild logic; reuses the existing Blueprint ZIP builder and Flora Twin Spine staging adapter contract. |
| `tools/knowledge-packs/build_uk_government_blueprint_package.py` | Blueprint Package ZIP builder | Emits `blueprint_manifest.json` at ZIP root and hashes declared assets. |

## Validation-hold boundary

The handover remains Candidate because v2.54 is a human-validation request pack and v2.55 is an await-validator-response / conditional-readiness assessment. The HMRC customer-stack workstream therefore remains on validation hold.
