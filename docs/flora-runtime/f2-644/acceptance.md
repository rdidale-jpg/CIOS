# Owner acceptance and rollback

Use a nonproduction checkout and a legitimately authorised existing session/workspace. No production data setup is performed by this PR.

1. Confirm ordinary UK → Banking → Lloyds exploration and all seven streams remain unchanged.
2. Where a current eligible Banking Financial run already exists, open Banking → **Financial analysis**. This link is absent otherwise; a page load creates nothing. Existing trusted F1 `create_run` remains an explicitly opted-in, capability/resource-guarded service; this sprint adds no anonymous endpoint or automatic startup run.
3. Inspect the UK household retail-deposit stocks, explicit dates, Reported labels, zero-inclusive chart and Calculated £1.555bn/0.0825% differences. Confirm these are sector stock comparisons, not named-bank results or adjusted flows.
4. Expand **Measurements and chart data** for source-scale amounts; expand **Sources, method and limitations** for original source, licence, definition, formula and vintage caveats. Open analysis detail, then test Back/Forward.
5. Select Lloyds within the Banking context, open Financial analysis and switch Forces/Back/close. Selection/layer context persists. Directly entering Lloyds must not display BoE as Lloyds financials.
6. Test desktop, both iPad orientations, mobile, keyboard, touch, 200% text, forced colours and no-JS disclosure. Browser previews are emulated Chromium, not physical Safari or screen-reader certification.
7. In isolated nonproduction source-owner state only, withdraw/revoke the source and confirm the entry disappears, direct Main is denied and standalone detail contains no dependent measurements, source IDs or calculation. History is retained. Restore only the exact eligible reviewed revision to reproduce it.
8. Verify cross-tenant/no-ACL sessions cannot infer the private entry or figures.

Owner decisions: accept the bounded Main composition and readability; accept the actual BoE proof and explicit limits; accept the finite reusable contracts without interpreting synthetic tests as admitted bank data; review source/privacy and regression evidence. Five-bank sources, EAR-1 decisions, Proposed ADR-027, physical device certification and production setup remain separate.

## Rollback

No schema migration, canonical mutation, source permission change or data conversion is introduced. The effective feature gate is an existing eligible, authorised Financial run; no run means no entry. Source withdrawal removes its intelligence at the owner boundary without deleting history. For implementation rollback, revert the F2 change through reviewed GitHub process to the verified F1 code cut, leaving existing run/source history intact. Do not delete runs or restore/overwrite production data. No rollback deployment is executed here; any later release or Render action requires separate owner authorisation and readiness validation.
