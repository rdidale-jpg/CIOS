"""BT FY26 governed ESEF/iXBRL ingestion for Flora's structured route."""
from __future__ import annotations
import hashlib,json,os,shutil,tempfile,time,zipfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
import xml.etree.ElementTree as ET
from cios.applications.flora.storage import data_path, atomic_write_json
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.live.source_registry import canonical_enterprise_id

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config/flora/structured_sources/bt-group-plc-fy26.json"
if not CONFIG_PATH.exists():
    CONFIG_PATH = Path(__file__).resolve().parents[4] / "config/flora/structured_sources/bt-group-plc-fy26.json"
IX_NS="{http://www.xbrl.org/2013/inlineXBRL}"; XBRLI_NS="{http://www.xbrl.org/2003/instance}"; XBRLDI_NS="{http://xbrl.org/2006/xbrldi}"
class OffHostRedirect(Exception): pass
class StructuredIngestionError(Exception):
    def __init__(self, message: str, code: str = "unexpected_runtime_error", stage: str = "unexpected runtime error"):
        super().__init__(message); self.code=code; self.stage=stage
class _NoOffHostRedirect(HTTPRedirectHandler):
    def __init__(self, approved:set[str]): self.approved=approved
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlparse(newurl).scheme != 'https' or urlparse(newurl).hostname not in self.approved: raise StructuredIngestionError(f'off-host redirect rejected: {newurl}', 'redirect_host_rejected', 'official filing retrieval')
        return super().redirect_request(req, fp, code, msg, headers, newurl)
@dataclass(frozen=True)
class RetrievedPackage:
    path:Path; sha256:str; final_url:str; status_code:int; content_type:str|None; size:int

def source_config()->dict[str,Any]:
    path=Path(os.getenv('FLORA_STRUCTURED_SOURCE_CONFIG') or CONFIG_PATH)
    if not path.exists(): raise StructuredIngestionError(f'structured source configuration missing: {path}', 'source_configuration_missing', 'governed source configuration')
    cfg=json.loads(path.read_text())
    if cfg.get('enterprise_id')!='bt-group-plc': raise StructuredIngestionError('BT governed source not selected for canonical enterprise', 'enterprise_identity_mismatch', 'governed source configuration')
    if cfg.get('source_kind')!='official_issuer_esef' or cfg.get('scope')!='group_consolidated': raise StructuredIngestionError('BT governed structured source not selected', 'source_configuration_not_selected', 'governed source configuration')
    if cfg.get('reporting_period')!='FY26' or cfg.get('period_start')!='2025-04-01' or cfg.get('period_end')!='2026-03-31': raise StructuredIngestionError('BT governed source period does not match FY26', 'reporting_period_mismatch', 'governed source configuration')
    if not cfg.get('artifact_url'): raise StructuredIngestionError('structured artifact URL missing', 'artifact_url_missing', 'governed source configuration')
    return cfg
