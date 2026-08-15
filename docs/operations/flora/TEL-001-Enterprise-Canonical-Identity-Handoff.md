# TEL-001 Enterprise Canonical Identity Handoff

## Decision

**SAFE TO MERGE.** The identity-handoff hypothesis was proven at the deployed
presentation boundary: a presentation route key (for example `bt-group`) was
being treated as the Relationship subject even though the governed endpoint is
the imported object ID (`ENT-BT`). The correction is read-only, generic, and
scoped to the assembled candidate Twin. No fixture, candidate, Relationship,
governance, assessment, recommendation, or promotion state is changed.

## Architecture and mandatory BT trace

The staging adapter owns imported business-object identity. `business_object_id`
returns the immutable `original_source_id` (falling back to the candidate record
ID). `assemble_semantic_twin` owns the Enterprise read model. It now retains two
explicitly different values: `presentation_key`, derived for navigation, and
`identity_key`, supplied by the candidate's `enterprise_id`/canonical identity.
`resolve_relationships` and `query_subject_associations` own the import-scoped
Relationship read path.

### Route / presentation identity

- Route: `/blueprint-import/{import_run_id}/enterprises/bt-group`
- Route key / slug: `bt-group`
- Display name: `BT Group`

### Enterprise view-model identity

- Object ID: `ENT-BT`
- Source ID: `ENT-BT`
- Canonical candidate ID: `ENT-BT`
- Candidate/import scope: the `SemanticTwin` assembled only from the selected
  `import_run_id` staging summary

### Relationship query input

- Subject ID supplied before the correction: `bt-group`
- Subject ID supplied after route resolution: `ENT-BT`
- Scope supplied: the current import's assembled `SemanticTwin`
- Subject family/type: `enterprise_twin` / Enterprise

### Relationship endpoint truth

- Expected canonical endpoint: `ENT-BT`
- Previous query identity: `bt-group`
- Match: **NO**
- Hypothesis proven: **YES**

The exact runtime chain is
`executive_workspace_page(..., view="enterprise", enterprise_id="bt-group")`
→ resolve the route against `SemanticEnterprise.presentation_key`
→ `_dossier(ent, twin, ...)`
→ `_associated_records(twin, ent, ...)`
→ `enterprise_associations(twin, ent, kinds)`
→ `query_subject_associations(twin, ent.identity_key, kinds)`.

The first divergence was the boundary between presentation routing and the
association consumer. The deployed consumer forwarded the presentation key
instead of handing off the already assembled Enterprise candidate. Exact
endpoint comparison therefore compared `bt-group` with `ENT-BT` and returned no
rows. The correction resolves the route to the import-scoped view model once and
lets the existing relationship owner consume its canonical identity.

No alias table is required: both identities are properties of the assembled
Enterprise read model. No global lookup occurs, so an equal route or object ID
in another import is invisible. Regression coverage explicitly proves colliding
IDs cannot cross import scopes.

## Direct canonical query truth

The governed Relationship records independently supply the expected sets. The
runtime query supplies the queried sets. Dossier business-object attributes
supply the rendered sets. All values below are exact IDs, not title matches.

| Enterprise | Presentation / canonical | Programmes (source = query = render) | Opportunities (source = query = render) |
|---|---|---|---|
| BT Group | `bt-group` / `ENT-BT` | `PROG-BT-TRANSFORMATION` | `OPP-BT-AI-ENGINEERING`, `OPP-BT-AIOPS`, `OPP-BT-VERIZON-JV-INTEGRATION` |
| CityFibre | `cityfibre` / `ENT-CITYFIBRE` | `PROG-CITYFIBRE-WHOLESALE` | `OPP-CITYFIBRE-PROJECT-GIGABIT`, `OPP-CITYFIBRE-WHOLESALE` |
| Openreach | `openreach` / `ENT-OPENREACH` | `PROG-OPENREACH-FTTP` | `OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE`, `OPP-OPENREACH-CP-ENABLEMENT`, `OPP-OPENREACH-FIBRE-AUTOMATION` |
| TalkTalk | `talktalk` / `ENT-TALKTALK` | `PROG-TALKTALK-PXC-DEMERGER` | `OPP-PXC-PLATFORM-EFFICIENCY`, `OPP-TALKTALK-COST` |
| Virgin Media O2 | `virgin-media-o2` / `ENT-VMO2` | `PROG-VMO2-LUMI-AI`, `PROG-VMO2-MOBILE-TRANSFORMATION` | `OPP-VMO2-AI-CX`, `OPP-VMO2-MOBILE-RAN-AI-ASSURANCE`, `OPP-VMO2-NEXFIBRE-MIGRATION` |
| VodafoneThree | `vodafonethree` / `ENT-VODAFONETHREE` | `PROG-VT-5G-SA`, `PROG-VT-INTEGRATION` | `OPP-VT-ENTERPRISE-5G`, `OPP-VT-NETWORK-AI-OPS`, `OPP-VT-WHOLESALE-REMEDY-ASSURANCE` |

For BT, `REL-W2-001` (`Enterprise owns Programme`) resolves `ENT-BT` →
`PROG-BT-TRANSFORMATION`. `REL-W2-014` (`Opportunity targets Enterprise`)
resolves `OPP-BT-AI-ENGINEERING` → `ENT-BT`; the existing type rule identifies
the Enterprise at the target endpoint without making Relationships generally
bidirectional. `REL-W4-183` supplies the Verizon integration Opportunity.

`PROG-BT-VERIZON-JV` remains unassociated because no explicit Relationship has
it as an endpoint. Duplicate Relationship evidence remains in query traces,
while dossier objects are deduplicated by canonical business-object identity.

## Diagnostic and operational acceptance

Advanced Inspection displays Enterprise, presentation identity, canonical
candidate identity, independently derived source sets, query sets, rendered
sets, and exact mismatch detail. A non-empty source set with an empty query is
an explicit failure with the reason “Source relationship truth contains
associations but runtime association query returned none.” A controlled
Enterprise with genuinely empty source/query/render sets still passes.

The unchanged fixture checksum is
`bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.
The reconciled protected populations remain 308 Relationships (252 resolved,
56 explicit missing endpoints), 13 Programmes, and 17 Opportunities. Factual
dimension isolation and candidate governance remain unchanged. This is a read
path correction, so a fresh import is **not** required.

Known out-of-scope presentation defects remain the BT Operating Model raw
dictionary rendering and Financial Position diagnostic/presentation
disagreement.
