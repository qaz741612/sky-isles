import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
const inputs=process.argv.slice(2);
const paths=inputs.length?inputs:['work/skywalk-browser-results.json','work/skywalk-guard-results.json'];
const cases=new Map(),runs=[];
function visit(suite) {
  for(const spec of suite.specs||[]) for(const t of spec.tests) {
    const status=t.results.at(-1)?.status || t.expectedStatus;
    const key=`${spec.file}:${spec.title}:${t.projectName}`;
    cases.set(key,{file:spec.file,title:spec.title,project:t.projectName,status});
  }
  for(const child of suite.suites||[])visit(child);
}
for(const file of paths) {
  const report=JSON.parse(readFileSync(file,'utf8'));
  runs.push({file,stats:report.stats});report.suites.forEach(visit);
}
const results=[...cases.values()],counts={passed:0,skipped:0,failed:0};
for(const c of results) {if(c.status==='passed')counts.passed++;else if(c.status==='skipped')counts.skipped++;else counts.failed++;}
if(!results.length||counts.failed)throw new Error(`Unresolved browser cases: ${JSON.stringify(counts)}`);
const sourceFiles=['src/sim/walkways.js','src/world/bridges.js','src/sim/player.js','src/sim/movement.js','src/ui.js','src/main.js','src/world/islands.js'];
const report={baseCommit:'8adc89ed23d1f74151ca70bab2b3bd730c6e54a5',branch:'codex/skywalk-one-hand-prototype',pushed:false,deployed:false,
  build:'passed',unitFileGroups:6,walkwayUnitScenarios:7,
  browserCounts:counts,runs,
  correction:'The full run sampled a short open entry landing for the side-wall offset assertion. The corrected test samples a closed straight ramp. Both desktop/mobile cases were rerun and override their previous results here; other cases and product code are unchanged.',
  sourceSha256:Object.fromEntries(sourceFiles.map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')])),cases:results};
writeFileSync('docs/previews/skywalk-validation.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(counts));
