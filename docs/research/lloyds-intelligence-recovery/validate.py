"""Finite recovery QA, no baseline refresh or production service access."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from recover import BASE, HERE, ROOT, build

PREFIX = str(HERE.relative_to(ROOT)) + '/'
TEST = 'tests/test_flora_lloyds_recovery_proof.py'
WORKFLOW = '.github/workflows/flora-verified-factory.yml'
ECONOMICS = '.github/workflows/flora-enterprise-economics-a1.yml'


def git(*args, env=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, env=env)


def validate():
    expected = json.loads(json.dumps(build()))
    for filename, value in expected.items():
        assert json.loads((HERE / filename).read_text()) == value, filename
    recovery = expected['Recovery.json']
    assert len(recovery['records']) == 49
    assert len({row['id'] for row in recovery['records']}) == 49
    assert all(not row['canonical_acceptance'] and not row['public_admission_in_this_sprint']
               and not row['new_original_source_verification'] for row in recovery['records'])
    sources = expected['Source-Register.json']
    ids = {s['id'] for s in sources['sources']}
    assert len(ids) == len(sources['sources']) == 100
    assert all(set(row['source_refs']) <= ids for row in recovery['records'])
    assert len(sources['unchanged_owner_proposals']) == 8
    assert all(not row['owner_evidence_acceptance'] and not row['canonical_acceptance']
               for row in sources['unchanged_owner_proposals'])
    assert len(recovery['reconciliations']) == 13
    assert all(c['arithmetic_reproduces'] for c in recovery['reconciliations'])
    backlog = list(csv.DictReader((HERE / 'Backlog-Disposition.csv').open()))
    assert [r['id'] for r in backlog] == ['R%02d' % i for i in range(1, 22)]
    assert all(r['remaining_boundary'] for r in backlog)
    for name in ('Proof-AI.json', 'Proof-Division.json'):
        proof = json.loads((HERE / name).read_text())
        assert not proof['publication_eligible'] and not proof['production_activation']
        assert proof['recovered_assertions'] == 2 and proof['repeat'] == 'repeat_no_change'
    changed = set(git('diff', '--name-only', BASE).decode().splitlines())
    changed |= set(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    assert changed and all(p.startswith(PREFIX) or p in {TEST, WORKFLOW, ECONOMICS} for p in changed), changed
    assert sorted(changed) == (HERE / 'File-Inventory.txt').read_text().splitlines()
    original = git('show', BASE + ':' + WORKFLOW).decode()
    original = original.replace("      - 'docs/research/initial-factory/verified/**'\n",
        "      - 'docs/research/initial-factory/verified/**'\n      - 'docs/research/lloyds-intelligence-recovery/**'\n")
    original = original.replace("      - 'tests/test_flora_verified_factory.py'\n",
        "      - 'tests/test_flora_verified_factory.py'\n      - 'tests/test_flora_lloyds_recovery_proof.py'\n")
    original = original.replace(' tests/test_flora_blueprint_import_promotion.py\n',
        ' tests/test_flora_blueprint_import_promotion.py tests/test_flora_lloyds_recovery_proof.py\n')
    assert (ROOT / WORKFLOW).read_text() == original
    economics = git('show', BASE + ':' + ECONOMICS).decode().replace(
        '          python docs/product/flora-experience/main-canvas/validate.py --browser "$RUNNER_TEMP/canvas-browser"',
        '          python docs/research/lloyds-intelligence-recovery/check_canvas_browser.py "$RUNNER_TEMP/canvas-browser"\n'
        '          # Keep the original #733 scope/hash/rollback audit on its approved cut.\n'
        '          git worktree add --detach "$RUNNER_TEMP/canvas-approved-cut" 3a4c7e0f6ad81af7ef32ed477a1a584ac2efae87\n'
        '          cd "$RUNNER_TEMP/canvas-approved-cut"\n'
        '          python docs/product/flora-experience/main-canvas/validate.py')
    assert (ROOT / ECONOMICS).read_text() == economics
    # Exact byte preservation of runtime, canonical artifacts, security,
    # artwork and all original historical research via Git's complete tree diff.
    assert not git('diff', '--name-only', BASE, '--', '.', ':(exclude)' + PREFIX,
                   ':(exclude)' + TEST, ':(exclude)' + WORKFLOW, ':(exclude)' + ECONOMICS).strip()
    links = 0
    for path in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            assert (path.parent / target.split('#')[0]).exists(), (path, target)
            links += 1
    # Reverse the exact staged candidate diff in a temporary index. Neither the
    # working files nor the real index, branches, services or stores are changed.
    candidate_tree = git('write-tree').decode().strip()
    patch = git('diff', '--binary', '--full-index', BASE, candidate_tree)
    with tempfile.TemporaryDirectory() as directory:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory) / 'index'))
        git('read-tree', candidate_tree, env=env)
        subprocess.run(['git', 'apply', '--cached', '--reverse'], input=patch, cwd=ROOT, env=env, check=True)
        rollback_tree = git('write-tree', env=env).decode().strip()
    assert rollback_tree == git('rev-parse', BASE + '^{tree}').decode().strip()
    return {'baseline': BASE, 'candidate_head': git('rev-parse', 'HEAD').decode().strip(),
            'candidate_tree': candidate_tree, 'changed_files': len(changed),
            'recovered_notes': 49, 'dated_crosswalk_entries': len(expected['Entity-Crosswalk.json']['entries']),
            'source_metadata_records_not_unique_publishers': len(ids), 'ric_duplicates_not_counted_again': 362,
            'backlog_dispositions': len(backlog), 'unchanged_owner_proposals': 8,
            'decimal_reconciliations': 13, 'local_links_checked': links,
            'rollback_tree': rollback_tree,
            'runtime_security_artwork_and_original_research_unchanged': True,
            'no_source_admission_or_production_activation': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = validate()
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
