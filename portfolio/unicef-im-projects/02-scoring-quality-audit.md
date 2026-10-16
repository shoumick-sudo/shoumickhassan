# 02 — Assessment Scoring, Validation and Audit Trails

**Evidence type:** historical NSDA assessment-reporting task account + fictional score-analysis reconstruction.  
**Prepared:** 16 October 2026.

## The task

I have reported using Excel for national skills-competition result processing, skill-wise PivotTables, scoring-rule checking and report reshaping. Those historical source records may identify individual candidates and are **not published**.

The [safe fictional workbook](https://docs.google.com/spreadsheets/d/170NsQVDp4zIx96zDYKpDDI5uAIk-86AiUX8f0NDw-cY/edit) shows transferable logic only.

## Illustrative dataset and rules

There are 12 fictional candidate-response rows split across two fictitious skills (S1 and S2). Each row is expected to account for 20 questions. **Illustrative** net score = Correct − 0.25 × Wrong. The 0.25 penalty is **not claimed as an NSDA policy**.

A row is invalid if Correct + Wrong + Blank ≠ 20, if there is a duplicate Candidate_ID, or if a component is negative. It must not receive a valid rank. Data quality exceptions are preserved rather than silently discarded.

- Fictional ID **C005** appears twice and both entries are flagged as duplicate.
- Fictional ID **C012** contains 21 total answers and is flagged for count mismatch.
- Valid results are ranked only against other valid entries in the same skill.

| Fictional skill | Valid rows | Flagged rows | Highest valid score | Mean valid score |
|---|---:|---:|---:|---:|
| S1 | 4 | 2 | 17.50 | 13.9375 |
| S2 | 5 | 1 | 20.00 | 14.25 |

These outputs are from the synthetic sheet's formula-based readback, not the 2025 competition.

## Excel-style implementation

Net score: `=Correct-0.25*Wrong`  
Count check: `=IF(SUM(Correct,Wrong,Blank)=20,"OK","COUNT_MISMATCH")`  
Duplicate check: `COUNTIF(candidate_id_column,current_id)>1`  
Rank among valid same-skill records: `1+COUNTIFS(skill_column,current_skill,score_column,">"&current_score,status_column,"OK")`.

A complete release workflow also requires official approved scoring policy, locked inputs, exception owners, reviewer action and versioned correction records.

## Applicant test

Open the workbook in **Microsoft Excel**, independently recreate a PivotTable, explain the three invalid rows and the current valid rank, and show how a reviewer-approved correction changes the summary. A Google Sheets formula is not sufficient evidence of desktop Excel expertise.

**UNICEF ToR transfer:** validation, duplicate detection, reconciliation, exception handling, auditable reporting.

## Limits

No real assessments, candidate records, proprietary examination questions, official rules or NSDA outcomes are represented. Historical authorship should be verified through acceptable private records or referees. Reconstruction was AI-assisted; independent applicant validation remains pending.