def retrieve_package(cfg:dict[str,Any])->RetrievedPackage:
    url=cfg['artifact_url']; parsed=urlparse(url); approved=set(cfg.get('approved_hosts') or ())
    if parsed.scheme!='https' or parsed.hostname not in approved: raise StructuredIngestionError('artifact URL is not approved HTTPS host', 'host_not_allowed', 'official filing retrieval')
    tmp=Path(tempfile.mkdtemp(prefix='flora-bt-esef-'))/'filing.zip'; opener=build_opener(_NoOffHostRedirect(approved)); last=None
    for _ in range(3):
        h=hashlib.sha256(); size=0
        try:
            with opener.open(Request(url,headers={'User-Agent':'Flora structured financial ingestion/1.0'}),timeout=30) as r, tmp.open('wb') as out:
                content_type = r.headers.get('content-type')
                if content_type and 'zip' not in content_type.lower() and 'octet-stream' not in content_type.lower(): raise StructuredIngestionError(f'content type rejected: {content_type}', 'content_type_rejected', 'official filing retrieval')
                content_length = int(r.headers.get('content-length') or 0)
                while True:
                    chunk=r.read(1024*1024)
                    if not chunk: break
                    size+=len(chunk)
                    if size>int(cfg['compressed_size_limit_bytes']): raise StructuredIngestionError('compressed package size limit exceeded', 'compressed_package_too_large', 'official filing retrieval')
                    h.update(chunk); out.write(chunk)
                if content_length and size != content_length: raise StructuredIngestionError('download incomplete', 'download_incomplete', 'official filing retrieval')
                return RetrievedPackage(tmp,h.hexdigest(),r.geturl(),getattr(r,'status',200),r.headers.get('content-type'),size)
        except HTTPError as exc:
            code='http_403' if exc.code==403 else ('http_404' if exc.code==404 else 'http_error')
            last=StructuredIngestionError(f'HTTP {exc.code}', code, 'official filing retrieval'); time.sleep(.2)
        except URLError as exc:
            reason=str(getattr(exc,'reason',exc)).lower(); code='http_403' if '403' in reason else ('dns_failure' if 'name or service' in reason or 'nodename' in reason else ('tls_failure' if 'ssl' in reason or 'certificate' in reason else 'http_error'))
            last=StructuredIngestionError(str(exc), code, 'official filing retrieval'); time.sleep(.2)
        except Exception as exc: last=exc; time.sleep(.2)
    
    msg=str(last); code=getattr(last,'code',None) or ('download_timeout' if 'timed out' in msg.lower() else 'http_error')
    raise StructuredIngestionError(f'structured source retrieval failed: {last}', code, 'official filing retrieval')
def validate_archive(path:Path,cfg:dict[str,Any])->list[zipfile.ZipInfo]:
    infos=[]; total=0
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            parts=Path(info.filename.replace('\\','/')).parts
            if info.filename.startswith('/') or '..' in parts: raise StructuredIngestionError('ZIP-slip entry rejected', 'unsafe_archive', 'structured package validation')
            total+=info.file_size; infos.append(info)
            if total>int(cfg['expanded_size_limit_bytes']): raise StructuredIngestionError('expanded archive size limit exceeded', 'structured_package_invalid', 'structured package validation')
            if len(infos)>int(cfg['entry_count_limit']): raise StructuredIngestionError('archive entry count limit exceeded', 'structured_package_invalid', 'structured package validation')
    return infos
def _contexts(root):
    out={}
    for c in root.iter(XBRLI_NS+'context'):
        cid=c.attrib.get('id'); ident=c.find(f'.//{XBRLI_NS}identifier'); s=c.find(f'.//{XBRLI_NS}startDate'); e=c.find(f'.//{XBRLI_NS}endDate'); inst=c.find(f'.//{XBRLI_NS}instant')
        dims=[ET.tostring(d,encoding='unicode') for d in c.iter() if d.tag in {XBRLDI_NS+'explicitMember',XBRLDI_NS+'typedMember'}]
        if cid: out[cid]={'context_id':cid,'entity_identifier':(ident.text or '').strip() if ident is not None else '', 'period_start':(s.text or '').strip() if s is not None else None, 'period_end':(e.text or '').strip() if e is not None else None, 'instant':(inst.text or '').strip() if inst is not None else None, 'dimensions':dims, 'scope':'group_consolidated' if not dims else 'dimensioned'}
    return out
