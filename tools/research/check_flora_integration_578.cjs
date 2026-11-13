/* Isolated public banner check. No remote requests or production writes. */
const {chromium}=require('playwright'),fs=require('fs'),assert=require('node:assert/strict'),path=require('path');
(async()=>{
 const [base,out]=process.argv.slice(2),origin=new URL(base);
 if(origin.protocol!=='http:'||!['127.0.0.1','localhost'].includes(origin.hostname))throw Error('Local origins only');
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const checks=[],external=[],writes=[];
 try{
  for(const [device,viewport] of Object.entries({desktop:{width:1440,height:1000},ipad:{width:1024,height:1366},mobile:{width:390,height:844}})){
   const context=await browser.newContext({viewport,javaScriptEnabled:false});
   await context.route('**/*',route=>{const req=route.request();if(new URL(req.url()).origin!==origin.origin){external.push(req.url());return route.abort();}if(req.method()!=='GET')writes.push(req.method());return route.continue();});
   const page=await context.newPage();
   for(const [key,suffix] of [['cloud','/district?district=cloud'],['all','/participants']]){
    const response=await page.goto(base+'/industries/technology/experience'+suffix);assert.equal(response.status(),200);
    const banner=page.locator('.commercial-sector-banner');assert.equal(await banner.count(),1);
    const rect=await banner.boundingBox(),table=await page.locator('.commercial-table').boundingBox();
    assert(rect.height>=44&&rect.height<=88);assert(rect.y+rect.height<table.y);
    assert.equal(await banner.locator('img').getAttribute('src'),'/industries/technology/experience/assets/artwork');
    assert.equal(await page.locator('h1').count(),1);assert(await page.locator('.commercial-table tbody tr').count()>0);
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await banner.focus();assert(await banner.evaluate(el=>el===document.activeElement));
    await Promise.all([page.waitForURL(base+'/industries/technology/experience'),page.keyboard.press('Enter')]);assert.equal(new URL(page.url()).pathname,'/industries/technology/experience');
    await page.goto(base+'/industries/technology/experience'+suffix);
    await page.screenshot({path:path.join(out,device+'-'+key+'-banner.png'),fullPage:true});
    await page.getByRole('link',{name:'Participant ↕',exact:true}).click();assert.equal(await page.locator('th[aria-sort=descending]').count(),1);
    checks.push({device,screen:key,banner_height:rect.height,native_keyboard:true,native_sort:true,overflow:false});
   }
   await context.close();
  }
  assert.equal(external.length,0);assert.equal(writes.length,0);
  fs.writeFileSync(path.join(out,'Banner-Checks.json'),JSON.stringify({passed:checks.length,checks,external_requests:0,network_writes:0},null,2)+'\n');
  console.log(checks.length+' responsive no-JavaScript banner/sort/keyboard scenarios passed');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1)});
