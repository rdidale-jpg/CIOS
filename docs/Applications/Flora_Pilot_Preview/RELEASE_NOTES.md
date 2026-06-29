# Flora Pilot Preview Release Notes

## Summary

This PR delivers a text-only accessible Flora Morning Edition preview for 2026-06-29.

## Binary artefact policy

PDF, PNG and ZIP artefacts are generated locally by the Flora publisher workflow, but they are not committed in this PR because the current PR flow does not support binary artefacts.

The branch intentionally excludes:

- `*.pdf`
- `*.png`
- `*.zip`

## Future delivery

Binary delivery should be handled later via GitHub Releases, not PR files. Release assets are the appropriate place for locally generated PDFs, page preview PNGs and packaged ZIP downloads.

## Included files

- `README.md`
- `Morning_Edition_2026-06-29.md`
- `Morning_Edition_2026-06-29.html`
- `VERSION.json`
- `RELEASE_NOTES.md`