def extract_candidates(zip_path:Path,cfg:dict[str,Any],receipt:RetrievedPackage):
    
    try: validate_archive(zip_path,cfg)
    except zipfile.BadZipFile as exc: raise StructuredIngestionError(f'invalid ZIP package: {exc}', 'invalid_zip', 'structured package validation') from exc
    candidates=[]; quarantine=[]; required=cfg['required_metrics']
    with zipfile.ZipFile(zip_path) as z:
        docs=[n for n in z.namelist() if n.endswith(('.xhtml','.html'))]
        if not docs: raise StructuredIngestionError('no inline XBRL document in package', 'structured_package_invalid', 'structured package validation')
        root=ET.fromstring(z.read(docs[0]))
    contexts=_contexts(root)
    for el in root.iter():
        qn=el.attrib.get('name') or ''
        if el.tag!=IX_NS+'nonFraction' or qn not in required: continue
        ctx=contexts.get(el.attrib.get('contextRef','')); reason=None
        if not ctx: reason='missing_context'
        elif ctx['entity_identifier']!=cfg['lei']: reason='wrong_entity_identifier'
        elif ctx['period_start']!=cfg['period_start'] or ctx['period_end']!=cfg['period_end']: reason='wrong_period_or_comparator'
        elif ctx['instant']: reason='instant_context_for_duration_metric'
        elif ctx['dimensions']: reason='unsupported_dimension_or_segment'
        if reason: quarantine.append({'qname':qn,'context_ref':el.attrib.get('contextRef'),'reason':reason}); continue
        reported=Decimal(''.join(el.itertext()).strip().replace(',','')); metric=required[qn]
        candidates.append({'metric_id':metric,'qname':qn,'context':ctx,'unit_ref':el.attrib.get('unitRef'),'decimals':el.attrib.get('decimals'),'precision':el.attrib.get('precision'),'reported_amount':str(reported),'reported_scale':'millions','normalised_amount':str(reported*Decimal(1000000)),'source_locator':f"{receipt.final_url}#{docs[0]}#{qn}:{ctx['context_id']}"})
    return candidates, quarantine
def _statement(metric, amount):
    labels={'revenue':'revenue','operating_profit':'operating profit','profit_before_tax':'profit before tax'}
    return f"BT Group reported FY26 statutory {labels[metric]} of £{Decimal(amount):,}m."
def _snapshot():
    svc=ObservationMemoryService(); ent=canonical_enterprise_id('bt-group-plc') or 'bt-group-plc'; model=svc.models.get(ent); obs=svc.observations.list()
    return {'canonical_enterprise_id':ent,'observations':len(obs),'attributes':len(model.attributes),'active_observation_count':len(obs),'active_enterprise_model_attribute_count':len(model.attributes),'state_existed_before_run':bool(obs or model.attributes)}
def _reload_ok(obs_ids, attrs):
    svc=ObservationMemoryService(); model=svc.models.get('bt-group-plc')
    return all(svc.observations.get(o) for o in obs_ids) and all(a in model.attributes for a in attrs)
