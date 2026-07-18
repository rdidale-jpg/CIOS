# Banking Knowledge Domain

## Purpose

The Banking knowledge domain governs Banking Enterprise Intelligence research assets and their reusable knowledge outputs. Banking is the reference implementation for the reusable Enterprise Knowledge governance model.

## Contents

- [MANIFEST.yaml](MANIFEST.yaml) defines the governed asset inventory and stable asset identifiers.
- [industry/](industry/README.md) contains industry foundations, Industry Twins and mechanism catalogues.
- [infrastructure/](infrastructure/README.md) contains infrastructure Twins and infrastructure-scoped evidence.
- [enterprises/](enterprises/README.md) contains enterprise-scoped Twin directories.
- [comparisons/](comparisons/README.md) contains differential and comparison artefacts.
- [flora/](flora/README.md) contains discovery metadata for Flora.

## Governance rules

- Preserve original Enterprise Knowledge content; do not rewrite Twins, research, observations or evidence during governance work.
- Use stable asset identifiers from [MANIFEST.yaml](MANIFEST.yaml); never derive relationships from filenames.
- Convert legacy text assets to Markdown and retain provenance through metadata.
- Keep commercial opportunity material separate from mechanism validation.

## Relationship to other assets

The domain is registered in the repository-level [REGISTER.md](../REGISTER.md). The manifest is the domain-level control point; folder README files provide human navigation only.
