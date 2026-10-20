# Release validation — 20 October 2026

## Automated checks executed

12 pytest tests passed on the local release: original month totals and family totals; group uniqueness; demographic reconciliation; exact count changes; retention of 34 missing source block IDs; 33 valid source polygons and WGS84 coordinate bounds; indicator measure distinctions and funding >100%; exclusion of restricted points; API date and camp filtering; CSV filter reconciliation; PDF validity/security headers/read-only API; frontend asset serving; and current source-quality statuses.

A separate PostgreSQL/PostGIS check records the normalized warehouse totals, all polygon validity, sum of changes and absence of reader INSERT/UPDATE privileges. See database validation JSON in Drive.

Local PostgreSQL TCP access is unavailable in this execution environment (DNS failure); warehouse load used the connected Neon SQL transaction tool. Runtime connection is tested separately from Render. Failed loads were transactional and did not partially modify source tables.

Live hosting, browser filters/map/export checks and mobile layout are tracked in the deployment record. This file alone is not proof that they passed.

Not complete: full September block-level workbook; WASH rights/functionality clearance; geospatial facility inventory analysis; applicant independent rerun and five-minute demonstration. No claim of independent human verification or operational institutional adoption.
