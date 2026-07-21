# Researcher Knowledge Pack Release Process

The Researcher Knowledge Pack release version is governed by a single semantic version selected for the release. Tagged GitHub Actions releases derive that version from tags named `researcher-knowledge-pack-vMAJOR.MINOR.PATCH`; manual workflow runs require the same bare semantic version as an explicit input and publish workflow artefacts only.

## Version-bump workflow

1. Update pack content in canonical repository sources.
2. Update `knowledge-packs/researcher/CHANGELOG.md`.
3. Update `knowledge-packs/researcher/MIGRATION.md` where required.
4. Select the next semantic version.
5. Run the builder locally with the selected version, for example:

   ```bash
   python3 tools/knowledge-packs/build_researcher_pack.py --version 2.2.0 --output-dir dist
   ```

6. Run pack tests and validation.
7. Commit all source changes.
8. Create an annotated tag that exactly matches the selected version:

   ```bash
   git tag -a researcher-knowledge-pack-v2.2.0 \
     -m "Publish CIOS Researcher Knowledge Pack v2.2.0"
   ```

9. Push the commit and tag.
10. GitHub Actions builds and publishes the governed release from the tag.

Do not move an existing release tag to another commit. If a tag already exists and points elsewhere, stop and resolve the governance issue before publishing.

## Semantic-version intent

- **PATCH** — corrections that do not materially change Researcher behaviour or included doctrine.
- **MINOR** — backward-compatible additions, new governed guidance, templates or source inclusions.
- **MAJOR** — breaking changes to pack structure, operating boundaries, doctrine interpretation or required consumer behaviour.

The participant-aware update from v2.1.0 should normally be released as v2.2.0 unless repository governance identifies a breaking change.

## Hard-coded-version audit

The active workflow, builder, tests and operational instructions must not hard-code release artefact names for historical versions. Historical references to v2.1.0 remain valid in changelog, migration and governance-history documents when they describe prior releases or upgrade paths.
