# Technical note

Independent portfolio demonstration using synthetic programme data. Not UNICEF or official response data.

## Purpose and architecture

The example shows how an information-management officer can connect a reporting roster, stable master codes, validation, revision control, indicator calculations and management reporting. Everything represents a fictional programme. Operational dates are April–September 2026, with a 16 October 2026 cutoff. Seed 20261016 controls synthetic generation. There is no primary survey, actual intervention, causal analysis or empirical humanitarian finding.

`expected report roster → simulated submissions and raw rows → validation and issue log → approved submission selection → SQL reporting view → dashboard / spreadsheet / management brief`

`sql/schema.sql` owns the database model. One expected report is one partner–location–month. Each partner belongs to one sector and reports one event indicator. The six expected cells per report are sex F/M/U crossed with child/adult. Child means under 18; adult means 18 or older. U means sex unknown. These are mutually exclusive reporting categories, not actual person records. There are no disability data. Repeated contacts across reporting cells or months cannot establish unique people reached.

## Release values

- 432 expected reports, 426 received and 408 with an approved current version.
- 2,667 raw rows preserved; 2,448 rows in current approved results.
- Six reports entirely absent; eighteen defective versions rejected.
- 42 issue flags across 36 flagged rows, including multiple flags on some rows. Duplicate-cell reports also trigger coverage flags on otherwise valid cells. The report-level exclusion affects 111 rows, including other cells in the affected reports.
- Twelve approved revised reports supersede version 1; six newer drafts never replace the approved version.
- Fourteen automated tests pass. These are assistant-run software tests and arithmetic checks. They are not independent human review or evidence of applicant proficiency.

## Rules and aggregation

Negative values, missing values, fractional counts, invalid sex/age categories, mismatched location and report codes, duplicate cells, and incorrect six-cell coverage produce critical issues. Critical issues quarantine the entire submission version. The raw layer remains unchanged. Rejection is a simulated technical status, not a real partner or programme decision. Rows in earlier approved versions and valid drafts remain in the database but are excluded from the current publication view.

Select the latest approved version by report ID, never the maximum version regardless of status. SQL constructs an expected-report left-side view so missing submissions are visible. All expectations are due by the cutoff; this release does not demonstrate future-due roster filtering.

Receipt completeness = reports received / reports expected. Approval completeness = reports with a current approved version / reports expected. Timeliness = reports received on or before the due date / reports expected. A timely receipt may contain invalid data. The simulation assigns the same receipt date to all revisions of a report, so it does not test realistic revision receipt chronology.

Output = sum of six cells from selected approved versions. Matching target = sum of report-level targets at the same sector, period, partner and location scope. Targets remain present for missing or rejected reports. Missing actuals stay null and are shown as unavailable in detailed reporting. The sum of observed actuals is a partial observed total, not proof that missing reports have zero activity. Never sum targets after joining them to six disaggregation rows; that multiplies the denominator sixfold.

Every expected report has an illustrative target of 900 events. Targets are scenario parameters, not needs estimates. Unit costs are illustrative US-dollar-per-event parameters. Costed target = event target × unit cost. No PIN, CIN, unique reach, funding need or real budget is inferred.

## Facility and spatial products

108 fictional facilities have two observations, on 28 and 30 September. The latest snapshot includes functional, disrupted and unknown statuses. At 16 October all are 16 days old and fail a seven-day freshness rule. The dashboard labels them historical. It cannot support current emergency decisions.

The twelve locations occupy an arbitrary 4 × 3 local XY grid. `fictional_grid.json` is a schematic feature collection with no geographic CRS. It is not RFC7946 GeoJSON and must not be interpreted as latitude/longitude. No map tiles, administrative boundaries, real camp locations, routing or GIS software are used. GIS competency is an explicit remaining gap.

## Reproducibility and limitations

Python's standard-library generator and SQLite build reproduce the core files. SQL and independent Python aggregation agree in the tests. SQLite foreign-key enforcement is enabled on the build connection. A backup/restore test checks preservation of approved results. Actual database access is controlled by the local filesystem; role-based security described in the SOP is a proposed deployment policy and has not been implemented or tested.

The dashboard embeds release data and works offline. The workbook uses SUMIFS, COUNTIF and matching-denominator formulas; generator changes require deliberate refresh and reconciliation. It was recalculated and rendered with the authoring engine, and an editable unit-cost change was tested. Microsoft Excel desktop behavior remains unverified. The XLSForm is authored but not compiled, deployed or used by real enumerators. The CSV adapter converts a mock form export to long-form staging records; it does not authenticate users or approve data.

Substantial AI assistance produced code, synthetic inputs, documentation and verification. The applicant must independently reproduce, alter and explain the workflow before presenting it as personal skills evidence. Real training delivery, institutional implementation and humanitarian impact are not claimed.

## External references

Context only; no third-party data or documents redistributed:

- Vacancy and linked ToR: https://jobs.unicef.org/en-us/job/596316/information-management-officer-no2-ta-364-days-138681-coxs-bazar-bangladesh-apro
- SQLite foreign-key documentation: https://sqlite.org/foreignkeys.html
- Zenodo publication and DOI workflow: https://help.zenodo.org/docs/deposit/create-new-upload/

Accessed 16 October 2026. The vacancy informs the competency selection. This demonstrator does not implement or reproduce an official UNICEF platform or reporting template.
