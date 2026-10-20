"""Emit migration/load SQL for environments without direct PostgreSQL egress."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def lit(x):return "'"+str(x).replace("'","''")+"'"
def bundle():
 d=json.loads((ROOT/'data/release.json').read_text());q=[(ROOT/'sql/001_schema.sql').read_text()]
 for s in d['sources']:q.append('INSERT INTO cxb.source_asset VALUES('+lit(s['id'])+','+lit(json.dumps(s))+'::jsonb) ON CONFLICT(id) DO UPDATE SET metadata=excluded.metadata')
 for label in sorted({x['label'] for x in d['population']}):q.append('INSERT INTO cxb.geography(id,label) VALUES('+lit(label)+','+lit(label)+') ON CONFLICT DO NOTHING')
 for x in d['population']:q.append('INSERT INTO cxb.population_snapshot VALUES('+','.join(map(lit,[x['label'],x['date'],x['population'],x['families'],x['source_id']]))+') ON CONFLICT DO NOTHING')
 for x in d['demographics']:q.append('INSERT INTO cxb.demographic_snapshot VALUES('+','.join(map(lit,[x['label'],x['date'],x['age'],x['sex'],x['population'],x['source_id']]))+') ON CONFLICT DO NOTHING')
 for i,x in enumerate(d['indicators']):q.append('INSERT INTO cxb.sector_indicator VALUES('+lit(i)+','+lit(json.dumps(x))+'::jsonb) ON CONFLICT DO NOTHING')
 for f in d['geometry']['features']:q.append('UPDATE cxb.geography SET geometry=ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON('+lit(json.dumps(f['geometry']))+'),4326)),geometry_source=\'HDX_CAMPS\' WHERE id='+lit(f['properties']['label']))
 p=ROOT/'data/release.json';q.append('INSERT INTO cxb.analysis_release(id,payload,sha256) VALUES(\'current\','+lit(p.read_text())+'::jsonb,'+lit(hashlib.sha256(p.read_bytes()).hexdigest())+') ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,sha256=excluded.sha256,loaded_at=now()')
 return q
if __name__=='__main__':print(json.dumps(bundle()))
