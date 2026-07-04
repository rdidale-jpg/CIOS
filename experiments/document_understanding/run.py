from __future__ import annotations
import argparse, hashlib, json, uuid
from pathlib import Path
from .providers import OpenAIDirectPDFProvider, AnthropicDirectPDFProvider, LayoutOpenAIProvider
from .schema import ExperimentDocument, FoundationFactSet, PageRange, now_iso
PROVIDERS={'openai-direct':OpenAIDirectPDFProvider,'anthropic-direct':AnthropicDirectPDFProvider,'layout-openai':LayoutOpenAIProvider}
def parse_pages(s):
    if not s: return None
    out=[]
    for part in s.split(','):
        a,*b=part.split('-'); out.append(PageRange(start=int(a),end=int(b[0] if b else a)))
    return out
def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('--enterprise',required=True); p.add_argument('--document',required=True); p.add_argument('--route',required=True,choices=[*PROVIDERS,'flora-baseline']); p.add_argument('--pages'); p.add_argument('--pdf'); p.add_argument('--output-dir',default='.document_understanding/runs')
    a=p.parse_args(argv); Path(a.output_dir).mkdir(parents=True,exist_ok=True)
    if a.route=='flora-baseline':
        t=now_iso(); run={'run_id':str(uuid.uuid4()),'route':'flora-baseline','provider':'flora','model':'deterministic-regex','status':'completed','started_at':t,'completed_at':t,'latency_seconds':0,'facts':[],'provider_errors':[]}
    else:
        if a.pdf and Path(a.pdf).is_file(): data=Path(a.pdf).read_bytes(); checksum=hashlib.sha256(data).hexdigest(); page_count=1
        else: checksum='unavailable'; page_count=1
        doc=ExperimentDocument(document_id=a.document,enterprise_id=a.enterprise,title=a.document,source_url='',retrieval_timestamp=now_iso(),checksum=checksum,media_type='application/pdf',page_count=page_count,local_path=a.pdf)
        run=PROVIDERS[a.route]().extract_facts(doc,FoundationFactSet,parse_pages(a.pages)).model_dump(mode='json')
    path=Path(a.output_dir)/f"{run['run_id']}.json"; path.write_text(json.dumps(run,indent=2)); print(path)
if __name__=='__main__': main()
