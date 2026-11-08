# Repair 03 — existing journey and minimum changes

Recorded before implementation. Baseline main:
`cf7942fabb5f456f827c08f88e0d189a46ebc69f`, merged #530–#535.
Accepted ADR-002/009/012/014/024/026 remain unchanged. Research packages and
roadmaps are inputs, not proof of canonical model intelligence.

Receipt -> immutable archive -> validation/staging -> review/mappings -> owner
approval -> canonical subset promotion -> completion is implemented by the existing
Blueprint importer. Completion currently invokes Enterprise Canvas access repair
and links `/digital-twins/<package enterprise>/canvas` even for Industry imports.
The correct existing import-scoped Industry workspace is
`/blueprint-import/<run>/intelligence`; dossiers are its Enterprise views. Repair 02
links separately applied durable Enterprise Models. Those are distinct consumers.

Canvas header and candidate lenses currently use package received_at as material
change time. A generic strategic-context fallback names MOD, and a generic lens
role says "accepted governed MOD Twin records". These are view defects, not missing
research. Preserve MOD-specific reasoning/labels when the actual enterprise is MOD;
generic or candidate-only views must not fabricate strategic context or material
change dates.

| Audit defect | Existing implementation | Actual retained boundary | Minimum correction |
| --- | --- | --- | --- |
| F06 | semantic_twin query_subject_associations / enterprise_associations feed dossier programme/opportunity lists | BNK has 18 Owner owns Programme and 11 Enterprise has Opportunity Hypothesis edges; TEL uses Enterprise owns Programme / Opportunity targets Enterprise | Add exact typed producer relationship names with their supplied directions; share rules across opportunity customer rendering. Require resolved endpoints and correct related object family; preserve candidate/source/edge lineage. No undirected or fuzzy association. |
| F07 | shared Researcher selector adapter, Canonical Factual Projection and dossier financial dimension | BNK financial_position has economic_model, current_signal and latest_reporting; existing selectors consume financial_intelligence/context/financials | Add a compatible selector and read fallback, keep verbatim narrative and explicit Evidence IDs. Label source financial narrative and candidate interpretation; do not generate numeric canonical facts or calculated economics. |
| F08 | key_reports uses explicit primary Evidence subject and SemanticEnterprise identities | EV-BARCLAYS-AR2025 supported_object is Barclays; dossier ENT-BARCLAYS name is Barclays PLC; publisher is not subject authority | Use the existing governed alias resolver, adding the explicit repository-owned Barclays -> barclays-plc alias. Include producer-supplied dossier aliases; reject unresolved/ambiguous primary identities and preserve group/competitor/shared distinctions. No legal-suffix stripping or title/publisher guessing. |
| F09 | review_plan class-persistence diagnostics already distinguish persistable/support/non-persistable; summary hard-codes non_persistable=0 and includes wrappers in Creates | Accepted staged business wrappers can remain non-persistable; successful execution does not make all wrappers canonical | Derive presentation partitions from existing class diagnostics and effect records. Show actual/approved mutations, skipped/deferred/support classes, model projection and complete-acceptance not-established status separately. Do not change promotion permissions or object owners. |
| F11 | completion routing and existing Canvas header/lens/overview | Industry identity may open an unrelated Enterprise Canvas; fallback MOD content and receipt-derived change time | Industry completion opens its existing workspace, preserves legitimate model links, skips wrong Canvas access repair. Guard generic MOD text and keep missing model/strategic/change state honest. |

Actual artifacts remain the original hash-pinned TEL W5/W6 and BNK W1 ZIPs used
in Repairs 01/02. No source content, canonical intelligence or accepted ADR will be
edited. Import-scoped source views remain distinct from durable model-backed truth,
qualified pressures and commercial hypotheses. Existing governance, Evidence and
model handoff services are reused; this is not a new Navigator or dashboard.

Implementation note: inspection of the strict shared-profile/package version
checks showed that no profile change was needed for F07. The existing adapter
already preserves the raw source payload, so the final correction uses the
existing factual read-model fallback and embedded Evidence selector. The shared
profile, Researcher pack metadata and retained package versions remain unchanged.
