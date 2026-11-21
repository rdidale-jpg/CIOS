from pathlib import Path
from html import escape as e
import json,re,os
R=Path(__file__).resolve().parents[5];D=Path(__file__).resolve().parent.parent;old=D.parent/'rich'
os.environ['FLORA_DATA_DIR']='/tmp/flora-lj2-design'
from cios.applications.flora import visual_v2
raw=json.loads((R/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json').read_text());claims={c['id']:c for c in raw['claims']};sources={s['id']:s for s in raw['sources']}
def force(cid,title,question,counter):
 c=claims[cid];return {'id':cid,'title':title,'text':c['statement'],'date':c['reporting_period'],'question':question,'counter':counter,'source_ids':c['source_ids'],'sources':[{'id':s,'url':sources[s]['url'],'title':sources[s]['title'],'publication_date':sources[s].get('publication_date')}for s in c['source_ids']],'status':c.get('verification'),'kind':c['kind']}
uk=[]
for key in visual_v2.FACTORS:
 v=visual_v2.insight(key);uk.append({'id':key,'title':{'political':'Public buying','economic':'Economic growth','social':'Social value','technological':'Cyber resilience','legal':'Cyber reform','environmental':'Climate reporting'}[key],'text':v['text'],'date':v['lineage'].get('as_of','2026-11-13'),'question':v['effect'],'counter':v['details'],'source_ids':v['lineage']['source_ids'],'sources':[{k:s.get(k)for k in ['id','title','url','publication_date']}for s in v['sources']],'status':v['lineage']['authority'],'kind':v['lineage'].get('kind','frozen public extract')})
bank=[force('UK-RATE-NOV26','Rates & margins','Which funding sensitivities apply to this bank?','Rate direction alone does not establish lost margin or customer demand.'),force('UK-PRA-REPORT27','Resilience reporting','Which legal entities and existing controls are in scope?','The firm may already be ready; deadline is not external scope.'),force('UK-FCA-REPORT27','Customer outcomes','Which service outcome remains unresolved?','Industry rule does not prove this bank has an unmet need.'),force('LBG-ENVOY-CONTROLS','AI & control','What outcome is not covered by current platforms?','Lloyds is an enterprise example, not evidence for every bank; controls already exist.'),force('UK-VALUE','Competition & trust','Which relationship or customer friction is material?','Conceptual value-system interpretation, not a dated loss of market share.'),force('UK-CTP','Technology dependence','Which specific service has a proven exposure?','Older repository reference; designation dates are not newly verified.')]
lbg=[force('LBG-A2030-PLATFORMS','Core modernisation','Which migration decision is still open?','A stated priority does not reveal supplier scope or decision dates.'),force('LBG-A2030-CIR','Cost discipline','What baseline and customer outcome constrain change?','Below 45% in 2030 is a target, not achieved performance or a budget.'),force('LBG-ENVOY-CONTROLS','AI benefit & control','Is a process-only alternative sufficient?','Internal teams, controls and existing partners may cover the need.'),force('LBG-BRAND26-TIMING','Brand & service change','Which customer outcomes still need validation?','A planned 2027 branch timetable does not prove open procurement.'),force('LBG-Q326-INVESTMENT','Investment choices','Which allocation remains undecided?','Plateauing investment is current-cycle commentary, not a ban on later investment.'),force('UK-PRA-REPORT27','Resilience obligations','Which Lloyds legal entity and actual readiness evidence apply?','Sector context only; entity applicability and external need are unverified.')]
force_map={'uk':uk,'banking':bank,'lloyds':lbg}
positions=[('barclays','Barclays',18,48),('hsbc-uk','HSBC UK',48,42),('lloyds','Lloyds Banking Group',80,48),('natwest','NatWest Group',28,76),('santander-uk','Santander UK',73,77),('boe','Bank of England',18,22),('pra','PRA',38,20),('fca','FCA',87,22),('payments','Payments',53,65)]
def spot(id,title,x,y,href):
 mx=(x-50)*2 if x>=50 else x*2;fy=(y+(100 if x>=50 else 0))/2
 return f'<a class="spot active" data-label-id="{id}" href="{href}" style="--x:{x}%;--y:{y}%;--mx:{mx}%;--fy:{fy}%">{e(title)} <span aria-hidden="true">›</span></a>'
def cleanfig(html):
 fig=re.search(r'<figure class="world".*?</figure>',html,re.S).group(0)
 return re.sub(r'<a\b[^>]*class="spot.*?</a>|<span\b[^>]*class="spot.*?</span>','',fig,flags=re.S)
def panel(id,title,text,back):return f'<section class="focus" id="{id}" tabindex="-1"><a class="close" href="{back}" aria-label="Close {e(title)}">×</a><h2>{e(title)}</h2>{text}</section>'
for scope,oldstate in [('uk','01-uk'),('banking','02-banking'),('lloyds','04-lloyds')]:
 for lens in ['landscape','forces']:
  for layer in (['enterprises'] if scope=='uk' else ['enterprises','suppliers','regulators']):
   file=f'{scope}-{lens}'+(''if layer=='enterprises'else '-'+layer)+'.html'
   def dest(l):return f'{scope}-{l}'+(''if layer=='enterprises'else '-'+layer)+'.html'
   html=(old/(oldstate+(''if layer=='enterprises'else '-'+layer)+'.html')).read_text()
   for src,target in [('01-uk','uk-'+lens),('02-banking','banking-'+lens),('03-groups','banking-'+lens),('04-lloyds','lloyds-'+lens)]:html=html.replace(src,target)
   html=html.replace('rich.css','lj2.css').replace('banking-ecosystem.png','banking-combined.png').replace('Model the Enterprise','Enterprise Builder')
   html=re.sub(r'<a href="banking-[^"]*">Banking groups</a>','',html)
   html=re.sub(r' › <a href="banking-[^"]*">Groups</a>','',html)
   controls='<nav class="lens" aria-label="View lens">'+''.join(f'<a data-lens="true" href="{dest(k)}"'+(' aria-current="page"'if k==lens else '')+'>'+t+'</a>'for k,t in [('landscape','LANDSCAPE'),('forces','FORCES')])+'</nav>'
   html=html.replace('<main id="main"',f'<main data-scope="{scope}" data-lens="{lens}" id="main"')
   html=html.replace('<figure class="world"',controls+'<figure class="world"',1)
   if scope=='uk':
    html=html.replace('UK GVA · 2024 · current basic prices','UK GVA · 2024 · current basic prices &nbsp; +0.7% real GDP · 3 months to Sep 2026 vs prior 3 months')
    html=html.replace('banking-'+lens+'.html','banking-landscape.html')
    html=html.replace(controls,controls+'<details class="uk-context"><summary>Economy · UK</summary><p>Government is a separate contextual lens proposed in #607, not another navigation level. No fiscal data or Government Twin is invented here.</p></details>')
   if scope=='banking':
    fig=cleanfig(html);fig=fig.replace('</figure>',''.join(spot(i,t,x,y,'lloyds-'+lens+(''if layer=='enterprises'else '-'+layer)+'.html'if i=='lloyds'else '#bank-'+i if i in ['barclays','hsbc-uk','natwest','santander-uk']else '#'+i)for i,t,x,y in positions)+'</figure>')
    html=re.sub(r'<figure class="world".*?</figure>',lambda m:fig,html,count=1,flags=re.S)
    html=re.sub(r'<section class="focus" id="groups".*?</section>','',html,flags=re.S)
    for i,t,_,_ in positions[:5]:
     if i=='lloyds':continue
     html=html.replace('</main>',panel('bank-'+i,t,'<p>Existing public-source profile; rich enterprise depth is not supplied for this bank in this pilot.</p><p><a data-lens="true" href="'+dest('forces'if lens=='landscape'else 'landscape')+'#bank-'+i+'">Switch lens with this bank selected</a></p>',file)+'</main>')
    html=html.replace('Banking groups','Banking enterprises')
   if lens=='forces':
    fig=cleanfig(html);fig=fig.replace('</figure>',''.join(spot('force-'+f['id'],f['title'],25 if n%2==0 else 75,22+(n//2)*28,'#force-'+f['id'])for n,f in enumerate(force_map[scope]))+'</figure>')
    html=re.sub(r'<figure class="world".*?</figure>',lambda m:fig,html,count=1,flags=re.S)
    for f in force_map[scope]:
     body='<p>'+e(f['text'])+'</p><p><strong>Evidence period:</strong> '+e(f['date'])+'</p><p><strong>Counterpoint:</strong> '+e(f['counter'])+'</p><p><strong>Question:</strong> '+e(f['question'])+'</p><p>Pressure does not establish demand, procurement, budget or an early influence window. Timing and applicability need validation.</p><details><summary>Sources</summary>'+''.join('<p><a href="'+e(s['url'],quote=True)+'">'+e(s['title'])+'</a> · publication '+e(s.get('publication_date')or'not established')+'</p>'for s in f['sources'])+'</details>'
     html=html.replace('</main>',panel('force-'+f['id'],f['title'],body,file)+'</main>')
    html=html.replace('class="commercial-story"','class="commercial-story" hidden')
    alt=''.join('<a href="#force-'+f['id']+'">'+e(f['title'])+'</a>'for f in force_map[scope])
    html=re.sub(r'<details class="text-view">.*?</details>','<details class="text-view"><summary>Text view</summary>'+alt+'</details>',html,flags=re.S)
   if scope=='banking':
    alt=''.join('<a href="'+('lloyds-'+lens+(''if layer=='enterprises'else '-'+layer)+'.html'if i=='lloyds'else '#bank-'+i if i in ['barclays','hsbc-uk','natwest','santander-uk']else '#'+i)+'">'+e(t)+'</a>'for i,t,_,_ in positions)
    html=re.sub(r'<details class="text-view">.*?</details>','<details class="text-view"><summary>Text view</summary>'+alt+'</details>',html,flags=re.S)
   html=html.replace('</body>','<script src="context.js"></script></body>')
   (D/file).write_text(html)
(D/'Force-Trace.json').write_text(json.dumps({'authority':'Design read projection only. No Material Pressure qualified; ADR-026 gates and original owners untouched. No second intelligence model.','scopes':force_map,'nine_gaps':'Research-Gaps.md','missing_macro_coverage':'No new geopolitical, energy-cost or workforce series fabricated where existing reviewed records do not support a specific claim.'},indent=2)+'\n')
