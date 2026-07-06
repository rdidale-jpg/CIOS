"""Synthetic rapid Financial Intelligence fixtures for tests only."""
from __future__ import annotations

from copy import deepcopy
from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir


def bt_fy26_seeded_rapid_result(run_id: str = 'rfi-bt') -> dict:
    facts = [
        {'fact_id':'bt-fy26-revenue','concept':'revenue','label':'Revenue','value':'19,654','period':'year ended 31 March 2026','scope':'Group consolidated','unit':'GBP','scale':'millions','basis':'statutory','state':'actual','source_id':'bt-fy26-annual-report','location':'Annual Report 2026, consolidated income statement','evidence':'Revenue £19,654m','extraction_method':'test_fixture_seed','confidence':0.9,'verification_status':'candidate_awaiting_structured_verification','contradiction':None},
        {'fact_id':'bt-fy26-op-profit','concept':'operating_profit','label':'Operating profit','value':'2,897','period':'year ended 31 March 2026','scope':'Group consolidated','unit':'GBP','scale':'millions','basis':'statutory','state':'actual','source_id':'bt-fy26-annual-report','location':'Annual Report 2026, consolidated income statement','evidence':'Operating profit £2,897m','extraction_method':'test_fixture_seed','confidence':0.9,'verification_status':'candidate_awaiting_structured_verification','contradiction':None},
        {'fact_id':'bt-fy26-pbt','concept':'profit_before_tax','label':'Profit before tax','value':'1,436','period':'year ended 31 March 2026','scope':'Group consolidated','unit':'GBP','scale':'millions','basis':'statutory','state':'actual','source_id':'bt-fy26-annual-report','location':'Annual Report 2026, consolidated income statement','evidence':'Profit before tax £1,436m','extraction_method':'test_fixture_seed','confidence':0.9,'verification_status':'candidate_awaiting_structured_verification','contradiction':None},
    ]
    result = {'run_id':run_id,'workflow':'rapid_financial_intelligence','enterprise_id':'bt-group-plc','legal_name':'BT Group plc','reporting_period':'FY26','created_at':'2026-07-06T00:00:00+00:00','status':'completed_with_verification_pending','sources':[{'source_id':'bt-fy26-annual-report','temporary_file_cleaned_up':True,'retrieved':True}],'reported_financial_reality':facts,'management_commitments':[],'enterprise_pressure':[],'transformation_hypotheses':[],'flagship_transformation_outlook':[],'unknowns':['Fixture only.'],'contradictions':[],'verification_status':'rapid_candidate_only','candidate_fact_count':len(facts),'accepted_canonical_fact_count':0,'facts_awaiting_verification':len(facts),'metrics':{'ai_call_count':0,'estimated_provider_cost_usd':0},'verification_exceptions':[],'canonical_update':{'enterprise_model_updated':False,'observations_created':0,'reason':'fixture candidate facts await governed acceptance'},'user_result':'# BT Group plc FY26 Financial Pressure and Transformation Outlook\n\nFixture-only rapid intelligence.'}
    return deepcopy(result)


def persisted_bt_fy26_seeded_rapid_result(run_id: str = 'rfi-bt') -> dict:
    result = bt_fy26_seeded_rapid_result(run_id)
    ensure_writable_dir(data_path('ai_financial_reports', 'rapid_runs'))
    atomic_write_json(data_path('ai_financial_reports', 'rapid_runs', run_id + '.json'), result)
    return result
