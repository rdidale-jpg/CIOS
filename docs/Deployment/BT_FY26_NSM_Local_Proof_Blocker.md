# BT FY26 NSM local structured-ingestion proof blocker

Date: 2026-07-05

## Outcome

The governed BT FY26 structured-source entry has been switched away from the BT issuer-hosted ESEF package and now points at the FCA National Storage Mechanism as the governed authority. The previous BT issuer package is retained only as corroborating source metadata and is not an automatic fallback.

Local proof has not completed because direct access from this execution environment to `data.fca.org.uk` is blocked by the outbound proxy with HTTP 403 before the original filed artifact can be downloaded.

## Searches and records checked

- FCA NSM target searched through the public FCA NSM entry point: `https://data.fca.org.uk/#/nsm/nationalstoragemechanism`.
- Issuer search terms used: `BT GROUP PLC`, `213800LRO7NS5CYQMN21`, `04190816`, `Annual Financial Report`, `2026-03-31`, `June 2026`.
- Corroborating regulatory announcement found: London Stock Exchange RNS item `BT.A` / `17635334`, titled `Annual Financial Report`, published at 10:52:48 on 2026-06-11. The announcement states that BT Group plc's Annual Report 2026 and Notice of Meeting 2026 were submitted to the National Storage Mechanism.

## Current governed-source correction

- `source_kind`: `official_nsm_esef`.
- `nsm_identifier`: `BT.A-17635334` pending direct NSM row identifier confirmation from the FCA UI/download response.
- `nsm_record_url`: `https://data.fca.org.uk/#/nsm/nationalstoragemechanism`.
- `artifact_url`: temporarily set to the NSM entry point so retrieval fails safely rather than falling back to the unsupported BT viewer package.
- BT issuer-hosted ESEF filing and viewer URLs are preserved under `corroborating_issuer_source` only.

## Local run result

Command:

```bash
FLORA_DATA_DIR=/tmp/flora-proof python - <<'PY'
from cios.applications.flora.financial_intelligence import bt_structured as bt
run=bt.ingest_bt_fy26('fi-nsm-local-proof')
print(run['status'])
print(run.get('failure_code'))
print(run.get('failure_stage'))
print(run.get('support_reference'))
print(run.get('structured_diagnostics',[{}])[0].get('artifact_url'))
print(run.get('ai_calls_made'), run.get('pdf_fallback_calls_made'))
PY
```

Result:

- Status: `structured_source_unavailable`.
- Failure code: `http_403`.
- Failure stage: `official filing retrieval`.
- Support reference: `FI-nsm-local-proof`.
- Adapter handoff attempted: `false`.
- Candidate fact count: `0`.
- AI calls: `0`.
- PDF fallback calls: `0`.

## Required next step

Use an environment with browser/UI access to the FCA NSM to accept the NSM notice, locate the BT Group plc FY26 Annual Financial Report row, and capture the FCA original-format download URL and row identifier. Only then should the `artifact_url` be replaced with the official original structured artifact URL and a hosted run/deployment attempted.

Do not widen `ixbrl-viewer.htm` recognition and do not restore the BT issuer package as an automatic fallback.
