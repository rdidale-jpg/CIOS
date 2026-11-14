const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[];
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:780}};
function check(v,label){assert(v,label);checks.push(label)}
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 for(const [phase,server] of Object.entries(cfg.servers)){
  const after=phase==='after',context=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,hasTouch:true}),p=await context.newPage();
  await p.goto(server.base+'/auth/sign-in');await p.locator('[name=user_id]').fill('preview-strategic');await p.locator('[name=password]').fill(cfg.password);
  await Promise.all([p.waitForURL('**/auth/workspace'),p.getByRole('button',{name:'Sign in',exact:true}).click()]);await Promise.all([p.waitForURL('**/blueprint-import/history'),p.getByRole('button',{name:'Select workspace'}).click()]);
  const base='/flora/command-centre/opportunity-assurance';
  const routes=after?{overview:base+'?cutoff=2026-11-13',...Object.fromEntries(Object.entries(server.development).map(([key,id])=>[key,base+'?'+new URLSearchParams({offer:server.strategic.offers[{'digital':'tech-strategic-digital-transformation','legacy':'tech-strategic-complex-legacy-modernisation','ai':'tech-strategic-ai-first-transformation','cyber':'tech-strategic-cybersecurity-resilience','esg':'tech-strategic-social-value-esg'}[key]],enterprise:key==='digital'||key==='legacy'?'santander-uk':key==='cyber'?'computacenter':'lloyds',candidate:id,cutoff:'2026-11-13'})]))}:{development:'/flora/offers/development'};
  for(const [device,size] of Object.entries(sizes)){
   await p.setViewportSize(size);
   for(const [name,route] of Object.entries(routes)){
    check((await p.goto(server.base+route)).status()===200,phase+' '+device+' '+name+': authorised');await p.evaluate(()=>document.fonts.ready);
    check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),phase+' '+device+' '+name+': no horizontal overflow');
    check(await p.locator('h1').count()===1,phase+' '+device+' '+name+': one heading');check(await p.locator('nav[aria-label="Primary product navigation"]').count()===1,phase+' '+device+' '+name+': one header');
    if(after&&name!=='overview'){
     const main=await p.locator('main').innerText();check(main.includes('Qualification input completeness'),device+' '+name+': explicit denominator');check(main.includes('Independently verified buyer need: Not established'),device+' '+name+': no false buyer verification');
     if(name==='digital')check(main.includes('10/10 inputs · 100% input completeness'),device+': ten complete inputs are not accuracy');
     if(name==='esg')check(main.includes('Research only'),device+': ESG abstention');
     await p.locator('[name=challenge]').focus();check(await p.locator('[name=challenge]').evaluate(e=>e===document.activeElement),device+' '+name+': keyboard challenge selector');
    }
    await p.evaluate(()=>{document.activeElement?.blur();scrollTo(0,0)});await p.screenshot({path:path.join(cfg.output,device+'-'+name+'-'+phase+'.jpg'),type:'jpeg',quality:85,fullPage:true});
   }
  }
  if(after){
   await p.setViewportSize(sizes.desktop);await p.goto(server.base+routes.digital);
   await p.locator('[name=challenge]').selectOption('Withdraw source');await p.locator('[name=source]').selectOption('BTI-TSB-TRANSFER');
   await Promise.all([p.waitForNavigation(),p.getByRole('button',{name:'Compare without saving'}).click()]);
   check((await p.locator('main').innerText()).includes('Prioritise → Research only'),'Withdrawal weakens real matcher result');check((await p.locator('main').innerText()).includes('Existing Pipeline unchanged'),'Existing Pipeline is not edited');
   await p.screenshot({path:path.join(cfg.output,'desktop-withdrawal-challenge.jpg'),type:'jpeg',quality:85,fullPage:true});
   await p.locator('summary').filter({hasText:'Challenge conditions, blockers and affected dependencies'}).click();check((await p.locator('main').innerText()).includes('would_require_reassessment'),'Source drift reports actual dependency changes');
   await p.setViewportSize({width:1280,height:900});await p.goto(server.base+routes.digital);await p.locator('body').evaluate(e=>e.style.zoom='200%');check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'200% desktop zoom');await p.screenshot({path:path.join(cfg.output,'zoom-200-digital.jpg'),type:'jpeg',quality:85,fullPage:true});
   const data=JSON.parse(fs.readFileSync(path.join(cfg.output,'Assurance-Pilots.json'),'utf8'));check(data.samples.length===5&&data.samples.every(s=>s.reproduced),'Five pilot machine paths reproducible');
   await p.goto(server.base+'/flora/offers');check(!(await p.locator('main').innerText()).includes('Command Centre'),'Seller portfolio has no forensic navigation');
  }
  await context.close();
 }
 fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({fixture_only:true,javascript:false,passed:checks.length,checks,viewports:sizes},null,2)+'\n');console.log('Passed '+checks.length+' owner assurance browser checks');
}finally{await browser.close()}})().catch(e=>{console.error(e.message);process.exitCode=1});
