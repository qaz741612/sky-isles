import{auditR21Arrival}from'./helpers/r21-arrival-audit.js';
import{test,expect}from'./helpers/software-qa.js';import fs from'node:fs';
test('final R21 arrival: original-profile landmarks, continuous gate-to-guide camera, manual orbit, dry checkpoint and panorama',async({page,isMobile})=>{
 test.setTimeout(600000);const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:180000});
 const report=await page.evaluate(auditR21Arrival);expect(report.rows).toHaveLength(4);expect(errors).toEqual([]);const dir=process.env.SKYISLES_QA_OUTPUT_DIR??'docs/previews/bdeh-r21/final-qa/regression';fs.mkdirSync(dir,{recursive:true});fs.writeFileSync(`${dir}/continuous-camera-${isMobile?'mobile':'desktop'}.json`,JSON.stringify({...report,errors})+'\n');
});
