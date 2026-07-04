from __future__ import annotations
import base64, json, os, time, uuid
from pathlib import Path
from .instructions import EXTRACTION_INSTRUCTIONS
from .schema import ExperimentDocument, ExtractionRun, FoundationFactSet, PageRange, now_iso
RAW_DIR=Path('.document_understanding/raw_responses')
def _not_executed(route, provider, model, error):
    t=now_iso(); return ExtractionRun(run_id=str(uuid.uuid4()),route=route,provider=provider,model=model,status='not_executed',started_at=t,completed_at=t,latency_seconds=0,provider_errors=[error])
class OpenAIDirectPDFProvider:
    def __init__(self, model='gpt-5.5', max_retries=2): self.model=model; self.max_retries=max_retries
    def extract_facts(self, document:ExperimentDocument, schema:type[FoundationFactSet]=FoundationFactSet, page_ranges:list[PageRange]|None=None)->ExtractionRun:
        if not os.getenv('OPENAI_API_KEY'): return _not_executed('openai-direct','openai',self.model,'OPENAI_API_KEY is not configured')
        if not document.local_path or not Path(document.local_path).is_file(): return _not_executed('openai-direct','openai',self.model,'local PDF is unavailable')
        started=time.time(); start_iso=now_iso(); RAW_DIR.mkdir(parents=True,exist_ok=True)
        try:
            from openai import OpenAI
            client=OpenAI(); data=base64.b64encode(Path(document.local_path).read_bytes()).decode('ascii')
            resp=client.responses.create(model=self.model,input=[{'role':'user','content':[{'type':'input_text','text':EXTRACTION_INSTRUCTIONS},{'type':'input_file','filename':Path(document.local_path).name,'file_data':f'data:application/pdf;base64,{data}'}]}],text={'format':{'type':'json_schema','name':'foundation_fact_set','schema':schema.model_json_schema(),'strict':True}})
            raw=resp.model_dump(mode='json') if hasattr(resp,'model_dump') else resp
            raw_path=RAW_DIR/f"{document.document_id}-openai-{uuid.uuid4().hex}.json"; raw_path.write_text(json.dumps(raw,indent=2,default=str))
            output=getattr(resp,'output_text','') or raw.get('output_text','')
            parsed=schema.model_validate_json(output) if output else FoundationFactSet()
            usage=(getattr(resp,'usage',None).model_dump() if getattr(resp,'usage',None) and hasattr(getattr(resp,'usage'),'model_dump') else (raw.get('usage') or {}))
            return ExtractionRun(run_id=str(uuid.uuid4()),route='openai-direct',provider='openai',model=self.model,model_version=self.model,status='completed',request_id=getattr(resp,'id',None) or raw.get('id'),started_at=start_iso,completed_at=now_iso(),latency_seconds=time.time()-started,usage=usage,raw_response_location=str(raw_path),facts=parsed.facts)
        except Exception as exc:
            return ExtractionRun(run_id=str(uuid.uuid4()),route='openai-direct',provider='openai',model=self.model,model_version=self.model,status='failed',started_at=start_iso,completed_at=now_iso(),latency_seconds=time.time()-started,provider_errors=[type(exc).__name__])
class AnthropicDirectPDFProvider:
    def __init__(self, model='claude-sonnet-4-5'): self.model=model
    def extract_facts(self, document, schema=FoundationFactSet, page_ranges=None):
        if not os.getenv('ANTHROPIC_API_KEY'): return _not_executed('anthropic-direct','anthropic',self.model,'ANTHROPIC_API_KEY is not configured')
        return _not_executed('anthropic-direct','anthropic',self.model,'Adapter boundary retained; execution requires Anthropic SDK wiring in a credentialed environment')
class LayoutOpenAIProvider:
    def __init__(self, model='gpt-5.5'): self.model=model
    def extract_facts(self, document, schema=FoundationFactSet, page_ranges=None):
        if not (os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or (os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT') and os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY'))):
            return _not_executed('layout-openai','layout+openai',self.model,'No Google Document AI or Azure Document Intelligence credentials configured')
        return _not_executed('layout-openai','layout+openai',self.model,'Provider boundary implemented; select one layout SDK before execution')
