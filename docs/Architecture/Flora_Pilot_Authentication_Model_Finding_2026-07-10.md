# Flora Pilot Authentication Model Finding — 2026-07-10

## Conclusion

**C. The pilot has no complete implemented authenticated-user model.**

The current deployed Flora web surface has public product routes plus a small product-session access helper that can read identity, workspace and roles from request headers or cookies. The repository does not contain a real sign-in route, session issuer, membership database, owner database, or deployment-backed identity provider wiring for normal browser navigation. Blueprint import is therefore enforcing a permission model that exists only as request metadata, not as a deployed browser sign-in flow.

## Evidence summary

- The three-tile Flora home route is public. `/`, `/flora`, and `/flora/` render `_flora_home_page()` without consulting any access helper.
- Normal legacy Flora feature routes such as `/morning-edition`, `/settings`, `/logbook`, `/case/*`, `/radar`, and `/scoring` render directly and are not authenticated.
- Enterprise Canvas and Financial Intelligence result routes do use access helpers, but their identity source is still headers/cookies, not a sign-in flow.
- The access helper accepts `X-Flora-User`, `X-Flora-Enterprises`, `X-Flora-Active-Workspace`, and `X-Flora-Roles` as trusted proxy headers when `FLORA_TRUST_PROXY_HEADERS` is not disabled, and otherwise reads `flora_user`, `flora_enterprises`, `flora_active_workspace`, and `flora_roles` cookies.
- There is no database-backed membership or owner-role store. Workspace membership is the enterprise list carried in the request metadata. Owner status is the presence of a role string in request metadata plus a recognised active workspace.
- Existing tests pass synthetic `X-Flora-*` headers and synthetic Flora cookies that a deployed browser will not send unless a proxy/session layer injects or issues them.

## Required question answers

1. **Does the original pilot have a real user sign-in flow?**  
   No repository sign-in flow was found. The web route table contains no login route or cookie/session issuance. Identity is only read from incoming headers/cookies.

2. **Is the three-tile landing page public or authenticated?**  
   Public. The route dispatch renders `_flora_home_page()` for `/`, `/flora`, and `/flora/` without an authentication check.

3. **Where is the current user identity normally obtained?**  
   `authenticated_flora_user(headers)` returns `X-Flora-User` when trusted proxy headers are enabled, otherwise `flora_user` from the Cookie header.

4. **Identity source classification:**
   - Application session: not implemented as a server-side session issuer/store.
   - Cookie: supported only by reading `flora_user` from incoming cookies.
   - Trusted reverse-proxy headers: supported by reading `X-Flora-User` when enabled.
   - Render environment variables: not used for account identity; only support/admin token checks and runtime host/port/revision settings appear.
   - Fixed pilot identity: not implemented as a runtime fallback.
   - Database membership: not implemented.
   - No implemented mechanism: no end-to-end browser sign-in mechanism exists in this repository.

5. **How is an active workspace normally selected?**  
   `active_flora_workspace(headers)` first reads `X-Flora-Active-Workspace` or `flora_active_workspace`; if absent, it falls back to the sole concrete enterprise in `X-Flora-Enterprises`/`flora_enterprises`. If multiple concrete enterprises exist and none is explicitly active, no active workspace is resolved.

6. **Where are workspace memberships stored?**  
   In request metadata only: `X-Flora-Enterprises` or `flora_enterprises`. No durable membership repository was found.

7. **Where is the owner role stored?**  
   In request metadata only: `X-Flora-Roles` or `flora_roles`. Owner aliases are interpreted by `raw_flora_roles()`, `flora_roles()`, and `is_cios_owner()`.

8. **Which existing route successfully resolves a user, workspace and role?**  
   No live browser route can be proven to do this without a cookie/proxy identity being present. In code, Blueprint import resolves account, active workspace, membership and owner-derived Blueprint authority via `blueprint_upload_authorisation(headers)`. Enterprise Canvas resolves user and workspace access, but not owner role. Financial Intelligence result access resolves user and enterprise access, but not role.

9. **Do any live routes currently use authenticated identity?**  
   Yes, some routes use request identity if provided: Blueprint import, Blueprint history/review/promotion, Enterprise Canvas, Enterprise Canvas feedback, and protected Financial Intelligence result/support report routes. But this does not prove a deployed browser sign-in model exists.

