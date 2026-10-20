import csv,io,json,sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from shapely.geometry import shape
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.main import app
D=json.loads((ROOT/'data/release.json').read_text());client=TestClient(app)
def test_original_published_totals():
 for date,pop,fam in [('2026-08-31',1204492,251166),('2026-09-30',1206528,251635)]:
  rows=[x for x in D['population'] if x['date']==date]
  assert len(rows)==35;assert sum(x['population'] for x in rows)==pop;assert sum(x['families'] for x in rows)==fam

def test_no_subtotal_doublecounting():
 assert len({(x['label'],x['date']) for x in D['population']})==70
 assert len(D['demographics'])==840
 for x in D['population']:
  assert sum(z['population'] for z in D['demographics'] if z['label']==x['label'] and z['date']==x['date'])==x['population']

def test_change_reconciliation():
 assert len(D['changes'])==35;assert sum(x['change'] for x in D['changes'])==2036
 assert next(x for x in D['changes'] if x['label']=='Camp 4 Extension')['change']==365
 assert next(x for x in D['changes'] if x['label']=='Bhasan Char')['change']==-277

def test_missing_block_ids_not_imputed():assert D['summary']['missing_block_ids']==34

def test_geometry_crs_and_crosswalk():
 g=D['geometry'];assert len(g['features'])==33;assert set(g['metadata']['unmatched_groups'])=={'Bhasan Char','Other'}
 for f in g['features']:
  sh=shape(f['geometry']);assert sh.is_valid;assert 92<sh.bounds[0]<93;assert 20<sh.bounds[1]<22
  assert f['properties']['label'] in {r['label'] for r in D['population']}

def test_indicators_preserve_denominators():
 assert len(D['indicators'])==18
 assert next(x for x in D['indicators'] if x['sector']=='Health' and x['measure_type']=='funded_pct')['percent']==126
 assert all(x['target_shortfall_pp'] is None for x in D['indicators'] if x['measure_type']=='funded_pct')

def test_no_sensitive_inventory_in_public_release():
 assert 'facilities' not in D and 'points' not in D
 assert 'publication gated'==D['wash']['status']

def test_api_totals_and_filter():
 r=client.get('/api/population');assert r.status_code==200;assert r.json()['total']==1206528
 r=client.get('/api/population?camp=Camp%2015');assert r.json()['total']==67821
 assert client.get('/api/population?date=2025-09-30').status_code==422
 assert client.get('/api/population?camp=imaginary').status_code==404

def test_exports_match_filters():
 r=client.get('/api/export/population.csv?date=2026-09-30&camp=Camp%2015');rows=list(csv.DictReader(io.StringIO(r.text)));assert len(rows)==1;assert rows[0]['population']=='67821'
 r=client.get('/api/export/population.csv?date=2026-09-30&search=Extension');assert len(list(csv.DictReader(io.StringIO(r.text))))==2
 assert client.get('/api/export/private.csv').status_code==404

def test_pdf_and_security():
 r=client.get('/api/report.pdf');assert r.status_code==200;assert r.content.startswith(b'%PDF')
 assert client.get('/api/release').headers['x-content-type-options']=='nosniff'
 assert client.post('/api/release',json={'population':0}).status_code==405

def test_frontend_assets():
 assert client.get('/').status_code==200
 for file in ['app.js','style.css','vendor/leaflet.js','vendor/leaflet.css']:assert client.get('/static/'+file).status_code==200

def test_quality_status_current():
 assert next(x for x in D['quality'] if x['rule']=='UNHCR HTML/JSON freshness')['status']=='RESOLVED'
 assert len({s['id'] for s in D['sources']})==len(D['sources'])


def test_september_workbook_crosschecks():
 assert D['summary']['september_detail_rows']==279
 assert D['summary']['september_missing_block_ids']==34
 assert D['summary']['matched_nonblank_block_keys']==245
 assert all(x['source_id']=='UNHCR_SEP_XLSX' for x in D['demographics'] if x['date']=='2026-09-30')
 assert client.get('/api/export/demographics.csv?date=2026-09-30&camp=Camp%2015').status_code==200
 rows=list(csv.DictReader(io.StringIO(client.get('/api/export/demographics.csv?date=2026-09-30&camp=Camp%2015').text)))
 assert len(rows)==12 and sum(int(x['population']) for x in rows)==67821

def test_map_downloads_respect_filters_and_legend():
 import xml.etree.ElementTree as ET
 r=client.get('/api/map.svg');assert r.status_code==200
 root=ET.fromstring(r.text)
 assert len(root.findall('{http://www.w3.org/2000/svg}path'))==34
 assert '25,001-40,000' in r.text and 'EPSG:32646' in r.text
 r=client.get('/api/map.svg?metric=change&camp=Camp%2015')
 assert len(ET.fromstring(r.text).findall('{http://www.w3.org/2000/svg}path'))==2
 assert 'Camp 15: 69' in r.text
 assert client.get('/api/map.svg?camp=Bhasan%20Char').status_code==404
 assert client.get('/api/map.svg?metric=madeup').status_code==422
 pdf=client.get('/api/map.pdf?metric=change')
 from pypdf import PdfReader
 assert pdf.status_code==200 and len(PdfReader(io.BytesIO(pdf.content)).pages)==1
 assert 'Aug-Sep 2026' in PdfReader(io.BytesIO(pdf.content)).pages[0].extract_text()

def test_wash_audit_keeps_units_and_reconciles():
 w=D['wash']['audit'];assert w['records']==78886
 assert sum(w['spatial_status_counts'].values())==78886
 assert w['source_attribute_sums']=={'F__of_Tube':13210,'F__of_Latr':51587,'F__of_Bath':25502}
 assert len(w['camp_aggregates'])==33
 assert sum(x['source_records'] for x in w['camp_aggregates'])==78886
 r=client.get('/api/export/wash.csv?camp=Camp%2015');rows=list(csv.DictReader(io.StringIO(r.text)))
 assert len(rows)==1 and int(rows[0]['source_records'])==7042
 assert 'Longitude' not in r.text and 'Unique_Cod' not in r.text
