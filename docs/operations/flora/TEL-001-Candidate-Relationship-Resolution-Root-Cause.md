# TEL-001 Candidate Relationship Resolution — Root Cause

## Merge conclusion

**SAFE TO MERGE.** Candidate endpoint resolution is a read-only inspection
operation. It neither changes candidate lifecycle state nor crosses the explicit
promotion boundary.

## Architectural answer

1. **Candidate-to-candidate resolution is intended: YES.** Accepted ADR-012
   requires object effects and original identities to be inspectable before
   acceptance, distinguishes package acceptance, candidate structured
   intelligence and canonical state, and requires staging without canonical
   mutation. The import runtime specification likewise makes the Acceptance
   Workspace responsible for inspecting package data, mappings, source location
   and proposed effects before promotion. A deterministic edge between two
   staged stable IDs is therefore inspectable candidate structure, not a
   canonical mutation.
2. **“Governed” did not mean “endpoint resolvable.”** In the old generic table it
   counted `SemanticObject.governance == "governed"`: an accepted/promoted
   canonical-state label. The adjacent “unresolved” column independently counted
   `not eligible_conclusion`. That property means a record is not an eligible
   executive conclusion (for example, an edge has no narrative statement); it
   does not mean its endpoints are missing. Human review and owner assessment
   were not consulted by either count.
3. **Canonical owner.** `semantic_twin.resolve_relationships` owns exact endpoint
   resolution; `enterprise_associations` is its typed Enterprise-query consumer.
   Advanced Inspection and the executive pages consume those same functions.

## Forensic trace and first divergence

The ZIP manifest declares one required 308-record
`record_sets/relationship_register_wave5.ndjson` collection. The validator and
Industry Delta adapter preserve each source ID, stage all 308 records in import
run `bpi-run-bd3924d85125e308`, and semantic assembly preserves `source`,
`target`, and `relationship_type` in each object's attributes.

`REL-W2-001` is the representative end-to-end trace:

| Boundary | ID / lookup | Population | Result |
|---|---|---|---|
| ZIP record | `REL-W2-001`: `ENT-BT` → `PROG-BT-TRANSFORMATION`; `Enterprise owns Programme` | governed Relationship register | present |
| Manifest | required Relationship register, count 308 | immutable ZIP | declared |
| Validator / stage | original ID `REL-W2-001`, unchanged endpoint IDs | checksum-derived import run | accepted candidate |
| Semantic identity | `ENT-BT`, `PROG-BT-TRANSFORMATION` | 1,060 candidates in this run | both present exactly once |
| Resolver | exact case-insensitive stable-ID lookup | non-Relationship objects in this `SemanticTwin` only | candidate relationship resolved |
| Enterprise query | match Enterprise endpoint and return the other typed endpoint | same resolver output | Programme returned with source type and Relationship ID |
| Diagnostics / dossier | same query functions | request-time read model | reconciled and rendered |

The **first divergence was the old Advanced Inspection generic technical table**:
it used executive-conclusion eligibility as its “Unresolved” measure. Since all
308 standalone Relationship candidates are structural records rather than
narrative conclusions, it printed 308 unresolved even though their endpoint
identities had never been tested. The earlier Enterprise read path also did not
consume standalone Relationship objects. No promotion lookup failed; endpoint
resolution was absent from that read boundary.

## TEL-001 source truth

* The 308 Relationships reconcile as **252 candidate-resolved**, **56
  candidate-unresolved (endpoint missing)**, and **0 promoted**. Every row and
  the type/family aggregate appear in the companion reconciliation.
* The 56 are truthful edges to aliases, sub-scopes, classification buckets, or
  absent IDs rather than staged business-object identities. Flora does not
  invent these endpoints.
* `REL-W2-001` explicitly relates BT to `PROG-BT-TRANSFORMATION`.
* The BT/Verizon Programme is `PROG-BT-VERIZON-JV`. No Relationship object has
  that Programme as either endpoint. Its structured Programme object supplies
  `owning_enterprise: ENT-BT`, so the existing canonical ownership rule—not
  narrative inference—associates it to BT.
