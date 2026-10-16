# Synthetic monitoring management brief

Cutoff 2026-10-16. Entirely fictional data and illustrative rating rules. No actual NSDA findings or corrective outcomes.

## Reporting position

184 of 192 due reports have a received submission (95.8%). 172 have a current approved valid version (89.6%). Eight reports are missing and twelve defective versions are held. Forty-eight future expectations are excluded. The source preserves 204 raw rows, including revisions and defects.

| Round | Expected | Received | Approved | Mean approved score /100 |
|---|---:|---:|---:|---:|
| 2026-09-18 | 48 | 46 | 46 | 52.17 |
| 2026-09-25 | 48 | 46 | 46 | 51.09 |
| 2026-10-02 | 48 | 45 | 45 | 49.44 |
| 2026-10-09 | 48 | 47 | 35 | 48.86 |

Do not interpret round means as matched institutional change. Coverage differs. A matched first/fourth-round calculation includes 34 fictional institutions, with mean paired change -1.62 percentage points. This is a synthetic descriptive result, not evidence of real institutional improvement or decline.

## Three follow-up priorities in the example

1. Request missing reports and corrected versions separately. The fourth round contains twelve held versions, so its lower observed mean is especially vulnerable to selective reporting. Do not rank real institutions using this simulation.
2. Follow up on 7 overdue unresolved fictional actions. Of 24 actions, 5 meet the evidence-and-verification closure rule. ACT-001 is labelled closed but lacks proof and stays unresolved.
3. Reconcile one approved score and its source version before releasing the summary. Use sql/analysis.sql, outputs/report_monitor.csv and the workbook. Newer drafts must not displace approved observations.

## Evidence and limits

The example supplies a tested workflow, not a measurement instrument or operational assessment. Criteria, weights and thresholds were invented for the reconstruction. Missing scores remain unavailable. Received means a submission row exists even if its receipt-date field is invalid; such a version cannot be approved. No actual provider, officer or learner identity is included.
