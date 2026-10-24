export function walkTour(plans) {
  const result=[],visited=new Set(['home']);
  function dfs(name) {
    for(const p of plans) {
      const next=p.from===name?p.to:p.to===name?p.from:null;
      if(!next || visited.has(next)) continue;
      visited.add(next);const points=p.from===name?p.points:[...p.points].reverse();
      result.push({to:next,points});dfs(next);result.push({to:name,points:[...points].reverse()});
    }
  }
  dfs('home');return result;
}