def _diagnostic(run_id,cfg,exc,receipt=None,candidate_count=0,canonical_count=0,adapter=False):
    code=getattr(exc,'code','unexpected_runtime_error'); stage=getattr(exc,'stage','unexpected runtime error')
    url=(cfg or {}).get('artifact_url',''); parsed=urlparse(url) if url else None
    return {'support_reference':'FI-'+run_id.removeprefix('fi-'),'enterprise_id':(cfg or {}).get('enterprise_id','bt-group-plc'),'reporting_period':(cfg or {}).get('reporting_period','FY26'),'execution_mode':'structured_standard_financials','source_configuration_status':'loaded' if cfg else 'missing','source_configuration_key':'bt-group-plc-fy26','source_kind':(cfg or {}).get('source_kind'),'artifact_host':parsed.hostname if parsed else None,'artifact_url':url or None,'artifact_resolution_status':'resolved' if url else 'missing','request_attempted': bool(receipt) or code not in {'source_configuration_missing','enterprise_identity_mismatch','reporting_period_mismatch','artifact_url_missing','host_not_allowed'},'http_status':getattr(receipt,'status_code',None),'redirect_chain':[],'final_host':urlparse(receipt.final_url).hostname if receipt else None,'content_type':getattr(receipt,'content_type',None),'reported_content_length':None,'bytes_downloaded':getattr(receipt,'size',0) if receipt else 0,'compressed_size_limit':int((cfg or {}).get('compressed_size_limit_bytes',0) or 0),'download_result':'succeeded' if receipt else 'failed','package_sha256':getattr(receipt,'sha256',None),'archive_validation_result':'passed' if adapter else ('not_attempted' if not receipt else 'failed'),'adapter_handoff_attempted':adapter,'adapter_result':'not_attempted' if not adapter else ('completed' if canonical_count else 'failed'),'candidate_fact_count':candidate_count,'canonical_fact_count':canonical_count,'failure_code':code,'failure_stage':stage,'safe_failure_message':'Structured financial source unavailable','timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'deployment_revision':os.getenv('RENDER_GIT_COMMIT') or os.getenv('RENDER_COMMIT') or os.getenv('GIT_COMMIT')}
def _persist_diag(run_id,diag): atomic_write_json(data_path('ai_financial_reports','diagnostics',f'{run_id}.json'),diag); print('Flora structured diagnostic '+json.dumps(diag,sort_keys=True),flush=True)
def _failure(run_id,before,exc,cfg=None,receipt=None):
    diag=_diagnostic(run_id,cfg,exc,receipt); _persist_diag(run_id,diag)
    after=_snapshot(); run={'run_id':run_id,'created_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'structured_source_unavailable','failure_category':'structured_source_unavailable','support_reference':'FI-'+run_id.removeprefix('fi-'),'failure_code':diag['failure_code'],'failure_stage':diag['failure_stage'],'user_message':'Structured financial source unavailable','user_message_display':'Structured financial source unavailable Support reference: FI-'+run_id.removeprefix('fi-')+' Failure stage: '+diag['failure_stage'],'structured_diagnostics':[diag],'provider_diagnostics':[diag],'exceptions':[{'exception_type':type(exc).__name__,'failure_stage':diag['failure_stage'],'failure_code':diag['failure_code'],'support_reference':'FI-'+run_id.removeprefix('fi-'),'user_message':'Structured financial source unavailable','rejection_reason':str(exc)}],'trusted_state_before':before,'trusted_state_after':after,'trusted_twin_changed':before.get('active_observation_count')!=after.get('active_observation_count') or before.get('active_enterprise_model_attribute_count')!=after.get('active_enterprise_model_attribute_count'),'ephemeral_state_absent_before_run':not before.get('state_existed_before_run'),'openai_calls_made':0,'ai_calls_made':0,'pdf_fallback_calls_made':0,'extraction_mode':'structured_standard_financials','provider_status':'not_executed','openai_invoked':False,'prohibited_path_counters':{'provider_calls':0,'pdf_section_selector_calls':0,'pdf_candidate_extractor_calls':0,'pdf_packet_calls':0},'usage':{'openai_calls':0},'collection':{'retrieved':False,'error':str(exc)},'run_status':{'structured_source':'unavailable','ai_calls_made':0,'pdf_fallback_calls_made':0}}
    atomic_write_json(data_path('ai_financial_reports','runs',f'{run_id}.json'),run); return run
def ingest_bt_fy26(run_id:str)->dict[str,Any]:
    cfg=None; before=_snapshot(); tmpdir=None; receipt=None
    try:
        cfg=source_config(); receipt=retrieve_package(cfg); tmpdir=receipt.path.parent; candidates,quarantine=extract_candidates(receipt.path,cfg,receipt); by={c['metric_id']:c for c in candidates}
        for m in ('revenue','operating_profit','profit_before_tax'):
            if m not in by: raise StructuredIngestionError(f'required standard fact missing: {m}', 'no_supported_facts', 'structured fact validation')
        svc=ObservationMemoryService(); results=[]; evidence_ids=[]; observation_ids=[]; attrs=[]
        for c in [by['revenue'],by['operating_profit'],by['profit_before_tax']]:
            eid='EV-BT-FY26-'+c['metric_id'].upper().replace('_','-'); attr=f"financial_performance.metrics.{c['metric_id']}.FY26.actual"; stmt=_statement(c['metric_id'],c['reported_amount'])
            evidence={'evidence_id':eid,'enterprise_id':'bt-group-plc','canonical_enterprise_id':'bt-group-plc','legal_name':cfg['legal_name'],'company_number':cfg['company_number'],'lei':cfg['lei'],'filing_title':'BT Group plc Annual Report 2026 ESEF filing','reporting_period':'FY26','source_class':cfg['source_kind'],'discovery_url':cfg['discovery_url'],'artifact_url':cfg['artifact_url'],'source_url':cfg['artifact_url'],'enterprise_scope':'group_consolidated','viewer_url':cfg['viewer_url'],'package_sha256':receipt.sha256,'qname':c['qname'],'context':c['context'],'unit_ref':c['unit_ref'],'currency':'GBP','reported_scale':c['reported_scale'],'decimals':c['decimals'],'precision':c['precision'],'reported_amount':c['reported_amount'],'display_value':f"£{Decimal(c['reported_amount']):,}m",'metric_identity':c['metric_id'],'metric_label':c['metric_id'].replace('_',' '),'normalised_amount':c['normalised_amount'],'original_display_value':f"£{Decimal(c['reported_amount']):,}m",'adapter_name':'StructuredFinancialAdapter','adapter_version':'structured-source-first-v1','collection_timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'acceptance_result':'accepted','source_locator':c['source_locator'],'commercial_condition':'financial_metric_reported','cleaned_observation':stmt,'affected_attribute':attr,'confidence':100,'period':'FY26','state':'actual','accounting_basis':'statutory','evidence_freshness':'current','observation_date':'2026-03-31','publication_date':'2026-05-22','page_range':'structured filing'}
            report=svc.process_evidence(evidence)
            if len(report.results)!=1 or report.rejected_claims: raise StructuredIngestionError(f"canonical validation failed for {c['metric_id']}: {report.rejected_claims}", 'adapter_handoff_failed', 'structured fact validation')
            result=report.results[0]; results.append(result.__dict__); evidence_ids.append(eid); observation_ids.append(result.observation_id); attrs.append(attr)
        after=_snapshot(); status={'structured_source':'available','ai_calls_made':0,'pdf_fallback_calls_made':0,'canonical_facts_accepted':3,'structured_evidence_records':3,'financial_observations':3,'enterprise_model_attributes':3,'trusted_twin_changed':before!=after,'persistent_state_verified_after_restart':_reload_ok(observation_ids,attrs)}
        diag=_diagnostic(run_id,cfg,StructuredIngestionError('', 'none', 'completed'),receipt,len(candidates),3,True); _persist_diag(run_id,diag)
        run={'run_id':run_id,'status':'completed','support_reference':'FI-'+run_id.removeprefix('fi-'),'structured_diagnostics':[diag],'provider_diagnostics':[diag],'collection':{'retrieved':True,'sha256':receipt.sha256,'final_url':receipt.final_url,'document_size':receipt.size},'claims':candidates,'candidate_exceptions':quarantine,'applied_results':results,'evidence_ids':evidence_ids,'observation_ids':observation_ids,'enterprise_attributes_changed':attrs,'run_status':status,'trusted_state_before':before,'trusted_state_after':after,'trusted_twin_changed':status['trusted_twin_changed'],'openai_calls_made':0,'ai_calls_made':0,'pdf_fallback_calls_made':0,'extraction_mode':'structured_standard_financials','provider_status':'not_executed','openai_invoked':False,'prohibited_path_counters':{'provider_calls':0,'pdf_section_selector_calls':0,'pdf_candidate_extractor_calls':0,'pdf_packet_calls':0}}
        atomic_write_json(data_path('ai_financial_reports','runs',f'{run_id}.json'),run); return run
    except Exception as exc: return _failure(run_id,before,exc,cfg,receipt)
    finally:
        if tmpdir and tmpdir.name.startswith('flora-bt-esef-'): shutil.rmtree(tmpdir,ignore_errors=True)
