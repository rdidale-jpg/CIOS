"""Isolated authored experience proof; exports HTML only, not application routes."""
from pathlib import Path
from html import escape as e
from lxml import html as H,etree
from urllib.parse import urlsplit,parse_qs,unquote,urlencode
import base64,json,re,copy
ROOT=Path(__file__).resolve().parents[4];D=Path(__file__).resolve().parents[1];OUT=D/'prototype'
refs=json.loads((D/'Evidence-References.json').read_text())['references'];proof=json.loads((D/'Proof-Cases.json').read_text());base=json.loads(Path('/tmp/si1-public-base.json').read_text())
art=json.loads((ROOT/'cios/applications/flora/visual_stream_assets/artwork.json').read_text())
NAMES={'uk':'United Kingdom','banking':'UK Banking','lloyds':'Lloyds Banking Group'}
css=(ROOT/'cios/applications/flora/design_assets/design.css').read_text()+'\n'+(ROOT/'cios/applications/flora/visual_stream_assets/streams.css').read_text()+'\n'+(D/'review-tools/prototype.css').read_text()
script=(D/'review-tools/prototype.js').read_text()

def serial(x):return etree.tostring(x,encoding='unicode',method='html')
def source_html(key):
 r=refs[key]
 sources=''.join('<p><a href="'+e(s['url'],quote=True)+'" rel="noreferrer" target="_blank">'+e(s['title'])+'</a> · '+e(s.get('published_at')or'Publication date unknown')+'</p><p class="timing">'+e(s.get('source_role',''))+' '+e(str(s['rights']))+'</p><details><summary>Source scope and review</summary><p>Read extent: '+e(str(s.get('extent')or'Unknown'))+'</p><p>Retrieved: '+e(str(s.get('retrieved_at')or'Unknown'))+'</p><p>'+e(str(s.get('limitation')or'No additional source-specific limitation recorded; original rights and scope still apply.'))+'</p></details>'for s in r['sources'])
 return '<article class="source-binding"><p>'+e(r['statement'])+'</p><p class="timing">'+e(r['reporting_period']or'Period unknown')+' · review '+e(r['review_cutoff'])+'</p>'+sources+'<details><summary>Original research reference</summary><p>'+e(key)+' · '+e(r['authority'])+'</p><p>'+e(r['owner_path'])+' · '+e(r['locator'])+'</p><p>Source-backed statement only; not independent verification of business effectiveness or an accepted Observation.</p></details></article>'

