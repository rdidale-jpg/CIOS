# Independent Enterprise Analysis handoff to BNK-IND-1

**Proposed documentation exchange v1; not an accepted import schema, new identity/source registry or runtime dependency.** Authoritative commissions #664 and #663 both require separate new-only directories. BNK-ENT-1 owns this folder; BNK-IND-1 owns docs/flora-runtime/bnk-ind-1/. Neither may edit shared overlays, snapshots, source rules or renderers in this stage.

## Contract and existing owners

| Review-file content | Narrow existing-owner mapping | What it does not authorise |
| --- | --- | --- |
| Source-Ledger URL, dates, excerpt locator/hash, rights/extent | Existing Source records / research primary-text and source-use owners | New host permission, original-byte archive or Evidence acceptance |
| Claims subject/type/source references and scope | SourceSegment / CandidateClaim / EvidencePackageItem proposal semantics | Canonical Observation creation or public admission by declaration |
| Identity-Crosswalk exact names and owner-scoped IDs | Existing Enterprise identity resolution / governed import owners | Canonical existence inferred from slug, route or empty model |
| Capability-Maps and executive writeups | EI/EIF/EGM-inspired read-only presentation candidates | Canonical taxonomy, supplier topology or accepted organisational model |
| Directed Relationship-Handoff edges and limitations | Existing relationship-candidate/business-object semantics after exact owner resolution | A resolved endpoint becoming a verified fact or contract |
| Financial-Reconciliation typed values and fixed QA | Existing Financial measurements/recipes/source owners in a later authorised adapter | A new financial engine or persistent run in this research sprint |

Each claim is a bounded review proposition with its own source set, reporting period, semantic kind, caveat and existing claim reference where available. Multi-field role/identity review summaries must be decomposed before any separately authorised Observation proposal; typed financial cells are already individually scoped. Each edge names directed subject/predicate/object, assertion kind, temporal semantics, evidence and public disposition. Measurement records preserve currency, unit/scale, duration/stock, accounting basis and state. No shared source IDs are overwritten; new BE-* IDs are doc-local review references only.

## Identity decisions to reconcile together

- Keep BIE-2 **actor:lloyds = Lloyds Bank PLC**, separate from **Assessment-Overlay::BK-ENT-001 = Lloyds Banking Group**.
- Preserve **actor:nationwide**, **actor:nbs-group** and the RUD reporting subject separately. Legacy Manifest::BK-ENT-003 and banking_portfolio::BK-ENT-003 conflict; do not merge by bare ID.
- Keep **actor:google / SUP-GOOGLE = brand**. Google Cloud EMEA Limited is a distinct doc-local legal-provider candidate, issuer-listed Ireland 660412. Google Ireland Ltd. 368047 is another entity. Neither is a new accepted Technology Twin.
- Keep **actor:payuk**, **actor:fps**, **actor:bacs**, **actor:ics** and **actor:cass** separate. An operator, system and switching service have different object kinds.
- canonical_enterprise_id may generate a fallback slug and EnterpriseModelRepository.get may return an empty object. Neither proves an accepted backing record. All proposed canonical IDs remain null until authorised reconciliation can inspect actual records/receipts.

## Positive and negative relationship proof

**Positive exact-entity evidence:** Companies House reports Group as active PSC of Lloyds Bank plc with share/vote control of at least 75% and director-appointment rights (BE-E01). This is not an inferred supplier contract. A separately inspected Pay.UK official list names Lloyds Bank plc and Nationwide as guarantors (BE-E02/E03): a genuine governance membership, not share ownership or a workload. The latter has unresolved public-use/source-adapter constraints; preserve factual verification and admission status separately. No eligible bank↔cloud legal-contract edge is claimed.

**Cross-layer path:** EAI-HMT-CTP26 → HMT designates named Google Cloud EMEA Limited, effective 13 July 2026; Banking mechanism → provider oversight/continuity context; LBG-ENVOY-GOOGLE → Group reports collaboration with Google Cloud brand. **Reject** a join into Lloyds Bank plc contracting a critical Envoy workload from the EMEA company. Designation, brand association, general contracting terms and legal identity do not supply actual customer/provider/service scope.

