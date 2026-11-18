import pytest

from cios.applications.flora import easyjet_capabilities as easyjet
from cios.applications.flora import experience_composition as experience
from cios.applications.flora import visual_streams as v
from tests.test_flora_uxr1_650 import main


@pytest.mark.parametrize("path", ["/enterprises/lloyds", v.EASYJET_ROUTE])
def test_enterprise_roots_observe_three_different_questions(path):
    roots = {}
    for stream in ("landscape", "inside", "forces"):
        query = {"stream": [stream]}
        facts = main(v.render(path, query))
        insight = main(v.render(path, {**query, "reading": ["insight"]}))
        assert 'aria-current=page>Facts' in facts
        assert 'data-semantic-type="insight"' not in facts
        assert 'data-semantic-type="insight"' in insight
        assert "What's changing?" not in facts
        roots[stream] = facts
    assert "Durable capabilities" in roots["inside"]
    assert roots["inside"].count('href="#ability-0"') == 2
    assert roots["inside"].count('id="ability-0"') == 1
    assert "Durable capabilities" not in roots["landscape"] + roots["forces"]
    assert "Disclosed response" in roots["forces"]
    assert "118,762" not in roots["inside"]
    if path == "/enterprises/lloyds":
        assert 'data-intelligence="service-recovery"' in roots["landscape"]
        assert "£502.8bn" in roots["landscape"]
        assert "£502.8bn" not in roots["inside"]


@pytest.mark.parametrize("scope,keys", [("uk", experience.UK_DIMENSIONS), ("banking", experience.BANKING_FORCES)])
def test_force_lenses_retain_subject_and_reject_outside_scope(scope, keys):
    path = v.SCOPES[scope]["route"]
    for key in keys:
        query = {"stream": ["forces"], "detail": [key]}
        facts = main(v.render(path, query))
        insight = main(v.render(path, {**query, "reading": ["insight"]}))
        assert f'detail={key}&amp;reading=insight' in facts
        assert 'class="experience-path"' in insight
        with pytest.raises(ValueError):
            v.resolve(path, {"stream": ["landscape"], "detail": [key]})


def test_airline_root_withdrawal_keeps_conceptual_map(monkeypatch):
    data = easyjet._data()
    next(s for s in data["sources"] if s["id"] == "SRC-AV-AR25")["withdrawn"] = True
    monkeypatch.setattr(easyjet, "_read_assessment", lambda: data)
    for mode in ("facts", "insight"):
        html = main(v.render(v.EASYJET_ROUTE, {"stream": ["inside"], "reading": [mode]}))
        assert "356 aircraft" not in html
        assert "Durable capabilities" in html
        assert 'data-semantic-type="insight"' not in html
