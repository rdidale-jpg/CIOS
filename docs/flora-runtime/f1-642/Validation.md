# Reproducible validation and visual comparison

The final exact SHA, hosted run URLs/outcomes and proof manifest are recorded in the draft PR's completion comment. Committed previews show the candidate application; the final proof is regenerated after commit so its `head` is the actual tested SHA, rather than embedding a self-referential SHA in this commit.

## Checks

| Layer | Scope |
|---|---|
| F1 |85focused tests: real source/typed stock semantics; synthetic flow/fiscal/calendar/sign/precision/assumptions; actual candidate repository/reload/idempotency; exact derivations; use/revision withdrawal; forged/missing payload; real tenant/resource/ACL/capability denial; protected write rollback; canonical-operation rejection; all173prior source bytes and unchanged comparator |
| Existing regression gate | `python tools/ci/flora_ci.py --output /tmp/flora-f1-ci`:27suites,388strict security; unchanged versioned failure/skip comparison and integrity/audit checks |
| Existing semantics/history | Existing FIG-1 hosted workflow:53FIG tests and629semantic/compatibility/source/visual/history cases. Three stale successful inventory/design-epoch assertions are explicitly corrected; no approved failure/skip baseline or comparator code is changed |
| Existing products | Existing main workflow:371Technology/Offers/library/triggers/development/visual/product checks and39CI-control tests |
| Real source proof | `python tools/research/f1_proof.py --output /tmp/flora-f1-proof`:actual retained BoE inputs, existing run storage/reload, deterministic calculation, withdrawal/sanitized reads, unchanged historical run; synthetic authority only |
| F1 browser | `python tools/research/f1_proof.py --output /tmp/flora-f1-proof --preview --baseline-root /path/to/validated-main`:70checks, including equivalent baseline/current desktop/iPad landscape/iPad portrait/mobile,320px,200% text with intact amounts, keyboard/touch sources, source licence, anonymous denial, direct URL/history and retained seven streams/two-selection journey |
| Full visual browser regression | `python tools/ci/flora_vp2_preview.py --output /tmp/flora-f1-visual`:709existing checks, including retained destinations/lenses/global tools, responsive/zoom/touch/keyboard/source access and loopback performance samples |

Selectors overlap and are not summed as unique coverage. Full-gate acceptance requires the exact existing36inherited failures and10approved skips, with zero unexplained signature changes. A direct financial compatibility subset also exposes five of those inherited authority-related failures; it is not falsely described as a clean raw pytest suite. Full comparator matching, not baseline refresh, determines acceptance. Physical iPad/Safari, production availability and screen-reader certification are not claimed.

## Investigated issues

The first working-tree full run correctly rejected the two new unregistered source files in two history-dependent suites. The existing inventory now names exactly those two hashes, preserving all earlier bytes. A new regression verifies the old173-entry cut and unchanged comparator against baseline. The BIE3 and unified successful-count assertions now expect the exact175file inventory. The FIG-1 test verifies that the **accepted FIG-1 design commit** changed no runtime/architecture/history; it no longer mistakes a later commissioned implementation for that historical design. No original source identity, approved failure/skip, comparator tolerance or old research byte is refreshed.

Early browser failures were isolated harness startup/path coupling and the new view's mobile table/legacy header at200% text. The Financial hash now uses an existing pure helper; the proof starts the full runtime against its complete checkout, and the F1-only page gets a responsive table/header treatment. These findings did not require production configuration or global visual redesign.

## Before/after

The comparison opens the **same non-production candidate run** with the validated main reader and the new reader under identical synthetic authority. The old reader ignores the typed extension and shows its generic empty canonical-claim review; the new reader displays the sourced analytical result without canonical promotion. No before screenshot is presented as a real historical production run or approved import. All original seven scenes,21responsive variants,7portrait scenes and23delivery assets remain unchanged; existing asset/hash and navigation suites plus the full visual browser run check preservation.

| Device | Before | After |
|---|---|---|
| Desktop | ![Baseline Financial reader](previews/before-desktop.jpg) | ![Typed analytical result](previews/after-desktop.jpg) |
| iPad landscape | ![Baseline iPad landscape](previews/before-ipad-landscape.jpg) | ![Candidate iPad landscape](previews/after-ipad-landscape.jpg) |
| iPad portrait | ![Baseline iPad portrait](previews/before-ipad-portrait.jpg) | ![Candidate iPad portrait](previews/after-ipad-portrait.jpg) |
| Mobile | ![Baseline mobile](previews/before-mobile.jpg) | ![Candidate mobile](previews/after-mobile.jpg) |

![200% mobile text; amounts intact](previews/after-mobile-200pct.jpg)

Workflow artifacts contain sanitized proof/browser results and previews only. Do not upload private CI scratch directories, authority databases, enrollment deliveries, cookies, environment configuration or raw tool logs.
