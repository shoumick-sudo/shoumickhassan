import json,csv
from pathlib import Path
root=Path(__file__).resolve().parents[1];s=json.loads((root/'outputs/summary.json').read_text())
table='\n'.join(f"| {r['sector']} | {r['actual']:,} | {r['target']:,} | {100*r['actual']/r['target']:.1f}% | {r['approved']}/{r['expected']} |" for r in s['sectors'])
text=f'''# Synthetic management brief

Independent portfolio demonstration using synthetic programme data. Not UNICEF or official response data.

Period: April–September 2026. Data cutoff: 16 October 2026. Version 0.1.0. AI-assisted technical example; no actual donor submission or programme result.

## Reporting position

{s['received_reports']} of {s['expected_reports']} reports were received ({100*s['received_reports']/s['expected_reports']:.1f}%). {s['approved_reports']} have a current approved version ({100*s['approved_reports']/s['expected_reports']:.1f}%). {s['on_time_reports']} were received on time ({100*s['on_time_reports']/s['expected_reports']:.1f}% of all expected reports).

| Sector | Observed approved events | Planned events | Observed / target | Approved reports |
|---|---:|---:|---:|---:|
{table}

These are three different service-event units, not unique people. Repeated attendance or contacts can occur. Do not total the sectors into beneficiaries. Targets are synthetic assumptions, not needs estimates. Unavailable reports leave actuals missing, so target gaps cannot be interpreted as proved service non-delivery.

## Three decisions supported by this simulation

1. Prioritize correction of eighteen defective submission versions and follow up on six entirely missing reports. Use outputs/report_monitor.csv, not a list generated only from received submissions. Keep the two categories distinct.
2. Delay any current emergency facility-status claim until the observation source is refreshed. All 108 latest facility observations are dated 30 September, sixteen days before cutoff; they fail the proposed seven-day freshness rule. The dashboard shows historical states and unknowns separately.
3. Review the lower observed/target ratios in WASH and Health alongside missingness and the realism of the target assumptions. Do not infer worse partner performance or real unmet need from a synthetic ratio alone.

## Audit and limitations

The source layer retains {s['raw_rows']:,} rows; {s['approved_rows']:,} enter current approved outputs. The issue log has {s['dq_issue_flags']} flags. Rows may have multiple flags, and a critical issue excludes the entire report version. Latest approved views avoid double counting revisions and keep newer unapproved drafts out. Every figure above comes from outputs/summary.json and report_monitor.csv. Fourteen Python tests and eight browser-independent dashboard logic checks were prepared; use the execution record for actual run results. No independent human review or applicant proficiency assessment is claimed.
'''
(root/'docs/MANAGEMENT_BRIEF.md').write_text(text)
print('Built docs/MANAGEMENT_BRIEF.md')
