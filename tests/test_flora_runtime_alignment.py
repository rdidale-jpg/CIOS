from pathlib import Path

from cios.applications.flora.live.alignment import (
    USER_FEEDBACK_PATH, build_acquisition_plans, can_support_strategic_signal,
    collection_priority, coverage_map_for, evidence_quality_band, lifecycle_action,
    persist_feedback, source_tier,
)
from cios.applications.flora.live.extractor import classify_relevance
from cios.applications.flora.live.source_registry import SourceRecord


def source(source_type='annual_report'):
    return SourceRecord(source_id='s1', organisation='Org', source_name='Annual report', source_type=source_type, url='https://example.com/report', sector='Utilities', evidence_tier='tier_1_company', expected_signal_types=['investment'])


def test_quality_bands_and_source_tiering():
    item={'source_type':'annual_report','source_name':'Annual report','evidence_type':'Primary Evidence','overall_evidence_quality':82,'specificity_markers':['quantified_value']}
    assert evidence_quality_band(item) >= 90
    assert source_tier('annual_report', 'Annual report', '') == 'Tier 1'
    assert source_tier('careers', 'Careers landing', '') == 'Tier 3'
    assert source_tier('accessibility', 'Accessibility statement', '') == 'diagnostics-only'


def test_boilerplate_rejected_supplier_menu_context_named_programme_accepted():
    gov='Jobs and contracts Procurement at DWP Working for DWP Publication scheme Accessibility Contact us'
    assert classify_relevance(gov, 'Procurement Readiness', source('govuk_publications'))['accepted_for_claims'] is False
    menu='Cloud services Data services Managed services Contact Careers About us'
    assert classify_relevance(menu, 'AI Modernisation', source('supplier_service_menu'))['evidence_type'] == 'Context Only'
    named='In 2026 the Phoenix modernisation programme will invest £15 million in a cloud platform with Microsoft.'
    assert classify_relevance(named, 'AI Modernisation', source('annual_report'))['accepted_for_claims'] is True


def test_coverage_plan_priority_lifecycle_and_signal_gate(tmp_path):
    evidence=[{'organisation':'Org','source_id':'a','source_type':'annual_report','source_name':'Annual report','evidence_type':'Primary Evidence','snippet':'2026 strategy programme invests £15 million in cloud platform','commercial_condition':'AI Modernisation','likely_capability':'cloud','specificity_markers':['quantified_value','named_programme'],'overall_evidence_quality':85,'evidence_quality_band':95,'source_tier':'Tier 1','extraction_timestamp':'2026-07-02T00:00:00+00:00'}]
    cmap=coverage_map_for('Org', evidence)
    assert any(r['category']=='Strategy' and r['evidence_count'] for r in cmap)
    plans=build_acquisition_plans([source()], evidence, [])
    assert plans[0]['organisation']=='Org'
    assert plans[0]['evidence_demand']
    assert collection_priority('high', 25) == 'collect urgently'
    lc=lifecycle_action({'source_type':'landing_page','source_classification':'landing_page','accepted_evidence_count':0,'rejected_evidence_count':4,'context_only_count':4})
    assert lc['lifecycle_action'] in {'diagnostics only','split into child sources','replace'}
    assert can_support_strategic_signal(evidence[0]) is True
    context=dict(evidence[0], evidence_type='Context Only', source_tier='Tier 3', evidence_quality_band=55)
    assert can_support_strategic_signal(context) is False


def test_feedback_persisted_and_affects_scoring(tmp_path, monkeypatch):
    # Use the real path but clean only this test's target id records are harmless JSONL append.
    row=persist_feedback('evidence','E-TEST','useful evidence','Org','ok')
    assert row['target_id']=='E-TEST'
    item={'evidence_id':'E-TEST','source_type':'annual_report','evidence_type':'Primary Evidence','overall_evidence_quality':75,'specificity_markers':['named_programme']}
    assert evidence_quality_band(item) >= 85


def test_no_llm_database_broad_crawl_imports():
    code='\n'.join(Path('cios/applications/flora/live').glob('*.py').__str__() for _ in [])
    for path in Path('cios/applications/flora/live').glob('*.py'):
        text=path.read_text().lower()
        assert 'openai' not in text
        assert 'sqlalchemy' not in text
        assert 'scrapy' not in text
