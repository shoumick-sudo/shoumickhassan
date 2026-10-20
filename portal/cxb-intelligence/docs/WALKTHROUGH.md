# Five-minute technical walkthrough and independent rerun

This is a prepared script, not evidence that the applicant has performed it. Use only claims you can explain and reproduce. Keep the application deadline independent of optional platform enhancements.

## Suggested live demonstration

**0:00-0:40 — Scope and provenance.** Open the live platform. State: independent, AI-assisted public-data portfolio, separate from professional NSDA work. Show 35 published groups; explain why 33 camp polygons exclude Bhasan Char and Other. Open UNHCR source document 124450 and its dated checksum.

**0:40-1:30 — Reconciliation.** Select September and Camp 4 Extension. Show 12,070 people versus 11,705 in August: +365, +3.118%. State that snapshot differences do not identify arrivals or causes. Switch dates and show the corresponding age/sex pyramid. Explain that subtotal rows are controls and the parallel five-year sheet is excluded. Both workbooks have 279 detail rows, 34 missing block IDs and 245 matching nonblank block keys; missing IDs are never invented.

**1:30-2:20 — Database and API.** Explain source_asset, geography, population_snapshot, demographic_snapshot and analysis_release. Show the read-only API and one filtered CSV. Explain the separate SELECT-only web role, server-side DATABASE_URL and HTTP 503 on database failure. Do not display credentials.

**2:20-3:15 — GIS.** Open Coxs_Bazar_Public_Evidence.qgz with camp_metrics.gpkg beside it. Toggle the population/change layers and inspect the saved print layout. Explain EPSG:32646 for projected mapping/areas, EPSG:4326 GeoJSON display, historical 12-Apr-2023 boundaries and exact published-name joins. Export a PDF and locate its source attribution, legend, scale and north arrow.

**3:15-4:10 — WASH quality.** Show aggregate audit: 78,266 records agree with named historical camp; 619 outside all polygons; one in a different camp. Publisher quantity sums reconcile in all 33 camps. Repeated codes are retained: records, cubicles and functional capacity are different units. No current access or shortage estimate follows from this 2025 inventory.

**4:10-5:00 — Indicators and limitations.** Show H1 UNICEF WASH attainment of 49% water and 53% sanitation against annual targets, with funding separately 67%. Explain why mid-year annual-target gaps do not prove schedule delay, and why overlapping reach counts cannot be summed or divided by a different date/geography's population.

## Independent rerun checklist

1. Clone the isolated cxb-real-data-release branch; enter portal/cxb-intelligence. Install requirements in a clean Python 3.12 virtual environment.
2. Obtain original files and source-tagged UNICEF extracted CSVs from the designated source archive. Verify their SHA-256 against data/source_register.csv. Keep detailed source files outside the public repository.
3. Run the ETL commands in README, including spatial and WASH audit stages. Inspect totals and missingness. Do not use owner credentials for the web service.
4. Run `python -m pytest -q tests`. Capture the actual terminal output with date and commit. Explain one failing assertion and how its source control works.
5. Run the SQL validation queries below using the separate project's read-only connection. Compare with API totals. Never show the credential in a recording.
6. Open the native QGIS project, check both layers resolve, inspect the print layout and make a fresh PDF export.
7. Record or deliver the five-minute explanation without reading ununderstood claims. Only then update personal proficiency and walkthrough statuses.

```sql
SELECT observation_date, count(*), sum(individuals), sum(families)
FROM cxb.population_snapshot GROUP BY observation_date ORDER BY 1;
SELECT observation_date, count(*), sum(individuals)
FROM cxb.demographic_snapshot GROUP BY observation_date ORDER BY 1;
SELECT count(*), bool_and(ST_IsValid(geometry)) FROM cxb.geography WHERE geometry IS NOT NULL;
SELECT sum(change) FROM cxb.population_change;
SELECT count(*), sum((summary->>'source_records')::integer) FROM cxb.wash_camp_audit;
```

Expected: 35 groups per date; August 1,204,492 people / 251,166 families; September 1,206,528 / 251,635; 420 demographic cells per date reconciling to those people; 33 valid polygons; +2,036 change; 33 WASH camp audit rows covering 78,886 records. Assistant validation is documented separately and must not be represented as applicant-performed work.
