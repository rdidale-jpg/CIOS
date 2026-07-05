# BT FY26 structured filing diagnostic

## Executive outcome

Outcome B — honest source blocker. No hosted deployment was made. The current governed BT source remains an official issuer ESEF ZIP URL, but this run could not complete a fresh local download from the execution environment because the BT asset returned HTTP 403 before bytes were received. The repository change therefore records the blocker and fixes a local handoff defect without claiming a proven raw filing.

## Official source search record

- BT Group investor annual reports page: located the issuer's Annual Report 2026 ESEF area listing an iXBRL filing ZIP and a separate iXBRL viewer XHTML asset.
- BT Group configured ZIP URL: attempted direct HTTPS retrieval of `https://www.bt.com/content/dam/bt-plc/assets/documents/investors/financial-reporting-and-news/annual-reports/2026/2026-bt-group-plc-esef-filing.zip`; result was HTTP 403 in this environment, so the package could not be re-downloaded locally for conclusive inspection.
- FCA National Storage Mechanism: public announcements state the Annual Report was submitted to the NSM, but no governed raw downloadable NSM artifact URL was resolved locally.
- Companies House: not used as a selected source because the task requires the FY26 consolidated Group structured AFR; Companies House is not the primary governed ESEF source for this deployment path.

## Current package status

The last hosted run reported SHA-256 `5ac8c17956e8393fc16d96817ba4b2f1560f6a6f65756a9ce3cdb5acdec752e5`, archive validation success, and `ixbrl-viewer.htm` present, but it did not prove package type, raw inline XBRL, selected report, adapter handoff, or candidate facts. Because the exact package could not be downloaded again locally, this diagnostic does not assert a new package classification from local bytes.

## Adapter handoff correction

`prepare_raw_report_from_package` now extracts the selected report entry from a ZIP package into a temporary work directory instead of copying and renaming the entire ZIP. This preserves a path-based adapter handoff while avoiding an invalid report file when a raw inline report is eventually proven inside a package.

## Explicit non-actions

- AI calls: 0.
- PDF fallback calls: 0.
- Viewer-value scraping: not introduced.
- Generic HTML financial extraction: not introduced.
- Hosted deployment: not attempted.
