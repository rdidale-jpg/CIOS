from hashlib import sha256
import json

import pytest

from tools.research.factory_zero_cost import candidates, hybrid_gate, manual_rows, score


def test_hybrid_requires_revision_bound_quote_and_explicit_fields():
    raw = b'<body><p>Company A has completed the acquisition of North Labs.</p></body>'
    passage = 'Company A has completed the acquisition of North Labs.'
    row = {'id': 'D01', 'sha256': sha256(raw).hexdigest(), 'paragraph': 1,
           'url': 'https://example.org/news', 'publisher': 'Company A'}
    response = {'actor': 'Company A', 'kind': 'acquisition', 'target': 'North Labs',
                'counterparty': 'North Labs', 'status': 'completed', 'quote': passage}
    claim, = candidates(row, passage, [response], '2026-11-23')
    assert hybrid_gate(claim, raw, '2026-11-23') is None
    assert claim['publication_eligible'] is False
    assert hybrid_gate(claim, raw + b' ', '2026-11-23') == 'assurance_withheld'
    assert hybrid_gate(claim, raw, None) == 'publication_date_unresolved'
    unsupported, = candidates(row, passage, [dict(response, target='South Labs')], '2026-11-23')
    assert hybrid_gate(unsupported, raw, '2026-11-23') == 'field_support_unresolved'
    hallucinated, = candidates(row, passage, [dict(response, quote='Made up.')], '2026-11-23')
    assert hybrid_gate(hallucinated, raw, '2026-11-23') == 'unbound_quote'


def test_manual_import_denies_unknown_revision_and_duplicate_ids(tmp_path):
    path = tmp_path / 'response.json'
    row = {'id': 'D01', 'sha256': 'a' * 64, 'claims': []}
    path.write_text(json.dumps([row]))
    assert manual_rows(path, [row]) == {'D01': []}
    path.write_text(json.dumps([row, row]))
    with pytest.raises(ValueError):
        manual_rows(path, [row, dict(row, id='D02')])
    path.write_text(json.dumps([dict(row, sha256='b' * 64)]))
    with pytest.raises(ValueError):
        manual_rows(path, [row])


def test_withdrawal_does_not_read_capture_or_turn_into_a_model_result():
    url = 'https://example.org/news'
    row = {'id': 'D01', 'split': 'evaluation', 'category': 'acquisition', 'url': url}
    result = score([row], [], {'D01': {'claims': []}}, {}, {url})
    assert result['documents'][0]['disposition'] == 'withdrawn'
    assert result['arms']['hybrid']['evaluation'] == {
        'evaluated_documents': 0, 'precision': None, 'recall': None}