* The BT/Verizon Opportunity is
  `OPP-BT-VERIZON-JV-INTEGRATION`. `REL-W4-183` explicitly links it to `ENT-BT`
  with type `Opportunity targets Enterprise`; both endpoints resolve as
  candidates.

## Identity, scope, coexistence, and direction

Endpoint lookup searches the immutable source/canonical ID exposed by
`business_object_id`; it does not search names, prose, aliases, generated
candidate-record IDs, or a global candidate store. A `SemanticTwin` is assembled
from exactly one package/import run, so its local identity registry is the safe
scope boundary. Duplicate IDs inside that scope produce `endpoint ambiguous`;
absent IDs produce `endpoint missing`; malformed edges and unsupported types
remain distinct.

Candidate inspection does not blend the canonical store into this candidate read
model. Consequently a promoted version cannot silently shadow a candidate here;
canonical comparison and promotion planning remain the accepted mapping/review
boundary. If a future read model intentionally supplies governed objects, the
resolver reports `promoted relationship resolved` only when the Relationship and
both endpoints are governed.

Enterprise association lookup preserves the source relationship type and ID. It
supports the existing Enterprise-centric inverse query (the Enterprise may be
either endpoint), but does not rewrite or duplicate the stored direction and does
not make arbitrary relationships bidirectional.

## Why the other diagnostic families differed

The 50 Membership candidates are not standalone Relationship objects and do not
participate in Enterprise Programme/Opportunity endpoint resolution. Their old
“50 unresolved” value meant “50 records not eligible as executive conclusions,”
not missing membership endpoints. Runtime membership behavior is therefore
unchanged.

Transformation Programmes reported zero unresolved because their substantive
summaries satisfied executive-conclusion eligibility. Relationships,
Memberships, Enterprise wrappers and Market Participant wrappers were structural
or identity records and failed that different eligibility predicate. The
different counts never represented a shared endpoint-resolution disposition.

## Governance preservation

Resolution constructs an immutable request-time result. It writes no review,
assessment, promotion, recommendation, mapping, ledger, or canonical object.
Candidate objects continue to display “Imported candidate — not yet reviewed,”
“Not promoted,” “Assessment not yet performed,” and “Not eligible.” A fresh
import is not required because the already-staged source identities and edges are
queried at read time.

## Resulting Enterprise sets

| Enterprise | Expected/rendered Programme IDs | Expected/rendered Opportunity IDs | Result |
|---|---|---|---|
| ENT-BT | PROG-BT-TRANSFORMATION; PROG-BT-VERIZON-JV | OPP-BT-AI-ENGINEERING; OPP-BT-AIOPS; OPP-BT-VERIZON-JV-INTEGRATION | PASS |
| ENT-CITYFIBRE | PROG-CITYFIBRE-WHOLESALE | OPP-CITYFIBRE-PROJECT-GIGABIT; OPP-CITYFIBRE-WHOLESALE | PASS |
| ENT-OPENREACH | PROG-OPENREACH-FTTP | OPP-OPENREACH-BDUK-DELIVERY-ASSURANCE; OPP-OPENREACH-CP-ENABLEMENT; OPP-OPENREACH-FIBRE-AUTOMATION | PASS |
| ENT-TALKTALK | PROG-TALKTALK-PXC-DEMERGER | OPP-PXC-PLATFORM-EFFICIENCY; OPP-TALKTALK-COST | PASS |
| ENT-VMO2 | PROG-VMO2-LUMI-AI; PROG-VMO2-MOBILE-TRANSFORMATION | OPP-VMO2-AI-CX; OPP-VMO2-MOBILE-RAN-AI-ASSURANCE; OPP-VMO2-NEXFIBRE-MIGRATION | PASS |
| ENT-VODAFONETHREE | PROG-VT-5G-SA; PROG-VT-INTEGRATION | OPP-VT-ENTERPRISE-5G; OPP-VT-NETWORK-AI-OPS; OPP-VT-WHOLESALE-REMEDY-ASSURANCE | PASS |
