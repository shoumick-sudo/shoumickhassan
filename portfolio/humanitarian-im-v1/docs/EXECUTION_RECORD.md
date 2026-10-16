# Execution record

Date: 16 October 2026. Run by ChatGPT/Codex in the build environment. This is not the applicant's own execution log or independent review.

Core environment: Python 3.12.14 and SQLite 3.53.1. The core uses Python's standard library. Database integrity check returned `ok`; foreign-key check returned no violations.

- `python src/pipeline.py`: completed. Summary contains 2,667 raw rows, 432 expected reports, 408 approved reports and 2,448 approved observation rows.
- `python -m unittest discover -s tests -v`: fourteen tests passed. Full assistant-run output: outputs/assistant_python_test_log.txt.
- `python src/build_dashboard.py`: completed.
- `node tests/test_dashboard.mjs`: eight logic checks passed. Full assistant-run output: outputs/assistant_dashboard_test_log.txt. These use a minimal simulated DOM, not a real browser.
- `python src/import_form.py data/mock_form_export.csv outputs/mock_form_staging.csv`: six staging rows produced. No rows approved or imported into the database.
- Two XLSX workbooks authored, recalculated, rendered and inspected. Sector totals matched SQL output. Changing Education unit cost from 2.50 to 3.00 updated its cost correctly, then the original was restored. No formula-error matches appeared in the authoring-engine scan. Microsoft Excel desktop was not available for native verification. XLSForm compilation, sandbox deployment and submission are unverified.
- Managed browser preview could not start because the environment denied its proc mount. Preview status confirmed stopped. No real-browser visual or interaction QA is claimed. Publication proceeds with this limitation disclosed.

Initial construction encountered an issues-table placeholder-count error; it was corrected before successful runs. Historical failure output was not represented as a passing run.

The core can be rerun from source. Workbook files are release snapshots and need deliberate source refresh after data changes. Authoring runtime dependencies are not bundled as third-party software.
