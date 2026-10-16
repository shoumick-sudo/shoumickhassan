PRAGMA foreign_keys=ON;
CREATE TABLE providers(provider_id TEXT PRIMARY KEY,label TEXT,zone TEXT);
CREATE TABLE officers(officer_id TEXT PRIMARY KEY,label TEXT);
CREATE TABLE expectations(report_id TEXT PRIMARY KEY,provider_id TEXT REFERENCES providers,officer_id TEXT REFERENCES officers,round_date TEXT,due_date TEXT,UNIQUE(provider_id,round_date));
CREATE TABLE raw_rows(row_id INTEGER PRIMARY KEY,payload TEXT NOT NULL);
CREATE TABLE submissions(submission_id TEXT PRIMARY KEY,report_id TEXT REFERENCES expectations,version INTEGER CHECK(version>0),submitted_on TEXT,decision TEXT CHECK(decision IN ('approved','draft','rejected')),UNIQUE(report_id,version));
CREATE TABLE scores(submission_id TEXT PRIMARY KEY REFERENCES submissions,raw_row_id INTEGER REFERENCES raw_rows,infrastructure INTEGER CHECK(infrastructure BETWEEN 0 AND 4),equipment INTEGER CHECK(equipment BETWEEN 0 AND 4),trainers INTEGER CHECK(trainers BETWEEN 0 AND 4),records INTEGER CHECK(records BETWEEN 0 AND 4),assessment_readiness INTEGER CHECK(assessment_readiness BETWEEN 0 AND 4));
CREATE TABLE dq_issues(issue_id INTEGER PRIMARY KEY,raw_row_id INTEGER REFERENCES raw_rows,submission_id TEXT,rule TEXT,action TEXT);
CREATE TABLE actions(action_id TEXT PRIMARY KEY,provider_id TEXT REFERENCES providers,owner TEXT,due_date TEXT,status TEXT CHECK(status IN ('open','in_progress','closed')),closure_evidence TEXT,verification TEXT CHECK(verification IN ('pending','verified')));
CREATE VIEW approved_current AS
SELECT s.*,v.raw_row_id,v.infrastructure,v.equipment,v.trainers,v.records,v.assessment_readiness,
25.0*(v.infrastructure+v.equipment+v.trainers+v.records+v.assessment_readiness)/5 AS score_pct
FROM submissions s JOIN scores v USING(submission_id)
WHERE s.decision='approved' AND NOT EXISTS
(SELECT 1 FROM submissions n WHERE n.report_id=s.report_id AND n.decision='approved' AND n.version>s.version);
CREATE VIEW report_monitor AS
SELECT e.*,p.label,p.zone,
EXISTS(SELECT 1 FROM submissions s WHERE s.report_id=e.report_id) received,
EXISTS(SELECT 1 FROM submissions s WHERE s.report_id=e.report_id AND s.submitted_on<=e.due_date) on_time,
a.submission_id,a.version,a.score_pct,a.infrastructure,a.equipment,a.trainers,a.records,a.assessment_readiness,
CASE WHEN a.score_pct IS NULL THEN 'unavailable' WHEN a.score_pct<50 THEN 'priority' WHEN a.score_pct<75 THEN 'attention' ELSE 'routine' END review_band
FROM expectations e JOIN providers p USING(provider_id) LEFT JOIN approved_current a USING(report_id);
