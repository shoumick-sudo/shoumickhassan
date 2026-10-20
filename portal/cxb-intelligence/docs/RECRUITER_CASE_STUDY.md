# Public humanitarian evidence with a reproducible audit trail

**Md Shoumick Hassan | Information Management & Spatial Analytics | October 2026**

**Problem.** Public humanitarian statistics arrive as spreadsheets, PDFs, web-page excerpts and historical spatial layers. A polished chart can conceal missing camps, duplicated totals, inconsistent periods and unsupported service-access claims.

**Delivered system.** A read-only FastAPI and PostgreSQL/PostGIS platform reconciles GoB/UNHCR August and September 2026 population snapshots for all 35 published geographical groups; displays 840 camp/age/sex aggregates across both months; joins 33 genuine ISCG/HDX camp polygons; and presents UNICEF H1 2026 programme-target and funding measures separately. It provides interactive filters, source inspection, CSV exports, projected SVG/PDF maps and a native QGIS project, PDF briefs, data hashes and reproducible Python ETL.

**Evidence.** August's 279 detail rows reproduce 1,204,492 people and 251,166 families without counting subtotals twice. September's 279 workbook detail rows independently match the original PDF's 1,206,528 people and 251,635 families. The difference is 2,036; Camp 4 Extension rises by 365 (+3.118%), the largest increase among matched groups. These changes do not establish arrivals or causes. Two population groups lack polygons and remain visibly unmapped.

**Judgment demonstrated by the product.** Missing source block identifiers are preserved. An earlier JSON date discrepancy is closed only after a fresh matching retrieval. WASH facility points remain withheld pending dataset-specific rights and functionality checks. UNICEF funding percentages above 100% are retained, and programme reach is never added across overlapping services or divided by an incompatible population total.


**Review route.** Open the live release URL in the deployment record; inspect Sources & Quality; filter Camp 4 Extension; export the count comparison; inspect the map's 2023 geometry caveat; rerun the documented tests and ETL.
