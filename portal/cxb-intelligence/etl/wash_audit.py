"""Audit a downloaded WASH shapefile privately; never emit precise coordinates or IDs."""
import argparse,collections,json,zipfile,tempfile
from pathlib import Path
import shapefile

def run(archive,out):
 with tempfile.TemporaryDirectory() as td:
  with zipfile.ZipFile(archive) as z:z.extractall(td)
  shp=next(Path(td).rglob('*.shp'));r=shapefile.Reader(str(shp));ids=collections.Counter();types=collections.Counter();camps=collections.Counter();bad=0;coord_disagreement=0;missing=0
  for sr in r.iterShapeRecords():
   a=sr.record.as_dict();code=a['Unique_Cod'];ids[code]+=1;types[a['Type_of_Fa']]+=1;camps[a['Camp_Name']]+=1
   if not code:missing+=1
   x,y=sr.shape.points[0]
   if not (92<x<93 and 20<y<22):bad+=1
   if abs(x-a['Longitude'])>1e-6 or abs(y-a['Latitude'])>1e-6:coord_disagreement+=1
  qa={'source_file':archive.name,'inventory_label':'September 2025','retrieval_date':'2026-10-20','records':len(r),'unique_nonblank_codes':len([x for x in ids if x]),'duplicate_code_excess':sum(v-1 for k,v in ids.items() if k and v>1),'missing_codes':missing,'invalid_coordinate_bounds':bad,'attribute_geometry_coordinate_mismatches':coord_disagreement,'source_crs':shp.with_suffix('.prj').read_text(),'facility_type_record_counts':dict(types),'published_camp_label_record_counts':dict(camps),'operational_status_field_present':False,'publication_status':'Precise points and row IDs withheld pending explicit reuse terms. Counts describe source records, not functional facility capacity.'}
  out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(qa,indent=2));print(json.dumps({k:v for k,v in qa.items() if not isinstance(v,dict)}))
 return qa
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.archive,a.out)
