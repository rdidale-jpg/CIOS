# Flora Authoritative Document Ingestion

## Retrieved versus parsed

A source is **retrieved** when the governed URL returns bytes or HTML successfully. A document is **parsed** only when the selected parser processes the retrieved payload. For `application/pdf` or PDF-looking bytes, Flora selects the PDF parser, records checksum/local cache path, page count, parser status, page-level text and extraction warnings.

Retrieved PDFs must not silently produce zero parser activity: diagnostics include documents retrieved, PDFs parsed, pages extracted, tables detected, parser status and warnings.

## Candidate dispositions

Evidence candidate counters are exhaustive for the pilot path:

```text
evidence_candidates = accepted + rejected + downgraded + duplicate
```

Additional status fields are available for context-only, corroborated and extraction-failed counts when those dispositions are produced by a parser or acceptance stage. A reconciliation invariant raises an error if counted candidates do not balance.

## Rejection diagnostics

Rejected and downgraded candidates retain source, snippet, attempted classification, relevance level, rejection reason and safer interpretation in diagnostics. The default progress view presents concise source/action-oriented errors and keeps raw JSON in an analyst details section.

## Factual acceptance path

Accepted factual document Evidence carries canonical enterprise ID, source ID, page number/page range, checksum, extraction method, source authority and affected Enterprise Model attribute. The memory service converts accepted Evidence to an atomic Observation and applies that Observation to the maintained Enterprise Model.
