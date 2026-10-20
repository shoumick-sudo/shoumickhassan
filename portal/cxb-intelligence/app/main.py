"""Read-only, source-attributed public analytical API."""
import csv,hashlib,io,json,os,textwrap
from pathlib import Path
from fastapi import FastAPI,HTTPException,Query
from fastapi.responses import FileResponse,Response
from fastapi.staticfiles import StaticFiles
from typing import Literal
from app import maps
import psycopg
ROOT=Path(__file__).resolve().parents[1]
app=FastAPI(title="Cox's Bazar Public Evidence Platform",version='0.2.0')

def release():
 url=os.getenv('DATABASE_URL')
 if url:
  try:
   with psycopg.connect(url,connect_timeout=8) as c:
    c.execute('SET TRANSACTION READ ONLY')
    c.execute('SET LOCAL statement_timeout=5000')
    r=c.execute("SELECT payload,sha256 FROM cxb.analysis_release WHERE id='current'").fetchone()
    if r:return r[0],'PostgreSQL / Neon',r[1]
    raise HTTPException(503,'Verified database release is unavailable.')
  except psycopg.Error:raise HTTPException(503,'Database temporarily unavailable; retry shortly.')
 p=ROOT/'data/release.json'
 return json.loads(p.read_text()),'local verified release',hashlib.sha256(p.read_bytes()).hexdigest()

@app.middleware('http')
async def security(request,call_next):
 r=await call_next(request)
 r.headers['X-Content-Type-Options']='nosniff';r.headers['Referrer-Policy']='strict-origin-when-cross-origin';r.headers['X-Frame-Options']='DENY'
 r.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https://*.tile.openstreetmap.org; connect-src 'self'; frame-ancestors 'none'"
 return r
@app.get('/health')
def health():
 d,engine,sha=release();return {'status':'ok','engine':engine,'data_sha256':sha,'groups':d['summary']['groups']}
@app.get('/api/release')
def get_release():
 d,engine,sha=release();return {**d,'engine':engine,'data_sha256':sha}
@app.get('/api/population')
def population(date:str=Query('2026-09-30',pattern='^2026-(08-31|09-30)$'),camp:str|None=None):
 d,_,_=release();r=[x for x in d['population'] if x['date']==date and (camp is None or x['label']==camp)]
 if camp and not r:raise HTTPException(404,'Unknown geography')
 return {'rows':r,'total':sum(x['population'] for x in r),'source_id':r[0]['source_id'] if r else None,'date':date}
@app.get('/api/export/{dataset}.csv')
def export(dataset:str,date:str|None=None,camp:str|None=None,search:str|None=None):
 d,_,_=release();allowed={'population':'population','changes':'changes','demographics':'demographics','sectors':'indicators','sources':'sources','wash':'wash'}
 if dataset not in allowed:raise HTTPException(404,'Unknown dataset')
 rows=d['wash']['audit']['camp_aggregates'] if dataset=='wash' else d[allowed[dataset]]
 if date:rows=[x for x in rows if x.get('date')==date]
 if camp:rows=[x for x in rows if x.get('label',x.get('camp'))==camp]
 if search:rows=[x for x in rows if search.lower() in x.get('label','').lower()]
 if not rows:raise HTTPException(404,'No records match filters')
 rows=[{k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in x.items()} for x in rows]
 out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(dict.fromkeys(k for row in rows for k in row)));w.writeheader();w.writerows(rows)
 return Response(out.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="{dataset}.csv"'})
@app.get('/api/geometry')
def geometry():return release()[0]['geometry']
@app.get('/api/map.svg')
def map_svg(metric:Literal['population','change']='population',camp:str|None=None):
 return Response(maps.svg(release()[0],metric,camp),media_type='image/svg+xml',headers={'Content-Disposition':'attachment; filename="Coxs_Bazar_Camp_Map.svg"'})
@app.get('/api/map.pdf')
def map_pdf(metric:Literal['population','change']='population',camp:str|None=None):
 return Response(maps.pdf(release()[0],metric,camp),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="Coxs_Bazar_Camp_Map.pdf"'})
@app.get('/api/report.pdf')
def report():
 from reportlab.pdfgen import canvas
 from reportlab.lib.pagesizes import A4
 from reportlab.lib.utils import simpleSplit
 d,engine,sha=release();out=io.BytesIO();c=canvas.Canvas(out,pagesize=A4);c.setAuthor('Md Shoumick Hassan');c.setTitle("Cox's Bazar | Public Evidence Brief");y=800
 def line(t,size=10):
  nonlocal y
  c.setFont('Helvetica',size)
  for src,dst in [('→',' -> '),('−','-'),('–','-'),('’',"'"),('‘',"'")]:t=t.replace(src,dst)
  wrapped=textwrap.wrap(t,width=110 if size<=8 else 90,break_long_words=True,break_on_hyphens=False)
  for s in [line for chunk in wrapped for line in simpleSplit(chunk,'Helvetica',size,490)]:
   if y<65:c.showPage();y=800;c.setFont('Helvetica',size)
   c.drawString(50,y,s);y-=size+5
 line("Cox's Bazar | Public Evidence Brief",17);line('Md Shoumick Hassan',12);line('Information Management & Spatial Analytics | Release '+d['release']+' | 20 October 2026',9);y-=12
 for f in d['findings']:
  line(f['title'],12);line(f['observation']);line('Calculation: '+f['method']);line('Limit: '+f['limitation']);line('Sources: '+', '.join(f['source_ids']));y-=8
 line('Scope and provenance',12)
 for s in d['sources']:line(s['id']+' | '+s['publisher']+' | '+s['reference_date']);line(s['url'],8)
 line('Data SHA-256: '+sha,8);line('Database: '+engine,8);c.save()
 return Response(out.getvalue(),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="Coxs_Bazar_Evidence_Brief.pdf"'})
@app.get('/')
def home():return FileResponse(ROOT/'static/index.html')
app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
