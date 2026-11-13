"""Business example wording preserves the original research and trust boundaries."""
from copy import deepcopy
from dataclasses import asdict
from html import escape

import pytest

from cios.applications.flora.observatory import engine, views
from tests.flora_html_contract import Document


@pytest.mark.parametrize('text', [
    'SEEDED / SYNTHETIC / FALLBACK — Governed public signal',
    'SEEDED / SYNTHETIC / FALLBACK: Example pressure <script>alert(1)</script>',
    "{'SEEDED / SYNTHETIC / FALLBACK': 3}",
])
def test_example_evidence_wording_keeps_non_live_limit_and_html_escaping(text):
    result = views._evidence_label(text)
    assert 'Example data / fallback (not live)' in result
    assert 'SYNTHETIC' not in result
    assert '<script>' not in result
    if '<script>' in text:
        assert '&lt;script&gt;' in result


def test_business_wording_does_not_rewrite_actual_names_or_source_quotes():
    text = 'Synthetic biology services — a real enterprise capability <unverified>'
    assert views._evidence_label(text) == escape(text)


def test_rendered_example_language_preserves_internal_evidence_and_scores(monkeypatch, tmp_path):
    empty = tmp_path / 'empty.jsonl'
    empty.write_text('')
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'runtime'))
    monkeypatch.setattr(engine, 'DEFAULT_PATH', empty)
    obs = engine.build_observatory()
    before = deepcopy(asdict(obs))
    monkeypatch.setattr(views, 'build_observatory', lambda: obs)
    monkeypatch.setattr(views, 'current_status', lambda: {})
    assert obs.evidence and not any(e.is_live for e in obs.evidence)
    assert all('SEEDED / SYNTHETIC / FALLBACK' in e.evidence_class for e in obs.evidence)
    html = views.organisation_observatory_page('BT')
    text = Document(html).text
    assert 'Example data / fallback (not live)' in text
    assert 'synthetic' not in text.lower()
    bt = next(org for org in obs.organisations if org.organisation == 'BT')
    for evidence_id in bt.case_for_change.supporting_evidence_ids:
        assert evidence_id in text
    assert asdict(obs) == before
