# WP0-FIX-001 — governed Industry Twin import correction

## Diagnostic conclusion

The failed DIST-001 record reached package inspection with its uploaded name,
checksum and import/session identity intact. Detection found `00_manifest.json`
and the governed Delta, but candidate extraction only read a top-level `records`
array. The supplied governed Delta uses an operation-oriented envelope. The
adapter consequently returned an empty tuple without an error. With no candidate
carrying a Twin type, the UI reported **Unclear**; with zero candidates there was
nothing to review, dry-run, promote or expose in Explore.

The generic receipt, registry and storage route did not intentionally load a
UKCG fixture. The dangerous coupling was instead operational: the UKCG workflow
subscribed to every change under `cios/**` on merges to `main` and `work`. Its
steps compile, test, materialise and upload a CI artefact; they contain no deploy
step and do not modify the running Flora service. It was therefore an obsolete,
over-broad candidate-package check rather than a deployment mechanism.

## Correction and acceptance boundary

The UKCG workflow is now triggered only by its UKCG materialiser, source,
package-builder, fixture test and workflow definition. Generic Flora changes no
longer invoke it. Production ingestion remains Flora's existing multipart upload,
registry, validator, staging, review, dry-run and promotion route.

The generic Delta adapter now accepts both row-oriented and governed
operation-oriented envelopes, normalises generic object vocabulary, preserves
producer identifiers, and records Industry Twin routing on extracted candidates.
It never searches repository content and has no DIST or UKCG fallback. A valid
Delta that yields no candidates now produces a blocking extraction diagnostic
containing the import correlation, checksum, manifest location and Delta
location. Review and later actions remain disabled rather than continuing.

Automated browser-boundary coverage uses an in-memory synthetic package. The
real DIST-001 ZIP is neither committed nor required. Final production acceptance
still requires an authorised operator to upload the real archive through Flora
and verify Review, dry-run, Promote and Explore against the deployed persistence
store. Until that browser exercise is recorded, the recommendation is **Revise**,
not Merge or Reject.
