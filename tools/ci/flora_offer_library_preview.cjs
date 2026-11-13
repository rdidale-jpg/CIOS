const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[],metrics={};
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:780}};
function check(v,label){assert(v,label);checks.push(label);}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 try{
  for(const [phase,server] of Object.entries(cfg.servers)){
   const context=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,hasTouch:true}),p=await context.newPage();
   await p.goto(server.base+'/auth/sign-in');await p.locator('[name=user_id]').fill('preview-seller');await p.locator('[name=password]').fill(cfg.password);
   await Promise.all([p.waitForURL('**/auth/workspace'),p.getByRole('button',{name:'Sign in',exact:true}).click()]);
   await Promise.all([p.waitForURL('**/blueprint-import/history'),p.getByRole('button',{name:'Select workspace'}).click()]);
   const routes=phase==='before'?{portfolio:'/flora/offers',discovery:'/flora/offers/discover?mode=account&selected=lloyds'}:{selection:'/flora/offers/start',portfolio:'/flora/offers',playbook:'/flora/offers/edit?offer='+server.pilots.si.offer_id,discovery:'/flora/offers/discover?mode=account&selected=lloyds'};
   for(const [device,size] of Object.entries(sizes)){
    await p.setViewportSize(size);
    for(const [name,route] of Object.entries(routes)){
     check((await p.goto(server.base+route)).status()===200,phase+' '+device+' '+name+': authorised page');
     await p.evaluate(()=>document.fonts.ready);
     check(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),phase+' '+device+' '+name+': no overflow');
     check(await p.locator('h1').count()===1,phase+' '+device+' '+name+': one heading');
     check(await p.locator('nav[aria-label="Primary product navigation"]').count()===1,phase+' '+device+' '+name+': one product header');
     check(await p.locator('.sources-menu').count()<=1,phase+' '+device+' '+name+': one optional source location');
     if(phase==='after')check(!/synthetic/i.test(await p.locator('body').innerText()),device+' '+name+': business example language');
     if(phase==='after'&&name==='selection'){
      const boxes=p.locator('input[name=templates]');check(await boxes.count()>=3,device+': relevant suggestions');
      check(await boxes.evaluateAll(es=>es.every(e=>!e.checked)),device+': no prechecked seller capability claims');
      check(await boxes.evaluateAll(es=>es.every(e=>e.getAttribute('aria-label').includes(e.closest('label').innerText.trim()))),device+': spoken checkbox name includes its visible label');
      await boxes.first().focus();check(await boxes.first().evaluate(e=>e===document.activeElement),device+': native keyboard selection');
      check(await p.locator('[name=confirmed]').count()===1,device+': seller confirmation required');
      await p.locator('.offer-card details').first().locator('summary').click();
      check((await p.locator('main').innerText()).includes('Buying events to verify'),device+': full playbook disclosure');
      await p.locator('.offer-card details').first().locator('summary').click();
     }
     if(phase==='after'&&name==='portfolio'){
      check(await p.locator('.offer-card').count()>=3,device+': three illustrative offers');
      check((await p.locator('main').innerText()).includes('When to explore'),device+': trigger highlights');
      check(await p.getByRole('link',{name:'Continue to discovery',exact:true}).count()===1,device+': one portfolio continuation');
     }
     if(phase==='after'&&name==='discovery'){
      check(await p.locator('[data-assessment-id]').count()===3,device+': three conservative account-led results');
      check((await p.locator('main').innerText()).includes('no urgency inferred.'),device+': no manufactured urgency');
      check(await p.getByText('Another way to start · compare the alternative',{exact:true}).count()===3,device+': second entry plays available');
     }
     await p.evaluate(()=>document.activeElement?.blur());
     await p.screenshot({path:path.join(cfg.output,device+'-'+name+'-'+phase+'.jpg'),type:'jpeg',quality:86,fullPage:true});
    }
   }
   if(phase==='after'){
    const oc=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false}),op=await oc.newPage();
    await op.goto(server.base+'/auth/sign-in');await op.locator('[name=user_id]').fill('preview-owner');await op.locator('[name=password]').fill(cfg.password);
    await Promise.all([op.waitForURL('**/auth/workspace'),op.getByRole('button',{name:'Sign in',exact:true}).click()]);
    await Promise.all([op.waitForURL('**/blueprint-import/history'),op.getByRole('button',{name:'Select workspace'}).click()]);
    for(const [device,size] of Object.entries(sizes)){
     await op.setViewportSize(size);check((await op.goto(server.base+'/flora/offers/start')).status()===200,device+': category step available');
     check(await op.locator('[name=primary]').inputValue()==='',device+': no implicit supplier category');
     await op.locator('summary').filter({hasText:'Also work in other categories?'}).click();
     check(await op.locator('[name=additional]').count()===12,device+': optional multi-sub-industry controls');
     check(await op.locator('[name=additional]').evaluateAll(es=>es.every(e=>!e.checked)),device+': no implied secondary categories');
     await op.screenshot({path:path.join(cfg.output,device+'-categories-after.jpg'),type:'jpeg',quality:86,fullPage:true});
    }
    await oc.close();
    for(const [pilot,data] of Object.entries(server.pilots)){
     const pc=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false}),pp=await pc.newPage();
     await pp.goto(server.base+'/auth/sign-in');await pp.locator('[name=user_id]').fill(data.user);await pp.locator('[name=password]').fill(cfg.password);
     await Promise.all([pp.waitForURL('**/auth/workspace'),pp.getByRole('button',{name:'Sign in',exact:true}).click()]);
     await Promise.all([pp.waitForURL('**/blueprint-import/history'),pp.getByRole('button',{name:'Select workspace'}).click()]);
     for(const [device,size] of Object.entries(sizes)){
      await pp.setViewportSize(size);await pp.goto(server.base+'/flora/offers');
      check(await pp.locator('main .offer-grid').first().locator(':scope>.offer-card').count()===3,pilot+' '+device+': exactly three selected examples');
      await pp.screenshot({path:path.join(cfg.output,device+'-'+pilot+'-portfolio.jpg'),type:'jpeg',quality:86,fullPage:true});
     }
     await pp.goto(server.base+'/flora/offers/edit?offer='+data.offer_id);
     check(await pp.locator('main').getByText('employer approved · v4',{exact:false}).count()===1,pilot+': independent approval retained');
     if(pilot!=='si')check((await pp.goto(server.base+'/flora/offers/edit?offer='+server.pilots.si.offer_id)).status()===403,pilot+': cannot cross selected employer boundary');
     if(pilot==='si'){
      const start=Date.now();await pp.goto(server.base+'/flora/offers/start');
      await pp.locator('input[name=templates][value^="tech-consulting-01:"]').check();await pp.locator('[name=confirmed]').check();
      await Promise.all([pp.waitForURL('**/flora/offers'),pp.getByRole('button',{name:'Create my private example offers',exact:true}).click()]);
      check(await pp.locator('main .offer-grid').first().locator(':scope>.offer-card').count()===3,'Repeat selection stays idempotent through actual CSRF-protected form');
      metrics.repeatSelectionSeconds=(Date.now()-start)/1000;
      await pp.getByRole('link',{name:'Continue to discovery',exact:true}).click();
      check(await pp.locator('[data-assessment-id]').count()===9,'Offer-led discovery uses the three existing offers and three governed account contexts');
     }
     metrics[pilot]={categories:data.categories,illustrativeOffers:data.count,approval:'Separate fixture reviewer; no real capability established'};
     await pc.close();
    }
   }
   await context.close();
  }
  fs.writeFileSync(path.join(cfg.output,'browser-checks.json'),JSON.stringify({fixture:'Isolated example users; no production or real company claims',javascript:false,checks,passed:checks.length,pilots:metrics,viewports:sizes},null,2)+'\n');
  console.log('Passed '+checks.length+' native-browser checks');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1;});
