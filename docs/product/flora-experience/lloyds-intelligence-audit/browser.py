"""Read-only diagnosis of the unchanged public runtime; diagnostic overlays only.

No stylesheet or route is changed. Red callouts are injected into this isolated
browser after raw captures, then removed on navigation. PDFs print FLORA itself,
never a protected publisher document. No live credential or private run lookup.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from playwright.sync_api import sync_playwright
from cios.applications.flora.web.app import FloraWebHandler

HERE=Path(__file__).resolve().parent
PATH='/enterprises/lloyds'
VIEWS={
 'group':'', 'economics':'?focus=economics', 'retail':'?focus=retail', 'commercial':'?focus=commercial',
 'ipi':'?focus=retirement', 'operations':'?stream=inside&focus=operations',
 'credit':'?stream=inside&focus=operations&detail=journey-credit',
 'capabilities':'?stream=inside&focus=capabilities', 'applications':'?stream=inside&focus=applications',
 'partners':'?stream=inside&focus=partners', 'programmes':'?stream=inside&focus=programmes',
 'people':'?stream=inside&focus=people&detail=structure', 'strategy':'?stream=forces&focus=strategy',
 'markets':'?stream=forces&focus=markets', 'resilience':'?stream=forces&focus=resilience',
 'competition':'?stream=forces&focus=competition', 'swot':'?stream=forces&focus=analysis',
 'costs':'?focus=economics&detail=costs','capital':'?focus=economics&detail=capital'}
TABLET={'group','economics','commercial','credit','capabilities','strategy','swot'}
class Quiet(FloraWebHandler):
 def log_message(self,*args):pass
GEOMETRY=r'''() => {
 const main=document.querySelector('main'), box=main.getBoundingClientRect();
 const vis=r=>r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth;
 const rect=e=>{let r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,right:r.right}};
 const clipped=[...main.querySelectorAll('.canvas-title,.gold-stocks strong,.le-measure strong')].filter(e=>e.scrollWidth>e.clientWidth+1&&e.clientWidth>0).map(e=>({text:e.textContent,box:rect(e),scrollWidth:e.scrollWidth}));
 const overlaps=[...main.querySelectorAll('[data-canvas-region]')].flatMap(e=>{let a=e.querySelector('.canvas-arrow'),t=e.querySelector('.canvas-title');if(!a||!t)return [];let x=a.getBoundingClientRect(),y=t.getBoundingClientRect();return Math.min(x.right,y.right)>Math.max(x.left,y.left)&&Math.min(x.bottom,y.bottom)>Math.max(x.top,y.top)?[{text:t.textContent,arrow:rect(a),title:rect(t)}]:[]});
 const markOverlaps=[...main.querySelectorAll('[data-canvas-region]')].flatMap(e=>{let a=e.querySelector('.canvas-mark'),t=e.querySelector('.canvas-title');if(!a||!t)return [];let x=a.getBoundingClientRect(),y=t.getBoundingClientRect();return Math.min(x.right,y.right)>Math.max(x.left,y.left)&&Math.min(x.bottom,y.bottom)>Math.max(x.top,y.top)?[{text:t.textContent,mark:rect(a),title:rect(t),markPosition:getComputedStyle(a).position}]:[]});
 const narrowLayerTitles=[...main.querySelectorAll('.canvas-layer-stack .canvas-title')].map(e=>({text:e.textContent,width:e.getBoundingClientRect().width,parentColumns:getComputedStyle(e.parentElement).gridTemplateColumns,markPosition:getComputedStyle(e.parentElement.querySelector('.canvas-mark')).position})).filter(x=>x.width<100);
 const regions=[...main.querySelectorAll('[data-canvas-region]')].map(e=>({name:e.getAttribute('aria-label')||e.textContent.trim().slice(0,90),kind:e.dataset.canvasRegion,box:rect(e),visible:vis(e.getBoundingClientRect()),words:e.textContent.trim().split(/\s+/).length}));
 const wraps=[...main.querySelectorAll('.canvas-title')].map(e=>{let r=document.createRange();r.selectNodeContents(e);return {text:e.textContent,lines:new Set([...r.getClientRects()].map(x=>Math.round(x.top))).size}}).filter(x=>x.lines>1);
 return {main:rect(main),viewport:{width:innerWidth,height:innerHeight},pageHeight:document.documentElement.scrollHeight,horizontalOverflow:document.documentElement.scrollWidth>innerWidth+1,clippedText:clipped,iconTitleBoxIntersections:overlaps,markTitleBoxIntersections:markOverlaps,narrowLayerTitles,wrappedTitles:wraps,regions,tables:main.querySelectorAll('table').length,words:main.innerText.trim().split(/\s+/).length,unavailableMentions:(main.innerText.match(/unknown|unavailable|unverified/gi)||[]).length,articleCount:main.querySelectorAll('.intelligence-statement').length};
}'''
CALLOUTS={
 'group':[('.canvas-businesses','1 · Three orientation businesses; no measured segment contribution'),('.canvas-financials','2 · Two Group measures dominate the economic story')],
 'economics':[('.gold-economic-map','1 · Four large mechanism targets are conceptual, not a measured bridge'),('.gold-stocks','2 · Two deposit stocks; not income, margin or organic inflow')],
 'commercial':[('.gold-table','1 · Conceptual activities, not a verified Lloyds workflow'),('.ceo-unavailable','2 · Segment contribution remains absent')],
 'credit':[('.canvas-layer-stack','1 · Navigable layers; role, system and contract edges remain unverified')],
 'strategy':[('.canvas-goal-rail','1 · Goals and disclosure horizons; not measured execution progress')],
 'swot':[('.gold-swot','1 · Eight themes remain hypotheses/analysis, not qualified opportunities')]}
def run(out):
 out.mkdir(parents=True,exist_ok=True);proof={'runtime_baseline':'3a4c7e0f6ad81af7ef32ed477a1a584ac2efae87','capture_checkout':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'mode':'isolated Guest public read; exact deployed code cut; not live DOM or physical iPad certification','screens':{},'files':{},'pdf':{},'live_probe':{},'runtime_errors':[]}
 try:
  with urllib.request.urlopen('https://flora-current.onrender.com/deployment',timeout=12)as r:
   d=json.load(r);proof['live_probe']={'http':r.status,'commit_sha':d.get('commit_sha')}
 except Exception as e:proof['live_probe']={'status':'unavailable from execution network','class':type(e).__name__,'limitation':'Render deployment API independently verifies the code SHA; no live DOM or live rendering claim'}
 with TemporaryDirectory(prefix='lloyds-diagnostic-')as data,sync_playwright()as pw:
  os.environ.update(FLORA_DATA_DIR=data,FLORA_ENVIRONMENT='development',FLORA_AUTH_PROVIDER='local',FLORA_TRUST_PROXY_HEADERS='0');os.environ.pop('OPENAI_API_KEY',None)
  with ThreadingHTTPServer(('127.0.0.1',0),Quiet)as server:
   thread=Thread(target=server.serve_forever,daemon=True);thread.start();base='http://127.0.0.1:'+str(server.server_port)
   browser=pw.chromium.launch(executable_path=shutil.which('chromium'),args=['--no-sandbox'])
   try:
    for device,(w,h)in {'desktop':(1440,1000),'ipad-landscape':(1194,834),'ipad-portrait':(834,1194)}.items():
     page=browser.new_page(viewport={'width':w,'height':h},has_touch=device!='desktop',reduced_motion='reduce')
     page.on('pageerror',lambda e:proof['runtime_errors'].append(str(e)))
     for name,q in VIEWS.items():
      if device!='desktop'and name not in TABLET:continue
      assert page.goto(base+PATH+q).status==200
      page.evaluate('document.fonts.ready');page.wait_for_function('[...document.images].filter(i=>i.checkVisibility()).every(i=>i.complete&&i.naturalWidth>0)')
      page.evaluate('scrollTo(0,0)');metrics=page.evaluate(GEOMETRY);metrics['url']=PATH+q;proof['screens'][device+':'+name]=metrics
      file=device+'-'+name+'.jpg';page.screenshot(path=out/file,quality=78);proof['files'][file]=hashlib.sha256((out/file).read_bytes()).hexdigest()
      if name in CALLOUTS and (device=='desktop'or name in {'economics','credit','swot'}):
       page.evaluate('''items=>{const style=document.createElement('style');style.textContent='.audit-callout{position:absolute!important;z-index:9999;background:#fff2e8;color:#8f2416;border:2px solid #a12c21;padding:8px 12px;font:12px/1.4 Arial;max-width:340px;box-shadow:0 2px 5px #0003;pointer-events:none}.audit-outline{outline:3px dashed #a12c21!important;outline-offset:2px}';document.head.append(style);for(const [selector,label]of items){let e=document.querySelector('main '+selector);if(!e)continue;e.classList.add('audit-outline');let r=e.getBoundingClientRect(),n=document.createElement('div');n.className='audit-callout';n.textContent=label;n.style.left=Math.min(innerWidth-365,Math.max(12,r.left+scrollX))+'px';n.style.top=Math.max(155,r.top+scrollY-48)+'px';document.body.append(n)}}''',CALLOUTS[name])
       file=device+'-'+name+'-annotated.jpg';page.screenshot(path=out/file,quality=80);proof['files'][file]=hashlib.sha256((out/file).read_bytes()).hexdigest()
     page.goto(base+PATH+VIEWS['credit']);target=page.locator('main .canvas-layer-stack .canvas-technology').first;target.scroll_into_view_if_needed();page.evaluate('scrollBy(0,-90)')
     for annotated in (False,True):
      if annotated:page.evaluate('''()=>{let n=document.createElement('div');n.textContent='Diagnostic: technology-region icon is absolute; title occupies the 65px grid column. No runtime repair applied.';Object.assign(n.style,{position:'fixed',left:'38%',right:'16px',top:'16px',zIndex:99999,background:'#fff2e8',border:'2px solid #a12c21',padding:'12px',font:'13px Arial',color:'#8f2416'});document.body.append(n);document.querySelectorAll('main .canvas-layer-stack .canvas-technology .canvas-title').forEach(e=>e.style.outline='3px dashed #a12c21')}''')
      file=device+'-credit-layer'+('-annotated'if annotated else'')+'.jpg';page.screenshot(path=out/file,quality=80);proof['files'][file]=hashlib.sha256((out/file).read_bytes()).hexdigest()
     if device=='desktop':
      for name in ('economics','credit','strategy'):
       page.goto(base+PATH+VIEWS[name]);page.evaluate('document.fonts.ready');file='print-'+name+'.pdf';page.pdf(path=out/file,format='A4',print_background=True,margin={'top':'10mm','bottom':'10mm','left':'10mm','right':'10mm'});proof['files'][file]=hashlib.sha256((out/file).read_bytes()).hexdigest()
       import pymupdf
       doc=pymupdf.open(out/file);proof['pdf'][name]={'pages':len(doc),'text_per_page':[len(p.get_text())for p in doc],'media':'Chromium A4 print, default app CSS; no print repair','legal_boundary':'FLORA application output, not issuer documents or tables'}
       img=doc[0].get_pixmap(matrix=pymupdf.Matrix(1.15,1.15));f='print-'+name+'-page1.jpg';(out/f).write_bytes(img.tobytes('jpeg',jpg_quality=75));proof['files'][f]=hashlib.sha256((out/f).read_bytes()).hexdigest()
     page.close()
   finally:browser.close();server.shutdown();thread.join(2)
 proof['geometry_limit']='Box intersection is a candidate defect, not proof of visible glyph collision. Title wrapping and vertical scrolling are measured separately, not automatically defects.'
 (out/'Browser-Diagnostic.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'screens':len(proof['screens']),'files':len(proof['files']),'pdf':proof['pdf'],'runtime_errors':proof['runtime_errors'],'live':proof['live_probe']}))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=HERE/'previews');args=a.parse_args();run(args.output)
