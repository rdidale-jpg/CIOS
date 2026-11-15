# Validation

Run with project Python3.12 dependencies:

```sh
python -m pytest tests/test_flora_intelligence_presentation_623.py tests/test_flora_visual_streams_612.py tests/test_flora_visual_v2_583.py tests/test_flora_research_intelligence.py tests/test_flora_design_system_585.py -q
python -m unittest discover -s tests/ci -v
PYTHONPATH=. python tools/ci/flora_ci.py --output /tmp/isp1-new-exact-head-output
PYTHONPATH=. python tools/ci/flora_isp1_preview.py --output docs/flora-runtime/isp1-623/previews --baseline-root /path/to/validated-main-worktree
```

Use a new empty output directory for each full CI run. Browser proof requires Node Playwright and `/usr/bin/chromium`; fixture credentials, local TLS keys and runtime data remain disposable, never committed. Screenshots contain only the public visual experience; no live production or seller records are captured.

Semantic cases cover six independent view types, verification/acceptance orthogonality, uncertain/transitive calculation inputs, incompatible dates/entity/basis/unit/target inputs, actual/target distinction, hypothesis falsifiers, counter-evidence, source URL/date failures, unsupported content omission and no owner metadata in hidden HTML. Real HTTP cases check anonymous/owner/seller access, revoked owner membership, exact finite query grammar, no-store responses, and unchanged core access. Domain/matcher/model/write spies and artwork checks prevent hidden owner reads or data changes.

Browser checks cover seven views ×desktop/iPad landscape/iPad portrait/mobile, native source details, no-JavaScript UK→Banking→Lloyds, stream switches, Back/Forward, effective200% zoom, forced-colour active context and anonymous inspection denial. Accessibility-tree snapshots are retained. These are Chromium/emulated-touch checks, not physical iPad/Safari or screen-reader certification. Owner real-device and live-production inspection remain manual.

Final exact SHA, local full result and both hosted workflow links/conclusions are recorded in the draft PR's validation comment after completion. The original388 strict security tests, inherited failure/skip baseline and comparator remain unchanged. No success is inferred merely from adding a workflow or from an expected baseline count.
