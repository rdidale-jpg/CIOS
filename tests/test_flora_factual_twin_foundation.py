from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table

from cios.applications.flora.live.documents import fetch_document, parse_pdf_document, DocumentFetchResult
from cios.applications.flora.live.source_registry import SourceRecord
from cios.applications.flora.memory.factual_twin import extract_factual_evidence, coverage_for_model, maturity_for_model
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.memory.views import factual_digital_twin_workspace


def _pdf(tmp_path: Path) -> bytes:
    p = tmp_path / "bt.pdf"
    doc = SimpleDocTemplate(str(p))
    doc.build([
        Paragraph("BT Group plc Annual Report 2026. BT Group plc operates in the telecommunications sector. strategic pillar Build.", None),
        PageBreak(),
        Paragraph("Consumer is reported as a business unit. Openreach is reported as a reporting segment. EE brand.", None),
        PageBreak(),
        Table([["metric", "FY26"], ["Group revenue", "£20.4bn"], ["Consumer revenue", "£9.5bn"], ["adjusted EBITDA", "£8.2bn"], ["free cash flow", "£1.4bn"]]),
        PageBreak(),
        Paragraph("Allison Kirkby held the role of Group Chief Executive.", None),
    ])
    return p.read_bytes()


def _source():
    return SourceRecord(source_id="bt-fixture", organisation="BT Group plc", source_name="BT fixture PDF", source_type="annual_report", url="https://example.com/bt.pdf", sector="Telecommunications", evidence_tier="tier_1_company", authority_tier="tier_1_company_authoritative", expected_signal_types=[])


def test_pdf_ingestion_embedded_text_page_checksum_and_no_ocr(tmp_path):
    raw = _pdf(tmp_path)
    fetch = DocumentFetchResult("https://example.com/bt.pdf", True, 200, "application/pdf", raw, "a"*64, str(tmp_path/"bt.pdf"), "2026-07-04T00:00:00+00:00")
    doc = parse_pdf_document(fetch, _source(), canonical_enterprise_id="bt-group-plc")
    assert doc.parser_status == "parsed"
    assert doc.page_count == 4
    assert doc.checksum == "a"*64
    assert doc.pages[0].page_number == 1
    assert "BT Group plc" in doc.pages[0].text
    assert doc.extraction_method == "embedded_text"
    assert "OCR" not in doc.extraction_method.upper()


def test_encrypted_or_no_text_pdf_fails_clearly(tmp_path):
    fetch = DocumentFetchResult("https://example.com/e.pdf", True, 200, "application/pdf", b"%PDF /Encrypt", "b"*64, "", "2026-07-04T00:00:00+00:00")
    doc = parse_pdf_document(fetch, _source(), canonical_enterprise_id="bt-group-plc")
    assert doc.parser_status == "failed"
    assert doc.error == "unsupported encryption"
    fetch2 = DocumentFetchResult("https://example.com/s.pdf", True, 200, "application/pdf", b"%PDF-1.4\n%%EOF", "c"*64, "", "2026-07-04T00:00:00+00:00")
    doc2 = parse_pdf_document(fetch2, _source(), canonical_enterprise_id="bt-group-plc")
    assert "OCR fallback required but not enabled" in doc2.warnings[0]


def test_table_fact_observation_model_idempotent_and_lineage(tmp_path):
    raw = _pdf(tmp_path)
    fetch = DocumentFetchResult("https://example.com/bt.pdf", True, 200, "application/pdf", raw, "d"*64, str(tmp_path/"bt.pdf"), "2026-07-04T00:00:00+00:00")
    doc = parse_pdf_document(fetch, _source(), canonical_enterprise_id="bt-group-plc")
    evidence, rejected = extract_factual_evidence(doc)
    assert any(e["page_number"] == 3 and "Group revenue" in e["extracted_text"] for e in evidence)
    assert any("Consumer revenue" in e["extracted_text"] and "FY26" in e["affected_attribute"] for e in evidence)
    assert any(e["commercial_condition"] == "strategic_pillar_stated" for e in evidence)
    assert any(e["commercial_condition"] == "executive_role_confirmed" for e in evidence)
    svc = ObservationMemoryService(ObservationRepository(tmp_path/"obs.jsonl"), EnterpriseModelRepository(tmp_path/"models"))
    results1 = [svc.accept_evidence(e) for e in evidence]
    results2 = [svc.accept_evidence(e) for e in evidence]
    model = svc.models.get("bt-group-plc")
    assert any(r.action == "created" for r in results1)
    assert len(svc.observations.list()) == len({o.observation_id for o in svc.observations.list()})
    assert any(k.startswith("financial_performance.metrics.revenue.FY26.actual") for k in model.attributes)
    assert any(k.startswith("financial_performance.metrics.revenue.FY26.actual") for k in model.attributes)
    assert "structure.units.Consumer" in model.attributes
    assert "strategy.pillars.Build" in model.attributes
    assert "leadership.roles.Group Chief Executive" in model.attributes
    assert all(a.observation_ids and a.evidence_ids for a in model.attributes.values())
    assert maturity_for_model(model) == "Foundation"
    coverage = coverage_for_model(model)
    assert coverage["financial_performance"]["coverage_percent"] >= 40


def test_factual_workspace_renders_drilldown_without_raw_error_dicts(tmp_path):
    raw = _pdf(tmp_path)
    fetch = DocumentFetchResult("https://example.com/bt.pdf", True, 200, "application/pdf", raw, "e"*64, str(tmp_path/"bt.pdf"), "2026-07-04T00:00:00+00:00")
    doc = parse_pdf_document(fetch, _source(), canonical_enterprise_id="bt-group-plc")
    evidence, _ = extract_factual_evidence(doc)
    svc = ObservationMemoryService(ObservationRepository(tmp_path/"obs.jsonl"), EnterpriseModelRepository(tmp_path/"models"))
    for e in evidence: svc.accept_evidence(e)
    html = factual_digital_twin_workspace("bt-group-plc", svc.models, svc.observations, evidence)
    assert "BT Digital Twin" in html and "Foundation" in html
    assert "Structure" in html and "Financials" in html and "Evidence Detail" in html
    assert "page 3" in html or "<td>3</td>" in html
    assert "{'" not in html
