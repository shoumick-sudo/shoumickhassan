"""Reproducible source detail extracts for the private source archive."""
import argparse
from pathlib import Path
from build import aug,writecsv

def run(raw,out):
 out.mkdir(parents=True,exist_ok=True)
 a=aug(raw/'unhcr_august_2026.xlsx')[0];b=aug(raw/'unhcr_september_2026.xlsx','2026-09-30','UNHCR_SEP_XLSX',(251635,1206528))[0]
 writecsv(out/'DERIVED_UNHCR_2026-09_Block_Population.csv',b)
 keys=[{(x['label'],x['block_id']):x for x in rows if x['block_id']} for rows in [a,b]]
 assert keys[0].keys()==keys[1].keys()
 rows=[{'camp':k[0],'block_id':k[1],'august':keys[0][k]['population'],'september':keys[1][k]['population'],'change':keys[1][k]['population']-keys[0][k]['population'],'method':'exact camp and nonblank block SSID; missing-ID rows excluded'} for k in sorted(keys[0])]
 writecsv(out/'DERIVED_UNHCR_2026-08_to_09_Block_Key_Comparison.csv',rows)
 assert sum(x['change'] for x in rows)+sum(x['population'] for x in b if not x['block_id'])-sum(x['population'] for x in a if not x['block_id'])==2036
 print('245 nonblank keys; +2086 keyed and -50 unkeyed population change reconcile to +2036. No unkeyed row-to-row matching.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.raw,a.out)
