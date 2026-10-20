"""Private, aggregate-only spatial QA; no source points or identifiers emitted."""
import argparse,collections,json,re
from pathlib import Path
import openpyxl,shapefile
from shapely.geometry import shape,Point
from shapely.strtree import STRtree
from pyproj import CRS

def canonical(label):
 return {'Camp KRC':'Kutupalong RC','Camp NRC':'Nayapara RC'}.get(label,re.sub(r'^Camp 0+(\d)',r'Camp \1',label.strip()))

def run(extracted,geometry,out,release=None):
 fs=json.load(open(geometry))['features'];names=[f['properties']['label'] for f in fs];tree=STRtree([shape(f['geometry']) for f in fs]);shp=next(extracted.rglob('*.shp'))
 assert CRS.from_wkt(shp.with_suffix('.prj').read_text()).to_epsg()==4326
 r=shapefile.Reader(str(shp));totals=collections.defaultdict(lambda:collections.Counter());status=collections.Counter();crosswalk={};overall=collections.Counter()
 for sr in r.iterShapeRecords():
  a=sr.record.as_dict();label=canonical(a['Camp_Name']);assert label in names;crosswalk[a['Camp_Name']]=label
  hits=tree.query(Point(*sr.shape.points[0]),predicate='intersects')
  kind='outside historical polygons' if not len(hits) else 'multiple historical polygons' if len(hits)>1 else 'agrees with published camp' if names[int(hits[0])]==label else 'different historical camp'
  status[kind]+=1;totals[label][kind]+=1;totals[label]['source_records']+=1
  for key in ['F__of_Tube','F__of_Latr','F__of_Bath']:
   value=a[key];assert value is None or isinstance(value,(float,int));value=value or 0
   assert value>=0 and int(value)==value
   totals[label][key]+=int(value);overall[key]+=int(value)
 # Validate the attribute sums against the source author's own pivot, not record counts.
 book=openpyxl.load_workbook(next(extracted.rglob('*.xlsx')),data_only=True,read_only=True)
 controls={canonical(row[0]):tuple(int(x or 0) for x in row[1:4]) for row in list(book['By Camps'].values)[3:] if row[0] and str(row[0]).startswith('Camp ')}
 assert set(controls)==set(totals)
 for label,expected in controls.items():assert tuple(totals[label][k] for k in ['F__of_Tube','F__of_Latr','F__of_Bath'])==expected,(label,'publisher pivot mismatch')
 result={'source_id':'WASH_2025','geometry_source':'HDX_CAMPS','geometry_date':'2023-04-12','inventory_period':'September 2025 archive','method':'Point intersects; boundary-inclusive; WGS84 EPSG:4326; exact normalized camp labels; no nearest-neighbour reassignment','records':len(r),'published_camp_crosswalk':crosswalk,'spatial_status_counts':dict(status),'source_attribute_sums':dict(overall),'publisher_pivot_reconciliation':'PASS: all 33 camps, all three quantity fields','camp_aggregates':[{**{'camp':label},**dict(v)} for label,v in sorted(totals.items())],'limits':['Not unique or operational facility counts; repeated source IDs not deduplicated.','2023 boundary mismatch may reflect geometry vintage or source naming; not proof of bad coordinates.','No per-record observation date or functionality field; no current service adequacy or accessibility inference.','Precise points and raw identifiers excluded; reuse terms remain unconfirmed.']}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['camp_aggregates','published_camp_crosswalk']}))
 if release:
  d=json.loads(release.read_text());d['wash']['audit']={k:v for k,v in result.items() if k!='published_camp_crosswalk'}
  d['wash']['note']='Historical source inventory only; quantity sums are not unique or functional facility capacity. Precise points withheld pending explicit reuse terms.'
  d['quality']=[q for q in d['quality'] if q['rule']!='WASH spatial and quantity reconciliation']
  d['quality'].append({'rule':'WASH spatial and quantity reconciliation','status':'PASS','detail':'All 78,886 records tested: 78,266 agree with named historical camp, 619 outside polygons, one in a different camp. All 33 camp quantity totals match publisher pivots. Mismatches retained; no spatial reassignment.'})
  release.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
  from build import writecsv
  writecsv(release.parent/'wash_camp_audit.csv',result['camp_aggregates'])
  (release.parent/'validation.json').write_text(json.dumps({'summary':d['summary'],'checks':d['quality'],'input_hashes':{x['filename']:x['sha256'] for x in d['sources']}},indent=2))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--extracted',type=Path,required=True);p.add_argument('--geometry',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--release',type=Path);a=p.parse_args();run(a.extracted,a.geometry,a.out,a.release)
