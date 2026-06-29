"""Tests for Flora v0.1."""

from __future__ import annotations

import ast
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
import subprocess
import sys
import pytest
import threading
from pathlib import Path

from cios.applications.flora.models import CommercialDNA, Priority, Signal, TargetAccount
from cios.applications.flora.pipeline import generate_daily_brief, generate_weekly_brief
from cios.applications.flora.scoring import calculate_scores
from cios.applications.flora.seed_data import sample_commercial_dna, sample_signals, sample_watchlist


def test_commercial_dna_model_construction() -> None:
    dna = sample_commercial_dna()
    assert isinstance(dna, CommercialDNA)
    assert "Telecommunications" in dna.sectors
    assert "Accenture" in dna.competitors


def test_watchlist_model_construction() -> None:
    watchlist = sample_watchlist()
    assert any(account.organisation_name == "Thames Water" for account in watchlist)
    assert watchlist[0].priority is Priority.HIGH


def test_signal_model_construction() -> None:
    signal = sample_signals()[0]
    assert isinstance(signal, Signal)
    assert signal.signal_id.startswith("FLORA-SIG-")
    assert signal.related_capabilities


def test_deterministic_scoring() -> None:
    dna = sample_commercial_dna()
    account = sample_watchlist()[0]
    signals = [signal for signal in sample_signals() if signal.organisation == account.organisation_name]
    first = calculate_scores(account, signals, dna)
    second = calculate_scores(account, signals, dna)
    assert first == second
    assert first.ai_reinvention_opportunity_score > 0


def test_daily_briefing_generation() -> None:
    brief = generate_daily_brief()
    assert brief.title == "Flora Daily Intelligence Brief"
    assert len(brief.items) == 5
    assert brief.items[0].rank == 1
    assert brief.items[0].strongest_detected_signals


def test_json_output_shape() -> None:
    payload = json.loads(generate_daily_brief().model_dump_json())
    assert payload["version"] == "0.2"
    assert payload["items"][0]["scores"]["ai_reinvention_opportunity_score"] >= 0
    assessment = payload["items"][0]["assessment"]
    assert assessment["evidence"]
    assert assessment["missing_evidence"]
    assert assessment["recommended_actions"][0]["commercial_pattern"]
    assert assessment["recommended_actions"][0]["sector_playbook"]
    assert assessment["recommended_actions"][0]["capability_playbook"]
    assert assessment["recommended_actions"][0]["executive_playbook"]
    assert assessment["recommended_actions"][0]["proposition"]


def test_cli_execution_text_and_json() -> None:
    text = subprocess.run([sys.executable, "-m", "cios.applications.flora.main"], check=True, text=True, capture_output=True)
    assert "Flora Daily Intelligence Brief" in text.stdout
    structured = subprocess.run([sys.executable, "-m", "cios.applications.flora.main", "--json"], check=True, text=True, capture_output=True)
    assert json.loads(structured.stdout)["items"]
    weekly = subprocess.run([sys.executable, "-m", "cios.applications.flora.main", "--weekly"], check=True, text=True, capture_output=True)
    assert "Flora Weekly Intelligence Brief" in weekly.stdout


def test_weekly_brief_generation() -> None:
    brief = generate_weekly_brief()
    assert brief.title == "Flora Weekly Intelligence Brief"
    assert brief.biggest_movers
    assert brief.score_changes
    assert brief.new_evidence
    assert brief.organisations_to_watch
    assert brief.organisations_to_deprioritise


def test_no_forbidden_imports() -> None:
    forbidden = {"openai", "requests", "httpx", "sqlalchemy", "sqlite", "sqlite3", "pymongo"}
    for path in Path("cios/applications/flora").rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = {node.module.split(".")[0]}
            else:
                continue
            assert forbidden.isdisjoint(imported), f"{path} imports {forbidden & imported}"

from cios.applications.flora.intelligence.case_file import generate_case_file
from cios.applications.flora.intelligence.evidence_engine import CommercialEvidence, EvidenceCategory, get_seed_evidence
from cios.applications.flora.intelligence.insight_engine import generate_insights
from cios.applications.flora.intelligence.timeline import build_timeline


def test_commercial_evidence_construction() -> None:
    evidence = get_seed_evidence()[0]
    assert isinstance(evidence, CommercialEvidence)
    assert evidence.evidence_category in set(EvidenceCategory)
    assert evidence.related_patterns


def test_insight_generation() -> None:
    evidence = [item for item in get_seed_evidence() if item.organisation == "Thames Water"]
    insights = generate_insights("Thames Water", evidence, ["ASSESSMENT-1"])
    assert insights
    assert insights[0].supporting_evidence
    assert "Customer Operations" in insights[0].title


def test_timeline_ordering() -> None:
    evidence = [item for item in get_seed_evidence() if item.organisation == "BT"]
    timeline = build_timeline(list(reversed(evidence)))
    assert [entry.entry_date for entry in timeline] == sorted(entry.entry_date for entry in timeline)
    assert len(timeline) == len(evidence)


