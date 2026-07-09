import json

import pytest

from cios.applications.flora.enterprise_canvas.feedback import EnterpriseCanvasFeedbackService, FeedbackAccessError
from cios.applications.flora.memory.repository import EnterpriseModelRepository, EvidenceRepository, ObservationRepository
from tests.test_flora_enterprise_canvas import HEADERS, model, stage_projections

REVIEW = {**HEADERS, "X-Flora-Roles": "feedback.review,feedback.view,feedback.submit"}
SUBMIT = {**HEADERS, "X-Flora-Roles": "feedback.submit,feedback.view"}
BAD = {"X-Flora-User": "mallory", "X-Flora-Enterprises": "other", "X-Flora-Roles": "feedback.submit"}


def submit(action, **kw):
    payload = dict(
        enterprise_id="synthetic-enterprise",
        tile_view_id="canvas-tile-abc",
        displayed_judgement_ref="Workforce pressure is affecting care access",
        lineage_ref="synthetic-enterprise:care_board",
        related_canonical_refs=("obs-state", "ev-state"),
        action_type=action,
        user_statement=f"statement for {action}",
        rationale=f"rationale for {action}",
        contributor_role="Account director",
        expected_consequence="review may strengthen or weaken the judgement",
        visibility="standard",
        supplied_at="2026-07-09T12:00:00+00:00",
        source_publication_or_package_version="1.0.0",
    )
    payload.update(kw)
    return EnterpriseCanvasFeedbackService().submit(SUBMIT, **payload)


def test_authorised_feedback_submission_and_tile_link(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    record = submit("confirm")
    assert record.feedback_id == "ecf-8fb4553aad655b7e5623"
    assert record.status == "submitted"
    assert record.tile_view_id == "canvas-tile-abc"
    assert record.displayed_judgement_ref.startswith("Workforce pressure")
    assert record.contributor_identity == "alice"
    assert record.contributor_role == "Account director"
    assert record.audit_history[0].event_type == "submitted"
    assert EnterpriseCanvasFeedbackService().visible_feedback(SUBMIT, "synthetic-enterprise", tile_view_id="canvas-tile-abc")[0].feedback_id == record.feedback_id


def test_unauthorised_submission_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    with pytest.raises(FeedbackAccessError):
        EnterpriseCanvasFeedbackService().submit(BAD, enterprise_id="synthetic-enterprise", action_type="confirm", user_statement="ok", rationale="because")


@pytest.mark.parametrize("action", ["confirm", "challenge", "correction", "context", "refresh"])
def test_plain_feedback_actions(tmp_path, monkeypatch, action):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    record = submit(action)
    assert record.action_type == action
    assert record.human_knowledge_classification == "not_human_knowledge"


def test_human_supplied_knowledge_requires_and_preserves_label(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    with pytest.raises(ValueError):
        submit("human_knowledge", human_knowledge_classification="not_human_knowledge")
    record = submit("human_knowledge", human_knowledge_classification="account_knowledge", supports_weakens_or_contradicts="supports", documentary_evidence_may_exist="yes")
    assert record.human_knowledge_classification == "account_knowledge"
    assert record.supports_weakens_or_contradicts == "supports"
    assert record.documentary_evidence_may_exist == "yes"


def test_unknown_contradiction_and_evidence_request_candidates(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    unk = submit("unknown", what_could_resolve_it="workforce rota evidence")
    con = submit("contradiction", position_a="capacity is stable", position_b="capacity is constrained")
    ev = submit("evidence_request", likely_owner_or_source="operations lead", urgency_or_accountability_event="board review")
    assert unk.linked_unknown_candidate["candidate_type"] == "unknown"
    assert unk.linked_unknown_candidate["what_could_resolve_it"] == "workforce rota evidence"
    assert con.linked_contradiction_candidate["position_a"] == "capacity is stable"
    assert con.linked_contradiction_candidate["position_b"] == "statement for contradiction"
    assert ev.evidence_request["likely_owner_or_source"] == "operations lead"
    assert ev.evidence_request["urgency_or_accountability_event"] == "board review"


def test_confidentiality_handling_and_status_display(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    restricted = submit("context", visibility="restricted")
    assert EnterpriseCanvasFeedbackService().visible_feedback(SUBMIT, "synthetic-enterprise") == []
    assert EnterpriseCanvasFeedbackService().visible_feedback(REVIEW, "synthetic-enterprise")[0].feedback_id == restricted.feedback_id


def test_review_state_change_and_unauthorised_review_rejection(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    record = submit("challenge")
    with pytest.raises(FeedbackAccessError):
        EnterpriseCanvasFeedbackService().change_status(SUBMIT, record.feedback_id, "under_review")
    updated = EnterpriseCanvasFeedbackService().change_status(REVIEW, record.feedback_id, "needs_evidence", "ask owner")
    assert updated.status == "needs_evidence"
    assert [e.event_type for e in updated.audit_history] == ["submitted", "status_changed"]


def test_append_only_audit_and_supersession_not_silent_edit(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    first = submit("correction", user_statement="old correction")
    second = submit("correction", user_statement="new correction", supersedes_feedback_id=first.feedback_id, supplied_at="2026-07-09T12:01:00+00:00")
    EnterpriseCanvasFeedbackService().change_status(REVIEW, first.feedback_id, "superseded", "replaced by later correction")
    rows = EnterpriseCanvasFeedbackService().repo.list_all()
    assert len(rows) == 3
    assert rows[0].user_statement == "old correction"
    assert second.supersedes_feedback_id == first.feedback_id


def test_no_canonical_mutation_from_feedback_submission(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    model(tmp_path); stage_projections()
    before_model = EnterpriseModelRepository().get("synthetic-enterprise").to_dict()
    before_ev = [dict(r) for r in EvidenceRepository().list()]
    before_obs = [o.to_dict() for o in ObservationRepository().list()]
    submit("human_knowledge", human_knowledge_classification="validation")
    assert EnterpriseModelRepository().get("synthetic-enterprise").to_dict() == before_model
    assert EvidenceRepository().list() == before_ev
    assert [o.to_dict() for o in ObservationRepository().list()] == before_obs
    assert "MOD" not in json.dumps([r.to_dict() for r in EnterpriseCanvasFeedbackService().repo.list_all()])
