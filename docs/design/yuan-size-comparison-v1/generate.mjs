// Review-only sandbox. Never writes the running website's src/, public/, or UI.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
const root=process.cwd(),out=path.join(root,'docs/design/yuan-size-comparison-v1');
const baseline=JSON.parse(fs.readFileSync('src/data/yuan-plan.json'));
for(const [id,factor] of [['a',.85],['b',.75]]){
 const dest=path.join(root,'work/yuan-size',id);fs.mkdirSync(dest,{recursive:true});
 for(const item of ['src','public','scripts','test','docs/design/yuan-masterplan-v1'])fs.cpSync(path.join(root,item),path.join(dest,item),{recursive:true});
 for(const item of ['index.html','package.json','vite.config.js'])fs.copyFileSync(path.join(root,item),path.join(dest,item));
 if(!fs.existsSync(path.join(dest,'node_modules')))fs.symlinkSync(path.join(root,'node_modules'),path.join(dest,'node_modules'),'dir');
 const plan=structuredClone(baseline);
 // Coordinates already contain the PR #4 compression. Apply ONLY this new factor.
 for(const n of plan.nodes){n.x*=factor;n.z*=factor;}
 for(const e of plan.edges)e.controlPointsXZ=e.controlPointsXZ.map(p=>p.map(v=>v*factor));
 // Metadata used only for sampling density, never a second coordinate transform.
 plan.compressionXZ=baseline.compressionXZ*factor;
 plan.review={baseCommit:'860cf7a57a6d65771bbb445ea04493c219047a56',relativeScaleXZ:factor,radiiAndModelsUnchanged:true};
 fs.writeFileSync(path.join(dest,'src/data/yuan-plan.json'),JSON.stringify(plan,null,2)+'\n');
 execFileSync(process.execPath,['scripts/build-yuan-world.mjs'],{cwd:dest,stdio:'pipe'});
 const target=path.join(out,id);fs.mkdirSync(target,{recursive:true});
 for(const name of ['yuan-plan.json','yuan-layout.json','yuan-surface.json'])fs.copyFileSync(path.join(dest,'src/data',name),path.join(target,name));
 console.log(id,'sandbox generated at',dest);
}