def agenda(scope):
 items=proof['agendas'][scope];cards=''
 for i,x in enumerate(items):
  key=x['view_ref'].split(':')[-1]
  analysis=x['analysis'];swot=''.join('<p><strong>'+e(k.replace('_',' ').title())+'</strong> '+e(' '.join(v)if v else'No supported finding in this proof.')+'</p>'for k,v in analysis['swot'].items())
  challenges=''.join('<li>'+e(c['statement'])+' <small>'+('Reported counter-evidence'if c['source_refs']else'Alternative or limit to test')+'</small></li>'for c in x['challenges'])
  trace=next(t for t in proof['traces']if t['issue']==x['view_ref'])
  edges=''.join('<li><strong>'+e(edge['status'].replace('_',' '))+'</strong> · '+e(edge['rationale'])+'</li>'for edge in trace['admission_path'])
  conditional=''.join('<li>'+e(edge['from'])+' → '+e(edge['to'])+'<p><strong>'+e(edge['status'])+'</strong> · '+e(edge['rationale'])+'</p></li>'for edge in trace['conditional_transmission_path'])
  cards+='<article class="agenda-card"><p class="eyebrow">'+('Company-stated priority'if x['leadership']['attribution_basis']else'Decision to investigate')+'</p><h3>'+e(x['title'])+'</h3><p>'+e(x['why_it_matters'])+'</p><p class="uncertainty"><strong>Biggest uncertainty</strong> '+e(x['biggest_uncertainty'])+'</p><details class="issue-detail" id="issue-'+key+'"><summary>Explore the decision</summary><h4>A useful first conversation</h4><p>'+e(x['decision']['question'])+'</p><h4>Best next action</h4><p>'+e(x['commercial']['next_investigation'])+'</p><h4>Who to understand</h4><p>'+e('; '.join(x['leadership']['role_hypotheses']))+'. Role ownership unconfirmed.</p><h4>What is committed</h4><p>'+e(x['decision']['already_committed'])+'</p><h4>What remains open</h4><p>'+e(x['decision']['remaining_choices'])+' No influence window is established.</p><h4>Counter-evidence and alternative explanations</h4><ul>'+challenges+'</ul><p class="boundary">No demonstrated pain, confirmed buyer need, budget or supplier opportunity is established.</p><details><summary>Analysis behind this question</summary><p><strong>External factors</strong> '+e(', '.join(analysis['pestle']))+'</p><p><strong>Competitive economics</strong> '+e(' '.join(analysis['five_forces']))+'</p><p><strong>Value chain</strong> '+e(' '.join(analysis['value_chain']))+'</p>'+swot+'<h4>Supported admission path</h4><ol>'+edges+'</ol>'+('<h4>Conditional transmission — excluded from stronger claims</h4><ol>'+conditional+'</ol>'if conditional else'')+'<p>'+e(trace['excluded_conclusion'])+'</p></details><details class="issue-sources"><summary>Sources and dates</summary>'+''.join(source_html(r)for r in x['source_refs'])+'</details></details></article>'
 methods='<details class="analysis-inventory"><summary>The wider strategic picture</summary><p>This is a bounded design proof, not a complete diagnosis. Unknowns remain visible; research gaps are not enterprise weaknesses.</p><h3>Forces of Change</h3><p>Political · Economic · Social · Technological · Legal · Environmental. All six are considered; not every factor supports an issue.</p><p>UK policy and aggregate cyber evidence do not automatically apply to a bank. France-scoped guidance does not establish a Lloyds duty.</p><h3>Competitive economics</h3><p>Rivalry · New entrants · Substitutes · Supplier power · Buyer power. Current market shares, bargaining effects and profit pools remain unmeasured. No score or ranking is assigned.</p><h3>How value is created and captured</h3><p>Customer acquisition → deposits and funding → lending and payments → service outcomes. Risk, platforms, data and people enable the chain. These are business functions, not verified contracts or a current system map.</p><h3>Performance and operating model</h3><p>Lloyds deposit stock, nine-month profit and future efficiency target are distinct measures. Current income, costs, comparable growth, legal hierarchy and system dependencies remain unresolved. No cost-to-serve or external deal value is calculated.</p><h3>Leadership and choices</h3><p>Company-stated priorities are distinct from named executive beliefs. Current ownership, alternatives, incumbent coverage and remaining decisions need validation.</p><h3>Strengths and weaknesses</h3><p>Existing announced AI capability challenges a missing-platform pitch. Effectiveness is unverified. No current internal weakness or demonstrated pain is fabricated.</p><p><a href="../Analytical-Design.md">Complete analytical design and coverage</a></p></details>'
 negatives=''
 if scope in ('banking','lloyds'):
  for n in proof['negative_cases']:
   rs=n.get('source_refs',[])+n.get('excluded_source_refs',[])
   negatives+='<details class="negative-case" id="negative-'+n['id']+'"><summary>'+e(n['title'])+'</summary><p>'+e(n['observed'])+'</p><p>'+e(n['interpretation'])+'</p><p><strong>'+e(n['decision_specific_result'])+'</strong></p>'+('<p>'+e(n['next_test'])+'</p>'if n.get('next_test')else'')+'<details><summary>Sources and dates</summary>'+''.join(source_html(r)for r in rs)+'</details></details>'
 return '<details class="leadership-agenda" id="agenda"><summary>Leadership agenda <span>'+str(len(items))+' questions worth investigating</span></summary><section id="agenda-content" tabindex="-1" aria-labelledby="agenda-title" data-agenda-scope="'+scope+'"><div class="agenda-intro"><p class="eyebrow">'+e(NAMES[scope])+'</p><h2 id="agenda-title">The decisions that deserve a closer look</h2><p>What matters, what remains uncertain, and a useful next conversation.</p></div><div class="agenda-grid">'+cards+'</div>'+methods+('<details class="challenge-cases"><summary>When to hold back</summary>'+negatives+'</details>'if negatives else'')+'<p class="design-note">Design proof · existing public research reviewed through 14 November 2026 · no private records or sales opportunities created.</p></section></details>'

