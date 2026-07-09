# Flora Source-Only Pull Request

This branch publishes the governed Flora product implementation as normal repository source only.

## Retained capabilities

- Flora Home is served at `/`, `/flora` and `/flora/`.
- Blueprint Import supports governed package upload, validation, review, dry-run planning and explicit promotion.
- Import History remains available for inspection of submitted Blueprint packages.
- Enterprise Canvas remains available with lineage inspection and governed feedback routes.
- The Flora web home shows the release identifier for deployed revision visibility.
- The legacy BT landing screen is not part of the Flora home experience.

## Excluded handoff artifacts

The pull request intentionally excludes binary handoff and runtime artifacts, including ZIP archives, Git bundles, workbooks, PDFs, DOCX files, database files, uploaded Blueprint packages, MOD source material, runtime state, logs, screenshots, caches, compiled Python files, virtual environments, environment files, secrets and large generated artifacts.

