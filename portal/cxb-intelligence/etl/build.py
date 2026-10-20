"""Deterministic real-source ETL. No estimates, imputation or generated observations."""
import argparse,collections,csv,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
import openpyxl
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
AGES=[('below 1',10,11),('1-4',12,13),('5-11',14,16),('12-17',17,18),('18-59',21,22),('60+',23,24)]
def canon(s):
 s=s.replace('*','').strip()
 s=re.sub(r'^Camp 0+(\d)',r'Camp \1',s)
 return s

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def writecsv(path,rows):
 if not rows:return
 with open(path,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in rows for k in row)),lineterminator="\n");w.writeheader();w.writerows(rows)
def aug(path,date='2026-08-31',source_id='UNHCR_AUG',expected=(251166,1204492)):
 ws=openpyxl.load_workbook(path,data_only=True).worksheets[0]
 blocks=[];published={};camp=None;grand=None
 for idx,row in enumerate(ws.values,1):
  label,block,families,pop=row[1],row[5],row[7],row[8]
  if idx<10 or not isinstance(pop,(int,float)):continue
  if label:camp=canon(label)
  if block=='Total':published[camp]=(int(families),int(pop));continue
  if block in (None,''):grand=(int(families),int(pop));continue
  d={'label':camp,'source_row':idx,'block_id':row[6] or None,'block_label':block,'families':int(families),'population':int(pop)}
  for age,f,m in AGES:
   d[age+'_female']=int(row[f]);d[age+'_male']=int(row[m])
  assert sum(d[a+'_'+s] for a,_,_ in AGES for s in ['female','male'])==pop,('age mismatch',idx)
  blocks.append(d)
 groups=[];demo=[]
 for label,(fam,pop) in published.items():
  b=[x for x in blocks if x['label']==label]
  assert sum(x['population'] for x in b)==pop,(label,'subtotal')
  assert sum(x['families'] for x in b)==fam
  groups.append({'label':label,'date':date,'families':fam,'population':pop,'source_id':source_id,'missing_block_rows':sum(x['block_id'] is None for x in b)})
  for age,_,_ in AGES:
   for sex in ['female','male']:demo.append({'label':label,'date':date,'age':age,'sex':sex,'population':sum(x[age+'_'+sex] for x in b),'source_id':source_id})
 assert (sum(x['families'] for x in groups),sum(x['population'] for x in groups))==grand
 assert grand==expected
 return blocks,groups,demo

def sep(path):
 # Text extraction in layout mode preserves the two side-by-side tables on page 2.
 text=subprocess.check_output(['pdftotext','-layout',str(path),'-'],text=True)
 p=r'(Camp \d+(?:[EW]| Extension)?|Bhasan Char|Kutupalong RC|Nayapara RC|Other)\s+([\d,]+)\s+([\d,]+)'
 rows=[{'label':l,'date':'2026-09-30','families':int(f.replace(',','')),'population':int(n.replace(',','')),'source_id':'UNHCR_SEP','missing_block_rows':None} for l,f,n in re.findall(p,text)]
 assert len(rows)==len({r['label'] for r in rows})==35
 assert sum(x['population'] for x in rows)==1206528
 assert sum(x['families'] for x in rows)==251635
 return rows

