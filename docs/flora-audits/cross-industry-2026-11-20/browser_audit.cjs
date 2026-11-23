const fs=require('fs'),{chromium}=require('playwright');
const cfg=JSON.parse(fs.readFileSync(process.argv[2]));
const routes=[
 ['uk','/'],['catalogue','/industries'],['banking','/industries/banking'],
 ['nationwide','/industries/banking?selected=nationwide'],['natwest','/industries/banking?selected=natwest'],
 ['lloyds','/enterprises/lloyds'],['lloyds-inside','/enterprises/lloyds?stream=inside'],
 ['aviation-industry','/industries/aviation'],['easyjet-legacy','/enterprises/easyjet'],
 ['easyjet-visual','/enterprises/easyjet/preview'],
 ['easyjet-fleet','/enterprises/easyjet/preview?stream=inside&detail=fleet-operations'],
 ['technology','/industries/technology/experience'],
 ['technology-comparison','/industries/technology/experience/participants'],
 ['nvidia','/industries/technology/experience/enterprise?enterprise=nvidia'],
 ['equinix','/industries/technology/experience/enterprise?enterprise=equinix'],
 ['digital-twins','/digital-twins']
];
const viewports=[['desktop',1440,1000],['ipad-landscape',1180,820],['ipad-portrait',820,1180],['mobile',390,844]];
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const observations=[],denials=[];
 try{
  for(const[device,width,height]of viewports){
   const page=await browser.newPage({viewport:{width,height},hasTouch:device!=='desktop',reducedMotion:'reduce'});
   for(const[label,path]of routes){
    const response=await page.goto(cfg.base+path);await page.evaluate(()=>document.fonts.ready);
    const metrics=await page.evaluate(()=>{
     const main=document.querySelector('main')||document.body;
     const visible=e=>e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden'&&![...e.closest('details')?[e.closest('details')]:[]].some(d=>!d.open&&!d.querySelector('summary')?.contains(e));
     return {headline:[...main.querySelectorAll('h1')].map(e=>e.innerText),
      regions:document.querySelectorAll('body>[data-region]').length,
      readingModes:[...document.querySelectorAll('.reading-mode a')].map(e=>e.innerText),
      primaryStreams:[...document.querySelectorAll('.stream-switcher a')].map(e=>e.innerText),
      overflow:document.documentElement.scrollWidth>innerWidth,
      imageCount:document.querySelectorAll('img').length,
      disclosures:main.querySelectorAll('details').length,
      visibleSourceLinks:[...main.querySelectorAll('a[href^="https:"]')].filter(visible).length,
      compactSceneClosed:!!document.querySelector('#left .compact-scene:not([open])'),
      wideSceneVisible:!!document.querySelector('#left .wide-scene')?.getClientRects().length,
      wordCount:main.innerText.trim().split(/\s+/).length};
    });
    observations.push({device,label,path,status:response.status(),...metrics});
   }
   await page.close();console.log('Audited '+device);
  }
  const page=await browser.newPage();
  for(const path of ['/industries/telecommunications','/industries/utilities','/industries/energy','/industries/insurance','/industries/media','/industries/sport','/industries/banking?stream=changing','/financial-intelligence','/digital-twins/bt-group-plc','/flora/offers']){
   const response=await page.request.get(cfg.base+path,{maxRedirects:0});denials.push({path,status:response.status()});
  }
  fs.writeFileSync(cfg.output,JSON.stringify({auditedMain:'03719d7573f087c65d9622719273aa4b89caf7d3',
   method:'Isolated localhost Guest GETs; no production, canonical acceptance, authentication provisioning or changes. Representative templates, not every enterprise/browser.',
   observations,unsupportedOrProtectedProbes:denials},null,2)+'\n');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exit(1)});
