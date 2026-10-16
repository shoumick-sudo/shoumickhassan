PRAGMA foreign_keys=ON;
CREATE TABLE locations(location_id TEXT PRIMARY KEY,label TEXT NOT NULL,x REAL,y REAL);
CREATE TABLE partners(partner_id TEXT PRIMARY KEY,sector TEXT NOT NULL,indicator TEXT NOT NULL,unit TEXT NOT NULL);
CREATE TABLE expectations(report_id TEXT PRIMARY KEY,partner_id TEXT REFERENCES partners,location_id TEXT REFERENCES locations,period TEXT,due_date TEXT,UNIQUE(partner_id,location_id,period));
CREATE TABLE submissions(submission_id TEXT PRIMARY KEY,report_id TEXT REFERENCES expectations,version INTEGER CHECK(version>0),received_date TEXT,status TEXT CHECK(status IN ('approved','draft','rejected')),UNIQUE(report_id,version));
CREATE TABLE raw_rows(row_id INTEGER PRIMARY KEY,payload TEXT NOT NULL);
CREATE TABLE issues(issue_id INTEGER PRIMARY KEY,row_id INTEGER REFERENCES raw_rows,submission_id TEXT,rule TEXT,severity TEXT,owner TEXT,action TEXT,status TEXT);
CREATE TABLE observations(row_id INTEGER PRIMARY KEY REFERENCES raw_rows,submission_id TEXT REFERENCES submissions,sex TEXT CHECK(sex IN ('F','M','U')),age TEXT CHECK(age IN ('child','adult')),value INTEGER CHECK(value>=0),UNIQUE(submission_id,sex,age));
CREATE TABLE plans(report_id TEXT PRIMARY KEY REFERENCES expectations,target INTEGER CHECK(target>=0),unit_cost REAL CHECK(unit_cost>=0));
CREATE TABLE facilities(facility_id TEXT PRIMARY KEY,location_id TEXT REFERENCES locations,sector TEXT);
CREATE TABLE facility_status(facility_id TEXT REFERENCES facilities,observed_at TEXT,status TEXT CHECK(status IN ('functional','disrupted','unknown')),PRIMARY KEY(facility_id,observed_at));
CREATE VIEW approved_submissions AS
 SELECT s.* FROM submissions s WHERE status='approved' AND NOT EXISTS
 (SELECT 1 FROM submissions newer WHERE newer.report_id=s.report_id AND newer.status='approved' AND newer.version>s.version);
CREATE VIEW approved_results AS
 SELECT e.report_id,e.partner_id,e.location_id,e.period,p.sector,p.indicator,p.unit,o.sex,o.age,o.value,o.row_id,s.submission_id,s.version
 FROM approved_submissions s JOIN expectations e USING(report_id) JOIN partners p USING(partner_id) JOIN observations o USING(submission_id);
CREATE VIEW report_monitor AS
 SELECT e.*,p.sector,p.indicator,p.unit,pl.target,pl.unit_cost,
 EXISTS(SELECT 1 FROM submissions s WHERE s.report_id=e.report_id) AS received,
 EXISTS(SELECT 1 FROM submissions s WHERE s.report_id=e.report_id AND s.received_date<=e.due_date) AS on_time,
 EXISTS(SELECT 1 FROM approved_submissions s WHERE s.report_id=e.report_id) AS approved,
 (SELECT SUM(r.value) FROM approved_results r WHERE r.report_id=e.report_id) AS actual
 FROM expectations e JOIN partners p USING(partner_id) JOIN plans pl USING(report_id);
