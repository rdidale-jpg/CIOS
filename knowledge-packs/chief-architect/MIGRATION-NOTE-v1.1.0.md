# Chief Architect Knowledge Pack v1.1.0 migration note

Version 1.1.0 changes release delivery, not the approved governed Knowledge Pack content. The ZIP and release evidence are rebuilt deterministically from the manifest and repository sources and are distributed as GitHub workflow artefacts rather than committed binaries.

Consumers should download the workflow artefact, verify the accompanying SHA-256 receipt, and validate the packaged `checksums.sha256` before use. Existing v1.0.0 consumers can migrate without changing document interpretation or authority precedence.
