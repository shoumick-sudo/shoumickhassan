"""Deterministic cartographic exports, projected to WGS 84 / UTM zone 46N."""
import io
from xml.sax.saxutils import escape
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform
from fastapi import HTTPException

PALETTE={'population':[('#c2dfb9','<=25,000'),('#5eb39b','25,001-40,000'),('#148774','40,001-55,000'),('#07534d','>55,000')],
         'change':[('#bd8664','Negative'),('#a5d2b8','0-50'),('#399b87','51-200'),('#08695f','>200')]}
def color(value,metric):
 i=(0 if value<0 else 1 if value<=50 else 2 if value<=200 else 3) if metric=='change' else (0 if value<=25000 else 1 if value<=40000 else 2 if value<=55000 else 3)
 return PALETTE[metric][i][0]

def scene(data,metric,camp):
 features=[f for f in data['geometry']['features'] if not camp or f['properties']['label']==camp]
 if not features:raise HTTPException(404,'No mapped camp matches the filter')
 project=Transformer.from_crs(4326,32646,always_xy=True).transform
 shapes=[transform(project,shape(f['geometry'])) for f in features]
 xmin=min(g.bounds[0] for g in shapes);ymin=min(g.bounds[1] for g in shapes);xmax=max(g.bounds[2] for g in shapes);ymax=max(g.bounds[3] for g in shapes)
 scale=min(650/(xmax-xmin),550/(ymax-ymin));xoff=50+(650-(xmax-xmin)*scale)/2;yoff=100+(550-(ymax-ymin)*scale)/2
 def xy(x,y):return xoff+(x-xmin)*scale,yoff+(ymax-y)*scale
 paths=[]
 for f,g in zip(features,shapes):
  polys=[g] if g.geom_type=='Polygon' else list(g.geoms)
  rings=[[xy(x,y) for x,y in ring.coords] for poly in polys for ring in [poly.exterior,*poly.interiors]]
  paths.append((rings,color(f['properties'][metric],metric),f['properties']['label'],f['properties'][metric]))
 title="Cox's Bazar | "+('Aug-Sep 2026 population change' if metric=='change' else 'September 2026 population')
 distance=next(x for x in [1000,500,200,100,50,20,10,5,1] if x*scale<=150)
 texts=[(50,38,title,24),(50,65,(camp or '33 matched camp polygons')+' | Individuals | WGS 84 / UTM zone 46N (EPSG:32646)',12),
 (760,125,'Legend | Individuals',13),(760,330,'N',16),(760,435,('1 km' if distance==1000 else str(distance)+' m'),11),
 (50,700,'Population: GoB / UNHCR, 30 Sep 2026. Change baseline: 31 Aug 2026.',12),
 (50,724,'Outlines: ISCG / HDX, 12 Apr 2023, CC0. Historical boundaries; no basemap.',12),
 (50,748,'Coverage: 33 of 35 groups. Bhasan Char and Other have no geometry in this source.',11),
 (50,772,'Independent AI-assisted portfolio. Count changes do not establish movement, causes or service access.',11),
 (50,796,'Sources: data.unhcr.org/documents/124450 | data.humdata.org/dataset/outline-of-camps-sites-of-rohingya-refugees-in-cox-s-bazar-bangladesh',8)]
 return paths,texts,scale*distance

def svg(data,metric,camp=None):
 paths,texts,scale=scene(data,metric,camp)
 parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="820" viewBox="0 0 1000 820">','<rect width="1000" height="820" fill="#f7f8f4"/>']
 for rings,fill,label,value in paths:
  path=''.join('M'+'L'.join(f'{x:.3f},{y:.3f}' for x,y in ring)+'Z' for ring in rings)
  parts.append(f'<path d="{path}" fill="{fill}" fill-rule="evenodd" stroke="white" stroke-width="0.8"><title>{escape(label)}: {value}</title></path>')
 for x,y,t,size in texts:parts.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" fill="#183b35">{escape(t)}</text>')
 for i,(c,label) in enumerate(PALETTE[metric]):
  y=150+i*31;parts.append(f'<rect x="760" y="{y}" width="20" height="17" fill="{c}"/><text x="792" y="{y+14}" font-family="sans-serif" font-size="12">{escape(label)}</text>')
 parts.append(f'<path d="M765,350L765,390M765,350L760,360M765,350L770,360M760,415L{760+scale:.3f},415" stroke="#183b35" fill="none" stroke-width="2"/>')
 parts.append('</svg>');return ''.join(parts)

def pdf(data,metric,camp=None):
 from reportlab.pdfgen import canvas
 from reportlab.lib.colors import HexColor
 from reportlab.lib.pagesizes import landscape,A4
 paths,texts,scale=scene(data,metric,camp);out=io.BytesIO();c=canvas.Canvas(out,pagesize=landscape(A4));factor=min(A4[1]/1000,A4[0]/820);c.translate((A4[1]-1000*factor)/2,0);c.scale(factor,factor)
 c.setFillColor(HexColor('#f7f8f4'));c.rect(0,0,1000,820,fill=1,stroke=0)
 for rings,fill,_,_ in paths:
  p=c.beginPath()
  for ring in rings:
   p.moveTo(ring[0][0],820-ring[0][1])
   for x,y in ring[1:]:p.lineTo(x,820-y)
   p.close()
  c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor('#ffffff'));c.setLineWidth(.8);c.drawPath(p,fill=1,stroke=1,fillMode=0)
 c.setFillColor(HexColor('#183b35'))
 for x,y,t,size in texts:c.setFont('Helvetica',size);c.drawString(x,820-y,t)
 for i,(fill,label) in enumerate(PALETTE[metric]):
  y=150+i*31;c.setFillColor(HexColor(fill));c.rect(760,820-y-17,20,17,fill=1,stroke=0);c.setFillColor(HexColor('#183b35'));c.setFont('Helvetica',12);c.drawString(792,820-y-14,label)
 c.setStrokeColor(HexColor('#183b35'));c.setLineWidth(2)
 for a,b in [((765,350),(765,390)),((765,350),(760,360)),((765,350),(770,360)),((760,415),(760+scale,415))]:c.line(a[0],820-a[1],b[0],820-b[1])
 c.setTitle(texts[0][2]);c.showPage();c.save();return out.getvalue()
