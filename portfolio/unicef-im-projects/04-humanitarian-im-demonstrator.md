# 04 — Humanitarian Information Management Demonstrator

**Type:** AI-assisted independent synthetic portfolio demonstration, built 16 October 2026. Not historical work for UNICEF, another UN agency, or a real refugee response.

## Why this example

The UNICEF Information Management Officer ToR combines multiple data concerns: shared master data, reporting expectations, indicator definitions, revision control, validation, planned versus achieved outputs, geographic coverage, dashboards and clear reporting trails. This demonstration treats them as one integrated fictional reporting service.

**[Open interactive demonstrator](https://shoumick-humanitarian-im-evidence.snappyraven4.chatgpt.site)**  
**[Inspect Python/SQLite source](../humanitarian-im-v1)**

## Scope of fictional reporting data

- Six fictitious partner organizations, twelve fictitious locations, three programme sectors and six reporting months.
- 108 fictitious facilities.
- 2,667 raw fictional observation rows with revision history; 432 expected report keys, 6 missing reports and 18 rejected revisions.
- 408 approved reports and 2,448 current approved observation rows, according to the 16 October build checkpoint.

Those figures are **synthetic record counts**, never people reached or results achieved in a real operation.

## Architecture and governance

Python/SQLite generation and cleaning; master partner/location/indicator definitions; expected submissions; validation and issue logs; raw versus approved revision selection; reconciliation; spreadsheet output; a browser dashboard; collection-form design; a simulated SOP/RACI, handover material and reporting brief.

The build checkpoint reports 14 Python tests and 8 dashboard logic checks passed during preparation. That is **not** proof of the applicant's independent execution. Current gaps include current real QGIS or Power BI artifact, ActivityInfo experience, end-user training actually delivered and application-level privacy/security validation.

## Questions to ask the applicant

1. Why does an expected report with no submission differ from a reported zero?
2. Why must rejected version 3 not automatically replace previously approved version 2?
3. What happens to a reported coverage ratio when its target is corrected?
4. How do source rows, SQL query outputs, dashboard figures and report text reconcile?
5. What data classifications and permissions would govern a real sensitive refugee-response dataset?

## Role match

UNICEF ToR I–VII, especially central systems, integrity checks, partner reporting cycles, data visualization, SOPs and capacity-guidance methods.

## Evidence boundary

Every partner, location, facility and programme figure is invented. The demo does not prove operational UN experience, real SitRep/JRP/HAC reporting, substantive GIS fieldwork or specialist platform use. All claims of proficiency require the applicant to reproduce and explain the workflow. No institutional endorsement or peer-reviewed publication is implied.
