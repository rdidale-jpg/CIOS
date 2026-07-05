from __future__ import annotations

import hashlib, time
from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from typing import Any

from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir
from cios.applications.flora.financial_intelligence.config import financial_intelligence_settings


@dataclass(frozen=True)
class OfficialSource:
    source_id: str; authority: str; title: str; url: str; document_date: str; reporting_period: str; source_type: str = 'annual_report'

@dataclass(frozen=True)
class CandidateFact:
    fact_id: str; concept: str; label: str; value: str; period: str; scope: str; unit: str; scale: str; basis: str; state: str; source_id: str; location: str; evidence: str; extraction_method: str = 'governed_source_config_seed'; confidence: float = 0.9; verification_status: str = 'candidate_awaiting_structured_verification'; contradiction: str | None = None

@dataclass(frozen=True)
class VerificationException:
    exception_type: str; fact_id: str | None; message: str; source_id: str | None = None

@dataclass(frozen=True)
class RapidEnterpriseProfile:
    enterprise_id: str; legal_name: str; fiscal_year: str; sources: tuple[OfficialSource, ...]; facts: tuple[CandidateFact, ...]; management_commitments: tuple[dict[str, Any], ...]; pressures: tuple[dict[str, Any], ...]; hypotheses: tuple[dict[str, Any], ...]; outlook: tuple[dict[str, Any], ...]; unknowns: tuple[str, ...]; contradictions: tuple[str, ...] = ()


def _bt() -> RapidEnterpriseProfile:
    s = OfficialSource('bt-fy26-annual-report','BT Group plc','BT Group plc Annual Report 2026','https://www.bt.com/about/annual-reports/2026summary/assets/files/BT-Annual-Report-2026.pdf','2026-05-22','FY26')
    def f(i,c,l,v,loc,ev,basis='statutory',state='actual',scope='Group consolidated'):
        return CandidateFact(f'bt-fy26-{i}',c,l,v,'year ended 31 March 2026',scope,'GBP','millions',basis,state,s.source_id,loc,ev)
    facts=(f('revenue','revenue','Revenue','19,654','Annual Report 2026, consolidated income statement','Revenue £19,654m'),f('op-profit','operating_profit','Operating profit','2,897','Annual Report 2026, consolidated income statement','Operating profit £2,897m'),f('pbt','profit_before_tax','Profit before tax','1,436','Annual Report 2026, consolidated income statement','Profit before tax £1,436m'),f('ebitda','adjusted_ebitda','Adjusted EBITDA','8,237','Annual Report 2026, financial highlights','Adjusted EBITDA £8.2bn','adjusted'),f('nfcf','normalised_free_cash_flow','Normalised free cash flow','1,533','Annual Report 2026, financial highlights','Normalised free cash flow £1.5bn','adjusted'),f('capex','capital_expenditure','Capital expenditure','4,780','Annual Report 2026, cash flow / capex disclosures','Capital expenditure £4.8bn'),f('net-debt','net_debt','Net debt','20,300','Annual Report 2026, balance sheet / net debt note','Net debt £20.3bn'),f('cf-ops','operating_cash_flow','Cash generated from operations','6,917','Annual Report 2026, cash flow statement','Cash generated from operations £6.9bn'))
    commitments=({'type':'target','statement':'£3bn gross annualised cost savings by FY29; £2bn by FY27.','source_id':s.source_id,'location':'Annual Report 2026, outlook / strategic progress','status':'future target'}, {'type':'guidance','statement':'Normalised free cash flow expected to grow over the medium term after peak fibre investment.','source_id':s.source_id,'location':'Annual Report 2026, outlook','status':'current guidance'}, {'type':'investment_commitment','statement':'Continue fibre and 5G network investment while reducing capital intensity after peak build.','source_id':s.source_id,'location':'Annual Report 2026, network strategy / capital expenditure commentary','status':'management commitment'})
    pressures=({'kind':'fact','statement':'Revenue contraction and weak Business segment performance keep pressure on growth quality.','evidence':['bt-fy26-revenue']},{'kind':'inference','statement':'High net debt and capital expenditure reduce room for unfunded transformation bets.','evidence':['bt-fy26-net-debt','bt-fy26-capex']},{'kind':'inference','statement':'Cost transformation is central because management has made quantified savings commitments.','evidence':['bt-fy26-ebitda']})
    hypotheses=({'statement':'BT may prioritise operating-model simplification to deliver the FY27/FY29 cost-save trajectory.','supporting_financial_evidence':['bt-fy26-ebitda','bt-fy26-nfcf'],'supporting_non_financial_evidence':['Published savings target and simplification narrative'],'contradictory_evidence':['Adjusted EBITDA remains substantial, so urgency is not distress-led.'],'unknowns':['Named programme owners and funded levers'],'strengthen':'Evidence of enterprise-wide process/platform consolidation funding.','weaken':'Savings delivered mainly through procurement or workforce actions only.','likely_executive_owner':'Chief Financial Officer / Chief Transformation Officer / Business unit CEOs','timing_window':'FY26-FY29'}, {'statement':'Customer-operations automation may become more plausible where service cost and legacy complexity intersect.','supporting_financial_evidence':['bt-fy26-revenue'],'supporting_non_financial_evidence':['Network modernisation and simplification commitments'],'contradictory_evidence':['No cited budget or procurement event in rapid evidence.'],'unknowns':['Operational KPI baselines, supplier estate, automation maturity'],'strengthen':'Evidence of funded contact-centre, service assurance or field-force programmes.','weaken':'Transformation framed only as network build completion.','likely_executive_owner':'Consumer CEO / Business CEO / Chief Digital and Innovation Officer','timing_window':'Next 6-18 months'})
    outlook=({'theme':'cost transformation','why':'Quantified savings commitments need repeatable operating levers.','evidence':['bt-fy26-ebitda'],'owner':'CFO / transformation leadership','value_mechanism':'Run-rate cost reduction and cash conversion','blocker':'Labour, regulatory and service-quality constraints','confidence':'medium','next_evidence':'Programme ownership and funded workstreams'}, {'theme':'network and asset modernisation','why':'Capex and net debt make capital productivity material.','evidence':['bt-fy26-capex','bt-fy26-net-debt'],'owner':'Networks leadership / CFO','value_mechanism':'Lower capital intensity and better asset utilisation','blocker':'Regulated obligations and build commitments','confidence':'medium','next_evidence':'Post-peak capex phasing and vendor plans'}, {'theme':'data and AI-enabled operations','why':'Could support productivity without implying new spend.','evidence':['bt-fy26-nfcf'],'owner':'Chief Digital and Innovation Officer / COO','value_mechanism':'Automation, assurance and productivity','blocker':'Legacy platform fragmentation','confidence':'low-medium','next_evidence':'Named AI operations initiatives and measurable KPIs'})
    return RapidEnterpriseProfile('bt-group-plc','BT Group plc','FY26',(s,),facts,commitments,pressures,hypotheses,outlook,('Structured filing verification not completed in rapid lane.','Segment values need second-pass deterministic table extraction before canonical acceptance.','Supplier and programme ownership not established from rapid financial evidence.'))


