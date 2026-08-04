"""Pilot Blueprint review authority remains separate from promotion authority."""
from __future__ import annotations

from cios.applications.flora.access import (
    BLUEPRINT_PROMOTE_PERMISSION,
    BLUEPRINT_REVIEW_PERMISSION,
    blueprint_upload_authorisation,
    flora_roles,
)
from cios.applications.flora.blueprint_import.promotion import (
    can_approve_blueprint_promotion,
    can_execute_blueprint_promotion,
)
from cios.applications.flora.blueprint_import.views import (
    promotion_confirmation_page,
    review_page,
    upload_and_validate_blueprint,
)
from cios.applications.flora.pilot_import import PILOT_IMPORT_ACTOR
from tests.test_flora_blueprint_import_validation import pkg


def _pilot(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    monkeypatch.delenv("FLORA_PILOT_AUTO_SIGN_IN", raising=False)


def test_pilot_upload_review_and_dispositions_do_not_grant_promotion(monkeypatch, tmp_path):
    _pilot(monkeypatch, tmp_path)
    records = [
        {"external_id": "TEL-OBS-1", "record_class": "observation", "truth_class": "evidence_backed",
         "payload": {"proposed_effect": "unchanged"}},
        {"external_id": "TEL-UNKNOWN-1", "record_class": "unknown", "truth_class": "unknown", "payload": {}},
    ]

    upload = blueprint_upload_authorisation({})
    assert upload.decision == "allowed"
    assert upload.user_id == PILOT_IMPORT_ACTOR
    assert BLUEPRINT_REVIEW_PERMISSION in flora_roles({})
    assert BLUEPRINT_PROMOTE_PERMISSION not in flora_roles({})

    _, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": pkg({"enterprise_id": "TEL-001"}, records=records)},
        {"blueprint_zip.filename": "TEL-001.zip", "blueprint_zip.content_type": "application/zip"},
        {},
    )
    assert status == 200
    run_id = target.rsplit("/", 1)[-1]

    review, review_status = review_page(run_id, {})
    assert review_status == 200
    assert "TEL-OBS-1" in review
    assert "observation" in review
    assert "unchanged" in review.casefold()
    assert "Promotion permission required" in review
    assert not can_approve_blueprint_promotion({}, "TEL-001")
    assert not can_execute_blueprint_promotion({}, "TEL-001")

    promotion, promotion_status = promotion_confirmation_page(run_id, {})
    assert promotion_status == 403
    assert "do not have permission to promote" in promotion
    assert not (tmp_path / "memory").exists()


def test_non_pilot_workspace_and_capability_checks_are_unchanged(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    monkeypatch.delenv("FLORA_ENVIRONMENT", raising=False)
    authorised = {
        "X-Flora-User": "reviewer", "X-Flora-Enterprises": "TEL-001",
        "X-Flora-Active-Workspace": "TEL-001", "X-Flora-Roles": "package.upload,package.review",
    }
    unauthorised = {
        "X-Flora-User": "outsider", "X-Flora-Enterprises": "OTHER",
        "X-Flora-Active-Workspace": "OTHER", "X-Flora-Roles": "package.review",
    }
    _, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": pkg({"enterprise_id": "TEL-001"})},
        {"blueprint_zip.filename": "TEL-001.zip", "blueprint_zip.content_type": "application/zip"},
        authorised,
    )
    assert status == 200
    denied, denied_status = review_page(target.rsplit("/", 1)[-1], unauthorised)
    assert denied_status == 403
    assert "not authorised to review" in denied
