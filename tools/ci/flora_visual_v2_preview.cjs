const {chromium}=require('playwright'), fs=require('fs'),path=require('path'),assert=require('node:assert/strict'),crypto=require('crypto');
const config=JSON.parse(fs.readFileSync(process.argv[2],'utf8')),checks=[],errors=[];
const sizes={desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:780}};
const factors=['political','economic','social','technological','legal','environmental'];
function check(v,label){assert(v,label);checks.push(label);}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const context=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false}),page=await context.newPage();
 page.on('pageerror',e=>errors.push(e.message));
 async function capture(name){await page.evaluate(()=>{document.activeElement?.blur();return document.fonts.ready});await page.screenshot({path:path.join(config.output,name+'.jpg'),type:'jpeg',quality:94,fullPage:true});}
 async function common(name){
  await page.waitForLoadState('load');await page.evaluate(()=>document.fonts.ready);
  const over=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);if(over)console.log(JSON.stringify(await page.evaluate(()=>[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).map(e=>({tag:e.tagName,cls:e.className,width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})))));check(!over,name+': no page overflow');
  check(await page.locator('h1').count()===1,name+': one heading');
  check(await page.locator('nav').count()===1,name+': one header navigation');
  check(await page.locator('header nav').count()===1,name+': navigation beside FLORA');
  check(await page.locator('main>figure').count()===1,name+': one illustration');
  check(await page.locator('main>section,main>article,footer').count()===0,name+': no detached content or footer');
  check(!/My Commercial Focus|What.s Changing|Recommended Sales Plays|More from FLORA|Inspect evidence/.test(await page.locator('main').innerText()),name+': no secondary modules');
 }
 async function targetChecks(selector,name){
  const boxes=[];
  for(const el of await page.locator(selector).all()){
   const b=await el.boundingBox();check(b.width>=44&&b.height>=44,name+': touch >=44px');
   await el.focus();check(await el.evaluate(e=>document.activeElement===e),name+': native keyboard target');boxes.push(b);
  }
  check(boxes.every((a,i)=>boxes.every((b,j)=>i===j||a.x+a.width<=b.x||b.x+b.width<=a.x||a.y+a.height<=b.y||b.y+b.height<=a.y)),name+': targets do not overlap');
 }
 try{
  for(const [device,viewport] of Object.entries(sizes)){
   await page.setViewportSize(viewport);
   let r=await page.goto(config.base+'/visual-v2?market=GB');check(r.status()===200,device+': public Home');await common(device+' Home');
   check(await page.locator('[data-sic]').count()===20,device+': all domestic SIC sections');
   check(await page.locator('.researched').count()===3,device+': only supported sub-sectors clickable');
   check(await page.locator('main a:not(.researched)').count()===0,device+': no redundant Home links');
   check(await page.locator('.district-scale').count()===5,device+': five restrained comparable GVA shares');
   for(const district of await page.locator('.district').all()){
    const b=await district.boundingBox();check(b.x>=-1&&b.x+b.width<=viewport.width+1,device+': district label within image');
   }
   await targetChecks('.researched',device+' Home');await capture(device+'-economy');
   if(config.baseline){
    const before=await context.newPage();await before.setViewportSize(viewport);await before.goto(config.baseline+'/home?market=GB');await before.screenshot({path:path.join(config.output,device+'-home-v1-before.jpg'),type:'jpeg',quality:94,fullPage:true});
    const old=await before.goto(config.baseline+'/');check(old.status()===200,device+': baseline canonical Home');
    const oldImage=await before.screenshot({fullPage:true,animations:'disabled',caret:'hide'});
    await page.goto(config.base+'/');const current=await page.screenshot({fullPage:true,animations:'disabled',caret:'hide'});
    check(crypto.createHash('sha256').update(oldImage).digest('hex')===crypto.createHash('sha256').update(current).digest('hex'),device+': canonical Home pixel preserved');await before.close();
   }
   await page.goto(config.base+'/visual-v2?market=GB');await Promise.all([page.waitForNavigation({waitUntil:'load'}),page.getByRole('link',{name:'PESTLE',exact:true}).click()]);check(new URL(page.url()).pathname==='/visual-v2/pestle',device+': PESTLE in one header action');
   await common(device+' PESTLE');await targetChecks('.factor',device+' PESTLE');
   check(await page.locator('.factor').count()===6,device+': six initial factor labels');check(await page.locator('.image-insight').count()===0,device+': no permanent insight cards');await capture(device+'-pestle');
   for(const factor of factors){
    const el=page.locator('#factor-'+factor);await el.focus();await Promise.all([page.waitForNavigation({waitUntil:'load'}),page.keyboard.press('Enter')]);
    await page.locator('.image-insight[data-factor="'+factor+'"]').waitFor();
    check(await page.locator('.image-insight').count()===1,device+' '+factor+': single no-JS insight');
    const art=await page.locator('.pestle-scene').boundingBox(),ins=await page.locator('.image-insight').boundingBox();
    check(ins.x>=art.x&&ins.y>=art.y&&ins.x+ins.width<=art.x+art.width+1&&ins.y+ins.height<=art.y+art.height+1,device+' '+factor+': insight remains over image');
    const covered=await page.locator('.factor').evaluateAll(es=>es.filter(el=>{const b=el.getBoundingClientRect(),s=document.querySelector('.image-insight').getBoundingClientRect();return !(b.right<=s.left||b.left>=s.right||b.bottom<=s.top||b.top>=s.bottom)}).length);
    check(covered===0,device+' '+factor+': all six factor labels remain uncovered');
    if(device==='desktop'||['technological','economic'].includes(factor))await capture(device+'-pestle-'+factor);
    await Promise.all([page.waitForNavigation({waitUntil:'load'}),page.getByRole('link',{name:'Close '+factor[0].toUpperCase()+factor.slice(1)+' insight',exact:true}).click()]);
    check(await page.locator('.image-insight').count()===0,device+' '+factor+': native close');
    check(await page.evaluate(f=>document.activeElement.id==='factor-'+f,factor),device+' '+factor+': no-JS close returns focus');
   }
   await page.locator('.sources-menu>summary').click();check(await page.getByText('Scale, scope & sources',{exact:true}).isVisible(),device+': single optional source view');
   check(await page.getByText('Rounded sections total 100.2%',{exact:false}).isVisible(),device+': rounding disclosed');
   await page.locator('.statistical-table summary').click();check(await page.locator('.statistical-table tbody tr').count()===20,device+': complete optional comparable series');
   check(await page.locator('.source-sheet').evaluate(e=>{const b=e.getBoundingClientRect();return b.left>=0&&b.right<=innerWidth}),device+': optional source view stays in viewport');await page.locator('.sources-menu>summary').click();
   await page.locator('.product-menu summary').click();check(await page.locator('.product-menu .menu-sheet').evaluate(e=>{const b=e.getBoundingClientRect();return b.left>=0&&b.right<=innerWidth}),device+': workspace menu stays in viewport');await page.locator('.product-menu summary').click();
   for(const [name,href] of [['technology','/industries/technology/experience'],['banking','/industries/banking'],['aviation','/industries/aviation']]){
    await page.goto(config.base+'/visual-v2');await page.locator('[data-research="'+name+'"]').focus();
    const [response]=await Promise.all([page.waitForNavigation(),page.keyboard.press('Enter')]);
    check(response.status()===200&&new URL(page.url()).pathname===href,device+' '+name+': native Enter reaches supported research');
   }
  }
  await context.close();
  const enhanced=await browser.newContext({ignoreHTTPSErrors:true,viewport:sizes.desktop}),p=await enhanced.newPage();
  await p.goto(config.base+'/visual-v2/pestle?market=GB');await Promise.all([p.waitForNavigation({waitUntil:'load'}),p.locator('#factor-technological').click()]);
  check(await p.evaluate(()=>document.activeElement.id==='insight'),'JS enhancement focuses selected insight');
  await Promise.all([p.waitForNavigation({waitUntil:'load'}),p.keyboard.press('Escape')]);check(!new URL(p.url()).searchParams.has('factor'),'Escape closes insight');check(await p.evaluate(()=>document.activeElement.id==='factor-technological'),'Escape returns focus to selected factor');
  await p.locator('.sources-menu>summary').click();await p.keyboard.press('Escape');check(await p.locator('.sources-menu').getAttribute('open')===null,'Escape closes source disclosure');
  await p.locator('.sources-menu>summary').click();await p.locator('.statistical-table summary').click();check(await p.locator('.sources-menu').getAttribute('open')!==null,'nested methodology does not close source disclosure');await p.keyboard.press('Escape');
  await p.locator('.skip').focus();await p.keyboard.press('Enter');check(await p.evaluate(()=>document.activeElement.id==='visual-content'),'skip reaches focusable visual');
  await p.goto(config.base+'/auth/sign-in');await p.locator('[name=user_id]').fill('preview-owner');await p.locator('[name=password]').fill(config.password);
  await Promise.all([p.waitForURL('**/auth/workspace'),p.getByRole('button',{name:'Sign in',exact:true}).click()]);
  await Promise.all([p.waitForURL('**/blueprint-import/history'),p.getByRole('button',{name:'Select workspace'}).click()]);
  await p.goto(config.base+'/visual-v2?market=GB');await p.locator('.product-menu summary').click();
  check(await p.getByRole('link',{name:'Switch workspace',exact:true}).isVisible(),'verified workspace control retained');
  check(await p.locator('form[action="/auth/sign-out"] input[name=csrf]').count()===1,'existing CSRF decorates sign-out');
  await p.getByRole('button',{name:'Sign out',exact:true}).click();await p.goto(config.base+'/visual-v2');await p.locator('.product-menu summary').click();
  check(await p.getByRole('link',{name:'Sign in',exact:true}).isVisible(),'sign-out returns to public view');
  await p.emulateMedia({reducedMotion:'reduce'});await p.goto(config.base+'/visual-v2');await p.pdf({path:path.join(config.output,'economy-print.pdf'),format:'A4',printBackground:true});
  await p.goto(config.base+'/visual-v2/pestle?factor=economic#insight');check(await p.locator('.factor').count()===6,'reduced motion retains six native factors');
  await p.pdf({path:path.join(config.output,'pestle-print.pdf'),format:'A4',printBackground:true});checks.push('print exported');
  await enhanced.close();
  const touch=await browser.newContext({ignoreHTTPSErrors:true,javaScriptEnabled:false,hasTouch:true,viewport:sizes['ipad-landscape']}),tp=await touch.newPage();
  await tp.goto(config.base+'/visual-v2/pestle');await Promise.all([tp.waitForNavigation({waitUntil:'load'}),tp.locator('#factor-social').tap()]);check(await tp.locator('.image-insight[data-factor=social]').count()===1,'native iPad touch reveals insight');
  const cdp=await tp.context().newCDPSession(tp);const tree=await cdp.send('Accessibility.getFullAXTree');
  check(factors.every(f=>tree.nodes.some(n=>n.role?.value==='link'&&n.name?.value?.startsWith(f[0].toUpperCase()+f.slice(1)))),'browser accessibility tree exposes all six named factor links');
  check(tree.nodes.some(n=>n.role?.value==='heading'&&n.name?.value==='Social value needs delivery.'),'browser accessibility tree exposes selected intelligence heading');
  await touch.close();check(errors.length===0,'no page errors');
  fs.writeFileSync(path.join(config.output,'Browser-Checks.json'),JSON.stringify({passed:checks.length,failed:0,viewports:sizes,checks,limitations:['Chromium emulation, not physical iPad/Safari or screen-reader certification','Synthetic local authentication only','Design-first preview; no canonical Home replacement or deployment']},null,2)+'\n');
  console.log(checks.length+' visual v2 browser checks passed');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1)});
