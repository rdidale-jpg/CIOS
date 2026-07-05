from cios.applications.flora.financial_intelligence.normalisation import canonicalise_financial_claim, canonical_metric, METRIC_CATALOGUE
from cios.applications.flora.financial_intelligence.schema import ExperimentDocument, ExtractionRun, FoundationFact
from cios.applications.flora.financial_intelligence.section_packets import merge_packet_facts
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository
from cios.applications.flora.memory.service import ObservationMemoryService


def claim(predicate='reported revenue for FY26', amount=19.7, scale='bn', basis='statutory'):
    return {
        'claim_type':'financial_metric_reported','canonical_enterprise_id':'bt-group-plc','predicate':predicate,
        'metric_identity':predicate,'reported_amount':amount,'value':amount,'reported_scale':scale,'scale':scale,
        'currency':'GBP','period':'FY26','state':'actual','page_reference':'3','source_excerpt':f'{predicate} £{amount}{scale}',
        'business_unit':'BT Group plc','confidence':95,'evidence_id':'E1','accounting_basis':basis,
        'original_statement':f'BT Group plc reported {predicate} of £{amount}{scale}.'
    }


def test_provider_labels_do_not_slugify_and_aliases_resolve():
    assert canonical_metric('reported revenue for FY26') == 'revenue'
    assert canonical_metric('Adjusteda EBITDA for FY26') == 'adjusted_ebitda'
    assert canonical_metric('reported revenue for FY26') != 'reported_revenue_for_fy26'
    assert 'FY26' not in canonical_metric('capital expenditure for FY26')
    assert set(METRIC_CATALOGUE) >= {'revenue','adjusted_ebitda','operating_profit','profit_before_tax','capital_expenditure','cash_flow_from_operating_activities','normalised_free_cash_flow','net_debt'}


def test_canonical_path_numeric_value_and_display_are_separate(tmp_path):
    c, reasons = canonicalise_financial_claim(claim())
    assert reasons == []
    assert c['affected_attribute'] == 'financial_performance.metrics.revenue.FY26.actual'
    assert c['normalised_amount'] == 19700000000
    assert c['original_display_value'] == '£19.7bn'
    assert c['canonical_financial_fact']['normalised_amount'] == 19700000000
    svc = ObservationMemoryService(ObservationRepository(tmp_path/'obs.jsonl'), EnterpriseModelRepository(tmp_path/'models'))
    report = svc.process_evidence({'enterprise_id':'bt-group-plc','canonical_enterprise_id':'bt-group-plc','commercial_condition':'financial_metric_reported','cleaned_observation':'BT Group plc reported FY26 Revenue of £19.7bn.','affected_attribute':c['affected_attribute'],'value':c['normalised_amount'],'evidence_id':'E1','page_range':'3','confidence':95,'publication_date':'2026-01-01'})
    assert report.results
    model = EnterpriseModelRepository(tmp_path/'models').get('bt-group-plc')
    assert model.attributes[c['affected_attribute']].current_value == 19700000000
    assert model.attributes[c['affected_attribute']].current_value != 'BT Group plc reported FY26 Revenue of £19.7bn.'


def test_narrative_and_ambiguous_basis_block_acceptance():
    c, reasons = canonicalise_financial_claim(claim('reiterated expectation of cash flow inflection in FY27', 2.0, None, None))
    assert 'non_numeric_narrative' in reasons
    c2, reasons2 = canonicalise_financial_claim(claim('operating profit', 1.0, 'bn', None))
    assert 'accounting_basis_ambiguous' in reasons2
    assert c2['canonical_financial_fact'] is None


def test_multiple_packet_facts_are_not_truncated_or_overwritten():
    doc = ExperimentDocument(document_id='d', enterprise_id='bt-group-plc', title='t', source_url='u', retrieval_timestamp='now', checksum='h', media_type='application/pdf', page_count=20)
    facts=[]
    for i in range(10):
        facts.append(FoundationFact.model_validate({'fact_id':f'f{i}','canonical_enterprise_id':'bt-group-plc','claim_type':'financial_metric_reported','subject_type':'enterprise','subject_name':'BT Group plc','predicate':'revenue' if i%2 else 'capital expenditure','object_type':'metric','value':{'kind':'numeric','amount':i+1,'scale':'bn','unit':'GBP','currency':'GBP'},'business_unit':'BT Group plc','period_label':f'FY{i}','state':'actual','source_document_id':'d','source_page_start':i+1,'source_page_end':i+1,'source_excerpt':f'fact {i} £{i+1}bn','extraction_confidence':.9,'explicit_in_source':True,'extractor_provider':'openai','extractor_model':'m','extractor_version':'m'}))
    runs=[ExtractionRun(run_id='r1',route='x',provider='openai',model='m',status='completed',started_at='x',completed_at='x',latency_seconds=0,facts=facts[:5]), ExtractionRun(run_id='r2',route='x',provider='openai',model='m',status='completed',started_at='x',completed_at='x',latency_seconds=0,facts=facts[5:])]
    merged = merge_packet_facts(runs, doc)
    assert len(merged.facts) == 10
    assert [f.fact_id for f in merged.facts][:5] == [f'f{i}' for i in range(5)]
