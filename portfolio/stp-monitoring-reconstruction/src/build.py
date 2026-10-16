"""Synthetic STP monitoring reconstruction. Standard-library Python 3.10+.
Run: python src/build.py
Optionally: --source path/to/candidate_monitoring.csv --cutoff 2026-10-16 --output outputs
Imported sources replace synthetic raw submissions, not masters/expectations. No auto-approval.
"""
import argparse,csv,hashlib,json,random,sqlite3,sys
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CRITERIA=['infrastructure','equipment','trainers','records','assessment_readiness']
SEED=16102026
NOTICE='Synthetic reconstruction of monitoring methods. Not an NSDA dataset, official rating or original dashboard.'

def csv_write(path,rows,fields=None):
    rows=list(rows)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)

def fixture():
    rng=random.Random(SEED)
    providers=[dict(provider_id=f'DEMO-STP-{i+1:03}',label=f'Fictional training centre {i+1:03}',zone=f'Fictional zone {i%8+1}') for i in range(48)]
    officers=[dict(officer_id=f'DEMO-O-{i+1:02}',label=f'Fictional monitoring officer {i+1:02}') for i in range(8)]
    rounds=['2026-09-18','2026-09-25','2026-10-02','2026-10-09','2026-10-23']
    expectations=[];raw=[];truth=[]
    for ri,rd in enumerate(rounds):
        for i,p in enumerate(providers):
            n=len(expectations)+1;rid=f'MON-{n:04}';oid=officers[i%8]['officer_id'];due=str(date.fromisoformat(rd)+timedelta(days=2))
            expectations.append(dict(report_id=rid,provider_id=p['provider_id'],officer_id=oid,round_date=rd,due_date=due))
            if ri==4:continue # A future expected round; must not depress today's completeness.
            if n in [20,40,60,80,100,120,140,180]:truth.append(dict(report_id=rid,rule='missing_report'));continue
            for version,decision in [(1,'approved')]+([(2,'approved')] if n<=12 else [])+([(3,'draft')] if n<=6 else []):
                r=dict(row_id=len(raw)+1,submission_id=f'{rid}-v{version}',report_id=rid,provider_id=p['provider_id'],officer_id=oid,version=version,round_date=rd,submitted_on=str(date.fromisoformat(due)+timedelta(days=2 if n%9==0 else -1)),decision=decision)
                r.update({k:rng.randint(0,4) for k in CRITERIA})
                if version==3:r.update({k:4 for k in CRITERIA})
                raw.append(r)
    for i,n in enumerate(range(160,172)):
        r=next(r for r in raw if r['report_id']==f'MON-{n:04}')
        rule=['score_range','missing_score','provider_mismatch','duplicate_submission','officer_mismatch','future_receipt'][i%6]
        if rule=='score_range':r['equipment']=9
        elif rule=='missing_score':r['records']=''
        elif rule=='provider_mismatch':r['provider_id']='INVALID-PROVIDER'
        elif rule=='officer_mismatch':r['officer_id']='INVALID-OFFICER'
        elif rule=='future_receipt':r['submitted_on']='2026-12-31'
        else:raw.append(dict(r,row_id=len(raw)+1))
        truth.append(dict(report_id=r['report_id'],rule=rule))
    actions=[]
    for i,p in enumerate(providers[:24]):
        closed=i%4==0
        actions.append(dict(action_id=f'ACT-{i+1:03}',provider_id=p['provider_id'],owner=f'DEMO-OWNER-{i%8+1:02}',due_date='2026-10-12' if i%2==0 else '2026-10-20',status='closed' if closed else 'in_progress' if i%3==0 else 'open',closure_evidence='SIMULATED: correction checked against fictional evidence' if closed and i!=0 else '',verification='verified' if closed and i!=0 else 'pending'))
    return dict(providers=providers,officers=officers,expectations=expectations,raw=raw,actions=actions,seeded_truth=truth)

def validate(raw,expectations,cutoff):
    ex={e['report_id']:e for e in expectations};counts=Counter(r['submission_id'] for r in raw);issues=[]
    for r in raw:
        rules=[];e=ex.get(r['report_id'])
        if not e:rules.append('unknown_report')
        else:
            for field in ['provider_id','officer_id']:
                if r[field]!=e[field]:rules.append(field.split('_')[0]+'_mismatch')
            if r['round_date']!=e['round_date']:rules.append('round_mismatch')
        if counts[r['submission_id']]>1:rules.append('duplicate_submission')
        for k in CRITERIA:
            if str(r[k]).strip()=='':rules.append('missing_score');continue
            try:
                value=float(r[k])
                if not value.is_integer() or value<0 or value>4:rules.append('score_range')
            except (ValueError,TypeError):rules.append('score_range')
        try:
            received=date.fromisoformat(r['submitted_on']);round_date=date.fromisoformat(r['round_date'])
            if received>date.fromisoformat(cutoff):rules.append('future_receipt')
            if received<round_date:rules.append('receipt_before_round')
        except ValueError:rules.append('invalid_date')
        try:
            v=int(r['version'])
            if str(v)!=str(r['version']) or v<1:rules.append('invalid_version')
            if r['submission_id']!=f"{r['report_id']}-v{v}":rules.append('submission_id_mismatch')
        except (ValueError,TypeError):rules.append('invalid_version')
        if r['decision'] not in ['approved','draft','rejected']:rules.append('invalid_decision')
        for rule in sorted(set(rules)):
            issues.append(dict(issue_id=len(issues)+1,raw_row_id=r['row_id'],submission_id=r['submission_id'],rule=rule,action='Hold entire version; request correction and preserve original'))
    return issues

