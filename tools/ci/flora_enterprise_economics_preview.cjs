const fs = require('fs');
const {chromium} = require('playwright');
const cfg = JSON.parse(fs.readFileSync(process.argv[2]));
const assert = (ok, message) => { if (!ok) throw Error(message); };
const views = [['desktop',1440,1000],['ipad-landscape',1180,820],['ipad-portrait',820,1180],['mobile',390,844],['mobile-320',320,740]];
// Exercise the retained A1 component explicitly; CEO default has its own proof.
const banks = '/enterprises/lloyds?stream=landscape&detail=funding';
const airline = '/enterprises/easyjet/preview?stream=landscape';
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CI ? undefined : '/usr/bin/chromium', args:['--no-sandbox']});
  let checks = 0;
  const check = (ok, message) => { assert(ok, message); checks++; };
  try {
    for (const [label,width,height] of views) {
      const page = await browser.newPage({viewport:{width,height},hasTouch:label!=='desktop',reducedMotion:'reduce',javaScriptEnabled:label!=='mobile-320'});
      for (const [company,route,stage] of [['lloyds',banks,'profit-costs'],['easyjet',airline,'airline-return']]) {
        const response = await page.goto(cfg.base+route);
        check(response.status()===200,company+' route');
        check(response.headers()['cache-control']==='no-store','no browser cache');
        if (cfg.before) {
          await page.screenshot({path:`${cfg.output}/before-${company}-${label}.jpg`,quality:78});
          continue;
        }
        if(label==='ipad-portrait') {
          const left=page.locator('#left .compact-scene > summary');
          await left.click();
          await page.screenshot({path:`${cfg.output}/left-open-${company}-${label}.jpg`,quality:78});
          await left.click();
        }
        check(await page.locator('[data-region=top]').count()===1,'one Top');
        check(await page.locator('[data-region=left]').count()===1,'one Left');
        check(await page.locator('[data-region=main]').count()===1,'one Main');
        check(await page.locator('.econ-stages a').count()===3,'three economic stages');
        check(await page.locator('.econ-stages [aria-current=page]').count()===1,'one selected stage');
        check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no horizontal overflow');
        await page.screenshot({path:`${cfg.output}/after-${company}-facts-${label}.jpg`,quality:78});
        const target=page.locator(`.econ-stages a[data-stage="${stage}"]`);
        const bounds=await target.boundingBox();
        check(bounds.width>=44&&bounds.height>=44,'economic stage touch target');
        if(label==='desktop') {
          await target.focus();
          check(await target.evaluate(el=>getComputedStyle(el).outlineStyle)==='solid','visible keyboard focus');
          await page.keyboard.press('Enter');
        }
        else { await target.tap(); }
        await page.waitForURL(url=>url.searchParams.get('detail')===stage);
        check(new URL(page.url()).searchParams.get('detail')===stage,'stage deep link');
        check(await page.locator('.econ-stages [aria-current]').getAttribute('data-stage')===stage,'selection follows URL');
        check(await page.getByRole('navigation',{name:'Reading mode',exact:true}).count()===0,'one unified presentation');
        const unified = await page.locator('main').innerText();
        await page.goto(page.url().split('#')[0]+'&reading=insight');
        await page.waitForURL(url=>url.searchParams.get('reading')==='insight');
        check(new URL(page.url()).searchParams.get('detail')===stage,'legacy link preserves stage');
        check(await page.locator('main').innerText()===unified,'legacy reading URL has identical intelligence');
        check(await page.locator('.econ-focus [data-semantic-type=insight]').count()===1,'insight semantic label');
        await page.screenshot({path:`${cfg.output}/after-${company}-insight-${label}.jpg`,quality:78});
        await page.goBack(); await page.goForward(); await page.reload();
        check(new URL(page.url()).searchParams.get('reading')==='insight','back forward reload');
        const disclosure=page.locator('.econ-basis > summary');
        check(await disclosure.count()===0,'executive canvas has no evidence accordion');
        check(!(await page.locator('main').innerText()).match(/£11\.084bn|£477\.5bn|3\.21%|£10,106|£665m/),'no restricted or research-only financial outputs');
        await page.getByRole('link',{name:'Close economic detail',exact:true}).click();
        await page.waitForURL(url=>!url.searchParams.has('detail'));
        check(new URL(page.url()).pathname===(company==='lloyds'?'/enterprises/lloyds':'/enterprises/easyjet/preview'),'close preserves enterprise');
        for(const forbidden of ['workspace=private','run_id=fi-private','export=csv']) {
          check([403,404].includes((await page.request.get(cfg.base+route+'&'+forbidden)).status()),'unsupported/private query denied');
        }
        if(label==='mobile') {
          await page.evaluate(()=>document.documentElement.style.zoom='2');
          check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'200 percent zoom');
          await page.screenshot({path:`${cfg.output}/zoom-${company}.jpg`,quality:78});
          await page.evaluate(()=>document.documentElement.style.zoom='1');
        }
      }
      await page.close();
      console.log('PASS '+label+(cfg.before?' baseline':''));
    }
    if(!cfg.before) {
      const page=await browser.newPage({viewport:{width:1440,height:1000}});
      for(const [company,route,domain,id,values] of [
        ['lloyds',banks,'banking','PR-LBG-Q326',['£502.8bn','£6.6bn','£6.3bn']],
        ['easyjet',airline,'aviation','SRC-AV-AR25',['356 aircraft','1,202 routes']]
      ]) {
        await page.goto(cfg.base+route);
        const before=await page.content();
        check(values.every(x=>before.includes(x)),'released inputs visible before withdrawal');
        await page.goto(cfg.base+'/?stream=landscape');
        const file=`${cfg.repo}/enterprise-knowledge/${domain}/research-model/Assessment-Overlay.json`;
        const original=fs.readFileSync(file);
        try {
          const data=JSON.parse(original);
          data.sources.find(x=>x.id===id).withdrawn=true;
          fs.writeFileSync(file,JSON.stringify(data));
          await page.goBack();
          await page.waitForLoadState('load');
          await page.locator('.econ-stages a').first().waitFor();
          let html=await page.content();
          check(values.every(x=>!html.includes(x)),'Back revalidates current source; no stale hidden or accessible values');
          await page.reload();
          await page.emulateMedia({media:'print'});
          html=await page.content();
          check(values.every(x=>!html.includes(x)),'withdrawal removes print/evidence/ARIA representations');
          await page.screenshot({path:`${cfg.output}/withdrawn-${company}.jpg`,quality:78});
          await page.emulateMedia({media:'screen'});
          await page.reload();
          check(await page.locator('.econ-stages a').count()===3,'illustrative model survives withdrawal');
        } finally { fs.writeFileSync(file,original); }
      }
      await page.close();
    }
    fs.writeFileSync(`${cfg.output}/${cfg.before?'Before':'Browser'}-Checks.json`,JSON.stringify({checks,viewports:views,liveServices:false},null,2)+'\n');
  } finally { await browser.close(); }
})().catch(e=>{console.error(e.message);process.exit(1)});
