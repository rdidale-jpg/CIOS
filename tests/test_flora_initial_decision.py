"""The offline brief isolates held inputs and reuses existing public facts."""
from copy import deepcopy
from datetime import date
import json
import shutil

import pytest

from tools.research import initial_decision as brief
from cios.applications.flora.research_intelligence import cycle
from cios.applications.flora.research_intelligence.model import load_assessment
from tests.test_flora_research_cycle import AS_OF, submission

PACKAGE = brief.ROOT / 'docs/research/lloyds-tier1-sprint1'
CUTOFF = date(2026, 11, 22)


def test_lloyds_review_reuses_source_bound_preview_without_releasing_candidates():
    text = brief.render(PACKAGE, CUTOFF, 'lloyds-service')
    assert '118,762 complaints' in text
    assert 'Candidate preparation (11)' in text
    assert 'External context owner review (7)' in text
    assert 'Held or needs further evidence (22)' in text
    assert 'mapping (3): R01, R02, R12' in text
    assert 'Sprout.ai' not in text
    assert '31 Unknowns' in text
    assert '118,762' not in brief.render(PACKAGE, date(2026, 9, 1), 'lloyds-service')


def test_duplicate_and_withdrawal_do_not_block_unrelated_preparation(monkeypatch):
    manifest, records, sources, endpoints, lineage = brief.read_review(PACKAGE)
    duplicate = deepcopy(records['evidence'][0])
    records['evidence'].append(dict(duplicate, id='test-repeat'))
    sources['ch-hbos']['status'] = 'withdrawn'
    monkeypatch.setattr(brief, 'read_review', lambda _: (manifest, records, sources, endpoints, lineage))
    _, batches, edges, deferred, _, _ = brief.prepare(PACKAGE, CUTOFF)
    assert batches['Exact repeat within package'] == ['test-repeat → F01']
    assert 'F02' in batches['Held or needs further evidence']
    assert 'F18' in batches['Candidate preparation']
    assert 'R02' in deferred and 'R12' in edges


def test_foreign_record_scope_is_rejected(tmp_path):
    local = tmp_path / 'package'
    shutil.copytree(PACKAGE, local)
    path = local / 'evidence.ndjson'
    rows = path.read_text().splitlines()
    rows[0] = json.dumps(dict(json.loads(rows[0]), enterprise_id='foreign-enterprise'))
    path.write_text('\n'.join(rows) + '\n')
    with pytest.raises(ValueError, match='Ambiguous identity, scope'):
        brief.render(local, CUTOFF)


def test_source_export_reuses_validated_acquisition(monkeypatch, tmp_path):
    data = load_assessment()
    item = submission(data, tmp_path, effect='new')
    acquire = cycle.acquire
    acquired = []

    def observed(source, assessment):
        result = acquire(source, assessment)
        acquired.append(result)
        return result

    monkeypatch.setattr(cycle, 'acquire', observed)
    retained = []
    report = cycle.run_cycle(data, AS_OF, [item], on_acquired=retained.append)
    assert len(acquired) == 1 and retained[0] is acquired[0]
    assert report['waves'][0]['proposals'][0]['raw_sha256'] == retained[0]['primary_content_sha256']
