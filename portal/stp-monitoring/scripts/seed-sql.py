import json,pathlib
p=pathlib.Path(__file__).resolve().parents[1]
d=json.load(open(p/'server/seed.json'));wid='00000000-0000-4000-8000-000000000001'
def q(x):return "'"+str(x).replace("'","''")+"'"
s=[(p/'sql/001.sql').read_text(),f"INSERT INTO stp.workspaces(id,name,public) VALUES('{wid}','STP monitoring · synthetic showcase',true) ON CONFLICT DO NOTHING"]
s.append('INSERT INTO stp.reports(workspace_id,id,provider_id,label,zone,officer_id,round_date,due_date) VALUES '+','.join('('+','.join(map(q,[wid,r['report_id'],r['provider_id'],r['label'],r['zone'],r['officer_id'],r['round_date'],r['due_date']]))+')' for r in d['reports'])+' ON CONFLICT DO NOTHING')
keys=['infrastructure','equipment','trainers','records','assessment_readiness']
s.append('INSERT INTO stp.submissions(workspace_id,report_id,version,scores,decision,submitted_at,actor,reviewer) VALUES '+','.join('('+','.join(map(q,[wid,r['report_id'],r['version'],json.dumps({k:r[k] for k in keys}),r['decision'],r['submitted_on'],'synthetic-seed','synthetic-reviewer']))+')' for r in d['submissions'])+' ON CONFLICT DO NOTHING')
s.append('INSERT INTO stp.actions(workspace_id,provider_id,title,owner,due_date,status,evidence,verification) VALUES '+','.join('('+','.join(map(q,[wid,a['provider_id'],a['action_id']+': Synthetic corrective action',a['owner'],a['due_date'],'closed' if a['closure_accepted'] else ('in_progress' if a['status']=='closed' else a['status']),a['closure_evidence'] or '','verified' if a['closure_accepted'] else 'pending']))+')' for a in d['actions']))
s.append(f"INSERT INTO stp.audit(workspace_id,actor,event,record_id,detail) VALUES('{wid}','system','synthetic_seed','{wid}','{{\"source\":\"STP reconstruction v1\",\"invalidSourceVersionsExcluded\":12,\"issueFlags\":14,\"unverifiedClosuresReopened\":true}}')")
json.dump(s,open(p/'sql/seed-statements.json','w'))
