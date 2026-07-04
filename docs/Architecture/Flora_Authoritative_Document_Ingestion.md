# Flora Authoritative Document Ingestion

Flora now treats governed documents as a staged acquisition pipeline rather than assuming every source is HTML.

## Source stages

1. governed source selection from the profile allow-list;
2. retrieval with explicit byte and timeout limits;
3. media-type classification;
4. PDF parsing for `application/pdf` sources;
5. page-indexed Evidence extraction;
6. atomic Observation creation;
7. Enterprise Model projection.

## PDF retrieval

PDF retrieval uses a source-specific request, no crawling, and stores downloaded bytes under `.flora_pilot/documents` using a checksum-derived filename. The checksum is used as the durable document identity input.

## PDF parsing

The first parser path is born-digital embedded text extraction. It preserves page numbers and records parser status, page count, extraction method, extraction version and warnings. OCR is not enabled by default.

## Table extraction

The v0 extractor recognises deterministic financial table rows where metric, segment, period and value are clear. Uncertain tables are rejected with `Table extraction uncertain` rather than silently accepted.

## Provenance and page lineage

Each accepted Evidence item carries document ID, source ID, source title, publisher, source URL, source type, source tier, checksum, media type, page number, extraction method, extracted text and confidence. Observations retain Evidence IDs so model attributes can navigate back to the supporting page.

## OCR fallback

OCR may be introduced only when a source is authoritative and no embedded text exists. Any OCR-derived Evidence must be explicitly labelled, downgraded in confidence and retain original page references. Current runtime records the need for OCR but does not silently perform it.

## Error handling

Retrieval, parsing and Evidence extraction are separate stages. Failure categories distinguish retrieval failure, unsupported media type, PDF extraction failure, table uncertainty and Evidence validation rejection.

## Security constraints

PDFs are treated as untrusted external input. Flora applies byte limits, page-count limits, checksum storage, no embedded-content execution, no path-derived filenames, parser exception containment and bounded retained files.

## Limitations

The parser prioritises simple born-digital PDFs and deterministic table rows. Rich layout reconstruction, OCR, attachments, scripts and broad autonomous source discovery are intentionally out of scope for this foundation sprint.
