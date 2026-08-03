# Creating a future Industry Twin research mission

This is an operating convention within the existing Researcher Knowledge Pack, not a new architectural standard. Twin Object Profile ownership remains with the canonical Industry Twin package inventory contract; Flora may populate gaps and subject IDs but does not own research behaviour.

1. Choose an active template in `templates/templates-v1.json`.
2. Copy and complete a versioned Research Mission Manifest validated by the schema.
3. Provide the industry scope, geography, current gaps and baseline release in the manifest.
4. Generate the commission with `python3 tools/knowledge-packs/research_missions.py MANIFEST --output BRIEF`.
5. Build the Researcher Knowledge Pack with its existing builder.
6. Issue the generated brief, manifest and pack to the researcher.
7. Validate returned structured outputs against the named Twin Object Profiles and the pre-delivery contract.

Migration: replace manually rewritten briefs with a manifest; keep industry facts only in that manifest. Select the matching template, pin all required registered profile versions, transfer current gaps/subjects, and check in the deterministic generated brief.
