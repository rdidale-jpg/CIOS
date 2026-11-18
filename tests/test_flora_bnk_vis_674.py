import pytest

from cios.applications.flora import visual_streams as v
from tests.test_flora_eai2_integration import changed_release
from tests.test_flora_uxr1_650 import retained

BANKING = "/industries/banking"


@pytest.mark.parametrize("stage,phrase", [
    ("customers", "Distribution and account servicing"),
    ("funding", "Interest and risk"),
    ("providers", "Shared dependencies"),
])
def test_banking_stage_and_reading_are_independent(stage, phrase):
    q = {"detail": [stage]}
    facts = v.render(BANKING, q)
    insight = v.render(BANKING, {**q, "reading": ["insight"]})
    assert phrase not in facts and phrase in insight
    assert f'detail={stage}' in insight
    assert 'aria-current=page>Facts' in facts
    assert 'aria-current=page>FLORA Insight' in insight
    assert v.BANKING_ART in facts
    assert v.EASYJET_ART in v.render(v.EASYJET_ROUTE, {})


@pytest.mark.parametrize("query", [
    {"detail": ["funding"], "stream": ["forces"]},
    {"detail": ["providers"], "selected": ["nationwide"]},
    {"detail": ["customers"], "agenda": ["service-landscape"]},
])
def test_incompatible_stage_context_rejected(query):
    with pytest.raises(ValueError):
        v.resolve(BANKING, query)


@pytest.mark.parametrize("flag", ["rights", "private", "withdrawn", "source_host"])
def test_provider_source_lifecycle_gates_both_modes(tmp_path, monkeypatch, flag):
    q = {"detail": ["providers"]}
    assert "Google Cloud EMEA Limited" in v.render(BANKING, q)
    assert "workload remain unverified" in v.render(BANKING, {**q, "reading": ["insight"]})
    changed_release("provider", flag, tmp_path, monkeypatch)
    for mode in ("facts", "insight"):
        html = v.render(BANKING, {**q, "reading": [mode]})
        assert "Google Cloud EMEA Limited" not in html
        assert v.BANKING_ART in html


def test_funding_withdrawal_suppresses_only_derived_values(retained):
    import json

    query = {"detail": ["funding"]}
    assert "6,378 − 4,021 − 331 = 2,026" in v.render(BANKING, query)
    data = json.loads(retained.read_text())
    data["sources"][1]["withdrawn"] = True
    retained.write_text(json.dumps(data))
    facts = v.render(BANKING, query)
    insight = v.render(BANKING, {**query, "reading": ["insight"]})
    assert "6,378" not in facts + insight
    assert "bank and building society balance sheets" in facts
    assert "No supported FLORA Insight" in insight