def local_href(url,view):
 parts=urlsplit(url)
 if parts.scheme or parts.netloc:return url
 q=parse_qs(parts.query);path=parts.path
 scope={'/':'uk','/flora':'uk','/pestle':'uk','/industries/banking':'banking','/enterprises/lloyds':'lloyds'}.get(path)
 if scope:
  stream=q.get('stream',['forces'if path=='/pestle'else'inside'if scope=='lloyds'else'landscape'])[0]
  name=scope+'-'+stream
  if name in base:
   frag=parts.fragment
   if q.get('detail'):frag='focus-'+q['detail'][0]
   if not path and frag:return '#'+frag
   extra={k:v[0]for k,v in q.items()if k in ('layer','selected')};query='?'+urlencode(extra)if extra else''
   return name+'.html'+query+('#'+frag if frag else'')
 if not path:return url
 if path.startswith('/visual-streams/assets/'):
  asset=path.rsplit('/',1)[1]+'.webp';return '../../../../cios/applications/flora/visual_stream_assets/'+asset
 if path.startswith('/'):
  return 'https://flora-current.onrender.com'+url
 return url

OUT.mkdir(exist_ok=True);docs={}
for view,row in base.items():
 doc=H.document_fromstring(row['html']);head=doc.find('head')
 for node in list(head):
  if node.tag in ('link','script'):head.remove(node)
 style=H.Element('style');style.text=css;head.append(style)
 main=doc.find('.//main')
 # Export all current optional focus details, bound to their original source owners.
 for sid,raw in row['details'].items():
  focus=H.document_fromstring(raw).xpath('//section[@id="insight"]')[0]
  focus.set('id','focus-'+sid);focus.set('aria-labelledby','focus-title-'+sid)
  title=focus.xpath('.//*[@id="insight-title"]')[0];title.set('id','focus-title-'+sid)
  main.append(focus)
 ag=H.fragment_fromstring(agenda(row['scope']));main.append(ag)
 cta=H.Element('a',href='#agenda-content',attrib={'class':'agenda-link'});cta.text='Leadership agenda';doc.xpath('//div[@class="page-title"]')[0].append(cta)
 for a in doc.xpath('//*[@href]'):
  a.set('href',local_href(a.get('href'),view))
  if a.get('href','').startswith('https://flora-current'):
   a.set('target','_blank');a.set('rel','noreferrer')
 # Avoid duplicate text/focus IDs from the baseline details.
 for img in doc.xpath('//img'):
  img.set('src',local_href(img.get('src'),view));img.attrib.pop('srcset',None);img.attrib.pop('sizes',None)
 js=H.Element('script');js.text=script;doc.find('body').append(js)
 docs[view]=doc
 (OUT/(view+'.html')).write_text('<!doctype html>'+serial(doc))
# Single-file owner walkthrough: preserve the seven bodies and their accepted geometry.
# Artwork is embedded once per scene, not repeated per image half.
embedded={};chunks=[]
for view,doc0 in docs.items():
 doc=copy.deepcopy(doc0);body=doc.find('body');pane=H.Element('div',attrib={'class':'prototype-pane','data-view':view,'hidden':''})
 for n in list(body):
  if n.tag!='script':pane.append(n)
 for n in pane.xpath('.//*[@id]'):
  n.set('id',view+'--'+n.get('id'))
 for n in pane.xpath('.//*[@aria-labelledby]'):
  n.set('aria-labelledby',' '.join(view+'--'+x for x in n.get('aria-labelledby').split()))
 for n in pane.xpath('.//*[@href]'):
  href=n.get('href')
  if href.startswith('#'):n.set('href','#'+view+'--'+href[1:])
  elif '.html' in href and not href.startswith('http'):
   target,_,frag=href.partition('#');filename,sep,query=target.partition('?');name=filename.removesuffix('.html')
   if name in docs:n.set('href','#'+name+('?'+query if sep else'')+('--'+frag if frag else''))
  elif href.startswith('../'):n.set('href','https://github.com/rdidale-jpg/CIOS/blob/codex/flora-si1-615/docs/flora-runtime/si1-615/'+href[3:]);n.set('target','_blank');n.set('rel','noreferrer')
 for img in pane.xpath('.//img'):
  path=(OUT/img.get('src')).resolve();key=path.name
  embedded[key]='data:image/webp;base64,'+base64.b64encode(path.read_bytes()).decode()
  img.attrib.pop('src',None);img.set('data-art-key',key)
 chunks.append(serial(pane))
bootstrap='const embeddedArtwork='+json.dumps(embedded)+';\n'+script
single='<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>FLORA · SI-1 design walkthrough</title><style>'+css+'</style></head><body class="ds-page vex-page standalone">'+''.join(chunks)+'<noscript><p>JavaScript enables this single-file walkthrough. Use the seven adjacent static HTML pages for native no-script navigation.</p></noscript><script>'+bootstrap+'</script></body></html>'
(OUT/'FLORA-SI1-Walkthrough.html').write_text(single)
print('Seven native static views and one self-contained HTML walkthrough; unchanged accepted artwork reused.')