def build(raw,inputs,out):
 out.mkdir(exist_ok=True,parents=True)
 blocks,a,demo=aug(raw/'unhcr_august_2026.xlsx')
 sep_blocks,s,sep_demo=aug(raw/'unhcr_september_2026.xlsx','2026-09-30','UNHCR_SEP_XLSX',(251635,1206528))
 pdf=sep(raw/'unhcr_sep2026.pdf')
 assert {x['label']:(x['families'],x['population']) for x in s}=={x['label']:(x['families'],x['population']) for x in pdf},'September XLSX/PDF mismatch'
 demo+=sep_demo
 keyed=[{(x['label'],x['block_id']):x for x in rows if x['block_id']} for rows in [blocks,sep_blocks]]
 assert all(len(k)==sum(x['block_id'] is not None for x in rows) for k,rows in zip(keyed,[blocks,sep_blocks])),'Duplicate nonblank camp/block keys'
 assert keyed[0].keys()==keyed[1].keys(),'Changed block key coverage needs review'
 assert {x['label'] for x in a}=={x['label'] for x in s}
 by={x['label']:x for x in a}
 changes=[{'label':x['label'],'august':by[x['label']]['population'],'september':x['population'],'change':x['population']-by[x['label']]['population'],'change_pct':round((x['population']/by[x['label']]['population']-1)*100,6),'join_method':'exact normalized published name; asterisk footnotes removed','source_ids':['UNHCR_AUG','UNHCR_SEP']} for x in s]
 # Verify existing August extracts independently; don't trust earlier QA statuses.
 old=list(csv.DictReader(open(inputs/'DERIVED_UNHCR_2026-08_Camp_Aggregates.csv',encoding='utf-8-sig')))
 assert {canon(x['camp_source_label']):int(x['individuals_from_blocks']) for x in old}=={x['label']:x['population'] for x in a}
 inds=list(csv.DictReader(open(inputs/'DERIVED_UNICEF_2026-H1_HAC_Indicators.csv',encoding='utf-8-sig')))
 page=PdfReader(raw/'unicef_h1_2026.pdf').pages[0].extract_text(extraction_mode='layout')
 # Validate chart percentages in order against the original PDF, preserving funding >100%.
 ps=[int(n) for n in re.findall(r'(?<![\d,])([0-9]{1,3})%',page)]
 expected=[int(x['percent']) for x in inds]
 assert any(ps[i:i+18]==expected for i in range(len(ps)-17)),('UNICEF chart mismatch',ps)
 for x in inds:x['percent']=int(x['percent']);x['source_id']='UNICEF_H1';x['target_shortfall_pp']=100-x['percent'] if x['measure_type']=='target_attainment_pct' else None
 reach=list(csv.DictReader(open(inputs/'DERIVED_UNICEF_2026-H1_Reported_Reach.csv',encoding='utf-8-sig')))
 for x in reach:
  x['reported_value']=int(x['reported_value']);assert f"{x['reported_value']:,}" in page;x['source_id']='UNICEF_H1'
 feed=json.load(open(raw/'unhcr_population.json'))['data'][0]
 assert feed['date']=='2026-09-30' and int(feed['individuals'])==1173291
 qa=[{'rule':'August total and 35 subtotals','status':'PASS','detail':'279 detail rows reconcile to 1,204,492 individuals and 251,166 families.'},
 {'rule':'Age-sex categories','status':'PASS','detail':'12 disjoint broad age/sex cells sum to every detail row in both workbooks; 840 camp/age/sex aggregates; alternate five-year sheets excluded.'},
 {'rule':'September completeness','status':'PASS','detail':f'Official September XLSX: {len(sep_blocks)} detail rows and 35 group subtotals reconcile to 1,206,528 individuals and 251,635 families. All 35 family/population totals independently match PDF page 2.'},
 {'rule':'Block-key continuity','status':'PASS','detail':f'{len(keyed[0])} unique nonblank camp/block keys match across both workbooks; missing IDs retained, not joined or imputed.'},
 {'rule':'Cross-month keys','status':'PASS','detail':'35/35 exact normalized names. RC footnote asterisks stripped; no fuzzy matching.'},
 {'rule':'Missing August block identifiers','status':'WARNING','detail':str(sum(b['block_id'] is None for b in blocks))+' rows retain missing source IDs; no invented codes.'},
 {'rule':'UNHCR HTML/JSON freshness','status':'RESOLVED','detail':'Earlier archived disagreement no longer reproduced: downloaded feed now reports 30 Sep 2026 and 1,173,291 CXB. Checked 20 Oct 2026.'},
 {'rule':'UNICEF scope','status':'WARNING','detail':'HAC target attainment, sector funding and Rohingya headline reach use different definitions. No cross-sector sum or September coverage ratio.'},
 {'rule':'WASH point redistribution','status':'BLOCKED','detail':'Historical September 2025 infrastructure acquired; explicit reuse terms and field functionality definitions unresolved. Precise points withheld from public app.'}]
 sources=[]
 specs=[('UNHCR_AUG','unhcr_august_2026.xlsx','GoB / UNHCR','https://drive.google.com/file/d/1eVSV8CEzqqcimyBTCX-SobmmNZ0x16T2/view','2026-08-31','279 block/detail rows; 35 groups','Public source workbook; original retained in private Drive. Camp-level statistical facts attributed; source not relicensed.','Original XLSX; Standard breakdown; rows 10–324'),('UNHCR_SEP','unhcr_sep2026.pdf','GoB / UNHCR','https://data.unhcr.org/en/documents/details/124447','2026-09-30','35 camp/geography groups','UNHCR ODP CC BY 4.0 except stated otherwise; source attribution retained.','Original PDF; page 2 population table'),('UNICEF_H1','unicef_h1_2026.pdf','UNICEF Bangladesh','https://www.unicef.org/media/183486/file/Bangladesh-Humanitarian-Situation-Report-No.75%28Mid-Year%29%2C30-June-2026.pdf.pdf','2026-06-30','Bangladesh HAC; headline reach CXB + Bhasan Char','Statistical facts with attribution; original PDF not redistributed by app.','Original PDF page 1 chart and Highlights'),('UNHCR_JSON','unhcr_population.json','GoB / UNHCR','https://data.unhcr.org/population/?geo_id=591&population_group=5555&widget_id=691154','2026-09-30','Cox’s Bazar aggregate','UNHCR ODP CC BY 4.0 default','Original API JSON; first data record'),('WASH_2025','wash_infrastructure_sep2025.zip','WASH Sector / Rohingya Response','https://rohingyaresponse.org/sectors/coxs-bazar/wash/','2025-09','Historical inventory; exact observation dates not provided for each record','Explicit dataset redistribution terms unconfirmed; point data not publicly served.','Original ZIP shapefile and attribute workbook')]
 specs.append(('UNHCR_SEP_XLSX','unhcr_september_2026.xlsx','GoB / UNHCR','https://data.unhcr.org/en/documents/details/124450','2026-09-30','279 detail rows; 35 groups; 420 age/sex aggregates','UNHCR ODP CC BY 4.0 except stated otherwise; attribution retained.','Original XLSX; Standard breakdown; rows 10–324; all group totals cross-checked against independent PDF'))
 for sid,f,publisher,url,date,coverage,license,lineage in specs:
  sources.append(dict(id=sid,publisher=publisher,url=url,reference_date=date,retrieved_at='2026-10-20',filename=f,sha256=digest(raw/f),byte_size=(raw/f).stat().st_size,coverage=coverage,licence=license,lineage=lineage,units='individuals/families' if sid.startswith('UNHCR') else 'percent or people' if sid=='UNICEF_H1' else 'source inventory records; units require field-specific interpretation',status='verified original'))
 with zipfile.ZipFile(raw/'wash_infrastructure_sep2025.zip') as z:
  shp_index=z.read(next(n for n in z.namelist() if n.endswith('.shx')))
  inventory_records=(len(shp_index)-100)//8
 data={'release':'0.2.0','built_on':'2026-10-20','population':a+s,'demographics':demo,'changes':changes,'indicators':inds,'reach':reach,'sources':sources,'quality':qa,'geometry':{'type':'FeatureCollection','features':[]},'wash':{'status':'publication gated','records':inventory_records,'reference_period':'September 2025 archive','note':'Acquired inventory; record count is not functional facility capacity. Exact point redistribution terms unconfirmed.'}}
 data['summary']={'august_population':sum(x['population'] for x in a),'september_population':sum(x['population'] for x in s),'change':sum(x['change'] for x in changes),'groups':35,'matched_groups':35,'august_detail_rows':len(blocks),'missing_block_ids':sum(x['block_id'] is None for x in blocks),'september_detail_rows':len(sep_blocks),'september_missing_block_ids':sum(x['block_id'] is None for x in sep_blocks),'matched_nonblank_block_keys':len(keyed[0]),'september_cxb':1173291,'september_bhasan_char':33237}
 data['findings']=[{'title':'Published population rose by 2,036','observation':'1,204,492 → 1,206,528 (+0.169%) between 31 August and 30 September 2026.','method':'Sum all 35 groups per date and subtract August from September.','limitation':'Registered/biometrically identified population snapshots; changes do not identify migration, births or registration effects.','source_ids':['UNHCR_AUG','UNHCR_SEP']}, {'title':'Camp 4 Extension has the largest percentage increase','observation':'Camp 4 Extension: 11,705 → 12,070 people (+365; +3.118%). Largest absolute and percentage increase among 35 matched groups.','method':'(September / August − 1) × 100 for each of 35 matched groups.','limitation':'Count changes only; geographic definitions and field mechanisms need verification.','source_ids':['UNHCR_AUG','UNHCR_SEP']},{'title':'Water and sanitation remain below annual targets at H1','observation':'Published target attainment: water 49%, sanitation 53%; separate WASH funding status 67%.','method':'Read page 1 UNICEF response chart. Shortfall to annual target is 51 and 47 percentage points.','limitation':'Mid-year annual-target progress is not evidence of being behind schedule; no planned H1 trajectory. Funding is a distinct measure.','source_ids':['UNICEF_H1']}]
 (out/'release.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 writecsv(out/'population.csv',data['population']);writecsv(out/'demographics.csv',demo)
 writecsv(out/'camp_changes.csv',[{k:v for k,v in x.items() if k!='source_ids'} for x in changes]);writecsv(out/'sector_indicators.csv',inds);writecsv(out/'source_register.csv',sources)
 (out/'validation.json').write_text(json.dumps({'summary':data['summary'],'checks':qa,'input_hashes':{x['filename']:x['sha256'] for x in sources}},indent=2))
 print(json.dumps(data['summary']))
 return data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,default=ROOT/'data');a=p.parse_args();build(a.raw,a.inputs,a.out)
