import json,sqlite3
from pathlib import Path
root=Path(__file__).resolve().parents[1];s=json.loads((root/'outputs/summary.json').read_text());c=sqlite3.connect(root/'outputs/monitoring.sqlite');c.row_factory=sqlite3.Row
rs=c.execute('SELECT round_date,COUNT(*) expected,SUM(received) received,COUNT(submission_id) approved,ROUND(AVG(score_pct),2) mean FROM report_monitor WHERE due_date<=? GROUP BY round_date',(s['cutoff'],)).fetchall()
table='\n'.join(f"| {r['round_date']} | {r['expected']} | {r['received']} | {r['approved']} | {r['mean']:.2f} |" for r in rs)
paired=c.execute("SELECT COUNT(*) n,AVG(b.score_pct-a.score_pct) change FROM report_monitor a JOIN report_monitor b USING(provider_id) WHERE a.round_date='2026-09-18' AND b.round_date='2026-10-09' AND a.submission_id IS NOT NULL AND b.submission_id IS NOT NULL").fetchone()
text=f'''# Synthetic monitoring management brief

Cutoff {s['cutoff']}. Entirely fictional data and illustrative rating rules. No actual NSDA findings or corrective outcomes.

## Reporting position

{s['received_reports']} of {s['due_reports']} due reports have a received submission ({100*s['received_reports']/s['due_reports']:.1f}%). {s['approved_reports']} have a current approved valid version ({100*s['approved_reports']/s['due_reports']:.1f}%). Eight reports are missing and twelve defective versions are held. Forty-eight future expectations are excluded. The source preserves {s['raw_rows']} raw rows, including revisions and defects.

| Round | Expected | Received | Approved | Mean approved score /100 |
|---|---:|---:|---:|---:|
{table}

Do not interpret round means as matched institutional change. Coverage differs. A matched first/fourth-round calculation includes {paired['n']} fictional institutions, with mean paired change {paired['change']:.2f} percentage points. This is a synthetic descriptive result, not evidence of real institutional improvement or decline.

## Three follow-up priorities in the example

1. Request missing reports and corrected versions separately. The fourth round contains twelve held versions, so its lower observed mean is especially vulnerable to selective reporting. Do not rank real institutions using this simulation.
2. Follow up on {s['overdue_actions']} overdue unresolved fictional actions. Of {s['actions']} actions, {s['accepted_closures']} meet the evidence-and-verification closure rule. ACT-001 is labelled closed but lacks proof and stays unresolved.
3. Reconcile one approved score and its source version before releasing the summary. Use sql/analysis.sql, outputs/report_monitor.csv and the workbook. Newer drafts must not displace approved observations.

## Evidence and limits

The example supplies a tested workflow, not a measurement instrument or operational assessment. Criteria, weights and thresholds were invented for the reconstruction. Missing scores remain unavailable. Received means a submission row exists even if its receipt-date field is invalid; such a version cannot be approved. No actual provider, officer or learner identity is included.
'''
(root/'docs/MANAGEMENT_BRIEF.md').write_text(text);c.close();print('Wrote docs/MANAGEMENT_BRIEF.md')
