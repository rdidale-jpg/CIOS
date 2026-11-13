/* Local-only browser acceptance for the owner-approved end-to-end slice. */
const {chromium}=require('playwright');
const fs=require('fs');
const assert=require('node:assert/strict');
(async()=>{
 const origin=process.argv[2],out=process.argv[3];
 const target=new URL(origin);
 if(target.protocol!=='http:'||!['127.0.0.1','localhost'].includes(target.hostname)||!out)throw Error('Usage: local preview URL and output directory required');
 fs.mkdirSync(out,{recursive:true});
 const root='/industries/technology/experience';
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:1440,height:1050}}),page=await context.newPage();
 const errors=[],writes=[],external=[],checks=[];
 context.on('page',p=>p.on('pageerror',e=>errors.push(e.message)));
 page.on('pageerror',e=>errors.push(e.message));
 context.on('request',r=>{if(!['GET','HEAD'].includes(r.method()))writes.push({method:r.method(),url:r.url()});if(!r.url().startsWith(origin)&&!r.url().startsWith('data:'))external.push(r.url());});
 async function visit(suffix){const response=await page.goto(origin+root+suffix);assert.equal(response.status(),200,suffix);await page.waitForLoadState('networkidle');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'page overflow '+suffix);checks.push({suffix,width:page.viewportSize().width});}
 const screens=[['','arrival'],['?selected=cloud','selection'],['/district?district=cloud','market'],['/enterprise','enterprise'],['/operating-model','enterprise-model'],['/pipeline?scope=industry','pipeline'],['/opportunity?record=cooling&scope=industry','opportunity']];
 for(const [width,height,label] of [[1440,1050,'desktop'],[1024,768,'ipad-landscape'],[768,1024,'ipad-portrait'],[390,844,'mobile']]){
  await page.setViewportSize({width,height});
  for(const [suffix,name]of screens){await visit(suffix);await page.screenshot({path:`${out}/${name}-${label}.png`,fullPage:true});}
  await visit('?selected=cloud');
  const aligned=await page.evaluate(()=>{
   const image=document.querySelector('.exp-artwork>img').getBoundingClientRect(),hotspot=document.querySelector('[data-district="cloud"]').getBoundingClientRect();
   return {x:(hotspot.x-image.x)/image.width,y:(hotspot.y-image.y)/image.height,aspect:image.width/image.height};
  });
  assert(Math.abs(aligned.x-.69)<.005&&Math.abs(aligned.y-.23)<.005,JSON.stringify(aligned));
  assert(Math.abs(aligned.aspect-1.5)<.01,'artwork distortion '+JSON.stringify(aligned));
  if(width>=768){
   for(const district of ['applications','cloud','ai','cyber','services','channels','infrastructure','frontier']){
    await visit('');const a=page.locator(`[data-district="${district}"]`);await a.focus();await page.keyboard.press('Enter');await page.waitForURL(`**/district?district=${district}`);assert.equal(await page.locator('.commercial-table').count(),1);assert(page.url().includes('/district?district='+district));
   }
  }
 }
 await page.setViewportSize({width:1440,height:1050});
 await visit('/district?district=cloud');await page.getByRole('link',{name:'AI & Technology',exact:true}).click();assert(await page.locator('#macro-context').innerText().then(s=>s.includes('hybrid workloads')));assert(page.url().includes('/district?macro=technology'));
 await visit('/enterprise');assert.equal(await page.locator('.primary-nav a').filter({hasText:'Pipeline'}).getAttribute('href'),root+'/pipeline?scope=equinix');await page.getByRole('link',{name:'$9.217bn · Revenue'}).click();assert(await page.locator('#revenue').innerText().then(s=>s.includes('$8.748bn')));
 await page.getByRole('link',{name:'Explore enterprise →',exact:true}).click();await page.getByRole('link',{name:'Interconnection',exact:true}).click();assert(await page.locator('#operating-area').innerText().then(s=>s.includes('hybrid-cloud')));
 await page.getByRole('link',{name:'View enterprise Pipeline →'}).click();assert(await page.locator('#pipeline-rows').innerText().then(s=>s.includes('Add an illustrative opportunity')));
 // Add only through explicit user action in the enterprise-scoped preview.
 await page.getByRole('button',{name:'+ Opportunity',exact:true}).click();
 const dialog=page.locator('#demo-editor');await dialog.waitFor({state:'visible'});assert(await dialog.locator('[name=enterprise]').evaluate(e=>e.readOnly),'enterprise scope must not silently change');
 await dialog.locator('[name=title]').fill('Owner preview cooling');await dialog.locator('[name=tcv]').fill('123456.78');await dialog.locator('[name=close]').fill('2027-04-30');await dialog.locator('[name=owner]').fill('Demo owner');await dialog.locator('[name=unit]').fill('Facilities');await dialog.locator('[name=stakeholder]').fill('Demo sponsor');await dialog.locator('[name=next]').fill('Discuss scope');
 await dialog.getByRole('button',{name:'Save preview changes'}).click();assert(await page.locator('#pipeline-rows').innerText().then(s=>s.includes('£123,456.78')));
 await page.getByRole('link',{name:'Owner preview cooling',exact:true}).click();await page.getByRole('link',{name:'Open full opportunity →'}).click();
 const createdURL=page.url();assert(createdURL.includes('scope=equinix'));assert(await page.locator('h1').innerText()==='Owner preview cooling');
 await page.getByRole('combobox',{name:'Opportunity stage',exact:true}).selectOption('Qualified');await page.reload();assert.equal(await page.locator('#opportunity-stage').inputValue(),'Qualified');
 await page.getByLabel('Add a note',{exact:true}).fill('<img src=x onerror=alert(1)> Customer conversation pending');await page.getByRole('button',{name:'Add note',exact:true}).click();assert.equal(await page.locator('.exp-notes img').count(),0);assert(await page.locator('.exp-notes').allTextContents().then(s=>s.join(' ').includes('<img src=x')));
 await page.getByRole('button',{name:'Edit',exact:true}).click();
 await dialog.locator('[name=close]').fill('2026-01-01');await dialog.getByRole('button',{name:'Save preview changes'}).click();assert(await page.locator('#editor-error').innerText().then(s=>s.includes('close on or after start')));await page.keyboard.press('Escape');
 await page.getByRole('link',{name:'← Pipeline',exact:true}).click();await page.locator('#pipeline-search').fill('Owner preview cooling');assert.equal(await page.locator('#pipeline-rows tr').count(),1);
 await page.locator('#pipeline-stage').selectOption('Lost');assert(await page.locator('#pipeline-rows').innerText().then(s=>s.includes('Add an illustrative opportunity')));await page.locator('#pipeline-stage').selectOption('');
 await page.locator('#pipeline-search').fill('');await page.locator('[data-sort="tcv"]').click();assert.equal(await page.locator('[data-sort="tcv"]').locator('..').getAttribute('aria-sort'),'ascending');
 await page.locator('#pipeline-scope').selectOption('industry');await page.getByRole('button',{name:'Apply',exact:true}).click();assert(await page.locator('#pipeline-rows').innerText().then(s=>s.includes('Owner preview cooling')&&s.includes('Northbridge DC')));
 // Unknown local IDs and scope mismatches never resolve a server/private record.
 await visit('/opportunity?record=cooling&scope=equinix');assert.equal(await page.locator('h1').innerText(),'Opportunity unavailable');
 const fresh=await browser.newContext();const freshPage=await fresh.newPage();await freshPage.goto(createdURL);assert.equal(await freshPage.locator('h1').innerText(),'Opportunity unavailable');await fresh.close();
 // Native read path remains useful without JS.
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:1024,height:768}}),native=await nojs.newPage();await native.goto(origin+root);await native.locator('[data-district="cloud"]').click();await native.getByRole('link',{name:'Equinix →',exact:true}).click();await native.getByRole('link',{name:'Business & financials →'}).click();assert(await native.locator('#revenue').innerText().then(s=>s.includes('$9.217bn')));
 await native.goto(origin+root+'/pipeline');await native.getByRole('link',{name:'Cooling optimisation',exact:true}).click();assert.equal(await native.locator('h1').innerText(),'Cooling optimisation');await nojs.close();
 // Restricted storage still provides an honest, safe preview.
 const blocked=await browser.newContext();await blocked.addInitScript(()=>{Object.defineProperty(window,'sessionStorage',{get(){throw new Error('disabled')}})});const bp=await blocked.newPage();await bp.goto(origin+root+'/pipeline');assert.equal(await bp.locator('#pipeline-rows tr').count(),4);assert(await bp.locator('#preview-status').innerText().then(s=>s.includes('could not be loaded')));await blocked.close();
 await page.emulateMedia({reducedMotion:'reduce'});await visit('/pipeline');await page.pdf({path:out+'/pipeline-print.pdf',format:'A4',landscape:true,printBackground:true});
 assert.deepEqual(errors,[]);assert.deepEqual(writes,[]);assert.deepEqual(external,[]);
 fs.writeFileSync(out+'/Browser-Results.json',JSON.stringify({passed:true,responsiveChecks:checks.length,keyboardDistrictActivations:24,checks,errors,networkWrites:writes,externalRequests:external,tests:['image-relative alignment at four sizes','market-enterprise-financial-model-Pipeline drill','search filters numeric sorting','explicit enterprise-scoped tab-local creation','stage update persists on reload','dates rejected when close precedes start','notes rendered as text, not markup','scope changes preserve context and local edits','fresh context cannot read another tab preview','no-JavaScript native read journey','storage unavailable fallback','reduced motion and print'],limitations:['Chromium simulated iPad sizes; physical iPad/Safari and assistive technology not tested','Synthetic sales examples only; no live Pipeline integration']},null,2)+'\n');
 await browser.close();console.log('PASS',checks.length,'responsive views; end-to-end preview interactions; zero network writes.');
})().catch(e=>{console.error(e);process.exit(1)});
