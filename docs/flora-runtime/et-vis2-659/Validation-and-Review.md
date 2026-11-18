# Validation and independent critique

The draft PR's final validation comment records the frozen candidate SHA and exact-head local/hosted results. This document describes repeatable checks and limits; pre-commit screenshots alone are not an exact-head CI claim.

## Reproduction

Use the repository requirements and Python environment. Keep all runtime/test data isolated. No live account or credentials are needed.

```sh
python -m pytest tests/test_flora_etvis2_659.py tests/test_flora_aviation_twin.py tests/test_flora_visual_intelligence.py tests/test_flora_visual_panels_632.py -q
python tools/research/auth2_compatibility.py
python tools/research/etvis2_quality.py
python tools/ci/flora_ci.py --output /tmp/etvis2-final-ci
```

For browser proof, install Playwright 1.62.1 with Chromium, set `NODE_PATH` to that installation, then:

```sh
git worktree add --detach /tmp/etvis2-before fbac4c37910ed07b2baa516e1a5c8d7f329086de
python tools/research/etvis2_proof.py --output /tmp/etvis2-proof --baseline-root /tmp/etvis2-before
```

The new hosted ET-VIS workflow checks the candidate head explicitly; existing full FLORA validation/security, historical semantic/compatibility and responsive workflows still run. No comparator or inherited failure/skip baseline changed. Source withdrawal/staleness tests edit only disposable copies; the proof asserts public reads create no data/authority directory. The application code does not read private Financial runs, canonical Enterprise Models, Pipeline records or owner research stores.

## Browser evidence

Pre-freeze proof: **254 checks**, four target viewports, 320px at 200% text, no-JavaScript links, keyboard/focus/live announcement, touch, capability/lens state, Back/Forward/reload, actual Left DOM persistence, selected Main heading visibility, malformed query denials, source withdrawal/staleness preserving unrelated FY2025 context, protected-route denials and unchanged Aviation/Banking/Lloyds destinations. Actual side-by-side bounding boxes and successful asset responses are checked, not only HTML status. `Browser-Checks.json` holds individual assertions.

Browser coverage is Chromium emulation; Safari, physical iPad, a screen-reader session and production Render were not tested. The 200% check is text enlargement, not a claim of physical browser-device zoom certification. Full hosted results must be green before any later integration decision.

## Independent review and dispositions

Three actual separate reviewers inspected the implementation, retained evidence and rendered previews.

| Reviewer / executed work | Finding | Disposition |
| --- | --- | --- |
| Architecture/security; personally ran 108 focused tests | Wrong base stylesheet route; missing accepted header assets | Use existing extensionless `panel-styles`, add `ds.head()`, verify all resources and actual columns. |
| Evidence/commercial; personally ran 56 focused tests plus in-memory negative probes | Whole-overlay validation suppressed unrelated good sources | Read fixed registered file; check root/perimeter and exact consumed Source/claim pins; existing model/ISP per-disclosure checks; actual render-level damaged-snapshot test. |
| Architecture/security | Referenced capability restrictions and malformed JSON shapes | Validate current referenced capability records and root/profile collection shapes; negative tests. |
| Visual/UX; inspected actual desktop, iPad both, mobile and enlarged text | Selection could leave new Main below fold | Collapse mobile scene after capability choice; focus and bring Main heading into view; browser checks visible heading. |
| Visual/UX | 200% labels split into fragments | Wrap whole controls and preserve complete words; corrected actual 200% preview inspected. |
| Visual/UX and evidence/commercial | Booking/connected-cabin announcements are adjacent, not proven capability change | Label dated company/adjacent channel context and retain unestablished capability effect explicitly. |
| Architecture/security | Generic conceptual Forces copy was labelled FLORA Insight without the Statement contract | Relabel Conceptual operating mechanism; keep eligible Reported facts separate. |
| Visual/UX | Repeated defensive explanations cluttered conceptual sections | One model-scope statement; retain material fact/relationship caveats. |
| Visual/UX | Vector scene flatter than rich approved originals | Open owner artistic-acceptance tradeoff, explicitly disclosed; do not claim visual parity or replace an original asset. |
| Evidence/commercial | Incomplete compound claim support; source admission is not licence proof | Narrow exact facts; no new rights/grants; source-use limits documented. |

All security findings within scope are addressed. The visual reviewer re-inspected v5 renders/code and confirmed the three readability/interaction/context blockers resolved; no remaining material UX blocker for bounded owner review was found. Artistic parity remains unestablished. Final exact-head test confirmation follows frozen-candidate proof. Independent review is advisory and does not constitute source/canonical acceptance, owner design approval or production readiness.

## Known limits

Three capability groupings and three **bounded prototype** modes, not a full enterprise ontology, verified systems topology, live News, causal change engine or modelling tool. No actual capability-level costs, revenue allocation, productivity, buying authority or commercial opportunity is known from this slice. Earlier retained issuer dates/short excerpts retain their original verification limits. The preview is intentionally discoverable through its explicit review URL; no existing production journey is replaced. Original illustrations and established source/security controls remain unchanged.
