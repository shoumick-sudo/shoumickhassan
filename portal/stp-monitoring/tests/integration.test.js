import test from 'node:test';import assert from 'node:assert/strict';import pg from 'pg';import {randomUUID} from 'node:crypto';import {createApp} from '../server/app.js';import {criteria,showcase} from '../server/domain.js';
test('persistent workflow, roles, isolation, stale edits and audit', {skip:!process.env.DATABASE_URL},async()=>{
 const pool=new pg.Pool({connectionString:process.env.DATABASE_URL,max:4});const actor='integration-'+randomUUID();const app=createApp({pool,authURL:process.env.NEON_AUTH_BASE_URL,verify:async t=>{if(t==='invalid')throw Error();return {sub:t}}});const server=app.listen(0,'127.0.0.1');await new Promise(r=>server.once('listening',r));const base='http://127.0.0.1:'+server.address().port;
 async function api(path,method='GET',body,user=actor){const r=await fetch(base+'/api'+path,{method,headers:{...(user?{Authorization:'Bearer '+user}:{}),'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});const d=await r.json();return {status:r.status,data:d}}
 try{
 assert.equal((await api(`/workspaces/${showcase}/data`,'GET',null,null)).status,200);
 assert.equal((await api(`/workspaces/${showcase}/reports/MON-0001/submissions`,'POST',{})).status,403);
 assert.equal((await api('/workspaces','GET',null,'invalid')).status,401);
 const w=await api('/workspaces','POST',{name:'Automated integration · synthetic'});assert.equal(w.status,201);const path='/workspaces/'+w.data.id;
 assert.equal((await api(path+'/data','GET',null,actor+'-stranger')).status,404);
 const before=(await api(path+'/data')).data.rows.find(r=>r.id==='MON-0001').current.version;
 const score=Object.fromEntries(criteria.map(k=>[k,4]));assert.equal((await api(path+'/reports/MON-0001/submissions','POST',{scores:{...score,records:5}})).status,400);
 const s=await api(path+'/reports/MON-0001/submissions','POST',{scores:score});assert.equal(s.status,201);
 assert.equal((await api(path+'/data')).data.rows.find(r=>r.id==='MON-0001').current.version,before);
 const inv=await api(path+'/access-codes','POST',{role:'officer'});assert.equal(inv.status,201);
 assert.equal((await api('/access-codes/redeem','POST',{code:inv.data.code},actor+'-officer')).status,200);
 assert.equal((await api('/access-codes/redeem','POST',{code:inv.data.code},actor+'-other')).status,400);
 assert.equal((await api(path+'/submissions/'+s.data.id+'/review','POST',{decision:'approved',note:'Officer should not approve'},actor+'-officer')).status,403);
 assert.equal((await api(path+'/submissions/'+s.data.id+'/review','POST',{decision:'approved',note:'Validated all five synthetic criteria'})).status,200);
 assert.equal((await api(path+'/submissions/'+s.data.id+'/review','POST',{decision:'approved',note:'Repeated'})).status,409);
 const a={provider_id:'DEMO-STP-001',title:'Synthetic integration correction',owner:'Test owner',due_date:'2026-10-30',status:'open',verification:'pending',evidence:''};let r=await api(path+'/actions','POST',a);assert.equal(r.status,201);const aid=r.data.id;
 assert.equal((await api(path+'/actions/'+aid,'PATCH',{...a,revision:1,status:'closed'})).status,400);
 assert.equal((await api(path+'/actions/'+aid,'PATCH',{...a,revision:1,status:'closed',verification:'verified',evidence:'SIMULATED validation'},actor+'-officer')).status,403);
 const closed={...a,revision:1,status:'closed',verification:'verified',evidence:'SIMULATED validation'};assert.equal((await api(path+'/actions/'+aid,'PATCH',closed)).status,200);assert.equal((await api(path+'/actions/'+aid,'PATCH',closed)).status,409);
 const reload=(await api(path+'/data')).data;assert.equal(reload.actions.find(x=>x.id===aid).status,'closed');assert.equal(reload.rows.find(x=>x.id==='MON-0001').score,100);assert(reload.audit.some(x=>x.event==='submission_approved'));assert(reload.audit.some(x=>x.event==='action_updated'));
 // Read with an independent database connection: persistence is not in process memory.
 const check=await pool.query('SELECT status,revision FROM stp.actions WHERE workspace_id=$1 AND id=$2',[w.data.id,aid]);assert.equal(check.rows[0].revision,2);
 console.log('Integration verified: persistence, access denial, roles, code replay, review conflicts, closure evidence, stale revisions, audit.');
 }finally{await new Promise(r=>server.close(r));await pool.end()}
});
