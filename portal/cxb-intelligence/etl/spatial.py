"""Verified HDX camp polygons; EPSG:32646 -> EPSG:4326; explicit name joins."""
import argparse,collections,json,zipfile
from pathlib import Path
import shapefile
from shapely.geometry import shape,mapping
from shapely.ops import transform
from pyproj import Transformer,CRS
from build import digest,writecsv
ROOT=Path(__file__).resolve().parents[1]
def run(raw,boundary):
 d=json.loads((ROOT/'data/release.json').read_text());p=next(boundary.rglob('*.shp'));r=shapefile.Reader(str(p))
 crs=CRS.from_wkt(p.with_suffix('.prj').read_text()).to_2d();assert crs.to_epsg()==32646
 to_wgs=Transformer.from_crs(crs,4326,always_xy=True).transform
 counts={x['label']:x for x in d['changes']};features=[];audit=[]
 for sr in r.iterShapeRecords():
  attr=sr.record.as_dict();label=attr['CampName'];g=shape(sr.shape.__geo_interface__)
  assert g.is_valid and not g.is_empty
  geo=transform(to_wgs,g);assert 92<geo.bounds[0]<93 and 20<geo.bounds[1]<22
  # Source uses 'Kutupalong RC' and 'Nayapara RC'; no fuzzy or approximate geocoding.
  assert label in counts,('unmatched polygon',label)
  f={'type':'Feature','geometry':json.loads(json.dumps(mapping(geo)),parse_float=lambda v:round(float(v),7)),'properties':{'label':label,'pcode':attr['CampSSID'],'source_id':'HDX_CAMPS','geometry_date':'2023-04-12','source_crs':'EPSG:32646','display_crs':'EPSG:4326','historical_area_km2':round(g.area/1e6,6),'population':counts[label]['september'],'change':counts[label]['change']}}
  features.append(f);audit.append({'population_label':label,'geometry_label':label,'pcode':attr['CampSSID'],'method':'exact published CampName','status':'matched'})
 unmatched=sorted(set(counts)-{f['properties']['label'] for f in features});assert len(features)==33
 meta=json.load(open(raw/'hdx_metadata.json'))['result'];resource=next(x for x in meta['resources'] if x['name'].endswith('.zip'))
 d['sources']=[s for s in d['sources'] if s['id']!='HDX_CAMPS'];d['sources'].append({'id':'HDX_CAMPS','publisher':'RRRC / ISCG / Site Management Sector / UNHCR / IOM via HDX','url':'https://data.humdata.org/dataset/'+meta['name'],'download_url':resource['url'],'reference_date':'2023-04-12','retrieved_at':'2026-10-20','filename':'hdx_camp_outlines.zip','sha256':digest(raw/'hdx_camp_outlines.zip'),'byte_size':(raw/'hdx_camp_outlines.zip').stat().st_size,'coverage':'33 Cox’s Bazar camp polygons; excludes Bhasan Char and Other','licence':meta['license_title'],'lineage':'Original SHP; CampName/CampSSID; EPSG:32646 to 4326; coordinates rounded to 7 decimals','units':'polygons; historical area km2','status':'verified original'})
 d['geometry']={'type':'FeatureCollection','features':features,'metadata':{'source_id':'HDX_CAMPS','geometry_date':'2023-04-12','licence':meta['license_title'],'matched_groups':len(features),'unmatched_groups':unmatched,'coverage_note':'Historical 2023 boundaries joined to 2026 published population; not verified current outlines.'}}
 d['quality']=[q for q in d['quality'] if q['rule']!='Camp geometry / crosswalk'];d['quality'].append({'rule':'Camp geometry / crosswalk','status':'PASS','detail':f'33 valid polygons transformed from EPSG:32646 to 4326. Exact name joins; unmatched: {", ".join(unmatched)}. Historical geometry explicitly labelled.'})
 (ROOT/'data/release.json').write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')));(ROOT/'data/camp_boundaries.geojson').write_text(json.dumps(d['geometry']))
 writecsv(ROOT/'data/geo_crosswalk_review.csv',audit+[{'population_label':x,'geometry_label':'','pcode':'','method':'no geometry in source','status':'unmatched'} for x in unmatched])
 writecsv(ROOT/'data/source_register.csv',d['sources'])
 print(json.dumps(d['geometry']['metadata']))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--boundaries',type=Path,required=True);a=p.parse_args();run(a.raw,a.boundaries)
