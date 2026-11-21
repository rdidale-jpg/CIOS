"""Audit integrity checks only. Never changes application/tests/source records."""
from collections import Counter
import csv
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from collect import BASE, collect


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def validate():
    checks = 0
    def check(value, message):
        nonlocal checks
        assert value, message
        checks += 1

    subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, 'HEAD'], cwd=ROOT, check=True)
    check(git('merge-base', BASE, 'HEAD') == BASE, 'Audit must descend from inspected main')
    prefix = str(HERE.relative_to(ROOT)) + '/'
    changed = git('diff', '--name-only', BASE).splitlines()
    check(all(p.startswith(prefix) for p in changed), 'Only documentation/audit files may change')
    tracked = git('diff', '--name-only', BASE, 'HEAD').splitlines()
    check(all(p.startswith(prefix) for p in tracked), 'Committed runtime/Source/canonical change')
    evidence = json.loads((HERE / 'Repository-Evidence.json').read_text())
    check(evidence['audited_main'] == BASE, 'Incorrect audited runtime SHA')
    with tempfile.TemporaryDirectory(prefix='flora-audit-reproduce-') as scratch:
        collect(Path(scratch))
        for name in ('Repository-Evidence.json', 'Enterprise-Inventory.csv'):
            check((HERE / name).read_bytes() == (Path(scratch) / name).read_bytes(), 'Non-reproducible inventory: ' + name)
    for path, digest in evidence['source_paths_sha256'].items():
        raw = (ROOT / path).read_bytes()
        check(sha256(raw).hexdigest() == digest, 'Evidence changed: ' + path)
        base = subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)
        check(raw == base, 'Evidence is not from audited main: ' + path)

    rows = list(csv.DictReader((HERE / 'Enterprise-Inventory.csv').open()))
    counts = Counter(row['family'] for row in rows)
    check(len(rows) == 371, 'Unexpected owner-qualified inventory population')
    check(dict(counts) == evidence['counts']['by_inventory_family'], 'Count semantics mismatch')
    check(counts['technology_provider'] == 80 and counts['wave3_dossier'] == 25, 'Lost provider/dossier coverage')
    check(counts['source_organisation_label'] == 103 and counts['tms_priority_subject'] == 14, 'Lost retained source/package population')
    check(counts['research_supplier_or_role_node'] == 10, 'Lost supplier/aggregate-role boundaries')
    check(counts['visual_context_or_role'] == 20 and counts['macro_entity_applicability_trace'] == 2, 'Lost comparator/role/applicability scope')
    check(evidence['financial_selection_keys'] == ['boe-household-deposit-stocks', 'nationwide-fy2026'], 'Financial rollout assertion stale')
    check(len(evidence['uk_sector_foundations']) == 20 and all(not r['public_admission'] for r in evidence['uk_sector_foundations']), 'Research cannot imply public admission')
    check(not evidence['live_Render_or_canonical_stores_inspected'] and evidence['source_permission_changes'] == 0, 'Authority boundary changed')
    for row in rows:
        path = row['evidence_path'].split('::')[0]
        check((ROOT / path).is_file(), 'Missing enterprise evidence: ' + path)
        check(bool(row['canonical_maturity']) and bool(row['runtime_presentation']), 'Conflated/empty maturity dimension')

    case = ROOT / 'enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json'
    raw = case.read_bytes()
    check(sha256(raw).hexdigest() == 'd5d6c29d840502101991c166428af18e7a4b77b19b016f9bfe9707130a809775', 'Lloyds source/hold changed')
    d = json.loads(raw)
    exceptions = {r['issue']: r['status'] for r in d['rights']['material_exceptions']}
    check(d['rights']['contract_restriction_found'] is None and exceptions['lloyds_section_2'] == exceptions['lloyds_section_5_deep_links'] == 'unresolved', 'Legal authority invented')

    browser = json.loads((HERE / 'Browser-Observations.json').read_text())
    observed = browser['observations']
    check(browser['auditedMain'] == BASE and len(observed) == 64, 'Incorrect browser scope')
    check(all(row['status'] == 200 for row in observed), 'Unexpected representative route failure')
    check(not any(row['overflow'] for row in observed), 'Observed overflow must be reported/reconciled')
    expected = {'uk','banking','nationwide','natwest','lloyds','lloyds-inside','easyjet-visual','easyjet-fleet'}
    check({r['label'] for r in observed if r['regions'] == 3} == expected, 'Current common-shell claims inaccurate')
    check(all(r['readingModes'] == ['Facts','FLORA Insight'] for r in observed if r['label'] in expected), 'Claimed reading-mode availability inaccurate')

    # Validate local links and every pinned-main source target, including ZIP
    # paths. Do not perform network or source-rights decisions for a link check.
    seen = set()
    for page in HERE.glob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)', page.read_text()):
            if link.startswith('#'):
                continue
            parsed = urlsplit(link)
            if parsed.scheme:
                anchor = f'https://github.com/rdidale-jpg/CIOS/blob/{BASE}/'
                if link.startswith(anchor):
                    target = unquote(link[len(anchor):].split('#')[0])
                    if target not in seen:
                        check((ROOT / target).is_file(), 'Broken pinned source link: ' + target)
                        seen.add(target)
                continue
            check((page.parent / unquote(parsed.path)).is_file(), 'Broken local report link: ' + link)
    check(all((HERE / n).is_file() for n in ['README.md','Industry-Coverage.md','Enterprise-Presentation.md','Gaps-and-Reuse.md','Next-Decisions.md','Evidence-Map.md','Validation-and-Critique.md']), 'Missing deliverable')
    return {'documentation_head': git('rev-parse', 'HEAD'), 'audited_runtime': BASE,
            'passed': True, 'checks': checks, 'owner_qualified_inventory_rows': len(rows),
            'representative_browser_observations': len(observed), 'production_inspected': False,
            'runtime_or_canonical_changes': 0, 'source_permissions_changed': 0,
            'scope': 'Documentation evidence/inventory integrity, not a rerun of runtime security/regression'}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
