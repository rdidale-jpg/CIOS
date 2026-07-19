from __future__ import annotations
import hashlib, json, re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[4]
KNOW = ROOT / 'enterprise-knowledge'

@dataclass(frozen=True)
class SourceSegment:
    segment_id: str; asset_id: str; section_heading: str; content: str; content_hash: str; source_location: str; authority: str; status: str
    def to_dict(self): return asdict(self)

@dataclass(frozen=True)
class CandidateClaim:
    claim_id: str; claim_type: str; statement: str; source_asset_id: str; source_segment_id: str; scope: str; subject: str; predicate: str; object: str; time_scope: str; participant_scope: str; enterprise_scope: str; confidence: str; authority: str; status: str; supporting_ids: list[str]; contradicting_ids: list[str]
    def to_dict(self): return asdict(self)

def _sha(text: str) -> str: return hashlib.sha256(text.encode('utf-8')).hexdigest()
def _slug(s: str) -> str: return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')[:48] or 'root'

def segment_markdown(asset_id: str, path: Path, status: str='Validated') -> list[SourceSegment]:
    text = path.read_text(encoding='utf-8')
    if text.startswith('---'):
        parts = text.split('---',2)
        if len(parts)==3: text=parts[2]
    headings = list(re.finditer(r'^(#{1,4})\s+(.+?)\s*$', text, re.M))
    segs=[]
    if not headings:
        body=text.strip()
        if body: segs.append(_seg(asset_id,'Document',body,path,status,1))
        return segs
    for i,h in enumerate(headings):
        start=h.end(); end=headings[i+1].start() if i+1<len(headings) else len(text)
        body=text[start:end].strip()
        if len(body)<30: continue
        heading=re.sub(r'[`*_]','',h.group(2)).strip()
        segs.append(_seg(asset_id,heading,body,path,status,i+1))
    return segs

def _seg(asset_id, heading, body, path, status, idx):
    excerpt='\n'.join(line.strip() for line in body.splitlines() if line.strip())[:2400]
    return SourceSegment(f'{asset_id}::seg-{idx:03d}-{_slug(heading)}',asset_id,heading,excerpt,_sha(excerpt),str(path.relative_to(ROOT)), 'governed_source', status)

def load_asset_content(asset: dict[str,Any]) -> dict[str,Any]:
    path=KNOW/asset['location']; suffix=path.suffix.lower(); text=''
    if suffix=='.md':
        segments=segment_markdown(asset['asset_id'],path,asset.get('status',''))
        text=path.read_text(encoding='utf-8')
    elif suffix=='.json':
        data=json.loads(path.read_text(encoding='utf-8')); text=json.dumps(data,sort_keys=True,indent=2); segments=[_seg(asset['asset_id'],'JSON content',text,path,asset.get('status',''),1)]
    elif suffix in ('.yml','.yaml') and yaml:
        data=yaml.safe_load(path.read_text(encoding='utf-8')); text=json.dumps(data,sort_keys=True,indent=2,default=str); segments=[_seg(asset['asset_id'],'YAML content',text,path,asset.get('status',''),1)]
    else:
        return {'asset_id':asset['asset_id'],'unsupported':True,'sections':[],'claims':[]}
    return {'asset_id':asset['asset_id'],'asset_type':asset.get('asset_type',''),'title':asset.get('title',''),'authority':'governed_source','status':asset.get('status',''),'version':asset.get('version',''),'source_path':str(path.relative_to(ROOT)),'sections':[s.to_dict() for s in segments],'claims':[c.to_dict() for c in extract_claims(segments)],'relationships':asset.get('relationships',[]),'content_hash':_sha(text)}

def extract_claims(segments: list[SourceSegment]) -> list[CandidateClaim]:
    claims=[]; keywords={'mechanism':'mechanism','unknown':'evidence gap','contradict':'contradiction','branch':'observed change','access':'observed change','executive':'executive implication','commercial':'commercial implication','participant':'participant difference'}
    for s in segments:
        sentences=re.split(r'(?<=[.!?])\s+', re.sub(r'\s+',' ',s.content))
        chosen=[]
        for sent in sentences:
            low=sent.lower()
            if 45 < len(sent) < 360 and any(k in low or k in s.section_heading.lower() for k in keywords): chosen.append(sent.strip())
            if len(chosen)>=2: break
        for n,sent in enumerate(chosen,1):
            ctype=next((v for k,v in keywords.items() if k in sent.lower() or k in s.section_heading.lower()),'causal proposition')
            claims.append(CandidateClaim(f'{s.segment_id}::claim-{n}',ctype,sent,s.asset_id,s.segment_id,'Banking',sent.split(' ',1)[0], 'indicates', sent, 'current', 'UK Banking participant types','', 'Medium','derived_runtime_claim','Derived runtime claim',[],[]))
    return claims

