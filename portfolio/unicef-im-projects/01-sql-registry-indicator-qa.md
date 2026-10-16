# 01 — Administrative SQL and Indicator Quality Assurance

**Evidence type:** historical professional task account + synthetic reconstruction.  
**Prepared:** 16 October 2026. **Not** an NSDA system export.

## The practical problem

An administrative reporting table may have one provider linked to multiple courses and multiple assessment/certification rows. Summing after a one-to-many join can inflate provider totals; missing foreign keys can silently omit items; duplicate course keys create inconsistent reporting.

In my NSDA role, I have reported working with PostgreSQL queries through Metabase, data exports and a ministry-oriented report. The precise individual role in that historical deliverable is verified separately from this example, using permissible evidence rather than source data publication.

## Safe runnable example

A [working synthetic Google Sheets workbook](https://docs.google.com/spreadsheets/d/1C-VUB1VrCfsXTtSwWUn2Rl1252O9wDaty52wySJsFg4/edit) contains 8 fictional provider rows and 14 fictional course rows with a lookup from child to master records.

Two fictional course rows use the same key **CR12**. One row points to nonexistent provider **P99**. These seeded errors exist to show why validation must occur before approval.

| Fictional group | Unique providers | Active providers | Raw accredited course rows |
|---|---:|---:|---:|
| Group-A | 4 | 3 | 7 |
| Group-B | 4 | 4 | 3 |

**Warning:** the last column intentionally counts raw rows, including the two repeated CR12 rows in Group-A. It is **not** an approved clean indicator. The QA rules flag those two duplicates plus the P99 orphan: three flagged records in all.

## Reproducible SQL pattern

```sql
SELECT
    p.ministry_group,
    COUNT(DISTINCT p.provider_id) AS provider_count,
    COUNT(DISTINCT CASE WHEN p.registration_status = 'Active'
                         THEN p.provider_id END) AS active_provider_count,
    COUNT(DISTINCT CASE WHEN c.accreditation = 'Accredited'
                         AND c.qa_flag = 'OK'
                         THEN c.course_id END) AS reviewed_accredited_courses
FROM providers p
LEFT JOIN courses c ON c.provider_id = p.provider_id
GROUP BY p.ministry_group
ORDER BY p.ministry_group;
```

This query expresses a method, **not actual NSDA SQL**. A release process must additionally review flagged rows, record a correction and reconcile approved output. For this invented example, excluding both duplicate CR12 rows leaves **5** reviewed accredited course IDs in Group-A, and **3** in Group-B, assuming all other rows pass their checks.

## Interview demonstration

Explain the difference between provider grain and course grain; correct the duplicate and orphan in a working copy; show why COUNT(*) is unsafe for provider totals; reconcile the changed result; retain the original exception log.

**UNICEF ToR transfer:** integration and relational data structures; data-quality checks; indicator governance; traceable programme reporting.

## Limits

This case is a reproducible illustration, not historical proof of the applicant's specific job role or official dataset accuracy. No real organizations, credentials or personal records are supplied. The synthetic workbook was AI-assisted and applicant independent operation is still to be verified.
