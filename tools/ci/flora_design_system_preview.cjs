const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[],metrics={},errors=[];
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:780}};
const tech='/industries/technology/experience';
const routes={home:'/',technology:tech,frontier:tech+'/district?district=frontier',nvidia:tech+'/enterprise?enterprise=nvidia&district=frontier',pestle:'/visual-v2/pestle?market=GB&factor=technological#insight',model:tech+'/operating-model?area=interconnection#operating-area',banking:'/industries/banking',aviation:'/industries/aviation'};
function check(v,label){assert(v,label);checks.push(label);}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 async function screenshot(p,name){await p.waitForLoadState('load');await p.evaluate(()=>{document.activeElement?.blur();return document.fonts.ready});await p.screenshot({path:path.join(cfg.output,name+'.jpg'),type:'jpeg',quality:90,fullPage:true});}
 async function measure(p){
  return await p.evaluate(()=>{
   const visible=e=>!!(e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden');
   const main=document.querySelector('main')||document.body;
   return {primaryNavigations:document.querySelectorAll('nav[aria-label="Primary product navigation"]').length,
    bodyNavigation:[...main.querySelectorAll('nav')].filter(visible).length,
    bodyGlobalLinks:[...main.querySelectorAll('a')].filter(e=>visible(e)&&['/','/industries','/enterprises','/flora/offers','/opportunities','/flora/sales/pipeline'].includes(e.getAttribute('href'))).length,
    sourcePrompts:[...main.querySelectorAll('a,summary')].filter(e=>visible(e)&&/inspect.*evidence|sources.*context|source.*provenance|^research$|^details$|measurement context/i.test(e.textContent)).length,
    visibleWords:main.innerText.split(/\s+/).filter(Boolean).length};
  });
 }
 async function layout(p,label,after){
  await p.waitForLoadState('load');await p.evaluate(()=>document.fonts.ready);
  const bounds=await p.evaluate(()=>({w:innerWidth,scroll:document.documentElement.scrollWidth,over:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&getComputedStyle(e).position!=='absolute').slice(0,8).map(e=>({tag:e.tagName,cls:e.className,right:e.getBoundingClientRect().right}))}));
  if(after&&bounds.scroll>bounds.w+1)console.log(label,JSON.stringify(bounds));
  if(after){check(bounds.scroll<=bounds.w+1,label+': no page overflow');check(await p.locator('h1').count()===1,label+': one heading');check(await p.locator('header.product-header nav[aria-label="Primary product navigation"]').count()===1,label+': shared compact header');check(await p.locator('main .commercial-district-nav,main .commercial-jumps,main .exp-scene-heading nav,main .exp-support').count()===0,label+': no duplicate technology navigation');}
 }
 async function login(p,server){
  await p.goto(server.base+'/auth/sign-in');await p.locator('[name=user_id]').fill('preview-seller');await p.locator('[name=password]').fill(cfg.password);
  await Promise.all([p.waitForURL('**/auth/workspace'),p.getByRole('button',{name:'Sign in',exact:true}).click()]);
  await Promise.all([p.waitForURL('**/blueprint-import/history'),p.getByRole('button',{name:'Select workspace'}).click()]);
 }
 try{
  for(const [phase,server] of Object.entries(cfg.servers)){
   const after=phase==='after';metrics[phase]={};
   const context=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,hasTouch:true}),p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
   for(const [device,viewport] of Object.entries(sizes)){
    await p.setViewportSize(viewport);
    for(const [name,route] of Object.entries(routes)){
     if(['model','banking','aviation'].includes(name)&&!['desktop','ipad-portrait','mobile'].includes(device))continue;
     const response=await p.goto(server.base+(after&&name==='pestle'?route.replace('/visual-v2/pestle','/pestle'):route));check(response.status()===200,phase+' '+device+' '+name+': available');
     await layout(p,phase+' '+device+' '+name,after);await screenshot(p,device+'-'+name+'-'+phase);
     if(device==='desktop')metrics[phase][name]=await measure(p);
     if(after&&name==='home'){
      check(await p.locator('[data-sic]').count()===20,device+': approved complete UK landscape');check(await p.locator('[data-research]').count()===3,device+': only researched Home regions');
      check(await p.locator('main section,main article').count()===0,device+': no old Home content modules');
      check(!(await p.content()).includes('Synthetic UK services company'),device+': public Home has no employer data');
     }
     if(after&&name==='technology'){
      check(await p.locator('[data-district]').count()===8,device+': eight industry anchors');
      for(const a of await p.locator('[data-district]').all()){
       const b=await a.boundingBox();check(b.width>=44&&b.height>=44,device+': industry touch >=44px');check(await a.locator('em').isVisible(),device+': readable initial industry name');await a.focus();check(await a.evaluate(e=>e===document.activeElement),device+': native industry keyboard focus');
      }
      check((await p.locator('main').innerText()).includes('share of UK GVA, 2024'),device+': scoped industry financial context');
     }
     if(after&&name==='frontier'){
      check(await p.locator('tbody tr').count()>0,device+': compact participants');
      check(await p.locator('tbody tr').evaluateAll(rs=>rs.every(r=>r.querySelectorAll('a').length===1)),device+': company is the only row link');
      check(await p.locator('main .commercial-source,main .commercial-metric').count()===0,device+': no per-row evidence disclosure');
      check((await p.locator('[data-participant=nvidia] [data-metric=uk_revenue]').textContent()).trim()==='',device+': no invented NVIDIA UK revenue');
      await Promise.all([p.waitForNavigation({waitUntil:'load'}),p.locator('[data-comparison-sort=name]').click()]);check(await p.locator('th[aria-sort=descending]').count()===1,device+': native sortable comparison');
     }
     if(after&&name==='nvidia'){
      for(const value of ['$215.938bn','$120.067bn','71.1%','$96.221bn','c. 42,000','Global group · FY2026 ended 25 January 2026 · USD'])check((await p.locator('main').innerText()).includes(value),device+': retained financial '+value);
      check(await p.locator('.commercial-opportunity').count()===3,device+': three original opportunity hypotheses');
      check(await p.locator('main .commercial-source').count()===0,device+': single source location');
      check(await p.locator('main a[href*="/flora/sales/capture"]').count()===0,device+': no unbound NVIDIA capture');
      await p.locator('.sources-menu>summary').click();check((await p.locator('.source-sheet').innerText()).includes('UK-specific revenue'),device+': source/geography boundaries retained');
      check(await p.locator('.source-sheet a[href*="nvidia"]').count()>0,device+': actual source links available');await p.locator('.sources-menu>summary').click();
     }
     if(after&&name==='pestle'){
      check(await p.locator('.factor').count()===6,device+': approved six-factor PESTLE');check(await p.locator('.pestle-scene .image-insight').count()===1,device+': insight stays in image');
      const box=await p.locator('.image-insight').boundingBox();check(await p.locator('.factor').evaluateAll((es,b)=>es.every(e=>{const a=e.getBoundingClientRect();return a.right<=b.x||a.left>=b.x+b.width||a.bottom<=b.y||a.top>=b.y+b.height}),box),device+': all six PESTLE controls unobscured');
      for(const factor of ['political','economic','social','technological','legal','environmental']){
       await p.goto(server.base+'/pestle?market=GB&factor='+factor+'#insight');
       const art=await p.locator('.pestle-scene').boundingBox(),ins=await p.locator('.image-insight').boundingBox();
       check(ins.x>=art.x&&ins.y>=art.y&&ins.x+ins.width<=art.x+art.width+1&&ins.y+ins.height<=art.y+art.height+1,device+' '+factor+': selected insight remains over approved art');
       check(await p.locator('.factor').evaluateAll((es,b)=>es.every(e=>{const a=e.getBoundingClientRect();return a.right<=b.x||a.left>=b.x+b.width||a.bottom<=b.y||a.top>=b.y+b.height}),ins),device+' '+factor+': factor labels remain unobscured');
      }

     }
     if(after&&name==='model'){
      check(await p.locator('.ds-model .ds-model-control').count()===2,device+': existing conceptual model areas');check(await p.locator('.ds-model .ds-model-insight').count()===1,device+': model question over image');
      await Promise.all([p.waitForNavigation({waitUntil:'load'}),p.getByRole('link',{name:'Facilities',exact:true}).click()]);check(await p.locator('#operating-area h2').innerText()==='Facilities',device+': native no-JS model state');
     }
    }
   }
   await context.close();
   const priv=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,hasTouch:true}),seller=await priv.newPage();await login(seller,server);
   const privateRoutes={offers:'/flora/offers',discovery:'/flora/offers/discover?mode=account&selected=lloyds',pipeline:'/flora/sales/pipeline',qualification:'/flora/sales/'+server.pipeline_id};
   for(const [device,viewport] of Object.entries(sizes)){
    await seller.setViewportSize(viewport);
    for(const [name,route] of Object.entries(privateRoutes)){
     const r=await seller.goto(server.base+route);check(r.status()===200,phase+' '+device+' '+name+': authorised workspace');await layout(seller,phase+' '+device+' '+name,after);await screenshot(seller,device+'-'+name+'-'+phase);
     if(device==='desktop')metrics[phase][name]=await measure(seller);
     if(after&&name==='discovery'){
      check(await seller.locator('[data-assessment-id]').count()>0,device+': existing matcher result');check(await seller.locator('main a[href="/flora/sales/new?enterprise=lloyds"]').count()>0,device+': explicit manual qualification route');
      check(await seller.locator('main a[href="/flora/sales/pipeline"]').count()===0,device+': repeated Pipeline shortcut removed');
      check(await seller.locator('main .source-list').count()===0,device+': private lineage in one source disclosure');
      await seller.locator('.sources-menu>summary').click();check((await seller.locator('.source-sheet').innerText()).includes('SYNTHETIC proof'),device+': authorised offer proof still accessible');await seller.locator('.sources-menu>summary').click();
     }
     if(after&&name==='qualification'){
      check(await seller.locator('form[action="/flora/sales/'+server.pipeline_id+'/save"]').count()===1,device+': original edit form retained');
      check(await seller.locator('input[name=csrf]').count()>0,device+': CSRF form token retained');
      check((await seller.locator('main').innerText()).includes('Discovered'),device+': no automatic qualification');
     }
    }
   }
   if(after){
    await seller.setViewportSize(sizes.desktop);await seller.goto(server.base+'/flora/offers/discover?mode=account&selected=lloyds');
    await Promise.all([seller.waitForNavigation({waitUntil:'load'}),seller.locator('main a[href="/flora/sales/new?enterprise=lloyds"]').first().click()]);
    check(new URL(seller.url()).pathname==='/flora/sales/new','Offers to manual Pipeline is a GET, not an implicit capture');
    check(await seller.locator('form[action="/flora/sales/create"] input[name=csrf]').count()===1,'manual creation still requires the existing CSRF-protected form');
    await seller.goto(server.base+'/flora/offers');await seller.locator('.product-menu>summary').click();check(await seller.getByRole('link',{name:'Switch workspace',exact:true}).count()===1,'verified account controls preserved');
    await seller.getByRole('button',{name:'Sign out',exact:true}).click();
    check((await seller.goto(server.base+'/flora/offers')).status()!==200,'signed-out seller cannot read Offers');check((await seller.goto(server.base+'/flora/sales/pipeline')).status()!==200,'signed-out seller cannot read Pipeline');
   }
   await priv.close();
  }
  const enhanced=await browser.newContext({ignoreHTTPSErrors:true,viewport:sizes.desktop}),p=await enhanced.newPage();
  await p.goto(cfg.servers.after.base+routes.nvidia);await p.locator('.ds-skip').focus();await p.keyboard.press('Enter');check(await p.evaluate(()=>document.activeElement.id==='page-content'),'shared skip focuses main');
  await p.locator('.sources-menu>summary').click();await p.keyboard.press('Escape');check(await p.locator('.sources-menu').getAttribute('open')===null,'Escape closes source disclosure');
  await p.emulateMedia({reducedMotion:'reduce'});
  await p.pdf({path:path.join(cfg.output,'nvidia-print.pdf'),format:'A4',printBackground:true});
  await p.goto(cfg.servers.after.base+'/');await p.pdf({path:path.join(cfg.output,'home-print.pdf'),format:'A4',printBackground:true});
  const cdp=await p.context().newCDPSession(p);const tree=await cdp.send('Accessibility.getFullAXTree');check(tree.nodes.some(n=>n.role?.value==='heading'&&n.name?.value==='United Kingdom'),'accessible country heading');
  await enhanced.close();check(errors.length===0,'no browser page errors');
  fs.writeFileSync(path.join(cfg.output,'Browser-Checks.json'),JSON.stringify({passed:checks.length,failed:0,viewports:sizes,checks,limitations:['Chromium emulation; physical iPad/Safari, screen-reader and high-zoom owner review remain manual','All private company/offer/approval/Pipeline records are synthetic fixtures','Browser navigation made no commercial domain writes']},null,2)+'\n');
  fs.writeFileSync(path.join(cfg.output,'Editorial-Comparison.json'),JSON.stringify(metrics,null,2)+'\n');console.log(checks.length+' unified design-system checks passed');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1)});
