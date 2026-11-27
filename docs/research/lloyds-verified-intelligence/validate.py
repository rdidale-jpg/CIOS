"""Review-only scope, traceability and exact reverse-tree proof; no baseline writes."""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from review import BASE, ROOT, HERE, build

PREFIX = str(HERE.relative_to(ROOT)) + '/'


def git(*args, env=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, env=env)


def validate():
    expected = build()
    for name, value in expected.items():
        assert json.loads((HERE / name).read_text()) == value, name
    notes = expected['Note-Disposition.json']['notes']
    crosswalk = expected['Crosswalk-Review.json']['entries']
    sources = expected['Source-Inspection.json']['sources']
    assert len(notes) == len({r['recovery_id'] for r in notes}) == 49
    assert len(crosswalk) == 34
    refs = {r['review_ref'] for r in sources}
    assert all(set(r['reviewed_source_refs']) <= refs for r in [*notes, *crosswalk])
    assert all(r['original_bytes_sha256'] is None and not r['source_use_authority_changed'] for r in sources)
    status = json.loads((HERE / 'Journey-Status.json').read_text())
    assert status['input_sha'] == BASE and len(status['journeys']) == 2
    for row in status['journeys']:
        assert row['state'] == 'blocked_before_acquisition_and_staging'
        assert row['original_bytes_sha256'] is None
        assert len(row['blockers']) == 3
        assert not row['candidate_evidence_created'] and not row['new_canonical_acceptance'] and not row['production_activation']
    changed = set(git('diff', '--name-only', BASE).decode().splitlines())
    changed |= set(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    assert changed and all(p.startswith(PREFIX) for p in changed), changed
    assert sorted(changed) == (HERE / 'File-Inventory.txt').read_text().splitlines()
    assert not git('diff', '--name-only', BASE, '--', '.', ':(exclude)' + PREFIX).strip()
    links = 0
    for file in HERE.glob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)', file.read_text()):
            if '://' in link or link.startswith('#'): continue
            assert (file.parent / link.split('#')[0]).exists(), (file, link)
            links += 1
    tree = git('write-tree').decode().strip()
    patch = git('diff', '--binary', '--full-index', BASE, tree)
    with tempfile.TemporaryDirectory() as directory:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(directory) / 'index'))
        git('read-tree', tree, env=env)
        subprocess.run(['git', 'apply', '--cached', '--reverse'], input=patch, cwd=ROOT, env=env, check=True)
        rollback = git('write-tree', env=env).decode().strip()
    assert rollback == git('rev-parse', BASE + '^{tree}').decode().strip()
    return {'head': git('rev-parse', 'HEAD').decode().strip(), 'input_sha': BASE,
            'candidate_tree': tree, 'files': len(changed), 'note_dispositions': len(notes),
            'crosswalk_dispositions': len(crosswalk), 'source_inspections': len(sources),
            'genuine_byte_bound_journeys_complete': 0, 'blocked_journeys': 2,
            'local_links_checked': links, 'rollback_tree': rollback,
            'original_runtime_security_artwork_research_unchanged': True,
            'source_authority_and_pipeline_changes': False, 'passed': True}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
