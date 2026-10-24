// Generate a true x/z plan, Chinese labels, heights and route statistics from source data.
import { writeFileSync } from 'node:fs';
import { ISLANDS } from '../src/world/islands.js';
import { planWalkways,WALKWAY } from '../src/sim/walkways.js';
const plans=planWalkways(ISLANDS),names=['交通大升級','安心生養','幸福養老','產業青年','宜居環境','智慧公所','治水防災','教育發展'];
const px=x=>465+x*8,py=z=>480+z*8;
let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="950" viewBox="0 0 1000 950"><rect width="1000" height="950" fill="#f6f0f8"/><g font-family="sans-serif" fill="#51446b"><text x="32" y="44" font-size="26" font-weight="bold">苑裡政策島｜八島空中觀光步道</text><text x="32" y="76" font-size="16">依實際 x/z 座標繪製・八島七線・寬 ${WALKWAY.width}・最大中心坡度 ${WALKWAY.maxGrade*100}%（約 9.1°）</text>`;
for(const p of plans) {
  const pts=p.points.map(v=>`${px(v.x)},${py(v.z)}`).join(' ');
  svg+=`<polyline points="${pts}" fill="none" stroke="#a497ae" stroke-width="${WALKWAY.width*8+4}" stroke-linejoin="miter"/><polyline points="${pts}" fill="none" stroke="#ded3c7" stroke-width="${WALKWAY.width*8-2}" stroke-linejoin="miter"/>`;
}
ISLANDS.forEach((i,n)=>{
 svg+=`<circle cx="${px(i.x)}" cy="${py(i.z)}" r="${i.r*8}" fill="#b0d4bb" stroke="#668a7c" stroke-width="2"/><text x="${px(i.x)}" y="${py(i.z)-3}" text-anchor="middle" font-size="16" font-weight="bold">${names[n]}</text><text x="${px(i.x)}" y="${py(i.z)+21}" text-anchor="middle" font-size="13">高度 ${i.y}</text>`;
});
svg+=`<text x="32" y="900" font-size="15">灰米色線為實際步道／平台；轉折路段處理原有高差，無須跳躍。圖上交疊不代表不同高度相接。</text><text x="32" y="925" font-size="14">政策主題與觀光動線示意，非苑裡實際地圖或工程核定資訊。</text></g></svg>`;
writeFileSync('docs/previews/skywalk-network.svg',svg);
writeFileSync('docs/previews/skywalk-routes.json',JSON.stringify({width:WALKWAY.width,maxGrade:WALKWAY.maxGrade,railHeight:WALKWAY.railHeight,islands:ISLANDS,routes:plans.map(({id,from,to,length,points})=>({id,from,to,length,points}))},null,2)+'\n');
console.log('Generated docs/previews/skywalk-network.svg and skywalk-routes.json');
