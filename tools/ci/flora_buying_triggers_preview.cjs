const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[];
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:780}};
const base='/flora/offers';
function check(value,label){assert(value,label);checks.push(label);}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  for(const [phase,server] of Object.entries(cfg.servers)){
   const after=phase==='after',context=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,hasTouch:true}),p=await context.newPage();
   await p.goto(server.base+'/auth/sign-in');await p.locator('[name=user_id]').fill('preview-strategic');await p.locator('[name=password]').fill(cfg.password);
   await Promise.all([p.waitForURL('**/auth/workspace'),p.getByRole('button',{name:'Sign in',exact:true}).click()]);
   await Promise.all([p.waitForURL('**/blueprint-import/history'),p.getByRole('button',{name:'Select workspace'}).click()]);
   const ids=server.strategic.offers,digital=ids['tech-strategic-digital-transformation'],legacy=ids['tech-strategic-complex-legacy-modernisation'],ai=ids['tech-strategic-ai-first-transformation'],cyber=ids['tech-strategic-cybersecurity-resilience'],esg=ids['tech-strategic-social-value-esg'];
   const routes=after?{
    shortlist:base+'/triggers?selected='+digital,
    account:base+'/triggers?mode=account&selected=lloyds',
    legacy:base+'/trigger-detail?offer='+legacy+'&enterprise=santander-uk',
    ai:base+'/trigger-detail?offer='+ai+'&enterprise=lloyds',
    cyber:base+'/trigger-detail?offer='+cyber+'&enterprise=lloyds',
    esg:base+'/triggers?selected='+esg,
    santander:base+'/trigger-detail?offer='+digital+'&enterprise=santander-uk',
    lloyds:base+'/trigger-detail?offer='+digital+'&enterprise=lloyds',
    computacenter:base+'/trigger-detail?offer='+digital+'&enterprise=computacenter',
    'cc-legacy':base+'/trigger-detail?offer='+legacy+'&enterprise=computacenter',
    'cc-cyber':base+'/trigger-detail?offer='+cyber+'&enterprise=computacenter',
    bt:base+'/trigger-detail?offer='+digital+'&enterprise=bt',
    natwest:base+'/trigger-detail?offer='+digital+'&enterprise=natwest'
   }:{discovery:base+'/discover?mode=offer&selected='+digital,portfolio:base};
   for(const [device,size] of Object.entries(sizes)){
    await p.setViewportSize(size);
    for(const [name,route] of Object.entries(routes)){
     check((await p.goto(server.base+route)).status()===200,phase+' '+device+' '+name+': authorised');
     await p.evaluate(()=>document.fonts.ready);
     check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),phase+' '+device+' '+name+': no page overflow');
     check(await p.locator('h1').count()===1,phase+' '+device+' '+name+': one main heading');
     check(await p.locator('nav[aria-label="Primary product navigation"]').count()===1,phase+' '+device+' '+name+': one compact product navigation');
     check(await p.locator('.sources-menu').count()<=1,phase+' '+device+' '+name+': one optional source location');
     if(after){
      check(!/synthetic/i.test(await p.locator('body').innerText()),device+' '+name+': business language');
      if(['shortlist','account','esg'].includes(name)){
       const rows=p.locator('.trigger-row');check(await rows.count()===(name==='account'?5:10),device+' '+name+': bounded permitted candidates');
       check(await rows.evaluateAll(es=>es.every(e=>e.querySelectorAll('a').length===1)),device+' '+name+': one primary action per row');
       await rows.first().locator('a').focus();check(await rows.first().locator('a').evaluate(e=>e===document.activeElement),device+' '+name+': native keyboard focus');
       if(name==='shortlist'){check((await rows.first().innerText()).includes('Santander UK'),device+': linked dated integration/plan ranks first');check(await rows.locator('[data-tier="Prioritise"]').count()===0,'Tier is a row attribute, not an invented score');}
       if(name==='esg')check(await rows.evaluateAll(es=>es.every(e=>e.dataset.tier==='Research only')),device+': ESG does not auto-match policy or rhetoric');
      }else{
       check((await p.locator('main').innerText()).includes('The deciding question'),device+' '+name+': one primary disconfirming question');
       check(await p.getByRole('heading',{name:'Reported timeline',exact:true}).count()===1,device+' '+name+': dated timeline');
       if(name!=='cyber')check((await p.locator('main').innerText()).includes('Stop condition:'),device+' '+name+': bounded enterprise diagnostic and stop condition');
       if(name==='legacy'){check((await p.locator('main').innerText()).includes('2026-11-10'),device+': real reported catalyst date');check((await p.locator('main').innerText()).includes('conditional'),device+': planned migration remains conditional');}
       if(name==='cyber')check((await p.locator('main').innerText()).includes('Envoy'),device+': existing controls remain counter-evidence');
       await p.locator('.sources-menu>summary').click();check((await p.locator('.source-sheet').innerText()).includes('Retained excerpt'),device+' '+name+': original source passages on demand');await p.locator('.sources-menu>summary').click();
      }
     }
     await p.evaluate(()=>{document.activeElement?.blur();scrollTo(0,0)});
     const capture={path:path.join(cfg.output,device+'-'+name+'-'+phase+'.jpg'),type:'jpeg',quality:86,fullPage:true};
     if(after&&['shortlist','account','esg'].includes(name)){
      const box=await p.locator('.trigger-row').nth(name==='account'?4:5).boundingBox();capture.fullPage=false;capture.clip={x:0,y:0,width:size.width,height:Math.ceil(box.y+box.height+24)};
     }
     await p.screenshot(capture);
    }
   }
   if(after){
    await p.goto(server.base+base+'/triggers?selected='+digital);
    await p.getByText('Save a private reviewed shortlist',{exact:true}).click();
    const checkboxes=p.locator('[name=assessment_ids]');await checkboxes.nth(0).check();await checkboxes.nth(1).check();
    await p.locator('[name=note]').fill('Example owner-reviewed research candidates; no buying intent confirmed.');await p.locator('[name=confirmed]').check();
    const entries=await p.locator('form[action="/flora/offers/shortlist-save"]').evaluate(f=>[...new FormData(f).entries()]);
    await Promise.all([p.waitForURL('**/flora/offers/shortlists?*'),p.getByRole('button',{name:'Save reviewed shortlist',exact:true}).click()]);
    check((await p.locator('main').innerText()).includes('Reviewed shortlist · v1'),'Deliberate actor-reviewed snapshot saved');
    check((await p.locator('main').innerText()).includes('no buying intent confirmed'),'Private note remains separate from facts');
    const replay=await context.request.post(server.base+base+'/shortlist-save',{data:new URLSearchParams(entries).toString(),headers:{Origin:server.base,'Content-Type':'application/x-www-form-urlencoded'}});
    check(replay.status()===403,'Stale review replay denied without a duplicate snapshot');
    for(const [device,size] of Object.entries(sizes)){await p.setViewportSize(size);await p.screenshot({path:path.join(cfg.output,device+'-reviewed-after.jpg'),type:'jpeg',quality:86,fullPage:true});}
    await p.goto(server.base+base+'/studio');check((await p.locator('main').innerText()).includes('disabled'),'Studio remains disabled');
   }
   await context.close();
  }
  const data=JSON.parse(fs.readFileSync(path.join(cfg.output,'Assessment-Matrix.json'),'utf8'));
  check(data.samples.length===50&&data.samples.every(r=>r.both_modes_identical&&r.economics===null&&!r.pipeline_eligible),'Fifty source-backed assessments; same matcher, no values or Pipeline eligibility');
  const tailored=data.samples.filter(r=>r.entry_play_detail);
  check(tailored.length===10&&new Set(tailored.map(r=>r.entry_play_detail.diagnostic)).size===10,'Ten distinct evidence-linked diagnostics for supported pairs');
  check(data.samples.filter(r=>r.tier==='Research only').every(r=>!r.entry_play_detail&&r.entry_play.includes('No programme diagnostic is recommended')),'Research-only cases do not become diagnostic mandates');
  check(data.samples.filter(r=>r.offer_id==='tech-strategic-social-value-esg').every(r=>r.tier==='Research only'),'All ESG unknowns retained; no manufactured positive case');
  fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({fixture:'Local example seller and explicit fixture approvals; no real company capability or live opportunity asserted',javascript:false,passed:checks.length,checks,viewports:sizes},null,2)+'\n');console.log('Passed '+checks.length+' buying-trigger browser checks');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
