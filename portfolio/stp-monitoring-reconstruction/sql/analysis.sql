-- Fictional monitoring rubric. Never use these bands as NSDA regulatory ratings.
-- Due roster denominator: missing reports remain; future rounds are excluded.
SELECT round_date,COUNT(*) expected,SUM(received) received,COUNT(submission_id) approved,
SUM(on_time) timely,ROUND(AVG(score_pct),2) mean_approved_score
FROM report_monitor WHERE due_date<='2026-10-16' GROUP BY round_date;

-- Follow-up list; score is null when no current approved observation exists.
SELECT report_id,provider_id,officer_id,round_date,received,score_pct,review_band
FROM report_monitor WHERE due_date<='2026-10-16' AND (submission_id IS NULL OR score_pct<75)
ORDER BY round_date,score_pct;

-- Matched-provider descriptive change between first and fourth rounds.
SELECT COUNT(*) matched_providers,ROUND(AVG(b.score_pct-a.score_pct),2) mean_paired_change_pp
FROM report_monitor a JOIN report_monitor b USING(provider_id)
WHERE a.round_date='2026-09-18' AND b.round_date='2026-10-09'
AND a.submission_id IS NOT NULL AND b.submission_id IS NOT NULL;

-- A claimed closure needs both evidence and verification.
SELECT *,CASE WHEN status='closed' AND TRIM(closure_evidence)<>'' AND verification='verified'
THEN 1 ELSE 0 END closure_accepted FROM actions;
