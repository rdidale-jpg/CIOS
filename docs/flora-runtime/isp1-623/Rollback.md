# Rollback

This PR changes read-only display policy and restricts a finite set of research-inspection GET routes to existing owners. It contains no schema, model migration, source import, canonical write, Offer change or Pipeline mutation.

Before any later integration, retain this PR's exact commit and the validated main base. Code rollback is a reviewed revert of the ISP1 commit, followed by the unchanged full security/regression and route checks. No database/data restore is required for this change. A revert would also restore the earlier public research-inspection boundary; review that exposure explicitly rather than treating it as a cosmetic rollback. A narrower fix can retain owner-only inspection while reverting specific presentation changes.

Existing research records, source excerpts, artwork, owner decisions and historical evidence must remain preserved. Do not roll back owner research records by deleting them. No Render deployment or rollback is performed in this sprint; owner acceptance and a separate exact-commit deployment decision are required.
