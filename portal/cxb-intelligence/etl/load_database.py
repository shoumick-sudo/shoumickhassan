"""Load only public, validated aggregates. DATABASE_URL must be an owner credential."""
import hashlib,json,os,re
from pathlib import Path
import psycopg
from psycopg.types.json import Jsonb
ROOT=Path(__file__).resolve().parents[1]
def load(url):
 p=ROOT/'data/release.json';d=json.loads(p.read_text())
 with psycopg.connect(url) as c:
  c.execute((ROOT/'sql/001_schema.sql').read_text())
  for s in d['sources']:c.execute('INSERT INTO cxb.source_asset VALUES(%s,%s) ON CONFLICT(id) DO UPDATE SET metadata=excluded.metadata',(s['id'],Jsonb(s)))
  for label in sorted({x['label'] for x in d['population']}):c.execute('INSERT INTO cxb.geography(id,label) VALUES(%s,%s) ON CONFLICT(id) DO NOTHING',(label,label))
  for x in d['population']:c.execute('INSERT INTO cxb.population_snapshot VALUES(%s,%s,%s,%s,%s) ON CONFLICT(geo_id,observation_date) DO UPDATE SET individuals=excluded.individuals,families=excluded.families,source_id=excluded.source_id',(x['label'],x['date'],x['population'],x['families'],x['source_id']))
  for x in d['demographics']:c.execute('INSERT INTO cxb.demographic_snapshot VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(geo_id,observation_date,age_band,sex) DO UPDATE SET individuals=excluded.individuals,source_id=excluded.source_id',(x['label'],x['date'],x['age'],x['sex'],x['population'],x['source_id']))
  for i,x in enumerate(d['indicators']):c.execute('INSERT INTO cxb.sector_indicator VALUES(%s,%s) ON CONFLICT(id) DO UPDATE SET observation=excluded.observation',(str(i),Jsonb(x)))
  for f in d['geometry']['features']:
   c.execute('UPDATE cxb.geography SET geometry=ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s),4326)),geometry_source=%s WHERE id=%s',(json.dumps(f['geometry']),'HDX_CAMPS',f['properties']['label']))
  for x in d['wash']['audit']['camp_aggregates']:c.execute('INSERT INTO cxb.wash_camp_audit(geo_id,source_id,summary) VALUES(%s,%s,%s) ON CONFLICT(geo_id,source_id) DO UPDATE SET summary=excluded.summary',(x['camp'],'WASH_2025',Jsonb(x)))
  c.execute('INSERT INTO cxb.analysis_release(id,payload,sha256) VALUES(%s,%s,%s) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,sha256=excluded.sha256,loaded_at=now()',('current',Jsonb(d),hashlib.sha256(p.read_bytes()).hexdigest()))
  totals=c.execute('SELECT observation_date::text,sum(individuals),sum(families),count(*) FROM cxb.population_snapshot GROUP BY observation_date ORDER BY observation_date').fetchall()
  changes=c.execute('SELECT sum(change),count(*) FROM cxb.population_change').fetchone()
  assert totals==[('2026-08-31',1204492,251166,35),('2026-09-30',1206528,251635,35)]
  assert changes==(2036,35)
  print(json.dumps({'totals':totals,'changes':changes,'postgis':c.execute('SELECT postgis_version()').fetchone()[0]},default=str))
if __name__=='__main__':load(os.environ['DATABASE_URL'])
