"""Create, reopen and render an actual native QGIS project using QGIS 3.34+.
Run with the desktop QGIS Python environment, not the web-server venv.
"""
import argparse,json,os,sys
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from qgis.core import (Qgis,QgsApplication,QgsProject,QgsVectorLayer,QgsVectorFileWriter,QgsCoordinateReferenceSystem,QgsFillSymbol,QgsRendererRange,QgsGraduatedSymbolRenderer,QgsPrintLayout,QgsLayoutItemMap,QgsLayoutPoint,QgsLayoutSize,QgsLayoutItemLabel,QgsLayoutItemLegend,QgsLayoutItemScaleBar,QgsLayoutExporter,QgsUnitTypes,QgsRectangle,QgsWkbTypes)
from qgis.PyQt.QtGui import QColor,QFont
ROOT=Path(__file__).resolve().parents[1]
def run(out):
 out.mkdir(parents=True,exist_ok=True);project=QgsProject.instance();project.setCrs(QgsCoordinateReferenceSystem('EPSG:32646'));project.setFilePathStorage(Qgis.FilePathType.Relative)
 d=json.loads((ROOT/'data/release.json').read_text());temp=out/'camp_metrics.geojson';temp.write_text(json.dumps(d['geometry']))
 layer=QgsVectorLayer(str(temp),'source','ogr');assert layer.isValid() and layer.featureCount()==33
 opts=QgsVectorFileWriter.SaveVectorOptions();opts.driverName='GPKG';opts.layerName='camp_metrics';opts.fileEncoding='UTF-8';opts.overrideGeometryType=QgsWkbTypes.MultiPolygon;opts.forceMulti=True
 result=QgsVectorFileWriter.writeAsVectorFormatV3(layer,str(out/'camp_metrics.gpkg'),project.transformContext(),opts);assert result[0]==QgsVectorFileWriter.NoError,result
 layers=[]
 for metric,title,classes in [('population','People, 30 Sep 2026',[(0,25000,'#c2dfb9','<=25,000'),(25000,40000,'#5eb39b','25,001-40,000'),(40000,55000,'#148774','40,001-55,000'),(55000,1000000,'#07534d','>55,000')]),('change','Aug-Sep count change',[(-1000000,-.5,'#bd8664','Negative'),(-.5,50,'#a5d2b8','0-50'),(50,200,'#399b87','51-200'),(200,1000000,'#08695f','>200')])]:
  l=QgsVectorLayer(str(out/'camp_metrics.gpkg')+'|layername=camp_metrics',title,'ogr');assert l.isValid();ranges=[]
  for lower,upper,col,label in classes:
   symbol=QgsFillSymbol.createSimple({'color':col,'outline_color':'#ffffff','outline_width':'0.15'});ranges.append(QgsRendererRange(lower,upper,symbol,label))
  l.setRenderer(QgsGraduatedSymbolRenderer(metric,ranges));project.addMapLayer(l);layers.append(l)
  metadata=l.metadata();metadata.setTitle(title+' / historical 2023 boundaries');metadata.setAbstract('Population: GoB/UNHCR September 2026 XLSX document 124450; independently reconciled with factsheet 124447. Outlines: ISCG/HDX 12 April 2023, CC0. No facility locations. Bhasan Char and Other unmapped.');l.setMetadata(metadata)
 project.layerTreeRoot().findLayer(layers[1].id()).setItemVisibilityChecked(False)
 layout=QgsPrintLayout(project);layout.initializeDefaults();layout.setName('September population - source and limits');layout.pageCollection().pages()[0].setPageSize('A4',QgsLayoutItemPage.Portrait)
 def label(text,x,y,w,h,size=9):
  item=QgsLayoutItemLabel(layout);item.setText(text);item.setFont(QFont('DejaVu Sans',size));layout.addLayoutItem(item);item.attemptMove(QgsLayoutPoint(x,y));item.attemptResize(QgsLayoutSize(w,h));return item
 label("Cox's Bazar | Public evidence",14,10,180,12,17)
 label('Population, 30 September 2026 | Md Shoumick Hassan',14,25,182,10,9)
 mapitem=QgsLayoutItemMap(layout);layout.addLayoutItem(mapitem);mapitem.attemptMove(QgsLayoutPoint(14,40));mapitem.attemptResize(QgsLayoutSize(132,192));mapitem.setCrs(project.crs());mapitem.setLayers([layers[0]]);mapitem.setKeepLayerSet(True)
 extent=QgsCoordinateTransform(layers[0].crs(),project.crs(),project).transformBoundingBox(layers[0].extent());extent.scale(1.08);mapitem.zoomToExtent(extent)
 legend=QgsLayoutItemLegend(layout);legend.setTitle('Individuals');layout.addLayoutItem(legend);legend.setLinkedMap(mapitem);legend.setAutoUpdateModel(False);legend.model().rootGroup().clear();legend.model().rootGroup().addLayer(layers[0]);legend.attemptMove(QgsLayoutPoint(149,51));legend.attemptResize(QgsLayoutSize(48,60))
 label('N\n↑',153,122,15,22,14)
 scale=QgsLayoutItemScaleBar(layout);scale.setStyle('Single Box');scale.setLinkedMap(mapitem);scale.setUnits(QgsUnitTypes.DistanceKilometers);scale.setUnitsPerSegment(2);scale.setNumberOfSegments(1);scale.setNumberOfSegmentsLeft(0);scale.setUnitLabel('km');scale.setFont(QFont('DejaVu Sans',8));layout.addLayoutItem(scale);scale.attemptMove(QgsLayoutPoint(150,163))
 label('33 of 35 groups mapped.\nBhasan Char and Other\nhave no source geometry.',149,184,49,30,8)
 label('CRS: WGS 84 / UTM 46N\nEPSG:32646\nNo basemap',149,216,49,22,8)
 label('Population: GoB / UNHCR, 31 Aug and 30 Sep 2026. data.unhcr.org/documents/124450\nOutlines: ISCG / HDX, 12 Apr 2023, CC0. Historical polygons; current boundaries unverified.\nCount changes do not establish movement, causes, service access or functional capacity.\nSource crosswalk, methods and all 35 published groups accompany the project.',14,244,183,36,8)
 project.layoutManager().addLayout(layout);project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent,project.crs()));project.setTitle("Cox's Bazar Public Evidence | 20 October 2026");project.setFileName(str(out/'Coxs_Bazar_Public_Evidence.qgz'));assert project.write()
 pdf=out/'Coxs_Bazar_QGIS_Map.pdf';exporter=QgsLayoutExporter(layout);assert exporter.exportToPdf(str(pdf),QgsLayoutExporter.PdfExportSettings())==QgsLayoutExporter.Success
 # Reopen the saved file in a fresh project: validates relative paths, provider and saved layout.
 check=QgsProject();assert check.read(str(out/'Coxs_Bazar_Public_Evidence.qgz'));assert len(check.mapLayers())==2
 assert all(l.isValid() and l.featureCount()==33 for l in check.mapLayers().values());assert len(check.layoutManager().layouts())==1
 # Native engine rerender after reopen; inspect resulting PNG and PDF separately.
 png=out/'Coxs_Bazar_QGIS_Map.png';assert QgsLayoutExporter(check.layoutManager().layouts()[0]).exportToImage(str(png),QgsLayoutExporter.ImageExportSettings())==QgsLayoutExporter.Success
 qa={'qgis_version':Qgis.QGIS_VERSION,'project_reopened':True,'valid_layers':2,'features_per_layer':33,'project_crs':check.crs().authid(),'relative_paths':True,'pdf_export':'success','png_export_after_reopen':'success','personal_desktop_demonstration':'pending; assistant execution does not establish applicant proficiency'}
 (out/'QGIS_QA.json').write_text(json.dumps(qa,indent=2));print(json.dumps(qa));return qa
if __name__=='__main__':
 from qgis.core import QgsLayoutItemPage,QgsCoordinateTransform,QgsReferencedRectangle
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();qgs=QgsApplication([],False);qgs.initQgis();run(args.out)
 QgsProject.instance().clear()
 import gc;gc.collect();qgs.exitQgis()
