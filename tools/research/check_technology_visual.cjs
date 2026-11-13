const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const out=process.argv[3];if(!out)throw Error('Usage: node check_technology_visual.cjs http://127.0.0.1:PORT OUTPUT');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1080},deviceScaleFactor:1});const errors=[],results=[];
 page.on('pageerror',e=>errors.push(String(e)));const base=process.argv[2];const target=new URL(base);if(target.protocol!=='http:'||!['127.0.0.1','localhost'].includes(target.hostname))throw Error('Local isolated preview required');
 async function visit(path){const r=await page.goto(base+path);if(r.status()!=200)throw Error(path+' '+r.status());await page.waitForLoadState('networkidle');if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw Error('overflow '+path+' '+page.viewportSize().width);results.push({path,width:page.viewportSize().width,status:r.status(),overflow:false});}
 for(const [lens,name] of [['how','how-it-works'],['uses','who-uses-what'],['work','where-work-may-emerge']]){
  await visit('/industries/technology?lens='+lens);await page.screenshot({path:out+'/'+name+'-desktop.png',fullPage:true});
 }
 await visit('/industries/technology');await page.locator('.scene-role.ai:visible').focus();await page.keyboard.press('Enter');await page.waitForURL('**segment=ai#landscape');if(!await page.locator('.tech-inspector').innerText().then(s=>s.includes('AI & decisions')))throw Error('keyboard role selection');
 await page.locator('.tech-inspector a').filter({hasText:'Microsoft'}).click();await page.waitForURL('**provider=microsoft#provider');
 await visit('/industries/technology?lens=uses&relationship=programme-67-5');await page.getByRole('link',{name:'Open existing Lloyds Banking Group enterprise →'}).click();await page.waitForURL('**/enterprises/lloyds');
 await visit('/industries/technology?lens=uses&relationship=programme-202-1');await page.getByRole('link',{name:'Open existing easyJet enterprise →'}).click();await page.waitForURL('**/enterprises/easyjet');
 await visit('/industries/technology?lens=work');await page.locator('.world-wide [data-theme="theme-2"]').click();await page.locator('#theme-2 li a').first().click();await page.waitForURL('**relationship=programme-213-1#programme');if(!await page.locator('.tech-programme').innerText().then(s=>s.includes('Aviva')))throw Error('theme programme');
 await page.getByRole('link',{name:'Inspect research passage & source limits'}).click();const id=await page.evaluate(()=>decodeURIComponent(location.hash.slice(1)));if(!await page.locator('[id="'+id+'"]').evaluate(e=>e.open))throw Error('source disclosure not open');
 for(const [width,height,label] of [[1024,900,'tablet'],[768,1024,'portrait-tablet'],[390,844,'mobile']]){
  await page.setViewportSize({width,height});
  for(const [lens,name] of [['how','how-it-works'],['uses','who-uses-what'],['work','where-work-may-emerge']]){await visit('/industries/technology?lens='+lens);await page.screenshot({path:out+'/'+name+'-'+label+'.png',fullPage:true});}
  for(const p of ['/industries/technology/providers?provider=tcs-diligenta','/industries/technology/models?model=2','/industries/technology/timeline','/industries/technology/evidence','/industries/banking','/industries/aviation','/enterprises/lloyds','/enterprises/easyjet'])await visit(p);
 }
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:1024,height:900}});const nj=await nojs.newPage();await nj.goto(base+'/industries/technology');await nj.locator('.scene-role.cyber:visible').click();if(!(await nj.locator('.tech-inspector').innerText()).includes('Cyber & resilience'))throw Error('no JS selection');
 await page.setViewportSize({width:1440,height:1080});await visit('/industries/technology?lens=uses&relationship=programme-222-4');await page.emulateMedia({reducedMotion:'reduce'});await page.pdf({path:out+'/programme-print.pdf',format:'A4',printBackground:true});
 if(errors.length)throw Error(JSON.stringify(errors));
 fs.writeFileSync(out+'/Browser-Results.json',JSON.stringify({base,results,errors,keyboardRoleSelection:true,providerDrill:true,existingLloydsAndEasyjetNavigation:true,themeProgrammeEvidenceDrill:true,noJavaScriptRoleSelection:true,printGenerated:true,limitations:['Chromium only; physical iPad/Safari and assistive-technology user testing not performed','No owner comprehension or independent source-factuality acceptance claimed']},null,2)+'\n');await browser.close();console.log('PASS',results.length,'view checks; keyboard, no-JS, source and existing-enterprise journeys.');
})().catch(e=>{console.error(e);process.exit(1)});
