// Isolated static prototype checks; all external traffic is blocked.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');const assert=require('assert');
const D=path.resolve(__dirname,'..'),root='http://127.0.0.1:8766/docs/flora-runtime/si1-615/prototype/';
const views=['uk-landscape','uk-forces','banking-landscape','banking-forces','lloyds-inside','lloyds-landscape','lloyds-forces'];
const sizes={desktop:[1440,1000],ipad_landscape:[1180,820],ipad_portrait:[820,1180],mobile:[390,844],narrow:[320,740]};
let checks=0;const results=[],errors=[],external=[];function check(ok,label){assert(ok,label);checks++;}
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 await context.route('**/*',route=>{const u=route.request().url();if(u.startsWith('http://127.0.0.1:8766/')||u.startsWith('data:'))route.continue();else{external.push(u);route.abort();}});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 for(const [size,[width,height]]of Object.entries(sizes)){
  await page.setViewportSize({width,height});
  for(const view of views){
   await page.goto(root+'FLORA-SI1-Walkthrough.html#'+view);await page.waitForFunction(()=>[...document.querySelectorAll('.prototype-pane:not([hidden]) img')].every(i=>i.complete&&i.naturalWidth>0));
   const pane=page.locator('.prototype-pane:not([hidden])');check(await pane.count()===1,size+' '+view+' visible pane');
   check(await pane.locator('.stream-switcher [aria-current="page"]').innerText()===view.split('-')[1].replace(/^./,c=>c.toUpperCase()),'active stream');
   check(await pane.locator('h1').count()===1,'one scope heading');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'no horizontal overflow '+size+' '+view);
   const expected=view.startsWith('lloyds')?3:2;
   check(await pane.locator('.agenda-card').count()===expected,'unpadded shared agenda');
   if(size==='desktop')await page.screenshot({path:path.join(D,'previews',view+'-desktop.png')});
   await pane.locator('.agenda-link').focus();await page.keyboard.press('Enter');
   check(await pane.locator('.leadership-agenda').evaluate(x=>x.open),'keyboard agenda reveal');
   check(await page.evaluate(()=>document.activeElement.id.endsWith('agenda-content')),'focus follows agenda');
   if(view.endsWith('landscape')||view==='lloyds-inside'){
    await page.evaluate(()=>document.activeElement.blur());await page.screenshot({path:path.join(D,'previews',view+'-agenda-'+size+'.png')});
    if(size==='desktop'){
     const before=await page.content();await page.evaluate(()=>document.querySelectorAll('.agenda-link,.leadership-agenda').forEach(n=>n.remove()));await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(D,'previews',view+'-before-desktop.png')});await page.reload();await page.goto(root+'FLORA-SI1-Walkthrough.html#'+view+'--agenda-content');
    }
   }
   const first=pane.locator('.issue-detail').first();await first.locator(':scope > summary').click();
   check(await first.evaluate(x=>x.open),'decision disclosure');
   const sources=first.locator('.issue-sources');await sources.locator(':scope > summary').click();
   check(await sources.locator('a').count()>0,'inspectable original sources');
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'source inspection wraps '+size);
   await first.locator(':scope > summary').focus();await page.keyboard.press('Escape');check(!await first.evaluate(x=>x.open),'Escape closes focused disclosure');
  }
  results.push({viewport:size,width,height,seven_views:'pass',keyboard:'pass',sources:'pass',overflow:'pass'});
 }
 // Direct two-step journey and native history.
 await page.goto(root+'FLORA-SI1-Walkthrough.html#uk-landscape');
 await page.locator('.prototype-pane:not([hidden]) .spot[data-research="banking"]').click();check(page.url().endsWith('#banking-landscape'),'UK -> Banking');
 await page.locator('.prototype-pane:not([hidden]) .spot[data-label-id="lloyds"]').click();check(page.url().endsWith('#lloyds-inside'),'Banking -> Lloyds direct');
 await page.goBack();check(page.url().endsWith('#banking-landscape'),'Back retains industry');await page.goForward();check(page.url().endsWith('#lloyds-inside'),'Forward retains enterprise');
 await page.goto(root+'FLORA-SI1-Walkthrough.html#banking-forces?layer=regulators&selected=lloyds');
 await page.locator('.prototype-pane:not([hidden]) .stream-switcher a').first().click();check(page.url().includes('banking-landscape?layer=regulators&selected=lloyds'),'stream switch preserves layer and selected bank');
 check(await page.locator('.prototype-pane:not([hidden]) .spot.selected').getAttribute('data-label-id')==='lloyds','selected bank visible');
 // Deep-link native optional focus panel, then close to the correct label.
 await page.goto(root+'FLORA-SI1-Walkthrough.html#lloyds-inside--focus-economics');
 check(await page.locator('#lloyds-inside--focus-economics').isVisible(),'deep-linked current insight');
 await page.locator('#lloyds-inside--focus-economics .close-insight').click();check(page.url().includes('label-economics'),'close returns to current label');
 // Negative source/applicability and quiet cases remain inspectable.
 await page.goto(root+'FLORA-SI1-Walkthrough.html#banking-landscape--negative-fr-law-lloyds');
 check(await page.locator('#banking-landscape--negative-fr-law-lloyds').evaluate(x=>x.open),'negative case deep link');
 await page.screenshot({path:path.join(D,'previews','negative-applicability.png')});
 // 200% equivalent CSS viewport and mobile touch.
 await page.setViewportSize({width:720,height:500});await page.goto(root+'FLORA-SI1-Walkthrough.html#lloyds-inside--agenda-content');check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'200% layout reflow');
 await page.screenshot({path:path.join(D,'previews','lloyds-agenda-200pct-reflow.png')});
 const touch=await browser.newContext({viewport:{width:820,height:1180},hasTouch:true,isMobile:true});const tp=await touch.newPage();await tp.goto(root+'FLORA-SI1-Walkthrough.html#lloyds-inside');await tp.locator('.prototype-pane:not([hidden]) .agenda-link').tap();check(await tp.locator('.prototype-pane:not([hidden]) .leadership-agenda').evaluate(x=>x.open),'touch agenda');await touch.close();
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:820,height:1180}});const np=await nojs.newPage();await np.goto(root+'lloyds-inside.html');await np.locator('.leadership-agenda > summary').click();check(await np.locator('.leadership-agenda').evaluate(x=>x.open),'native no-script disclosure');await np.locator('.stream-switcher a').nth(1).click();check(np.url().endsWith('lloyds-landscape.html'),'native no-script stream navigation');await nojs.close();
 await page.emulateMedia({reducedMotion:'reduce',forcedColors:'active'});await page.goto(root+'FLORA-SI1-Walkthrough.html#lloyds-inside--agenda-content');check(await page.locator('.prototype-pane:not([hidden]) .agenda-card').first().isVisible(),'forced colors visible');await page.screenshot({path:path.join(D,'previews','forced-colors.png')});
 check(errors.length===0,'no browser errors '+errors.join(','));check(external.length===0,'no external requests');
 const out={status:'pass',checks,viewports:results,additional:['direct journey','Back/Forward','deep links','selected-bank/layer preservation','keyboard focus and Escape','touch','native no-script static fallback','200% equivalent reflow','forced colors/reduced motion'],browser:'Chromium '+browser.version(),page_errors:errors,external_requests:external,limitations:['Automated structural/interaction checks, not a screen-reader user study or complete WCAG certification.','200% uses equivalent CSS viewport; physical browser/OS zoom still needs owner testing.','Static public design proof: no production routes, private IAM or real Pipeline writes exercised.']};
 fs.writeFileSync(path.join(D,'Browser-Validation.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({status:out.status,checks,previews:fs.readdirSync(path.join(D,'previews')).length}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
