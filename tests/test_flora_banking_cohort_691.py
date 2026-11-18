import pytest

from cios.applications.flora import banking_cohort as cohort
from cios.applications.flora import leadership_agenda as agenda
from cios.applications.flora import visual_streams as v
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_uxr1_650 import main


@pytest.mark.parametrize("subject", cohort.SUBJECTS)
def test_cohort_perspectives_and_exact_context(subject):
    path = "/industries/banking"
    for stream in cohort.STREAMS:
        query = {"selected": [subject], "stream": [stream]}
        facts = v.render(path, query)
        insight = v.render(path, {**query, "reading": ["insight"]})
        assert "aria-current=page>Facts" in facts
        assert "aria-current=page>FLORA Insight" in insight
        assert f"stream={stream}&amp;selected={subject}&amp;reading=insight" in facts
        assert cohort.SUBJECTS[subject][0] in facts + insight
        assert "What's changing?" not in facts + insight
    assert v.BANKING_ART in v.render(path, {"selected": [subject]})


def test_service_withdrawal_keeps_starling_structure(monkeypatch):
    query = {"selected": ["starling"], "stream": ["inside"]}
    assert "15,223" in main(v.render("/industries/banking", query))
    original = agenda.routine_service_issue
    monkeypatch.setattr(agenda, "routine_service_issue", lambda key: None if key == "starling" else original(key))
    for mode in ("facts", "insight"):
        html = main(v.render("/industries/banking", {**query, "reading": [mode]}))
        assert "15,223" not in html and "Durable capabilities" in html
        assert "Scoped evidence for this selection is unavailable" in html


@pytest.mark.parametrize("query", [
    {"stream": ["inside"]},
    {"stream": ["inside"], "selected": ["monzo"]},
    {"stream": ["inside"], "selected": ["natwest"], "detail": ["payments"]},
    {"stream": ["inside"], "selected": ["boe"], "agenda": ["provider-oversight"]},
])
def test_unsupported_contexts_are_rejected(query):
    with pytest.raises(ValueError):
        v.resolve("/industries/banking", query)


def test_infrastructure_is_contextual_and_not_a_participant_register():
    html = main(v.render("/industries/banking", {"stream": ["inside"], "selected": ["boe"]}))
    assert "Conceptual" in html and "bilateral dependencies are unverified" in html
    assert "4 November 2026" not in html and "Pay.UK" not in html
    assert not public_request_target("/industries/banking?selected=boe&stream=inside&workspace=private")


@pytest.mark.parametrize("subject,period", [
    ("natwest", "1 January–30 June 2026"),
    ("hsbc-uk", "1 January–30 June 2026"),
    ("nationwide", "1 October 2025–31 March 2026"),
    ("starling", "1 October 2025–31 March 2026"),
])
def test_legal_service_period_is_subject_specific(subject, period):
    html = main(v.render("/industries/banking", {"stream": ["inside"], "selected": [subject]}))
    assert period in html


def test_specialist_bank_picker_remains_available_at_cohort_landing():
    html = main(v.render("/industries/banking", {"selected": ["hsbc-uk"], "layer": ["regulators"]}))
    assert 'aria-label="Banking enterprises"' in html
    assert 'layer=regulators&amp;selected=santander-uk' in html