def test_case_file_generation_and_narrative() -> None:
    case_file = generate_case_file("ThamesWater")
    assert case_file.organisation == "Thames Water"
    assert case_file.evidence
    assert case_file.timeline
    assert case_file.insights
    assert len(case_file.executive_summary.split()) <= 400
    assert case_file.open_questions


def test_cli_case_output_text_and_json() -> None:
    text = subprocess.run([sys.executable, "-m", "cios.applications.flora.main", "--case", "ThamesWater"], check=True, text=True, capture_output=True)
    assert "Living Commercial Case File: Thames Water" in text.stdout
    assert "Commercial Timeline" in text.stdout
    structured = subprocess.run([sys.executable, "-m", "cios.applications.flora.main", "--case", "BT", "--json"], check=True, text=True, capture_output=True)
    payload = json.loads(structured.stdout)
    assert payload["organisation"] == "BT"
    assert payload["evidence"]
    assert payload["timeline"]

from cios.applications.flora.workspace.app import FloraWorkspaceHandler, _display_urls, _env_host, _env_port, _print_startup_message
from cios.applications.flora.workspace.export import CASE_SLUGS, generate_export
from cios.applications.flora.workspace.feedback import create_feedback_record, create_logbook_record
from cios.applications.flora.workspace.views import case_page, landing_page


def test_workspace_server_defaults_to_localhost_port_8000(monkeypatch) -> None:
    monkeypatch.delenv("FLORA_HOST", raising=False)
    monkeypatch.delenv("FLORA_PORT", raising=False)
    assert _env_host() == "127.0.0.1"
    assert _env_port() == 8000


def test_workspace_server_accepts_hosted_preview_bind_env(monkeypatch) -> None:
    monkeypatch.setenv("FLORA_HOST", "0.0.0.0")
    monkeypatch.setenv("FLORA_PORT", "8000")
    assert _env_host() == "0.0.0.0"
    assert _env_port() == 8000
    assert _display_urls("0.0.0.0", 8000) == ["http://localhost:8000", "http://127.0.0.1:8000"]


def test_workspace_startup_message_prints_access_instructions(capsys, monkeypatch) -> None:
    monkeypatch.setenv("FLORA_PREVIEW_URL", "https://preview.example.test")
    _print_startup_message("0.0.0.0", 8000)
    output = capsys.readouterr().out
    assert "Listening on: 0.0.0.0:8000" in output
    assert "https://preview.example.test" in output
    assert "FLORA_HOST=0.0.0.0" in output
    assert "FLORA_PORT=8000" in output


def test_workspace_landing_page_renders() -> None:
    html = landing_page()
    assert "Good Morning Rob" in html
    assert "What changed?" in html
    assert "Watchlist" in html
    assert "/case/ThamesWater" in html


def test_workspace_head_request_supported() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FloraWorkspaceHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("HEAD", "/")
        response = connection.getresponse()
        assert response.status == 200
        assert response.getheader("Content-Type") == "text/html; charset=utf-8"
        assert response.read() == b""
    finally:
        connection.close()
        server.shutdown()
        server.server_close()


def test_workspace_case_file_page_renders_expected_sections() -> None:
    html = case_page("BT")
    for section in [
        "Executive Summary",
        "Commercial DNA View",
        "Commercial Timeline",
        "Evidence Ledger",
        "Commercial Insights",
        "Pressure Profile",
        "AI Reinvention Assessment",
        "Capability Heatmap",
        "Competitive Context",
        "Open Intelligence Questions",
        "Recommended Actions",
        "Explainability panel",
    ]:
        assert section in html


def test_workspace_static_export_generates_required_files(tmp_path) -> None:
    index_path = generate_export(tmp_path / "export")
    assert index_path == tmp_path / "export" / "index.html"

    required_files = [
        "index.html",
        "settings.html",
        "logbook.html",
        *(f"case/{slug}.html" for slug in CASE_SLUGS),
    ]
    for filename in required_files:
        assert (tmp_path / "export" / filename).is_file()

    index_html = index_path.read_text(encoding="utf-8")
    assert "Good Morning Rob" in index_html
    assert "href='case/ThamesWater.html'" in index_html
    assert "href='settings.html'" in index_html
    assert "href='logbook.html'" in index_html
    assert "href='/" not in index_html
    assert "action='/" not in (tmp_path / "export" / "logbook.html").read_text(encoding="utf-8")

    case_html = (tmp_path / "export" / "case" / "BT.html").read_text(encoding="utf-8")
    assert "Flora Case File" in case_html
    assert "href='../index.html'" in case_html
    assert "action='#feedback'" in case_html
    assert "href='/" not in case_html
    assert "action='/" not in case_html

