// Traverse every physical route in both directions, including cycles and end caps.
export function walkTour(plans) {
 const result=[],used=new Set();
 function dfs(node){for(const p of plans){if(used.has(p.id)||!(p.from===node||p.to===node))continue;used.add(p.id);const next=p.from===node?p.to:p.from,points=p.from===node?p.points:[...p.points].reverse();result.push({to:next,points});dfs(next);result.push({to:node,points:[...points].reverse()});}}
 dfs('F');return result;
}
