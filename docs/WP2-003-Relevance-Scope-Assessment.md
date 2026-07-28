# WP2-003 — Relevance and scope pre-flight assessment

## Findings

The existing Review composes staged candidates with a package inspection and the
`TwinIdentityProjection`. Proposed Twin type, subject, governed scope and owner
are owner-backed when that projection is recognised. Package inspection can also
carry geography, time horizon and included sub-sectors. Candidate payloads retain
truth class, Evidence/lineage fields, owner annotations, commercial consequence,
decision relevance, relationships and classifications when supplied.

These fields were available but not composed into the executive conclusion
cards. Material-conclusion selection previously selected the first five payloads
with a `conclusion` or `statement`; it did not require a candidate-to-Twin link,
scope, relevance basis, truth class, Evidence state, or validation disposition.
That record-order selection is why mixed sectors could appear as one narrative.

## Presentation contract and boundaries

`CandidateRelevance` is a read-only, presentation-only projection. It accepts
only explicit package or candidate fields and uses the minimal labels `core`,
`relevant sub-sector`, `adjacent`, `unresolved`, and `out of scope`. Unknown or
missing status values become `unresolved`; labels, keywords, worksheet position
and record proximity are never classification evidence. No relevance score,
taxonomy, persistence owner, canonical write, or promotion mutation was added.

Primary eligibility requires an explicit Twin target and supporting relationship,
inspectable relevance basis and owner, supplied truth class and Evidence/lineage
state, clear scope, and a core or relevant-sub-sector status. Adjacent,
out-of-scope, unresolved, quarantined, and standalone Contradiction candidates do
not become primary conclusions. Contradictions remain available through existing
challenge and quarantine views.

## Missing and ambiguous semantics

Legacy packages frequently omit candidate-to-Twin relationships, relevance
status, classification basis, decision relevance, commercial consequence,
geography, period, or sub-sector. Those values remain visibly “Not supplied” or
“unresolved”; the presentation does not derive them. Whether adjacent content is
retained by a particular canonical owner remains governed by existing validation,
mapping and promotion semantics. Confirming scope can recompose presentation
groups, but it cannot create missing candidate relevance annotations. Canonical
ownership of richer industry/sub-sector classifications remains outside WP2-003.
