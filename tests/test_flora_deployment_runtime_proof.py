from cios.applications.flora.blueprint_import import runtime_proof as subject


def test_declaration_is_not_feature_proof(monkeypatch):
    monkeypatch.setattr(subject.importlib, "import_module", lambda _: object())
    proof = subject.runtime_proof()
    assert not proof.bt_route_connected
    assert proof.runtime_verdict != "PROVEN CURRENT"


def test_commit_mismatch(monkeypatch):
    monkeypatch.setattr(subject, "_repository_commit", lambda: "AAA")
    monkeypatch.setenv("RENDER_GIT_COMMIT", "BBB")
    proof = subject.runtime_proof()
    assert proof.commit_match == "NO"
    assert proof.executive_answer == "NO"


def test_commit_unknown_is_not_mismatch(monkeypatch):
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    proof = subject.runtime_proof()
    assert proof.commit_match == "UNKNOWN"
    assert proof.runtime_verdict != "PROVEN MISMATCH"


def test_loaded_but_route_disconnected(monkeypatch):
    monkeypatch.setattr(subject, "_repository_commit", lambda: "AAA")
    monkeypatch.setenv("RENDER_GIT_COMMIT", "AAA")
    monkeypatch.setattr(subject.importlib, "import_module", lambda _: object())
    proof = subject.runtime_proof()
    assert proof.implementation_present and proof.implementation_loaded
    assert not proof.bt_route_connected
    assert proof.runtime_verdict == "DEPLOYMENT PROVEN — FEATURE FAILURE"


def test_full_runtime_proof(monkeypatch):
    monkeypatch.setattr(subject, "_repository_commit", lambda: "AAA")
    monkeypatch.setenv("RENDER_GIT_COMMIT", "AAA")
    proof = subject.runtime_proof()
    assert proof.bt_route_connected and proof.advanced_inspection_connected
    assert proof.executive_answer == "YES"
