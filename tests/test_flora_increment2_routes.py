from __future__ import annotations

import threading
from http.client import HTTPConnection
from urllib.parse import quote_plus

from cios.applications.flora.web.app import FloraWebHandler
from cios.applications.flora.enterprise_intelligence.explain import increment2_runtime_path, runtime_audit_log_path


def _get(path: str) -> tuple[int, str]:
    server = __import__("http.server").server.ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start(); conn = HTTPConnection("127.0.0.1", server.server_port)
    try:
        conn.request("GET", path)
        response = conn.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        conn.close(); server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_lloyds_workspace_exposes_fixed_explain_action_without_prompt_input() -> None:
    status, html = _get("/flora/object/BK-ENT-001")
    assert status == 200
    assert "Explain what has changed" in html
    assert "/flora/object/BK-ENT-001/explain" in html
    assert "Q-LBG-CHANGE-EXPLAIN-001" in html
    assert "name='question'" not in html


def test_rendered_explain_contains_required_distinct_sections_and_identifiers() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain")
    assert status == 200
    for text in [
        "Explanation summary", "Supported changes", "Source passages", "Evidence", "Governed Observations",
        "Bounded interpretations", "Unknowns", "Competing interpretations", "Confidence limits", "Next Evidence demands",
        "Context Package ID:", "Package hash:", "Baseline:", "Inspect Context Package independently",
    ]:
        assert text in html
    assert "recommend pursuit" not in html.lower()
    assert "opportunity score" not in html.lower()


def test_context_package_and_claim_lineage_are_independently_inspectable() -> None:
    for path, expected in [
        ("/flora/object/BK-ENT-001/context-package", "Inspectable Context Package"),
        ("/flora/object/BK-ENT-001/lineage/CHG-LBG-002", "Claim-level lineage"),
    ]:
        status, html = _get(path)
        assert status == 200
        assert expected in html
        assert "Source passages" in html or "Runtime lineage" in html


def test_unsupported_question_and_object_fail_safely_without_partial_explanation() -> None:
    status, html = _get("/flora/object/BK-ENT-001/explain?question_id=" + quote_plus("Q-UNSUPPORTED"))
    assert status == 200
    assert "Safe unavailable" in html
    assert "unsupported_question" in html
    assert "Supported change:" not in html

    status, html = _get("/flora/object/unsupported-object")
    assert status == 200
    assert "safe_unavailable" in html


def test_audit_events_are_complete_and_non_canonical_for_runtime_path(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    outcome = increment2_runtime_path(correlation_id="test-correlation")
    assert outcome["status"] == "available"
    required = {
        "approved_question_validation", "context_plan_creation", "governed_retrieval", "exclusions",
        "context_package_assembly", "package_validation", "package_freezing", "bounded_explain_execution", "output_validation",
    }
    assert required <= {e["event_type"] for e in outcome["audit_events"]}
    for event in outcome["audit_events"]:
        for field in ["correlation_id", "focus_object_id", "approved_question_id", "context_package_id", "context_package_version", "context_package_hash", "retrieval_policy_version", "corpus_baseline", "evaluation_baseline", "worker_or_model_identifier", "prompt_version", "execution_timestamp", "validator_outcome", "failure_reason", "route_identifier", "lifecycle_classification"]:
            assert field in event
        assert event["lifecycle_classification"] == "non_canonical_runtime_audit_event"
    assert runtime_audit_log_path().exists()
    assert "non_canonical_runtime_audit_event" in runtime_audit_log_path().read_text()
