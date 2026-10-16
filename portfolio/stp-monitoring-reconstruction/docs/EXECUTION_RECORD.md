# Build and verification record

Date: 16 October 2026. Executed by ChatGPT/Codex, not recorded as the applicant's unaided performance.

- Standard-library Python build completed; seeded results are saved in outputs/summary.json.
- `python -m unittest discover -s tests -v`: eighteen tests passed. See outputs/assistant_python_tests.txt.
- `node tests/test_dashboard.mjs`: eleven logic checks passed. See outputs/assistant_dashboard_tests.txt. The checks use a simulated DOM, not a real browser.
- Tests cover seeded defects, empty approved results after draft-only import, raw preservation, unique reporting grain, future expectations, missing versus zero, latest approved versions, score arithmetic, date errors, invalid ratings, closure evidence, foreign keys, paired descriptions and backup/restore.
- Excel-compatible workbook recalculated and reconciled against the database: 192 due / 172 approved; 24 actions / 5 accepted closures / 7 overdue. Score editing, missing-rating handling and evidence-based closure changes were checked and reverted. No formula-error matches were found in the authoring-engine scan. All four sheets were rendered and visually inspected. Native Excel desktop behavior remains unverified.
- Managed browser preview failed because the environment denied its proc mount; supervisor status was stopped. Browser visual QA was not performed. No deployment or account use of Google Forms, Google Sheets, Metabase or a scheduler is claimed for this new implementation.
- An early test exposed an empty-result CSV export defect, which was repaired. An exact float equality assertion was changed to a ten-decimal numerical comparison. Successful final logs replace neither historical failures nor human review.

The core source regenerates CSV/JSON/SQLite/dashboard files. The workbook is a release snapshot requiring deliberate refresh; the core command does not rebuild it. A personal applicant walkthrough remains separate from these assistant-run checks.
