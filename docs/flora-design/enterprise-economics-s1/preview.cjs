const {chromium}=require('playwright'), fs=require('fs'), path=require('path'), assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')), checks=[];
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194}};
function check(value,label){assert(value,label);checks.push(label)}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.ECONOMICS_CHROMIUM||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),args:['--no-sandbox']});
 const ctx=await browser.newContext(),page=await ctx.newPage(),requests=[];
 page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>console.error('PAGE ERROR:',e.message));
 const url=(o,e,m='facts',extra='')=>cfg.base+`/view.html?option=${o}&enterprise=${e}&mode=${m}`+extra;
 async function ready(target){const r=await page.goto(target);check(r.status()===200,'HTTP200 '+new URL(target).search);await page.locator('img:visible').evaluateAll(es=>Promise.all(es.map(e=>e.decode())));}
 async function shot(name){await page.screenshot({path:path.join(cfg.output,name+'.jpg'),fullPage:true,quality:85});}
 for(const[device,size]of Object.entries(sizes)){
  await page.setViewportSize(size);
  for(const o of ['a','b','c'])for(const e of ['lloyds','easyjet'])for(const m of ['facts','insight']){
   const label=[o,e,m,device].join('-');await ready(url(o,e,m));
   check(await page.locator('body > [data-region]').count()===3,'Exactly Top/Left/Main '+label);
   check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'No horizontal overflow '+label);
   check((await page.locator('.reading [aria-current=page]').textContent())===(m==='facts'?'Facts':'FLORA Insight'),'Explicit reading mode '+label);
   check(!(await page.locator('#top').innerText()).includes('Economics'),'No global Economics toggle '+label);
   if(e==='lloyds'){
    check(!(await page.locator('#main').innerText()).includes('£'),'No Lloyds financial values '+label);
    check((await page.locator('#main').innerText()).includes('Illustrative'),'Bank illustration label '+label);
   }else{
    const text=await page.locator('#main').innerText();check(text.includes('£10.106bn')&&text.includes('£665m'),'Verified Group measures '+label);
    check(text.includes('2025')&&text.includes('Group'),'Period and Group scope '+label);
   }
   check(await page.locator('.compact-art').isVisible()===(device==='ipad-portrait'),'Portrait disclosure only '+label);
   await shot(label);
   await page.locator('#inspect').click();check(await page.locator('#basis').isVisible(),'On-demand inspection '+label);
   const basis=await page.locator('#basis').innerText();
   if(e==='easyjet')check(basis.includes('8.56')&&basis.includes('APM')&&basis.includes('2024'),'Calculation/basis inspectable '+label);
   else check(await page.locator('#basis a[href*=".pdf"]').count()===0,'No Lloyds PDF link '+label);
   if(o==='a'&&m==='facts')await shot(label+'-source');
   await page.keyboard.press('Escape');check(await page.locator('#inspect').evaluate(e=>e===document.activeElement),'Inspection focus restored '+label);
  }
  for(const e of ['lloyds','easyjet'])for(const view of ['forces','leadership']){
   await ready(url('a',e,'facts','&view='+view));await shot('a-'+e+'-'+view+'-'+device);
   check((await page.locator('main').innerText()).includes(view==='forces'?'Conditions':'Decisions'),'Related view real content '+e+view+device);
  }
 }
 await page.setViewportSize(sizes.desktop);
 for(const o of ['a','b','c'])for(const e of ['lloyds','easyjet']){
  await ready(url(o,e));check((await page.locator('.reading [aria-current=page]').innerText())==='Facts','Facts default '+o+e);
  if(o==='a'){
   await page.locator('.flow-node').nth(1).click();check(new URL(page.url()).searchParams.get('subject')===(e==='lloyds'?'lending':'capacity'),'Selected stage in URL '+e);
  }
  const subject=new URL(page.url()).searchParams.get('subject');
  await page.locator('.reading a').nth(1).click();let u=new URL(page.url());
  check(u.searchParams.get('enterprise')===e&&u.searchParams.get('option')===o&&u.searchParams.get('mode')==='insight'&&u.searchParams.get('subject')===subject,'Reading preserves complete context '+o+e);
  await page.goBack();await page.waitForFunction(()=>new URL(location.href).searchParams.get('mode')==='facts');check(new URL(page.url()).searchParams.get('mode')==='facts','Back restores Facts '+o+e);
  await page.goForward();await page.waitForFunction(()=>new URL(location.href).searchParams.get('mode')==='insight');check(new URL(page.url()).searchParams.get('mode')==='insight','Forward restores Insight '+o+e);
  await page.reload();check((await page.locator('.reading [aria-current=page]').innerText())==='FLORA Insight','Deep reload '+o+e);
  await page.getByRole('link',{name:'Related forces →',exact:true}).click();check(new URL(page.url()).searchParams.get('enterprise')===e,'Forces retains enterprise '+o+e);
  await page.getByRole('link',{name:'Leadership context →',exact:true}).click();check((await page.locator('main').innerText()).includes('Illustrative functional perspectives'),'Leadership not buyer authority '+o+e);
  await page.getByRole('link',{name:'Back to economics →',exact:true}).click();check(new URL(page.url()).searchParams.get('option')===o,'Return retains option '+o+e);
 }
 await ready(url('c','easyjet'));await page.locator('.lens-toggle').click();check(await page.locator('.lens-canvas').getAttribute('data-overlay')==='off','C overlay dismisses only locally');
 check(new URL(page.url()).searchParams.get('enterprise')==='easyjet','C retains enterprise');await page.locator('.lens-toggle').focus();await page.keyboard.press('Space');check(await page.locator('.lens-canvas').getAttribute('data-overlay')==='on','C keyboard Space toggles lens');await page.keyboard.press('Tab');check(await page.locator(':focus').count()===1,'Keyboard focus remains addressable');await page.goBack();check(await page.locator('.lens-canvas').getAttribute('data-overlay')==='off','C Back restores preceding overlay state');
 const touch=await browser.newContext({viewport:sizes['ipad-portrait'],hasTouch:true}),tp=await touch.newPage();await tp.goto(url('a','easyjet'));await tp.locator('.compact-art summary').tap();check(await tp.locator('.compact-art').getAttribute('open')!==null,'Portrait touch opens Left');await tp.locator('.compact-art .scene-label').first().tap();check(await tp.locator('.compact-art').getAttribute('open')!==null,'Subject navigation retains open portrait context');await touch.close();
 await page.setViewportSize({width:390,height:844});
 for(const o of ['a','b','c']){
  await ready(url(o,'easyjet'));check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'Mobile reflow '+o);
  await page.evaluate(()=>{const es=[...document.querySelectorAll('#main *')],sizes=es.map(e=>parseFloat(getComputedStyle(e).fontSize));es.forEach((e,i)=>e.style.fontSize=(sizes[i]*2)+'px')});
  check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'200pct text '+o);await shot(o+'-easyjet-mobile-200pct');
 }
 await ready(cfg.base+'/view.html?option=a&enterprise=lloyds&workspace=private');check((await page.locator('main').innerText()).includes('unavailable'),'Unknown identity/workspace selectors rejected');
 check(requests.every(r=>r.startsWith(cfg.base)),'No external requests, source fetch or private service');
 // Comparison sheets are review artifacts, not a fourth product panel.
 for(const device of Object.keys(sizes)){
  const content=`<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;padding:28px;background:#f4f1e7;color:#173e33;font-family:system-ui}h1{font:40px Georgia}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.cell{border-top:1px solid #a4b39c;padding-top:10px}.cell img{width:100%;display:block}h2{font:23px Georgia;margin:8px 0}</style></head><body><h1>FLORA · Enterprise economics · ${device}</h1><p>Design only · A: Landscape / B: Operating model / C: Contextual lens · Lloyds is illustrative, figures withheld</p><div class="grid">${['lloyds','easyjet'].flatMap(e=>['a','b','c'].map(o=>`<section class="cell"><h2>${o.toUpperCase()} · ${e==='lloyds'?'Lloyds Banking Group':'easyJet'}</h2><img src="${o}-${e}-facts-${device}.jpg" alt="Option ${o} ${e} ${device}"></section>`)).join('')}</div></body></html>`;
  fs.writeFileSync(path.join(cfg.output,'comparison-'+device+'.html'),content);await page.setViewportSize({width:1800,height:1200});await page.goto(cfg.base+'/shots/comparison-'+device+'.html');await page.locator('img:visible').evaluateAll(es=>Promise.all(es.map(e=>e.decode())));await shot('comparison-'+device);
 }
 fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({passed:checks.length,checks,sizes,limits:'Static design only; no FLORA runtime, live authentication or physical-device certification'},null,2)+'\n');
 await browser.close();console.log(checks.length+' design browser checks passed');
})().catch(e=>{console.error(e);process.exit(1)});