A supplier-side announcement adds Pay.UK/Vocalink continuity context, not an exact signed legal edge. No payment scheme is invented as a company to force an edge.

## Date and lifecycle fields

Keep publication, observation/retrieval, reporting period, announcement, legal effective date, completion, expiry and supersession separate. Null publication date is valid when genuinely unestablished. The May/April Envoy date discrepancy remains; Google's June 2024 technical description remains historical; the 2 April 2026 transfer does not rewrite Nationwide's 31 March reporting perimeter.

Source withdrawal, changed rights, retraction or a core contradiction must invalidate dependent candidate statements/edges, including counts/labels, while preserving history and unrelated eligible material. No automatic Model update, Material Pressure qualification or Opportunity follows. Private customer/seller records are never inputs to this public research handoff.

## Concurrency and release sequence

1. Publish independent draft Enterprise PR and source/identity/edge files; Industry consumes pinned references, not a merged shared overlay.
2. BNK-IND compares IDs/party scopes and flags collisions in its own folder. Resolve differences through owner review, without silent name matching or duplicate provider entities.
3. Existing-owner/source-use review determines which factual analytical projections are eligible. Technical allowlisting is not a rights grant and canonical acceptance is a separate, stronger authority.
4. A later explicitly authorised integration slice maps exact candidates into existing read services and acceptance mechanisms. Presentation lead alone edits shared runtime files, tests withdrawal/ACL, and retains rollback.

This handoff is ready for review. It is not a claim that BNK-IND-1 has consumed/accepted it, or that unmerged #661/#657/#662 code/research is an application dependency. No runtime work is launched by this PR.

## Pinned BNK-IND-1 reconciliation

The separate draft [#665](https://github.com/rdidale-jpg/CIOS/pull/665) was inspected at **46f0ed42e10f2c8a2cabbf344498898e94072990**, based on the same main. Its files remain unchanged and are not imported. This is Enterprise-side acknowledgement; joint owner acceptance remains pending.

| Industry handoff | Enterprise counterpart | Reconciliation |
| --- | --- | --- |
| IND-CTP / IND-RESILIENCE | BE-GC-DESIGNATION / BE-E05 | Same retained EAI-HMT-CTP26 identity, 10 July publication and 13 July effect. Context is not proof of an individual bank's exposure. |
| IND-ENVOY | BE-LBG-ENVOY / BE-E04 | Same PR-LBG-ENVOY; Group subject, provider brand and date conflict preserved. Use owner-qualified BK-ENT-001, not actor:lloyds. |
| IND-NBS | BE-NBS-FINANCIAL-BASIS / Financial-Reconciliation | Same finite RUD1-NATIONWIDE-FY26 source and consolidated reporting subject; both profit bridges agree, integration expenditure included once. |
| IND-OPERATOR | BE-PAY-SERVICES / BE-E09 | Same operator/service distinction; Industry's CASS release is an additional source, not automatically another accepted claim. |
| IND-PART-LLOYDS / IND-PART-NATIONWIDE | BE-E02 / BE-E03 | Complementary, **different predicates**: FPS participation versus guarantor membership. Neither implies the other or an executed bilateral contract. Enterprise does not upgrade Industry's review-only participation facts. |
| IND-REJECT | BE-N01 | Both reject Lloyds Bank plc → contracted critical Envoy workload → Google Cloud EMEA Limited. |
| IND-RAILS / IND-MPC / IND-SWITCH / IND-FCA | Deferred to Industry | Industry-owned measures/events and source-use decisions are not copied into the Enterprise pack or presented as newly verified here. |

Industry's bare actor references are retained against its BIE-2 owner. This pack adds the legacy/current BK-ENT-003 collision warning for any subsequent join. The two packs independently encountered unreadable Pay.UK financial accounts: neither supplies missing turnover or fees to the other. Their source observations may use different retrieval methods; a retained HTML digest is not this pack's short-excerpt hash. Keep each original provenance record.

Owner review should confirm the namespace mapping and distinct relationship predicates before a later Presentation owner consumes either pack. Publication of this handoff does not authorise shared-code edits or source admission.
