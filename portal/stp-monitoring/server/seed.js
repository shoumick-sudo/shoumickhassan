import data from './seed.json' with {type:'json'};
import {criteria} from './domain.js';
export async function seed(client,id){
 for(const r of data.reports)await client.query('INSERT INTO stp.reports(workspace_id,id,provider_id,label,zone,officer_id,round_date,due_date) VALUES($1,$2,$3,$4,$5,$6,$7,$8)',[id,r.report_id,r.provider_id,r.label,r.zone,r.officer_id,r.round_date,r.due_date]);
 for(const s of data.submissions)await client.query('INSERT INTO stp.submissions(workspace_id,report_id,version,scores,decision,submitted_at,actor,reviewer) VALUES($1,$2,$3,$4,$5,$6,$7,$8)',[id,s.report_id,s.version,Object.fromEntries(criteria.map(k=>[k,s[k]])),s.decision,s.submitted_on,'synthetic-seed',s.decision==='approved'?'synthetic-reviewer':null]);
 for(const a of data.actions){const closed=!!a.closure_accepted;await client.query('INSERT INTO stp.actions(workspace_id,provider_id,title,owner,due_date,status,evidence,verification) VALUES($1,$2,$3,$4,$5,$6,$7,$8)',[id,a.provider_id,`${a.action_id}: Synthetic corrective action`,a.owner,a.due_date,closed?'closed':a.status==='closed'?'in_progress':a.status,a.closure_evidence||'',closed?'verified':'pending']);}
 await client.query("INSERT INTO stp.audit(workspace_id,actor,event,record_id,detail) VALUES($1,'system','synthetic_seed',$1,$2)",[id,{source:'STP reconstruction v1',rejectedSourceVersions:12,issueFlags:data.issues.length,notice:'Invalid source versions excluded from live workflow; raw source retained in public repository. Unverified historical closures reopened.'}]);
}
