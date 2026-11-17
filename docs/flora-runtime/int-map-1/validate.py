"""Read-only decision-pack checks, never a runtime intelligence engine."""
import ast
from datetime import date
from decimal import Decimal
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[3]
PACK=Path(__file__).resolve().parent
BASE='fbac4c37910ed07b2baa516e1a5c8d7f329086de'
ALLOWED=('docs/flora-runtime/int-map-1/','.github/workflows/flora-int-map1-653.yml')


def validate():
    subprocess.run(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT,check=True)
    changed=subprocess.check_output(['git','diff','--name-only',BASE],cwd=ROOT,text=True).splitlines()
    changed+=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    assert all(p.startswith(ALLOWED[0])or p==ALLOWED[1]for p in changed), 'Change outside decision/design boundary'
    register=json.loads((PACK/'Traceability.json').read_text())
    assert register['baseline']==BASE and register['authority']=='design_audit_only_not_runtime_registry'
    for row in register['code_anchors']:
        raw=(ROOT/row['path']).read_bytes()
        assert sha256(raw).hexdigest()==row['sha256']
        assert raw==subprocess.check_output(['git','show',BASE+':'+row['path']],cwd=ROOT)
        body=ast.parse(raw).body
        for part in row['symbol'].split('.'):
            matches=[n for n in body if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name==part]
            assert len(matches)==1
            body=matches[0].body
        assert len(matches)==1 and matches[0].lineno==row['line']
    for row in register['retained_files']:
        raw=(ROOT/row['path']).read_bytes()
        assert sha256(raw).hexdigest()==row['sha256']
        assert raw==subprocess.check_output(['git','show',BASE+':'+row['path']],cwd=ROOT)
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'cios/applications/flora/visual_stream_assets'],cwd=ROOT,text=True).splitlines()
    assert len(paths)==51
    for path in paths:
        assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
    news=json.loads((ROOT/'docs/flora-runtime/bie2/News-Candidates.json').read_text())
    assert len(news['events'])==17 and all(r['production_news_eligible']is False for r in news['events'])
    assert news['anchor']=='2026-11-15'
    ctp=json.loads((ROOT/register['examples'][0]['source_file']).read_text())
    assert ctp['source']['id']=='EAI-HMT-CTP26' and ctp['source']['publication_date']=='2026-07-10'
    rud=json.loads((ROOT/register['examples'][1]['source_file']).read_text())
    source=next(s for s in rud['sources']if s['id']=='RUD1-NATIONWIDE-FY26')
    assert source['publication_date']=='2026-05-21'
    assert source['reported_subject']['start']=='2025-04-01' and source['reported_subject']['end']=='2026-03-31'
    ms=next(r for r in rud['financial_selections']if r['key']=='nationwide-fy2026')['measurements']
    values={r['metric']:Decimal(r['value']['amount'])for r in ms}
    assert len(values)==8 and values['total_income']+values['operating_costs']+values['credit_impairment']==values['underlying_profit_before_tax']==2026
    assert sum(values[k]for k in ('underlying_profit_before_tax','income_basis_adjustment','acquisition_expense_adjustment','member_reward_payments'))==values['profit_before_tax']==1490
    overlay=json.loads((ROOT/register['examples'][2]['source_file']).read_text())
    envoy=next(s for s in overlay['sources']if s['id']=='PR-LBG-ENVOY')
    assert envoy['publication_date']=='2026-05-01'
    assert all(date.fromisoformat(e['publication'])<date(2026,8,1)for e in register['examples'])
    html=(PACK/'concept/index.html').read_text()
    assert not re.search(r'https?://|\bfetch\s*\(|XMLHttpRequest|WebSocket|localStorage|sessionStorage',html)
    class Links(HTMLParser):
        refs=[]
        def handle_starttag(self,tag,attrs):
            if tag=='img':self.refs.append(dict(attrs)['src'])
    parser=Links();parser.feed(html)
    for ref in parser.refs+re.findall(r"url\(['\"]?([^)'\"]+)['\"]?\)",html):
        assert (PACK/'concept'/ref).resolve().is_file()
    links=0
    for p in PACK.glob('*.md'):
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
            if target.startswith(('https:','http:','#')):continue
            assert (p.parent/target.split('#')[0]).is_file(), (p.name,target)
            links+=1
    return {'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'baseline':BASE,'preserved_initial_draft':register['prior_draft_head'],'code_anchors':len(register['code_anchors']),
        'unchanged_retained_files':len(register['retained_files']),'unchanged_visual_files':len(paths),
        'candidate_news_rows':17,'production_news_admissions':0,'example_source_date_checks':3,
        'financial_bridge_checks':2,'local_markdown_links':links,'application_changes':0,'source_permission_changes':0,
        'canonical_or_production_writes':0,'scope':'Static decision integrity; not runtime or live-production validation'}


if __name__=='__main__':print(json.dumps(validate(),indent=2))
