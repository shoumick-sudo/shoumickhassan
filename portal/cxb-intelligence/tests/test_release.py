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
 assert len(D['demographics'])==420
 for x in D['population']:
  if x['date']=='2026-08-31':assert sum(z['population'] for z in D['demographics'] if z['label']==x['label'])==x['population']

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
