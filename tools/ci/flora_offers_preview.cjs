// Local synthetic owner walkthrough. Config (including fixture password) is never published.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const config = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const checks = [];
function check(condition, label) { if (!condition) throw new Error(label); checks.push(label); }
(async () => {
 const browser = await chromium.launch({executablePath:'/usr/bin/chromium', args:['--no-sandbox']});
 const errors = [];
 const sha = bytes => require('crypto').createHash('sha256').update(bytes).digest('hex');
 async function login(context, user) {
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  await page.goto(config.base + '/auth/sign-in');
  await page.locator('[name=user_id]').fill(user);
  await page.locator('[name=password]').fill(config.password);
  await Promise.all([page.waitForURL('**/auth/workspace'), page.getByRole('button', {name:'Sign in',exact:true}).click()]);
  await Promise.all([page.waitForURL('**/blueprint-import/history'), page.getByRole('button',{name:'Select workspace'}).click()]);
  return page;
 }
 async function capture(page, name, label) {
  await page.locator('.offers').waitFor();
  check(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth + 1), name + ': no horizontal overflow');
  check(await page.locator('.offers h1').count() === 1, name + ': one screen title');
  check(await page.locator('.offers nav a').count() === 5, name + ': five simple destinations');
  check(await page.locator('form[method=post]').evaluateAll(forms => forms.every(f => !!f.querySelector('[name=csrf]'))), name + ': CSRF on every mutation form');
  await page.screenshot({path:path.join(config.output,name+'.png'),fullPage:true});
  checks.push(name + ': captured ' + label);
 }
 try {
  const anonymous = await browser.newContext({ignoreHTTPSErrors:true});
  const anon = await anonymous.newPage();
  const denied = await anon.goto(config.base+'/flora/offers'); check(denied.status()===403,'anonymous denied private pilot');
  await anonymous.close();
  if (config.baseline) {
   const publicContext = await browser.newContext({ignoreHTTPSErrors:true});
   const original = await publicContext.newPage(); const current = await publicContext.newPage();
   const parityPaths = ['/industries/banking','/industries/aviation','/enterprises/lloyds','/enterprises/easyjet','/industries/technology/experience'];
   for (const [device, viewport] of Object.entries({desktop:{width:1440,height:1000},ipad:{width:1024,height:1366},mobile:{width:390,height:844}})) {
    await original.setViewportSize(viewport); await current.setViewportSize(viewport);
    for (const route of parityPaths) {
     const before = await original.goto(config.baseline+route); const after = await current.goto(config.base+route);
     check(before.status()===200 && after.status()===200,device+' '+route+': existing public journey accessible');
     await original.bringToFront(); await original.evaluate(()=>document.fonts.ready);
     const first = await original.screenshot({fullPage:true,animations:'disabled',caret:'hide'});
     await current.bringToFront(); await current.evaluate(()=>document.fonts.ready);
     const second = await current.screenshot({fullPage:true,animations:'disabled',caret:'hide'});
     if(sha(first)!==sha(second)){fs.writeFileSync(path.join(config.output,'diagnostic-before.png'),first);fs.writeFileSync(path.join(config.output,'diagnostic-after.png'),second);}
     check(sha(first)===sha(second),device+' '+route+': pixels identical to main');
     if(route==='/industries/technology/experience') fs.writeFileSync(path.join(config.output,device+'-before-technology.png'),first);
    }
    await original.goto(config.baseline+'/opportunities');
    await original.screenshot({path:path.join(config.output,device+'-before-opportunities.png'),fullPage:true});
    await current.goto(config.base+'/opportunities');
    await current.screenshot({path:path.join(config.output,device+'-after-opportunities.png'),fullPage:true});
   }
   await publicContext.close();
  }
  for (const [device, viewport] of Object.entries({desktop:{width:1440,height:1000},ipad:{width:1024,height:1366},mobile:{width:390,height:844}})) {
   const context = await browser.newContext({ignoreHTTPSErrors:true,viewport, deviceScaleFactor:1});
   const page = await login(context, 'preview-seller');
   const screens = [
    ['catalogue','/flora/offers','catalogue with illustrative approved fixture offers'],
    ['company','/flora/offers/company','authorised employer selection'],
    ['variation','/flora/offers/edit?offer='+config.private_id,'private variation and protected parent'],
    ['offer-led','/flora/offers/discover?mode=offer&selected='+config.first_offer,'offer-led discovery'],
    ['account-led','/flora/offers/discover?mode=account&selected=lloyds','account-led discovery'],
    ['studio-off','/flora/offers/studio','default-disabled creative Studio']
   ];
   for (const [name, route, label] of screens) {
    const response = await page.goto(config.base+route); check(response.status()===200,device+' '+name+': authorised 200');
    await capture(page, device+'-'+name, label);
    if(name==='variation') {
     check(await page.locator('textarea[name=capabilities]').count()===0,device+': protected parent capability not editable');
     check(await page.locator('[name=entry_play]').count()===1,device+': variation entry play editable');
    }
    if(name==='offer-led') {
     const ids = await page.locator('[data-assessment-id]').evaluateAll(nodes=>nodes.map(n=>n.dataset.assessmentId));
     check(ids.length===3 && new Set(ids).size===3,device+': three unique account matches');
     await page.locator('details').filter({has:page.locator('summary', {hasText:'Assessment, uncertainty and sources'})}).first().locator('summary').click();
     check(await page.getByText('Counter-indicators:',{exact:false}).first().isVisible(),device+': counter-indicators inspectable');
    }
    if(name==='studio-off') check(await page.getByText('Off by default',{exact:false}).count()>0,device+': Studio initially disabled');
    await page.keyboard.press('Control+Home');
    await page.locator('.offers nav a').first().focus();
    check(await page.evaluate(()=>document.activeElement.matches('.offers nav a')),device+' '+name+': keyboard navigation focus');
    await page.keyboard.press('Tab');
    check(await page.evaluate(()=>document.activeElement.matches('.offers nav a')),device+' '+name+': tab reaches next destination');
   }
   // A real browser POST exercises version creation and approval submission.
   await page.goto(config.base+'/flora/offers/edit?template=consulting');
   await page.locator('[name=name]').fill('Synthetic browser-created private offer '+device);
   await Promise.all([page.waitForURL('**/flora/offers/edit?offer=*'), page.getByRole('button',{name:'Save new private version'}).click()]);
   check(await page.getByText('private draft · v1',{exact:false}).count()>0,device+': browser creates private version');
   await Promise.all([page.waitForURL('**/flora/offers'),page.getByRole('button',{name:'Submit for employer review'}).click()]);
   check(await page.getByText('submitted for review',{exact:false}).count()>0,device+': browser submits separately');
   await context.close();
  }
  const ownerContext = await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:1440,height:1000}});
  const owner = await login(ownerContext,'preview-owner');
  await owner.goto(config.base+'/flora/offers/company');
  await owner.getByText('Owner: authorise company context',{exact:true}).click();
  check(await owner.locator('[name=organisation]').count()===1,'owner setup uses existing EmployerContext without imported Twin');
  await Promise.all([owner.waitForURL('**/flora/offers/company'),owner.getByRole('button',{name:'Save declared company context'}).click()]);
  await owner.getByText('Owner: authorise company context',{exact:true}).click();
  check(await owner.locator('[name=organisation]').inputValue()==='Illustrative UK services company','browser saves declared profile separately from employer binding');
  for (const [device, viewport] of Object.entries({desktop:{width:1440,height:1000},ipad:{width:1024,height:1366},mobile:{width:390,height:844}})) {
   await owner.setViewportSize(viewport); await capture(owner,device+'-owner-setup','owner declaration and separate employer binding');
  }
  await ownerContext.close();
  const reviewerContext = await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:1440,height:1000}});
  const reviewer = await login(reviewerContext,'preview-reviewer');
  await reviewer.goto(config.base+'/flora/offers/review');
  await capture(reviewer,'desktop-review','separate delegated employer review');
  check(await reviewer.getByText('Banking service resilience',{exact:true}).count()===0,'reviewer cannot see private variation');
  for (const [device, viewport] of Object.entries({ipad:{width:1024,height:1366},mobile:{width:390,height:844}})) {
   await reviewer.setViewportSize(viewport); await capture(reviewer,device+'-review','separate employer review');
  }
  await reviewerContext.close();
  const studioContext = await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:1440,height:1000}});
  const studio = await login(studioContext,'preview-seller');
  await studio.goto(config.base+'/flora/offers/studio');
  await Promise.all([studio.waitForURL('**/flora/offers/studio'), studio.getByRole('button',{name:'Enable for me in this workspace'}).click()]);
  await studio.locator('[name=first]').selectOption(config.first_offer+':3');
  await studio.locator('[name=second]').selectOption(config.second_offer+':3');
  await Promise.all([studio.waitForURL('**/flora/offers/edit?offer=*'),studio.getByRole('button',{name:'Save private combination draft'}).click()]);
  check(await studio.getByText('private draft · v1',{exact:false}).count()>0,'Studio saves a private composite');
  for (const [device, viewport] of Object.entries({desktop:{width:1440,height:1000},ipad:{width:1024,height:1366},mobile:{width:390,height:844}})) {
   await studio.setViewportSize(viewport); await capture(studio,device+'-composite','private version-pinned combination draft');
  }
  await studio.goto(config.base+'/flora/offers/studio');
  await Promise.all([studio.waitForURL('**/flora/offers/studio'),studio.getByRole('button',{name:'Disable Studio',exact:true}).click()]);
  check(await studio.getByText('Off by default',{exact:false}).count()>0,'Studio opt-in reversible');
  await studioContext.close();
  check(errors.length===0,'no browser page errors');
  fs.writeFileSync(path.join(config.output,'Browser-Checks.json'),JSON.stringify({devices:['1440x1000','1024x1366','390x844'],checks,passed:checks.length,failed:0,authority:'isolated synthetic fixture; no real company approvals or customer leads'},null,2)+'\n');
  console.log(checks.length+' responsive/owner browser checks passed');
 } finally { await browser.close(); }
})().catch(e=>{console.error(e.message);process.exit(1)});
