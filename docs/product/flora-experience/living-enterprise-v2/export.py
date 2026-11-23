"""Package the same prototype renderer as one offline, read-only design preview.

Rendered snapshot only; never an application intelligence store or deployment.
"""
import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).parent))
import prototype as design


def build(output):
    pages={}
    for stream,regions in design.REGIONS.items():
        for focus,*_ in regions:
            markup=design.render(design.State(stream,focus,focus))
            pages[stream+':'+focus]=re.search(r'<body[^>]*>(.*)</body>',markup,re.S)[1]
    initial=design.render(design.State())
    head=re.search(r'<head>(.*)</head>',initial,re.S)[1]
    def text_asset(path):
        if path=='/design/living.css':return (design.HERE/'living.css').read_text()
        if path.startswith('/design-system/assets/'):return design.ds.asset(path.rsplit('/',1)[1])[0].decode()
        if path.startswith(design.v.ASSET_BASE):return design.v.asset(path.rsplit('/',1)[1])[0].decode()
        raise ValueError('Unknown design dependency')
    head=re.sub(r'<link[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>',lambda m:'<style>'+text_asset(m[1])+'</style>' if 'stylesheet'in m[0] else '',head)
    head=re.sub(r'<script[^>]*src=[\'"][^\'"]+[\'"][^>]*></script>','',head)
    assets={}
    for path in set(re.findall(r'/visual-streams/assets/[a-zA-Z0-9-]+',head+''.join(pages.values()))):
        raw,mime=design.v.asset(path.rsplit('/',1)[1]);assets[path]='data:'+mime.split(';')[0]+';base64,'+base64.b64encode(raw).decode()
    for path,data in assets.items():head=head.replace(path,data)
    # A bare key is sufficient; every state was rendered by the current Source
    # owners. Client code changes presentation/navigation, never intelligence.
    config={'pages':pages,'assets':assets,'subjects':design.SUBJECTS,'base':design.BASE,
            'captured':datetime.now(timezone.utc).isoformat(),'compact_script':(design.HERE/'living.js').read_text()}
    packed=json.dumps(config,separators=(',',':')).replace('</','<\\/')
    script=r'''
const cfg=JSON.parse(document.getElementById('le-snapshot').textContent);
let current;
function state(){
 const p=new URLSearchParams(location.search),stream=p.get('stream')||'landscape';
 const first={landscape:'retail',inside:'operations',forces:'funding'};
 const focus=p.get('focus')||first[stream],subject=p.get('subject')||focus;
 if([...p.keys()].some(k=>!['stream','focus','subject'].includes(k))||!cfg.pages[stream+':'+focus]||!cfg.subjects[subject])throw Error('Unsupported design state');
 return {stream,focus,subject};
}
function paint(){
 current=state();let html=cfg.pages[current.stream+':'+current.focus];
 for(const [path,data] of Object.entries(cfg.assets))html=html.split(path).join(data);
 document.body.innerHTML=html;
 document.body.dataset.focus=current.focus;document.body.dataset.subject=current.subject;
 if(current.subject!==current.focus){
  document.querySelector('main .eyebrow').append(' · From '+cfg.subjects[current.subject]);
  const note=document.createElement('p');note.className='le-limit';note.textContent='Retained context only. Group-wide intelligence does not establish divisional allocation or capability-specific exposure.';
  const target=document.querySelector('main .le-next, main .le-investigate');if(target)target.before(note);else document.querySelector('main #overview').append(note);
 }
 for(const a of document.querySelectorAll('a[href]')){
  const raw=a.getAttribute('href');if(raw.startsWith('#'))continue;
  const u=new URL(raw,'https://preview.invalid');
  if(u.pathname==='/design/lloyds'){
   if(!a.hasAttribute('data-region-key'))u.searchParams.set('subject',current.subject);
   a.setAttribute('href',location.pathname+'?'+u.searchParams.toString()+u.hash);a.dataset.designLink='true';
  }else if(raw.startsWith('/'))a.href='https://flora-current.onrender.com'+raw;
 }
 // Execute only the existing trusted choice component and compact-scene script.
 for(const script of document.querySelectorAll('body script')){const code=script.textContent;script.remove();Function(code)();}
 Function(cfg.compact_script)();
 document.querySelector('.le-design-note').textContent='Design snapshot · '+cfg.base.slice(0,7);
}
document.addEventListener('click',event=>{
 const a=event.target.closest('a[data-design-link]');
 if(!a||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
 event.preventDefault();history.pushState({},'',a.getAttribute('href'));paint();
 const main=document.querySelector('main');main.focus({preventScroll:true});if(innerWidth<1000)main.scrollIntoView();else scrollTo(0,0);
});
addEventListener('popstate',paint);
try{paint();}catch(error){document.body.textContent='Unsupported design state. Open this file without query parameters.';}
'''
    # Keep snapshot data outside Body because Body is swapped as one existing frame.
    html='<!doctype html><html lang="en-GB"><head>'+head+'<script id="le-snapshot" type="application/json">'+packed+'</script></head><body class="ds-page vp-page le-page" data-prototype="design-snapshot"><script>'+script+'</script></body></html>'
    Path(output).write_text(html)
    return {'states':len(pages),'embedded_assets':len(assets),'bytes':Path(output).stat().st_size,'source':'existing renderer; design snapshot only','base':design.BASE}

if __name__=='__main__':print(json.dumps(build(design.HERE/'preview.html'),indent=2))
