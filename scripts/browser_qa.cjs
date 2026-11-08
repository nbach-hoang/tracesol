/* Optional developer QA: npm install --no-save playwright; npx playwright install chromium.
   The app itself has no Node or Playwright dependency. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.TRACESOL_PLAYWRIGHT || 'playwright');
const root = path.resolve(__dirname,'..');
const output = path.join(root,'output');
const shots = path.join(root,'submission','screenshots');
fs.mkdirSync(output,{recursive:true});fs.mkdirSync(shots,{recursive:true});
const checks=[];
function passed(name){checks.push({name,status:'passed'});}
async function run(){
 const browser=await chromium.launch({headless:true,...(process.env.TRACESOL_BROWSER?{channel:process.env.TRACESOL_BROWSER}:{})});
 try{
 const context=await browser.newContext({viewport:{width:1440,height:1050},acceptDownloads:true});
 const page=await context.newPage();const errors=[];const external=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:8765')&&!r.url().startsWith('blob:'))external.push(r.url());});
 page.on('dialog',d=>d.accept());
 await page.goto('http://127.0.0.1:8765');
 await page.waitForFunction(()=>document.querySelector('#m-records').textContent==='12');
 assert.equal(await page.locator('#m-normalized').textContent(),'10');assert.equal(await page.locator('#m-conflicts').textContent(),'2');passed('Demo metrics: 12 records, 10 converted, 2 disagreeing pairs');
 await page.screenshot({path:path.join(shots,'01-evidence-workbench.png'),fullPage:true});
 await page.getByRole('button',{name:'Compare conditions',exact:false}).click();
 assert.equal(await page.locator('.compare-grid .panel').first().locator('.pair').count(),2);
 await page.screenshot({path:path.join(shots,'02-condition-comparisons.png'),fullPage:true});
 await page.locator('#threshold').selectOption('1');await page.waitForFunction(()=>document.querySelector('#m-conflicts').textContent==='0');
 await page.locator('#threshold').selectOption('0.5');await page.waitForFunction(()=>document.querySelector('#m-conflicts').textContent==='2');passed('Threshold sensitivity and exact-boundary behavior');
 await page.getByRole('button',{name:/Evidence library/}).click();
 await page.locator('#search').fill('caffeine');assert.equal(await page.locator('#evidence-body tr').count(),2);
 await page.locator('#search').fill('does-not-exist');assert.match(await page.locator('#evidence-body').textContent(),/No records match/);
 await page.locator('#search').fill('');await page.locator('#status-filter').selectOption('invalid');assert.equal(await page.locator('#evidence-body tr').count(),2);
 await page.locator('#status-filter').selectOption('all');passed('Search, empty-state, invalid-record filter');
 await page.getByRole('button',{name:'Inspect Quercetin, Q-03',exact:true}).click();
 await page.locator('#decision').selectOption('follow_up');await page.locator('#review-form button').click();assert.match(await page.locator('#review-error').textContent(),/Add a reason/);
 await page.locator('#review-note').fill('Synthetic demonstration: inspect the tenfold discrepancy against the original source; do not choose either value automatically.');
 await page.locator('#review-form button').click();await page.waitForFunction(()=>document.querySelector('#review-note')?.value.includes('tenfold'));
 await page.getByRole('button',{name:/Review decisions/}).click();await page.waitForSelector('.reviews-table');assert.match(await page.locator('.reviews-table').textContent(),/tenfold/);passed('Decision requires a reason and appears in review log');
 await page.screenshot({path:path.join(shots,'03-review-decisions.png'),fullPage:true});
 await page.getByRole('button',{name:'Save workspace',exact:true}).first().click();
 const downloadPromise=page.waitForEvent('download');await page.locator('#reviews-save').click();const saved=await downloadPromise;
 const savePath=path.join(output,'qa-workspace.json');await saved.saveAs(savePath);
 const workspace=JSON.parse(fs.readFileSync(savePath,'utf8'));assert.equal(workspace.reviews['row-3'].state,'follow_up');passed('Workspace export preserves review decisions');
 await page.getByRole('button',{name:/Evidence library/}).click();
 await page.getByRole('button',{name:'Inspect Quercetin, Q-03',exact:true}).click();await page.locator('#edit-record').click();await page.locator('#edit-value').fill('0.30224');
 await page.getByRole('button',{name:'Apply & recheck'}).click();await page.waitForFunction(()=>document.querySelector('#m-conflicts').textContent==='0');
 assert.equal(await page.locator('#decision').inputValue(),'pending');passed('Editing rechecks comparisons and resets the edited decision');
 assert.equal(await page.locator('#dataset-tag').textContent(),'SYNTHETIC DATA');
 await page.locator('#session-file').setInputFiles(savePath);await page.waitForFunction(()=>document.querySelector('#m-conflicts').textContent==='2');passed('Reopening workspace restores original dataset and recalculates');
 await page.locator('#export-open').click();
 for(const kind of ['json','csv','html']){
  const wait=page.waitForEvent('download');await page.locator(`[data-export="${kind}"]`).click();const item=await wait;const outPath=path.join(output,item.suggestedFilename());await item.saveAs(outPath);assert.ok(fs.statSync(outPath).size>100);passed(`${kind.toUpperCase()} audit export downloads successfully`);
 }
 await page.locator('#export-dialog .close-dialog').click();
 await page.locator('#import-open').click();await page.locator('#csv-text').fill('bad,header\n1,2');await page.getByRole('button',{name:'Analyze evidence →'}).click();assert.match(await page.locator('#import-error').textContent(),/Missing required columns/);passed('Malformed import produces an actionable error');
 const csv=fs.readFileSync(path.join(root,'data/demo.csv'),'utf8').replace('Quercetin','<img src=x onerror=window.BAD=1>');
 await page.locator('#csv-text').fill(csv);await page.getByRole('button',{name:'Analyze evidence →'}).click();await page.waitForSelector('#import-dialog:not([open])',{state:'attached'});
 assert.equal(await page.evaluate(()=>window.BAD),undefined);assert.equal(await page.locator('#evidence-body img').count(),0);passed('User-supplied markup is displayed as text, not executed');
 await page.locator('#load-demo').click();await page.waitForFunction(()=>document.querySelector('#dataset-tag').textContent==='SYNTHETIC DATA');
 for(const width of [1440,1024,768,390]){
  await page.setViewportSize({width,height:1000});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`Page overflow at ${width}px`);
  if(width===390){await page.locator('#toast').evaluate(el=>el.hidden=true);await page.screenshot({path:path.join(shots,'04-mobile-workbench.png'),fullPage:true});}
 }
 passed('Responsive layouts: 1440, 1024, 768, 390 pixels, no page overflow');
 await page.setViewportSize({width:1440,height:1050});
 await page.getByRole('button',{name:/Methods & limits/}).click();assert.match(await page.locator('#view-content').textContent(),/Unknown is not a match/);passed('Methods and scientific limitations available in app');
 assert.deepEqual(errors,[]);assert.deepEqual(external,[]);passed('No browser script errors or third-party network requests');
 await context.close();
 fs.writeFileSync(path.join(output,'browser-qa.json'),JSON.stringify({checked_at:new Date().toISOString(),browser:process.env.TRACESOL_BROWSER||'Playwright Chromium',checks},null,2));
 console.log(JSON.stringify({passed:checks.length,checks},null,2));
 }finally{await browser.close();}
}
run().catch(e=>{console.error(e);process.exitCode=1;});
