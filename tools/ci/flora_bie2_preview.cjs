// Actual isolated VP-2 runtime: BIE-2 numerical release, no production service.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[],errors=[];
const sizes={desktop:{width:1440,height:900},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844}};
function check(v,label){assert(v,label);checks.push(label)}
async function load(p,base,url){const r=await p.goto(base+url);check(r.status()===200,'HTTP200 '+url);await p.evaluate(()=>document.fonts.ready);await p.locator('img:visible').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))))}
async function layout(p,label){check(await p.locator('body>[data-region]').count()===3,label+' three regions');check(await p.locator('h1').count()===1,label+' one h1');check(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),label+' no overflow');check(await p.locator('.stream-switcher [aria-current]').count()===1,label+' one active stream');}
async function shot(p,name){await p.screenshot({path:path.join(cfg.output,name+'.jpg'),fullPage:true,quality:78})}
(async()=>{const browser=await chromium.launch({headless:true,executablePath:fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined});try{
 for(const [size,viewport]of Object.entries(sizes)){
  const context=await browser.newContext({ignoreHTTPSErrors:true,viewport,hasTouch:size!=='desktop'}),p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
  if(cfg.baseline){await load(p,cfg.baseline,'/industries/banking');await layout(p,'before '+size);check(await p.locator('[data-intelligence=service-landscape]').count()===0,'baseline no new peer release '+size);await shot(p,'before-'+size+'-banking');}
  await load(p,cfg.base,'/industries/banking');await layout(p,'after '+size);await shot(p,'after-'+size+'-banking');
  check(await p.locator('[data-intelligence=service-landscape]').count()===1,'single Main pilot '+size);
  await p.getByRole('link',{name:'Forces',exact:true}).click();await layout(p,'Forces '+size);check(new URL(p.url()).searchParams.get('stream')==='forces','existing Forces '+size);await shot(p,'after-'+size+'-banking-forces');
  await load(p,cfg.base,'/industries/banking?agenda=service-landscape&selected=lloyds&layer=regulators');
  await layout(p,'agenda '+size);await shot(p,'after-'+size+'-peer-agenda');
  const text=await p.locator('#agenda-insight').innerText();for(const token of ['90,678','79,323','92,548','January–June 2026','not a service-quality ranking'])check(text.includes(token),'default clarity '+size+' '+token);
  check(await p.locator('main a[href^="https:"]').count()<=1,'only separated legal attribution link '+size);
  check(await p.locator('main details').count()===0,'ordinary agenda has no research expanders '+size);
  for(const stream of ['landscape','forces']){await p.getByRole('link',{name:stream[0].toUpperCase()+stream.slice(1),exact:true}).click();const u=new URL(p.url());check(u.searchParams.get('agenda')==='service-landscape'&&u.searchParams.get('selected')==='lloyds'&&u.searchParams.get('layer')==='regulators','scope subject layer agenda retained '+size+' '+stream)}
  await p.goBack();check(new URL(p.url()).searchParams.get('agenda')==='service-landscape','Back '+size);await p.goForward();check(new URL(p.url()).searchParams.get('agenda')==='service-landscape','Forward '+size);
  await load(p,cfg.base,'/');const scene=size==='mobile'||size==='ipad-portrait'?'.compact-scene':'.wide-scene';
  if(scene==='.compact-scene'){await p.locator(scene+'>summary').tap();check(await p.locator(scene).evaluate(e=>e.open),'touch UK scene '+size)}
  await p.locator(scene+' [data-research=banking]').click();
  if(scene==='.compact-scene')await p.locator(scene+'>summary').tap();
  await p.locator(scene+' [data-label-id=lloyds]').click();check(new URL(p.url()).pathname==='/enterprises/lloyds','UK Banking Lloyds two selections '+size);
  for(const [route,streams]of [['/',['landscape','forces']],['/industries/banking',['landscape','forces']],['/enterprises/lloyds',['inside','landscape','forces']]])for(const stream of streams){await load(p,cfg.base,route+'?stream='+stream);await layout(p,size+' '+route+' '+stream)}
  const html=await p.content();check(!['actor:','Banking-Corpus','ADR-027','next_investigation_owner_only'].some(t=>html.includes(t))&&!/\bgap:/i.test(await p.locator('main').innerText()),'no research administration '+size);
  await context.close();
 }
 const context=await browser.newContext({ignoreHTTPSErrors:true,viewport:sizes.desktop}),p=await context.newPage();
 for(const target of ['/docs/flora-runtime/bie2/Enterprise-Dossiers.json','/docs/flora-runtime/bie2/News-Candidates.json','/visual-streams/assets/BIE2-FCA-Peers-Candidate','/industries/banking?agenda=service-landscape&workspace=foreign','/enterprises/lloyds?agenda=service-landscape','/?agenda=service-landscape']){const r=await p.request.get(cfg.base+target);check([403,404].includes(r.status()),'research and context isolation '+target)}
 await load(p,cfg.base,'/industries/banking?agenda=service-landscape');fs.writeFileSync(path.join(cfg.output,'Peer-Agenda-Accessibility.yml'),await p.locator('body').ariaSnapshot());
 await p.setViewportSize({width:320,height:812});await layout(p,'320px');await p.emulateMedia({forcedColors:'active'});await layout(p,'forced colours');await p.emulateMedia({forcedColors:'none'});await p.evaluate(()=>document.documentElement.style.zoom='200%');await layout(p,'200percent zoom');
 check(errors.length===0,'no browser script errors');await context.close();
 fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({passed:checks.length,checks,errors,sizes,baseline:'b5b05f841bc6f17f5ffe3286a65e8745e7c79ec3',limitations:'Actual app with isolated fixture only; Chromium desktop and emulated iPad/mobile touch. No physical Safari, screen-reader certification or production identity proof.'},null,2)+'\n');console.log(checks.length+' BIE-2 browser checks passed');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