def db_build(data,out,cutoff):
    path=out/'monitoring.sqlite'
    if path.exists():path.unlink()
    c=sqlite3.connect(path);c.row_factory=sqlite3.Row;c.executescript((ROOT/'sql/schema.sql').read_text())
    for table in ['providers','officers','expectations','actions']:
        rs=data[table];keys=list(rs[0]);c.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for k in keys)})",[tuple(r[k] for k in keys) for r in rs])
    issues=validate(data['raw'],data['expectations'],cutoff);bad={i['submission_id'] for i in issues};seen=set()
    ex={e['report_id']:e for e in data['expectations']}
    for r in data['raw']:
        c.execute('INSERT INTO raw_rows VALUES (?,?)',(r['row_id'],json.dumps(r,sort_keys=True)))
        sid=r['submission_id']
        if sid in seen:continue
        seen.add(sid)
        if r['report_id'] not in ex:continue
        try:v=int(r['version'])
        except (ValueError,TypeError):continue
        if v<1 or str(v)!=str(r['version']):continue
        c.execute('INSERT INTO submissions VALUES (?,?,?,?,?)',(sid,r['report_id'],v,r['submitted_on'],'rejected' if sid in bad else r['decision']))
        if sid not in bad:c.execute('INSERT INTO scores VALUES (?,?,?,?,?,?,?)',(sid,r['row_id'],*(int(float(r[k])) for k in CRITERIA)))
    c.executemany('INSERT INTO dq_issues VALUES (?,?,?,?,?)',[tuple(i.values()) for i in issues]);c.commit();return c,issues

def read(c,q,params=()):return [dict(r) for r in c.execute(q,params)]

def export(c,data,issues,out,cutoff):
    reports=read(c,'SELECT * FROM report_monitor ORDER BY round_date,provider_id')
    for r in reports:r['is_due']=int(r['due_date']<=cutoff)
    actions=read(c,'SELECT * FROM actions')
    for a in actions:
        a['closure_accepted']=int(a['status']=='closed' and bool(a['closure_evidence'].strip()) and a['verification']=='verified')
        a['overdue']=int(not a['closure_accepted'] and a['due_date']<cutoff)
    due=[r for r in reports if r['is_due']]
    summary=dict(notice=NOTICE,version='1.0.0',seed=SEED,cutoff=cutoff,providers=len(data['providers']),raw_rows=len(data['raw']),due_reports=len(due),future_expectations=len(reports)-len(due),received_reports=sum(r['received'] for r in due),approved_reports=sum(r['submission_id'] is not None for r in due),timely_reports=sum(r['on_time'] for r in due),issue_flags=len(issues),rejected_versions=len({i['submission_id'] for i in issues}),actions=len(actions),accepted_closures=sum(a['closure_accepted'] for a in actions),overdue_actions=sum(a['overdue'] for a in actions))
    csv_write(out/'report_monitor.csv',reports);csv_write(out/'action_tracker.csv',actions)
    csv_write(out/'dq_issues.csv',issues,['issue_id','raw_row_id','submission_id','rule','action'])
    csv_write(out/'approved_scores.csv',[r for r in reports if r['submission_id']],list(reports[0]))
    csv_write(out/'quarantined_rows.csv',[r for r in data['raw'] if r['submission_id'] in {i['submission_id'] for i in issues}],list(data['raw'][0]) if data['raw'] else ['row_id','submission_id'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    dataset=dict(summary=summary,reports=reports,actions=actions,issues=issues,criteria=CRITERIA,raw=data['raw'])
    (out/'dashboard_data.json').write_text(json.dumps(dataset,indent=2))
    template=(ROOT/'src/dashboard.template.html').read_text()
    (out/'dashboard.html').write_text(template.replace('@@DATA@@',json.dumps(dataset).replace('</','<\\/')))
    return summary

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path);parser.add_argument('--cutoff',default='2026-10-16');parser.add_argument('--output',type=Path,default=ROOT/'outputs');args=parser.parse_args();date.fromisoformat(args.cutoff)
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);(ROOT/'data').mkdir(exist_ok=True)
    data=fixture()
    for key in ['providers','officers','expectations','raw','actions','seeded_truth']:csv_write(ROOT/'data'/f'{key}.csv',data[key])
    if args.source:
        with args.source.open(encoding='utf-8-sig') as f:
            reader=csv.DictReader(f)
            required={'submission_id','report_id','provider_id','officer_id','version','round_date','submitted_on',*CRITERIA}
            missing=required-set(reader.fieldnames or [])
            if missing:parser.error('Missing CSV columns: '+', '.join(sorted(missing)))
            data['raw']=list(reader)
        for i,r in enumerate(data['raw']):r['row_id']=i+1;r['decision']='draft' # Imported data require explicit review; never auto-approve.
    c,issues=db_build(data,out,args.cutoff);summary=export(c,data,issues,out,args.cutoff)
    c.close();print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
