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
        assert 'aria-label="Reading mode"' not in facts
        assert main(facts) == main(insight)
        assert f"stream={stream}&amp;selected={subject}" in facts
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
    assert "Conceptual" in html and "participant links remain unverified" in html
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


def test_hsbc_perspectives_separate_model_activity_and_pressure():
    query = {"selected": ["hsbc-uk"]}
    landscape = main(v.render("/industries/banking", query))
    inside = main(v.render("/industries/banking", {**query, "stream": ["inside"]}))
    forces = main(v.render("/industries/banking", {**query, "stream": ["forces"], "reading": ["insight"]}))
    assert landscape.index("How a UK bank inside a wider group earns") < landscape.index("Customer service evidence")
    assert "Conceptual · activity and capability map" in inside
    assert "79,323" in forces and "59.09%" not in forces
    assert "Service workload" in forces and "Company response" in forces
    assert forces.count("Compare rates on a matched customer base") == 1


def test_starling_platform_is_separate_from_scoped_bank_evidence():
    query = {"selected": ["starling"], "reading": ["insight"]}
    html = main(v.render("/industries/banking", query))
    assert "Group and Engine platform economics remain separate research" in html
    assert "data-semantic-type=\"insight\"" not in html
    assert "15,223" in html
    assert "Starling Bank Limited" in html and "1 October 2025–31 March 2026" in html


def test_nationwide_group_and_society_views_remain_separate():
    path = "/industries/banking"
    query = {"selected": ["nationwide"]}
    landscape = main(v.render(path, {**query, "reading": ["insight"]}))
    inside = main(v.render(path, {**query, "stream": ["inside"]}))
    assert "6,378 − 4,021 − 331 = 2,026" in landscape
    assert "£2,026m + £1m − £138m − £399m = £1,490m" in landscape
    assert landscape.count("6,378 − 4,021 − 331 = 2,026") == 1
    assert "100,886" in landscape and "100,886" in inside
    assert "Customer complaints · Society" in landscape
    assert "Consolidated Group" in landscape and "31 March 2026" in landscape
    assert "1 October 2025–31 March 2026" in inside and "6,378" not in inside
