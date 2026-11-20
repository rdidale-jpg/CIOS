"""Exact-head A1 assurance and reversible-tree proof; no production access."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
BASE = '03719d7573f087c65d9622719273aa4b89caf7d3'


def git(*args, **kwargs):
    return subprocess.check_output(['git', *args], cwd=ROOT, **kwargs)


def validate():
    from tools.research.enterprise_economics_compatibility import validate as renderer
    from tools.research.auth2_compatibility import validate as history
    from tools.research.public_financial_compatibility import validate as financial_cut
    from cios.applications.flora.financial_intelligence.candidate_analytics import public_factual_projection

    git('merge-base', '--is-ancestor', BASE, 'HEAD')
    renderer_report = renderer(ROOT)
    financial_report = financial_cut(ROOT)
    history_report = history()
    originals = {}
    for folder in ('visual_stream_assets', 'easyjet_art', 'banking_art'):
        for path in git('ls-tree', '-r', '--name-only', BASE, 'cios/applications/flora/' + folder, text=True).splitlines():
            raw = (ROOT / path).read_bytes()
            assert raw == git('show', BASE + ':' + path), path
            originals[path] = sha256(raw).hexdigest()
    # All source/research, private-run and canonical owners remain byte exact.
    protected = ['enterprise-knowledge', 'architecture',
                 'cios/applications/flora/financial_intelligence',
                 'cios/applications/flora/research_intelligence',
                 'cios/applications/flora/security.py', 'cios/applications/flora/security_store.py',
                 'cios/applications/flora/supabase_identity.py', 'cios/applications/flora/web/app.py',
                 'cios/applications/flora/memory', 'cios/applications/flora/blueprint_import',
                 'cios/applications/flora/offers', 'cios/applications/flora/seller_development',
                 'tools/ci/flora_ci.py', 'tools/ci/flora-baseline-v1.json']
    assert not git('diff', BASE, '--', *protected), 'Protected owner/history/comparator modified'
    case = ROOT / 'enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json'
    source = json.loads(case.read_text())
    assert source['rights']['contract_restriction_found'] is None
    exceptions = {x['issue']: x['status'] for x in source['rights']['material_exceptions']}
    assert exceptions['lloyds_section_2'] == exceptions['lloyds_section_5_deep_links'] == 'unresolved'
    assert public_factual_projection() == {}
    head = git('rev-parse', 'HEAD', text=True).strip()
    # Apply the complete reverse patch in a temporary INDEX, never the worktree
    # or data directories. Its resulting tree must equal the verified baseline.
    with tempfile.TemporaryDirectory(prefix='flora-economics-rollback-') as scratch:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(scratch) / 'index'))
        git('read-tree', head, env=env)
        patch = git('diff', '--binary', BASE, head)
        if patch:
            subprocess.run(['git', 'apply', '--cached', '--reverse', '--whitespace=nowarn'], input=patch, cwd=ROOT, env=env, check=True)
        rolled_back = git('write-tree', env=env, text=True).strip()
    baseline_tree = git('rev-parse', BASE + '^{tree}', text=True).strip()
    assert rolled_back == baseline_tree
    return {'head': head, 'base': BASE, 'renderer': renderer_report,
            'financial_cut': financial_report, 'historical_quality': history_report,
            'original_assets': originals, 'source_permissions_added': 0,
            'private_financial_owners_changed': False, 'canonical_or_production_writes': 0,
            'lloyds_section2': 'unresolved; affected projection inactive',
            'lloyds_section5': 'unresolved; PDF deep links deferred',
            'rollback_tree': rolled_back, 'baseline_tree': baseline_tree,
            'changed_files': git('diff', '--name-only', BASE, head, text=True).splitlines()}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
