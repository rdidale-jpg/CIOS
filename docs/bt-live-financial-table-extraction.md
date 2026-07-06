# BT live financial table extraction compatibility

This change keeps rapid Financial Intelligence on the official-results-PDF path. It does not add source fallback, AI, OCR, Evidence writes, Observation writes, Enterprise Model writes, or canonical acceptance.

## Root-cause checkpoint

The bounded parser diagnostics showed the failing layout is not a complete pipe-style row table. The relevant table can be represented as separate positioned text blocks: section/title and scale context are emitted independently, period headings are positioned in value columns, and metric labels and numeric values can arrive as separate blocks. The former matcher only reconstructed rows containing literal `|` separators in page text, so it produced zero `_Row` objects for that structure and then emitted `metric label not found` for revenue, operating profit, and profit before tax.

The structural regression fixture is labelled `synthetic BT-results-layout regression fixture` and models:

- separate label and value text blocks;
- comparator and current-period columns, with FY25 inserted before FY26;
- an explicit `GBP m` scale heading;
- statutory Group rows for Revenue, Operating profit, and Profit before tax;
- adjusted and segment decoys.

## Extractor design

The generic official-results-PDF extractor now uses PyMuPDF's deterministic word coordinates in addition to page text. It preserves one extraction profile and reconstructs rows using:

- one-based page number;
- section/table markers;
- scale markers;
- period heading words and x-coordinates;
- label words left of the period columns;
- vertically aligned value cells under the positively identified FY26 column.

The extractor still requires explicit scale, section/table context, period-column identification, Group scope from the configured profile, statutory basis from the metric profile, and actual measurement state from the metric profile. Adjusted and segment rows are rejected with bounded diagnostics.

## Diagnostics and product wording

Rapid extraction diagnostics expose bounded structural fields: layout strategy, table regions found, period columns found, scale markers found, normalized labels encountered, and legacy/geometric row counts. They do not persist complete document text, temporary paths, or full word collections.

The normal product view translates runtime codes into business language. Zero-candidate official-source results now say that the report was retrieved but no safe financial findings were identified. Partial results show successful candidates separately from unresolved business metric names.
