-- All programme values are synthetic. Outputs are service events, never unique people.
-- 1. Indicator results and matching targets; missing reports remain in denominator.
SELECT sector,indicator,unit,SUM(COALESCE(actual,0)) observed_output,SUM(target) target,
 ROUND(100.0*SUM(COALESCE(actual,0))/NULLIF(SUM(target),0),1) pct_target,
 SUM(approved) approved_reports,COUNT(*) expected_reports
FROM report_monitor GROUP BY sector,indicator,unit;
-- 2. Follow-up roster includes expected reports absent from submissions.
SELECT report_id,period,partner_id,location_id,received,approved
FROM report_monitor WHERE approved=0 ORDER BY received,period,partner_id;
-- 3. Latest observed facility state. Unknown/stale states require separate treatment.
SELECT f.sector,s.status,COUNT(*) facilities FROM facilities f JOIN facility_status s USING(facility_id)
WHERE s.observed_at=(SELECT MAX(s2.observed_at) FROM facility_status s2 WHERE s2.facility_id=s.facility_id)
GROUP BY f.sector,s.status;
-- 4. Find revisions excluded from the current publication view.
SELECT s.* FROM submissions s LEFT JOIN approved_submissions a USING(submission_id)
WHERE a.submission_id IS NULL;
