"""Convert a mock XLSForm CSV export to long-form staging; no automatic approval.
Usage: python src/import_form.py input.csv staging.csv
Required input columns: report_id,version,f_child,f_adult,m_child,m_adult,u_child,u_adult
"""
import csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def convert(input_path,output_path):
    master={r['report_id']:r for r in csv.DictReader((ROOT/'data/expectations.csv').open())}
    incoming=list(csv.DictReader(Path(input_path).open()));seen=set();out=[]
    for r in incoming:
        key=(r['report_id'],r['version'])
        if key in seen:raise ValueError('Duplicate report/version in export; reconcile before import')
        seen.add(key)
        if r['report_id'] not in master:raise ValueError('Unknown report ID')
        if not r['version'].isdigit() or int(r['version'])<1:raise ValueError('Version must be a positive integer')
        e=master[r['report_id']]
        for sex in ['F','M','U']:
            for age in ['child','adult']:
                val=r[sex.lower()+'_'+age]
                if not val.isdigit() or int(val)>1000000:raise ValueError('Counts must be whole numbers from 0 to 1000000')
                out.append(dict(row_id=len(out)+1,submission_id=f"{r['report_id']}-v{int(r['version'])}",report_id=r['report_id'],partner_id=e['partner_id'],location_id=e['location_id'],period=e['period'],sex=sex,age=age,value=int(val)))
    if not out:raise ValueError('No reports in export')
    with Path(output_path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    return out
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit(__doc__)
    print(f'{len(convert(sys.argv[1],sys.argv[2]))} staging rows. Review required; nothing approved or imported into the database.')
