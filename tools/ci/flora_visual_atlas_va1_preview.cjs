const {chromium}=require('playwright');const fs=require('fs'),path=require('path'),assert=require('assert');
const out=path.resolve(__dirname,'../../docs/flora-runtime/visual-atlas-va1/previews');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});const checks=[];const ctx=await b.newContext({javaScriptEnabled:false});const p=await ctx.newPage();
for(const [device,size] of Object.entries({desktop:{width:1440,height:1000},'ipad-landscape':{width:1194,height:834},'ipad-portrait':{width:834,height:1194},mobile:{width:390,height:844},'mobile-320':{width:320,height:780}})){
 await p.setViewportSize(size);
 for(const a of ['a','b','c']) for(const scope of ['uk','banking','technology','lloyds','nvidia','government']){
 const id=`${a}-${scope}`,url=`http://127.0.0.1:8776/${id}.html`;assert.equal((await p.goto(url)).status(),200);await p.evaluate(()=>document.fonts.ready);
 assert(await p.locator('h1').isVisible());assert.equal(await p.locator('header nav a').count(),5);
 const overflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);assert(!overflow,device+' '+id+' overflow');
 assert.equal(await p.locator('main .stats .stat').count(),3);assert.equal(await p.locator('svg a').count(),6);
 await p.screenshot({path:path.join(out,`${device}-${id}.jpg`),type:'jpeg',quality:75,fullPage:true});
 checks.push({device,id,status:'pass',noJS:true,checks:['loads','headline','five tool links','three metric slots','six landscape anchors','no horizontal overflow']});
 }
}
await p.setViewportSize({width:720,height:500});for(const a of ['a','b','c']){await p.goto(`http://127.0.0.1:8776/${a}-uk.html`);assert(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth));await p.keyboard.press('Tab');assert.equal(await p.evaluate(()=>document.activeElement.textContent),'Skip to content');await p.keyboard.press('Enter');assert.equal(await p.evaluate(()=>document.activeElement.id),'main');await p.screenshot({path:path.join(out,`zoom-200-${a}-uk.jpg`),quality:75,fullPage:true});checks.push({id:a,zoomEquivalent:'1440 CSS viewport at 200% = 720 CSS px',keyboardSkip:'pass'});}
await p.goto('http://127.0.0.1:8776/a-uk.html');await p.getByRole('link',{name:'Banking →'}).click();assert(p.url().includes('a-banking'));await p.getByRole('link',{name:'Lloyds Banking Group →',exact:false}).first().click();assert(p.url().includes('a-lloyds'));
fs.writeFileSync(path.join(out,'Browser-Checks.json'),JSON.stringify({pages:90,assertions:540,zoomKeyboardCases:3,journey:'UK → Banking → Lloyds',checks},null,2));await b.close();console.log('90 responsive pages / 540 assertions + 3 zoom/keyboard cases + UK → Banking → Lloyds journey passed');})().catch(e=>{console.error(e);process.exit(1)});
