# Security Repair 01A trust boundary assessment

Pinned main: `dc9203e6880f8722e821d39cf53b689732edb0e7`.
The earlier 12 isolated reproduction checks ran against that unchanged SHA before
implementation. The new same-case acceptance comparisons reproduce rejection
requirements on main and exercise the repaired code without a fixture identity
provider. This increment supplies no working owner authentication mechanism.

## Boundary inventory and changes

| Boundary | Original defect or exposure | Repair and remaining owner |
| --- | --- | --- |
| access.py | Unsigned identity/workspace/enterprise/role cookies, header flag, shared actor and legacy session establish authority | Only the server verification seam can supply authority. It returns None in 01A; no flag, header, cookie or caller object can enable it. Existing capability policy remains here. |
| Workspace scope | Broad enterprise grants evaluated before explicit resource workspace | Resource workspace must match selected workspace before wildcard enterprise access. |
| pilot_auth.py | Shared credentials issue non-revocable owner cookies from environment claims | Legacy issuance raises PermissionError, resolution returns None and validation is disabled. Sign-in explains the closed transition. Historical bytes are untouched. |
| pilot_import.py | Environment mode grants upload/inspect/review and shared commercial editing | No shared grants or anonymous upload; deployment mode alone does not establish a verified perimeter. |
| Main HTTP handler | Mutations and some protected reads dispatch without authorisation; body read before policy | Explicit source-public GET allowlist; protected GET/HEAD denied before data access. All privileged POST requests denied before body parsing/dispatch. |
| Public reference preference | Resume-cookie POST, no intelligence write | Exact configured-Origin check permits only this non-authority navigation cookie. Missing/mismatched/null origin denies. It cannot grant identity or capability. |
| Legacy workspace HTTP listener | Alternate unauthenticated feedback/logbook writes | Legacy listener closed for GET/HEAD/POST; use the canonical main entry point for public source views. |
| Blueprint review | Shared actor can claim Chief Architect; GET prepares defaults/mappings/plans | No shared authority; reviewer/approver/executor must match verified identity. GET renders existing state only; explicit prepare_review service handles preparation and is unreachable by public HTTP in 01A. Coordinator checks authority before writing jobs. |
| Import panels/history | Registry enumeration before access; global tombstones and source-as-canonical Banking row | Public entry does not enumerate private registry or candidate fingerprints. Authorised panel records are filtered before output. Unscoped tombstones stay offline; false source-derived canonical history row removed. Package history retains inspection checks. |
| Executive workspace | Existing versus absent package can produce different unauthenticated responses | Verify actor before reading registry. Transport denies protected routes regardless of guessed IDs. |
| Financial review/apply | Direct services and routes mutate without actor | Route denial plus capability/resource checks at service entry, before run loading or mutation. |
| Brief generation | Browser headers used directly for attribution | Route denied; service requires verified capability/resource access and exact actor/workspace correspondence. |
| Canvas feedback | Separate direct header/cookie role parser and user-provided role attribution | Shared server role evaluator; identity-derived role attribution; existing resource policies retained. |
| Commercial Context | Shared pilot grants and actor-only checks | Shared grants removed. Existing scope/capability policy remains; no production actor can resolve in 01A. |
| Recovery/destruction | Upload permission opens storage recovery; direct deletion/cleanup lacks authority | HTTP closed; dedicated recovery capability at execution and direct cleanup; candidate deletion requires import administration and package scope. |
| Architecture export/support | Unverified attribution/shared support-token route | Protected transport closed; export attribution uses shared verified resolver; shared support-token authorisation disabled. |
| User/workspace administration | No verified administration service exists | No route or provisioning mechanism added; unknown/administrative routes default denied. |

## Service and repository responsibilities

Product services are policy boundaries. Internal repositories, archive reception,
canonical constructors, lifecycle commit helpers and deterministic memory/pipeline
functions remain trusted application internals; they are not public authority
issuers. HTTP cannot reach mutating dispatch or invoke them using browser claims.
Existing promotion plan fingerprints, rationale, lineage, constructor checks,
compensation and receipts are retained; there is no automatic promotion.

The security seam is deliberately closed, not a configurable placeholder issuer.
01B must add actual verification, server membership, revocation, CSRF and recent
reauthentication before enabling any privileged route. No SQLite, human account,
enrollment, session issuer or production activation flag is implemented in 01A.

## HTTP semantics and disclosure

No accepted protected browser mutation exists in 01A, including same-origin
requests. This closes CSRF as well as authentication paths without pretending a
CSRF-token validator exists. Before 01B opens mutations, it must validate both
session-bound CSRF and configured Origin. The sole public POST exception changes
only a non-authority reference-navigation cookie and requires exact Origin.

The public GET rules cover repository Banking presentations, public discovery
shells and source Evidence views. They do not permit arbitrary imported package,
Enterprise Canvas, financial-run, filesystem or private Evidence repository reads.
Protected routes use generic denial without sensitive IDs, names or counts.
Unscoped tombstones remain unchanged and are not globally rendered; restored
authorised tombstone visibility requires evidence-backed workspace resolution.

## Historical operational warning

The current lifecycle declaration omits the four generic acceptance fields that
produce the prior warning. This change does not fabricate PASS results, suppress
an authenticated operational failure or rewrite the historical declaration.
Unauthenticated setup no longer reads its candidate-backed operational panel.
Declaration/schema reconciliation remains a separate documented dependency.

## Scope limits

No Render access, deployment, environment change, owner provisioning, persistent
root change, reassignment, migration or production intelligence mutation occurs.
Possession of OS/filesystem access remains outside the browser threat boundary.
Public curated Banking remains source-labelled and does not acquire canonical
assurance through this repair.
