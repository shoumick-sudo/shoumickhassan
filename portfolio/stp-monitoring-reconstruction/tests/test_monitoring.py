import csv,importlib.util,json,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build',ROOT/'src/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
class MonitoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.out=Path(cls.tmp.name);cls.data=b.fixture();cls.c,cls.issues=b.db_build(cls.data,cls.out,'2026-10-16');cls.summary=b.export(cls.c,cls.data,cls.issues,cls.out,'2026-10-16')
    @classmethod
    def tearDownClass(cls):cls.c.close();cls.tmp.cleanup()
    def test_deterministic_generation(self):self.assertEqual(self.data,b.fixture())
    def test_expected_report_grain(self):
        self.assertEqual(len(self.data['expectations']),240)
        self.assertEqual(len({(r['provider_id'],r['round_date']) for r in self.data['expectations']}),240)
    def test_future_expectations_not_in_denominator(self):
        self.assertEqual(self.summary['due_reports'],192);self.assertEqual(self.summary['future_expectations'],48)
    def test_missing_reports_remain_visible(self):
        missing={r['report_id'] for r in self.data['seeded_truth'] if r['rule']=='missing_report'}
        actual={r[0] for r in self.c.execute("SELECT report_id FROM report_monitor WHERE received=0 AND due_date<='2026-10-16'")};self.assertEqual(missing,actual)
    def test_seeded_bad_versions_all_detected(self):
        detected={(i['submission_id'].split('-v')[0],i['rule']) for i in self.issues}
        for r in self.data['seeded_truth']:
            if r['rule']!='missing_report':self.assertIn((r['report_id'],r['rule']),detected)
    def test_raw_preservation(self):self.assertEqual(self.c.execute('SELECT COUNT(*) FROM raw_rows').fetchone()[0],204)
    def test_duplicate_version_wholly_excluded(self):
        for rid in ['MON-0163','MON-0169']:
            self.assertEqual(self.c.execute('SELECT COUNT(*) FROM approved_current WHERE report_id=?',(rid,)).fetchone()[0],0)
    def test_latest_approved_ignores_new_draft(self):
        self.assertEqual(self.c.execute("SELECT version FROM approved_current WHERE report_id='MON-0001'").fetchone()[0],2)
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM approved_current WHERE version=3').fetchone()[0],0)
    def test_formula_matches_independent_row_calculation(self):
        raw={r['row_id']:r for r in self.data['raw']}
        for row in self.c.execute('SELECT raw_row_id,score_pct FROM approved_current'):
            self.assertAlmostEqual(row['score_pct'],sum(raw[row['raw_row_id']][k] for k in b.CRITERIA)/20*100,places=10)
    def test_missing_vs_zero_score(self):
        r=dict(self.data['raw'][0]);r.update({k:0 for k in b.CRITERIA});self.assertEqual(b.validate([r],self.data['expectations'],'2026-10-16'),[])
        r['records']='';self.assertIn('missing_score',[i['rule'] for i in b.validate([r],self.data['expectations'],'2026-10-16')])
    def test_fractional_rating_rejected(self):
        r=dict(self.data['raw'][0],equipment=2.5);self.assertIn('score_range',[i['rule'] for i in b.validate([r],self.data['expectations'],'2026-10-16')])
    def test_invalid_and_before_round_dates(self):
        for value,rule in [('not-a-date','invalid_date'),('2026-01-01','receipt_before_round')]:
            r=dict(self.data['raw'][0],submitted_on=value);self.assertIn(rule,[i['rule'] for i in b.validate([r],self.data['expectations'],'2026-10-16')])
    def test_no_closure_without_evidence_and_verification(self):
        with (self.out/'action_tracker.csv').open() as f:a=next(r for r in csv.DictReader(f) if r['action_id']=='ACT-001')
        self.assertEqual(a['status'],'closed');self.assertEqual(a['closure_accepted'],'0');self.assertEqual(a['overdue'],'1')
    def test_foreign_keys_and_integrity(self):
        self.assertEqual(self.c.execute('PRAGMA foreign_keys').fetchone()[0],1);self.assertEqual(list(self.c.execute('PRAGMA foreign_key_check')),[]);self.assertEqual(self.c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        with self.assertRaises(sqlite3.IntegrityError):self.c.execute("INSERT INTO actions VALUES ('X','MISSING','DEMO','2026-10-01','open','','pending')")
    def test_common_grain_prevents_version_inflation(self):
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM report_monitor WHERE due_date<='2026-10-16'").fetchone()[0],192)
        self.assertEqual(self.c.execute('SELECT COUNT(DISTINCT report_id) FROM approved_current').fetchone()[0],self.summary['approved_reports'])
    def test_paired_change_uses_only_matched_providers(self):
        r=list(self.c.execute("SELECT a.provider_id,a.score_pct x,b.score_pct y FROM report_monitor a JOIN report_monitor b USING(provider_id) WHERE a.round_date='2026-09-18' AND b.round_date='2026-10-09' AND a.submission_id IS NOT NULL AND b.submission_id IS NOT NULL"))
        self.assertEqual(len(r),len({x['provider_id'] for x in r}));self.assertLess(len(r),48)
    def test_imported_candidates_are_drafts(self):
        path=self.out/'candidate.csv';b.csv_write(path,[self.data['raw'][0]])
        target=self.out/'imported';p=subprocess.run([sys.executable,str(ROOT/'src/build.py'),'--source',str(path),'--output',str(target)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr);summary=json.loads((target/'summary.json').read_text());self.assertEqual(summary['approved_reports'],0);self.assertEqual(summary['received_reports'],1)
    def test_backup_restore_preserves_results(self):
        clone=sqlite3.connect(self.out/'backup.sqlite');self.c.backup(clone);self.assertEqual(clone.execute('SELECT COUNT(*) FROM approved_current').fetchone()[0],172);clone.close()
if __name__=='__main__':unittest.main(verbosity=2)
