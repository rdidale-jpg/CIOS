# Pack index and reproducibility

These JSON files are documentary proposals and audit snapshots, **not import schemas, a truth registry or runtime stores**.

| File | Contents |
| --- | --- |
| [Research-Baseline](Research-Baseline.json) | Verified ancestry, latest merged contract, prior research pins, truthful baseline CI limitations |
| [Sources](Sources.json) | 37 used original-source acquisition/use records, bounded excerpts and exact extents |
| [Claims](Claims.json) | 114 propositions: 57 reported, 4 estimated, 27 calculated, 26 Insights; counts are not independent accepted facts |
| [Twenty-Sector-Foundations](Twenty-Sector-Foundations.json) | Every SIC A–T prior reference, economic delta, dimension coverage, alternative and continuing demand |
| [UK-PESTLE](UK-PESTLE.json) | Six conditions and same-scope mechanisms; no automatic enterprise applicability |
| [Priority-Industry-Analyses](Priority-Industry-Analyses.json) | Banking/Aviation/Technology value systems, Five Forces, contextual PESTLE and decision-use limits |
| [Typed-Relationships](Typed-Relationships.json) | Eight directed role/action/composition proposals with status, identity limits and source dependencies |
| [Financial-and-Scope-QA](Financial-and-Scope-QA.json) | Eight exact-input audit calculations; 19 GVA residuals are separately typed in Claims |
| [Dated-Change-Seeds](Dated-Change-Seeds.json) | Eight dated seeds separating publication, occurrence, effect, measurement, retrieval and dedup identity; no active News claim |
| [Experience-Readiness-Handoff](Experience-Readiness-Handoff.json) | All 16 merged requirement keys, existing eligible versus withheld premises and scope/period-specific proposal assessments |
| [Exceptions-and-Demands](Exceptions-and-Demands.json) | 14 material acquisition, rights, identity, period, import and research limitations |
| [Wave-4-Provider-Worklist](Wave-4-Provider-Worklist.json) | Each of the exact 80 existing partial profiles; original discovery leads are not element-specific closure evidence |
| [Continuing-Waves](Continuing-Waves.json) | Waves 3–6; existing enterprise occurrences/cohorts, eight batches of ten providers, all 103 configured organisation targets and outcome follow-up |

Waves 3–6 are finite populations, not a promise to complete unspecified “more research”. Wave 3 reconciles current banking and six BIE dossiers/five limited profiles, legacy banking, easyJet/holidays, the four #666 assessments and priority Technology enterprises. The inventory retains file/README occurrences as **document references**, not additional enterprises. Exact legal-entity deduplication is subsequent evidence work.

Wave 4 individually covers all 80 profiles; six closure demands per provider require identity, original current economics, strategy/operating capabilities, actual relationships, dated outcomes and source-use mapping. Existing URLs are discovery leads. Eight overlapping commercial roles do not yield eight complete markets or 80 accepted Twins.

Wave 5 covers all 103 named source targets from 150 declarations, eight additional BT collection-profile sources in a separate namespace, all 76 Banking actor occurrences and verified retained TEL/TMS/MOD scope. Enabled flags are not proof of collection, admission or a Model. Wave 6 tests real outcomes, contract scope and source cadence; no automatic opportunity is created.

Reproduce documentary QA from repository root:

```bash
python docs/flora-runtime/research-enrich-all-w2-685/validate.py
python -m pytest tests/test_flora_research_enrich_all_w2_685.py -q
python -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --output /tmp/flora-w2-ci
```

The new research workflow uses exact PR-head checkout and read-only GitHub permissions. Existing full CI, security and failure/skip comparator remain unchanged. The research validator checks declared dependencies and numerical cuts; it cannot independently establish publisher rights or canonical authority. These are reviewed explicitly, rather than inferred from passing tests.
