# SI-1 validation and review boundary

Baseline: `fe66516c15726dc45de147ede2674c9172f8cac6` (VEX-1 merge #613). [Full hosted main validation](https://github.com/rdidale-jpg/CIOS/actions/runs/43632122612) is **success**, push/main, on that exact SHA. Remote main was rechecked unchanged before publication. This is a design PR; the SI-1 paths do not trigger the existing path-filtered FLORA runtime workflow. No workflow was changed merely to make a green badge.

## Design acceptance checks

- **12 artifact tests pass:** proposed schemas, three agendas, original source/architecture fingerprints, date/statistic/source binding, reference resolution, distinct gap sets/identity, pain/SWOT boundaries, original artwork, unique IDs, shared cross-stream agendas and exact source URLs.
- **Nine adversarial schema mutations are rejected:** budget, TCV, Pipeline hand-off, named buyer, demonstrated pain, canonical object, qualified pressure, arbitrary score and unsupported early influence.
- **401 browser checks pass**, recorded in [Browser-Validation.json](Browser-Validation.json). Five sizes: desktop 1440×1000, iPad landscape 1180×820, iPad portrait 820×1180, mobile 390×844 and narrow 320×740; all seven views at each size.
- Direct UK → Banking → Lloyds, active stream, Back/Forward, deep links, selected bank/layer preservation, keyboard focus/Enter/Escape, touch, native no-script static navigation, source inspection, forced colours/reduced motion and 200% equivalent CSS-viewport reflow checked. Zero page errors and zero external requests during the recorded browser run.
- **Independent agent review:** 12 artifact tests independently rerun; final finding count zero after corrections. [Critique and dispositions](Independent-Critique.md). The reviewer inspected rather than independently reran the browser suite.
- Seven original artwork hashes verified against accepted design commit `c6bf2280594922db6951c5c36205984c85ca4aea`; all 21 current main WebP derivative hashes verified. None changed.
- No change to runtime, original tests/baseline, source owners, accepted architecture, workflows, dependencies, permissions, Offer/seller/Pipeline services or production configuration. Static discovery indexes 36 existing code modules and 65 available test modules; availability is not a claim that every module was rerun.

**Local versioned gate: PASS — 1,386 passed, 36 matched inherited failures, 10 unchanged skips; all 388 strict security tests passed, zero comparison issues.** The result is recorded separately in [Runtime-Validation-Summary.json](Runtime-Validation-Summary.json). That run covers the unchanged baseline runtime with the design artifacts present; it is distinct from a fresh full hosted job on the eventual documentation-only design SHA. The design artifact tests are rerun after committing, and the exact reviewed SHA is in the PR description.

## Reproduce

From the repository root, in an isolated Python environment with the repository requirements, `jsonschema` and `lxml` installed; Playwright and Chromium are needed for browser checks:

```sh
PYTHONPATH=. python docs/flora-runtime/si1-615/review-tools/evidence.py
python docs/flora-runtime/si1-615/review-tools/examples.py
python docs/flora-runtime/si1-615/review-tools/contracts.py
python docs/flora-runtime/si1-615/review-tools/discovery.py
PYTHONPATH=. python docs/flora-runtime/si1-615/review-tools/render-base.py
python docs/flora-runtime/si1-615/review-tools/prototype.py
python docs/flora-runtime/si1-615/review-tools/validate.py
python -m http.server 8766 --bind 127.0.0.1
```

In a second terminal, `node docs/flora-runtime/si1-615/review-tools/browser.cjs`. The script uses `/usr/bin/chromium`; adapt that local executable path if necessary. The baseline HTML export is transient under `/tmp`, not a new research store. Existing `tools/ci/flora_ci.py --output <new-empty-temporary-directory>` runs the versioned runtime/security comparator using isolated test data. Raw temporary logs, private fixture records and tokens are not published in this pack.

## Limits and owner checks

These are automated structural and interaction checks, not a complete WCAG certification or screen-reader user study. Physical desktop/iPad/mobile, actual browser/OS zoom, assistive-technology reading order and preferred agenda placement need owner review. Sources were not fetched anew to prove factual currentness or live availability; original URL equality and existing metadata were checked. The single-file review prototype is about 6.7 MB; it embeds seven existing images for offline review and is not a proposed production asset-delivery strategy.

Existing IAM is preserved by zero runtime changes, not reimplemented or simulated in this public prototype. No real private tenant, employer, customer attestation or Pipeline data was read or changed. No live application provider, paid research call, autonomous collector, News worker or modelling engine was invoked.

The analytical model is complete as a method; current national structural diagnosis, Banking market economics/positioning and Lloyds operating/leadership research remain incomplete. None of the selected examples establishes demonstrated pain or a qualified opportunity. Implementation, canonical changes, NEWS-1 and production release require separate owner approval.
