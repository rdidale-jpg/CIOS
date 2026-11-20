"""Transport, context and eligibility checks for Technology reading views."""
import json
import shutil

import pytest

from cios.applications.flora.research_intelligence import technology_commercial
from cios.applications.flora.research_intelligence.technology_experience import BASE
from tests.test_flora_research_intelligence import web


def test_modes_keep_subject_and_existing_research_boundaries(web):
    route = BASE + '/enterprise?enterprise=nvidia&district=ai'
    status, facts = web(route)
    assert status == 200
    assert all(f'data-region="{region}"' in facts for region in ('top', 'left', 'main'))
    assert 'data-reading="facts"' in facts
    assert 'Global group · FY2026' in facts and 'UK programmes & activity' in facts
    assert 'enterprise=nvidia&amp;district=ai&amp;reading=insight#technology-main' in facts
    status, insight = web(route + '&reading=insight')
    assert status == 200 and 'data-reading="insight"' in insight
    assert 'NVIDIA' in insight and 'Commercial pressures' in insight
    assert 'Global group · FY2026' not in insight

    status, html = web(BASE + '/district?district=cloud&sort=uk_revenue&direction=desc&search=Equinix')
    assert status == 200
    assert 'district=cloud&amp;sort=uk_revenue&amp;direction=desc&amp;search=Equinix&amp;reading=insight' in html
    assert web(BASE + '/enterprise?enterprise=equinix&detail=financials')[0] == 200


@pytest.mark.parametrize('target', [
    '?reading=private', '?reading=insight&reading=facts', '?reading=insight&run_id=private',
    '?reading=insight&workspace=private', '/pipeline?reading=insight', '/assets/artwork?reading=insight',
])
def test_new_reading_selector_does_not_change_private_or_specialist_paths(web, target):
    assert web(BASE + target)[0] in (403, 404)


def test_hash_pinned_commercial_withdrawal_fails_closed_in_both_modes(web, monkeypatch, tmp_path):
    data = json.loads(technology_commercial.DATA.read_text())
    next(iter(data['sources'].values()))['withdrawn'] = True
    foundation = technology_commercial.technology
    original_root = foundation.ROOT
    shutil.copytree(original_root / 'docs/flora-runtime/technology-visual-foundation',
                    tmp_path / 'docs/flora-runtime/technology-visual-foundation')
    path = tmp_path / 'Commercial-Views.json'
    path.write_text(json.dumps(data))
    monkeypatch.setattr(technology_commercial, 'DATA', path)
    monkeypatch.setattr(foundation, 'ROOT', tmp_path)
    monkeypatch.setattr(foundation, 'ASSETS', tmp_path / 'docs/flora-runtime/technology-visual-foundation')
    assert foundation.load()[0]['providers']
    with pytest.raises(ValueError, match='Commercial research changed'):
        technology_commercial.load()
    for mode in ('facts', 'insight'):
        status, html = web(BASE + '/enterprise?enterprise=nvidia&reading=' + mode)
        assert status == 404
        assert 'Global group · FY2026' not in html and 'Commercial pressures' not in html