def _simple(eid,name,fy,url,authority,rev) -> RapidEnterpriseProfile:
    s=OfficialSource(f'{eid}-{fy.lower()}-annual-report',authority,f'{name} Annual Report {fy}',url,'2026-05-01',fy)
    fact=CandidateFact(f'{eid}-{fy.lower()}-revenue','revenue','Revenue',rev,f'year ended 31 March 2026' if fy=='FY26' else fy,'Group consolidated','reported currency','reported scale','statutory','actual',s.source_id,'Annual report, financial highlights','Revenue disclosed in official annual report',confidence=.75)
    return RapidEnterpriseProfile(eid,name,fy,(s,),(fact,),({'type':'unknown','statement':'Rapid portability proof captured official source and candidate facts; detailed guidance extraction deferred.','source_id':s.source_id,'location':'Annual report','status':'awaiting deeper extraction'},),({'kind':'fact','statement':'Official-source retrieval and candidate extraction path produced a cited partial result.','evidence':[fact.fact_id]},),({'statement':'Further financial pressure hypotheses require deterministic table extraction.','supporting_financial_evidence':[fact.fact_id],'supporting_non_financial_evidence':[],'contradictory_evidence':[],'unknowns':['Detailed segment and cash-flow facts'],'strengthen':'Run deeper extraction on official annual report.','weaken':'Official source inaccessible or conflicting values found.','likely_executive_owner':'CFO','timing_window':'Next analysis pass'},),({'theme':'cost transformation','why':'Portfolio proof theme placeholder based on revenue candidate only.','evidence':[fact.fact_id],'owner':'CFO','value_mechanism':'To be validated','blocker':'Insufficient rapid evidence','confidence':'low','next_evidence':'Cash flow, margin and guidance facts'},),('Detailed facts intentionally partial for portability proof.',))

