const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(process.env.TRACESOL_PLAYWRIGHT||'playwright');
(async()=>{const browser=await chromium.launch({headless:true,...(process.env.TRACESOL_BROWSER?{channel:process.env.TRACESOL_BROWSER}:{})});try{const page=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});await page.goto(pathToFileURL(path.resolve(__dirname,'../submission/cover.html')).href);await page.screenshot({path:path.resolve(__dirname,'../submission/screenshots/00-tracesol-cover.png')});console.log('Cover saved at 1200 × 630 pixels.');}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
