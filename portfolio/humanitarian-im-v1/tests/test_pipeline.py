import importlib.util,json,sqlite3,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pipeline',ROOT/'src/pipeline.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.data=p.generate()
        cls.c,cls.issues=p.build(cls.data,Path(cls.tmp.name)/'test.sqlite')
    @classmethod
    def tearDownClass(cls):cls.c.close();cls.tmp.cleanup()
    def test_reproducible_seed(self):self.assertEqual(self.data,p.generate())
    def test_master_and_expected_grain(self):
        self.assertEqual(len(self.data['expectations']),432)
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM report_monitor').fetchone()[0],432)
    def test_all_seeded_defects_detected(self):
        for t in self.data['seeded_truth']:
            if t['rule']=='missing_report':continue
            self.assertIn((t['submission_id'],t['rule']),{(i['submission_id'],i['rule']) for i in self.issues})
    def test_missing_reports_not_lost(self):
        missing={r['report_id'] for r in self.data['seeded_truth'] if r['rule']=='missing_report'}
        actual={r[0] for r in self.c.execute('SELECT report_id FROM report_monitor WHERE received=0')}
        self.assertEqual(missing,actual)
    def test_latest_approved_and_draft_isolation(self):
        for i in range(1,13):
            self.assertEqual(self.c.execute('SELECT version FROM approved_submissions WHERE report_id=?',(f'R{i:04}',)).fetchone()[0],2)
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM approved_results WHERE version=3').fetchone()[0],0)
    def test_rejected_submissions_never_published(self):
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM approved_results r JOIN submissions s USING(submission_id) WHERE s.status!='approved'").fetchone()[0],0)
    def test_raw_rows_all_preserved(self):
        self.assertEqual(self.c.execute('SELECT COUNT(*) FROM raw_rows').fetchone()[0],len(self.data['raw']))
    def test_no_target_inflation_from_disaggregation_join(self):
        self.assertEqual(self.c.execute('SELECT SUM(target) FROM report_monitor').fetchone()[0],432*900)
    def test_sql_totals_match_independent_python(self):
        bad={i['submission_id'] for i in self.issues}
        selected={}
        for s in self.data['submissions']:
            if s['status']=='approved' and s['submission_id'] not in bad:
                if s['version']>selected.get(s['report_id'],{}).get('version',0):selected[s['report_id']]=s
        ids={s['submission_id'] for s in selected.values()}
        total=sum(r['value'] for r in self.data['raw'] if r['submission_id'] in ids)
        self.assertEqual(total,self.c.execute('SELECT SUM(value) FROM approved_results').fetchone()[0])
    def test_on_time_uses_expected_denominator(self):
        on_time=self.c.execute('SELECT SUM(on_time) FROM report_monitor').fetchone()[0]
        first={}
        for s in self.data['submissions']:first.setdefault(s['report_id'],s['received_date'])
        independently=sum(e['report_id'] in first and first[e['report_id']]<=e['due_date'] for e in self.data['expectations'])
        self.assertEqual(on_time,independently)
    def test_sql_foreign_keys_active(self):
        self.assertEqual(self.c.execute('PRAGMA foreign_keys').fetchone()[0],1)
        self.assertEqual(list(self.c.execute('PRAGMA foreign_key_check')),[])
        with self.assertRaises(sqlite3.IntegrityError):self.c.execute("INSERT INTO plans VALUES ('NO_REPORT',1,1)")
    def test_zero_is_valid_missing_is_not(self):
        r=dict(self.data['raw'][0],value=0)
        group=[dict(r,sex=s,age=a,row_id=i+1) for i,(s,a) in enumerate((s,a) for s in ['F','M','U'] for a in ['child','adult'])]
        self.assertEqual(p.validate(group,self.data['expectations']),[])
        group[0]['value']='';self.assertIn('missing_value',[x['rule'] for x in p.validate(group,self.data['expectations'])])
    def test_latest_facility_observation(self):
        n=self.c.execute("SELECT COUNT(*) FROM facility_status WHERE observed_at='2026-09-30'").fetchone()[0]
        self.assertEqual(n,108)
    def test_backup_restore(self):
        backup=sqlite3.connect(Path(self.tmp.name)/'backup.sqlite');self.c.backup(backup)
        self.assertEqual(backup.execute('SELECT COUNT(*) FROM approved_results').fetchone()[0],self.c.execute('SELECT COUNT(*) FROM approved_results').fetchone()[0]);backup.close()

if __name__=='__main__':unittest.main(verbosity=2)
