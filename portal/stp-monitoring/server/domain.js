export const criteria=['infrastructure','equipment','trainers','records','assessment_readiness'];
export const showcase='00000000-0000-4000-8000-000000000001';
export function scoresValid(s){return s && Object.keys(s).length===5 && criteria.every(k=>Number.isInteger(s[k])&&s[k]>=0&&s[k]<=4)}
export function closureValid(s){return s.status!=='closed'||(s.verification==='verified'&&s.evidence?.trim().length>0)}
export function canReview(role){return ['owner','reviewer'].includes(role)}
export function summarise(reports,submissions,actions,cutoff=new Date().toISOString().slice(0,10)){
 const rows=reports.map(r=>{const versions=submissions.filter(s=>s.report_id===r.id).sort((a,b)=>b.version-a.version);const current=versions.find(s=>s.decision==='approved');const score=current?criteria.reduce((n,k)=>n+current.scores[k],0)*5:null;return {...r,versions,current,score,received:versions.length>0,band:score===null?'unavailable':score<50?'priority':score<75?'attention':'routine',due:r.due_date<=cutoff};});
 const due=rows.filter(r=>r.due);return {rows,metrics:{expected:due.length,received:due.filter(r=>r.received).length,approved:due.filter(r=>r.current).length,missing:due.filter(r=>!r.received).length,openActions:actions.filter(a=>a.status!=='closed').length,overdueActions:actions.filter(a=>a.status!=='closed'&&a.due_date<cutoff).length}};
}
