# Cox’s Bazar Public Evidence Platform

**Md Shoumick Hassan**

Population analysis, interactive GIS and humanitarian information management using source-verified public datasets.

## Release 0.2.0 — 20 October 2026

Implemented: FastAPI read-only API, PostgreSQL/PostGIS warehouse on a separate Neon project, population snapshots for 35 published groups in August and September 2026, 840 camp/age/sex aggregates across both months, exact monthly reconciliation, 33 genuine camp polygons, Leaflet filters/popups/legend, population and demographic comparisons, UNICEF H1 target/funding charts, provenance and QA panels, filtered CSV exports, projected SVG/PDF map exports, a native QGIS project and generated PDF brief. Backend tests and live/browser verification are recorded separately.

September population: **1,206,528**; August: **1,204,492**; difference **2,036**. These are count changes, not demonstrated movements. Camp 4 Extension has the largest absolute (+365) and relative (+3.118%) increase among 35 matched groups.

## Run the public release

Requires Python 3.12+ and pip. From `portal/cxb-intelligence`:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q tests
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Without DATABASE_URL the application explicitly identifies its local verified release. For hosted use, supply a read-only DATABASE_URL through the host's secret configuration; it never appears in client code. If the configured database is unavailable, API returns 503 rather than silently presenting local data as live database results.

## Reproduce ETL from original publishers

Original XLSX/PDF/ZIPs stay in the designated Drive archive. Obtain the files listed in `data/source_register.csv`; verify SHA-256 before processing. `pdftotext` (Poppler) is required to reconstruct September's side-by-side table. Place originals in an external `raw` directory; do not commit restricted files. Download the source-tagged UNICEF extracted CSV inputs from the same Drive package.

```sh
python etl/build.py --raw /absolute/path/raw --inputs /absolute/path/inputs
unzip /absolute/path/raw/hdx_camp_outlines.zip -d /absolute/path/boundaries
python etl/spatial.py --raw /absolute/path/raw --boundaries /absolute/path/boundaries
python etl/wash_spatial_audit.py --extracted /absolute/path/private_wash --geometry data/camp_boundaries.geojson --out /absolute/path/private/WASH_SPATIAL_QA_PRIVATE.json --release data/release.json
# Native QGIS (desktop Python, not the web-server environment):
QT_QPA_PLATFORM=offscreen /usr/bin/python3 etl/qgis_project.py --out /absolute/path/gis
# Administrative connection only for loading, never the public web service:
DATABASE_URL='<owner connection>' python etl/load_database.py
```

`etl/sql_bundle.py` supports loading through the connected Neon SQL tools where local PostgreSQL egress is blocked. Split the schema by semicolons into separate prepared statements. All loads target only the new cxb schema in the new cxb_public database.

## Data and inference limits

- August: original 279 detail rows, 35 groups, 34 missing block IDs retained. Both months publish camp-level demographics; the alternate age breakdown is not counted again.
- September: all 35 groups from page 2 of the official PDF, independently reconciled to 1,206,528 people and 251,635 families. Official September block XLSX (UNHCR document 124450) independently matches every PDF group/family total; 279 detail rows, 34 missing block IDs, and 245 nonblank keys shared with August.
- Geometry: 33 polygons from ISCG/HDX, 12 April 2023, CC0. Source EPSG:32646 transformed to EPSG:4326; output coordinates rounded to 7 decimal degrees. Bhasan Char and Other have no geometry in this source. Historical boundaries do not establish current outlines.
- WASH: September 2025 ZIP with 78,886 source records acquired. Precise points withheld because explicit reuse terms, per-record observation dates and functionality definitions remain unresolved. Aggregate spatial QA covers all records and reconciles all 33 camp quantity sums to publisher pivots; no service-capacity or facility-ratio claim is published.
- UNICEF: H1 annual-target progress, sector funding and headline reach remain separate. Funding may exceed 100%; no cap or invented denominator. No sum of overlapping service reach or mixing with September population.
- An earlier UNHCR JSON/HTML date discrepancy was resolved by a new original API retrieval on 20 October; the release records the dated resolution.

See `docs/METHODOLOGY.md`, `docs/GIS_HANDOVER.md`, and `docs/VALIDATION.md` for analytical methods, GIS workflows and verification records.

## Rights

Source data retain their original rights. HDX camp geometry is CC0 per the downloaded dataset metadata. UNHCR ODP data use its stated CC BY 4.0 default except stated otherwise. UNICEF statistical facts are attributed; original PDFs are linked, not republished by the app. Do not treat repository availability as permission to relicense original material. Leaflet 1.9.4 is BSD-2-Clause; its license is retained in static/vendor.
