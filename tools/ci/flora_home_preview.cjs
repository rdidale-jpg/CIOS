// Design preview only: local HTTPS/authentication and disposable synthetic seller context.
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),crypto=require('crypto');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const checks=[],errors=[];
function check(value,label){assert(value,label);checks.push(label);}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844}};
 const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
 async function capture(page,name){
  await page.locator('.home-world').waitFor();await page.evaluate(()=>document.fonts.ready);
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),name+': no overflow');
  check(await page.locator('h1').count()===1,name+': one clear heading');
  await page.screenshot({path:path.join(config.output,name+'.png'),fullPage:true});
 }
 try{
  const pub=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false}),page=await pub.newPage();
  page.on('pageerror',e=>errors.push(e.message));
  for(const [device,viewport] of Object.entries(sizes)){
   await page.setViewportSize(viewport);
   for(const [name,route] of [['uk-public','/home?market=GB'],['fr-public','/home?market=FR'],['global-forces','/home/global-forces?market=GB'],['fr-legal','/home/global-forces?market=FR&lens=legal']]){
    const r=await page.goto(config.base+route);check(r.status()===200,device+' '+name+': public view available');
    await capture(page,device+'-'+name);
    if(name==='uk-public'){
     check(await page.locator('[data-industry]').count()===3,device+': three labelled native regions');
     for(const link of await page.locator('[data-industry]').all()){
      const box=await link.boundingBox();check(box.height>=44&&box.width>=44,device+': touch target >=44px');
      check((await link.innerText()).trim().length>3,device+': visible initial industry label');
      await link.focus();check(await link.evaluate(el=>el===document.activeElement),device+': industry link keyboard focus');
     }
     check(await page.locator('.world-change').count()>=3,device+': dated source developments');
     check(await page.locator('[data-assessment-id]').count()===0,device+': no invented public sales plays');
     check(!(await page.content()).includes('Illustrative UK services company'),device+': no private employer in public HTML');
     await page.getByRole('link',{name:'Global forces',exact:false}).first().click();
     check(new URL(page.url()).pathname==='/home/global-forces',device+': global PESTLE one step');
     check(await page.getByRole('navigation',{name:'Global PESTLE lenses'}).locator('a').count()===7,device+': six lenses plus overview');
     await page.goto(config.base+'/home?market=GB');
     await page.getByLabel('Selected market').selectOption('FR');
     await Promise.all([page.waitForURL('**/home?market=FR'),page.getByRole('button',{name:'View',exact:true}).click()]);
     check(await page.locator('[data-industry]').count()===0,device+': second country has no invented regions');
     check(await page.locator('.world-change').count()===0,device+': second country has no invented briefing');
    }
   }
   await page.goto(config.base+'/home/global-forces?market=GB&lens=economic');
   check(await page.getByText('No selected signal is presented',{exact:false}).count()===1,device+': unsupported lens is not fabricated');
   await page.getByLabel('Selected market').selectOption('FR');
   await Promise.all([page.waitForURL('**/home/global-forces?lens=economic&market=FR'),page.getByRole('button',{name:'View',exact:true}).click()]);
   check(new URL(page.url()).searchParams.get('lens')==='economic',device+': country switch preserves explicit lens');
   if(config.baseline){
    const old=await pub.newPage();await old.setViewportSize(viewport);
    await old.goto(config.baseline+'/');await old.bringToFront();await old.evaluate(()=>document.fonts.ready);
    const before=await old.screenshot({fullPage:true,animations:'disabled',caret:'hide'});
    fs.writeFileSync(path.join(config.output,device+'-before-home.png'),before);
    await page.goto(config.base+'/');await page.bringToFront();await page.evaluate(()=>document.fonts.ready);
    const retained=await page.screenshot({fullPage:true,animations:'disabled',caret:'hide'});
    check(sha(before)===sha(retained),device+': canonical Home unchanged pending acceptance');await old.close();
   }
  }
  await pub.close();
  const priv=await browser.newContext({ignoreHTTPSErrors:true}),seller=await priv.newPage();
  await seller.goto(config.base+'/auth/sign-in');await seller.locator('[name=user_id]').fill('preview-seller');await seller.locator('[name=password]').fill(config.password);
  await Promise.all([seller.waitForURL('**/auth/workspace'),seller.getByRole('button',{name:'Sign in',exact:true}).click()]);
  await Promise.all([seller.waitForURL('**/blueprint-import/history'),seller.getByRole('button',{name:'Select workspace'}).click()]);
  for(const [device,viewport] of Object.entries(sizes)){
   await seller.setViewportSize(viewport);await seller.goto(config.base+'/home?market=GB');
   await capture(seller,device+'-uk-seller');
   check(await seller.getByText('Illustrative UK services company',{exact:true}).count()===1,device+': authorised employer context');
   const ids=await seller.locator('[data-assessment-id]').evaluateAll(el=>el.map(e=>e.dataset.assessmentId));
   check(ids.length>0&&ids.length<=3,device+': bounded existing assessed plays');
   check(await seller.getByText('United Kingdom · France',{exact:true}).count()===1,device+': seller territory separate from active market');
   await seller.goto(config.base+'/home?market=FR');await capture(seller,device+'-fr-seller');
   check(await seller.getByText('Illustrative UK services company',{exact:true}).count()===1,device+': market switch preserves employer');
   check(await seller.locator('[data-assessment-id]').count()===0,device+': no unsupported local account plays');
  }
  await seller.emulateMedia({reducedMotion:'reduce'});await seller.goto(config.base+'/home?market=GB');
  check(await seller.locator('[data-industry]').count()===3,'reduced motion keeps native navigation');
  await seller.emulateMedia({media:'print'});await seller.pdf({path:path.join(config.output,'home-seller-print.pdf'),format:'A4',printBackground:true});
  checks.push('print view exported');await priv.close();
  const compact=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,viewport:{width:320,height:780}}),cp=await compact.newPage();
  await cp.goto(config.base+'/home?market=GB');
  check(await cp.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'320px accessible without overflow');
  for(const link of await cp.locator('[data-industry]').all()){const box=await link.boundingBox();check(box.width>=44&&box.height>=44,'320px native region touch target');}
  await cp.locator('.home-skip').focus();await cp.keyboard.press('Enter');
  check(await cp.evaluate(()=>document.activeElement.id==='home-content'),'skip link reaches focusable Home content');await compact.close();
  check(errors.length===0,'no browser page errors');
  fs.writeFileSync(path.join(config.output,'Browser-Checks.json'),JSON.stringify({passed:checks.length,failed:0,viewports:sizes,checks,limitations:['Synthetic seller/approval fixtures only','Physical iPad Safari and assistive technology review required','Canonical Home retained; preview is not deployed','France is a layout study, not industry coverage']},null,2)+'\n');
  console.log(checks.length+' Home responsive/authenticated design checks passed');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1)});
