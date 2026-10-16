# Humanitarian information management demonstrator

**Independent portfolio demonstration using synthetic programme data. Not UNICEF or official response data.**

Prepared for Md Shoumick Hassan with substantial ChatGPT/Codex assistance in design, implementation, synthetic data generation, documentation and automated verification. Created 16 October 2026. Version 0.1.0. The applicant's independent walkthrough and practical assessment remain pending. This release is a technical demonstration, not evidence of journal publication, real humanitarian delivery or independent authorship of all code.

## Explore

Open `outputs/dashboard.html` in any modern browser. It runs offline, with no installation or network requests. Sector, period, partner and location filters update reporting, target and service-event summaries. Download the filtered reporting CSV or print the current view. The facility panel has a separately labelled historical reference date and filter scope.

`outputs/Programme_Reporting.xlsx` contains editable reporting formulas and a costed-target exercise. `outputs/Synthetic_Reporting_XLSForm.xlsx` is a form-design artifact; it has not been deployed or validated in Kobo/ODK. Excel desktop testing is pending.

## Reproduce the core

Use Python 3.10 or later. No third-party packages, API keys or external datasets are needed. From this directory:

```bash
python src/pipeline.py
python -m unittest discover -s tests -v
python src/build_dashboard.py
```

The pipeline overwrites generated files in `data/` and the CSV/JSON/SQLite outputs. It does not overwrite source code or the two XLSX workbooks. Do not store manual changes in generated output files. The workbook is a release snapshot; refresh its Report source from `outputs/report_monitor.csv` in Excel after changing the generator, then verify formulas and reconcile with SQL. Core reproduction does not regenerate the workbook.

## What is included

- Seeded fictional reporting data: six partners, twelve locations, three sectors, six months and 108 facilities.
- SQL schema, primary/foreign keys, constraints and analytical views.
- Immutable raw-row archive, submission versions, issue log and current approved results.
- Fourteen named automated tests covering seeded defects, missingness, versions, foreign keys, arithmetic reconciliation, reproducibility and backup/restore.
- A dashboard, spreadsheet reporting model, XLSForm design, collection-export adapter, management brief, indicator specifications, operating guide and partner orientation.

Read [the technical note](docs/TECHNICAL_NOTE.md) and [the operating guide](docs/OPERATING_GUIDE.md) before drawing conclusions from the example.

## Scope of claims

This uses SQLite, Python and browser JavaScript. It does not demonstrate PostgreSQL administration, live authentication, multi-user access enforcement, a production API, Power BI, QGIS/ArcGIS, ActivityInfo or deployed digital collection. The spatial panel is a fictional schematic, not a geographic map. Facility observations are stale at the reporting cutoff. Event counts are not unique beneficiaries. No real people, child records, refugee records, government datasets or institutional confidential material are included.

Public source is available for inspection. No open-source or data licence has been adopted for this new project. The author's earlier study-specific licences do not automatically extend to this case study. No institutional affiliation, endorsement or clearance is implied.
