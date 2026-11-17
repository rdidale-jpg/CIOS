const{chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const base=process.argv[2],out=process.argv[3],checks=[];fs.mkdirSync(out,{recursive:true});
const sizes={desktop:{width:1440,height:900},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:740}};
const check=(v,n)=>{assert(v,n);checks.push(n)};
(async()=>{const b=await chromium.launch({executablePath:process.env.VP2_CHROMIUM||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),args:['--no-sandbox']});try{
 const c=await b.newContext({hasTouch:true}),p=await c.newPage(),external=[];p.on('request',r=>{if(!r.url().startsWith(new URL(base).origin))external.push(r.url())});
 async function load(q=''){const r=await p.goto(base+q);check(r.status()===200,'static design200');await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode())))}
 async function shot(name){await p.screenshot({path:path.join(out,name+'.jpg'),fullPage:true,quality:82})}
 for(const[device,size]of Object.entries(sizes)){
  await p.setViewportSize(size);await load('?lens=changes&subject=banking&story=ctp');
  check(await p.getByRole('navigation',{name:'Insight view'}).locator('[aria-current=page]').innerText()==="What's changing?",device+' active stream');
  check(await p.locator('#rail button').count()===3,device+' exactly three historical developments');
  check((await p.locator('#window').innerText()).includes('context'),device+' historical context explicit');
  check((await p.locator('main').innerText()).includes('1 May–31 July 2026'),device+' stated historical period');
  check(!(await p.locator('main').innerText()).includes('This week'),device+' no false weekly edition');
  check(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),device+' no horizontal overflow');
  check(await p.locator('main details, main a[href^="https:"]').count()===0,device+' no source/admin clickdowns');
  check(await p.locator('img').evaluate(el=>el.naturalWidth>0),device+' approved artwork loaded');
  check(await p.locator('.streams a, #rail button, #subject, .brand, .global summary').evaluateAll(es=>es.every(e=>{const r=e.getBoundingClientRect();return r.width>=44&&r.height>=44})),device+' touch targets at least44px');
  check(await p.locator('.scene').evaluate(el=>el.open)===(size.width>900),device+' adaptive Left scene');
  await shot('banking-changes-'+device);
  for(const story of ['nationwide','lloyds']){await p.locator('[data-story='+story+']').click();check(new URL(p.url()).searchParams.get('story')===story,device+' one-action story '+story);check(await p.locator(':focus').getAttribute('data-story')===story,device+' story focus retained '+story);await shot(story+'-change-'+device)}
  await p.getByLabel('Banking focus').selectOption('nationwide');await p.getByRole('link',{name:'Forces',exact:true}).click();check(new URL(p.url()).searchParams.get('subject')==='nationwide',device+' focus survives stream');check(await p.getByLabel('Banking focus').inputValue()==='nationwide',device+' focus visible');check(!(await p.locator('#what').innerText()).includes('Designation'),device+' company focus not silently industry story');await shot('nationwide-forces-'+device);await p.goBack();check(new URL(p.url()).searchParams.get('lens')==='changes',device+' Back restores stream');await p.goForward();check(new URL(p.url()).searchParams.get('lens')==='forces',device+' Forward restores stream');
 }
 await load('?lens=changes&subject=nationwide&story=lloyds');check((await p.locator('h1').innerText()).includes('Nationwide'),'incompatible story filtered to exact subject');check(await p.locator('#rail button').count()===1,'enterprise focus does not inherit unrelated policy');
 await load('?lens=changes&subject=banking&story=ctp');await p.locator('[data-story=nationwide]').focus();await p.keyboard.press('Enter');check(new URL(p.url()).searchParams.get('story')==='nationwide','keyboard Enter selects story');check(await p.locator(':focus').getAttribute('data-story')==='nationwide','keyboard focus survives render');
 await p.locator('[data-story=lloyds]').focus();await p.keyboard.press('Space');await p.waitForFunction(()=>new URL(location.href).searchParams.get('story')==='lloyds');check(new URL(p.url()).searchParams.get('story')==='lloyds','keyboard Space selects story');
 await p.getByRole('link',{name:'Landscape',exact:true}).focus();await p.keyboard.press('Enter');check(new URL(p.url()).searchParams.get('lens')==='landscape','keyboard lens navigation');
 await p.setViewportSize(sizes.desktop);await load('?lens=changes&subject=banking');await p.getByRole('button',{name:'Lloyds Banking Group',exact:true}).click();check(await p.getByLabel('Banking focus').inputValue()==='lloyds','scene label shares single focus');check((await p.locator('h1').innerText()).includes('Lloyds'),'scene selection updates Main');
 await p.setViewportSize(sizes.mobile);await load('?lens=changes&subject=banking&story=nationwide');await p.evaluate(()=>{const es=[...document.querySelectorAll('body *')],s=es.map(e=>parseFloat(getComputedStyle(e).fontSize));es.forEach((e,i)=>e.style.setProperty('font-size',s[i]*2+'px','important'))});check(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'mobile200percent text reflows');await shot('mobile-200pct');
 check(external.length===0,'no remote assets/news/private service calls');check(await p.locator('main').count()===1&&await p.locator('header').count()===1,'semantic regions');
 await c.close();const nj=await b.newContext({javaScriptEnabled:false}),np=await nj.newPage();await np.goto(base);check((await np.locator('main').innerText()).includes('£2.026bn'),'no-JS factual text fallback');await nj.close();
 fs.writeFileSync(path.join(out,'Browser-Checks.json'),JSON.stringify({passed:checks.length,checks,sizes,scope:'Static design-only concept. Chromium/touch viewport and200percent text emulation; no application routes, private stores, live News, physical-iPad or runtime accessibility-compliance claim.'},null,2)+'\n');console.log(checks.length+' design checks passed');
}finally{await b.close()}})().catch(e=>{console.error(e.message);process.exit(1)});