def test_feedback_record_creation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    record = create_feedback_record(organisation="BT", action_text="Run discovery", feedback_type="Useful", optional_comment="Clear", source_page="/case/BT")
    assert record["feedback_id"].startswith("flora-feedback-")
    stored = json.loads((tmp_path / "feedback.jsonl").read_text().strip())
    assert stored["organisation"] == "BT"
    assert stored["feedback_type"] == "Useful"


def test_pilot_logbook_record_creation(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("FLORA_PILOT_DIR", str(tmp_path))
    record = create_logbook_record(biggest_insight="BT moved", biggest_miss="No sponsor", action_taken="Called account lead", flora_should_learn="Track sponsor gaps", value_score=5)
    assert record["logbook_id"].startswith("flora-logbook-")
    stored = json.loads((tmp_path / "logbook.jsonl").read_text().strip())
    assert stored["flora_value_score"] == 5
    assert stored["flora_should_learn"] == "Track sponsor gaps"

from cios.applications.flora.publisher.morning_edition import build_publication_context, generate_morning_edition


def test_publisher_generates_pdf_html_manifest_and_index(tmp_path) -> None:
    paths = generate_morning_edition(tmp_path)
    assert paths["pdf"].is_file()
    assert paths["pdf"].stat().st_size > 1000
    assert paths["html"].is_file()
    assert "Executive Summary" in paths["html"].read_text(encoding="utf-8")
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    assert manifest["product"] == "Flora Publisher"
    assert manifest["edition"] == "Morning Edition"
    assert manifest["case_files"]
    assert manifest["conditions"]
    index = paths["index"].read_text(encoding="utf-8")
    assert paths["pdf"].name in index
    assert paths["html"].name in index


def test_publisher_preserves_existing_flora_brief_compatibility(tmp_path) -> None:
    before = generate_daily_brief()
    generate_morning_edition(tmp_path)
    after = generate_daily_brief()
    assert after == before
    assert before.items[0].assessment is not None

from datetime import date
import types
import zipfile

from cios.applications.flora.publisher.morning_edition import write_release_notes
from cios.applications.flora.publisher.preview import generate_previews


def test_publisher_generates_zip_and_release_notes(tmp_path) -> None:
    paths = generate_morning_edition(tmp_path, publication_date=date(2026, 6, 29))
    assert paths["zip"].is_file()
    assert paths["release_notes"].is_file()

    notes = paths["release_notes"].read_text(encoding="utf-8")
    assert "Morning Edition version" in notes
    assert "Publication date" in notes
    assert "Morning_Edition_2026-06-29.zip" in notes
    assert "Known limitations" in notes
    assert "GitHub Release assets" in notes

    with zipfile.ZipFile(paths["zip"]) as archive:
        names = set(archive.namelist())
    assert "Morning_Edition_2026-06-29.pdf" in names
    assert "Morning_Edition_2026-06-29.html" in names
    assert "VERSION.json" in names
    assert "index.html" in names
    assert "previews/" in names


def test_preview_generation_creates_pngs_and_refreshes_zip(tmp_path, monkeypatch) -> None:
    paths = generate_morning_edition(tmp_path, publication_date=date(2026, 6, 29))

    class FakePixmap:
        def save(self, output_path: str) -> None:
            Path(output_path).write_bytes(b"fake-png")

    class FakePage:
        def get_pixmap(self, matrix, alpha: bool):  # noqa: ANN001
            return FakePixmap()

    class FakeDocument:
        def __iter__(self):
            return iter([FakePage(), FakePage()])

        def close(self) -> None:
            pass

    fake_fitz = types.SimpleNamespace(open=lambda _path: FakeDocument(), Matrix=lambda _x, _y: object())
    monkeypatch.setitem(sys.modules, "fitz", fake_fitz)

    previews = generate_previews(paths["pdf"], tmp_path)
    assert [path.name for path in previews] == ["page-01.png", "page-02.png"]
    assert all(path.parent == tmp_path / "previews" for path in previews)

    with zipfile.ZipFile(paths["zip"]) as archive:
        names = set(archive.namelist())
    assert "previews/page-01.png" in names
    assert "previews/page-02.png" in names


def test_preview_generation_gracefully_handles_missing_dependency(tmp_path, monkeypatch) -> None:
    paths = generate_morning_edition(tmp_path, publication_date=date(2026, 6, 29))
    monkeypatch.delitem(sys.modules, "fitz", raising=False)

    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):  # noqa: ANN001
        if name == "fitz":
            raise ImportError("missing fitz")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(RuntimeError, match="PyMuPDF"):
        generate_previews(paths["pdf"], tmp_path)


def test_write_release_notes_includes_required_sections(tmp_path) -> None:
    ctx = build_publication_context(date(2026, 6, 29))
    path = write_release_notes(ctx, tmp_path, "Morning_Edition_2026-06-29.zip")
    text = path.read_text(encoding="utf-8")
    for expected in ["Morning Edition version", "Publication date", "Files included", "Known limitations", "Instructions for downloading"]:
        assert expected in text
