const {chromium}=require('playwright'), fs=require('fs'), path=require('path'), assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')), checks=[];
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844}};
const route='/enterprises/lloyds?stream=landscape&detail=lending-income';
function check(value,label){assert(value,label);checks.push(label)}
function shipping(){return JSON.parse(fs.readFileSync(cfg.source,'utf8'))}
function save(s){fs.writeFileSync(cfg.source,JSON.stringify(s))}
function resolve(s){s.rights.contract_restriction_found=false;Object.assign(s.rights.material_exceptions[0],{status:'resolved_for_factual_method',resolved_by:'ISOLATED TEST ONLY',resolved_on:'2026-11-19',basis:'ISOLATED test double; no live legal clearance'});return s}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.VP2_CHROMIUM||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),args:['--no-sandbox']});
 const original=shipping();
 try{
  const ctx=await browser.newContext(),page=await ctx.newPage();
  async function load(url=route){const r=await page.goto(cfg.base+url);check(r.status()===200,'HTTP200 '+url);check(r.headers()['cache-control']==='no-store','no-store '+url);await page.locator('img:visible').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));return page.locator('main').innerText()}
  async function shot(name){await page.screenshot({path:path.join(cfg.output,name+'.jpg'),fullPage:true,quality:82})}
  for(const [device,size]of Object.entries(sizes)){
   await page.setViewportSize(size);save(original);let text=await load();
   check(!text.includes('£11.084bn'),'pending Source output absent '+device);await shot('shipping-pending-'+device);
   save(resolve(structuredClone(original)));text=await load();
   check(['£11.084bn','3.21%','£477.5bn'].every(s=>text.includes(s)),'three reported scoped facts '+device);
   check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'responsive '+device);
   check(await page.locator('.public-financial-facts details').count()===0,'no research expanders '+device);
   check((await page.locator('.public-financial-facts a').getAttribute('href'))==='https://www.lloydsbankinggroup.com/','homepage attribution '+device);
   check(!(await page.content()).includes(original.url),'no direct PDF locator '+device);
   await shot('isolated-resolved-facts-'+device);
   text=await load(route+'&reading=insight');let labels=await page.locator('.public-financial-facts .eyebrow').allTextContents();check(labels.includes('FLORA Insight')&&labels.includes('Reported'),'reported facts distinct from analysis '+device);await shot('isolated-resolved-insight-'+device);
   await page.goBack();check(new URL(page.url()).searchParams.get('detail')==='lending-income','Back retains component '+device);
   await page.goForward();check(new URL(page.url()).searchParams.get('reading')==='insight','Forward retains reading '+device);
   await page.keyboard.press('Tab');check(await page.locator(':focus').count()===1,'keyboard focus '+device);
   await page.emulateMedia({media:'print'});let denied=shipping();denied.withdrawn=true;save(denied);text=await load();
   check(!['£11.084bn','3.21%','£477.5bn'].some(s=>text.includes(s)),'withdrawal removes print/DOM/current output '+device);
   check(await page.locator('#public-financial-title').count()===0,'withdrawal removes accessibility target '+device);
   await page.emulateMedia({media:'screen'});
  }
  save(resolve(structuredClone(original)));await page.setViewportSize(sizes.mobile);await load();
  await page.evaluate(()=>{const es=[...document.querySelectorAll('main *')],sizes=es.map(el=>parseFloat(getComputedStyle(el).fontSize));es.forEach((el,i)=>el.style.setProperty('font-size',(sizes[i]*2)+'px','important'))});
  check(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'mobile 200pct text');await shot('isolated-resolved-mobile-200pct');
  const result={passed:checks.length,checks,sizes,limits:'Real loopback application/Chromium; emulated devices; positive Source resolution is an isolated double, not live approval. Already downloaded documents/screenshots cannot be remotely recalled.'};
  fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify(result,null,2)+'\n');console.log(checks.length+' public financial browser checks passed');await ctx.close();
 }finally{save(original);await browser.close()}
})().catch(e=>{console.error(String(e.message));process.exit(1)});
