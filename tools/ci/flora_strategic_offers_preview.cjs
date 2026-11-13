const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[];
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:780}};
function check(value,label){assert(value,label);checks.push(label);}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 async function login(server,user){
  const c=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,hasTouch:true}),p=await c.newPage();
  await p.goto(server.base+'/auth/sign-in');await p.locator('[name=user_id]').fill(user);await p.locator('[name=password]').fill(cfg.password);
  await Promise.all([p.waitForURL('**/auth/workspace'),p.getByRole('button',{name:'Sign in',exact:true}).click()]);
  await Promise.all([p.waitForURL('**/blueprint-import/history'),p.getByRole('button',{name:'Select workspace'}).click()]);return {c,p};
 }
 try{
  for(const [phase,server] of Object.entries(cfg.servers)){
   const after=phase==='after',actor=await login(server,after?'preview-strategic':'preview-seller'),p=actor.p;
   const routes={selection:'/flora/offers/start',portfolio:'/flora/offers',discovery:'/flora/offers/discover?mode=account&selected=lloyds'};
   if(after){routes.cyber='/flora/offers/edit?offer='+server.strategic.offers['tech-strategic-cybersecurity-resilience'];routes.esg='/flora/offers/edit?offer='+server.strategic.offers['tech-strategic-social-value-esg'];}
   for(const [device,size] of Object.entries(sizes)){
    await p.setViewportSize(size);
    for(const [name,route] of Object.entries(routes)){
     check((await p.goto(server.base+route)).status()===200,phase+' '+device+' '+name+': authorised');
     await p.evaluate(()=>document.fonts.ready);
     check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),phase+' '+device+' '+name+': no page overflow');
     check(await p.locator('h1').count()===1,phase+' '+device+' '+name+': one main heading');
     check(await p.locator('nav[aria-label="Primary product navigation"]').count()===1,phase+' '+device+' '+name+': one product navigation');
     check(await p.locator('.sources-menu').count()<=1,phase+' '+device+' '+name+': one optional source location');
     if(after){
      check(!/synthetic/i.test(await p.locator('body').innerText()),device+' '+name+': business example language');
      if(name==='selection'){
       const expected=['Enterprise Digital Transformation','AI-first Business Transformation','Enterprise Cybersecurity & Resilience','Complex Legacy Application Modernisation','Social Value & ESG Transformation'];
       check(JSON.stringify(await p.locator('.offer-grid>.offer-card h2').allTextContents()).startsWith(JSON.stringify(expected).slice(0,-1)),device+': five owner priorities first');
       const boxes=p.locator('input[name=templates]');check(await boxes.evaluateAll(es=>es.every(e=>!e.checked)),device+': no implied seller capabilities');
       check(await boxes.evaluateAll(es=>es.every(e=>e.getAttribute('aria-label').includes(e.closest('label').innerText.trim()))),device+': spoken names include visible labels');
       await boxes.first().focus();await p.keyboard.press('Space');check(await boxes.first().isChecked(),device+': keyboard Space selects native checkbox');await p.keyboard.press('Space');
       await p.getByText('Change business categories',{exact:true}).click();
       check(await p.locator('[name=primary] option:checked').innerText()==='Digital Transformation & Consulting',device+': customer-facing category with stable ID');
       await p.getByText('Delivery specialism (optional)',{exact:true}).click();check(await p.locator('[name=specialisms]').isChecked(),device+': explicit Systems Integration preference retained');
       await p.getByText('Change business categories',{exact:true}).click();
      }
      if(name==='portfolio')check(await p.locator('main .offer-grid').first().locator(':scope>.offer-card').count()===5,device+': five selected priority drafts');
      if(name==='discovery'){
       check(await p.locator('[data-assessment-id]').count()===5,device+': same-account five differentiated hypotheses');
       check(await p.getByText('Value to validate',{exact:true}).count()===5,device+': qualitative economic value visible');
       const esg=p.locator('article.pair').filter({has:p.getByRole('heading',{name:/Social Value & ESG/})});
       check((await esg.innerText()).includes('No account-specific indicator'),device+': ESG remains research without invented account evidence');
       check((await p.locator('main').innerText()).includes('no urgency inferred.'),device+': no buying urgency inferred');
      }
      if(name==='cyber'||name==='esg'){
       await p.getByText('See the sales playbook',{exact:true}).click();
       check(await p.getByRole('heading',{name:'Economic value to validate',exact:true}).isVisible(),device+' '+name+': complete economic method');
       check(await p.getByRole('heading',{name:'Conditional follow-on opportunities',exact:true}).isVisible(),device+' '+name+': gated follow-on opportunities');
       if(name==='esg')check((await p.locator('main').innerText()).includes('PPN 002 is not a universal UK'),device+': social-value jurisdiction boundary');
      }
     }
     await p.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0)});
     const capture={path:path.join(cfg.output,device+'-'+name+'-'+phase+'.jpg'),type:'jpeg',quality:86,fullPage:true};
     if(after&&(name==='cyber'||name==='esg')){capture.fullPage=false;capture.clip={x:0,y:0,width:size.width,height:Math.min(1900,await p.evaluate(()=>document.documentElement.scrollHeight))};}
     if(after&&name==='selection'){const last=await p.locator('.offer-grid>.offer-card').nth(4).boundingBox();capture.fullPage=false;capture.clip={x:0,y:0,width:size.width,height:Math.ceil(last.y+last.height+24)};}
     await p.screenshot(capture);
    }
   }
   if(after){
    await p.goto(server.base+'/flora/offers/start');await p.locator('input[name=templates]').first().check();await p.locator('[name=confirmed]').check();
    await Promise.all([p.waitForURL('**/flora/offers'),p.getByRole('button',{name:'Create my private example offers',exact:true}).click()]);
    check(await p.locator('main .offer-grid').first().locator(':scope>.offer-card').count()===5,'Actual CSRF-protected repeat adoption is idempotent');
    await p.getByRole('link',{name:'Continue to discovery',exact:true}).click();check(await p.locator('[data-assessment-id]').count()===15,'Offer-led discovery produces same five offers across three governed accounts');
    await p.goto(server.base+'/flora/offers/studio');check((await p.locator('main').innerText()).includes('disabled'),'Studio remains off');
   }
   await actor.c.close();
  }
  const samples=JSON.parse(fs.readFileSync(path.join(cfg.output,'Sample-Matches.json'),'utf8'));
  check(samples.samples.length===15&&samples.samples.every(r=>r.matching_modes_identical&&!r.pipeline_eligible&&r.economics===null),'Fifteen identical-mode unvalued matches; no Pipeline eligibility');
  check(samples.samples.filter(r=>r.library_id==='tech-strategic-social-value-esg').every(r=>r.posture==='research'),'No fabricated ESG demand across all account examples');
  fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({fixture:'Isolated example seller; no real company capability, buyer intent or production data',javascript:false,checks,passed:checks.length,viewports:sizes},null,2)+'\n');console.log('Passed '+checks.length+' strategic-priority browser checks');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
