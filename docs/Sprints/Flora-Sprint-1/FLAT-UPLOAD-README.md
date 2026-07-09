# Flora Sprint 1 Flat Upload Pack v0.1

This pack is deliberately flat: it contains no nested directories and no duplicate filenames.

## Use

1. Open the GitHub documentation branch.
2. Navigate to `docs/Sprints/Flora-Sprint-1/`.
3. Upload every file from this folder into that directory.
4. Commit the upload to the documentation branch.
5. Run the instructions in `CODEX-INSTALL-FROM-FLAT-STAGING.md`.

Codex will then:
- move new documents to their governed target locations;
- reconcile the ADR index, Reference Architecture, Document Map and Glossary;
- place package metadata under `docs/Sprints/Flora-Sprint-1/package/`;
- remove the temporary flat staging files;
- validate that no runtime code changed.

Do not rename files before upload.
