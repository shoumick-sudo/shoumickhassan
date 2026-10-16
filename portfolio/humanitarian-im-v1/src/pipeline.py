"""Rebuild a fully synthetic IM case study. Python standard library only.
Run from the project root: python src/pipeline.py
No real people, places, programme data, credentials or external APIs are used.
"""
import calendar, csv, hashlib, json, random, sqlite3, sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SEED=20261016
CUTOFF='2026-10-16'
LABEL='Independent portfolio demonstration using synthetic programme data. Not UNICEF or official response data.'

def write_csv(path, rows, fields=None):
    rows=list(rows)
    if not rows and not fields: return
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0])); w.writeheader();w.writerows(rows)

def generate():
    rng=random.Random(SEED)
    locations=[dict(location_id=f'L{i+1:02}',label=f'Fictional location {i+1:02}',x=(i%4)*10,y=(i//4)*10) for i in range(12)]
    partners=[dict(partner_id=f'P{i+1:02}',sector=['Education','WASH','Health'][i//2],indicator=['ED_ATT','WA_CON','HE_CON'][i//2],unit=['learning attendances','WASH service contacts','health consultation events'][i//2]) for i in range(6)]
    expectations=[]; submissions=[]; raw=[]; plans=[]; truth=[]
    for mi in range(4,10):
        due=date(2026,mi,calendar.monthrange(2026,mi)[1])+timedelta(days=5)
        for p in partners:
            for loc in locations:
                n=len(expectations)+1; rid=f'R{n:04}'
                expectations.append(dict(report_id=rid,partner_id=p['partner_id'],location_id=loc['location_id'],period=f'2026-{mi:02}',due_date=str(due)))
                plans.append(dict(report_id=rid,target=900,unit_cost=[2.5,1.2,3.0][['Education','WASH','Health'].index(p['sector'])]))
                if n in [40,100,160,220,280,340]:
                    truth.append(dict(report_id=rid,submission_id='',rule='missing_report'));continue
                late=(n%11==0)
                receipt=str(due+timedelta(days=2 if late else -1))
                for version,status in [(1,'approved')]+([(2,'approved')] if n<=12 else [])+([(3,'draft')] if n<=6 else []):
                    sid=f'{rid}-v{version}'
                    submissions.append(dict(submission_id=sid,report_id=rid,version=version,received_date=receipt,status=status))
                    for sex in ['F','M','U']:
                        for age in ['child','adult']:
                            value=rng.randint(100,185) if sex!='U' else rng.randint(2,18)
                            if version==3: value=99999 # Demonstrates exclusion of newer unapproved revisions.
                            raw.append(dict(row_id=len(raw)+1,submission_id=sid,report_id=rid,partner_id=p['partner_id'],location_id=loc['location_id'],period=f'2026-{mi:02}',sex=sex,age=age,value=value))
    # Deliberate errors in unique reports; validator does not read the truth ledger.
    for j,n in enumerate(range(400,418)):
        sid=f'R{n:04}-v1'; row=next(r for r in raw if r['submission_id']==sid)
        rule=['negative','missing_value','location_mismatch','bad_category','duplicate_cell','non_integer'][j%6]
        if rule=='negative': row['value']=-7
        elif rule=='missing_value': row['value']=''
        elif rule=='location_mismatch': row['location_id']='L99'
        elif rule=='bad_category': row['sex']='X'
        elif rule=='non_integer': row['value']='12.5'
        else:
            copy=dict(row);copy['row_id']=len(raw)+1;raw.append(copy)
        truth.append(dict(report_id=f'R{n:04}',submission_id=sid,rule=rule))
    facilities=[]; statuses=[]
    for i in range(108):
        fid=f'F{i+1:03}';sector=['Education','WASH','Health'][i%3]
        facilities.append(dict(facility_id=fid,location_id=locations[i%12]['location_id'],sector=sector))
        statuses.append(dict(facility_id=fid,observed_at='2026-09-28',status='functional'))
        statuses.append(dict(facility_id=fid,observed_at='2026-09-30',status='unknown' if i%17==0 else 'disrupted' if i%7==0 else 'functional'))
    data=dict(locations=locations,partners=partners,expectations=expectations,submissions=submissions,raw=raw,plans=plans,facilities=facilities,facility_status=statuses,seeded_truth=truth)
    return data

def validate(raw, expectations):
    ex={e['report_id']:e for e in expectations}
    cells=Counter((r['submission_id'],r['sex'],r['age']) for r in raw)
    groups=defaultdict(list)
    for r in raw: groups[r['submission_id']].append(r)
    issues=[]
    for r in raw:
        rules=[]; value=r['value']; e=ex.get(r['report_id'])
        if value=='': rules.append('missing_value')
        else:
            try:
                x=float(value)
                if x<0: rules.append('negative')
                if not x.is_integer(): rules.append('non_integer')
                if x>1000000: rules.append('out_of_range')
            except (ValueError,TypeError,OverflowError): rules.append('not_numeric')
        if not e: rules.append('unknown_report')
        elif r['location_id']!=e['location_id']:rules.append('location_mismatch')
        if e and (r['partner_id']!=e['partner_id'] or r['period']!=e['period']):rules.append('report_key_mismatch')
        if r['sex'] not in ['F','M','U'] or r['age'] not in ['child','adult']:rules.append('bad_category')
        if cells[(r['submission_id'],r['sex'],r['age'])]>1:rules.append('duplicate_cell')
        if len(groups[r['submission_id']])!=6:rules.append('incomplete_or_duplicate_strata')
        for rule in rules:
            issues.append(dict(issue_id=len(issues)+1,row_id=r['row_id'],submission_id=r['submission_id'],rule=rule,severity='critical',owner='SIMULATED_PARTNER_FOCAL_POINT',action='Request corrected resubmission; whole version excluded pending correction',status='open'))
    return issues

def build(data, dbpath):
    if dbpath.exists():dbpath.unlink()
    c=sqlite3.connect(dbpath);c.row_factory=sqlite3.Row;c.executescript((ROOT/'sql/schema.sql').read_text())
    issues=validate(data['raw'],data['expectations']);bad={i['submission_id'] for i in issues}
    for table in ['locations','partners','expectations','submissions','plans','facilities','facility_status']:
        rows=data[table]
        if table=='submissions':rows=[dict(r,status='rejected' if r['submission_id'] in bad else r['status']) for r in rows]
        fields=list(rows[0]);c.executemany(f"INSERT INTO {table} ({','.join(fields)}) VALUES ({','.join('?' for _ in fields)})",[tuple(r[f] for f in fields) for r in rows])
    c.executemany('INSERT INTO raw_rows VALUES (?,?)',[(r['row_id'],json.dumps(r,sort_keys=True)) for r in data['raw']])
    for r in data['raw']:
        if r['submission_id'] not in bad:c.execute('INSERT INTO observations VALUES (?,?,?,?,?)',(r['row_id'],r['submission_id'],r['sex'],r['age'],int(r['value'])))
    for r in issues:
        c.execute('INSERT INTO issues VALUES (?,?,?,?,?,?,?,?)',tuple(r.values()))
    c.commit();return c,issues

def rows(c,query):return [dict(r) for r in c.execute(query)]

def export(c,data,issues):
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    for name,values in data.items():write_csv(ROOT/'data'/f'{name}.csv',values)
    reports=rows(c,'SELECT * FROM report_monitor ORDER BY report_id')
    approved=rows(c,'SELECT * FROM approved_results ORDER BY row_id')
    for name,values in [('report_monitor',reports),('approved_results',approved),('dq_issues',issues)]:write_csv(out/f'{name}.csv',values)
    sectors=rows(c,"SELECT sector,indicator,unit,SUM(COALESCE(actual,0)) actual,SUM(target) target,SUM(approved) approved,COUNT(*) expected,SUM(received) received,SUM(on_time) on_time FROM report_monitor GROUP BY sector,indicator,unit")
    latest=rows(c,"SELECT f.*,s.status,s.observed_at FROM facilities f JOIN facility_status s USING(facility_id) WHERE s.observed_at=(SELECT MAX(t.observed_at) FROM facility_status t WHERE t.facility_id=s.facility_id)")
    rejected=c.execute("SELECT COUNT(*) FROM submissions WHERE status='rejected'").fetchone()[0]
    summary=dict(label=LABEL,version='0.1.0',cutoff=CUTOFF,seed=SEED,raw_rows=len(data['raw']),approved_rows=len(approved),expected_reports=len(reports),received_reports=sum(r['received'] for r in reports),approved_reports=sum(r['approved'] for r in reports),on_time_reports=sum(r['on_time'] for r in reports),rejected_versions=rejected,dq_issue_flags=len(issues),rejected_rows=sum(1 for r in data['raw'] if r['submission_id'] in {i['submission_id'] for i in issues}),sectors=sectors,facilities=latest)
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    (out/'dashboard_data.json').write_text(json.dumps(dict(summary=summary,reports=reports,locations=data['locations']),indent=2))
    geo=dict(type='FeatureCollection',name='Fictional local grid; no geographic CRS or real-world location',features=[dict(type='Feature',geometry=dict(type='Point',coordinates=[l['x'],l['y']]),properties=l) for l in data['locations']])
    # Deliberately use a CSV local grid rather than mislabel arbitrary XY as RFC7946 longitude/latitude.
    (out/'fictional_grid.json').write_text(json.dumps(geo,indent=2))
    return summary

def run():
    for d in ['outputs','data']:(ROOT/d).mkdir(exist_ok=True)
    data=generate();c,issues=build(data,ROOT/'outputs/im_demo.sqlite');summary=export(c,data,issues)
    c.close();print(json.dumps({k:v for k,v in summary.items() if k not in ['facilities','sectors']},indent=2))

if __name__=='__main__':run()