10. **Are tests passing synthetic identity headers that the deployed browser never sends?**  
    Yes. Tests construct `X-Flora-User`, `X-Flora-Enterprises`, and `X-Flora-Roles` headers directly, and some tests construct Flora cookies directly.

11. **Was Blueprint import implemented against an identity model that does not yet exist in the pilot?**  
    Yes. Blueprint import assumes a canonical product-session identity with account, workspace and roles, but the repository provides only metadata readers and test-supplied headers/cookies, not a browser sign-in/session issuer.

12. **Is `package.upload` intended to be protected in the pilot, or was this enforcement introduced prematurely?**  
    The architecture/specification intends package upload to be protected, but enforcement was introduced before a deployable pilot identity/session mechanism existed. Anonymous upload must remain denied; the missing piece is an explicit pilot-safe owner identity mechanism or real upstream identity configuration.

## Route comparison

| Surface | Identity use today | Workspace source | Role source | Outcome for anonymous browser |
| --- | --- | --- | --- | --- |
| Three-tile home (`/`, `/flora`) | None | None | None | Renders public landing page |
| Legacy features (`/morning-edition`, `/settings`, `/logbook`, `/case/*`, `/radar`, `/scoring`) | None | None | None | Render public pages/forms |
| Enterprise Canvas | Requires `authenticated_flora_user()` and enterprise access | `X-Flora-Enterprises` / `flora_enterprises` | Not required for view | 403 |
| Enterprise Canvas feedback | Requires user, enterprise access and role-like permission | `X-Flora-Enterprises` / `flora_enterprises` | `X-Flora-Roles` / `flora_roles` | 403 |
| Financial Intelligence result/support report | Requires support token or user enterprise access | `X-Flora-Enterprises` / `flora_enterprises` | Not required | 403 |
| Blueprint import GET | Requires `blueprint_upload_authorisation()` | active workspace from header/cookie or sole enterprise | roles from header/cookie; owner aliases inherit package permissions | 403 with diagnostics |
| Blueprint upload POST | Same as GET, then validates package | same as GET | same as GET | 403; no package state written |

## Why Blueprint currently resolves anonymous

The live diagnostics show “Not signed in” and “No active workspace” because normal browser navigation to `/blueprint-import` carries neither `X-Flora-*` identity headers nor Flora session cookies. The route is functioning correctly according to its current access helper: no incoming account metadata means no account, no workspace, no membership, no owner role and no `package.upload` permission.

## Deployment dependency

The current code would require one of these deployment dependencies to identify a user:

1. a trusted upstream reverse proxy or identity provider that injects `X-Flora-User`, `X-Flora-Enterprises`, `X-Flora-Active-Workspace`, and `X-Flora-Roles`; or
2. an application route/session mechanism that issues `flora_user`, `flora_enterprises`, `flora_active_workspace`, and `flora_roles` cookies.

Neither dependency is implemented as a complete sign-in model in this repository. Render environment variables do not currently identify a normal account/workspace/role.

## Smallest safe correction

Do not grant Blueprint import to anonymous users and do not trust arbitrary browser-supplied identity headers as the long-term model.

For the current pilot, the smallest safe correction is to add an explicit **pilot-only owner session bootstrap** that is gated by a deployment secret, sets signed or otherwise tamper-resistant Flora session cookies for a configured pilot owner/workspace/role, and is clearly marked as temporary. The session should not hard-code Rob’s email or ID; it should read a configured pilot owner identifier and workspace from Render environment variables. Migration path: replace the bootstrap with the future canonical identity provider/session service while preserving the existing access helper contract (`authenticated_flora_user`, `active_flora_workspace`, roles/permissions).

Alternative if an upstream identity proxy already exists outside this repository: configure it to inject the required Flora identity headers and set `FLORA_TRUST_PROXY_HEADERS=1`, but only if those headers are stripped from public client input at the proxy boundary.

## Security boundary

- Anonymous users remain denied for Blueprint import and upload.
- Browser-supplied `X-Flora-*` headers must not be treated as trustworthy unless Render is behind a proxy that strips client headers and injects trusted identity.
- Owner authority should be explicit, workspace-scoped and temporary for the pilot.
- Package upload remains a protected operation because it stores potentially confidential enterprise intelligence and feeds a governed import workflow.
