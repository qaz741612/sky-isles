import{auditWorldSpaces}from'./helpers/world-spaces-audit.js';
import {test,expect} from './helpers/software-qa.js';
import fs from 'node:fs';
test('eight current places: authored public circuits, accessible exterior guards and camera orbit',async({page,isMobile})=>{
 test.setTimeout(420000);const outputDir=process.env.SKYISLES_QA_OUTPUT_DIR??'docs/previews/transport-station-glb-integration-v1';fs.mkdirSync(outputDir,{recursive:true});const progress=`${outputDir}/spaces-progress-${isMobile?'mobile':'desktop'}.ndjson`;fs.writeFileSync(progress,'');page.on('console',msg=>{const text=msg.text();if(text.startsWith('SPACE_QA '))fs.appendFileSync(progress,text.slice(9)+'\n');});await page.goto('/');await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();if(await page.locator('#touch-help').isVisible())await page.locator('#help-close').click();
 const result=await page.evaluate(auditWorldSpaces);
 expect(result.records).toHaveLength(8);expect(result.respawns).toBe(0);const folder=process.env.SKYISLES_QA_OUTPUT_DIR??'docs/previews/transport-station-glb-integration-v1';fs.mkdirSync(folder,{recursive:true});fs.writeFileSync(`${folder}/spaces-${isMobile?'mobile':'desktop'}.json`,JSON.stringify(result,null,2));
});
