# Native GIS handover

The Drive release folder contains Coxs_Bazar_Native_QGIS_Handover.zip: a native .qgz project, conformant MULTIPOLYGON GeoPackage, actual QGIS-generated PDF and reopened-layout PNG, source register, all-group CSV, historical geometry crosswalk, WASH aggregate audit and a README.

Created and reopened using QGIS 3.34.4. Two saved graduated layers each resolve to 33 features through a relative GeoPackage path. Layout uses EPSG:32646 with legend, north arrow, 2 km scale and source/coverage notes. GeoPackage stores EPSG:4326; historical source geometry date is 12-Apr-2023. No raw WASH locations or record IDs are included. See QGIS_QA.json.

Run `QT_QPA_PLATFORM=offscreen /usr/bin/python3 etl/qgis_project.py --out /absolute/path/gis` from an installed QGIS Python environment. Keep the complete package together when opening it on another computer. The web-service environment requires no QGIS installation.

The map totals 1,172,922 people and +2,313 change across 33 camp polygons. The public all-35-group universe totals 1,206,528 and +2,036, because Bhasan Char (33,237; -277) and Other (369; zero change) lack source polygons. These coverage differences must remain explicit.

This verifies an assistant-built native GIS artifact. Applicant independent opening, modification, export and explanation are still required before claiming personal desktop GIS proficiency.
