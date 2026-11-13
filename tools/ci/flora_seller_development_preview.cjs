const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[];
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:780}};
function check(v,label){assert(v,label);checks.push(label)}
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});try{
 for(const [phase,server] of Object.entries(cfg.servers)){
  const after=phase==='after',context=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,hasTouch:true}),p=await context.newPage();
  await p.goto(server.base+'/auth/sign-in');await p.locator('[name=user_id]').fill('preview-strategic');await p.locator('[name=password]').fill(cfg.password);
  await Promise.all([p.waitForURL('**/auth/workspace'),p.getByRole('button',{name:'Sign in',exact:true}).click()]);
  await Promise.all([p.waitForURL('**/blueprint-import/history'),p.getByRole('button',{name:'Select workspace'}).click()]);
  const routes=after?{list:'/flora/offers/development',...Object.fromEntries(Object.entries(server.development).map(([key,id])=>[key,'/flora/offers/development?candidate='+id]))}:{discovery:'/flora/offers/triggers?selected='+server.strategic.offers['tech-strategic-digital-transformation']};
  for(const [device,size] of Object.entries(sizes)){
   await p.setViewportSize(size);
   for(const [name,route] of Object.entries(routes)){
    check((await p.goto(server.base+route)).status()===200,phase+' '+device+' '+name+': scoped read');
    await p.evaluate(()=>document.fonts.ready);
    check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),phase+' '+device+' '+name+': no horizontal overflow');
    check(await p.locator('h1').count()===1,phase+' '+device+' '+name+': one heading');
    check(await p.locator('nav[aria-label="Primary product navigation"]').count()===1,phase+' '+device+' '+name+': one header');
    if(after&&name!=='list'){
     check((await p.locator('main').innerText()).includes('First conversation'),device+' '+name+': conversation foreground');
     check(await p.locator('button').filter({hasText:'Create reviewed Pipeline entry'}).count()===0,device+' '+name+': no premature Pipeline action');
     check(await p.locator('label').count()>0,device+' '+name+': native labelled controls');
     await p.locator('[name=challenge]').focus();check(await p.locator('[name=challenge]').evaluate(e=>e===document.activeElement),device+' '+name+': keyboard focus');
     if(name==='esg')check((await p.locator('main').innerText()).includes('No programme diagnostic is recommended'),device+': ESG abstention retained');
     if(name==='cyber')check((await p.locator('main').innerText()).includes('framework'),device+': existing security programme retained');
    }
    await p.evaluate(()=>{document.activeElement?.blur();scrollTo(0,0)});
    await p.screenshot({path:path.join(cfg.output,device+'-'+name+'-'+phase+'.jpg'),type:'jpeg',quality:85,fullPage:true});
   }
  }
  if(after){
   await p.goto(server.base+routes.digital);
   const saveForm=p.locator('form[action="/flora/offers/development-save"]');
   const captured=await saveForm.evaluate(f=>[...new FormData(f).entries()]);
   const bad=await context.request.post(server.base+'/flora/offers/development-save',{data:new URLSearchParams(captured).toString(),headers:{Origin:'https://foreign.example','Content-Type':'application/x-www-form-urlencoded'}});check(bad.status()===403,'Foreign Origin development write denied');
   await p.getByText('Proof, competition and commercial assumptions',{exact:true}).click();await p.getByText('Customer validation and qualification',{exact:true}).click();
   await p.locator('[name=challenge]').fill('Example fixture customer reports an unresolved migration journey ownership decision; no real customer claim.');
   await p.locator('[name=next_action]').fill('Example seller owner to review the customer-approved journey map with the programme function; fixture only.');
   await p.locator('[name=proof]').fill('Example separate employer delivery and rights review, fixture only');
   await p.locator('[name=alternatives]').fill('Example internal integration plan reviewed; confirm residual journey gap, fixture only');
   for(const key of ['problem','priority','buyer','funding','decision','competition','differentiation','timing','relationship','next_action']){
    await p.locator('[name=q_'+key+'_note]').fill('Example fixture '+key+' evidence recorded in a permitted illustrative customer discussion.');
    await p.locator('[name=q_'+key+'_source]').fill('Private example meeting/reference '+key);
    await p.locator('[name=q_'+key+'_kind]').selectOption(['competition','differentiation'].includes(key)?'Seller review':'Customer statement');
    await p.locator('[name=q_'+key+'_date]').fill('2026-11-13');
   }
   await p.locator('[name=state]').selectOption('Validate');await p.locator('[name=customer_attested]').check();await p.locator('[name=reviewed]').check();
   await Promise.all([p.waitForNavigation(),p.getByRole('button',{name:'Save development',exact:true}).click()]);
   check((await p.locator('main').innerText()).includes('Validate'),'Explicit customer-reported validation saved');
   for(const step of ['Create Preference','Qualify']){
    await p.getByText('Customer validation and qualification',{exact:true}).click();await p.locator('[name=customer_attested]').check();await p.locator('[name=reviewed]').check();await p.locator('[name=state]').selectOption(step);
    await Promise.all([p.waitForNavigation(),p.getByRole('button',{name:'Save development',exact:true}).click()]);
    check((await p.locator('main').innerText()).includes(step),'Seller explicitly selected '+step);
   }
   for(const [device,size] of Object.entries(sizes)){await p.setViewportSize(size);await p.screenshot({path:path.join(cfg.output,device+'-qualified-review.jpg'),type:'jpeg',quality:85,fullPage:true})}
   const handoff=p.locator('form[action="/flora/offers/development-handoff"]');const payload=await handoff.evaluate(f=>[...new FormData(f).entries()]);
   await handoff.locator('[name=confirmed]').check();
   const replayPayload=await handoff.evaluate(f=>[...new FormData(f).entries()]);
   await Promise.all([p.waitForURL('**/flora/sales/opp-*'),handoff.getByRole('button',{name:'Create reviewed Pipeline entry',exact:true}).click()]);
   check((await p.locator('main').innerText()).includes('Qualified'),'Only explicit reviewed handoff enters Pipeline');
   const replay=await context.request.post(server.base+'/flora/offers/development-handoff',{data:new URLSearchParams(replayPayload).toString(),headers:{Origin:server.base,'Content-Type':'application/x-www-form-urlencoded'},maxRedirects:0});check(replay.status()===303,'Same authorised handoff replay is idempotent');
   for(const [device,size] of Object.entries(sizes)){await p.setViewportSize(size);await p.screenshot({path:path.join(cfg.output,device+'-pipeline-handoff.jpg'),type:'jpeg',quality:85,fullPage:true})}
   await p.setViewportSize({width:1280,height:900});await p.goto(server.base+routes.ai);await p.locator('body').evaluate(e=>e.style.zoom='200%');check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'200 percent zoom remains readable without horizontal page overflow');await p.screenshot({path:path.join(cfg.output,'zoom-200-ai.jpg'),type:'jpeg',quality:85,fullPage:true});
   await p.goto(server.base+'/flora/offers/studio');check((await p.locator('main').innerText()).includes('disabled'),'Creative Studio default-off');
  }
  await context.close();
 }
 fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({fixture_only:true,javascript:false,passed:checks.length,checks,viewports:sizes},null,2)+'\n');console.log('Passed '+checks.length+' Sprint C browser checks');
}finally{await browser.close()}})().catch(e=>{console.error(e.message);process.exitCode=1});
