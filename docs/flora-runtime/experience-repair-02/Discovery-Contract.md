# Experience Repair 02 — discovery contract and ownership assessment

Pinned main: `acaf99cd26c5faf7719cf0fbda48edef6bc97c59`, merged #537 and #530–#536.
Main contains the tested Repair 01 commit `68ec48677382f46e89ad5f9feabf037a5c836194`.
Recorded before implementation. Accepted ADRs are unchanged; ADR-014/024 retain
the already documented header/body status ambiguity.

## Existing journey and owners

Home/Intelligence use static curated Banking links plus Repair 01's permission-
filtered Industry import counts. `/digital-twins` uses `governed_twin_list` over
Canvas access records; it does not enumerate Industry package workspaces.
Factory completion correctly opens `/blueprint-import/<run>/intelligence` for an
Industry package. That workspace already links enterprise dossiers, Evidence and
Unknowns. `/flora/banking/inspect` is shadowed by the earlier Banking catch-all;
`/industries/uk-banking` already reaches the source-only inspection adapter.

Existing owners: BlueprintPackageRegistry (immutable receipt),
project_twin_identity/GovernedIdentityResolutionRepository (explicit metadata and
confirmed identity), CandidateStagingRepository (source candidates),
ImportHumanReviewRepository (review acknowledgement), ImportLifecycleService
(receipt-backed current/superseded/archived state), EnterpriseModelRepository
(durable state), EnterpriseCanvasAccessRepository and existing access functions
(visible Canvas records). No new canonical registry or identity owner is needed.

## Smallest read-only extension

Extend `digital_twins.py`, the existing discovery/presenter, with an in-memory
projection and shared card renderer. Preserve the compatibility Canvas-list API.
Home, Intelligence and Digital Twins consume the same projection; destinations
remain the existing Banking, Industry workspace/inspection and Enterprise Canvas
routes. No source/data adaptation, model merging or backfill is performed.

| View field | Derivation / boundary |
| --- | --- |
| Presentation key | Namespaced existing route/import/Canvas identifier; view key only, never stored canonical identity |
| Display name / type | Curated feature's existing label; explicit governed package subject name or package ID; canonical Enterprise ID for Canvas. Never ZIP filename, name guessing or fuzzy matching |
| Source / owner | Curated repository context, import identity/staging/lifecycle, or existing Enterprise Model + Canvas access |
| Status / current | Source-curated; Candidate; Under review when existing acknowledgement exists; current partial promotion; Superseded/Archived from existing lifecycle; Model-backed only for persisted valid model; Unknown/Unavailable otherwise. These are display labels, not a new lifecycle enum |
| Identity | Source package, import run, governed Twin and primary subject, presentation route and canonical Enterprise remain distinct. Cross-references use explicit access-record import links and existing governed ID resolution only |
| Visibility | Curated public pilot retains existing access. Other items require authentication and existing owner access/inspection or Canvas ACL checks. Workspace-bound entries must match the active workspace, even under broad enterprise grants. Legacy unscoped records still require owner checks |
| Dates | Meaningful intelligence update Unknown unless explicitly supplied by the owner. Pilot snapshot and lifecycle/review event dates are separately labelled; receipt/access timestamps never become intelligence effective dates |
| Destination | Staged Industry content → existing Industry workspace; unstaged receipt → existing inspection; authorised Canvas → existing Canvas route; curated Banking → existing pilot. Industry identities never become fake Canvas entries |
| Availability / Unknowns | Missing stage/model/identity or unreadable owner state remains explicit. Anonymous/empty/no-access messaging does not confirm protected record names, totals, IDs or destinations |

The projection reads owner outcomes; it never calls promotion, model save,
identity confirmation, access repair, or `EnterpriseCanvasService.get_canvas`
(which has an existing repair side effect). Model presence alone is not complete
Commercial Digital Twin assurance. Source-only and imported dossiers remain
separate even when their display names match. Historical promoted releases stay
inspectable, with current state explicit; deleted/cancelled candidates are not
invented as available current intelligence.

Permissions are checked before constructing names, item counts, IDs and links.
No inaccessible record is reported as an item or included in visible totals.
Unreadable state uses generic unavailable text, never raw storage exceptions.
The projection does not claim no intelligence exists merely because this account
has no visible records. This is a navigation/read-model repair, not a new dashboard,
canonical Banking adapter, economic engine or unified intelligence store.