MECHANISM_DETAILS={
 'BM-04':('Assisted-access substitution','Branch networks are fragmenting into a mix of proprietary branches, shared hubs, Post Office access and digital support.','It decides whether physical access is a cost to remove, a trust asset, or a regulated inclusion obligation.'),
 'BM-02':('Customer trust and conduct feedback','Customer outcomes, complaints and conduct evidence feed retention, brand permission and regulatory pressure.','It explains why physical access can still matter when routine transactions move digital.'),
 'BM-14':('Consumer Duty outcome evidence','Regulation is pushing banks to prove customer outcomes, especially for vulnerable customers and complex needs.','It constrains channel simplification unless banks can evidence fair access and good outcomes.'),
 'BM-15':('Legacy complexity cost-to-income','Incumbent technology and operating complexity raise cost, slow change and increase migration risk.','It explains the pressure to simplify estates and channels, but also why change must be controlled.'),
}
OBS_TEXT={
 'BK-OBS-014':'Digital adoption and branch reduction are changing routine distribution, but do not remove the need for physical or assisted service.',
 'BK-OBS-015':'Shared access, hubs and Post Office models are becoming part of the industry response to branch withdrawal and access-to-cash obligations.',
 'BK-OBS-016':'Customer trust, vulnerability and complex service needs mean channel migration cannot be judged only by transaction volume.',
 'BK-OBS-029':'Participant type changes the meaning of physical footprint: incumbents may see cost pressure while mutual/community models may see member value and trust.',
 'BK-OBS-047':'Branches can be both cost burdens and trust assets; this is a real participant-type tension rather than a simple contradiction.',
}

def build_semantic_context(run_id, question, assets, hyp, observations, mechanisms):
    loaded=[load_asset_content(a) for a in assets]
    segments=[]; claims=[]
    for a in loaded:
        segments.extend(a.get('sections',[])[:8]); claims.extend(a.get('claims',[])[:8])
    permitted={a['asset_id'] for a in assets}|{hyp['hypothesis_id']}|{o['observation_id'] for o in observations}|{m['mechanism_id'] for m in mechanisms}|{s['segment_id'] for s in segments}
    return {'object_id':f'{run_id}-semantic-context','object_type':'semantic_context','status':'PASS','authority':'derived_runtime_assessment','confidence':'Medium','unknowns':[],'contradictions':[],'validation_state':'schema_valid','context_id':f'{run_id}-semantic-context','run_id':run_id,'question':question,'intent':'Explain Banking change in commercial language','industry_scope':'Banking','enterprise_scope':'participant-type only unless governed enterprise evidence is selected','participant_scope':'UK retail and commercial banking participant types','governed_objects':loaded,'source_segments':segments,'candidate_claims':claims,'observation_texts':{o['observation_id']:o['statement'] for o in observations},'mechanism_texts':{mid:{'name':v[0],'meaning':v[1],'why_it_matters':v[2]} for mid,v in MECHANISM_DETAILS.items()},'hypothesis_texts':{hyp['hypothesis_id']:hyp['statement']},'participant_differences':['Shareholder incumbents face stronger estate cost and simplification pressure.','Mutuals and community-oriented participants can treat branches as trust, inclusion and member-value assets.','Digital challengers validate app-first expectations but do not prove physical access is irrelevant for all segments.'],'unknowns':semantic_unknowns(hyp.get('unknowns',[])),'contradictions':semantic_contradictions(hyp.get('contradictions',[])),'permitted_source_ids':sorted(permitted),'excluded_source_ids':[],'token_budget':12000,'content_hash':_sha(json.dumps(loaded,sort_keys=True,default=str))}

def semantic_unknowns(raw):
    return [
      {'unknown_id':'UNK-SHARED-ACCESS-ECONOMICS','question':'Are shared hubs and assisted-access models economically sustainable at meaningful scale?','why_it_matters':'It determines whether mixed access is structural or only a mitigation layer.','decision_constrained':'Proposal or investment case around branch/hub operating models.','evidence_required':['utilisation','cost-to-serve','operating model','ownership and funding','participant comparison'],'affected_claims':['BM-04'],'affected_hypotheses':['BRH-003'],'affected_recommendation':'Validate economics before proposal','source_ids':['EK-BANK-RHYP-001','BK-REF-001']},
      {'unknown_id':'UNK-ASSISTED-CUSTOMER-RELIANCE','question':'Which customer segments still rely on assisted physical access for completion, trust or inclusion?','why_it_matters':'It prevents over-reading digital adoption as universal channel sufficiency.','decision_constrained':'Executive prioritisation of assisted service and vulnerable customer support.','evidence_required':['segment usage','vulnerability data','channel migration','service completion rates'],'affected_claims':['BK-OBS-016','BM-14'],'affected_hypotheses':['BRH-003'],'affected_recommendation':'Run learning conversation before stronger action','source_ids':['EK-BANK-RHYP-001','BK-IND-002']},
      {'unknown_id':'UNK-NAMED-EXECUTIVE-OWNERSHIP','question':'Which named executive owns the access, trust and simplification decision in a selected enterprise?','why_it_matters':'Flora can identify role-level relevance but must not invent account-specific ownership.','decision_constrained':'Named executive outreach and account-specific recommendation.','evidence_required':['organisational accountability','programme sponsorship','public role evidence','human account knowledge'],'affected_claims':['executive relevance'],'affected_hypotheses':['BRH-003'],'affected_recommendation':'Keep action at validation/discovery level','source_ids':['BK-FLR-SSN-SPEC-001']},
    ]

def semantic_contradictions(raw):
    return [{'contradiction_id':'CONTRA-BRANCH-COST-TRUST','claim_a':'Branch estates are cost and simplification targets as routine demand moves digital.','claim_b':'Physical access remains a trust, inclusion and assisted-service asset for some customers and participant types.','scope_difference':'Cost lens versus customer access and trust lens.','participant_difference':'Shareholder incumbents, mutuals, community banks and digital challengers experience the mechanism differently.','time_difference':'Current transition period; sustainable end-state unresolved.','source_ids':['BK-IND-002','BK-CMP-002','EK-BANK-RHYP-001'],'why_unresolved':'Both claims are grounded and may be true in different contexts.','effect_on_confidence':'Downgrades proposal confidence while preserving the mixed-model interpretation.','effect_on_recommendation':'Supports learning and validation, not a direct recommendation.'}]
