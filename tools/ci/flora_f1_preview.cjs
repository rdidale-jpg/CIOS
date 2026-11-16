const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[],errors=[];
const sizes={desktop:{width:1440,height:900},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:740}};
const check=(v,s)=>{assert(v,s);checks.push(s)};
(async()=>{const browser=await chromium.launch({executablePath:process.env.VP2_CHROMIUM||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),args:['--no-sandbox']});try{
 const anonymous=await browser.newContext({ignoreHTTPSErrors:true});
 check((await anonymous.request.get(cfg.base+'/ai-financial-report/'+cfg.run_id)).status()===403,'anonymous run denied');await anonymous.close();
 const owner=await browser.newContext({ignoreHTTPSErrors:true,hasTouch:true}),p=await owner.newPage();p.on('pageerror',e=>errors.push(e.message));
 await p.goto(cfg.base+'/auth/sign-in');await p.locator('input[name=user_id]').fill('preview-owner');await p.locator('input[name=password]').fill(cfg.password);await p.getByRole('button',{name:'Sign in',exact:true}).click();
 if(new URL(p.url()).pathname==='/auth/workspace'){await p.locator('select[name=workspace_id]').selectOption('preview-workspace');await p.getByRole('button',{name:'Select workspace',exact:true}).click()}
 const run='/ai-financial-report/'+cfg.run_id;
 for(const[device,size]of Object.entries(sizes)){
  if(cfg.baseline&&device!=='mobile-320'){await p.setViewportSize(size);const before=await p.goto(cfg.baseline+run);check(before.status()===200,device+' baseline old reader');check(!(await p.locator('body').innerText()).includes('1,884,726'),device+' old reader has no typed analytical result');await p.screenshot({path:path.join(cfg.output,'before-'+device+'.jpg'),fullPage:true,quality:80})}
  await p.setViewportSize(size);const response=await p.goto(cfg.base+run);check(response.status()===200,device+' authorised result');
  check(await p.getByRole('heading',{name:'UK household retail-deposit stocks',exact:true}).count()===1,device+' source scoped title');
  const body=await p.locator('body').innerText();check(body.includes('1,884,726')&&body.includes('1,886,281')&&body.includes('1,555 GBP millions')&&body.includes('0.0825%'),device+' real values units derivation');
  check(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),device+' no horizontal overflow');
  const details=p.locator('details').filter({has:p.locator('summary', {hasText:'Sources and calculation'})});await details.locator('summary').focus();await p.keyboard.press('Enter');check(await details.evaluate(e=>e.open),device+' keyboard source disclosure');await details.locator('summary').tap();check(!await details.evaluate(e=>e.open),device+' touch collapse');await details.locator('summary').tap();check(await details.evaluate(e=>e.open),device+' touch disclosure');
  check(await details.getByRole('link',{name:'Licence',exact:true}).count()===1,device+' licence on demand');
  await p.screenshot({path:path.join(cfg.output,'after-'+device+'.jpg'),fullPage:true,quality:80});
  if(device==='mobile'){await p.evaluate(()=>{const es=[...document.querySelectorAll('body *')],sizes=es.map(e=>parseFloat(getComputedStyle(e).fontSize));es.forEach((e,i)=>e.style.setProperty('font-size',sizes[i]*2+'px','important'))});await p.screenshot({path:path.join(cfg.output,'after-mobile-200pct.jpg'),fullPage:true,quality:80});check(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'200pct mobile text no overflow');check(await p.locator('.f1-result tbody th').evaluateAll(es=>es.every(e=>{const r=document.createRange();r.selectNodeContents(e);return r.getClientRects().length===1})),'200pct amounts remain on one line')}
 }
 // All seven accepted visual streams still render in the real application.
 for(const[scope,route,streams]of [['uk','/',['landscape','forces']],['banking','/industries/banking',['landscape','forces']],['lloyds','/enterprises/lloyds',['inside','landscape','forces']]]){
  await p.setViewportSize(sizes.desktop);
  for(const stream of streams){const r=await p.goto(cfg.base+route+'?stream='+stream);check(r.status()===200,scope+' '+stream+' remains available ('+r.status()+')');check(await p.locator('body>[data-region]').count()===3,scope+' '+stream+' VP2 regions retained')}
 }
 await p.goto(cfg.base+'/');await p.locator('.wide-scene [data-research=banking]').click();check(new URL(p.url()).pathname==='/industries/banking','UK Banking first selection');await p.locator('.wide-scene .portrait [data-label-id=lloyds]').click();check(new URL(p.url()).pathname==='/enterprises/lloyds','Lloyds second selection');
 await p.goto(cfg.base+run);await p.goBack();check(new URL(p.url()).pathname==='/enterprises/lloyds','Back restores journey');await p.goForward();check(new URL(p.url()).pathname===run,'Forward restores analytical deep link');
 check(errors.length===0,'no browser script errors');fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({checks,passed:checks.length,errors,sizes,limitations:'Loopback Chromium and emulated touch/tablet sizes; synthetic authority, real source numbers; not production or physical Safari/screen-reader certification.'},null,2)+'\n');console.log(checks.length+' F1 browser checks passed');await owner.close();
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
