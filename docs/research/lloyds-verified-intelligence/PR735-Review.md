# Independent recheck of the proposed #735 integration

Reviewed candidate: `c7122f89f56871685772767eab207fd93b7550ce`. Current main verified as `0a6423fe3a32d0a0d5d11fe9d7027859e94c6df7`. #735 is draft, unmerged and mergeable. **No explicit merge approval has been assumed from the conditional wording of this commission.**

## Rechecked evidence

- GitHub's current PR metadata reports the exact candidate and 23 files. Local Git scope matches the committed inventory; the local working tree at that candidate is clean.
- The candidate's QA was rerun independently. It reconstructs all recovery manifests from immutable research refs; verifies the eight proposal fingerprints, 13 Decimal reconciliations, note/crosswalk/source identities, 17 local links and exact two-workflow delta; all pass.
- Exact Git tree comparison proves runtime, original research, Source/Financial/security/canonical files, artwork and Pipeline code unchanged. Audit #734 is a parent through the current main baseline; its approved tree remains `576599df46ebacdceef4b74bd8b3e39b7cdd772e`.
- The actual 58-case focused test command was rerun at the immutable #735 candidate: **58 passed**. This is not presented as an independent security review by another agent.
- Current hosted runs are successful at that exact SHA: [full gate](https://github.com/rdidale-jpg/CIOS/actions/runs/45883477856), [Factory](https://github.com/rdidale-jpg/CIOS/actions/runs/45883432485), [AUTH-2](https://github.com/rdidale-jpg/CIOS/actions/runs/45883432510), [Economics/browser](https://github.com/rdidale-jpg/CIOS/actions/runs/45883432489). A superseded duplicate trigger was cancelled by concurrency, not an unaddressed failed check.
- The completed full-gate job log was inspected, not just its green badge. It checks out `c7122f89...`; the real security suite records **388 passed, zero issues**. Domain/financial/legacy retain the expected 1/12/23 failures and ten domain skips with zero comparator issues. Earlier deliberately failing/skipped security lines belong to the gate's failure-behaviour self-tests; they are not failures of the real security run.
- Existing exact-head local full evidence records 1,432 cases, 1,386 passes, 36 inherited failures, ten skips, zero issues; 146 integrity comparisons, 15 audit chains and 17 record digests. The same 21 previously repaired baseline exceptions remain passing. No baseline file changed.
- Reversing the candidate binary diff in a temporary Git index returns the main/audit tree exactly. No real branch, runtime store or production data is altered by this rollback test.

The earlier Economics failure was a historical scope audit applied to a later branch. The original frozen validator/inventory are unchanged; its approved-cut audit and the fresh current-head browser check both pass. This CI repair is part of the exact 23-file candidate, not a new source permission.

## Compatibility and conditional integration procedure

The candidate descends directly from verified main plus its two recovery/CI commits. No current-main conflict or runtime dependency change was observed. Acceptance is limited to recovered research and isolated proofs, with original-byte/publication/identity limitations retained. It does not authorise §2 output, §5 PDF links, canonical imports or production activation.

After the owner explicitly approves merging this exact SHA, recheck PR head, scope, main and successful latest checks, then use the existing protected GitHub merge flow with the approved-head guard. Do not squash/rewrite or add unrelated work. Verify the merge tree equals the approved candidate tree `a51265aa64217bbfc673cdff5e9fbb39da96fe2e` when main is unchanged; otherwise stop for a reviewed reconciliation. Run applicable post-merge integrity/security/comparator checks at the resulting main SHA. Record any paths-filtered hosted jobs honestly; do not infer a fresh run where none occurred. No Render operation is authorised.

This subsequent research draft is stacked on #735's branch so its new-file diff stays separate and does not silently incorporate the still-unmerged candidate into main. Retargeting it after an authorised #735 merge is a normal dependency update; no acceptance of the new intelligence is implied.