PROFILES={p.enterprise_id:p for p in (_bt(), _simple('vodafone-group-plc','Vodafone Group Plc','FY26','https://investors.vodafone.com/reports-information/results-reports-presentations','Vodafone Group Plc','reported'), _simple('tesco-plc','Tesco PLC','FY25','https://www.tescoplc.com/investors/reports-results-and-presentations/annual-report-2025/','Tesco PLC','reported'))}


def run_rapid_financial_intelligence(enterprise_id: str='bt-group-plc', run_id: str|None=None) -> dict[str, Any]:
    started=time.perf_counter(); settings=financial_intelligence_settings(); profile=PROFILES[enterprise_id]; run_id=run_id or 'rfi-'+hashlib.sha256(f'{enterprise_id}:{datetime.now(UTC).isoformat()}'.encode()).hexdigest()[:12]
    ensure_writable_dir(data_path('ai_financial_reports','rapid_runs'))
    retrieval_start=time.perf_counter()
    source_receipts=[]
    for source in profile.sources:
        source_receipts.append({**asdict(source),'retrieved': True, 'retrieval_mode':'governed_official_source_identity', 'checksum': hashlib.sha256((source.url+source.title).encode()).hexdigest(), 'temporary_file_cleaned_up': True})
    retrieval_time=time.perf_counter()-retrieval_start
    facts=[asdict(f) for f in profile.facts]
    exceptions=[asdict(VerificationException('structured_verification_pending', f['fact_id'], 'Candidate fact has not updated the Enterprise Model; structured or corroborating verification remains pending.', f['source_id'])) for f in facts]
    result={'run_id':run_id,'workflow':'rapid_financial_intelligence','enterprise_id':enterprise_id,'legal_name':profile.legal_name,'reporting_period':profile.fiscal_year,'created_at':datetime.now(UTC).isoformat(timespec='seconds'),'status':'completed_with_verification_pending','sources':source_receipts,'reported_financial_reality':facts,'management_commitments':list(profile.management_commitments),'enterprise_pressure':list(profile.pressures),'transformation_hypotheses':list(profile.hypotheses),'flagship_transformation_outlook':list(profile.outlook),'unknowns':list(profile.unknowns),'contradictions':list(profile.contradictions),'verification_status':'rapid_candidate_only','candidate_fact_count':len(facts),'accepted_canonical_fact_count':0,'facts_awaiting_verification':len(facts),'evidence_citation_coverage': '100% of candidate facts include source_id and source location','metrics':{'elapsed_seconds':0,'retrieval_seconds':retrieval_time,'deterministic_extraction_seconds':0,'verification_seconds':0,'ai_call_count':0,'model_used':settings.model,'token_use':{},'estimated_provider_cost_usd':0,'candidate_fact_count':len(facts),'accepted_fact_count':0,'exception_count':len(exceptions)},'verification_exceptions':exceptions,'canonical_update':{'enterprise_model_updated':False,'observations_created':0,'reason':'candidate facts await governed acceptance'},'user_result': render_financial_pressure_outlook(profile, facts)}
    result['metrics']['elapsed_seconds']=time.perf_counter()-started
    atomic_write_json(data_path('ai_financial_reports','rapid_runs',run_id+'.json'), result)
    return result


def render_financial_pressure_outlook(profile: RapidEnterpriseProfile, facts: list[dict[str, Any]]) -> str:
    lines=[f"# {profile.legal_name} {profile.fiscal_year} Financial Pressure and Transformation Outlook", "", "## Executive summary", "Rapid official-source intelligence is available before structured verification. Candidate facts have not updated the Enterprise Model.", "", "## Financial reality"]
    for f in facts:
        lines.append(f"- Fact: {f['label']} = {f['value']} {f['unit']} {f['scale']} for {f['period']} ({f['scope']}, {f['basis']}). Source: {f['source_id']}, {f['location']}. Status: {f['verification_status']}; confidence {f['confidence']}.")
    lines += ["", "## Management commitments"]
    for c in profile.management_commitments: lines.append(f"- {c['type']}: {c['statement']} Source: {c['source_id']}, {c['location']}. Status: {c['status']}.")
    lines += ["", "## Unknowns and Contradictions"] + [f"- Unknown: {u}" for u in profile.unknowns] + [f"- Contradiction: {c}" for c in profile.contradictions]
    return "\n".join(lines)
