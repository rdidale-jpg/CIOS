const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[];
const check=(value,label)=>{assert(value,label);checks.push(label)};
const route='/enterprises/easyjet/preview';
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844}};
const href=(c='fleet-operations',s='landscape')=>cfg.base+route+'?stream='+s+'&capability='+c;
async function load(p,url,status=200){console.log('Load '+new URL(url).pathname+' '+new URL(url).search);const r=await p.goto(url,{waitUntil:'domcontentloaded',timeout:15000});check(r.status()===status,`HTTP ${status} ${new URL(url).pathname}`);await p.evaluate(()=>document.fonts.ready);await p.locator('img:visible').evaluateAll(es=>Promise.race([Promise.all(es.map(e=>e.decode().catch(()=>{}))),new Promise(resolve=>setTimeout(resolve,1500))]));}
async function shot(p,name,full=true){await p.screenshot({path:path.join(cfg.output,name+'.jpg'),fullPage:full,quality:85})}
async function selected(p,cap,stream='landscape'){
 await p.waitForFunction(({cap,stream})=>document.body.dataset.capability===cap&&document.body.dataset.stream===stream,{cap,stream});
 check(await p.locator('h1').innerText()===({'fleet-operations':'Fleet Operations','network-planning':'Network Planning','customer-service':'Customer Service'}[cap]),'Main capability '+cap+' '+stream);
 check((await p.locator('.airline-scene [aria-current]').getAttribute('id'))==='cap-'+cap,'Left selected '+cap+' '+stream);
 check(new URL(p.url()).searchParams.get('capability')===cap,'URL selection '+cap+' '+stream);
}
(async()=>{
 const options={headless:true};if(fs.existsSync('/usr/bin/chromium')) options.executablePath='/usr/bin/chromium';
 const browser=await chromium.launch(options);
 try{
 const context=await browser.newContext({hasTouch:true,reducedMotion:'reduce'}),p=await context.newPage();
 const failedAssets=[];p.on('response',r=>{if(r.url().includes('/assets/')&&r.status()>=400)failedAssets.push(r.url())});
 for(const[device,size]of Object.entries(sizes)){
  await p.setViewportSize(size);await load(p,cfg.baseline+'/enterprises/easyjet');await shot(p,'before-easyjet-'+device,false);
  for(const cap of ['fleet-operations','network-planning']){
   await load(p,href(cap));await selected(p,cap);
   check(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'no page overflow '+device+' '+cap);
   if(device!=='mobile'){const left=await p.locator('#left').boundingBox(),main=await p.locator('main').boundingBox();check(main.x>=left.x+left.width-1,'Left and Main actually side by side '+device+' '+cap);}
   check(await p.locator('[data-region]').count()===3,'exact Top Left Main '+device+' '+cap);
   check(await p.locator('main details').count()===0,'no nested intelligence expanders '+device+' '+cap);
   check(await p.locator('main a').count()===0,'no source workflow in Main '+device+' '+cap);
   check((await p.locator('main').innerText()).includes(cap==='fleet-operations'?'356 aircraft':'1,202 routes'),'historical fact visible '+device+' '+cap);
   await shot(p,'after-'+cap+'-'+device);
  }
  const scene=p.locator('.scene-control');if(await scene.getAttribute('open')===null)await scene.locator('summary').tap();
  await p.evaluate(()=>window.originalLeft=document.querySelector('#left'));
  await p.locator('#cap-fleet-operations').tap();await selected(p,'fleet-operations');
  check(await p.evaluate(()=>window.originalLeft===document.querySelector('#left')),'Left DOM persists touch '+device);
  if(await scene.getAttribute('open')===null)await scene.locator('summary').tap();
  await p.locator('#cap-network-planning').tap();await selected(p,'network-planning');
  const headingBox=await p.locator('h1').boundingBox();check(headingBox.y>=0&&headingBox.y< size.height,'selected Main heading visible '+device);
  await p.goBack();await selected(p,'fleet-operations');await p.goForward();await selected(p,'network-planning');
  await p.reload();await selected(p,'network-planning');
  for(const[stream,label]of [['forces','Forces'],['changing',"What's changing?"],['landscape','Landscape']]){
   await p.getByRole('link',{name:label,exact:true}).click();await selected(p,'network-planning',stream);
   check(new URL(p.url()).searchParams.get('capability')==='network-planning','lens retains capability '+device+' '+stream);
   if(device==='desktop')await shot(p,'after-network-'+stream+'-desktop');
  }
  if(device==='mobile'){await p.locator('.scene-control summary').tap();await shot(p,'after-mobile-operating-system');}
 }
 await p.setViewportSize(sizes.desktop);await load(p,href());
 await p.locator('#cap-network-planning').focus();await p.keyboard.press('Enter');await selected(p,'network-planning');
 check(await p.locator('h1').evaluate(e=>e===document.activeElement),'keyboard selection moves focus to Main');
 check((await p.locator('#preview-status').textContent()).includes('Network Planning'),'live selection announced');
 await p.locator('#cap-customer-service').focus();await p.keyboard.press('Enter');await selected(p,'customer-service');
 check((await p.locator('main').innerText()).includes('booking support'),'third differentiated capability');
 for(const cap of ['fleet-operations','customer-service'])for(const stream of ['forces','changing']){
  await load(p,href(cap,stream));await selected(p,cap,stream);await shot(p,'after-'+cap+'-'+stream+'-desktop');
 }
 await p.setViewportSize({width:320,height:900});await load(p,href('network-planning'));
 await p.evaluate(()=>{const nodes=[...document.querySelectorAll('body *')],sizes=nodes.map(e=>parseFloat(getComputedStyle(e).fontSize));nodes.forEach((e,i)=>e.style.setProperty('font-size',sizes[i]*2+'px','important'))});
 check(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'320px 200pct text no page overflow');await shot(p,'after-mobile-200pct');
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:sizes.desktop}),np=await nojs.newPage();
 await load(np,href());await np.locator('#cap-network-planning').click();check((await np.locator('h1').innerText())==='Network Planning','no-JS capability GET journey');
 await np.getByRole('link',{name:'Forces',exact:true}).click();check(new URL(np.url()).searchParams.get('capability')==='network-planning','no-JS lens preserves capability');await shot(np,'after-nojs-network-forces');await nojs.close();
 console.log('Lifecycle proof');
 const original=fs.readFileSync(cfg.source_package);try{
  for(const flag of ['withdrawn','stale']){
   const data=JSON.parse(original);data.sources.find(s=>s.id==='SRC-AV-CHAT26')[flag]=true;fs.writeFileSync(cfg.source_package,JSON.stringify(data));
   await load(p,href('network-planning','changing'));check(!(await p.locator('main').innerText()).includes('ChatGPT'),'actual source '+flag+' removes disclosure');
   await load(p,href());check((await p.locator('main').innerText()).includes('356 aircraft'),'unrelated FY25 fact survives '+flag);
  }
 }finally{fs.writeFileSync(cfg.source_package,original)}
 for(const suffix of ['?capability=private-record','?stream=inside','?source=private','?capability=network-planning&capability=fleet-operations']){
  const r=await context.request.get(cfg.base+route+suffix,{timeout:15000});check([403,404].includes(r.status()),'invalid or duplicate perimeter denied '+suffix);
 }
 for(const target of ['/financial-intelligence','/flora/offers','/sales-pipeline'])check([403,404].includes((await context.request.get(cfg.base+target,{timeout:15000})).status()),'Guest private denial '+target);
 for(const target of ['/industries/banking','/enterprises/lloyds','/industries/aviation','/enterprises/easyjet']){
  await load(p,cfg.base+target);check(!(await p.locator('body').innerText()).includes('Enterprise Twin · Preview'),'existing route not replaced '+target);
 }
 check(failedAssets.length===0,'all rendered artwork styles and interaction resources loaded');
 const asset=await context.request.get(cfg.base+route+'/assets/artwork',{method:'HEAD',timeout:15000});check(asset.status()===200&&asset.headers()['content-type'].includes('svg'),'HEAD asset content type');
 fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({passed:checks.length,checks,sizes,limitations:'Real local app HTTP; Chromium/touch emulation, not physical iPad or Safari. No live source acquisition, production account or data.'},null,2)+'\n');
 console.log(checks.length+' ET-VIS-2 browser checks passed');await context.close();
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
