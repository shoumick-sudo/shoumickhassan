# STP monitoring, dashboards and corrective action

**A new synthetic reconstruction of methods used in professional monitoring work. It is not the original NSDA system or an NSDA dataset.**

Prepared for Md Shoumick Hassan on 16 October 2026. Version 1.0.0. Substantial ChatGPT/Codex assistance was used for implementation, design, documentation and verification. Applicant-confirmed professional contributions and the new reconstruction are described separately in `docs/EXPERIENCE_AND_CV.md`.

## Run it

The Python pipeline uses the standard library only. Use Python 3.10 or later:

```bash
python src/build.py
python -m unittest discover -s tests -v
```

Open `outputs/dashboard.html` in a browser. It works offline. The dashboard provides monitoring filters, an expected-report roster, a local collection/revision exercise, a data-quality log and a corrective-action exercise. An unapproved draft does not change the dashboard, and an action cannot be accepted as closed without evidence and verification. Browser exercise changes are held in memory; reload resets them. Export a candidate or action CSV to retain the exercise.

Optional browser-independent JavaScript checks, if Node.js is installed:

```bash
node tests/test_dashboard.mjs
```

To validate a candidate CSV exported from the collection exercise:

```bash
python src/build.py --source candidate.csv --output imported_candidate
```

Every imported row is treated as a draft, regardless of its supplied decision. Import does not confer approval. The candidate must match the fictional master/expected-report roster. The original fixtures are generated separately. The pipeline overwrites generated data and files in the selected output directory; save manual changes elsewhere.

## Release contents

- `src/build.py`: seeded data, validation, SQLite build and output generation.
- `sql/schema.sql`: master records, expectations, raw rows, submissions, scores, issues and actions.
- `sql/analysis.sql`: reporting, follow-up, paired descriptive change and closure queries.
- `data/`: complete fictional source fixtures and seeded-defect truth ledger.
- `outputs/`: dashboard, SQLite database, reporting CSVs, issue/quarantine files, summary and assistant-run test logs.
- `outputs/STP_Monitoring_and_Actions.xlsx`: editable score formulas, due-roster reporting and verified-closure checks. This is a release snapshot, not an automatically linked database. Core commands do not recreate the workbook; refresh it deliberately after source changes and reconcile it.
- `docs/`: recruiter case, historical/reconstruction crosswalk, indicator definitions, collection specification, SOP, management brief and execution record.
- `MANIFEST.sha256`: integrity hashes for release files.

The public code folder may omit generated binary outputs; download the complete ZIP from the live demonstration for the XLSX and saved database, or rebuild the standard-library core.

## Demonstration data and decisions

48 fictional training centres, eight fictional officers and five expected rounds. At the 16 October cutoff, four rounds are due (192 expectations) and one round is in the future (48 expectations). The generated source includes missing reports, revised approved submissions, newer drafts, duplicates, invalid scores and master/date errors.

The illustrative checklist has five 0–4 ratings with equal weights. Score = sum of ratings ÷ 20 × 100. Review bands are priority below 50, attention from 50 to below 75, and routine from 75. **These are invented teaching rules, not NSDA inspection or registration standards.** Do not use them for actual institutional judgments.

## Limits

The historical work is applicant-confirmed; individual original dashboards and code were not re-opened for this reconstruction. This release does not establish exact historical dates, record counts, framework names or quantified impact. It does not deploy Google Forms, Google Sheets, Metabase, a scheduler, authentication or a multi-user approval system. The new implementation uses Python, SQLite and browser HTML/JavaScript, while the candidate's separately recorded professional work used the confirmed platform categories.

No internal NSDA CSVs, candidate identities, source queries, credentials or private evidence documents are included. No journal publication, real provider compliance finding, institutional endorsement or measured operational improvement is claimed. No open licence has been assigned to this new reconstruction.
