# CIOS Chief Architect Knowledge Pack

This pack packages the canonical Chief Architect operating handbook and shared architecture authorities required to validate knowledge-pack production readiness.
# Chief Architect Knowledge Pack

The Chief Architect Knowledge Pack ZIP is a generated release artefact and is not stored in source control.

Build the reproducible release and its validation evidence from the repository root:

```sh
python3 tools/knowledge-packs/build_pack.py --profile chief-architect
```

Generated release files are written to the ignored `dist/` directory. GitHub Actions runs the same build and publishes the ZIP, checksum receipt, build and validation reports, change reports, migration note, and exception lists as downloadable workflow artefacts.
